#! /usr/bin/env python3
"""
Synchronize odoo-import data (from zeit.txt) with Jira worklog entries.
"""

__copyright__ = "(C) 2022-2023 Guido Draheim, licensed under the Apache License 2.0"""
__version__ = "0.3.2097"

from typing import Optional, Union, Dict, List, Tuple, Iterable, Iterator, cast

import logging
import re
import os
import csv
import datetime

import tabtotext
import zeit2json as zeit_api
from tabtotext import viewFMT, str18, str27, str40
from tabtools import strHours
from timerange import get_date, first_of_month, last_of_month, last_sunday, next_sunday, dayrange, is_dayrange
import jira2data_api as jira_api
import netrc
import gitrc

# from math import round
from fnmatch import fnmatchcase as fnmatch
from tabtotext import JSONList, JSONDict, JSONBase, JSONItem
from odoo2data_api import EntryID, ProjID, TaskID

Day = datetime.date
Num = float

logg = logging.getLogger("zeit2jira")
DONE = (logging.WARNING + logging.ERROR) // 2
logging.addLevelName(DONE, "DONE")
NIX = ""
REMOTE = ""

DAYS = dayrange()
# [for zeit2json]
ZEIT_FILENAME = ""  # get_zeit_filename()
ZEIT_USER_NAME = ""  # get_user_name() in zeit
ZEIT_SUMMARY = "stundenzettel"
# [end zeit2json]

UPDATE = False
SHORTNAME = 0
SHORTDESC = 0
ONLYZEIT = 0

LABELS = ""
FORMAT = ""
OUTPUT = "-"
JSONFILE = ""
XLSXFILE = ""
CSVFILE = ""
CSVDATA = ""
XLSXDATA = ""
ZEITDATA = ""

def strDesc(val: str) -> str:
    if SHORTDESC:
        return str40(val)
    return val
def strName(value: JSONItem) -> str:
    if value is None:
        return "~"
    if SHORTDESC:
        return str27(value)
    return str(value)

def update_per_days(data: JSONList, user: str = NIX) -> JSONList:
    changes: JSONList = []
    tickets: Dict[str, JSONList] = {}
    for item in data:
        taskname: str = cast(str, item["Ticket"])
        if not taskname:
            continue
        if taskname not in tickets:
            tickets[taskname] = []
        tickets[taskname] += [item]
    if ONLYZEIT:
        return changes
    daydata: Dict[str, Dict[Day, JSONList]] = {}
    jira = jira_api.Worklogs(user=user, remote=REMOTE)
    logg.debug("tickets = %s", tickets)
    for taskname, items in tickets.items():
        for item in jira.timesheet(taskname, DAYS.after, DAYS.before):
            item_date: Day = get_date(cast(str, item["entry_date"]))
            item_size: Num = cast(Num, item["entry_size"])
            if taskname not in daydata:
                daydata[taskname] = {}
            if item_date not in daydata[taskname]:
                daydata[taskname][item_date] = []
            daydata[taskname][item_date] += [item]
    for taskname, items in tickets.items():
        for item in items:
            pref_id: str = cast(str, item["Topic"])
            new_desc: str = cast(str, item["Description"])
            new_date: Day = cast(Day, item["Date"])
            new_size: Num = cast(Num, item["Quantity"])
            found: JSONList = []
            if taskname not in daydata:
                logg.info("---: (%s) ----- no worklogs in jira!", taskname)
            elif new_date not in daydata[taskname]:
                logg.info("---: (%s) ----- no day data in jira %s", taskname, new_date)
            else:
                found = daydata[taskname][new_date]
            matching = []
            for old in found:
                old_entry_desc = cast(str, old["entry_desc"])
                if old_entry_desc.startswith(f"{pref_id} "):
                    matching.append(old)
            if not matching:
                logg.info("NEW: (%s) [%s] %s", new_date, strHours(new_size), strDesc(new_desc))
                if UPDATE:
                    done = jira.worklog_create(taskname, new_date, new_size, new_desc)
                    logg.info("-->: %s", done)
                changes.append({"act": "NEW", "at task": taskname,
                                "date": new_date, "desc": new_desc, "zeit": new_size})
            elif len(matching) > 1:
                logg.info(" *multiple: (%s) [%s] %s", new_date, strHours(new_size), strDesc(new_desc))
                for matched in matching:
                    _old_date: Day = cast(Day, matched["entry_date"])
                    _old_size: Num = cast(Num, matched["entry_size"])
                    _old_desc: str = cast(str, matched["entry_desc"])
            else:  # len(matching) == 1
                matched = matching[0]
                old_date: Day = cast(Day, matched["entry_date"])
                old_size: Num = cast(Num, matched["entry_size"])
                old_desc: str = cast(str, matched["entry_desc"])
                if old_size != new_size or old_desc != new_desc:
                    logg.info("old: (%s) [%s] %s", old_date, strHours(old_size), strDesc(old_desc))
                    logg.info("new: (%s) [%s] %s", new_date, strHours(new_size), strDesc(new_desc))
                    if UPDATE:
                        old_id = cast(EntryID, matched["entry_id"])
                        done = jira.worklog_update(old_id, taskname, new_date, new_size, new_desc)
                        logg.info("-->: %s", done)
                    changes.append({"act": "UPD", "at task": taskname,
                                    "date": new_date, "desc": new_desc, "zeit": new_size})
                else:
                    logg.info(" ok: (%s) [%s] %s", new_date, strHours(new_size), strDesc(new_desc))
    return changes

def summary_per_day(data: JSONList, user: str = NIX) -> JSONList:
    tickets: Dict[str, bool] = {}
    daydata: Dict[Day, JSONDict] = {}
    for item in data:
        taskname: str = cast(str, item["Ticket"])
        if not taskname:
            continue
        new_date: Day = cast(Day, item["Date"])
        new_size: Num = cast(Num, item["Quantity"])
        if new_date not in daydata:
            daydata[new_date] = {"date": new_date, "jira": 0, "zeit": 0}
        daydata[new_date]["zeit"] += new_size  # type: ignore
        tickets[taskname] = True
    if ONLYZEIT:
        return list(daydata.values())
    jira = jira_api.Worklogs(user=user, remote=REMOTE)
    for taskname, hint in tickets.items():
        for item in jira.timesheet(taskname, DAYS.after, DAYS.before):
            logg.info("............. %s", item)
            old_date: Day = get_date(cast(str, item["entry_date"]))
            old_size: Num = cast(Num, item["entry_size"])
            if old_date not in daydata:
                daydata[old_date] = {"date": old_date, "jira": 0, "zeit": 0}
            daydata[old_date]["jira"] += old_size  # type: ignore
    return list(daydata.values())

def jira_project(taskname: str) -> str:
    parts = taskname.split("-", 1)
    return parts[0]

def summary_per_project_ticket(data: JSONList, user: str = NIX) -> JSONList:
    tickets: Dict[str, str] = {}
    sumdata: Dict[str, JSONDict] = {}
    for item in data:
        taskname: str = cast(str, item["Ticket"])
        if not taskname:
            continue
        new_proj: str = jira_project(taskname)
        new_date: Day = cast(Day, item["Date"])
        new_size: Num = cast(Num, item["Quantity"])
        new_key = taskname
        if new_key not in sumdata:
            sumdata[new_key] = {"at proj": new_proj, "at task": taskname, "jira": 0, "zeit": 0}
        sumdata[new_key]["zeit"] += new_size  # type: ignore
        tickets[taskname] = new_proj
    if ONLYZEIT:
        return list(sumdata.values())
    dayjira: Dict[Day, JSONList] = {}
    jira = jira_api.Worklogs(user=user, remote=REMOTE)
    for taskname, projname in tickets.items():
        for item in jira.timesheet(taskname, DAYS.after, DAYS.before):
            old_date: Day = get_date(cast(str, item["entry_date"]))
            old_size: Num = cast(Num, item["entry_size"])
            old_key = taskname
            if old_key not in sumdata:
                sumdata[old_key] = {"at proj": projname, "at task": taskname, "jira": 0, "zeit": 0}
            sumdata[old_key]["jira"] += old_size  # type: ignore
    return list(sumdata.values())

def summary_per_project(data: JSONList, user: str = NIX) -> JSONList:
    sumdata = summary_per_project_ticket(data, user)
    sumproj: Dict[str, JSONDict] = {}
    for item in sumdata:
        proj_name = cast(str, item["at proj"])
        task_name = cast(str, item["at task"])
        if proj_name not in sumproj:
            sumproj[proj_name] = {"at proj": proj_name, "jira": 0, "zeit": 0}
        sumproj[proj_name]["jira"] += item["jira"]  # type: ignore
        sumproj[proj_name]["zeit"] += item["zeit"]  # type: ignore
    return list(sumproj.values())

def fnmatches(text: str, pattern: str) -> bool:
    for pat in pattern.split("|"):
        if fnmatch(text, pat + "*"):
            return True
    return False

def pref_desc(desc: str) -> str:
    if " " not in desc:
        return desc.strip()
    else:
        return desc.split(" ", 1)[0]

def summary_per_topic(data: JSONList, user: str = NIX) -> JSONList:
    tickets: Dict[str, str] = {}
    sumdata: Dict[str, JSONDict] = {}
    for item in data:
        taskname: str = cast(str, item["Ticket"])
        if not taskname:
            continue
        new_proj: str = jira_project(taskname)
        new_desc: str = cast(str, item["Description"])
        new_date: Day = cast(Day, item["Date"])
        new_size: Num = cast(Num, item["Quantity"])
        new_pref = pref_desc(new_desc)
        if new_pref not in sumdata:
            sumdata[new_pref] = {"at topic": new_pref, "jira": 0, "zeit": 0}
        sumdata[new_pref]["zeit"] += new_size  # type: ignore
        tickets[taskname] = new_proj
    if ONLYZEIT:
        return list(sumdata.values())
    jira = jira_api.Worklogs(user=user, remote=REMOTE)
    for taskname, projname in tickets.items():
        for item in jira.timesheet(taskname, DAYS.after, DAYS.before):
            old_desc: str = cast(str, item["entry_desc"])
            old_date: Day = get_date(cast(str, item["entry_date"]))
            old_size: Num = cast(Num, item["entry_size"])
            old_key = taskname
            old_pref = pref_desc(old_desc)
            if old_pref not in sumdata:
                sumdata[old_pref] = {"at topic": old_pref, "jira": 0, "zeit": 0}
            sumdata[old_pref]["jira"] += old_size  # type: ignore
    return list(sumdata.values())

def withNoTask(data: Iterable[JSONDict]) -> Iterator[JSONDict]:
    for item in data:
        if "Task" in item:
            del item["Task"]
        if "Project" in item:
            item["OdooProject"] = str18(item["Project"])
            del item["Project"]
        if "Description" in item:
            item["ShortDescription"] = strDesc(cast(str, item["Description"]))
            del item["Description"]
        yield item

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
                report_func = report_call.replace("(data", ".").replace("(", " ").replace(")", "").strip()
                if report_name:
                    print(f"{report_name} {report_func}")
            report_name = None
        return
    ###########################################################
    zeit_api.ZEIT_AFTER = DAYS.after.isoformat()
    zeit_api.ZEIT_BEFORE = DAYS.before.isoformat()
    zeit_api.ZEIT_USER_NAME = ZEIT_USER_NAME
    zeit_api.ZEIT_SUMMARY = ZEIT_SUMMARY
    conf = zeit_api.ZeitConfig(ZEITDATA, username=ZEIT_USER_NAME)
    zeit = zeit_api.Zeit(conf)
    if CSVDATA:
        data = tabtotext.readFromCSV(CSVDATA)
    elif XLSXDATA:
        import tabtoxlsx
        data = tabtoxlsx.readFromXLSX(XLSXDATA)
    else:
        data = zeit.read_entries2(DAYS.after, DAYS.before)
    if arg in ["json", "make"]:
        json_text = tabtotext.tabToJSON(data)
        json_file = conf.filename(DAYS.after) + ".json"
        with open(json_file, "w") as f:
            f.write(json_text)
        logg.log(DONE, "written %s (%s entries)", json_file, len(data))
        return
    if arg in ["csv", "make"]:
        csv_text = tabtotext.tabToCSV(data)
        csv_file = conf.filename(DAYS.after) + ".csv"
        with open(csv_file, "w") as f:
            f.write(csv_text)
        logg.log(DONE, "written %s (%s entries)", csv_file, len(data))
        return
    # ---------------------------------
    FMT = FORMAT
    summary = []
    results: JSONList = []
    if arg in ["zz", "zeit"]:
        results = list(withNoTask(data))   # list existing Odoo entries and associated Zeit metadata
    elif arg in ["uu", "update"]:
        results = update_per_days(data, ZEIT_USER_NAME)  # looks for prefix on the day, perhaps updating time and description
    elif arg in ["cc", "compare", "days"]:
        results = summary_per_day(data, ZEIT_USER_NAME)   # group by day across all Odoo projects
    elif arg in ["ee", "summarize", "tasks"]:
        results = summary_per_project_ticket(data, ZEIT_USER_NAME)  # group by Odoo project-and-task
    elif arg in ["ss", "summary"]:
        results = summary_per_project(data, ZEIT_USER_NAME)  # group by Odoo project
        sum_zeit = sum([float(cast(JSONBase, item["zeit"])) for item in results if item["zeit"]])
        sum_jira = sum([float(cast(JSONBase, item["jira"])) for item in results if item["jira"]])
        summary = [f"{sum_zeit} hours zeit", f"{sum_jira} hours jira"]
    elif arg in ["tt", "topics"]:
        results = summary_per_topic(data, ZEIT_USER_NAME)  # group by topic prefix in description
    else:
        logg.error("unknown report '%s'", arg)
        import sys
        logg.error("  hint: check available reports:    %s help", sys.argv[0])
    if results:
        if SHORTNAME:
            for item in results:
                if "at proj" in item:
                    item["at proj"] = strName(item["at proj"])
                if "at task" in item:
                    item["at task"] = strName(item["at task"])
        formats = {"zeit": "{:4.2f}", "odoo": "{:4.2f}", "summe": "{:4.2f}"}
        done = tabtotext.tabToPrintWithFormats(results, OUTPUT, FMT,  # ..
                                               selects=LABELS, formats=formats, legend=summary)
        if done:
            logg.log(DONE, " %s", done)
        if JSONFILE:
            FMT = "json"
            with open(JSONFILE, "w") as f:
                f.write(tabtotext.tabToJSON(results))
            logg.log(DONE, " %s written   %s '%s'", FMT, viewFMT(FMT), JSONFILE)
        if XLSXFILE:
            FMT = "xlsx"
            import tabtoxlsx
            tabtoxlsx.saveToXLSX(XLSXFILE, results)
            logg.log(DONE, " %s written   %s '%s'", FMT, viewFMT(FMT), XLSXFILE)

if __name__ == "__main__":
    from optparse import OptionParser
    cmdline = OptionParser("%prog [help|data|check|valid|update|compare|summarize|summary|topics]", epilog=__doc__)
    cmdline.formatter.max_help_position = 30
    cmdline.add_option("-v", "--verbose", action="count", default=0,
                       help="more verbose logging")
    cmdline.add_option("-r", "--remote", metavar="URL", default="",
                       help="url to Jira API endpoint (or gitconfig jira.url)")
    cmdline.add_option("-a", "--after", metavar="DATE", default=None,
                       help="only evaluate entrys on and after date")
    cmdline.add_option("-b", "--before", metavar="DATE", default=None,
                       help="only evaluate entrys on and before date")
    cmdline.add_option("-s", "--summary", metavar="TEXT", default=ZEIT_SUMMARY,
                       help="suffix for summary report [%default]")
    cmdline.add_option("-U", "--user-name", metavar="TEXT", default=ZEIT_USER_NAME,
                       help="user name for the output report (not for login)")
    # ..............
    cmdline.add_option("-q", "--shortname", action="count", default=SHORTNAME,
                       help="present short names for proj+task [%default]")
    cmdline.add_option("-Q", "--shortdesc", action="count", default=SHORTDESC,
                       help="present short lines for description [%default]")
    cmdline.add_option("-z", "--onlyzeit", action="count", default=ONLYZEIT,
                       help="present only local zeit data [%default]")
    cmdline.add_option("-L", "--labels", metavar="LIST", action="append", default=[], help="select and rename columns")
    cmdline.add_option("-o", "--format", metavar="FMT", help="json|yaml|html|wide|md|htm|tab|csv", default=FORMAT)
    cmdline.add_option("-O", "--output", metavar="CON", default=OUTPUT, help="redirect output to filename")
    cmdline.add_option("-J", "--jsonfile", metavar="FILE", default=JSONFILE, help="write also json data file")
    cmdline.add_option("-X", "--xlsxfile", metavar="FILE", default=XLSXFILE, help="write also xlsx data file")
    cmdline.add_option("-D", "--csvfile", metavar="FILE", default=CSVFILE, help="write also sCSV data file")
    cmdline.add_option("-d", "--csvdata", metavar="FILE", default=CSVDATA, help="use data from semicolonCSV file")
    cmdline.add_option("-x", "--xlsxdata", metavar="FILE", default=XLSXDATA, help="use data from xlsx data file")
    cmdline.add_option("-f", "--zeitdata", metavar="FILE", default=ZEITDATA, help="use data from this zeit.txt")
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
    REMOTE = opt.remote
    UPDATE = opt.update
    LABELS = ",".join(opt.labels)
    FORMAT = opt.format
    OUTPUT = opt.output
    JSONFILE = opt.jsonfile
    XLSXFILE = opt.xlsxfile
    CSVFILE = opt.csvfile
    CSVDATA = opt.csvdata
    XLSXDATA = opt.xlsxdata
    ZEITDATA = opt.zeitdata
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
    ZEIT_USER_NAME = opt.user_name
    ZEIT_SUMMARY = opt.summary
    DAYS = dayrange(opt.after, opt.before)
    if not args:
        args = ["make"]
    elif len(args) == 1 and is_dayrange(args[0]):
        args += ["compare"]
    elif len(args) >= 2 and is_dayrange(args[1]):
        logg.warning("a dayrange should come first: '%s' (reordering now)", args[1])
        args = [args[1], args[0]] + args[2:]
    for arg in args:
        run(arg)
