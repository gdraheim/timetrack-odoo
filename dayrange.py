#! /usr/bin/python3

from typing import Union, Optional, Tuple

import logging
import re
import datetime

Day = datetime.date

logg = logging.getLogger("dayrange")

FUTURE = 3  # months (otherwise assume date is for last year)

class DayrangeException(Exception):
    pass

symbolic_dayrange = [
    "week", "thisweek", "this-week", "nextweek", "next-week", "lastweek", "last-week",
    "weeks", "lastweeks", "last-weeks", "blastweek", "blast-week", "before-last-week",
    "month", "thismonth", "this-month", "nextmonth", "next-month", "lastmonth", "last-month",
    "months", "lastmonths", "last-months", "beforelastmonth", "blastmonth", "blast-month", "before-last-month",
    "this", "last", "late", "latest", "blast", "beforelast", "before-last", "b4last",
    "M00", "M01", "M02", "M03", "M04", "M05", "M06", "M07", "M08", "M09", "M10", "M11", "M12",
    "M01-M02", "M02-M03", "M03-M04", "M04-M05", "M05-M06", "M06-M07", "M07-M08", "M08-M09", "M09-M10", "M10-M11", "M11-M12",
    "M01-M03", "M02-M04", "M03-M05", "M04-M06", "M05-M07", "M06-M08", "M07-M09", "M08-M10", "M09-M11", "M10-M12",
    "year", "thisyear"]

def is_dayrange(arg: str) -> bool:
    return arg in symbolic_dayrange
def get_symbolic_dayrange(arg: str) -> Tuple[str, str]:
    after, before = days_for_symbolic_dayrange(arg)
    return (after.isoformat(), before.isoformat())
def days_for_symbolic_dayrange(arg: str) -> Tuple[Day, Day]:
    if arg in ["thisweek", "this-week", "week"]:  # e.g. run week sync"
        after = last_sunday(-1)
        before = next_sunday(-1)
        return (after, before)
    if arg in ["lastweek", "last-week", "latest"]:  # e.g. "run latest sync"
        after = last_sunday(-6)
        before = next_sunday(-1)
        today = Day.today()
        if today > before:
           before = today
        return (after, before)
    if arg in ["lastweeks", "last-weeks", "late"]:  # e.g. "run late sync"
        after = last_sunday(-13)
        before = next_sunday(-1)
        today = Day.today()
        if today > before:
           before = today
        return (after, before)
    if arg in ["nextweek", "next-week", "next"]:  # e.g. "run next sync"
        after = last_sunday(+7)
        before = next_sunday(+7)
        return (after, before)
    if arg in ["nextmonth", "next-month"]:
        after = firstday_of_month(+1)
        before = lastday_of_month(+1)
        return (after, before)
    if arg in ["thismonth", "this-month", "this", "month"]:
        after = firstday_of_month(+0)
        before = lastday_of_month(+0)
        return (after, before)
    if arg in ["lastmonth", "last-month", "last"]:  # e.g. "run last summary"
        after = firstday_of_month(-1)
        before = lastday_of_month(-1)
        return (after, before)
    if arg in ["lastmonths", "last-months", "months"]:
        after = firstday_of_month(-1)
        before = lastday_of_month(+0)
        return (after, before)
    if arg in ["beforelastmonth", "before-last-month", "beforelast", "blast", "blast-month", "b4last"]:
        after = firstday_of_month(-2)
        before = lastday_of_month(-2)
        return (after, before)
    if arg in ["M00", "M01", "M02", "M03", "M04", "M05", "M06", "M07", "M08", "M09", "M10", "M11", "M12"]:
        after = firstday_of_month_name(arg)
        before = lastday_of_month_name(arg)
        return (after, before)
    if arg in ["M01-M02", "M02-M03", "M03-M04", "M04-M05", "M05-M06", "M06-M07", "M07-M08", "M08-M09", "M09-M10", "M10-M11", "M11-M12"]:
        after = firstday_of_month_name(arg.split("-")[0])
        before = lastday_of_month_name(arg.split("-")[1])
        if before.year < after.year:
            before = date_dotformat("99.%02i.%04i" % (before.month, after.year))
        return (after, before)
    if arg in ["M01-M03", "M02-M04", "M03-M05", "M04-M06", "M05-M07", "M06-M08", "M07-M09", "M08-M10", "M09-M11", "M10-M12"]:
        after = firstday_of_month_name(arg.split("-")[0])
        before = lastday_of_month_name(arg.split("-")[1])
        if before.year < after.year:
            before = date_dotformat("99.%02i.%04i" % (before.month, after.year))
        return (after, before)
    if arg in ["year", "thisyear"]:
        after = firstday_of_month_name("M01")
        before = lastday_of_month(0)
        return (after, before)
    raise DayrangeException("unknown symbolic dayrange '%s'" % arg)

class Dayrange:
    after: Day
    before: Day
    def __init__(self, after: Day, before: Day):
        self.after = after
        self.before = before
    def __len__(self) -> int:
        return(self.before - self.after).days + 1
    def __str__(self) -> str:
        after = self.after
        before = self.before
        return f"{after} .. {before}"
    def __iter__(self) -> "Dayrange":  # Self in Python 3.11
        return Dayrange(self.after, self.before)
    def __next__(self) -> Day:
        value = self.after
        if value > self.before:
            raise StopIteration()
        self.after += datetime.timedelta(days=1)
        return value
    def __eq__(self, days: object) -> bool:
        if not isinstance(days, Dayrange):
            return NotImplemented
        return self.before == days.before and self.after == days.after
    def __le__(self, days: object) -> bool:
        if not isinstance(days, Dayrange):
            return NotImplemented
        return self.before <= days.before and self.after >= days.after
    def __ge__(self, days: object) -> bool:
        if not isinstance(days, Dayrange):
            return NotImplemented
        return self.before >= days.before and self.after <= days.after
    def __lt__(self, days: object) -> bool:
        return self.__le__(days) and not self.__eq__(days)
    def __gt__(self, days: object) -> bool:
        return self.__ge__(days) and not self.__eq__(days)

class dayrange(Dayrange):
    def __init__(self, after: Union[None, str, Day] = None, before: Union[None, str, Day] = None):
        if not after:
            self.after = firstday_of_month(0)
        elif isinstance(after, str):
            if after in symbolic_dayrange:
                after, before = get_symbolic_dayrange(after)
            elif ".." in after and not before:
                after, before = after.split("..", 1)
            self.after = get_date(after)
        else:
            self.after = after
        if not before:
            self.before = lastday_of_month(0)
        elif isinstance(before, str):
            self.before = get_date(before)
        else:
            self.before = before

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

########################################################
def firstday_of_month(diff: int) -> Day:
    return date_dotformat(first_of_month(diff))
def first_of_month(diff: int) -> str:
    assert -11 <= diff and diff <= +11
    today = Day.today()
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
    today = Day.today()
    year = today.year
    month = today.month + diff
    if month <= 0:
        month += 12
        year -= 1
    if month > 12:
        month -= 12
        year += 1
    return f"99.{month}.{year}"

def firstday_of_month_name(name: str) -> Day:
    return date_dotformat(first_of_month_name(name))
def first_of_month_name(name: str) -> str:
    today = Day.today()
    year = today.year
    #
    monthnames = ["M00", "M01", "M02", "M03", "M04", "M05", "M06", "M07", "M08", "M09", "M10", "M11", "M12"]
    if name in monthnames:
        month = monthnames.index(name)
    else:
        month = today.month
    if month == 0:
        year -= 1  # M00 case
        month = 12
    elif month > today.month + FUTURE:
        year -= 1  # assume last year
    return f"01.{month}.{year}"

def lastday_of_month_name(name: str) -> Day:
    return date_dotformat(last_of_month_name(name))
def last_of_month_name(name: str) -> str:
    today = Day.today()
    year = today.year
    #
    monthnames = ["M00", "M01", "M02", "M03", "M04", "M05", "M06", "M07", "M08", "M09", "M10", "M11", "M12"]
    if name in monthnames:
        month = monthnames.index(name)
    else:
        month = today.month
    if month == 0:
        year -= 1  # M00 case
        month = 12
    elif month > today.month + FUTURE:
        year -= 1  # assume last year
    return f"99.{month}.{year}"

#########################################################
def last_sunday(diff: int) -> Day:
    today = Day.today()
    for attempt in range(7):
        diffs = datetime.timedelta(days=diff - attempt)
        day = today + diffs
        if day.weekday() in [0, 7]:
            return day
    return today + datetime.timedelta(days=-7)

def next_sunday(diff: int) -> Day:
    today = Day.today()
    for attempt in range(7):
        diffs = datetime.timedelta(days=diff + attempt)
        day = today + diffs
        if day.weekday() in [0, 7]:
            return day
    return today + datetime.timedelta(days=+7)

def get_date(text: str, on_or_before: Optional[Day] = None) -> Day:
    if isinstance(text, Day):
        return text
    refday = on_or_before or Day.today()
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

def check_days(days: dayrange) -> None:
    print(f"days = after {days.after} ... {days.before} before")
    amount = len(days)
    print(f"these are {amount} days")

if __name__ == "__main__":
    from optparse import OptionParser
    cmdline = OptionParser("%prog files...")
    cmdline.add_option("-v", "--verbose", action="count", default=0,
                       help="more verbose logging")
    cmdline.add_option("-a", "--after", metavar="DATE", default=None,
                       help="only evaluate on and after [first of month]")
    cmdline.add_option("-b", "--before", metavar="DATE", default=None,
                       help="only evaluate on and before [last of month]")
    opt, args = cmdline.parse_args()
    logging.basicConfig(level=max(0, logging.WARNING - 10 * opt.verbose))
    logg.setLevel(level=max(0, logging.WARNING - 10 * opt.verbose))
    # logg.addHandler(logging.StreamHandler())
    days = dayrange(opt.after, opt.before)
    if not args:
        args = ["check"]
    for arg in args:
        if arg in ["check"]:
            check_days(days)
