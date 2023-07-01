#! /usr/bin/env python3
"""
Read and format Jira worklog entries. Provides additional reports.
"""

__copyright__ = "(C) 2022-2023 Guido Draheim, licensed under the Apache License 2.0"""
__version__ = "0.4.2102"

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
from timerange import get_date, is_dayrange, dayrange, last_sunday, next_sunday
from tabtotext import tabToJSON, tabToPrintWith, JSONDict, JSONList, JSONItem, viewFMT, setNoRight, tabWithDateHour

from jira2data_api import JiraFrontend, jiraGetWorklog, setJiraUser, setJiraURL

logg = logging.getLogger("JIRA2DATA")
DONE = (logging.WARNING + logging.ERROR) // 2
logging.addLevelName(DONE, "DONE")


NIX = ""
Day = datetime.date
DAYS = dayrange()

MAXROUNDS = 1000
LIMIT = 1000

PROJECTS: List[str] = []
PROJECTDEFAULT = "ASO"

LABELS = ""
FORMAT = ""
OUTPUT = ""
JSONFILE = ""
XLSXFILE = ""
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
    found = find_jira_odoo_values(taskname, desc)
    if found:
        return cast(str, found.proj)
    parts = taskname.split("-", 1)
    return parts[0]
def jira_odoo_task(taskname: str, desc: str = "") -> str:
    found = find_jira_odoo_values(taskname, desc)
    if found:
        return cast(str, found.task)
    return taskname
def find_jira_odoo_values(taskname: str, desc: str = "") -> Optional[OdooValues]:
    if jira_odoomap:
        values = jira_odoomap.values(taskname)
        if desc:
            for value in sorted(values, key=lambda x: cast(str, x.pref), reverse=True):
                if desc.startswith(cast(str, value.pref)):
                    return value
        if values:
            first = sorted(values, key=lambda x: cast(str, x.pref), reverse=True)
            return first[0]
    return None

def read_odoo_taskdata(filename: str) -> Dict[str, List[str]]:
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
    mapping: Dict[str, Dict[str, Optional[OdooValues]]] = {}
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
            if prefix not in mapping:
                mapping[prefix] = {}
            mapping[prefix][issue] = find_jira_odoo_values(issue, prefix)
            key = (started.strftime("%Y-%m-%d"), prefix)
            if key not in data:
                data[key] = []
            sunday = last_sunday(0, started)
            if weekstart is None or weekstart != sunday:
                nextsunday = next_sunday(0, sunday)
                line = "so **** WEEK %s-%s" % (sunday.strftime("%d.%m."), nextsunday.strftime("%d.%m."))
                data[(sunday.strftime("%Y-%m-%d"), "***")] = [line]
                weekstart = sunday
            weekday = WEEKDAYS[started.isoweekday()]
            hh = int(hours)
            mm = int((hours - hh) * 60)
            line = f"{weekday} {hh}:{mm:02} {desc}"
            data[key] += [line]
    zeit_txt = "# zeit.txt"
    for prefix in sorted(mapping):
        for issue in sorted(mapping[prefix]):
            values = mapping[prefix][issue]
            if values:
                proj = cast(str, values.proj)
                task = cast(str, values.task)
                yield {zeit_txt: f""">> {prefix} [{proj}] """}
                yield {zeit_txt: f""">> {prefix} "{task}" """}
                break
        issues = " ".join(sorted(mapping[prefix]))
        yield {zeit_txt: f">> {prefix} {issues}"}
    for key in sorted(data):
        lines = data[key]
        if len(lines) > 1:
            logg.warning(" multiple lines for day %s topic %s", *key)
            for line in lines:
                logg.warning(" | %s", line)
        for line in lines:
            yield {zeit_txt: line}

def run(remote: JiraFrontend, args: List[str]) -> int:
    global DAYS
    if TASKDATA:
        read_odoo_taskdata(TASKDATA)
    # execute verbs after arguments are scanned
    FMT = FORMAT
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
                    report_func = report_call.replace("(remote)", ".").replace(
                        "(data)", ".").replace("(", " ").replace(")", "").strip()
                    if report_name:
                        print(f"{report_name} {report_func}")
                report_name = None
            return 0
        report = arg.lower()
        if report in ["allprojects"]:
            result = list(jiraGetProjects(remote))  # list all Jira project trackers (including unused)
        elif report in ["projects", "pp"]:
            result = list(only_ActiveJiraProjects(jiraGetProjects(remote)))  # list Jira project trackers
        elif report in ["user"]:
            result = [{"url": remote.url(), "user": remote.user()}]  # show Jira connection info
        elif report in ["all", "ll"]:
            result = list(jiraGetProjectsIssuesInDays(remote, PROJECTS or [PROJECTDEFAULT]))  # projects with updates lately
        elif report in ["tickets", "tt"]:
            result = list(jiraGetUserIssuesInDays(remote))  # projects with updates lately
        elif report in ["allactivity", "aaa"]:
            result = list(jiraGetUserActivityInDays(remote))  # projects with updates lately
        elif report in ["activity", "aa"]:
            result = list(only_shorterActivity(jiraGetUserActivityInDays(remote)))  # projects with updates lately
            sortby = ["upcreated"]
        elif report in ["myactivity", "a"]:
            result = list(item for item in only_shorterActivity(
                jiraGetUserActivityInDays(remote)) if item["itemAuthor"] == remote.user())
            sortby = ["upcreated"]
        elif report in ["odoo", "data", "d"]:
            result = list(jiraOdooData(remote))  # list all Jira entries in Odoo update format
        elif report in ["zeit", "text", "z"]:
            result = list(jiraZeitData(remote))  # list all Jira entries in Zeit sheet format
            if not FMT:
                FMT = "wide"
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
        done = tabToPrintWith(result, OUTPUT, FMT,  # ..
                              selects=LABELS, sorts=sortby, legend=summary, reorder=lastdesc)
        if done:
            logg.log(DONE, " %s", done)
        if JSONFILE:
            FMT = "json"
            with open(JSONFILE, "w") as f:
                print(tabToJSON(result, sorts=sortby), file=f)
                logg.log(DONE, " %s written  %s %s", FMT, viewFMT(FMT), JSONFILE)
        if XLSXFILE:
            FMT = "xlsx"
            import tabtoxlsx
            tabtoxlsx.saveToXLSX(XLSXFILE, result, sorts=sortby)
            logg.log(DONE, " %s written  %s %s", FMT, viewFMT(FMT), XLSXFILE)
    return 0

if __name__ == "__main__":
    from optparse import OptionParser
    cmdline = OptionParser("%prog [-options] [help|commands..]", epilog=__doc__, version=__version__)
    cmdline.formatter.max_help_position = 30
    cmdline.add_option("-v", "--verbose", action="count", default=0, help="more verbose logging")
    cmdline.add_option("-^", "--quiet", action="count", default=0, help="less verbose logging")
    cmdline.add_option("-r", "--remote", metavar="URL", default="",
                       help="url to Jira API endpoint (or gitconfig jira.url)")
    cmdline.add_option("-a", "--after", metavar="DATE", default=None,
                       help="only evaluate entrys on and after [first of month]")
    cmdline.add_option("-b", "--before", metavar="DATE", default=None,
                       help="only evaluate entrys on and before [last of month]")
    cmdline.add_option("-j", "--project", metavar="JIRA", action="append", default=PROJECTS,
                       help="jira projects (%default) or " + PROJECTDEFAULT)
    cmdline.add_option("-L", "--labels", metavar="LIST", action="append",
                       default=[], help="select and format columns (new=col:h)")
    cmdline.add_option("-o", "--format", metavar="FMT", help="json|yaml|html|wide|md|htm|tab|csv|dat", default=FORMAT)
    cmdline.add_option("-O", "--output", metavar="CON", default=OUTPUT, help="redirect output to filename")
    cmdline.add_option("-J", "--jsonfile", metavar="PATH", default=JSONFILE, help="write also json data file")
    cmdline.add_option("-X", "--xlsxfile", metavar="FILE", default=XLSXFILE, help="write also xmlx data file")
    cmdline.add_option("-m", "--taskdata", metavar="PATH", default=TASKDATA, help="use odootopic mapping file")
    cmdline.add_option("-q", "--dryrun", action="count", default=0)
    cmdline.add_option("-Q", "--shortdesc", action="count", default=SHORTDESC,
                       help="present short lines for description [%default]")
    cmdline.add_option("-U", "--user", metavar="NAME", default=NIX,
                       help="filter for user [%default]")
    opt, args = cmdline.parse_args()
    logging.basicConfig(level=max(0, logging.WARNING - 10 * opt.verbose + 10 * opt.quiet))
    warnings.simplefilter("once", InsecureRequestWarning)
    SHORTDESC = opt.shortdesc
    DRYRUN = opt.dryrun
    DAYS = dayrange(opt.after, opt.before)
    PROJECTS = opt.project
    LABELS = ",".join(opt.labels)
    FORMAT = opt.format
    OUTPUT = opt.output
    JSONFILE = opt.jsonfile
    XLSXFILE = opt.xlsxfile
    TASKDATA = opt.taskdata
    setJiraUser(opt.user)
    tabWithDateHour()
    remote = JiraFrontend(opt.remote)
    if not args:
        args = ["projects"]
    elif len(args) == 1 and is_dayrange(args[0]):
        args += ["odoo"]
    elif len(args) >= 2 and is_dayrange(args[1]):
        logg.warning("a dayrange should come first: '%s' (reordering now)", args[1])
        args = [args[1], args[0]] + args[2:]
    run(remote, args)
