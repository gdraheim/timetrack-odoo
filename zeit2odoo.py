#! /usr/bin/python3

from typing import Optional, Union, Dict, List, Tuple, cast

import logging
import re
import csv
import datetime

import tabtotext
import zeit2json
from zeit2json import get_date, first_of_month, last_of_month, last_sunday, next_sunday, get_zeit_after, get_zeit_before, get_zeit_filename
import odoo_rest as odoo_api
import netrc
import gitrc

from tabtotext import JSONList, JSONDict, JSONBase
from odoo_rest import EntryID, ProjID, TaskID

Day = datetime.date
Num = float

logg = logging.getLogger("zeit2odoo")
DONE = (logging.WARNING + logging.ERROR) // 2
logging.addLevelName(DONE, "DONE")

# [for zeit2json]
AFTER = ""  # get_zeit_after()
BEFORE = ""  # get_zeit_before()
ZEIT_FILENAME = ""  # get_zeit_filename()
ZEIT_USER_NAME = ""  # get_user_name() in zeit
ZEIT_SUMMARY = "stundenzettel"
ZEIT_PROJFILTER = ""
ZEIT_TASKFILTER = ""
ZEIT_TEXTFILTER = ""
ZEIT_DESCFILTER = ""
ZEIT_EXTRATIME = False
ZEIT_SHORT = False
# [end zeit2json]

UPDATE = False
SHORTDESC = False

SCSVFILE = ""
TEXTFILE = ""
JSONFILE = ""
HTMLFILE = ""
XLSXFILE = ""

norm_frac_1_4 = 0x00BC
norm_frac_1_2 = 0x00BD
norm_frac_3_4 = 0x00BE

def strDesc(val: str) -> str:
    if SHORTDESC:
        if len(val) > 40:
            return val[:37] + "..."
    return val

def strHours(val: Union[int, float, str]) -> str:
    numm = float(val)
    base = int(numm)
    frac = numm - base
    indent = ""
    if base <= 9:
        indent = " "
    if -0.02 < frac and frac < 0.02:
        if not base:
            return " 0"
        return "%s%i%c" % (indent, base, "h")
    if 0.22 < frac and frac < 0.27:
        if not base:
            return "%s%s%c" % (indent, " ", norm_frac_1_4)
        return "%s%i%c" % (indent, base, norm_frac_1_4)
    if 0.48 < frac and frac < 0.52:
        if not base:
            return "%s%s%c" % (indent, " ", norm_frac_1_2)
        return "%s%i%c" % (indent, base, norm_frac_1_2)
    if 0.72 < frac and frac < 0.77:
        if not base:
            return "%s%s%c" % (indent, " ", norm_frac_3_4)
        return "%s%i%c" % (indent, base, norm_frac_3_4)
    return "%s%f" % (indent, numm)

def check_in_sync(data: JSONList) -> JSONList:
    changes: JSONList = []
    odoo = odoo_api.Odoo()
    for item in data:
        orig_id = cast(str, item["ID"])
        proj_id = cast(str, item["Project"])
        task_id = cast(str, item["Task"])
        pref_id = cast(str, item["Topic"])
        new_desc = cast(str, item["Description"])
        new_date = cast(Day, item["Date"])
        new_size = cast(Num, item["Quantity"])
        # records = odoo.timesheet_records(date)
        # logg.info("found %sx records for %s", len(records), date)
        found = odoo.timesheet_record(proj_id, task_id, new_date)
        if not found:
            logg.info("NEW: [%s] %s", strHours(new_size), new_desc)
            if UPDATE:
                done = odoo.timesheet_create(proj_id, task_id, new_date, new_size, new_desc)
                logg.info("-->: %s", done)
            changes.append({"act": "NEW", "at proj": proj_id, "at task": task_id,
                            "date": new_date, "desc": new_desc, "zeit": new_size})
        elif len(found) == 1:
            old_desc = cast(str, found[0]["entry_desc"])
            old_size = cast(Num, found[0]["entry_size"])
            old_date = cast(Day, found[0]["entry_date"])
            if old_desc != new_desc or old_size != new_size:
                pre_desc = pref_id + " " + old_desc
                if pre_desc == new_desc and old_size == new_size:
                    logg.info(" TO: [%s] %s", strHours(new_size), new_desc)
                else:
                    logg.info("old: [%s] %s", strHours(old_size), old_desc)
                    logg.info("new: [%s] %s", strHours(new_size), new_desc)
                if UPDATE:
                    done = odoo.timesheet_update(proj_id, task_id, old_date, new_size, new_desc)
                    logg.info("-->: %s", done)
                changes.append({"act": "UPD", "at proj": proj_id, "at task": task_id,
                                "date": new_date, "desc": new_desc, "zeit": new_size})
            else:
                logg.info(" ok: [%s] %s", strHours(new_size), new_desc)
        else:
            ok = False
            for item in found:
                old_desc = cast(str, item["entry_desc"])
                if old_desc == new_desc:
                    ok = True
            if ok:
                for item in found:
                    ref_size = cast(Num, item["entry_size"])
                    ref_desc = cast(str, item["entry_desc"])
                    logg.info("*ok: [%s] %s", strHours(ref_size), strDesc(ref_desc))
            else:
                logg.warning("*multiple: %s", new_desc)
                for item in found:
                    ref_size = cast(Num, item["entry_size"])
                    ref_desc = cast(str, item["entry_desc"])
                    logg.warning("******: [%s] %s", strHours(ref_size), strDesc(ref_desc))
    return changes

def valid_per_days(data: JSONList) -> JSONList:
    daysum: Dict[Day, Num] = {}
    for item in data:
        orig_id = cast(str, item["ID"])
        proj_id = cast(str, item["Project"])
        task_id = cast(str, item["Task"])
        pref_id = cast(str, item["Topic"])
        new_desc = cast(str, item["Description"])
        new_date = cast(Day, item["Date"])
        new_size = cast(Num, item["Quantity"])
        if new_date not in daysum:
            daysum[new_date] = 0
        daysum[new_date] = daysum[new_date] + new_size
    return __valid_per_days(data, daysum)
def __valid_per_days(data: JSONList, daysum: Dict[Day, Num]) -> JSONList:
    results: JSONList = []
    odoo = odoo_api.Odoo()
    for sum_date in sorted(daysum.keys()):
        new_sum = daysum[sum_date]
        found = odoo.timesheet_records(sum_date)
        if not found:
            logg.info(" NO: (%s)", sum_date)
        old_sum: Num = 0
        for item in found:
            old_size = cast(Num, item["entry_size"])
            old_sum += old_size
        if old_sum != new_sum:
            logg.info("old: (%s) [%s]", sum_date, strHours(old_sum))
            logg.info("new: (%s) [%s]", sum_date, strHours(new_sum))
        else:
            logg.info(" ok: (%s) [%s]", sum_date, strHours(new_sum))
        results.append({"date": sum_date, "zeit": new_sum, "odoo": old_sum})
    return results

def update_per_days(data: JSONList) -> JSONList:
    daydata: Dict[Day, JSONList] = {}
    for item in data:
        orig_id: str = cast(str, item["ID"])
        proj_id: str = cast(str, item["Project"])
        task_id: str = cast(str, item["Task"])
        pref_id: str = cast(str, item["Topic"])
        new_desc: str = cast(str, item["Description"])
        new_date: Day = cast(Day, item["Date"])
        new_size: Num = cast(Num, item["Quantity"])
        if new_date not in daydata:
            daydata[new_date] = []
        daydata[new_date].append(item)
    return __update_per_days(data, daydata)
def __update_per_days(data: JSONList, daydata: Dict[Day, JSONList]) -> JSONList:
    changes: JSONList = []
    odoo = odoo_api.Odoo()
    for day in sorted(daydata.keys()):
        items = daydata[day]
        found = odoo.timesheet_records(day)
        if not found:
            logg.info("---: (%s) ----- no data from odoo", day)
        for item in items:
            orig_id: str = cast(str, item["ID"])
            proj_id: str = cast(str, item["Project"])
            task_id: str = cast(str, item["Task"])
            pref_id: str = cast(str, item["Topic"])
            new_desc: str = cast(str, item["Description"])
            new_date: Day = cast(Day, item["Date"])
            new_size: Num = cast(Num, item["Quantity"])
            matching = []
            for old in found:
                old_entry_desc = cast(str, old["entry_desc"])
                if old_entry_desc.startswith(f"{pref_id} "):
                    matching.append(old)
            if not matching:
                logg.info("NEW: (%s) [%s] %s", new_date, strHours(new_size), strDesc(new_desc))
                if UPDATE:
                    done = odoo.timesheet_create(proj_id, task_id, new_date, new_size, new_desc)
                    logg.info("-->: %s", done)
                changes.append({"act": "NEW", "at proj": proj_id, "at task": task_id,
                                "date": new_date, "desc": new_desc, "zeit": new_size})
            elif len(matching) > 1:
                logg.info(" *multiple: (%s) [%s] %s", new_date, strHours(new_size), strDesc(new_desc))
                for matched in matching:
                    _old_date: str = cast(str, matched["entry_date"])
                    _old_size: Num = cast(Num, matched["entry_size"])
                    _old_desc: str = cast(str, matched["entry_desc"])
            else:  # len(matching) == 1
                matched = matching[0]
                old_date: str = cast(str, matched["entry_date"])
                old_size: Num = cast(Num, matched["entry_size"])
                old_desc: str = cast(str, matched["entry_desc"])
                old_proj: str = cast(str, matched["proj_name"])
                old_task: str = cast(str, matched["task_name"])
                if old_size != new_size or old_desc != new_desc or old_proj != proj_id or old_task != task_id:
                    logg.info("old: (%s) [%s] %s", old_date, strHours(old_size), strDesc(old_desc))
                    logg.info("new: (%s) [%s] %s", new_date, strHours(new_size), strDesc(new_desc))
                    if proj_id != proj_id or old_task != task_id:
                        logg.info("REF: (%s)       [%s] \"%s\"", new_date, old_proj, old_task)
                        logg.info("UPD: (%s)       [%s] \"%s\"", new_date, proj_id, task_id)
                    if UPDATE:
                        old_id = cast(EntryID, matched["entry_id"])
                        done = odoo.timesheet_write(old_id, proj_id, task_id, new_date, new_size, new_desc)
                        logg.info("-->: %s", done)
                    changes.append({"act": "UPD", "at proj": proj_id, "at task": task_id,
                                    "date": new_date, "desc": new_desc, "zeit": new_size})
                else:
                    logg.info(" ok: (%s) [%s] %s", new_date, strHours(new_size), strDesc(new_desc))
    return changes

def summary_per_day(data: JSONList, odoodata: Optional[JSONList] = None) -> JSONList:
    if not odoodata:
        odoo = odoo_api.Odoo()
        return _summary_per_day(data, odoo.timesheet(get_zeit_after(), get_zeit_before()))
    return _summary_per_day(data, odoodata)
def _summary_per_day(data: JSONList, odoodata: JSONList) -> JSONList:
    daydata: Dict[Day, JSONDict] = {}
    for item in data:
        new_date: Day = cast(Day, item["Date"])
        new_size: Num = cast(Num, item["Quantity"])
        if new_date not in daydata:
            daydata[new_date] = {"date": new_date, "odoo": 0, "zeit": 0}
        daydata[new_date]["zeit"] += new_size  # type: ignore
    dayodoo: Dict[Day, JSONList] = {}
    for item in odoodata:
        old_date: Day = get_date(cast(str, item["entry_date"]))
        old_size: Num = cast(Num, item["entry_size"])
        if old_date not in daydata:
            daydata[old_date] = {"date": old_date, "odoo": 0, "zeit": 0}
        daydata[old_date]["odoo"] += old_size  # type: ignore
    return list(daydata.values())

def summary_per_project_task(data: JSONList, odoodata: Optional[JSONList] = None) -> JSONList:
    if not odoodata:
        odoo = odoo_api.Odoo()
        return _summary_per_project_task(data, odoo.timesheet(get_zeit_after(), get_zeit_before()))
    return _summary_per_project_task(data, odoodata)
def _summary_per_project_task(data: JSONList, odoodata: JSONList) -> JSONList:
    sumdata: Dict[Tuple[str, str], JSONDict] = {}
    for item in data:
        proj_id: str = cast(str, item["Project"])
        task_id: str = cast(str, item["Task"])
        new_date: Day = cast(Day, item["Date"])
        new_size: Num = cast(Num, item["Quantity"])
        new_key = (proj_id, task_id)
        if new_key not in sumdata:
            sumdata[new_key] = {"at proj": proj_id, "at task": task_id, "odoo": 0, "zeit": 0}
        sumdata[new_key]["zeit"] += new_size  # type: ignore
    dayodoo: Dict[Day, JSONList] = {}
    for item in odoodata:
        proj_name: str = cast(str, item["proj_name"])
        task_name: str = cast(str, item["task_name"])
        old_date: Day = get_date(cast(str, item["entry_date"]))
        old_size: Num = cast(Num, item["entry_size"])
        old_key = (proj_name, task_name)
        if old_key not in sumdata:
            sumdata[old_key] = {"at proj": proj_name, "at task": task_name, "odoo": 0, "zeit": 0}
        sumdata[old_key]["odoo"] += old_size  # type: ignore
    return list(sumdata.values())

def summary_per_project(data: JSONList, odoodata: Optional[JSONList] = None) -> JSONList:
    if not odoodata:
        odoo = odoo_api.Odoo()
        return _summary_per_project(data, odoo.timesheet(get_zeit_after(), get_zeit_before()))
    return _summary_per_project(data, odoodata)
def _summary_per_project(data: JSONList, odoodata: JSONList) -> JSONList:
    sumdata = _summary_per_project_task(data, odoodata)
    sumproj: Dict[str, JSONDict] = {}
    for item in sumdata:
        proj_name = cast(str, item["at proj"])
        task_name = cast(str, item["at task"])
        if proj_name not in sumproj:
            sumproj[proj_name] = {"at proj": proj_name, "odoo": 0, "zeit": 0}
        sumproj[proj_name]["odoo"] += item["odoo"]  # type: ignore
        sumproj[proj_name]["zeit"] += item["zeit"]  # type: ignore
    return list(sumproj.values())

def pref_desc(desc: str) -> str:
    if " " not in desc:
        return desc.strip()
    else:
        return desc.split(" ", 1)[0]

def summary_per_topic(data: JSONList, odoodata: Optional[JSONList] = None) -> JSONList:
    if not odoodata:
        odoo = odoo_api.Odoo()
        return _summary_per_topic(data, odoo.timesheet(get_zeit_after(), get_zeit_before()))
    return _summary_per_topic(data, odoodata)
def _summary_per_topic(data: JSONList, odoodata: JSONList) -> JSONList:
    sumdata: Dict[str, JSONDict] = {}
    for item in data:
        new_desc: str = cast(str, item["Description"])
        new_date: Day = cast(Day, item["Date"])
        new_size: Num = cast(Num, item["Quantity"])
        new_pref = pref_desc(new_desc)
        if new_pref not in sumdata:
            sumdata[new_pref] = {"at topic": new_pref, "odoo": 0, "zeit": 0}
        sumdata[new_pref]["zeit"] += new_size  # type: ignore
    dayodoo: Dict[Day, JSONList] = {}
    for item in odoodata:
        old_desc: str = cast(str, item["entry_desc"])
        old_date: Day = get_date(cast(str, item["entry_date"]))
        old_size: Num = cast(Num, item["entry_size"])
        old_pref = pref_desc(old_desc)
        if old_pref not in sumdata:
            sumdata[old_pref] = {"at topic": old_pref, "odoo": 0, "zeit": 0}
        sumdata[old_pref]["odoo"] += old_size  # type: ignore
    return list(sumdata.values())

def run(arg: str) -> None:
    global AFTER, BEFORE
    if arg in ["latest", "week"]:
        AFTER = last_sunday(-1).isoformat()
        BEFORE = next_sunday(-1).isoformat()
        logg.log(DONE, "%s -> %s %s", arg, AFTER, BEFORE)
        return
    if arg in ["late", "lastweek"]:
        AFTER = last_sunday(-6).isoformat()
        BEFORE = next_sunday(-6).isoformat()
        logg.log(DONE, "%s -> %s %s", arg, AFTER, BEFORE)
        return
    if arg in ["next", "nextmonth", "next-month"]:
        AFTER = first_of_month(-1)
        BEFORE = last_of_month(-1)
        logg.log(DONE, "%s -> %s %s", arg, AFTER, BEFORE)
        return
    if arg in ["this", "thismonth", "this-month"]:
        AFTER = first_of_month(+0)
        BEFORE = last_of_month(+0)
        logg.log(DONE, "%s -> %s %s", arg, AFTER, BEFORE)
        return
    if arg in ["last", "lastmonth", "last-month"]:
        AFTER = first_of_month(-1)
        BEFORE = last_of_month(-1)
        logg.log(DONE, "%s -> %s %s", arg, AFTER, BEFORE)
        return
    if arg in ["beforelast", "beforelastmonth", "before-last-month", "blast", "b4last"]:
        AFTER = first_of_month(-2)
        BEFORE = last_of_month(-2)
        logg.log(DONE, "%s -> %s %s", arg, AFTER, BEFORE)
        return
    zeit2json.ZEIT_AFTER = AFTER
    zeit2json.ZEIT_BEFORE = BEFORE
    zeit2json.ZEIT_USER_NAME = ZEIT_USER_NAME
    zeit2json.ZEIT_SUMMARY = ZEIT_SUMMARY
    zeit2json.ZEIT_PROJFILTER = ZEIT_PROJFILTER
    zeit2json.ZEIT_TASKFILTER = ZEIT_TASKFILTER
    zeit2json.ZEIT_TEXTFILTER = ZEIT_TEXTFILTER
    zeit2json.ZEIT_DESCFILTER = ZEIT_DESCFILTER
    zeit2json.ZEIT_EXTRATIME = ZEIT_EXTRATIME
    zeit2json.ZEIT_SHORT = ZEIT_SHORT
    filename = get_zeit_filename()
    data = zeit2json.read_data(filename)
    if arg in ["json", "make"]:
        json_text = tabtotext.tabToJSON(data)
        json_file = filename + ".json"
        with open(json_file, "w") as f:
            f.write(json_text)
        logg.log(DONE, "written %s (%s entries)", json_file, len(data))
    if arg in ["csv", "make"]:
        csv_text = tabtotext.tabToJSON(data)
        csv_file = filename + ".csv"
        with open(csv_file, "w") as f:
            f.write(csv_text)
        logg.log(DONE, "written %s (%s entries)", csv_file, len(data))
    summary = []
    results: JSONList = []
    if arg in ["cc", "check"]:
        results = check_in_sync(data)
    if arg in ["vv", "valid"]:
        results = valid_per_days(data)
    if arg in ["uu", "update"]:
        results = update_per_days(data)
    if arg in ["cc", "compare"]:
        results = summary_per_day(data)
    if arg in ["sss", "summarize", "tasks"]:
        results = summary_per_project_task(data)
    if arg in ["ss", "summary"]:
        results = summary_per_project(data)
        sum_zeit = sum([float(cast(JSONBase, item["zeit"])) for item in results if item["zeit"]])
        sum_odoo = sum([float(cast(JSONBase, item["odoo"])) for item in results if item["odoo"]])
        summary = [f"{sum_zeit} hours zeit", f"{sum_odoo} hours odoo"]
    if arg in ["ss", "topics"]:
        results = summary_per_topic(data)
    if results:
        print(tabtotext.tabToGFM(results, formats={"zeit": " %4.2f", "odoo": " %4.2f"}))
        for line in summary:
            print(f"# {line}")
        if SCSVFILE:
            with open(SCSVFILE, "w") as f:
                f.write(tabtotext.tabToCSV(results))
            logg.log(DONE, " scsv written '%s'", SCSVFILE)
        if JSONFILE:
            with open(JSONFILE, "w") as f:
                f.write(tabtotext.tabToJSON(results))
            logg.log(DONE, " json written '%s'", JSONFILE)
        if HTMLFILE:
            with open(HTMLFILE, "w") as f:
                f.write(tabtotext.tabToHTML(results))
            logg.log(DONE, " html written '%s'", HTMLFILE)
        if TEXTFILE:
            with open(TEXTFILE, "w") as f:
                f.write(tabtotext.tabToGFM(results))
            logg.log(DONE, " text written '%s'", TEXTFILE)
        if XLSXFILE:
            import tabtoxlsx
            tabtoxlsx.saveToXLSX(XLSXFILE, results)
            logg.log(DONE, " xlsx written '%s'", XLSXFILE)

if __name__ == "__main__":
    from optparse import OptionParser
    cmdline = OptionParser("%prog [check|valid|update|compare|summarize|summary|topics] files...")
    cmdline.add_option("-v", "--verbose", action="count", default=0,
                       help="more verbose logging")
    cmdline.add_option("-a", "--after", metavar="DATE", default=AFTER,
                       help="only evaluate entrys on and after [first of year]")
    cmdline.add_option("-b", "--before", metavar="DATE", default=BEFORE,
                       help="only evaluate entrys on and before [last of year]")
    cmdline.add_option("-f", "--filename", metavar="TEXT", default=ZEIT_FILENAME,
                       help="choose input filename [%default]")
    cmdline.add_option("-s", "--summary", metavar="TEXT", default=ZEIT_SUMMARY,
                       help="suffix for summary report [%default]")
    cmdline.add_option("-P", "--projfilter", metavar="TEXT", default=ZEIT_PROJFILTER,
                       help="filter for odoo project [%default]")
    cmdline.add_option("-T", "--taskfilter", metavar="TEXT", default=ZEIT_TASKFILTER,
                       help="filter for odoo task [%default]")
    cmdline.add_option("-D", "--descfilter", metavar="TEXT", default=ZEIT_DESCFILTER,
                       help="filter for some description [%default]")
    cmdline.add_option("-F", "--textfilter", metavar="TEXT", default=ZEIT_TEXTFILTER,
                       help="filter for text project [%default]")
    cmdline.add_option("-x", "--extra", action="store_true", default=ZEIT_EXTRATIME,
                       help="allow for the extra times [%default]")
    cmdline.add_option("-z", "--short", action="store_true", default=ZEIT_SHORT,
                       help="present the shorthand names for projects and tasks [%default]")
    cmdline.add_option("-U", "--user-name", metavar="TEXT", default=ZEIT_USER_NAME,
                       help="user name for the output report (not for login)")
    # ..............
    cmdline.add_option("-Z", "--shortdesc", action="store_true", default=SHORTDESC,
                       help="present the shorthand names for description [%default]")
    cmdline.add_option("--SCSVfile", metavar="FILE", default=SCSVFILE)
    cmdline.add_option("--textfile", metavar="FILE", default=TEXTFILE)
    cmdline.add_option("--jsonfile", metavar="FILE", default=JSONFILE)
    cmdline.add_option("--htmlfile", metavar="FILE", default=HTMLFILE)
    cmdline.add_option("--xlsxfile", metavar="FILE", default=XLSXFILE)
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
    SCSVFILE = opt.SCSVfile
    TEXTFILE = opt.textfile
    JSONFILE = opt.jsonfile
    HTMLFILE = opt.htmlfile
    XLSXFILE = opt.xlsxfile
    # zeit2json
    ZEIT_USER_NAME = opt.user_name
    ZEIT_SHORT = opt.short
    ZEIT_EXTRATIME = opt.extra
    ZEIT_PROJFILTER = opt.projfilter
    ZEIT_TASKFILTER = opt.taskfilter
    ZEIT_TEXTFILTER = opt.textfilter
    ZEIT_DESCFILTER = opt.descfilter
    ZEIT_FILENAME = opt.filename
    ZEIT_SUMMARY = opt.summary
    AFTER = opt.after
    BEFORE = opt.before
    if not args:
        args = ["make"]
    for arg in args:
        run(arg)
