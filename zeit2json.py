#! /usr/bin/env python3
"""
Read zeit.txt files and format as odoo-import data. The resulting csv or xlsx
can imported via the Odoo web UI. Here it is a helper module generating json
data (list of dict) in the odoo-import format which get synchronized to Odoo
or Jira via their Rest APIs. See zeit2odoo.py and zeit2jira.py.

(this module was initially developed as zeit2excel.py and retains some of the
older optins)
"""

__copyright__ = "(C) 2017-2024 Guido Draheim, licensed under the Apache License 2.0"""
__version__ = "0.6.3352"

from typing import List, Dict, Union, Optional, Sequence, TextIO, Iterator, cast

import logging
import re
import os
import csv
import datetime
import os.path as path

import tabtotext
from tabtotext import JSONList, JSONDict, JSONItem, viewFMT
from timerange import get_date, Day, is_dayrange, dayrange
from odootopic import OdooValuesForTopic

logg = logging.getLogger("zeit2json")
DONE = (logging.WARNING + logging.ERROR) // 2
NOTE = (logging.INFO + logging.WARNING) // 2
HINT = (logging.INFO + logging.DEBUG) // 2
logging.addLevelName(DONE, "DONE")
logging.addLevelName(NOTE, "NOTE")
logging.addLevelName(HINT, "HINT")


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
ZEIT_FUTURE = False

DEFAULT_FILENAME = "~/zeit{YEAR}.txt"

WRITEXLSX = False
WRITEJSON = True
WRITECSV = True
JSONFILE = ""
XLSXFILE = ""
CSVFILE = ""
OUTPUT = ""
LABELS: List[str] = []

NEWFORMAT = True
TitleID = "ID"
TitleDate = "Date"  # "Datum"
TitleUser = "User"
TitleDesc = "Description"  # "Beschreibung"
TitlePref = "Topic"  # Prefix used in Desc
TitleProj = "Project"  # "Projekt"
TitleTask = "Task"  # "Aufgabe"
TitleTime = "Quantity"  # "Anzahl"
TitleTicket = "Ticket"

# format to map a topic to the proj/task
_zeit_topics_mapping = """
>> odoo [GUIDO (Private Investigations)]
>> odoo "Odoo Automation",
"""

class DateFromWeekday:
    mo: Optional[Day] = None
    di: Optional[Day] = None
    mi: Optional[Day] = None
    do: Optional[Day] = None
    fr: Optional[Day] = None
    sa: Optional[Day] = None
    so: Optional[Day] = None
    ignore = False
    def __init__(self) -> None:
        self.weekspan1 = re.compile(r"(\d+[.]\d+[.]\d*)-*(\d+[.]\d+[.]\d*).*")
        self.weekstart1 = re.compile(r"(\d+[.]\d+[.]\d*) *$")
    def setweek(self, weekdesc: str, weekdays: List[str] = ["so", "mo"], refdate: Optional[Day] = None) -> bool:
        today = Day.today()
        span1 = self.weekspan1.match(weekdesc)
        start1 = self.weekstart1.match(weekdesc)
        match1 = span1 or start1
        if not match1:
            logg.error("could not parse WEEK %s", weekdesc)
            return False
        # sync weekdays to dates
        date1 = get_date(match1.group(1), refdate or today)
        if date1 > today and not ZEIT_FUTURE:
            logg.info("going to ignore future week date (%s)", date1)
            self.ignore = True
        else:
            self.ignore = False
        # checking if given date1 matches with day-name of the weekstart
        logg.debug("start of week %s", date1)
        offset = 0
        plus2 = date1 + datetime.timedelta(days=2)
        if "sa" in weekdays and plus2.weekday() == 0:  # 0(monday)
            self.sa = date1 + datetime.timedelta(days=0)
            self.so = date1 + datetime.timedelta(days=1)
            self.mo = date1 + datetime.timedelta(days=2)
            self.di = date1 + datetime.timedelta(days=3)
            self.mi = date1 + datetime.timedelta(days=4)
            self.do = date1 + datetime.timedelta(days=5)
            self.fr = date1 + datetime.timedelta(days=6)
            logg.debug("accept %s %s as 'sa'", weekdays, date1)
            return True
        elif "so" in weekdays and plus2.weekday() == 1:  # 1(tuesday)
            self.so = date1 + datetime.timedelta(days=0)
            self.mo = date1 + datetime.timedelta(days=1)
            self.di = date1 + datetime.timedelta(days=2)
            self.mi = date1 + datetime.timedelta(days=3)
            self.do = date1 + datetime.timedelta(days=4)
            self.fr = date1 + datetime.timedelta(days=5)
            self.sa = date1 + datetime.timedelta(days=6)
            logg.debug("accept %s %s as 'so'", weekdays, date1)
            return True
        elif "so" in weekdays and "mo" in weekdays and plus2.weekday() == 2:
            self.so = date1 + datetime.timedelta(days=1)
            self.mo = date1 + datetime.timedelta(days=2)
            self.di = date1 + datetime.timedelta(days=3)
            self.mi = date1 + datetime.timedelta(days=4)
            self.do = date1 + datetime.timedelta(days=5)
            self.fr = date1 + datetime.timedelta(days=6)
            self.sa = date1 + datetime.timedelta(days=7)
            logg.debug("accept %s %s as 'so'", weekdays, date1)
            return True
        elif "mo" in weekdays and plus2.weekday() == 2:
            self.mo = date1 + datetime.timedelta(days=1)
            self.di = date1 + datetime.timedelta(days=2)
            self.mi = date1 + datetime.timedelta(days=3)
            self.do = date1 + datetime.timedelta(days=4)
            self.fr = date1 + datetime.timedelta(days=5)
            self.sa = date1 + datetime.timedelta(days=6)
            self.so = date1 + datetime.timedelta(days=7)
            logg.debug("accept %s %s as 'mo'", weekdays, date1)
            return True
        else:
            logg.error("not a week start: %s", weekdesc)
            logg.error(" real date: %s", date1)
            logg.error("  real day: %s (allowed %s)", ["mo", "di", "mi",
                                                       "do", "fr", "sa", "so"][date1.weekday()], weekdays)
            logg.info("going to ignore incompatible weekstart (%s %s)", weekdays, weekdesc)
            self.ignore = True
            return False
    def daydate(self, day: str, line: Optional[str] = None) -> Optional[Day]:
        if self.ignore:
            if line:
                logg.warning("ignoring %s", line)
            return None
        if day in ["mo"]:
            return self.mo
        if day in ["di", "tu"]:
            return self.di
        if day in ["mi", "we"]:
            return self.mi
        if day in ["do", "th"]:
            return self.do
        if day in ["fr"]:
            return self.fr
        if day in ["sa"]:
            return self.sa
        if day in ["so", "su"]:
            return self.so
        logg.error("no day to put the line to: %s", day)
        if line:
            logg.error("   %s", line.strip())
        return None

def time2float(time: str) -> float:
    time = time.replace(",", ".")
    time = time.replace(":00", ".00")
    time = time.replace(":15", ".25")
    time = time.replace(":30", ".50")
    time = time.replace(":45", ".75")
    if len(time) >= 3 and time[-3] == ':' and time[-2].isdigit() and time[-1].isdigit():
        newtime = time[:-3] + ".{:02n}".format(int(time[-2:]) / 60 * 100)
        logg.warning(" !! unusual time %s -> %s", time, newtime)
        return float(newtime)
    return float(time)

def cleandesc(desc: str) -> str:
    d = desc.replace("*", "").replace(" , ", ", ")
    m = re.match("(.*)\\S*\\d:\\d+\\S*$", d)
    if m:
        return m.group(1)
    return d

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

def get_user_name() -> Optional[str]:  # obsolete
    zeit = ZeitConfig()
    return zeit.user_name()
def get_zeit_filename(on_or_after: Optional[Day] = None) -> str:  # obsolete
    after = on_or_after or get_zeit_after()
    return zeit_filename(after)
def zeit_filename(after: Day) -> str:  # obsolete
    zeit = ZeitConfig()
    return zeit.filename(after)

class ZeitConfig:
    pathspec: str
    username: Optional[str]
    site: Optional[str]
    def __init__(self, pathspec: Optional[str] = None, username: Optional[str] = None):
        self.pathspec = pathspec or ""
        self.username = username
    def for_user(self, user: str) -> "ZeitConfig":
        self.username = user
        return self
    def from_file(self, spec: str) -> "ZeitConfig":
        self.pathspec = spec
        return self
    def on_site(self, site: str) -> "ZeitConfig":
        self.site = site
        return self
    def name(self) -> str:
        if self.site:
            return self.site
        return path.basename(path.dirname(self.pathspec))
    def user_name(self) -> Optional[str]:
        global ZEIT_USER_NAME
        if ZEIT_USER_NAME:
            return ZEIT_USER_NAME
        import dotgitconfig
        return dotgitconfig.git_config_value("user.name")
    def filespec(self) -> str:
        if self.pathspec:
            return self.pathspec
        global ZEIT_FILENAME
        if ZEIT_FILENAME:
            return ZEIT_FILENAME
        import dotgitconfig
        found = dotgitconfig.git_config_value("zeit.filename")
        if found:
            return found
        return DEFAULT_FILENAME
    def filename(self, after: Day) -> str:
        filename = self.filespec()
        return self.expand(filename, after)
    def expand(self, filename: str, after: Day) -> str:
        YEAR = after.year
        return path.expanduser(filename.format(**locals()))

class Zeit:
    def __init__(self, config: Optional[ZeitConfig] = None):
        self.config = config or ZeitConfig()
    def read_entries(self, on_or_after: Day, on_or_before: Day) -> JSONList:
        filename = self.config.filename(on_or_after)
        return read_data(filename, on_or_after, on_or_before)
    def read_entries2(self, on_or_after: Day, on_or_before: Day) -> JSONList:
        filename = self.config.filename(on_or_after)
        return read_data2(filename, on_or_after, on_or_before)

def read_zeit(on_or_after: Day, on_or_before: Day) -> JSONList:
    zeit = Zeit()
    return zeit.read_entries(on_or_after, on_or_before)
def read_data(filename: str, on_or_after: Optional[Day] = None, on_or_before: Optional[Day] = None) -> JSONList:
    logg.info("reading %s", filename)
    return scan_data(open(filename), on_or_after, on_or_before)
def read_data2(filename: str, on_or_after: Optional[Day] = None, on_or_before: Optional[Day] = None) -> JSONList:
    logg.info("reading %s", filename)
    return scan_data2(open(filename), on_or_after, on_or_before)

def scan_data2(lines_from_file: Union[Sequence[str], TextIO], on_or_after: Optional[Day] = None, on_or_before: Optional[Day] = None, username: Optional[str] = None) -> JSONList:
    return list(each_scan_data2(lines_from_file, on_or_after or get_zeit_after(), on_or_before or get_zeit_before(), username))
def each_scan_data2(lines_from_file: Union[Sequence[str], TextIO], on_or_after: Day, on_or_before: Day, username: Optional[str] = None) -> Iterator[JSONDict]:
    for item in scanlines(lines_from_file, on_or_after, on_or_before, username):
        if TitleID in item:
            del item[TitleID]  # new
        yield item
def scan_data(lines_from_file: Union[Sequence[str], TextIO], on_or_after: Optional[Day] = None, on_or_before: Optional[Day] = None, username: Optional[str] = None) -> JSONList:
    return list(each_scan_data(lines_from_file, on_or_after or get_zeit_after(), on_or_before or get_zeit_before(), username))
def each_scan_data(lines_from_file: Union[Sequence[str], TextIO], on_or_after: Day, on_or_before: Day, username: Optional[str] = None) -> Iterator[JSONDict]:
    for item in scanlines(lines_from_file, on_or_after, on_or_before, username):
        if TitleTicket in item:
            del item[TitleTicket]  # new
        yield item

def scanlines(lines_from_file: Union[Sequence[str], TextIO], on_or_after: Day, on_or_before: Day, username: Optional[str] = None) -> Iterator[JSONDict]:
    odoomap = OdooValuesForTopic(ZEIT_SHORT)
    weekmap = DateFromWeekday()
    idvalues: Dict[str, str] = {}
    cols0 = re.compile(r"^(\S+)\s+(\S+)+\s+(\S+)(\s*)$")
    cols1 = re.compile(r"^(\S+)\s+(\S+)+\s+(\S+)\s+(.*)")
    timespan = re.compile(r"(\d+)(:\d+)?-(\d+)(:\d+)?")
    for line in lines_from_file:
        try:
            line = line.strip()
            if not line:
                continue
            if line.startswith("#"):
                continue
            if line.startswith(">>"):
                odoomap.scanline(line)
                continue
            # general format is:
            # <weekday> <timespan> <topic-word> <description>
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
            day, time, topic, desc = m.groups()
            if time.startswith("("):
                logg.debug("??: %s", line)
                continue
            mm = timespan.match(time + "$")
            if mm:
                logg.error("ignoring a timespan %s (%s)", time, line.strip())
                continue
            # checking for week start:
            # <weekday> **** WEEK <date-string>
            weekdesc = ""
            weekdays = ["so", "mo"]
            if day.strip() in ["**"]:  # old-style "** **** WEEK ..."
                if topic.strip() not in ["WEEK"]:
                    logg.error("could not check *** %s", topic)
                    continue
                weekdesc = desc
                logg.debug("found weekdesc %s", weekdesc)
            elif time.strip() in ["**", "***", "****", "*****", "******", "*******"]:
                if topic.strip() not in ["WEEK"]:
                    logg.error("could not check *** %s", topic)
                    continue
                weekdesc = desc
                weekdays = [day]
                logg.debug("found weekdesc %s", weekdesc)
            if weekdesc:
                weekmap.setweek(weekdesc, weekdays, on_or_before)
                continue
            # else # convert weekday to real date and get odoo values
            daydate = weekmap.daydate(day, line)
            if daydate is None:
                logg.error("no daydate for day '%s'", day)
                continue
            if on_or_after and daydate < on_or_after:
                logg.debug("daydate %s is before %s", daydate, on_or_after)
                continue
            if on_or_before and daydate > on_or_before:
                logg.debug("daydate %s is after %s", daydate, on_or_before)
                continue
            if True:
                odoo = odoomap.lookup(topic, daydate)
                if not odoo:
                    logg.error("can not find odoo values for topic %s (on %s)", topic, daydate)
                    logg.error("    on line: %s", line.strip())
                    raise ValueError(topic)
                itemDate = daydate
                itemTime = time2float(time)
                itemDesc = odoo.pref + " " + cleandesc(desc)
                itemPref = odoo.pref
                itemProj = odoo.proj
                itemTask = odoo.task
                itemUser = username
                if ZEIT_SHORT:
                    if "(onsite)" in desc:
                        itemTask += " (onsite)"
                # idx = account.proj_ids[proj]
                datex = int(daydate.strftime("%y%m%d"))
                # year = daydate.strftime("%y")
                itemID = "%s%s" % (datex, topic)
                item: JSONDict = {}
                item[TitleID] = itemID
                item[TitleDate] = itemDate
                item[TitleTime] = itemTime
                item[TitleDesc] = itemDesc
                item[TitlePref] = itemPref
                item[TitleProj] = itemProj
                item[TitleTask] = itemTask
                item[TitleUser] = itemUser
                item[TitleTicket] = odoo.ticket  # new
                #
                if itemID in idvalues:
                    logg.error("duplicate idvalue %s", itemID)
                    logg.error("OLD:   %s", idvalues[itemID].strip())
                    logg.error("NEW:   %s", line.strip())
                idvalues[itemID] = line
                yield item
        except:
            logg.error("FOR:    %s", line.strip())
            raise
def filter_data(data: JSONList = []) -> JSONList:
    return list(each_filter_data(data))
def each_filter_data(data: JSONList = []) -> Iterator[JSONDict]:
    r: JSONList = []
    for item in data:
        # itemDate = cast(str, item[TitleDate])
        itemDesc = cast(str, item[TitleDesc])
        itemPref = cast(str, item[TitlePref])
        itemProj = cast(str, item[TitleProj])
        itemTask = cast(str, item[TitleTask])
        ok = True
        if ZEIT_PROJFILTER and ok:
            ok = False
            for check in ZEIT_PROJFILTER.split(","):
                if check and check.lower() in itemProj.lower():
                    ok = True
            logg.log(HINT, "odoo filter '%s' on project '%s' => %s", ZEIT_PROJFILTER, itemProj, ok)
        if ZEIT_TASKFILTER and ok:
            ok = False
            for check in ZEIT_TASKFILTER.split(","):
                if check and check.lower() in itemTask.lower():
                    ok = True
            logg.log(HINT, "odoo filter '%s' on task '%s' => %s", ZEIT_TASKFILTER, itemTask, ok)
        if ZEIT_TEXTFILTER and ok:
            ok = False
            for check in ZEIT_TEXTFILTER.split(","):
                if check and check.lower() in itemPref.lower():
                    ok = True
            logg.log(HINT, "text filter '%s' on project %s => %s", ZEIT_TEXTFILTER, itemPref, ok)
        if ZEIT_DESCFILTER and ok:
            ok = False
            for check in ZEIT_DESCFILTER.split(","):
                if check and check.lower() in itemDesc.lower():
                    ok = True
            logg.log(HINT, "text filter '%s' on description %s => %s", ZEIT_DESCFILTER, itemDesc, ok)
        if not ZEIT_EXTRATIME:
            if "extra " in itemTask:
                ok = False
            if "check " in itemTask:
                ok = False
        if ok:
            yield item

def get_data(filename: str) -> JSONList:
    filename = arg
    on_or_before = get_zeit_before()
    on_or_after = get_zeit_after()
    if on_or_after.year != on_or_before.year:
        logg.error("--after / --before must be the same year (-a ... to -b ...)")
    logg.error("read %s", filename)
    if NEWFORMAT:
        zeitdata = read_data2(filename, on_or_after, on_or_before)
    else:
        zeitdata = read_data(filename, on_or_after, on_or_before)
    return filter_data(zeitdata)

def run(arg: str) -> None:
    if is_dayrange(arg):
        days = dayrange(arg)
        logg.log(DONE, "%s -> %s %s", arg, days.after, days.before)
        global ZEIT_AFTER, ZEIT_BEFORE
        ZEIT_AFTER = days.after.isoformat()
        ZEIT_BEFORE = days.before.isoformat()
        return
    filename = arg
    data = get_data(filename)
    headers = ["Date", "Project", "Task", "Topic", "Ticket", "User", "Quantity:.2f", "Description"]
    if OUTPUT:
        done = tabtotext.print_tabtotext(OUTPUT, data, headers, LABELS)
        if done:
            logg.log(DONE, " %s '%s'", done, OUTPUT)
    if WRITEJSON or JSONFILE:
        FMT = "json"
        json_text = tabtotext.tabtoJSON(data, headers)
        json_file = JSONFILE or f"{filename}.{FMT}"
        with open(json_file, "w") as f:
            f.write(json_text)
        logg.log(DONE, " %s written   %s '%s'  (%s entries)", FMT, viewFMT(FMT), json_file, len(data))
    if WRITECSV or CSVFILE:
        FMT = "csv"
        csv_text = tabtotext.tabtoCSV(data, headers)
        csv_file = CSVFILE or f"{filename}.{FMT}"
        with open(csv_file, "w") as f:
            f.write(csv_text)
        logg.log(DONE, " %s written   %s '%s'  (%s entries)", FMT, viewFMT(FMT), csv_file, len(data))
    if WRITEXLSX or XLSXFILE:
        FMT = "xlsx"
        xlsx_file = XLSXFILE or f"{filename}.{FMT}"
        import tabtoxlsx
        tabtoxlsx.tabtoXLSX(xlsx_file, data, headers)
        logg.log(DONE, " %s written   %s '%s'  (%s entries)", FMT, viewFMT(FMT), xlsx_file, len(data))

if __name__ == "__main__":
    from optparse import OptionParser
    cmdline = OptionParser("%prog [-opt] files...", epilog=__doc__, version=__version__)
    cmdline.formatter.max_help_position = 30
    cmdline.add_option("-v", "--verbose", action="count", default=0, help="more verbose logging")
    cmdline.add_option("-^", "--quiet", action="count", default=0, help="less verbose logging")
    cmdline.add_option("-1", "--oldformat", action="store_true", default=False,
                       help="generate ID column (was used as foreignkey in old odoo)")
    cmdline.add_option("-2", "--newformat", action="store_true", default=False,
                       help="generate Ticket column (can be used to import to jira)")
    cmdline.add_option("-8", "--future", action="store_true", default=ZEIT_FUTURE,
                       help="allow future entries from zeit timesheet")
    cmdline.add_option("-a", "--after", metavar="DATE", default=ZEIT_AFTER,
                       help="only evaluate entrys on and after [first of year]")
    cmdline.add_option("-b", "--before", metavar="DATE", default=ZEIT_BEFORE,
                       help="only evaluate entrys on and before [last of year]")
    cmdline.add_option("-s", "--summary", metavar="TEXT", default=ZEIT_SUMMARY,
                       help="suffix for summary report [%default]")
    cmdline.add_option("-f", "--filename", metavar="TEXT", default=ZEIT_FILENAME,
                       help="choose input filename [%s]" % (ZEIT_FILENAME or DEFAULT_FILENAME))
    cmdline.add_option("-L", "--labels", metavar="LIST", action="append", default=[],
                       help="select and format columns (new=col:h)")
    cmdline.add_option("-o", "--output", metavar="-", help="json|yaml|html|wide|md|htm|tab|csv|dat", default=OUTPUT)
    cmdline.add_option("-J", "--jsonfile", metavar="FILE", default=JSONFILE, help="write also to json data file")
    cmdline.add_option("-X", "--xlsxfile", metavar="FILE", default=XLSXFILE, help="write also to xlsx data file")
    cmdline.add_option("-D", "--csvfile", metavar="FILE", default=CSVFILE, help="write also to sCSV data file")
    cmdline.add_option("-P", "--projfilter", metavar="TEXT", default=ZEIT_PROJFILTER,
                       help="filter for odoo project [%default]")
    cmdline.add_option("-T", "--taskfilter", metavar="TEXT", default=ZEIT_TASKFILTER,
                       help="filter for odoo task [%default]")
    cmdline.add_option("-E", "--descfilter", metavar="TEXT", default=ZEIT_DESCFILTER,
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
    logging.basicConfig(level=max(0, logging.WARNING - 10 * opt.verbose + 10 * opt.quiet))
    logg.setLevel(level=max(0, logging.WARNING - 10 * opt.verbose + 10 * opt.quiet))
    # logg.addHandler(logging.StreamHandler())
    LABELS = opt.labels
    OUTPUT = opt.output
    JSONFILE = opt.jsonfile
    XLSXFILE = opt.xlsxfile
    CSVFILE = opt.csvfile
    if opt.newformat:
        NEWFORMAT = True
    elif opt.oldformat:
        NEWFORMAT = False
    ZEIT_USER_NAME = opt.user_name
    ZEIT_SHORT = opt.short
    ZEIT_EXTRATIME = opt.extra
    ZEIT_PROJFILTER = opt.projfilter
    ZEIT_TASKFILTER = opt.taskfilter
    ZEIT_TEXTFILTER = opt.textfilter
    ZEIT_DESCFILTER = opt.descfilter
    ZEIT_FILENAME = opt.filename
    ZEIT_SUMMARY = opt.summary
    ZEIT_FUTURE = opt.future
    ZEIT_AFTER = opt.after
    ZEIT_BEFORE = opt.before
    if not args or is_dayrange(args[0]):
        args += [get_zeit_filename()]
        logg.info(" %s ", args)
    for arg in args:
        run(arg)
