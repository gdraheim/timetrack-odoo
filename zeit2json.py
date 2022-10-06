#! /usr/bin/python3

from typing import List, Dict, Union, Optional, Sequence, TextIO

import logging
import re
import csv
import datetime
import os.path as path

import tabtotext
from tabtotext import JSONList, JSONDict, JSONItem

Day = datetime.date

logg = logging.getLogger("zeit2json")
DONE = (logging.WARNING + logging.ERROR) // 2
logging.addLevelName(DONE, "DONE")


ZEIT_AFTER = ""
ZEIT_BEFORE = ""
ZEIT_SUMMARY = "stundenzettel"
ZEIT_PROJFILTER = ""
ZEIT_TASKFILTER = ""
ZEIT_TEXTFILTER = ""
ZEIT_DESCFILTER = ""
ZEIT_EXTRATIME = False
ZEIT_SHORT = False
ZEIT_FILENAME = ""
ZEIT_USER_NAME = ""

WRITEJSON = True
WRITECSV = True

TitleID = "ID"
TitleDate = "Date"  # "Datum"
TitleUser = "User"
TitleDesc = "Description"  # "Beschreibung"
TitlePref = "Topic"  # Prefix used in Desc
TitleProj = "Project"  # "Projekt"
TitleTask = "Task"  # "Aufgabe"
TitleTime = "Quantity"  # "Anzahl"


# format to map a topic to the proj/task
mapping = """
>> odoo [GUIDO (Private Investigations)]
>> odoo "Odoo Automation",
"""

def get_user_name() -> Optional[str]:
    if ZEIT_USER_NAME:
        return ZEIT_USER_NAME
    import gitrc
    return gitrc.git_config_value("user.name")
def get_zeit_filename() -> str:
    if ZEIT_FILENAME:
        return expand_zeit_filename(ZEIT_FILENAME)
    import gitrc
    found = gitrc.git_config_value("zeit.filename")
    if found:
        return expand_zeit_filename(found)
    return expand_zeit_filename("~/zeit{YEAR}.txt")
def expand_zeit_filename(filename: str) -> str:
    YEAR = get_zeit_after().year
    return path.expanduser(filename.format(**locals()))

def get_zeit_after() -> Day:
    global ZEIT_AFTER
    if ZEIT_AFTER:
        return get_date(ZEIT_AFTER)
    today = datetime.date.today()
    return Day(today.year, 1, 1)
def get_zeit_before() -> Day:
    global ZEIT_BEFORE, ZEIT_AFTER
    if ZEIT_BEFORE:
        return get_date(ZEIT_BEFORE)
    if ZEIT_AFTER:
        after = get_date(ZEIT_AFTER)
        return Day(after.year, 12, 31)
    today = datetime.date.today()
    return Day(today.year, 12, 31)

def time2float(time: str) -> float:
    time = time.replace(",", ".")
    time = time.replace(":00", ".00")
    time = time.replace(":15", ".25")
    time = time.replace(":30", ".50")
    time = time.replace(":45", ".75")
    return float(time)

def cleandesc(desc: str) -> str:
    d = desc.replace("*", "").replace(" , ", ", ")
    m = re.match("(.*)\\S*\\d:\\d+\\S*$", d)
    if m:
        return m.group(1)
    return d

def date_isoformat(text: str) -> Day:
    if "-99" in text:
        for end in ["-31", "-30", "-29", "-28"]:
            try:
                text31 = text.replace("-99", end, 1)
                return datetime.datetime.strptime(text31, "%Y-%m-%d").date()
            except ValueError as e:
                logg.debug("[%s] %s", text31, e)
    return datetime.datetime.strptime(text, "%Y-%m-%d").date()

def date_dotformat(text: str) -> Day:
    if "99." in text:
        for end in ["31.", "30.", "29.", "28."]:
            try:
                text31 = text.replace("99.", end, 1)
                return datetime.datetime.strptime(text31, "%d.%m.%Y").date()
            except ValueError as e:
                logg.debug("[%s] %s", text31, e)
    return datetime.datetime.strptime(text, "%d.%m.%Y").date()

def firstday_of_month(diff: int) -> Day:
    return date_dotformat(first_of_month(diff))
def first_of_month(diff: int) -> str:
    assert -11 <= diff and diff <= +11
    today = datetime.date.today()
    year = today.year
    month = today.month + diff
    if month <= 0:
        month += 12
        year -= 1
    if month > 12:
        month -= 12
        year += 1
    return f"01.{month}.{year}"


def lastday_of_month(diff: int) -> Day:
    return date_dotformat(last_of_month(diff))
def last_of_month(diff: int) -> str:
    assert -11 <= diff and diff <= +11
    today = datetime.date.today()
    year = today.year
    month = today.month + diff
    if month <= 0:
        month += 12
        year -= 1
    if month > 12:
        month -= 12
        year += 1
    return f"99.{month}.{year}"

def last_sunday(diff: int) -> Day:
    today = datetime.date.today()
    for attempt in range(7):
        diffs = datetime.timedelta(days=diff - attempt)
        day = today + diffs
        if day.weekday() in [0, 7]:
            return day
    return today + datetime.timedelta(days=-7)

def next_sunday(diff: int) -> Day:
    today = datetime.date.today()
    for attempt in range(7):
        diffs = datetime.timedelta(days=diff + attempt)
        day = today + diffs
        if day.weekday() in [0, 7]:
            return day
    return today + datetime.timedelta(days=+7)

def get_date(text: str, on_or_before: Optional[Day] = None) -> Day:
    if isinstance(text, Day):
        return text
    refday = on_or_before or datetime.date.today()
    baseyear = str(refday.year)
    if re.match(r"\d+-\d+-\d+", text):
        return date_isoformat(text)
    if re.match(r"\d+-\d+", text):
        text2 = baseyear + "-" + text
        return date_isoformat(text2)
    if re.match(r"\d+[.]\d+[.]\d+", text):
        return date_dotformat(text)
    if re.match(r"\d+[.]\d+[.]", text):
        text2 = text + baseyear
        return date_dotformat(text2)
    if re.match(r"\d+[.]", text):
        basemonth = str(refday.month)
        text2 = text + basemonth + "." + baseyear
        return date_dotformat(text2)
    logg.error("'%s' does not match YYYY-mm-dd", text)
    return date_isoformat(text)

def read_data(filename: str) -> JSONList:
    logg.info("reading %s", filename)
    return scan_data(open(filename))
def scan_data(lines_from_file: Union[Sequence[str], TextIO]) -> JSONList:
    prefixed = {}
    customer = {}
    projects = {}
    proj_ids = {}
    custname = {}
    projname = {}
    #
    on_or_before = get_zeit_before()
    on_or_after = get_zeit_after()
    logg.info("reading %s - %s", on_or_after, on_or_before)
    idvalues: Dict[str, str] = {}
    cols0 = re.compile(r"^(\S+)\s+(\S+)+\s+(\S+)(\s*)$")
    cols1 = re.compile(r"^(\S+)\s+(\S+)+\s+(\S+)\s+(.*)")
    weekspan1 = re.compile(r"(\d+[.]\d+[.]\d*)-*(\d+[.]\d+[.]\d*).*")
    weekstart1 = re.compile(r"(\d+[.]\d+[.]\d*) *$")
    timespan = re.compile(r"(\d+)(:\d+)?-(\d+)(:\d+)?")
    mo, di, mi, do, fr, sa, so = None, None, None, None, None, None, None
    data: JSONList = []
    ignore = False
    for line in lines_from_file:
        try:
            line = line.strip()
            if not line:
                continue
            if line.startswith("#"):
                continue
            if line.startswith(">>"):
                as_prefixed = re.compile(r'^(\S+)\s+=\s*(\S+)')
                as_customer = re.compile(r'^(\S+)\s+\[(.*)\](.*)')
                as_project0 = re.compile(r'^(\S+)\s+["](AS-(\d+):.*)["](.*)')
                as_project1 = re.compile(r'^(\S+)\s+["](.*)["](.*)')
                as_project2 = re.compile(r'^(\S+)\s+(\w+):\s+["](.*)["](.*)')
                m = as_prefixed.match(line[2:].strip())
                if m:
                    prefixed[m.group(1)] = m.group(2)
                    continue
                m = as_customer.match(line[2:].strip())
                if m:
                    customer[m.group(1)] = m.group(2)
                    customer[m.group(1).upper()] = m.group(2)
                    projects[m.group(1)] = ""  # empty is always allowed (as of 2021)
                    projects[m.group(1).upper()] = ""
                    shorthand = m.group(3).strip().replace("#", ":")
                    if shorthand:
                        custname[m.group(2)] = shorthand
                    continue
                m = as_project0.match(line[2:].strip())
                if m:
                    projects[m.group(1)] = m.group(2)
                    proj_ids[m.group(1)] = m.group(3)
                    shorthand = m.group(4).strip().replace("#", ":")
                    if not shorthand: shorthand = m.group(2)
                    projname[m.group(1)] = shorthand
                    continue
                m = as_project1.match(line[2:].strip())
                if m:
                    projects[m.group(1)] = m.group(2)
                    shorthand = m.group(3).strip().replace("#", ":")
                    if not shorthand: shorthand = m.group(2)
                    projname[m.group(1)] = shorthand
                    continue
                m = as_project2.match(line[2:].strip())
                if m:
                    projects[m.group(1)] = m.group(3)
                    proj_ids[m.group(1)] = m.group(2)
                    shorthand = m.group(4).strip().replace("#", ":")
                    if not shorthand: shorthand = m.group(3)
                    projname[m.group(1)] = shorthand
                    continue
                logg.error("??? %s", line)
                continue
            m0 = cols0.match(line)
            m1 = cols1.match(line)
            m = m1 or m0
            if not m:
                if re.match("^\S+ [(].*", line):
                    logg.debug("?? %s", line)
                    continue
                if re.match("^\S+ \d+-\d+.*", line):
                    logg.debug("?? %s", line)
                    continue
                logg.error("?? %s", line)
                continue
            day, time, proj, desc = m.groups()
            if time.startswith("("):
                logg.debug("??: %s", line)
                continue
            mm = timespan.match(time + "$")
            if mm:
                logg.error("ignoring a timespan %s (%s)", time, line.strip())
                continue
            weekdesc = ""
            weekdays = ["so", "mo"]
            # old-style "** **** WEEK ..."
            if day.strip() in ["**"]:
                if proj.strip() not in ["WEEK"]:
                    logg.error("could not check *** %s", proj)
                    continue
                weekdesc = desc
                logg.debug("found weekdesc %s", weekdesc)
            elif time.strip() in ["**", "***", "****", "*****", "******", "*******"]:
                if proj.strip() not in ["WEEK"]:
                    logg.error("could not check *** %s", proj)
                    continue
                weekdesc = desc
                weekdays = [day]
                logg.debug("found weekdesc %s", weekdesc)
            if weekdesc:
                span1 = weekspan1.match(desc)
                start1 = weekstart1.match(desc)
                match1 = span1 or start1
                if not match1:
                    logg.error("could not parse WEEK %s", desc)
                    continue
                # sync weekdays to dates
                today = datetime.date.today()
                baseyear = on_or_before.year
                date1 = get_date(match1.group(1), on_or_before)
                if date1 > today:
                    # date1 = datetime.date(baseyear-1, m1, d1)
                    ignore = True
                else:
                    ignore = False
                logg.debug("start of week %s", date1)
                offset = 0
                plus2 = date1 + datetime.timedelta(days=2)
                if "sa" in weekdays and plus2.weekday() == 0:
                    sa = date1 + datetime.timedelta(days=0)
                    so = date1 + datetime.timedelta(days=1)
                    mo = date1 + datetime.timedelta(days=2)
                    di = date1 + datetime.timedelta(days=3)
                    mi = date1 + datetime.timedelta(days=4)
                    do = date1 + datetime.timedelta(days=5)
                    fr = date1 + datetime.timedelta(days=6)
                    logg.debug("accept %s %s as 'sa'", weekdays, date1)
                    continue
                elif "so" in weekdays and plus2.weekday() == 1:
                    so = date1 + datetime.timedelta(days=0)
                    mo = date1 + datetime.timedelta(days=1)
                    di = date1 + datetime.timedelta(days=2)
                    mi = date1 + datetime.timedelta(days=3)
                    do = date1 + datetime.timedelta(days=4)
                    fr = date1 + datetime.timedelta(days=5)
                    sa = date1 + datetime.timedelta(days=6)
                    logg.debug("accept %s %s as 'so'", weekdays, date1)
                    continue
                elif "so" in weekdays and "mo" in weekdays and plus2.weekday() == 2:
                    so = date1 + datetime.timedelta(days=1)
                    mo = date1 + datetime.timedelta(days=2)
                    di = date1 + datetime.timedelta(days=3)
                    mi = date1 + datetime.timedelta(days=4)
                    do = date1 + datetime.timedelta(days=5)
                    fr = date1 + datetime.timedelta(days=6)
                    sa = date1 + datetime.timedelta(days=7)
                    logg.debug("accept %s %s as 'so'", weekdays, date1)
                    continue
                elif "mo" in weekdays and plus2.weekday() == 2:
                    mo = date1 + datetime.timedelta(days=1)
                    di = date1 + datetime.timedelta(days=2)
                    mi = date1 + datetime.timedelta(days=3)
                    do = date1 + datetime.timedelta(days=4)
                    fr = date1 + datetime.timedelta(days=5)
                    sa = date1 + datetime.timedelta(days=6)
                    so = date1 + datetime.timedelta(days=7)
                    logg.debug("accept %s %s as 'mo'", weekdays, date1)
                    continue
                else:
                    logg.error("not a week start: %s", desc)
                    logg.error(" real date: %s", date1)
                    logg.error("  real day: %s (allowed %s)", ["mo", "di", "mi",
                                                               "do", "fr", "sa", "so"][date1.weekday()], weekdays)
                    continue
                logg.error("what is a '%s'?", line)
            # else
            if day not in ["mo", "di", "mi", "do", "fr", "sa", "so"]:
                logg.error("no day to put the line to: %s", day)
                logg.error("   %s", line.strip())
                continue
            if ignore:
                logg.warning("ignoring future %s", line)
                continue
            else:
                daydate = None
                if day in ["mo"]:
                    daydate = mo
                if day in ["di"]:
                    daydate = di
                if day in ["mi"]:
                    daydate = mi
                if day in ["do"]:
                    daydate = do
                if day in ["fr"]:
                    daydate = fr
                if day in ["sa"]:
                    daydate = sa
                if day in ["so"]:
                    daydate = so
            if daydate is None:
                logg.error("no daydate for day '%s'", day)
                continue
            if daydate < on_or_after:
                logg.debug("daydate %s is before %s", daydate, on_or_after)
                continue
            if daydate > on_or_before:
                logg.debug("daydate %s is after %s", daydate, on_or_before)
                continue
            if True:
                prefix = proj
                if desc.strip().startswith(":"):
                    desc = proj
                elif proj[-1] not in "0123456789" and len(proj) > 4:
                    prefix = proj
                elif proj in prefixed:
                    prefix = prefixed[proj]
                itemDate = daydate
                itemTime = time2float(time)
                itemDesc = prefix + " " + cleandesc(desc)
                itemPref = prefix
                itemProj = customer[proj]
                itemTask = projects[proj]
                itemUser = get_user_name()
                if ZEIT_SHORT:
                    if customer[proj] in custname:
                        itemProj = custname[customer[proj]]
                    if proj in projname:
                        itemTask = projname[proj]
                        if "(onsite)" in desc:
                            itemTask = projname[proj] + " (onsite)"
                # idx = proj_ids[proj]
                datex = int(daydate.strftime("%y%m%d"))
                # year = daydate.strftime("%y")
                itemID = "%s%s" % (datex, proj)
                ok = True
                if ZEIT_PROJFILTER and ok:
                    ok = False
                    for check in ZEIT_PROJFILTER.split(","):
                        if check and check.lower() in itemProj.lower():
                            ok = True
                    logg.info("odoo filter '%s' on project '%s' => %s", ZEIT_PROJFILTER, itemProj, ok)
                if ZEIT_TASKFILTER and ok:
                    ok = False
                    for check in ZEIT_TASKFILTER.split(","):
                        if check and check.lower() in itemTask.lower():
                            ok = True
                    logg.info("odoo filter '%s' on task '%s' => %s", ZEIT_TASKFILTER, itemTask, ok)
                if ZEIT_TEXTFILTER and ok:
                    ok = False
                    for check in ZEIT_TEXTFILTER.split(","):
                        if check and check.lower() in proj.lower():
                            ok = True
                    logg.info("text filter '%s' on project %s => %s", ZEIT_TEXTFILTER, proj, ok)
                if ZEIT_DESCFILTER and ok:
                    ok = False
                    for check in ZEIT_DESCFILTER.split(","):
                        if check and check.lower() in itemDesc.lower():
                            ok = True
                    logg.info("text filter '%s' on description %s => %s", ZEIT_DESCFILTER, itemDesc, ok)
                if not ZEIT_EXTRATIME:
                    if "extra " in itemTask:
                        ok = False
                    if "check " in itemTask:
                        ok = False
                item: JSONDict = {}
                item[TitleID] = itemID
                item[TitleDate] = itemDate
                item[TitleTime] = itemTime
                item[TitleDesc] = itemDesc
                item[TitlePref] = itemPref
                item[TitleProj] = itemProj
                item[TitleTask] = itemTask
                item[TitleUser] = itemUser
                if ok:
                    data.append(item)
                    logg.debug(" append %s", item)
                #
                if itemID in idvalues:
                    logg.error("duplicate idvalue %s", itemID)
                    logg.error("OLD:   %s", idvalues[itemID].strip())
                    logg.error("NEW:   %s", line.strip())
                idvalues[itemID] = line
        except:
            logg.error("FOR:    %s", line.strip())
            raise
    return data

def run(filename: str) -> None:
    before = get_zeit_before()
    after = get_zeit_after()
    if after.year != before.year:
        logg.error("--after / --before must be the same year (-a ... to -b ...)")
    logg.error("read %s", filename)
    data = read_data(filename)
    if WRITEJSON:
        json_text = tabtotext.tabToJSON(data)
        json_file = filename + ".json"
        with open(json_file, "w") as f:
            f.write(json_text)
        logg.log(DONE, "written %s (%s entries)", json_file, len(data))
    if WRITECSV:
        csv_text = tabtotext.tabToJSON(data)
        csv_file = filename + ".csv"
        with open(csv_file, "w") as f:
            f.write(csv_text)
        logg.log(DONE, "written %s (%s entries)", csv_file, len(data))

if __name__ == "__main__":
    from optparse import OptionParser
    cmdline = OptionParser("%prog files...")
    cmdline.add_option("-v", "--verbose", action="count", default=0,
                       help="more verbose logging")
    cmdline.add_option("-a", "--after", metavar="DATE", default=ZEIT_AFTER,
                       help="only evaluate entrys on and after [first of year]")
    cmdline.add_option("-b", "--before", metavar="DATE", default=ZEIT_BEFORE,
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
    opt, args = cmdline.parse_args()
    logging.basicConfig(level=max(0, logging.WARNING - 10 * opt.verbose))
    logg.setLevel(level=max(0, logging.WARNING - 10 * opt.verbose))
    # logg.addHandler(logging.StreamHandler())
    ZEIT_USER_NAME = opt.user_name
    ZEIT_SHORT = opt.short
    ZEIT_EXTRATIME = opt.extra
    ZEIT_PROJFILTER = opt.projfilter
    ZEIT_TASKFILTER = opt.taskfilter
    ZEIT_TEXTFILTER = opt.textfilter
    ZEIT_DESCFILTER = opt.descfilter
    ZEIT_FILENAME = opt.filename
    ZEIT_SUMMARY = opt.summary
    ZEIT_AFTER = opt.after
    ZEIT_BEFORE = opt.before
    if not args:
        args = [get_zeit_filename()]
        logg.info(" %s ", args)
    for arg in args:
        run(arg)
