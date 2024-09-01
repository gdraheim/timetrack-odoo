#! /usr/bin/env python3
"""
Interface to Jira as a method to read and store worklog entries
"""

__copyright__ = "(C) 2022-2024 Guido Draheim, licensed under the Apache License 2.0"""
__version__ = "0.4.3361"

from typing import Union, Dict, List, Any, Optional, Tuple, Iterable, Iterator, cast
from requests import Session, Response, HTTPError
import warnings
import logging
import json
import os
import re
import sys
import datetime
from urllib.parse import quote_plus as qq
from dotnetrc import get_username_password, str_get_username_password
from dotgitconfig import git_config_value
from timerange import get_date
from tabtotext import JSONDict, JSONList, JSONItem

logg = logging.getLogger(__name__ == "__main__" and os.path.basename(sys.argv[0]) or __name__)

def get_login() -> str:
    return os.environ.get("LOGIN", "") or os.environ.get("USER") or "admin"

Day = datetime.date
FrontendUrl = str
Verify = Union[bool, str]
NIX = ""

url_verify = False
url_timeout: Optional[int] = 20

MAXROUNDS = 1000
LIMIT = 1000

USER = NIX
JIRADEFAULT = "http://jira.host"  # RFC2606

def reset() -> None:
    pass  # for the mockup

def setJiraUser(user: str) -> None:
    global USER
    USER = user
def setJiraURL(url: FrontendUrl) -> None:
    global JIRADEFAULT
    JIRADEFAULT = url

class JiraFrontend:
    url_verify: Verify
    url_timeout: Optional[int]
    def __init__(self, remote: Optional[FrontendUrl] = None, verify: Optional[Verify] = None, timeout: Optional[int] = None):
        self.remote = remote
        if not self.remote:
            self.remote = git_config_value("jira.url")
            if not self.remote:
                logg.error("either set '-r http://url/to/jira' or add ~/.gitconfig [jira]url=http://url/to/jira")
                self.remote = JIRADEFAULT
        if self.remote.isalnum():
            found = git_config_value(self.remote, "url")
            if not found:
                logg.error(f"you chose '-r {remote}' but no such ~/.gitconfig [{remote}]url=http://url/to/jira")
                self.remote = f"https://{remote}.host"
            else:
                logg.debug(f"found '-r {remote}' is {found}")
                self.remote = found
        if verify is None:
            self.url_verify = url_verify
        else:
            self.url_verify = verify
        if timeout is None:
            if url_timeout and url_timeout < 900:
                self.url_timeout = int(url_timeout)
            else:
                self.url_timeout = int(git_config_value("jira.timeout") or "20")
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
            session.auth = get_username_password(url)
            self._sessions[url] = session
        return self._sessions[url]
    def pwinfo(self) -> str:
        return str_get_username_password(self.url()) + " for " + self.url()
    def user(self, url: Optional[str] = None) -> str:
        if self._user:
            return self._user
        if USER:
            self._user = USER
            if self._user:
                return self._user
        jira_user = git_config_value("jira.user")
        if jira_user:
            logg.info("user: using gitconfig jira.user")
            self._user = jira_user
            if self._user:
                return self._user
        user_name = git_config_value("user.name")
        # search jira users by name?
        user_mail = git_config_value("user.email")
        # search jira users by email?
        url = url or self.url()
        auth = get_username_password(url)
        if auth:
            logg.info("user: using dotnetrc authuser")
            self._user = auth[0]
            if self._user:
                return self._user
        logg.info("user: fallback to local login user")
        login_user = get_login()
        self._user = login_user
        return login_user

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
        logg.error("%s => %s\n", dir(r), r.text)
        if r.status_code == 404:
            logg.info("no such jira ticket: %s", issue)
            return  # ticket
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
    def __init__(self, user: str = NIX, remote: str = NIX) -> None:
        self.remote = JiraFrontend(remote)
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
