#! /usr/bin/python3

from typing import Optional, Union, Dict, List, Tuple, cast

import logging
import re
import os
import csv
import datetime
import sqlite3
import os.path as path
from contextlib import closing

import tabtotext
import zeit2json as zeit_api
from dayrange import get_date, first_of_month, last_of_month, last_sunday, next_sunday, dayrange, is_dayrange
import odoo_rest as odoo_api
import netrc
import gitrc

# from math import round
from fnmatch import fnmatchcase as fnmatch
from tabtotext import JSONList, JSONDict, JSONBase, JSONItem
from odoo_rest import EntryID, ProjID, TaskID

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

FORMAT = ""
OUTPUT = ""
TEXTFILE = ""
JSONFILE = ""
HTMLFILE = ""
XLSXFILE = ""

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
            for row in cur.execute("SELECT * FROM versions"):
                logg.debug("version  %s", row)
            cur.execute(
                "CREATE TABLE IF NOT EXISTS timesheet(site_name, site_type, proj_name, task_name, entry_date, entry_size, entry_desc)")
            cur.execute(
                "CREATE TABLE IF NOT EXISTS timespans(site_name, site_type, proj_name, task_name, entry_date, entry_size, entry_desc)")
            cur.execute(
                "CREATE TABLE IF NOT EXISTS timeevent(site_name, site_type, proj_name, task_name, entry_date, entry_time, entry_desc)")
            cur.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS timesheet_date ON timesheet(site_name, site_type, proj_name, task_name, entry_date)")
            cur.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS timespans_date ON timespans(site_name, site_type, proj_name, task_name, entry_date)")
            cur.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS timeevent_date ON timeevent(site_name, site_type, proj_name, task_name, entry_date)")
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

def editprog() -> str:
    return os.environ.get("EDIT", "mcedit")
def htmlprog() -> str:
    return os.environ.get("BROWSER", "chrome")
def xlsxprog() -> str:
    return os.environ.get("XLSVIEW", "oocalc")

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
            r.append({"row": str(ok)})
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
            r.append({"row": str(ok)})
    pull.commit()
    return r

def odoo_users(conf: Optional[odoo_api.OdooConfig] = None) -> JSONList:
    conf = conf or odoo_api.OdooConfig()
    odoo = odoo_api.Odoo(conf)
    users = odoo.users()
    return users

def run(arg: str) -> None:
    global DAYS
    if is_dayrange(arg):
        DAYS = dayrange(arg)
        logg.log(DONE, "%s -> %s %s", arg, DAYS.after, DAYS.before)
        return
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
        return
    ###########################################################
    zeit_conf = zeit_api.ZeitConfig(username=USER_NAME)
    odoo_conf = odoo_api.OdooConfig()
    summary: List[str] = []
    results: JSONList = []
    if arg in ["users"]:
        results = odoo_users(conf=odoo_conf)
    elif arg in ["pull-odoo", "pullodoo"]:
        results = pull_odoo(DAYS.after, DAYS.before, conf=odoo_conf)
    elif arg in ["pull-zeit", "pullzeit"]:
        results = pull_zeit(DAYS.after, DAYS.before, conf=zeit_conf)
    else:
        logg.error("unknown report '%s'", arg)
        import sys
        logg.error("  hint: check available reports:    %s help", sys.argv[0])
    if results:
        formats = {"zeit": " %4.2f", "odoo": " %4.2f", "summe": " %4.2f"}
        if not OUTPUT:
            print(tabtotext.tabToFMT(FORMAT, results, formats=formats, legend=summary))
        else:
            with open(OUTPUT, "w") as f:
                f.write(tabtotext.tabToFMT(FORMAT, results, formats=formats, legend=summary))
            logg.log(DONE, " %s written   %s '%s'", FORMAT, editprog(), OUTPUT)
        if JSONFILE:
            with open(JSONFILE, "w") as f:
                f.write(tabtotext.tabToJSON(results))
            logg.log(DONE, " json written   %s '%s'", editprog(), JSONFILE)
        if HTMLFILE:
            with open(HTMLFILE, "w") as f:
                f.write(tabtotext.tabToHTML(results))
            logg.log(DONE, " html written   %s '%s'", htmlprog(), HTMLFILE)
        if TEXTFILE:
            with open(TEXTFILE, "w") as f:
                f.write(tabtotext.tabToGFM(results, formats=formats))
            logg.log(DONE, " text written   %s '%s'", editprog(), TEXTFILE)
        if XLSXFILE:
            import tabtoxlsx
            tabtoxlsx.saveToXLSX(XLSXFILE, results)
            logg.log(DONE, " xlsx written   %s '%s'", xlsxprog(), XLSXFILE)

if __name__ == "__main__":
    from optparse import OptionParser
    cmdline = OptionParser("%prog [help|data|check|valid|update|compare|summarize|summary|topics] files...")
    cmdline.add_option("-v", "--verbose", action="count", default=0,
                       help="more verbose logging")
    cmdline.add_option("-a", "--after", metavar="DATE", default=None,
                       help="only evaluate entrys on and after [first of month]")
    cmdline.add_option("-b", "--before", metavar="DATE", default=None,
                       help="only evaluate entrys on and before [last of month]")
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
    cmdline.add_option("-o", "--format", metavar="FMT", help="json|yaml|html|wide|md|htm|tab|csv", default=FORMAT)
    cmdline.add_option("-O", "--output", metavar="FILE", default=OUTPUT)
    cmdline.add_option("-T", "--textfile", metavar="FILE", default=TEXTFILE)
    cmdline.add_option("-J", "--jsonfile", metavar="FILE", default=JSONFILE)
    cmdline.add_option("-H", "--htmlfile", metavar="FILE", default=HTMLFILE)
    cmdline.add_option("-X", "--xlsxfile", metavar="FILE", default=XLSXFILE)
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
    UPDATE = opt.update
    FORMAT = opt.format
    OUTPUT = opt.output
    TEXTFILE = opt.textfile
    JSONFILE = opt.jsonfile
    HTMLFILE = opt.htmlfile
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
    for arg in args:
        run(arg)
