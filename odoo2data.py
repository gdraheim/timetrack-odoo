#! /usr/bin/python3

from typing import Optional, Union, Dict, List, Tuple, cast, Iterable

import logging
import re
import os
import csv
import datetime

import tabtotext
import zeit2json
from dayrange import get_date, first_of_month, last_of_month, last_sunday, next_sunday, dayrange, is_dayrange
import odoo_rest as odoo_api
import netrc
import gitrc

# from math import round
from fnmatch import fnmatchcase as fnmatch
from tabtotext import JSONList, JSONDict, JSONBase, JSONItem, viewFMT
from odoo_rest import EntryID, ProjID, TaskID

Day = datetime.date
Num = float

logg = logging.getLogger("odoo2data")
DONE = (logging.WARNING + logging.ERROR) // 2
logging.addLevelName(DONE, "DONE")

DAYS = dayrange()

PRICES: List[str] = []
PRICE10 = 10
PRICEVAT = 0.19

SHORTNAME = 0
ONLYZEIT = 0
ADDFOOTER = 0

ODOO_PROJSKIP = ""
ODOO_PROJONLY = ""
ODOO_SUMMARY = ""

FOR_USER: List[str] = []

FORMAT = ""
OUTPUT = ""
JSONFILE = ""
XLSXFILE = ""

EURO = "euro"

def strName(value: JSONItem) -> str:
    if value is None:
        return "~"
    val = str(value)
    if SHORTNAME:
        if len(val) > 27:
            return val[:17] + "..." + val[-7:]
    return val

def get_proj_price_rate(proj: str) -> int:
    rate = 0
    for price in PRICES:
        if ":" in price:
            proj_name, proj_rate = price.split(":", 1)
            proj_pattern = (proj_name if "*" in proj_name else proj_name + "*")
            if fnmatches(proj, proj_pattern):
                rate = int(proj_rate)
        else:
            rate = int(price)
    if not rate:
        gitrc_price = gitrc.git_config_value("zeit.price")
        if gitrc_price:
            rate = int(gitrc_price)
    if not rate:
        rate = PRICE10  # ensure that price is not a copy of hours
    return rate

def get_price_vat() -> float:
    gitrc_vat = gitrc.git_config_value("zeit.vat")
    if gitrc_vat:
        return float(gitrc_vat)
    else:
        return PRICEVAT

def odoo_all_users() -> JSONList:
    odoo = odoo_api.Odoo()
    data = odoo.users()
    return data

def odoo_all_projects() -> JSONList:
    odoo = odoo_api.Odoo()
    data = odoo.projects()
    return data

def odoo_all_projects_tasks() -> JSONList:
    odoo = odoo_api.Odoo()
    data = odoo.projects_tasks()
    return data

def odoo_users() -> JSONList:
    return list(each_odoo_users())
def each_odoo_users() -> Iterable[JSONDict]:
    for item in odoo_all_users():
        name = cast(str, item["user_email"]).lower() + "|" + cast(str, item["user_fullname"]).lower()
        if ODOO_PROJONLY:
            if not fnmatches(name, ODOO_PROJONLY): continue
        if ODOO_PROJSKIP:
            if fnmatches(name, ODOO_PROJSKIP): continue
        yield item

def odoo_projects() -> JSONList:
    return list(each_odoo_projects())
def each_odoo_projects() -> Iterable[JSONDict]:
    for item in odoo_all_projects():
        name = cast(str, item["proj_name"]).lower()
        if ODOO_PROJONLY:
            if not fnmatches(name, ODOO_PROJONLY): continue
        if ODOO_PROJSKIP:
            if fnmatches(name, ODOO_PROJSKIP): continue
        yield item

def odoo_projects_tasks() -> JSONList:
    return list(each_odoo_projects_tasks())
def each_odoo_projects_tasks() -> Iterable[JSONDict]:
    for item in odoo_all_projects_tasks():
        name = cast(str, item["proj_name"]).lower()
        if ODOO_PROJONLY:
            if not fnmatches(name, ODOO_PROJONLY): continue
        if ODOO_PROJSKIP:
            if fnmatches(name, ODOO_PROJSKIP): continue
        yield item

# ========================================================================

def work_data(odoodata: Optional[JSONList] = None) -> JSONList:
    if not odoodata:
        odoo = odoo_api.Odoo().for_user(FOR_USER[0] if FOR_USER else "")
        odoodata = odoo.timesheet(DAYS.after, DAYS.before)
    # return list(odoodata)
    return list(_work_data(odoodata))
def _work_data(odoodata: JSONList) -> Iterable[JSONDict]:
    for item in odoodata:
        proj_name: str = cast(str, item["proj_name"])
        task_name: str = cast(str, item["task_name"])
        odoo_date: Day = get_date(cast(str, item["entry_date"]))  # in case we use raw zeit
        odoo_size: Num = cast(Num, item["entry_size"])
        odoo_desc: str = cast(str, item["entry_desc"])
        yield {"at proj": proj_name, "at task": task_name,
               "at date": odoo_date, "odoo": odoo_size, "worked on": odoo_desc}

WEEKDAYS = ["so", "mo", "di", "mi", "do", "fr", "sa", "so"]

def work_zeit(odoodata: Optional[JSONList] = None) -> JSONList:
    if not odoodata:
        odoo = odoo_api.Odoo().for_user(FOR_USER[0] if FOR_USER else "")
        odoodata = odoo.timesheet(DAYS.after, DAYS.before)
    # return list(odoodata)
    return list(_work_zeit(odoodata))
def _work_zeit(odoodata: JSONList) -> Iterable[JSONDict]:
    data: Dict[Tuple[str, str], List[str]] = {}
    mapping: Dict[str, str] = {}
    projnames: Dict[str, str] = {}
    tasknames: Dict[str, str] = {}
    weekstart = None
    for item in odoodata:
        proj_name: str = cast(str, item["proj_name"])
        task_name: str = cast(str, item["task_name"])
        odoo_date: Day = get_date(cast(str, item["entry_date"]))  # in case we use raw zeit
        odoo_size: Num = cast(Num, item["entry_size"])
        odoo_desc: str = cast(str, item["entry_desc"])
        prefix = odoo_desc.split(" ", 1)[0]
        mapping[prefix] = ""
        projnames[prefix] = proj_name
        tasknames[prefix] = task_name
        key = (odoo_date.strftime("%Y-%m-%d"), prefix)
        if key not in data:
            data[key] = []
        sunday = last_sunday(0, odoo_date)
        if weekstart is None or weekstart != sunday:
            nextsunday = next_sunday(0, sunday)
            line = "so **** WEEK %s-%s" % (sunday.strftime("%d.%m."), nextsunday.strftime("%d.%m."))
            data[(sunday.strftime("%Y-%m-%d"), "***")] = [line]
            weekstart = sunday
        weekday = WEEKDAYS[odoo_date.isoweekday()]
        hours = odoo_size
        desc = odoo_desc.strip()
        hh = int(hours)
        mm = int((hours - hh) * 60)
        line = f"{weekday} {hh}:{mm:02} {desc}"
        data[key] += [line]
    zeit_txt = "# zeit.txt"
    for prefix in sorted(mapping):
        issue = mapping[prefix]
        proj = projnames[prefix]
        task = tasknames[prefix]
        if proj:
            yield {zeit_txt: f""">> {prefix} [{proj}] """}
        if task:
            yield {zeit_txt: f""">> {prefix} "{task}" """}
        if issue:
            yield {zeit_txt: f""">> {prefix} {issue} """}
    for key in sorted(data):
        lines = data[key]
        if len(lines) > 1:
            logg.warning(" multiple lines for day %s topic %s", *key)
            for line in lines:
                logg.warning(" | %s", line)
        for line in lines:
            yield {zeit_txt: line}

# ========================================================================
def summary_per_day(odoodata: Optional[JSONList] = None) -> JSONList:
    if not odoodata:
        odoo = odoo_api.Odoo().for_user(FOR_USER[0] if FOR_USER else "")
        odoodata = odoo.timesheet(DAYS.after, DAYS.before)
    return _summary_per_day(odoodata)
def _summary_per_day(odoodata: JSONList) -> JSONList:
    daydata: Dict[Day, JSONDict] = {}
    for item in odoodata:
        odoo_date: Day = get_date(cast(str, item["entry_date"]))
        odoo_size: Num = cast(Num, item["entry_size"])
        weekday = odoo_date.isoweekday()
        weekday_name = ["so", "mo", "di", "mi", "do", "fr", "sa", "so", "mo"][weekday + 1]
        if odoo_date not in daydata:
            daydata[odoo_date] = {"date": odoo_date, "day": weekday_name, "odoo": 0}
        daydata[odoo_date]["odoo"] += odoo_size  # type: ignore
    return list(daydata.values())

def summary_per_project_task(odoodata: Optional[JSONList] = None) -> JSONList:
    if not odoodata:
        odoo = odoo_api.Odoo().for_user(FOR_USER[0] if FOR_USER else "")
        odoodata = odoo.timesheet(DAYS.after, DAYS.before)
    return _summary_per_project_task(odoodata)
def _summary_per_project_task(odoodata: JSONList) -> JSONList:
    sumdata: Dict[Tuple[str, str], JSONDict] = {}
    for item in odoodata:
        proj_name: str = cast(str, item["proj_name"])
        task_name: str = cast(str, item["task_name"])
        odoo_date: Day = get_date(cast(str, item["entry_date"]))
        odoo_size: Num = cast(Num, item["entry_size"])
        odoo_key = (proj_name, task_name)
        if ODOO_PROJONLY:
            if not fnmatches(proj_name, ODOO_PROJONLY): continue
        if ODOO_PROJSKIP:
            if fnmatches(proj_name, ODOO_PROJSKIP): continue
        if odoo_key not in sumdata:
            sumdata[odoo_key] = {"at proj": proj_name, "at task": task_name, "odoo": 0}
        sumdata[odoo_key]["odoo"] += odoo_size  # type: ignore
    return list(sumdata.values())

def summary_per_project(odoodata: Optional[JSONList] = None) -> JSONList:
    if not odoodata:
        odoo = odoo_api.Odoo().for_user(FOR_USER[0] if FOR_USER else "")
        odoodata = odoo.timesheet(DAYS.after, DAYS.before)
    return _summary_per_project(odoodata)
def _summary_per_project(odoodata: JSONList) -> JSONList:
    sumdata = _summary_per_project_task(odoodata)
    sumproj: Dict[str, JSONDict] = {}
    for item in sumdata:
        proj_name = cast(str, item["at proj"])
        task_name = cast(str, item["at task"])
        if proj_name not in sumproj:
            sumproj[proj_name] = {"at proj": proj_name, "odoo": 0}
        sumproj[proj_name]["odoo"] += item["odoo"]  # type: ignore
    return list(sumproj.values())

def reports_per_project(odoodata: Optional[JSONList] = None) -> JSONList:
    if odoodata:
        m = 0
        logg.info("%s: zeit", m)
        result = _report_per_project(odoodata, focus=m)
        users = FOR_USER
    else:
        result = []
        users = FOR_USER if FOR_USER else [""]
    for m, user in enumerate(users):
        logg.info("%i: %s", m + 1, user)
        odoo = odoo_api.Odoo().for_user(user)
        odoodata = odoo.timesheet(DAYS.after, DAYS.before)
        result += _report_per_project(odoodata, focus=m + 1)
    return sorted(result, key=lambda r: (r["am"], r["at proj"], r["m"]))
def report_per_project(odoodata: Optional[JSONList] = None) -> JSONList:
    if not odoodata:
        odoo = odoo_api.Odoo().for_user(FOR_USER[0] if FOR_USER else "")
        odoodata = odoo.timesheet(DAYS.after, DAYS.before)
    return _report_per_project(odoodata)
def _report_per_project(odoodata: JSONList, focus: int = 0) -> JSONList:
    sumdata = _monthly_per_project(odoodata)
    sumvals: JSONList = []
    for item in sumdata:
        new_month = cast(str, item["am"])
        proj_name = cast(str, item["at proj"])
        odoo_size = cast(float, item["odoo"])
        price_rate = get_proj_price_rate(proj_name)
        elem: JSONDict = {"am": new_month, "at proj": proj_name, "odoo": odoo_size, "m": focus,
                          "satz": int(price_rate), "summe": round(price_rate * odoo_size, 2)}
        sumvals.append(elem)
    return sumvals

def monthly_per_project(odoodata: Optional[JSONList] = None) -> JSONList:
    if not odoodata:
        odoo = odoo_api.Odoo().for_user(FOR_USER[0] if FOR_USER else "")
        odoodata = odoo.timesheet(DAYS.after, DAYS.before)
    return _monthly_per_project(odoodata)
def _monthly_per_project(odoodata: JSONList) -> JSONList:
    sumdata = _monthly_per_project_task(odoodata)
    sumproj: Dict[Tuple[str, str], JSONDict] = {}
    for item in sumdata:
        new_month = cast(str, item["am"])
        proj_name = cast(str, item["at proj"])
        task_name = cast(str, item["at task"])
        new_key = (new_month, proj_name)
        if new_key not in sumproj:
            sumproj[new_key] = {"am": new_month, "at proj": proj_name, "odoo": 0}
        sumproj[new_key]["odoo"] += item["odoo"]  # type: ignore
    return list(sumproj.values())

def monthly_per_project_task(odoodata: Optional[JSONList] = None) -> JSONList:
    if not odoodata:
        odoo = odoo_api.Odoo().for_user(FOR_USER[0] if FOR_USER else "")
        odoodata = odoo.timesheet(DAYS.after, DAYS.before)
    return _monthly_per_project_task(odoodata)
def _monthly_per_project_task(odoodata: JSONList) -> JSONList:
    sumdata: Dict[Tuple[str, str, str], JSONDict] = {}
    for item in odoodata:
        proj_name: str = cast(str, item["proj_name"])
        task_name: str = cast(str, item["task_name"])
        odoo_date: Day = get_date(cast(str, item["entry_date"]))
        odoo_size: Num = cast(Num, item["entry_size"])
        odoo_month = "M%02i" % odoo_date.month
        odoo_key = (odoo_month, proj_name, task_name)
        if ODOO_PROJONLY:
            if not fnmatches(proj_name, ODOO_PROJONLY): continue
        if ODOO_PROJSKIP:
            if fnmatches(proj_name, ODOO_PROJSKIP): continue
        if odoo_key not in sumdata:
            sumdata[odoo_key] = {"am": odoo_month, "at proj": proj_name, "at task": task_name, "odoo": 0, "zeit": 0}
        sumdata[odoo_key]["odoo"] += odoo_size  # type: ignore
    return list(sumdata.values())

def fnmatches(text: str, pattern: str) -> bool:
    for pat in pattern.split("|"):
        if pat.isalnum() and pat.islower():
            if fnmatch(text.lower(), f"*{pat}*"):
                return True
        else:
            if fnmatch(text, pat + "*"):
                return True
    return False

def pref_desc(desc: str) -> str:
    if " " not in desc:
        return desc.strip()
    else:
        return desc.split(" ", 1)[0]

def summary_per_topic(odoodata: Optional[JSONList] = None) -> JSONList:
    if not odoodata:
        odoo = odoo_api.Odoo().for_user(FOR_USER[0] if FOR_USER else "")
        odoodata = odoo.timesheet(DAYS.after, DAYS.before)
    return _summary_per_topic(odoodata)
def _summary_per_topic(odoodata: JSONList) -> JSONList:
    sumdata: Dict[str, JSONDict] = {}
    for item in odoodata:
        odoo_desc: str = cast(str, item["entry_desc"])
        odoo_date: Day = get_date(cast(str, item["entry_date"]))
        odoo_size: Num = cast(Num, item["entry_size"])
        odoo_pref = pref_desc(odoo_desc)
        if odoo_pref not in sumdata:
            sumdata[odoo_pref] = {"at topic": odoo_pref, "odoo": 0}
        sumdata[odoo_pref]["odoo"] += odoo_size  # type: ignore
    return list(sumdata.values())

def json2odoo(data: JSONList) -> JSONList:
    return list(_json2odoo(data))
def _json2odoo(data: JSONList) -> Iterable[JSONDict]:
    for item in data:
        info: JSONDict = {}
        info["proj_name"] = item["Project"]
        info["task_name"] = item["Task"]
        info["task_topic"] = item["Topic"]  # does not exist in odoo
        info["entry_desc"] = item["Description"]
        info["entry_date"] = item["Date"]
        info["entry_size"] = item["Quantity"]
        yield info

def run(arg: str) -> None:
    global DAYS
    if is_dayrange(arg):  # "week", "month", "last", "latest"
        DAYS = dayrange(arg)
        logg.log(DONE, "%s -> %s", arg, DAYS)
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
    data: Optional[JSONList] = None
    summary = []
    results: JSONList = []
    formats = {"odoo": " %4.2f", "summe": " %4.2f"}
    FMT = FORMAT
    if ONLYZEIT:
        import zeit2json
        data = json2odoo(zeit2json.read_zeit(DAYS.after, DAYS.before))
    if arg in ["ou", "odoo-users", "users"]:
        results = odoo_users()  # list all Odoo users
    elif arg in ["op", "odoo-projects", "projects"]:
        results = odoo_projects()  # list all Odoo projects (including unused)
        summary += ["# use 'oo' or 'odoo-projects-tasks' to see task details"]
    elif arg in ["oo", "opt", "odoo-projects-tasks", "projects-tasks"]:
        results = odoo_projects_tasks()  # list all Odoo projects-and-tasks (including unused)
        formats["task_name"] = '"{:}"'
    elif arg in ["ww", "data", "worked"]:
        results = work_data(data)  # list all Odoo entries
        if results and not SHORTNAME:
            summary += [" ### use -q or -qq to shorten the names for proj and task !!"]
    elif arg in ["z", "text", "zeit"]:
        results = work_zeit(data)  # list all Odoo entries in Zeit sheet format
        if not FMT:
            FMT = "wide"
    elif arg in ["dd", "dsummary", "days"]:
        results = summary_per_day(data)
    elif arg in ["xx", "report"]:
        results = report_per_project(data)  # group by Odoo project, per month and add price column
        sum_euro = sum([float(cast(JSONBase, item["summe"])) for item in results if item["summe"]])
        sum_odoo = sum([float(cast(JSONBase, item["odoo"])) for item in results if item["odoo"]])
        summary = [f"{sum_euro:11.2f} {EURO} summe", f"{sum_odoo:11.2f} hours odoo"]
        if results and not ADDFOOTER:
            summary += [" ### use -Z to add a VAT footer !!"]
        formats["summe"] = " {:$}"
    elif arg in ["xxx", "reports"]:
        results = reports_per_project(data)  # group by Odoo project, per month, add price and m column
        sum_euro = sum([float(cast(JSONBase, item["summe"])) for item in results if item["summe"]])
        sum_odoo = sum([float(cast(JSONBase, item["odoo"])) for item in results if item["odoo"]])
        summary = [f"{sum_euro:11.2f} {EURO} summe", f"{sum_odoo:11.2f} hours odoo"]
        if results and not ADDFOOTER:
            summary += [" ### use -Z to add a VAT footer !!"]
        formats["summe"] = " {:$}"
    elif arg in ["mm", "msummarize", "mtasks", "monthlys"]:
        results = monthly_per_project_task(data)  # group by Odoo project-and-task, seperate per month
    elif arg in ["sx", "msummary", "monthly"]:
        results = monthly_per_project(data)  # group by Odoo project but keep sums seperate per month
        sum_odoo = sum([float(cast(JSONBase, item["odoo"])) for item in results if item["odoo"]])
        summary = [f"{sum_odoo:11.2f} hours odoo"]
    elif arg in ["ee", "summarize", "tasks"]:
        results = summary_per_project_task(data)  # group by Odoo project-and-task, across the full given dayrange
    elif arg in ["ss", "summary"]:
        results = summary_per_project(data)  # group by Odoo project, across the full given dayrange
        sum_odoo = sum([float(cast(JSONBase, item["odoo"])) for item in results if item["odoo"]])
        summary = [f"{sum_odoo:11.2f} hours odoo"]
    elif arg in ["tt", "topics"]:
        results = summary_per_topic(data)  # group by topic prefix in description, across the full given dayrange
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
                if "worked on" in item and SHORTNAME > 1:
                    item["worked on"] = strName(item["worked on"])
        if ADDFOOTER:
            odoo: Optional[float] = None
            summe: Optional[float] = None
            for item in results:
                if "odoo" in item:
                    odoo = (odoo or 0.0) + cast(float, item["odoo"])
                if "summe" in item:
                    summe = (summe or 0.0) + cast(float, item["summe"])
            if odoo or summe:
                results.append({})
                results.append({"odoo": odoo, "summe": summe})
            if summe:
                price_vat = get_price_vat()
                results.append({"satz": price_vat, "summe": round(summe * price_vat, 2)})
                results.append({"summe": summe + round(summe * price_vat, 2)})
        if OUTPUT in ["", "-", "CON"]:
            print(tabtotext.tabToFMT(FMT, results, formats=formats, legend=summary))
        elif OUTPUT:
            with open(OUTPUT, "w") as f:
                f.write(tabtotext.tabToFMT(FMT, results, formats=formats, legend=summary))
            logg.log(DONE, " %s written   %s '%s'", FMT, viewFMT(FMT), OUTPUT)
        if JSONFILE:
            FMT = "json"
            with open(JSONFILE, "w") as f:
                f.write(tabtotext.tabToJSON(results))
            logg.log(DONE, " %s written   %s '%s'", FMT, viewFMT(FMT), JSONFILE)
        if XLSXFILE:
            FMT = "xlsx"
            import tabtoxlsx
            tabtoxlsx.saveToXLSX(XLSXFILE, results, formats=formats)
            logg.log(DONE, " %s written   %s '%s'", FMT, viewFMT(FMT), XLSXFILE)

if __name__ == "__main__":
    from optparse import OptionParser
    cmdline = OptionParser("%prog [help|work|days|summarize|summary|topics] files...")
    cmdline.add_option("-v", "--verbose", action="count", default=0,
                       help="more verbose logging")
    cmdline.add_option("-a", "--after", metavar="DATE", default=None,
                       help="only evaluate entrys on and after [first of month]")
    cmdline.add_option("-b", "--before", metavar="DATE", default=None,
                       help="only evaluate entrys on and before [last of month]")
    cmdline.add_option("-p", "--price", metavar="TEXT", action="append", default=PRICES,
                       help="pattern:price per hour [%default]")
    cmdline.add_option("--projskip", metavar="TEXT", default=ODOO_PROJSKIP,
                       help="filter for odoo project [%default]")
    cmdline.add_option("-P", "--projonly", metavar="TEXT", default=ODOO_PROJONLY,
                       help="filter for odoo project [%default]")
    # ..............
    cmdline.add_option("-q", "--shortname", action="count", default=SHORTNAME,
                       help="present short names for proj+task [%default]")
    cmdline.add_option("-z", "--onlyzeit", action="count", default=ONLYZEIT,
                       help="present only local zeit data [%default]")
    cmdline.add_option("-Z", "--addfooter", action="count", default=ADDFOOTER,
                       help="present sum as lines in data [%default]")
    cmdline.add_option("-o", "--format", metavar="FMT", help="json|yaml|html|wide|md|htm|tab|csv", default=FORMAT)
    cmdline.add_option("-O", "--output", metavar="CON", default=OUTPUT, help="redirect to filename")
    cmdline.add_option("-J", "--jsonfile", metavar="FILE", default=JSONFILE)
    cmdline.add_option("-X", "--xlsxfile", metavar="FILE", default=XLSXFILE)
    cmdline.add_option("-g", "--gitcredentials", metavar="FILE", default=netrc.GIT_CREDENTIALS)
    cmdline.add_option("-G", "--netcredentials", metavar="FILE", default=netrc.NET_CREDENTIALS)
    cmdline.add_option("-E", "--extracredentials", metavar="FILE", default=netrc.NETRC_FILENAME)
    cmdline.add_option("-c", "--config", metavar="NAME=VALUE", action="append", default=[])
    cmdline.add_option("-u", "--user", metavar="NAME", action="append", default=[],
                       help="show data for other users than the login user (use full name or email)")
    opt, args = cmdline.parse_args()
    logging.basicConfig(level=max(0, logging.WARNING - 10 * opt.verbose))
    logg.setLevel(level=max(0, logging.WARNING - 10 * opt.verbose))
    # logg.addHandler(logging.StreamHandler())
    for value in opt.config:
        gitrc.git_config_override(value)
    netrc.set_password_filename(opt.gitcredentials)
    netrc.add_password_filename(opt.netcredentials, opt.extracredentials)
    FOR_USER = opt.user
    FORMAT = opt.format
    OUTPUT = opt.output
    JSONFILE = opt.jsonfile
    XLSXFILE = opt.xlsxfile
    ONLYZEIT = opt.onlyzeit
    ADDFOOTER = opt.addfooter
    SHORTNAME = opt.shortname
    if opt.shortname > 1:
        ONLYZEIT = opt.shortname
    if opt.shortname > 2:
        ADDFOOTER = opt.shortname
    if opt.onlyzeit > 1:
        SHORTNAME = opt.onlyzeit
    if opt.onlyzeit > 2:
        ADDFOOTER = opt.onlyzeit
    # zeit2json
    ODOO_PROJONLY = opt.projonly
    ODOO_PROJSKIP = opt.projskip
    PRICES = opt.price
    DAYS = dayrange(opt.after, opt.before)
    if not args:
        args = ["projects"]
    elif len(args) == 1 and is_dayrange(args[0]):
        args += ["projects"]
    elif len(args) >= 2 and is_dayrange(args[1]):
        logg.error("a dayrange should come first: %s", args[1])
    for arg in args:
        run(arg)
