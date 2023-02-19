#! /usr/bin/python3
"""
interface to Jira as a method to read and store worklog entries
"""

from typing import Union, Dict, List, Any, Optional, Tuple, Iterable, Iterator, cast
from requests import Session, Response, HTTPError
from requests.packages.urllib3.exceptions import InsecureRequestWarning   # type: ignore[import]
import warnings
import logging
import json
import os
import re
import sys
import datetime
from odootopic import OdooValues, OdooValuesForTopic
from urllib.parse import quote_plus as qq
import netrc
import gitrc
from dayrange import get_date, is_dayrange, dayrange, last_sunday, next_sunday
from tabtotext import tabToJSON, tabToGFM, tabToHTML, JSONDict, JSONList, JSONItem, setNoRight, tabWithDateHour

logg = logging.getLogger("JIRA2DATA")

def get_login() -> str:
    return os.environ.get("LOGIN", "") or os.environ.get("USER") or "admin"

Day = datetime.date
FrontendUrl = str
Verify = Union[bool, str]
NIX = ""

url_verify = False
url_timeout: Optional[int] = 20
DAYS = dayrange()
USER = NIX

MAXROUNDS = 1000
LIMIT = 1000

PROJECTS: List[str] = []
PROJECTDEFAULT = "ASO"
JIRADEFAULT = "http://jira.host"  # RFC2606

HTMLFILE = ""
TEXTFILE = ""
JSONFILE = ""
TASKDATA = ""
SHORTDESC = 0
DRYRUN = 0

def strDesc(val: Optional[str]) -> Optional[str]:
    if SHORTDESC:
        return shortDesc(val)
    return val
def shortDesc(val: Optional[str]) -> Optional[str]:
    if not val:
        return val
    if len(val) > 40:
        return val[:37] + "..."
    return val

class JiraFrontend:
    url_verify: Verify
    url_timeout: Optional[int]
    def __init__(self, remote: Optional[FrontendUrl] = None, verify: Optional[Verify] = None, timeout: Optional[int] = None):
        self.remote = remote
        if not self.remote:
            self.remote = gitrc.git_config_value("jira.url")
            if not self.remote:
                logg.error("either set '-r http://url/to/jira' or add ~/.gitconfig [jira]url=http://url/to/jira")
                self.remote = JIRADEFAULT
        if verify is None:
            self.url_verify = url_verify
        else:
            self.url_verify = verify
        if timeout is None:
            if url_timeout and url_timeout < 900:
                self.url_timeout = int(url_timeout)
            else:
                self.url_timeout = int(gitrc.git_config_value("jira.timeout") or "20")
        else:
            self.url_timeout = timeout
        #
        self._user: Optional[str] = None
        self._sessions: Dict[str, Session] = {}
        self.json = {"Content-Type": "application/json"}
        self.json2 = {"Content-Type": "application/json", "Accept": "application/json"}
        self.asxml = {"Content-Type": "application/xml"}
    @property
    def timeout(self) -> Optional[int]:
        return self.url_timeout
    @property
    def verify(self) -> Verify:
        return self.url_verify
    def is_json(self, r: Response) -> bool:
        if "content-type" in r.headers:
            if "/json" in r.headers["content-type"]:
                return True
        return False
    def error(self, r: Response) -> bool:
        return r.status_code >= 300
    def critical(self, r: Response) -> bool:
        return r.status_code >= 400
    def severe(self, r: Response) -> bool:
        return r.status_code >= 500
    def url(self) -> FrontendUrl:
        return self.remote or JIRADEFAULT
    def jira(self) -> str:
        return self.remote or JIRADEFAULT
    def session(self, url: Optional[str] = None) -> Session:
        url = url or self.url()
        if url not in self._sessions:
            session = Session()
            session.auth = netrc.get_username_password(url)
            self._sessions[url] = session
        return self._sessions[url]
    def pwinfo(self) -> str:
        return netrc.str_get_username_password(self.url()) + " for " + self.url()
    def user(self, url: Optional[str] = None) -> str:
        if self._user:
            return self._user
        if USER:
            self._user = USER
            if self._user:
                return self._user
        jira_user = gitrc.git_config_value("jira.user")
        if jira_user:
            logg.info("user: using gitconfig jira.user")
            self._user = jira_user
            if self._user:
                return self._user
        user_name = gitrc.git_config_value("user.name")
        # search jira users by name?
        user_mail = gitrc.git_config_value("user.email")
        # search jira users by email?
        url = url or self.url()
        auth = netrc.get_username_password(url)
        if auth:
            logg.info("user: using netrc authuser")
            self._user = auth[0]
            if self._user:
                return self._user
        logg.info("user: fallback to local login user")
        login_user = get_login()
        self._user = login_user
        return login_user

def jiraGetProjects(api: JiraFrontend) -> JSONList:
    req = "/rest/api/2/project"
    req += "?expand=projectKeys"
    url = api.jira() + req
    http = api.session(api.jira())
    headers = {"Content-Type": "application/json"}
    r = http.get(url, headers=headers, verify=api.verify)
    if api.error(r):
        logg.error("%s => %s", req, r.text)
        logg.warning("    %s", api.pwinfo())
        raise HTTPError(r)
    else:
        logg.debug("%s => %s", req, r.text)
        data: JSONList = json.loads(r.text)
        for item in data:
            for field in ["self", "avatarUrls", "expand", "projectCategory"]:
                if field in item:
                    del item[field]
        return data

def only_ActiveJiraProjects(data: Iterable[JSONDict]) -> Iterator[JSONDict]:
    for item in data:
        if item.get("archived"):
            continue
        newitem = item.copy()
        for field in ["archived", "id", "projectKeys"]:
            if field in newitem:
                del newitem[field]
        yield newitem

def jiraGetProjectsIssuesInDays(api: JiraFrontend, projects: List[str], days: Optional[dayrange] = None) -> JSONList:
    days = days or DAYS
    projectlist = ",".join(projects)
    jql = f"""project in ({projectlist})"""
    if days:
        jql += f""" and 'updated' > {days.daysafter}d and 'updated' <= {days.daysbefore}d """
    req = "/rest/api/2/search"
    url = api.jira() + req
    http = api.session(api.jira())
    headers = {"Content-Type": "application/json"}
    result = []
    totals = 0
    starts = 0
    for attempt in range(MAXROUNDS):
        post = {
            "jql": jql,
            "startAt": starts,
            "maxResults": LIMIT,
        }
        r = http.post(url, headers=headers, verify=api.verify, json=post)
        if api.error(r):
            logg.error("%s => %s\n  query was %s", req, r.text, post)
            logg.warning("    %s", api.pwinfo())
            raise HTTPError(r)
        else:
            logg.debug("%s => %s", req, r.text)
            data: JSONDict = json.loads(r.text)
            logg.info("%s => %s", jql, data.keys())
            if "total" in data:
                totals = cast(int, data["total"])
            if "issues" not in data or not data["issues"]:
                break
            issues = cast(JSONList, data["issues"])
            logg.info("%s => %i issues (starts %i)", jql, len(issues), starts)
            for item in issues:
                # logg.info(" ..\n\n%s", item)
                if False:
                    logg.debug(" ..%s", [name for name in sorted(item["fields"].keys())
                                         if not name.startswith("customfield")])  # type: ignore[union-attr]
                issuetype = item["fields"].get("issuetype", {}).get("name", "")  # type: ignore[union-attr,index]
                res = {"issueId": item["id"], "issue": item["key"], "proj": item["fields"]["project"]["key"], "summary": item["fields"]["summary"],  # type: ignore[union-attr,index,call-overload]
                       "last_updated": get_date(cast(str, item["fields"]["updated"])), "issuetype": issuetype}  # type: ignore[union-attr,index,call-overload]
                result.append(res)
            if totals and totals == len(issues):
                break
            starts += LIMIT
    logg.info("have %s issues, but return %s issues", totals, len(result))
    return result


def jiraGetUserIssuesInDays(api: JiraFrontend, user: str = NIX, days: Optional[dayrange] = None) -> JSONList:
    days = days or DAYS
    user = user or api.user()
    jql = f"""watcher = '{user}'"""
    if days:
        jql += f""" and 'updated' > {days.daysafter}d and 'updated' <= {days.daysbefore}d """
    logg.warning("jql = %s", jql)
    req = "/rest/api/2/search"
    url = api.jira() + req
    http = api.session(api.jira())
    headers = {"Content-Type": "application/json"}
    result = []
    totals = 0
    starts = 0
    for attempt in range(MAXROUNDS):
        post = {
            "jql": jql,
            "startAt": starts,
            "maxResults": LIMIT,
        }
        r = http.post(url, headers=headers, verify=api.verify, json=post)
        if api.error(r):
            logg.error("%s => %s\n  query was %s", req, r.text, post)
            logg.warning("    %s", api.pwinfo())
            raise HTTPError(r)
        else:
            logg.debug("%s => %s", req, r.text)
            data: JSONDict = json.loads(r.text)
            logg.info("%s => %s", jql, data.keys())
            if "total" in data:
                totals = cast(int, data["total"])
            if "issues" not in data or not data["issues"]:
                break
            issues = cast(JSONList, data["issues"])
            logg.info("%s => %i issues (starts %i)", jql, len(issues), starts)
            for item in issues:
                # logg.info(" ..\n\n%s", item)
                if False:
                    logg.debug(" ..%s", [name for name in sorted(item["fields"].keys())
                                         if not name.startswith("customfield")])  # type: ignore[union-attr]
                issuetype = item["fields"].get("issuetype", {}).get("name", "")  # type: ignore[union-attr,index]
                res = {"issueId": item["id"], "issue": item["key"], "proj": item["fields"]["project"]["key"], "summary": item["fields"]["summary"],  # type: ignore[union-attr,index,call-overload]
                       "last_updated": get_date(cast(str, item["fields"]["updated"])), "issuetype": issuetype}  # type: ignore[union-attr,index,call-overload]
                result.append(res)
            if totals and totals == len(issues):
                break
            starts += LIMIT
    logg.info("have %s issues, but return %s issues", totals, len(result))
    return result

def jiraGetIssueActivity(api: JiraFrontend, issue: str) -> JSONList:
    return list(each_jiraGetIssueActivity(api, issue))
def each_jiraGetIssueActivity(api: JiraFrontend, issue: str) -> Iterator[JSONDict]:
    skipfields = ["self", "author", "updateAuthor", "body"]
    # req = f"/rest/api/2/issue/{issue}?expand=changelog&fields=summary"
    req = f"/rest/api/2/issue/{issue}?expand=changelog"
    url = api.jira() + req
    http = api.session(api.jira())
    headers = {"Content-Type": "application/json"}
    r = http.get(url, headers=headers, verify=api.verify)
    if api.error(r):
        logg.error("%s => %s\n", req, r.text)
        logg.warning("    %s", api.pwinfo())
        raise HTTPError(r)
    else:
        logg.debug("%s => %s", req, r.text)
        data = json.loads(r.text)
        # ['aggregateprogress', 'aggregatetimeestimate', 'aggregatetimeoriginalestimate', 'aggregatetimespent', 'assignee', 'components',
        # 'created', 'creator', 'description', 'duedate', 'environment', 'issuelinks', 'issuetype', 'labels', 'lastViewed', 'priority',
        # 'progress', 'project', 'reporter', 'resolution', 'resolutiondate', 'status', 'subtasks', 'summary',
        # 'timeestimate', 'timeoriginalestimate', 'timespent', 'updated', 'votes', 'watches', 'workratio']
        if False:
            logg.info("%s => %s", req, [name for name in data.keys() if "customfield" not in name])
            logg.info("%s fields -> %s", req, [name for name in data["fields"].keys() if "customfield" not in name])
            logg.info("%s fields comment -> %s", req, [name for name in data["fields"]
                                                       ["comment"].keys() if "customfield" not in name])
            logg.info("%s fields worklog -> %s", req, [name for name in data["fields"]
                                                       ["worklog"].keys() if "customfield" not in name])
            logg.info("%s changelog -> %s", req, [name for name in data["changelog"].keys() if "customfield" not in name])
        issuetype = data["fields"].get("issuetype", {}).get("name", "")
        for item in data["changelog"]["histories"]:
            # logg.info(" ..\n\n%s", item)
            # res = {"id": item["id"], "key": item["key"], "proj": item["fields"]["project"]["key"], "summary": item["fields"]["summary"], "type": issuetype}
            itemAuthor = item.get("author", {}).get("name", "")
            res = item.copy()
            res["issue"] = issue
            res["issuetype"] = issuetype
            res["itemAuthor"] = itemAuthor
            res["type"] = "history"
            for field in skipfields:
                if field in res:
                    del res[field]
            for item in item["items"]:
                res["change.field"] = item.get("field")
                res["change.fromString"] = item.get("fromString")
                res["change.toString"] = item.get("toString")
            del res["items"]
            yield res
        for item in data["fields"]["comment"]["comments"]:
            # logg.info(" ..\n\n%s", item)
            # res = {"id": item["id"], "key": item["key"], "proj": item["fields"]["project"]["key"], "summary": item["fields"]["summary"], "type": issuetype}
            itemAuthor = item.get("author", {}).get("name", "")
            res = item.copy()
            res["issue"] = issue
            res["issuetype"] = issuetype
            res["itemAuthor"] = itemAuthor
            res["type"] = "comment"
            for field in skipfields:
                if field in res:
                    del res[field]
            yield res
        for item in data["fields"]["worklog"]["worklogs"]:
            # logg.info(" ..\n\n%s", item)
            # res = {"id": item["id"], "key": item["key"], "proj": item["fields"]["project"]["key"], "summary": item["fields"]["summary"], "type": issuetype}
            itemAuthor = item.get("author", {}).get("name", "")
            res = item.copy()
            res["issue"] = issue
            res["issuetype"] = issuetype
            res["itemAuthor"] = itemAuthor
            res["type"] = "worklog"
            for field in skipfields:
                if field in res:
                    del res[field]
            yield res

def only_shorterActivity(data: Iterable[JSONDict]) -> Iterator[JSONDict]:
    for item in data:
        if item["type"] == "history" and item["change.field"] in ["RemoteIssueLink", "Link", "Rank", "Flagged", "Sprint", "Workflow", "Attachment"]:
            continue
        if "id" in item:
            del item["id"]
        if "created" in item:
            item["upcreated"] = get_date(cast(str, item["created"]))
            del item["created"]
        if "change.fromString" in item:
            del item["change.fromString"]
        if "change.fromString" in item:
            del item["change.fromString"]
        if "change.toString" in item:
            item["change.toString"] = shortDesc(cast(str, item["change.toString"]))
        yield item

def jiraGetUserActivityInDays(api: JiraFrontend, user: str = NIX, days: Optional[dayrange] = None) -> JSONList:
    return list(each_jiraGetUserActivityInDays(api, user, days))
def each_jiraGetUserActivityInDays(api: JiraFrontend, user: str = NIX, days: Optional[dayrange] = None) -> Iterator[JSONDict]:
    for ticket in jiraGetUserIssuesInDays(api, user, days):
        for item in each_jiraGetIssueActivity(api, cast(str, ticket["issue"])):
            yield item


#############################################################################################
def jiraOdooData(api: JiraFrontend, user: str = NIX, days: Optional[dayrange] = None) -> JSONList:
    return list(each_jiraOdooData(api, user, days))
def each_jiraOdooData(api: JiraFrontend, user: str = NIX, days: Optional[dayrange] = None) -> Iterator[JSONDict]:
    days = days or DAYS
    later = dayrange(days.after)
    for ticket in jiraGetUserIssuesInDays(api, user, later):
        user = user or api.user()
        issue = cast(str, ticket["issue"])
        for record in jiraGetWorklog(api, issue):
            if user:
                author = cast(str, record["authorname"])
                if user != author:
                    logg.debug("ignore author %s (we are %s)", author, user)
                    continue
            started = get_date(cast(str, record["started"]))
            if days.after > started or started > days.before:
                continue
            hours = cast(int, record["timeSpentSeconds"]) / 3600
            desc = cast(str, record["comment"])
            item: JSONDict = {}
            item["Date"] = started
            item["Quantity"] = hours
            item["Description"] = desc
            item["Project"] = jira_odoo_project(issue, desc)
            item["Task"] = jira_odoo_task(issue, desc)
            item["Ticket"] = issue
            item["User"] = user
            yield item

jira_odoomap: Optional[OdooValuesForTopic] = None

def jira_project(taskname: str) -> str:
    parts = taskname.split("-", 1)
    return parts[0]

def jira_odoo_project(taskname: str, desc: str = "") -> str:
    if jira_odoomap:
        values = jira_odoomap.values(taskname)
        if desc:
            for value in sorted(values, key=lambda x: cast(str, x.pref), reverse=True):
                if desc.startswith(cast(str, value.pref)):
                    return cast(str, value.proj)
        if values:
            first = sorted(values, key=lambda x: cast(str, x.pref), reverse=True)
            return cast(str, first[0].proj)
    parts = taskname.split("-", 1)
    return parts[0]

def jira_odoo_task(taskname: str, desc: str = "") -> str:
    if jira_odoomap:
        values = jira_odoomap.values(taskname)
        if desc:
            for value in sorted(values, key=lambda x: cast(str, x.pref), reverse=True):
                if desc.startswith(cast(str, value.pref)):
                    return cast(str, value.proj)
        if values:
            first = sorted(values, key=lambda x: cast(str, x.pref), reverse=True)
            return cast(str, first[0].task)
    return taskname

def read_odoo_taskdata(filename: str) -> Dict[str, str]:
    global jira_odoomap
    jira_odoomap = OdooValuesForTopic()
    for line in open(filename):
        if line.startswith(">>"):
            jira_odoomap.scanline(line)
    mapping = jira_odoomap.ticket4
    logg.info("jira odoomap %s", mapping)
    return mapping

#############################################################################################
WEEKDAYS = ["so", "mo", "di", "mi", "do", "fr", "sa", "so"]

def jiraZeitData(api: JiraFrontend, user: str = NIX, days: Optional[dayrange] = None) -> JSONList:
    return list(each_jiraZeitData(api, user, days))
def each_jiraZeitData(api: JiraFrontend, user: str = NIX, days: Optional[dayrange] = None) -> Iterator[JSONDict]:
    days = days or DAYS
    later = dayrange(days.after)
    data: Dict[Tuple[str, str], List[str]] = {}
    mapping: Dict[str, str] = {}
    weekstart = None
    for ticket in jiraGetUserIssuesInDays(api, user, later):
        user = user or api.user()
        issue = cast(str, ticket["issue"])
        for record in jiraGetWorklog(api, issue):
            if user:
                author = cast(str, record["authorname"])
                if user != author:
                    logg.debug("ignore author %s (we are %s)", author, user)
                    continue
            started = get_date(cast(str, record["started"]))
            if days.after > started or started > days.before:
                continue
            hours = cast(int, record["timeSpentSeconds"]) / 3600
            desc = cast(str, record["comment"])
            prefix = desc.split(" ", 1)[0]
            mapping[prefix] = issue
            key = (started.strftime("%Y-%m-%d"), prefix)
            if key not in data:
                data[key] = []
            sunday = last_sunday(0, started)
            if weekstart is None or weekstart != sunday:
                nextsunday = next_sunday(0, sunday)
                line = "so **** WEEK %s-%s" % (sunday.strftime("%d.%m."), nextsunday.strftime("%d.%m."))
                data[(sunday.strftime("%Y-%m-%d"), "***")] = [line]
            weekday = WEEKDAYS[started.weekday()]
            hh = int(hours)
            mm = int((hours - hh) * 60)
            line = f"{weekday} {hh}:{mm:02} {desc}"
            data[key] += [line]
    for prefix, issue in mapping.items():
        yield {"zeit.txt": f">> {prefix} {issue}"}
    for key in sorted(data):
        lines = data[key]
        if len(lines) > 1:
            logg.warning(" multiple lines for day %s topic %s", *key)
            for line in lines:
                logg.warning(" | %s", line)
        for line in lines:
            yield {"zeit.txt": line}

#############################################################################################
def date2isotime(ondate: Day) -> str:
    return ondate.strftime("%Y-%m-%dT20:20:00.000+0000")

def jiraGetWorklog(api: JiraFrontend, issue: str) -> JSONList:
    return list(_jiraGetWorklog(api, issue))
def _jiraGetWorklog(api: JiraFrontend, issue: str) -> Iterator[JSONDict]:
    skipfields = ["self", "author", "updateAuthor", "body"]
    req = f"/rest/api/2/issue/{issue}/worklog"
    url = api.jira() + req
    http = api.session(api.jira())
    headers = {"Content-Type": "application/json"}
    r = http.get(url, headers=headers, verify=api.verify)
    if api.error(r):
        logg.error("%s => %s\n", req, r.text)
        logg.warning("    %s", api.pwinfo())
        raise HTTPError(r)
    else:
        logg.debug("%s => %s", req, r.text)
        data = json.loads(r.text)
        # logg.info("data %s", data)
        # logg.debug("data worklogs %s", data["worklogs"])
        for res in data["worklogs"]:
            if "author" in res:
                res["authorname"] = res["author"]["name"]
            for field in skipfields:
                if field in res:
                    del res[field]
            yield res

def jiraAddWorklog(api: JiraFrontend, issue: str, ondate: Day, size: float, desc: str) -> JSONDict:
    req = f"/rest/api/2/issue/{issue}/worklog"
    url = api.jira() + req
    http = api.session(api.jira())
    headers = {"Content-Type": "application/json"}
    post = {
        "comment": desc,
        "started": date2isotime(ondate),
        "timeSpentSeconds": int(size * 3600),
    }
    logg.debug("post %s", post)
    r = http.post(url, headers=headers, verify=api.verify, json=post)
    if api.error(r):
        logg.error("%s => %s\n", req, r.text)
        logg.warning("    %s", api.pwinfo())
        raise HTTPError(r)
    else:
        logg.debug("%s => %s", req, r.text)
        data: JSONDict = json.loads(r.text)
        logg.debug("data %s", data)
        return data

def jiraUpdateWorklog(api: JiraFrontend, worklog: int, issue: str, ondate: Day, size: float, desc: str) -> JSONDict:
    req = f"/rest/api/2/issue/{issue}/worklog/{worklog}"
    url = api.jira() + req
    http = api.session(api.jira())
    headers = {"Content-Type": "application/json"}
    post = {
        "comment": desc,
        "started": date2isotime(ondate),
        "timeSpentSeconds": int(size * 3600),
    }
    logg.debug("put %s", post)
    r = http.put(url, headers=headers, verify=api.verify, json=post)
    if api.error(r):
        logg.error("%s => %s\n", req, r.text)
        logg.warning("    %s", api.pwinfo())
        raise HTTPError(r)
    else:
        logg.debug("%s => %s", req, r.text)
        data: JSONDict = json.loads(r.text)
        logg.debug("data %s", data)
        return data

class Worklogs:
    def __init__(self, user: str = NIX) -> None:
        self.remote = JiraFrontend()
        self.user = user
    def timesheet(self, issue: str, on_or_after: Day, on_or_before: Day) -> Iterator[JSONDict]:
        session = self.remote.session()
        user = self.user or self.remote.user()
        for record in jiraGetWorklog(self.remote, issue):
            if user:
                author = cast(str, record["authorname"])
                if user != author:
                    logg.debug("ignore author %s (we are %s)", author, user)
                    continue
            logg.debug("jira %s worklog %s", issue, record)
            created = get_date(cast(str, record["created"]))
            updated = get_date(cast(str, record["updated"]))
            started = get_date(cast(str, record["started"]))
            worktime = started or updated or created
            logg.debug("check %s on %s (%s .. %s)", record, worktime, on_or_after, on_or_before)
            if on_or_after > worktime or worktime > on_or_before:
                continue
            record["entry_id"] = record["id"]
            record["entry_date"] = worktime
            record["entry_size"] = cast(int, record["timeSpentSeconds"]) / 3600
            record["entry_desc"] = record["comment"]
            yield record
    def worklog_create(self, issue: str, ondate: Day, size: float, desc: str) -> JSONDict:
        return jiraAddWorklog(self.remote, issue, ondate, size, desc)
    def worklog_update(self, worklog: int, issue: str, ondate: Day, size: float, desc: str) -> JSONDict:
        return jiraUpdateWorklog(self.remote, worklog, issue, ondate, size, desc)

def run(remote: JiraFrontend, args: List[str]) -> int:
    global DAYS
    # execute verbs after arguments are scanned
    result: JSONList = []
    summary: List[str] = []
    sortby: List[str] = []
    tab = "|"
    for arg in args:
        if is_dayrange(arg):  # "week", "month", "last", "latest"
            DAYS = dayrange(arg)
            logg.info("using days = %s", DAYS)
            continue
        if arg in ["help"]:
            report_name = None
            for line in open(__file__):
                if line.strip().replace("elif", "if").startswith("if report in"):
                    report_name = line.split("if report in", 1)[1].strip()
                    continue
                elif line.strip().startswith("result = "):
                    report_call = line.split("result = ", 1)[1].strip()
                    if report_name:
                        print(f"{report_name} {report_call}")
                report_name = None
            return 0
        report = arg.lower()
        if report in ["allprojects"]:
            result = list(jiraGetProjects(remote))
        elif report in ["projects", "pp"]:
            result = list(only_ActiveJiraProjects(jiraGetProjects(remote)))
        elif report in ["user"]:
            result = [{"url": remote.url(), "user": remote.user()}]
        elif report in ["all", "ll"]:
            result = list(jiraGetProjectsIssuesInDays(remote, PROJECTS or [PROJECTDEFAULT]))
        elif report in ["tickets", "tt"]:
            result = list(jiraGetUserIssuesInDays(remote))
        elif report in ["allactivity", "aaa"]:
            result = list(jiraGetUserActivityInDays(remote))
        elif report in ["activity", "aa"]:
            result = list(only_shorterActivity(jiraGetUserActivityInDays(remote)))
            sortby = ["upcreated"]
        elif report in ["myactivity", "a"]:
            result = list(item for item in only_shorterActivity(
                jiraGetUserActivityInDays(remote)) if item["itemAuthor"] == remote.user())
            sortby = ["upcreated"]
        elif report in ["odoo", "data", "d"]:
            if TASKDATA:
                read_odoo_taskdata(TASKDATA)
            result = list(jiraOdooData(remote))
        elif report in ["zeit", "text", "z"]:
            if TASKDATA:
                read_odoo_taskdata(TASKDATA)
            result = list(jiraZeitData(remote))
            tab = ""
        else:
            logg.error("unknown report %s", report)
    def lastdesc(name: str) -> str:
        if name in ["Description", "comment"]:
            return f"z.{name}"
        if name in ["Quantity"]:
            return f"Day{name}"
        if name in ["upcreated"]:
            return f"at.{name}"
        return name
    if result:
        summary += ["found %s items" % (len(result))]
        print(tabToGFM(result, sorts=sortby, legend=summary, reorder=lastdesc, tab=tab))
        if TEXTFILE:
            with open(TEXTFILE, "w") as f:
                print(tabToGFM(result, sorts=sortby, legend=summary, reorder=lastdesc, tab=tab), file=f)
                logg.info("written %s", TEXTFILE)
        if HTMLFILE:
            with open(HTMLFILE, "w") as f:
                print(tabToHTML(result, sorts=sortby, legend=summary, reorder=lastdesc), file=f)
                logg.info("written %s", HTMLFILE)
        if JSONFILE:
            with open(JSONFILE, "w") as f:
                print(tabToJSON(result, sorts=sortby), file=f)
                logg.info("written %s", JSONFILE)
    return 0

if __name__ == "__main__":
    from optparse import OptionParser
    cmdline = OptionParser("%prog [options] [create|update|upload|parentpage]", epilog=__doc__)
    cmdline.add_option("-v", "--verbose", action="count", default=0,
                       help="more verbose logging")
    cmdline.add_option("-a", "--after", metavar="DATE", default=None,
                       help="only evaluate entrys on and after [first of month]")
    cmdline.add_option("-b", "--before", metavar="DATE", default=None,
                       help="only evaluate entrys on and before [last of month]")
    cmdline.add_option("-j", "--project", metavar="JIRA", action="append", default=PROJECTS,
                       help="jira projects (%default) or " + PROJECTDEFAULT)
    cmdline.add_option("-H", "--htmlfile", metavar="PATH", default=HTMLFILE)
    cmdline.add_option("-T", "--textfile", metavar="PATH", default=TEXTFILE)
    cmdline.add_option("-J", "--jsonfile", metavar="PATH", default=JSONFILE)
    cmdline.add_option("-m", "--taskdata", metavar="PATH", default=TASKDATA)
    cmdline.add_option("-q", "--dryrun", action="count", default=0)
    cmdline.add_option("-Q", "--shortdesc", action="count", default=SHORTDESC,
                       help="present short lines for description [%default]")
    cmdline.add_option("-r", "--restapi", "--remote", metavar="URL", default=None,
                       help="url to Jira API endpoint (or gitconfig jira.url)")
    cmdline.add_option("-U", "--user", metavar="NAME", default=USER,
                       help="filter for user [%default]")
    opt, args = cmdline.parse_args()
    logging.basicConfig(level=max(0, logging.ERROR - 10 * opt.verbose))
    warnings.simplefilter("once", InsecureRequestWarning)
    SHORTDESC = opt.shortdesc
    DRYRUN = opt.dryrun
    DAYS = dayrange(opt.after, opt.before)
    PROJECTS = opt.project
    JSONFILE = opt.jsonfile
    TEXTFILE = opt.textfile
    HTMLFILE = opt.htmlfile
    TASKDATA = opt.taskdata
    USER = opt.user
    tabWithDateHour()
    remote = JiraFrontend(opt.restapi)
    if not args:
        args = ["projects"]
    run(remote, args)
