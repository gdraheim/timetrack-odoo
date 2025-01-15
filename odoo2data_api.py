#! /usr/bin/env python3

__copyright__ = "(C) 2021-2025 Guido Draheim, licensed under the Apache License 2.0"""
__version__ = "1.0.4023"

# pylint: disable=unused-import,missing-function-docstring
import logging
from typing import List, Dict, Union, Optional, Tuple, Any, cast

import sys
import re
import os.path as path
import json
import requests
import datetime
import dotnetrc
import urllib.request
import random
from dotnetrc import set_password_filename, get_username_password, str_get_username_password, str_username_password
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

NIX = ""
ODOO_URL = ""
ODOO_DB = ""
ODOO_USERNAME = ""
JSONRPC = "/jsonrpc"

dotnetrc.NETRC_CLEARTEXT = True

class OdooException(Exception):
    pass

# https://www.odoo.com/documentation/master/developer/howtos/web_services.html
def json_rpc(url: str, method: str, params: Any) -> Any:
    data = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": random.randint(0, 1000000000),
    }
    logg.debug("json data = %s", data)
    req = urllib.request.Request(url=url, data=json.dumps(data).encode(), headers={
        "Content-Type":"application/json",
    })
    reply = json.loads(urllib.request.urlopen(req).read().decode('UTF-8'))
    if reply.get("error"):
        raise OdooException(reply["error"])
    return reply["result"]

def odoo_call(url: str, service: str, method: str, *args: Any) -> Any:
    return json_rpc(url, "call", {"service": service, "method": method, "args": args})


def strDate(val: Union[str, Day]) -> str:
    if isinstance(val, (datetime.date, datetime.datetime)):
        return val.strftime("%Y-%m-%d")
    return val

def odoo_username() -> str:
    if ODOO_USERNAME:
        return ODOO_USERNAME
    value = git_config_value("user.name")
    if value:
        return value
    return "Max Mustermann"

def odoo_url_jsonrpc() -> str:
    return odoo_url() + "/jsonrpc"
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

def odoo_login(url: str, db: str,  username: str, password: str) -> UserID:
    username, password = get_username_password(url)
    logg.info("using %s", str_username_password(username, password))
    uid = odoo_call(F"{url}{JSONRPC}", "common", "login", db, username, password)
    return cast(UserID, uid)

def odoo_get_users(url: str, db:str, usr: UserID, pwd: str) -> JSONList:
    info = odoo_call(F"{url}{JSONRPC}", "object", "execute", db, usr, pwd, "res.users", "search_read", [], ['id', 'name', 'email', 'active'])
    # info = odoo_call(F"{url}{JSONRPC}", "object", "execute", db, usr, pwd, "hr.employee.public", "search_read", [], ['id', 'name', 'work_email', 'active'])
    return cast(JSONList, info)


def odoo_get_projects(url: str, db:str, usr: UserID, pwd: str) -> JSONList:
    # info = odoo_call(F"{url}{JSONRPC}", "object", "execute", db, usr, pwd, "project.project", "fields_get", [], ['string', 'type'])
    info = odoo_call(F"{url}{JSONRPC}", "object", "execute", db, usr, pwd, "project.project", "search_read", [], ['id', 'name', 'active'])
    return cast(JSONList, info)

def odoo_get_projects_tasks(url: str, db:str, usr: UserID, pwd: str) -> JSONList:
    # info = odoo_call(F"{url}{JSONRPC}", "object", "execute", db, usr, pwd, "project.task", "fields_get", [], ['string', 'type'])
    # info = odoo_call(F"{url}{JSONRPC}", "object", "execute", db, usr, pwd, "project.task", "search_read", ['project_id','!=', False], ['id', 'name', 'active', 'project_id'])
    info = odoo_call(F"{url}{JSONRPC}", "object", "execute", db, usr, pwd, "project.task", "search_read", [], ['id', 'name', 'active', 'project_id'])
    return cast(JSONList, info)

def odoo_get_project_tasks(url: str, db:str, usr: UserID, pwd: str, proj_id: ProjREF) -> JSONList:
    # info = odoo_call(F"{url}{JSONRPC}", "object", "execute", db, usr, pwd, "project.task", "fields_get", [], ['string', 'type'])
    # info = odoo_call(F"{url}{JSONRPC}", "object", "execute", db, usr, pwd, "project.task", "search_read", ['project_id','!=', False], ['id', 'name', 'active', 'project_id'])
    info = odoo_call(F"{url}{JSONRPC}", "object", "execute", db, usr, pwd, "project.task", "search_read", ['project_id','=', proj_id], ['id', 'name', 'active', 'project_id'])
    return cast(JSONList, info)


# otter/odoo/rest.py#get_records_json
def odoo_get_timesheet_records(url: str, db:str, usr: UserID, pwd: str, uid: UserID, entry_date: Optional[Day] = None) -> JSONList:
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

    info = odoo_call(F"{url}{JSONRPC}", "object", "execute", db, usr, pwd, "account.analytic.line", "search_read", searching, [])
    return info

def odoo_get_timesheet_record(url: str, db:str, usr: UserID, pwd: str, uid: UserID, proj_id: ProjREF, task_id: TaskREF, entry_date: Optional[Day] = None) -> JSONList:
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

    info = odoo_call(F"{url}{JSONRPC}", "object", "execute", db, usr, pwd, "account.analytic.line", "search_read", searching, [])
    return info


# otter/odoo/rest.py#post_record
def odoo_add_timesheet_record(url: str, db:str, usr: UserID, pwd: str, uid: UserID, proj_id: ProjID, task_id: TaskID, entry_date: Day, entry_desc: str, entry_size: Num) -> bool:
    args = [{  # vals=
                    "date": strDate(entry_date),
                    "unit_amount": entry_size,
                    "name": entry_desc,
                    "project_id": proj_id,
                    "task_id": task_id,
                    "user_id": uid
                }]
    info = odoo_call(F"{url}{JSONRPC}", "object", "execute", db, usr, pwd, "account.analytic.line", "create", args)
    return info

def odoo_set_timesheet_record(url: str, db:str, usr: UserID, pwd: str, uid: UserID, proj_id: ProjID, task_id: TaskID, entry_date: Day, entry_desc: str, entry_size: Num) -> bool:
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

def odoo_write_timesheet_record(url: str, db:str, usr: UserID, pwd: str, uid: UserID, entry_id: EntryID, proj_id: ProjID, task_id: TaskID, entry_date: Day, entry_desc: str, entry_size: Num) -> bool:
    args = [ entry_id]
    vals = { 
                "unit_amount": entry_size,
                "name": entry_desc,
                "date": strDate(entry_date),
                "project_id": proj_id,
                "task_id": task_id,
                "user_id": uid
            }
    info = odoo_call(F"{url}{JSONRPC}", "object", "execute", db, usr, pwd, "account.analytic.line", "write", args, vals)
    return info

def odoo_delete_timesheet_record(url: str, db:str, usr: UserID, pwd: str, uid: UserID, entry_id: EntryID) -> bool:
    args = [entry_id]
    info = odoo_call(F"{url}{JSONRPC}", "object", "execute", db, usr, pwd, "account.analytic.line", "unlink", args)
    return info



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
        self.usr: UserID = 0
        self.pwd: str = NIX
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
    def setup(self) -> UserID:
        username, password = get_username_password(self.url)
        self.usr = odoo_login(self.url, self.db, username, password)
        self.pwd = password
        if self.user:
            self.usr = self.get_user_id(self.user)
        return self.usr
    def from_login(self) -> UserID:
        if not self.usr:
            return self.setup()
        return self.usr
    def for_user(self, name: str) -> "Odoo":
        if not self.usr:
            self.usr = self.setup()
        if name:
            self.usr = self.get_user_id(name)
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
    def users(self) -> JSONList:
        self.from_login()
        found = odoo_get_users(self.url, self.db, self.usr, self.pwd)
        return [{"user_id": item["id"], "user_fullname": item["name"], "user_email": item["email"]} for item in found if item["active"]]
    def projects(self) -> JSONList:
        self.from_login()
        found = odoo_get_projects(self.url, self.db, self.usr, self.pwd)
        return [{"proj_id": item["id"], "proj_name": item["name"]} for item in found if item["active"]]
    def projects_tasks(self) -> JSONList:
        self.from_login()
        found = odoo_get_projects_tasks(self.url, self.db, self.usr, self.pwd)
        return [{"task_id": item["id"], "task_name": item["name"],
                 "proj_id": item["project_id"][0], "proj_name": item["project_id"][1],  # type: ignore
                 } for item in found if item["active"]]
    def project_tasks(self, proj_id: ProjREF = 89) -> JSONList:
        found = odoo_get_project_tasks(self.url, self.db, self.usr, self.pwd, proj_id)
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
        found = odoo_get_timesheet_records(self.url, self.db, self.usr, self.pwd, uid, date)
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
        found = odoo_get_timesheet_record(self.url, self.db, self.usr, self.pwd, uid, proj, task, date)
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
        found = odoo_delete_timesheet_record(self.url, self.db, self.usr, self.pwd, uid,  #
                                             entry_id)
        logg.info("deleted %s", found)
        return found  # bool
    def timesheet_write(self, entry_id: EntryID, proj: ProjREF, task: TaskREF, date: Day, time: Num, desc: str) -> bool:
        uid = self.from_login()
        proj_id = self.proj_id(proj)
        task_id = self.task_id(proj, task)
        found = odoo_write_timesheet_record(self.url, self.db, self.usr, self.pwd, uid,  #
                                            entry_id, proj_id, task_id,  #
                                            entry_date=date, entry_size=time, entry_desc=desc)
        logg.info("written %s", found)
        return found  # bool
    def timesheet_create(self, proj: ProjREF, task: TaskREF, date: Day, time: Num, desc: str) -> bool:
        uid = self.from_login()
        proj_id = self.proj_id(proj)
        task_id = self.task_id(proj, task)
        found = odoo_add_timesheet_record(self.url, self.db, self.usr, self.pwd, uid, proj_id, task_id,
                                          entry_date=date, entry_size=time, entry_desc=desc)
        logg.info("created %s", found)
        return found  # bool
    def timesheet_update(self, proj: ProjREF, task: TaskREF, date: Day, time: Num, desc: str) -> bool:
        uid = self.from_login()
        proj_id = self.proj_id(proj)
        task_id = self.task_id(proj, task)
        found = odoo_set_timesheet_record(self.url, self.db, self.usr, self.pwd, uid, proj_id, task_id,
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
    if arg in ["help"]:
        cmdline.print_help()
        print("\nCommands:")
        previous = ""
        for line in open(__file__):
            if previous.strip().replace("elif arg", "if arg").startswith("if arg in"):
                if "#" in line:
                    print(previous.strip().split(" arg in")[1], line.strip().split("#")[1])
                else:
                    print(previous.strip().split(" arg in")[1], line.strip())
            previous = line
        raise SystemExit()
    if arg in ["dbs", "databases"]:
        odoo = Odoo()
        logg.info(" ODOO URL %s DB %s", odoo.url, odoo.db)
        print(", ".join(odoo.databases()))
    if arg in ["pjs", "projects"]:
        odoo = Odoo()
        logg.info(" ODOO URL %s DB %s", odoo.url, odoo.db)
        data = odoo.projects()
        text = tabtotext.tabtoGFM(data, ["proj_name:'%s'", "proj_id"])
        print(text)
    if arg in ["tks", "tasks"]:
        odoo = Odoo()
        logg.info(" ODOO URL %s DB %s", odoo.url, odoo.db)
        data = odoo.projects_tasks()
        text = tabtotext.tabtoGFM(data, ["proj_name:'%s'", "task_name:'%s'"])
        print(text)
    if arg in ["tks1", "tasks1"]:
        odoo = Odoo()
        logg.info(" ODOO URL %s DB %s", odoo.url, odoo.db)
        data = odoo.project_tasks()
        text = tabtotext.tabtoGFM(data, ["proj_name:'%s'", "task_name:'%s'"])
        print(text)

def reset() -> None:
    pass  # only defined in the mockup

if __name__ == "__main__":
    from optparse import OptionParser
    cmdline = OptionParser("%prog [-options] [help|commands...]", version=__version__)
    cmdline.add_option("-v", "--verbose", action="count", default=0, help="more verbose logging")
    cmdline.add_option("-^", "--quiet", action="count", default=0, help="less verbose logging")
    cmdline.add_option("-g", "--gitcredentials", metavar="FILE", default="~/.netrc")
    cmdline.add_option("-d", "--db", metavar="name", default=ODOO_DB)
    cmdline.add_option("-e", "--url", metavar="url", default=ODOO_URL)
    opt, args = cmdline.parse_args()
    logging.basicConfig(level=max(0, logging.WARNING - 10 * opt.verbose + 10 * opt.quiet))
    dotnetrc.set_password_filename(opt.gitcredentials)
    ODOO_URL = opt.url
    ODOO_DB = opt.db
    if not args:
        args = ["projects"]
    for arg in args:
        run(arg)
