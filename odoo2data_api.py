#! /usr/bin/env python3

__copyright__ = "(C) 2021-2023 Guido Draheim, licensed under the Apache License 2.0"""
__version__ = "0.7.2101"

import logging
from typing import List, Dict, Union, Optional, Tuple, Any, cast

import sys
import re
import os.path as path
import json
import requests
import datetime
import dotnetrc
from dotgitconfig import git_config_value
from fnmatch import fnmatchcase as fnmatch

import tabtotext
from tabtotext import JSONList, JSONDict
Cookies = Any
Day = datetime.date
Num = float
UserID = int
SessionID = str
ProjID = int
TaskID = int
ProjREF = Union[ProjID, str]
TaskREF = Union[TaskID, str]
EntryID = int

logg = logging.getLogger(__name__ == "__main__" and path.basename(sys.argv[0]) or __name__)

ODOO_URL = ""
ODOO_DB = ""

dotnetrc.NETRC_CLEARTEXT = True

class OdooException(Exception):
    pass

def strDate(val: Union[str, Day]) -> str:
    if isinstance(val, (datetime.date, datetime.datetime)):
        return val.strftime("%Y-%m-%d")
    return val

def odoo_url() -> str:
    if ODOO_URL:
        return ODOO_URL
    value = git_config_value("odoo.url")
    if value:
        return value
    value = git_config_value("zeit.url")
    if value:
        return value
    return "https://example.odoo.com"

def odoo_db() -> str:
    """ see https://o2sheet.com/docs/retrieve-odoo-database-name/ """
    if ODOO_DB:
        return ODOO_DB
    value = git_config_value("odoo.db")
    if value:
        return value
    value = git_config_value("zeit.db")
    if value:
        return value
    return "prod-example"

# otter/odoo/rest.py#login
def odoo_login(url: str, db: str, username: str, password: str) -> Tuple[UserID, SessionID]:
    request_json = {
        "jsonrpc": "2.0",
        "params": {
            "db": db,
            "login": username,
            "password": password
        }
    }
    response = requests.post(url + '/web/session/authenticate', json=request_json)
    logg.debug("%s", response.json())
    # before: and 'result' in response.json():
    if response.status_code != 200 or 'error' in response.json():
        if 'error' in response.json():
            logg.error("Error during login:")
            logg.error("  %s", response.json()['error']['data']['message'])
        else:
            logg.error("Error during login")
        raise OdooException("error login")
    uid = cast(UserID, response.json()['result']['uid'])
    session = cast(SessionID, response.cookies['session_id'])
    return uid, session

# otter/odoo/rest.py#get_databases_json
def odoo_get_databases(url: str) -> JSONList:
    request_json = {
        "jsonrpc": "2.0",
        "context": {}
    }
    # endpoint only for Odoo version >= 10
    response = requests.get(url + '/web/database/list', json=request_json)
    if response.status_code != 200 or 'result' not in response.json():
        logg.error("ERROR FETCHING DATABASES")
        raise OdooException("error databases")
    return response.json()['result']  # type: ignore

# otter/odoo/rest.py#get_projects_json
def odoo_get_projects(url: str, cookies: Cookies) -> JSONList:
    request_json = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "model": "project.project",
            "fields": [
                "id",
                "name",
                "active"
            ],
            "sort": "id ASC"
        }
    }
    response = requests.post(f"{url}/web/dataset/search_read", json=request_json, cookies=cookies)
    if response.status_code != 200 or 'result' not in response.json():
        logg.error("ERROR GET PROJECTS")
        if "error" in response.json():
            logg.error("  %s", response.json()['error']['data']['message'])
        return []
    return response.json()['result']['records']  # type: ignore

# otter/odoo/rest.py#get_projects_tasks_json
def odoo_get_projects_tasks(url: str, cookies: Cookies) -> JSONList:
    request_json = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "model": "project.task",
            "domain": [
                ["project_id", "!=", False]
            ],
            "fields": [
                "id",
                "name",
                "active",
                "project_id"
            ],
            "sort": "id ASC"
        }
    }
    response = requests.post(f"{url}/web/dataset/search_read", json=request_json, cookies=cookies)
    if response.status_code != 200 or 'result' not in response.json():
        logg.error("ERROR GET PROJECT TASKS")
        if "error" in response.json():
            logg.error("  %s", response.json()['error']['data']['message'])
        return []
    return response.json()['result']['records']  # type: ignore

def odoo_get_project_tasks(url: str, cookies: Cookies, proj_id: ProjREF) -> JSONList:
    request_json = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "model": "project.task",
            "domain": [
                ["project_id", "=", proj_id]
            ],
            "fields": [
                "id",
                "name",
                "active",
                "project_id"
            ],
            "sort": "id ASC"
        }
    }
    response = requests.post(f"{url}/web/dataset/search_read", json=request_json, cookies=cookies)
    if response.status_code != 200 or 'result' not in response.json():
        logg.error("ERROR GET PROJECT TASKS")
        logg.debug("%s", response.json())
        if "error" in response.json():
            logg.error("  %s", response.json()['error']['data']['message'])
        return []
    return response.json()['result']['records']  # type: ignore

# otter/odoo/rest.py#get_records_json
def odoo_get_timesheet_records(url: str, cookies: Cookies, uid: UserID, entry_date: Optional[Day] = None) -> JSONList:
    dateref = datetime.date.today().strftime("%Y-%m-%d")
    # logg.debug("date ref = %s", dateref)
    if entry_date:
        ondate = strDate(entry_date)
        logg.debug("ondate %s", ondate)
        searching = [
            ["project_id", "!=", False],
            ["task_id", "!=", False],
            ["user_id", "=", uid],
            ["date", "=", ondate],  # <<<<
        ]
    else:
        searching = [
            ["project_id", "!=", False],
            ["task_id", "!=", False],
            ["user_id", "=", uid]
        ]

    request_json = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "model": "account.analytic.line",
            "domain": searching,
            'date': dateref,
            "sort": "id ASC"
        }
    }

    response = requests.post(f"{url}/web/dataset/search_read", json=request_json, cookies=cookies)

    if response.status_code != 200 or 'result' not in response.json():
        logg.error("ERROR GET TIMESHEET")
        logg.debug("%s", response.json())
        if "error" in response.json():
            logg.error("  %s", response.json()['error']['data']['message'])
        return []

    return response.json()['result']['records']  # type: ignore

def odoo_get_timesheet_record(url: str, cookies: Cookies, uid: UserID, proj_id: ProjREF, task_id: TaskREF, entry_date: Optional[Day] = None) -> JSONList:
    dateref = datetime.date.today().strftime("%Y-%m-%d")
    # logg.debug("date ref = %s", dateref)
    if entry_date:
        ondate = strDate(entry_date)
        logg.debug("ondate %s", ondate)
        searching = [
            ["project_id", "=", proj_id],
            ["task_id", "=", task_id],
            ["user_id", "=", uid],
            ["date", "=", ondate],  # <<<<
        ]
    else:
        searching = [
            ["project_id", "=", proj_id],
            ["task_id", "=", task_id],
            ["user_id", "=", uid]
        ]
    request_json = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "model": "account.analytic.line",
            "domain": searching,
            'date': dateref,
            "sort": "id ASC"
        }
    }

    # logg.debug("request %s", request_json)
    response = requests.post(f"{url}/web/dataset/search_read", json=request_json, cookies=cookies)

    if response.status_code != 200 or 'result' not in response.json():
        logg.error("ERROR GET TIMESHEET")
        logg.debug("%s", response.json())
        if "error" in response.json():
            logg.error("  %s", response.json()['error']['data']['message'])
        return []

    return response.json()['result']['records']  # type: ignore

# otter/odoo/rest.py#post_record
def odoo_add_timesheet_record(url: str, cookies: Cookies, uid: UserID, proj_id: ProjID, task_id: TaskID, entry_date: Day, entry_desc: str, entry_size: Num) -> bool:
    request_json = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "args": [
                {  # vals=
                    "date": strDate(entry_date),
                    "unit_amount": entry_size,
                    "name": entry_desc,
                    "project_id": proj_id,
                    "task_id": task_id
                }
            ],
            "model": "account.analytic.line",
            "method": "create",
            "kwargs": {
                "context": {
                    "uid": uid,
                }
            }
        }
    }

    response = requests.post(f"{url}/web/dataset/call_kw/account.analytic.line/create", json=request_json,
                             cookies=cookies)

    if response.status_code != 200 or 'result' not in response.json():
        logg.error("ERROR SET TIMESHEET")
        logg.debug("%s", response.json())
        if "error" in response.json():
            logg.error("  %s", response.json()['error']['data']['message'])
        return False

    return response.json()['result']  # type: ignore

def odoo_set_timesheet_record(url: str, cookies: Cookies, uid: UserID, proj_id: ProjID, task_id: TaskID, entry_date: Day, entry_desc: str, entry_size: Num) -> bool:
    existing = odoo_get_timesheet_record(url, cookies, uid, proj_id, task_id, entry_date)
    if not existing:
        return odoo_add_timesheet_record(url, cookies, uid, proj_id, task_id, entry_date, entry_desc, entry_size)
    if len(existing) > 1:
        logg.error("existing %sx\n%s", len(existing), existing[0])
        raise OdooException("found multiple records for account&date")
    logg.debug("existing %s", existing)
    entry_id = cast(EntryID, existing[0]["id"])
    logg.info("update existing record [%s]", entry_id)
    return odoo_write_timesheet_record(url, cookies, uid, entry_id, proj_id, task_id, entry_date, entry_desc, entry_size)

def odoo_write_timesheet_record(url: str, cookies: Cookies, uid: UserID, entry_id: EntryID, proj_id: ProjID, task_id: TaskID, entry_date: Day, entry_desc: str, entry_size: Num) -> bool:
    request_json = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "args": [[entry_id],  # ids=
                     {  # vals=
                "unit_amount": entry_size,
                "name": entry_desc,
                "date": strDate(entry_date),
                "project_id": proj_id,
                "task_id": task_id
            }
            ],
            "model": "account.analytic.line",
            "method": "write",
            "kwargs": {
                "context": {
                    "uid": uid,
                }
            }
        }
    }

    response = requests.post(f"{url}/web/dataset/call_kw/account.analytic.line/write", json=request_json,
                             cookies=cookies)

    if response.status_code != 200 or 'result' not in response.json():
        logg.error("ERROR SET TIMESHEET")
        logg.debug("%s", response.json())
        if "error" in response.json():
            logg.error("  %s", response.json()['error']['data']['message'])
        return False

    return response.json()['result']  # type: ignore

def odoo_delete_timesheet_record(url: str, cookies: Cookies, uid: UserID, entry_id: EntryID) -> bool:
    request_json = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "args": [[entry_id],  # ids=
                     ],
            "model": "account.analytic.line",
            "method": "unlink",
            "kwargs": {
                "context": {
                    "uid": uid,
                }
            }
        }
    }

    response = requests.post(f"{url}/web/dataset/call_kw/account.analytic.line/unlink", json=request_json,
                             cookies=cookies)

    if response.status_code != 200 or 'result' not in response.json():
        logg.error("ERROR SET TIMESHEET")
        logg.debug("%s", response.json())
        if "error" in response.json():
            logg.error("  %s", response.json()['error']['data']['message'])
        return False

    return response.json()['result']  # type: ignore

def odoo_get_users(url: str, cookies: Cookies) -> JSONList:
    request_json = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "model": "res.users",
            "fields": [
                "id",
                "name",
                "email",
                "active",
            ],
            "sort": "id ASC"
        }
    }
    response = requests.post(f"{url}/web/dataset/search_read", json=request_json, cookies=cookies)
    if response.status_code != 200 or 'result' not in response.json():
        logg.error("ERROR GET USERS")
        if "error" in response.json():
            logg.error("  %s", response.json()['error']['data']['message'])
        return []
    return response.json()['result']['records']  # type: ignore

# https://www.odoo.com/documentation/10.0/api_integration.html
# search / search_read / search_count
# fields_get
# create / write / unlink (add, update, remote)

class OdooConfig:
    url: str
    db: str
    user: Optional[str]
    site: Optional[str]
    def __init__(self, url: Optional[str] = None, db: Optional[str] = None, *,  #
                 user: Optional[str] = None, site: Optional[str] = None):
        self.url: str = url or odoo_url()
        self.db: str = db or odoo_db()
        self.site: Optional[str] = site
        self.user: Optional[str] = user
    def name(self) -> str:
        if self.site:
            return self.site
        return self.db
    def on_site(self, site: str) -> "OdooConfig":
        self.site = site
        return self
    def for_user(self, user: str) -> "OdooConfig":
        self.user = user
        return self

class Odoo:
    def __init__(self, config: Optional[OdooConfig] = None):
        self.config: OdooConfig = config or OdooConfig()
        self.uid: Optional[UserID] = None
        self.sid: Optional[str] = None
        self._projtasklist: Optional[JSONList] = None
        logg.debug("URL %s DB %s", self.url, self.config.db)
        self.user_name: Optional[str] = None
    @property
    def url(self) -> str:
        return self.config.url
    @property
    def db(self) -> str:
        return self.config.db
    @property
    def user(self) -> str:
        if self.user_name:
            return self.user_name
        return self.config.user or ""
    def login(self) -> UserID:
        username, password = dotnetrc.get_username_password(self.config.url)
        uid, sid = odoo_login(self.url, self.db, username, password)
        self.uid = uid
        self.sid = sid
        if self.user:
            self.uid = self.get_user_id(self.user)
        return self.uid
    def from_login(self) -> UserID:
        if not self.uid:
            return self.login()
        return self.uid
    def for_user(self, name: str) -> "Odoo":
        if not self.uid:
            self.uid = self.login()
        if name:
            self.uid = self.get_user_id(name)
            self.user_name = name
        return self
    def get_user_id(self, name: str, default: Optional[UserID] = None) -> UserID:
        uid = default or -1
        users = self.users()
        if name.endswith("@"):
            emailname = name.lower().strip()[:-1]
            for user in users:
                if "user_email" not in user: continue
                attr = cast(str, user["user_email"])
                if attr.lower().strip().split("@", 1)[0] == emailname:
                    uid = cast(UserID, user["user_id"])
        elif "@" in name:
            email = name.lower().strip()
            for user in users:
                if "user_email" not in user: continue
                attr = cast(str, user["user_email"])
                if attr.lower().strip() == email:
                    uid = cast(UserID, user["user_id"])
        elif "*" in name:
            named = name.lower().strip().replace(" ", ".")
            for user in users:
                if "user_fullname" not in user: continue
                attr = cast(str, user["user_fullname"])
                if fnmatch(attr.lower().strip().replace(" ", "."), named):
                    uid = cast(UserID, user["user_id"])
        else:
            named = name.lower().strip().replace(" ", ".")
            for user in users:
                if "user_fullname" not in user: continue
                attr = cast(str, user["user_fullname"])
                if attr.lower().strip().replace(" ", ".") == named:
                    uid = cast(UserID, user["user_id"])
        return uid
    def databases(self) -> List[str]:
        found = odoo_get_databases(self.url)
        logg.info("%s", found)
        return cast(List[str], found)
    def cookies(self) -> Cookies:
        uid = self.from_login()
        return requests.utils.cookiejar_from_dict({"session_id": self.sid})  # type: ignore
    def users(self) -> JSONList:
        found = odoo_get_users(self.url, self.cookies())
        return [{"user_id": item["id"], "user_fullname": item["name"], "user_email": item["email"]} for item in found if item["active"]]
    def projects(self) -> JSONList:
        found = odoo_get_projects(self.config.url, self.cookies())
        return [{"proj_id": item["id"], "proj_name": item["name"]} for item in found if item["active"]]
    def projects_tasks(self) -> JSONList:
        found = odoo_get_projects_tasks(self.config.url, self.cookies())
        return [{"task_id": item["id"], "task_name": item["name"],
                 "proj_id": item["project_id"][0], "proj_name": item["project_id"][1],  # type: ignore
                 } for item in found if item["active"]]
    def project_tasks(self, proj_id: ProjREF = 89) -> JSONList:
        found = odoo_get_project_tasks(self.url, self.cookies(), proj_id)
        return [{"task_id": item["id"], "task_name": item["name"],
                 "proj_id": item["project_id"][0], "proj_name": item["project_id"][1],  # type: ignore
                 } for item in found if item["active"]]
    def projtasklist(self) -> JSONList:
        if self._projtasklist is None:
            data = self.projects_tasks()
            self._projtasklist = data
            return data
        return self._projtasklist
    def proj_id(self, proj_id: ProjREF) -> int:
        if isinstance(proj_id, int):
            return proj_id
        projtask = self.projtasklist()
        for item in projtask:
            if item["proj_name"] == proj_id:
                return cast(int, item["proj_id"])
        logg.warning("could not resolve proj_id '%s'", proj_id)
        return proj_id  # type: ignore
    def task_id(self, proj_id: ProjREF, task_id: TaskREF) -> int:
        if isinstance(task_id, int):
            return task_id
        projtask = self.projtasklist()
        for item in projtask:
            if str(proj_id) == item["proj_name"] or str(proj_id) == str(item["proj_id"]):
                if item["task_name"] == task_id:
                    return cast(int, item["task_id"])
        logg.warning("could not resolve task_id '%s' for proj_id '%s'", task_id, proj_id)
        return task_id  # type: ignore
    def clean(self, rec: JSONDict) -> JSONDict:
        for key in list(rec.keys()):
            if key.startswith("display_"):
                del rec[key]
        for name in ["__last_update", "account_id", "create_date", "create_uid", "write_date", "write_uid",
                     "department_id", "general_account_id", "group_id", "holiday_id", "user_timer_id", "is_timer_running",
                     "is_so_line_edited", "l10n_de_document_title", "l10n_de_template_data", "move_id", "ref", "so_line",
                     "partner_id", "project_user_id", "tag_ids", "timer_pause", "timer_start", "timesheet_invoice_id"]:
            if name in rec:
                del rec[name]
        return rec
    def timesheet_records(self, date: Optional[datetime.date] = None) -> JSONList:
        uid = self.from_login()
        found = odoo_get_timesheet_records(self.url, self.cookies(), uid, date)
        # logg.info("%s", found)
        for rec in found:
            self.clean(rec)
        if found:
            logg.debug("%s", found[0])
        return [{"proj_id": item["project_id"][0], "proj_name": item["project_id"][1],  # type: ignore
                 "task_id": item["task_id"][0], "task_name": item["task_id"][1],  # type: ignore
                 "user_id": item["user_id"][0], "user_name": item["user_id"][1],  # type: ignore
                 "entry_size": item["unit_amount"], "entry_desc": item["name"],  # type: ignore
                 "entry_id": item["id"], "entry_date": item["date"],
                 } for item in found]
    def timesheet_record(self, proj: str, task: str, date: Optional[datetime.date] = None) -> JSONList:
        uid = self.from_login()
        found = odoo_get_timesheet_record(self.url, self.cookies(), uid, proj, task, date)
        # logg.info("%s", found)
        for rec in found:
            self.clean(rec)
        if found:
            logg.debug("%s", found[0])
        return [{"proj_id": item["project_id"][0], "proj_name": item["project_id"][1],  # type: ignore
                 "task_id": item["task_id"][0], "task_name": item["task_id"][1],  # type: ignore
                 "user_id": item["user_id"][0], "user_name": item["user_id"][1],  # type: ignore
                 "entry_size": item["unit_amount"], "entry_desc": item["name"],  # type: ignore
                 "entry_id": item["id"], "entry_date": item["date"],
                 } for item in found]
    def timesheet_delete(self, entry_id: EntryID) -> bool:
        uid = self.from_login()
        found = odoo_delete_timesheet_record(self.url, self.cookies(), uid,  #
                                             entry_id)
        logg.info("deleted %s", found)
        return found  # bool
    def timesheet_write(self, entry_id: EntryID, proj: ProjREF, task: TaskREF, date: Day, time: Num, desc: str) -> bool:
        uid = self.from_login()
        proj_id = self.proj_id(proj)
        task_id = self.task_id(proj, task)
        found = odoo_write_timesheet_record(self.url, self.cookies(), uid,  #
                                            entry_id, proj_id, task_id,  #
                                            entry_date=date, entry_size=time, entry_desc=desc)
        logg.info("written %s", found)
        return found  # bool
    def timesheet_create(self, proj: ProjREF, task: TaskREF, date: Day, time: Num, desc: str) -> bool:
        uid = self.from_login()
        proj_id = self.proj_id(proj)
        task_id = self.task_id(proj, task)
        found = odoo_add_timesheet_record(self.url, self.cookies(), uid, proj_id, task_id,
                                          entry_date=date, entry_size=time, entry_desc=desc)
        logg.info("created %s", found)
        return found  # bool
    def timesheet_update(self, proj: ProjREF, task: TaskREF, date: Day, time: Num, desc: str) -> bool:
        uid = self.from_login()
        proj_id = self.proj_id(proj)
        task_id = self.task_id(proj, task)
        found = odoo_set_timesheet_record(self.url, self.cookies(), uid, proj_id, task_id,
                                          entry_date=date, entry_size=time, entry_desc=desc)
        logg.info("updated %s", found)
        return found  # bool
    def timesheet(self, after: Day, before: Optional[Day] = None) -> JSONList:
        if not before:
            before = datetime.date.today()
        if after > before:
            logg.error("--after=DAY must be --before=DAY")
            raise OdooException("bad timespan for timesheet()")
        timespan = before - after
        if timespan.days > 63:
            logg.warning("--after=%s --before=%s is %s days", after.isoformat(), before.isoformat(), timespan.days + 1)
        else:
            logg.info("--after=%s --before=%s is %s days", after.isoformat(), before.isoformat(), timespan.days + 1)
        ondate = after
        records: JSONList = []
        for attempt in range(366):
            logg.debug("ondate %s   (after %s before %s)", ondate.isoformat(), after.isoformat(), before.isoformat())
            found = self.timesheet_records(ondate)
            if found:
                for record in found:
                    records.append(record)
            if ondate == before:
                break
            ondate += datetime.timedelta(days=1)
        return records

###########################################################################################
def run(arg: str) -> None:
    if arg in ["dbs", "databases"]:
        odoo = Odoo()
        logg.info(" ODOO URL %s DB %s", odoo.url, odoo.db)
        print(", ".join(odoo.databases()))
    if arg in ["pjs", "projects"]:
        odoo = Odoo()
        logg.info(" ODOO URL %s DB %s", odoo.url, odoo.db)
        data = odoo.projects()
        text = tabtotext.tabToGFM(data, ["proj_name", "proj_id"], {"proj_name": "'%s'"})
        print(text)
    if arg in ["tks", "tasks"]:
        odoo = Odoo()
        logg.info(" ODOO URL %s DB %s", odoo.url, odoo.db)
        data = odoo.projects_tasks()
        text = tabtotext.tabToGFM(data, ["proj_name", "task_name"], {"proj_name": "'%s'", "task_name": "'%s'"})
        print(text)
    if arg in ["tks1", "tasks1"]:
        odoo = Odoo()
        logg.info(" ODOO URL %s DB %s", odoo.url, odoo.db)
        data = odoo.project_tasks()
        text = tabtotext.tabToGFM(data, ["proj_name", "task_name"], {"proj_name": "'%s'", "task_name": "'%s'"})
        print(text)

def reset() -> None:
    pass  # only defined in the mockup

if __name__ == "__main__":
    from optparse import OptionParser
    cmdline = OptionParser("%prog [options] command...")
    cmdline.add_option("-g", "--gitcredentials", metavar="FILE", default="~/.netrc")
    cmdline.add_option("-v", "--verbose", action="count", default=0)
    cmdline.add_option("-d", "--db", metavar="name", default=ODOO_DB)
    cmdline.add_option("-e", "--url", metavar="url", default=ODOO_URL)
    opt, args = cmdline.parse_args()
    logging.basicConfig(level=logging.WARNING - 10 * opt.verbose)
    dotnetrc.set_password_filename(opt.gitcredentials)
    ODOO_URL = opt.url
    ODOO_DB = opt.db
    if not args:
        args = ["projects"]
    for arg in args:
        run(arg)
