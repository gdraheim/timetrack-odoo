#! /usr/bin/python3

from typing import Union, Optional

import logging
import re
import datetime

Day = datetime.date

logg = logging.getLogger("dayrange")

class dayrange:
    after: Day
    before: Day
    def __init__(self, after: Union[None,str,Day] = None, before: Union[None,str,Day] = None):
        if not after:
            self.after = firstday_of_month(0)
        elif isinstance(after, str):
            self.after = get_date(after)
        else:
            self.after = after
        if not before:
            self.before = lastday_of_month(0)
        elif isinstance(before, str):
            self.before = get_date(before)
        else:
            self.before = before
    def __len__(self) -> int:
        return( self.before - self.after).days +1
    def __str__(self) -> str:
        after = self.after
        before = self.before
        return f"{after} .. {before}"

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

def check_days(days):
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
        args = [ "check" ]
    for arg in args:
        if arg in [ "check" ]:
            check_days(days)
