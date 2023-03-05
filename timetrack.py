#! /usr/bin/env python3

__copyright__ = "(C) 2019-2023 Guido Draheim, licensed under the Apache License 2.0"""
__version__ = "0.1.2097"

from typing import Optional, Union, Dict, List, Tuple, Iterable, cast

import logging
import re
import os
import csv
import datetime
import sqlite3
import os.path as path
from contextlib import closing
from configparser import ConfigParser

import tabtotext
import zeit2json as zeit_api
from timerange import get_date, first_of_month, last_of_month, last_sunday, next_sunday, dayrange, is_dayrange
import odoo2data_api as odoo_api
import netrc
import gitrc

# from math import round
from fnmatch import fnmatchcase as fnmatch
from tabtotext import JSONList, JSONDict, JSONBase, JSONItem, viewFMT
from odoo2data_api import EntryID, ProjID, TaskID

Day = datetime.date
Num = float

logg = logging.getLogger("timetrack")
DONE = (logging.WARNING + logging.ERROR) // 2
logging.addLevelName(DONE, "DONE")

USER_NAME = ""
PROJONLY = ""
PROJSKIP = ""

TIME_FILENAME = ""
TIME_SITENAME = ""

PRICES: List[str] = []
VAT = 0.10

DAYS = dayrange()
UPDATE = False
SHORTNAME = 0
SHORTDESC = 0
ONLYZEIT = 0

LABELS = ""
FORMAT = ""
OUTPUT = "-"
JSONFILE = ""
XLSXFILE = ""

SHORTNAME = True


def default_config(warn: bool = True) -> str:
    user_name = gitrc.git_config_value("user.name")
    user_mail = gitrc.git_config_value("user.email")
    odoo_url = gitrc.git_config_value("odoo.url")
    odoo_db = gitrc.git_config_value("odoo.db")
    odoo_email = gitrc.git_config_value("odoo.email")
    zeit_filename = gitrc.git_config_value("zeit.filename")
    jira_url = gitrc.git_config_value("jira.url")
    jira_user = gitrc.git_config_value("jira.user")
    if not user_name and warn:
        logg.error("~/.gitconfig [user] name= (missing)")
    if not user_mail and warn:
        logg.error("~/.gitconfig [user] email= (missing)")
    if not odoo_url and warn:
        logg.warning("~/.gitconfig [odoo] url= (missing)")
    if not odoo_db and warn:
        logg.warning("~/.gitconfig [odoo] db= (missing)")
    if not odoo_email and warn:
        logg.info("~/.gitconfig [odoo] email= (missing)")
    if not zeit_filename and warn:
        logg.info("~/.gitconfig [zeit] filename= (missing)")
    if not user_name or not user_mail:
        raise ValueError("~/.gitconfig not prepared with [user] name= / email=")
    if odoo_email:
        user_mail = odoo_email
    user_first = user_name.split(" ", 1)[0].lower()
    user_login, user_domain = user_mail.split("@", 1)
    user_site = user_domain.split(".", 1)[0]
    if not odoo_url:
        odoo_url = f"https://erp.{user_domain}"
    if not odoo_db:
        odoo_db = f"prod-{user_site}"
    if not zeit_filename:
        zeit_filename = "~/zeit{YEAR}.txt"
    if not jira_url:
        jira_url = f"https://jira.{user_domain}"
    if not jira_user:
        jira_user = f"{user_login}"
    conf = f"""
[{user_first}]
type = user
login = {user_login}

[{user_site}]
type = site
domain = {user_domain}

[odoo]
type = odoo
url = {odoo_url}
db = {odoo_db}

[zeit]
type = zeit
filename = {zeit_filename}

[jira]
type = jira
url = {jira_url}
user = {jira_user}
"""
    for num in range(1, 9):
        next_url = gitrc.git_config_value(f"jira{num}.url")
        next_user = gitrc.git_config_value(f"jira{num}.user")
        if next_url or next_user:
            if not next_url: next_url = jira_url
            if not next_user: next_user = jira_user
            conf += f"""
[jira{num}]
type = jira
url = {next_url}
user = {next_user}
"""
    return conf

class TimeConfig:
    def __init__(self, pathspec: Optional[str] = None, username: Optional[str] = None):
        self.pathspec = pathspec
        self.username = username
        self.sitename = None
    def user_name(self) -> Optional[str]:
        global USER_NAME
        if USER_NAME:
            return USER_NAME
        import gitrc
        return gitrc.git_config_value("user.name")
    def filespec(self) -> str:
        if self.pathspec:
            return self.pathspec
        global TIME_FILENAME
        if TIME_FILENAME:
            return TIME_FILENAME
        import gitrc
        found = gitrc.git_config_value("timetrack.filename")
        if found:
            return found
        return "~/timetrack{YEAR}.db3"
    def filename(self, after: Day) -> str:
        filename = self.filespec()
        return self.expand(filename, after)
    def expand(self, filename: str, after: Day) -> str:
        YEAR = after.year
        return path.expanduser(filename.format(**locals()))
    def site(self) -> str:
        if self.sitename:
            return self.sitename
        global TIME_SITENAME
        if TIME_SITENAME:
            return TIME_SITENAME
        import gitrc
        found = gitrc.git_config_value("timetrack.sitename")
        if found:
            return found
        found = gitrc.git_config_value("odoo.db")
        if found:
            return found
        return "moon"

class TimeDB:
    def __init__(self, conf: Optional[TimeConfig] = None):
        self.conf = conf or TimeConfig()
        self.conn: Optional[sqlite3.Connection] = None
    def db(self, after: Day) -> sqlite3.Connection:
        if self.conn is None:
            filename = self.conf.filename(after)
            logg.info("opening %s", filename)
            conn = sqlite3.connect(filename)
            self.conn = conn
        else:
            conn = self.conn
        return conn
    def tables(self, after: Day) -> None:
        with closing(self.db(after).cursor()) as cur:
            # res = cur.execute("SELECT tab, ver FROM versions")
            # cur.execute("DROP TABLE versions")
            cur.execute("CREATE TABLE IF NOT EXISTS versions(tab TEXT PRIMARY KEY, ver);")
            cur.execute("REPLACE INTO versions VALUES(?,?);", ('timesheet', 1.1))
            cur.execute("REPLACE INTO versions VALUES(?,?);", ('timespans', 1.2))
            cur.execute("REPLACE INTO versions VALUES(?,?);", ('timeevent', 1.2))
            for row in cur.execute("SELECT * FROM versions"):
                logg.debug("version  %s", row)
            cur.execute("""CREATE TABLE IF NOT EXISTS timesheet(
                site_name, site_type, proj_name, task_name, entry_date, entry_size, entry_desc)""")
            cur.execute("""CREATE TABLE IF NOT EXISTS timespans(
                site_name, site_type, proj_name, task_name, entry_date, entry_size, entry_desc)""")
            cur.execute("""CREATE TABLE IF NOT EXISTS timeevent(
                site_name, site_type, proj_name, task_name, entry_date, entry_time, entry_desc)""")
            cur.execute("""CREATE UNIQUE INDEX IF NOT EXISTS timesheet_date ON timesheet(
                site_name, site_type, proj_name, task_name, entry_date)""")
            cur.execute("""CREATE UNIQUE INDEX IF NOT EXISTS timespans_date ON timespans(
                site_name, site_type, proj_name, task_name, entry_date)""")
            cur.execute("""CREATE UNIQUE INDEX IF NOT EXISTS timeevent_date ON timeevent(
                site_name, site_type, proj_name, task_name, entry_date)""")
            found = cur.execute("select name from sqlite_schema where type = 'table'")
            for row in found:
                logg.debug("table %s", row)
    def commit(self) -> None:
        if self.conn:
            self.conn.commit()
    def close(self) -> None:
        if self.conn:
            self.conn.commit()
            self.conn = None
    def __del__(self) -> None:
        self.close()

def strName(value: JSONItem) -> str:
    if value is None:
        return "~"
    val = str(value)
    if SHORTNAME:
        if len(val) > 22:
            return val[:12] + "..." + val[-7:]
    return val

def pref_desc(desc: str) -> str:
    if " " not in desc:
        return desc.strip()
    else:
        return desc.split(" ", 1)[0]

def pull_odoo(after: Day, before: Day, conf: Optional[odoo_api.OdooConfig] = None) -> JSONList:
    r: JSONList = []
    conf = conf or odoo_api.OdooConfig()
    odoo = odoo_api.Odoo(conf)
    uses = TimeConfig()
    pull = TimeDB(uses)
    pull.tables(after)
    for item in odoo.timesheet(after, before):
        proj: str = cast(str, item["proj_name"])
        task: str = cast(str, item["task_name"])
        desc: str = cast(str, item["entry_desc"])
        pref: str = pref_desc(desc)
        date: Day = get_date(cast(str, item["entry_date"]))
        size: Num = cast(Num, item["entry_size"])
        logg.info(" %s", f"{date:%Y-%m-%d} {size:.2} : {desc}")
        site = uses.site()
        kind = "odoo"
        logg.info(" %s %s [%s] %s", site, kind, proj, task)
        with closing(pull.db(after).cursor()) as cur:
            ok = cur.execute("REPLACE INTO timesheet VALUES(?,?,?,?,?,?,?)", (site, kind, proj, task, date, size, desc))
            r.append({"row": ok.rowcount, "values": [site, kind, strName(proj), strName(task), f"{date:%Y-%m-%d}"]})
    pull.commit()
    return r


def pull_zeit(after: Day, before: Day, conf: Optional[zeit_api.ZeitConfig] = None) -> JSONList:
    r: JSONList = []
    conf = conf or zeit_api.ZeitConfig()
    zeit = zeit_api.Zeit(conf)
    uses = TimeConfig()
    pull = TimeDB(uses)
    pull.tables(after)
    for item in zeit.read_entries(after, before):
        proj: str = cast(str, item["Project"])
        task: str = cast(str, item["Task"])
        pref: str = cast(str, item["Topic"])  # explicit here
        date: Day = cast(Day, item["Date"])
        size: Num = cast(Num, item["Quantity"])
        desc: str = cast(str, item["Description"])
        logg.info(" %s", f"{date:%Y-%m-%d} {size:.2} : {desc}")
        site = uses.site()
        kind = "zeit"
        logg.info(" %s %s [%s] %s", site, kind, proj, task)
        with closing(pull.db(after).cursor()) as cur:
            ok = cur.execute("REPLACE INTO timespans VALUES(?,?,?,?,?,?,?)", (site, kind, proj, task, date, size, desc))
            r.append({"row": ok.rowcount, "values": [site, kind, strName(proj), strName(task), f"{date:%Y-%m-%d}"]})
    pull.commit()
    return r

def pull_jira(after: Day, before: Day, conf: Optional[odoo_api.OdooConfig] = None) -> JSONList:
    pass

def odoo_users(conf: Optional[odoo_api.OdooConfig] = None) -> JSONList:
    conf = conf or odoo_api.OdooConfig()
    odoo = odoo_api.Odoo(conf)
    users = odoo.users()
    return users

def set_object_types(config: ConfigParser) -> JSONList:
    return list(each_object_type(config))
def get_object_types(config: ConfigParser) -> JSONList:
    return list(each_object_type(config))
def each_object_type(config: ConfigParser) -> Iterable[JSONDict]:
    yield {"type": "user", "used": "mapping to external login names"}
    yield {"type": "zeit", "used": "access settings for zeit files"}
    yield {"type": "odoo", "used": "access settings for odoo systems"}
    yield {"type": "jira", "used": "access settings for jira systems"}
    yield {"type": "proxy", "used": "access setings for http proxies"}
    for name in config.sections():
        obj = config[name]
        typ = obj.get("type", "unknown")
        if typ in ["user", "zeit", "odoo", "jira", "proxy"]:
            yield {"type": typ, "name": name}
def pull_object_types(config: ConfigParser) -> JSONList:
    return list(each_pull_object_type(config))
def each_pull_object_type(config: ConfigParser) -> Iterable[JSONDict]:
    yield {"type": "zeit", "used": "get timespans from for zeit files"}
    yield {"type": "odoo", "used": "get timesheet from odoo systems"}
    yield {"type": "jira", "used": "get worklogs from jira systems"}
    for name in config.sections():
        obj = config[name]
        typ = obj.get("type", "unknown")
        if typ in ["zeit", "odoo", "jira"]:
            yield {"type": typ, "name": name}


def show_jira(name: str, config: ConfigParser) -> JSONList:
    return list(each_show_jira(name, config))
def each_show_jira(name: str, config: ConfigParser) -> Iterable[JSONDict]:
    for sec in config.sections():
        if not fnmatch(sec, name):
            continue
        obj = config[sec]
        if obj.get("type", "unknown") in ["jira"]:
            yield {"name": name, "type": "jira", "url": obj.get("url")}

def show_odoo(name: str, config: ConfigParser) -> JSONList:
    return list(each_show_odoo(name, config))
def each_show_odoo(name: str, config: ConfigParser) -> Iterable[JSONDict]:
    for sec in config.sections():
        if not fnmatch(sec, name):
            continue
        obj = config[sec]
        if obj.get("type", "unknown") in ["odoo"]:
            yield {"name": name, "type": "odoo", "url": obj.get("url"), "db": obj.get("db")}

def show_zeit(name: str, config: ConfigParser) -> JSONList:
    return list(each_show_zeit(name, config))
def each_show_zeit(name: str, config: ConfigParser) -> Iterable[JSONDict]:
    for sec in config.sections():
        if not fnmatch(sec, name):
            continue
        obj = config[sec]
        if obj.get("type", "unknown") in ["zeit"]:
            yield {"name": name, "type": "zeit", "filename": obj.get("filename")}

def show_user(name: str, config: ConfigParser) -> JSONList:
    return []

def run(config: ConfigParser, args: List[str]) -> JSONList:
    global DAYS
    verb = None
    summary: List[str] = []
    results: JSONList = []
    headers: List[str] = ["name", "type"]
    while args:
        arg = args[0]
        args = args[1:]
        if is_dayrange(arg):
            DAYS = dayrange(arg)
            logg.log(DONE, "%s -> %s %s", arg, DAYS.after, DAYS.before)
            continue
        if arg in ["help"]:
            report_name = None
            for line in open(__file__):
                if line.strip().replace("elif", "if").startswith("if arg in"):
                    report_name = line.split("if arg in", 1)[1].strip()
                    continue
                elif line.strip().startswith("results = "):
                    report_call = line.split("results = ", 1)[1].strip()
                    if report_name:
                        print(f"{report_name} {report_call}")
            report_name = None
            return [{"done": "help"}]
        if arg in ["conf", "config"]:
            found = default_config()
            print(found)
            continue
        if arg in ["with"]:
            if not args:
                logg.error("missing argument for 'with'")
                return [{"error": "missing argument"}]
            filename = args[0]
            args = args[1:]
            config2 = ConfigParser()
            config2.read(filename)
            config = config2
            continue
        if arg in ["get", "set", "pull"]:
            verb = arg
            if not args:
                if arg in ["get"]:  # any
                    results = get_object_types(config)
                elif arg in ["set"]:
                    results = set_object_types(config)
                elif arg in ["pull"]:
                    results = pull_object_types(config)
                else:
                    logg.error("unknown verb %s", verb)
                    return [{"error": "unknown verb"}]
            continue
        ###########################################################
        if verb and not config.has_section(arg):
            logg.error("no such object %s - use 'config' to check them", arg)
            raise ValueError("missing configuration")
        obj = config[arg]
        typ = obj.get("type", "unknown")
        if typ in ["unknown"]:
            logg.error("untyped object %s - use 'config to check it", arg)
            return [{"error": "untyped object"}]
        elif typ in ["zeit"]:
            user_name = obj.get("user", USER_NAME)
            file_spec = obj.get("filename")
            zeit_conf = zeit_api.ZeitConfig(file_spec)
            zeit_conf.for_user(user_name)
            if verb in ["pull"]:
                results = pull_zeit(DAYS.after, DAYS.before, conf=zeit_conf)
            elif verb in ["get"]:
                results = show_zeit(arg, config=config)
            else:
                logg.error("%s %s - not possible", verb, arg)
                return [{"error": "not possible"}]
        elif typ in ["odoo"]:
            user_name = obj.get("user", USER_NAME)
            odoo_url = obj.get("url")
            odoo_db = obj.get("db")
            odoo_conf = odoo_api.OdooConfig(odoo_url, odoo_db)
            odoo_conf.for_user(user_name)
            if verb in ["pull"]:
                results = pull_odoo(DAYS.after, DAYS.before, conf=odoo_conf)
            elif verb in ["get"]:
                results = show_odoo(arg, config=config)
            else:
                logg.error("%s %s - not possible", verb, arg)
                return [{"error": "not possible"}]
        elif typ in ["jira"]:
            jira_conf = None  # odoo_api.OdooConfig()
            if verb in ["pull"]:
                results = pull_jira(DAYS.after, DAYS.before, conf=odoo_conf)
            elif verb in ["get"]:
                results = show_jira(arg, config=config)
            else:
                logg.error("%s %s - not possible", verb, arg)
                return [{"error": "not possible"}]
        elif typ in ["user", "users"]:
            show_user(arg, config=config)
        else:
            logg.error("unknown object type % for  %s - use 'config to check it", typ, arg)
            return [{"error": "unknown object type"}]
    if results:
        FMT = FORMAT
        formats = {"zeit": "{:4.2f}", "odoo": "{:4.2f}", "summe": "{:4.2f}"}
        done = tabtotext.tabToPrintWith(results, OUTPUT, FMT,  # ..
                                        selects=LABELS, sorts=headers, formats=formats, legend=summary)
        if done:
            logg.log(DONE, " %s", done)
        if JSONFILE:
            FMT = "json"
            with open(JSONFILE, "w") as f:
                f.write(tabtotext.tabToJSON(results, headers))
            logg.log(DONE, " %s written   %s '%s'", FMT, viewFMT(FMT), JSONFILE)
        if XLSXFILE:
            FMT = "xlsx"
            import tabtoxlsx
            tabtoxlsx.saveToXLSX(XLSXFILE, results, headers)
            logg.log(DONE, " %s written   %s '%s'", FMT, viewFMT(FMT), XLSXFILE)
    return results

if __name__ == "__main__":
    from optparse import OptionParser
    cmdline = OptionParser("%prog [help|data|check|valid|update|compare|summarize|summary|topics] files...")
    cmdline.formatter.max_help_position = 30
    cmdline.add_option("--quiet", action="count", default=0,
                       help="less verbose logging")
    cmdline.add_option("-v", "--verbose", action="count", default=0,
                       help="more verbose logging")
    cmdline.add_option("-a", "--after", metavar="DATE", default=None,
                       help="only evaluate entrys on and after data")
    cmdline.add_option("-b", "--before", metavar="DATE", default=None,
                       help="only evaluate entrys on and before date")
    cmdline.add_option("-p", "--price", metavar="TEXT", action="append", default=PRICES,
                       help="pattern:price per hour [%default]")
    cmdline.add_option("--projskip", metavar="TEXT", default=PROJSKIP,
                       help="filter for odoo project [%default]")
    cmdline.add_option("-P", "--projonly", metavar="TEXT", default=PROJONLY,
                       help="filter for odoo project [%default]")
    cmdline.add_option("-U", "--user-name", metavar="TEXT", default=USER_NAME,
                       help="user name for the output report (not for login)")
    # ..............
    cmdline.add_option("-q", "--shortname", action="count", default=SHORTNAME,
                       help="present short names for proj+task [%default]")
    cmdline.add_option("-Q", "--shortdesc", action="count", default=SHORTDESC,
                       help="present short lines for description [%default]")
    cmdline.add_option("-z", "--onlyzeit", action="count", default=ONLYZEIT,
                       help="present only local zeit data [%default]")
    cmdline.add_option("-L", "--labels", metavar="LIST", action="append", default=[], help="select and format columns (new=col:h)")
    cmdline.add_option("-o", "--format", metavar="FMT", help="json|yaml|html|wide|md|htm|tab|csv|dat", default=FORMAT)
    cmdline.add_option("-O", "--output", metavar="CON", default=OUTPUT, help="redirect output to filename")
    cmdline.add_option("-J", "--jsonfile", metavar="FILE", default=JSONFILE, help="write also json data file")
    cmdline.add_option("-X", "--xlsxfile", metavar="FILE", default=XLSXFILE, help="write also xslx data file")
    cmdline.add_option("-g", "--gitcredentials", metavar="FILE", default=netrc.GIT_CREDENTIALS)
    cmdline.add_option("-G", "--netcredentials", metavar="FILE", default=netrc.NET_CREDENTIALS)
    cmdline.add_option("-E", "--extracredentials", metavar="FILE", default=netrc.NETRC_FILENAME)
    cmdline.add_option("-c", "--config", metavar="NAME=VALUE", action="append", default=[])
    cmdline.add_option("-y", "--update", action="store_true", default=UPDATE,
                       help="actually update odoo")
    opt, args = cmdline.parse_args()
    logging.basicConfig(level=max(0, logging.WARNING - 10 * opt.verbose))
    logg.setLevel(level=max(0, logging.WARNING - 10 * opt.verbose))
    # logg.addHandler(logging.StreamHandler())
    for value in opt.config:
        gitrc.git_config_override(value)
    netrc.set_password_filename(opt.gitcredentials)
    netrc.add_password_filename(opt.netcredentials, opt.extracredentials)
    config = ConfigParser()
    config.read_string(default_config(False))
    UPDATE = opt.update
    LABELS = ",".join(opt.labels)
    FORMAT = opt.format
    OUTPUT = opt.output
    JSONFILE = opt.jsonfile
    XLSXFILE = opt.xlsxfile
    ONLYZEIT = opt.onlyzeit
    SHORTDESC = opt.shortdesc
    SHORTNAME = opt.shortname
    ONLYZEIT = opt.onlyzeit
    if opt.shortname > 1:
        SHORTDESC = opt.shortname
    if opt.shortname > 2:
        ONLYZEIT = opt.shortname
    if opt.onlyzeit > 1:
        SHORTNAME = opt.onlyzeit
    if opt.onlyzeit > 2:
        SHORTDESC = opt.onlyzeit
    # zeit2json
    USER_NAME = opt.user_name
    PROJONLY = opt.projonly
    PROJSKIP = opt.projskip
    PRICES = opt.price
    DAYS = dayrange(opt.after, opt.before)
    if not args:
        args = ["make"]
    elif len(args) == 1 and is_dayrange(args[0]):
        args += ["odoo"]
    elif len(args) >= 2 and is_dayrange(args[1]):
        logg.warning("a dayrange should come first: '%s' (reordering now)", args[1])
        args = [args[1], args[0]] + args[2:]
    run(config, args)
