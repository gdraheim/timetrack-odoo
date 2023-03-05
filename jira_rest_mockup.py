#! /usr/bin/env python3
"""
Mockup interface to Jira as a method to read and store worklog entries
"""

__copyright__ = "(C) 2022-2023 Guido Draheim, licensed under the Apache License 2.0"""
__version__ = "0.3.2096"

from typing import Union, Dict, List, Any, Optional, Tuple, Iterable, Iterator, cast
from requests import Session, Response, HTTPError
import warnings
import logging
import json
import os
import re
import sys
import datetime
from urllib.parse import quote_plus as qq
import netrc
import gitrc
from dayrange import get_date
from tabtotext import JSONDict, JSONList, JSONItem

logg = logging.getLogger(__name__ == "__main__" and os.path.basename(sys.argv[0]) or __name__)

Day = datetime.date
NIX = ""

db_tickets: Dict[str, Dict[int, JSONDict]] = {}
db_next_id = 1000

class JiraException(Exception):
    pass

def reset() -> None:
    db_tickets["SAND-4"] = {}
    db_tickets["BUGS-5"] = {}
    db_next_id = 1000
    day = Day(2020,12,12)
    work = Worklogs()
    work.worklog_create("SAND-4", day, 2, "local extending frontend")
    work.worklog_create("BUGS-5", day, 3, "local analyzed problem")

def jiraGetWorklog(remote: str, issue: str) -> JSONList:
    if issue in db_tickets:
        return list(db_tickets[issue].values())
    raise JiraException("no such issue")

class Worklogs:
    def __init__(self, user: str = NIX, remote: str = NIX) -> None:
        self.remote = remote
        self.user = user
    def timesheet(self, issue: str, on_or_after: Day, on_or_before: Day) -> Iterator[JSONDict]:
        global db_next_id, db_tickets
        if issue not in db_tickets:
            raise JiraException("no such issue")
        for worklog, record in db_tickets[issue].items():
            worktime = cast(Day, record["entry_date"])
            if on_or_after > worktime or worktime > on_or_before:
                continue
            yield record.copy()
    def worklog_create(self, issue: str, ondate: Day, size: float, desc: str) -> JSONDict:
        global db_next_id, db_tickets
        if issue not in db_tickets:
            raise JiraException("no such issue")
        next_id = db_next_id
        db_next_id += 1
        record: JSONDict = {}
        record["entry_id"] = next_id
        record["entry_date"] = ondate
        record["entry_size"] = size
        record["entry_desc"] = desc
        record["entry_user"] = self.user
        db_tickets[issue][next_id] = record
        return record
    def worklog_update(self, worklog: int, issue: str, ondate: Day, size: float, desc: str) -> JSONDict:
        global db_next_id, db_tickets
        if issue not in db_tickets:
            raise JiraException("no such issue")
        if worklog in db_tickets[issue]:
            del db_tickets[issue][worklog]
        return {}
