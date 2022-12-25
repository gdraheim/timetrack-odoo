#! /usr/bin/python3
from typing import Dict, List, Optional, Generator, cast
from odoo_rest import Cookies, UserID, ProjID, ProjREF, TaskID, TaskREF, EntryID, OdooException

from tabtotext import JSONList, JSONDict, JSONItem, Date, Time

import sys
import os.path as path
import datetime

import logging
logg = logging.getLogger(__name__ == "__main__" and path.basename(sys.argv[0]) or __name__)

Day = Date
Num = float

mock_uid: UserID = 11
mock_sid = "*22*"
mock_db = "mock-db"
mock_url = "https://odoo_rest_mock.test"
mock_proj_1 = "Project-1"
mock_task_1 = "Developments"
mock_proj_2 = "MGMT"
mock_task_2 = "Project Management"

DB = mock_db
URL = mock_url

db_projlist = [mock_proj_1, mock_proj_2]
db_tasklist = {mock_proj_1: [mock_task_1], mock_proj_2: [mock_task_2]}
db_records: JSONList = []

def reset() -> None:
    global DB, URL
    DB = mock_db
    URL = mock_url
    global db_projlist, db_tasklist, db_records
    db_projlist = [mock_proj_1, mock_proj_2]
    db_tasklist = {mock_proj_1: [mock_task_1], mock_proj_2: [mock_task_2]}
    db_records = []

class Odoo:
    def __init__(self, url: Optional[str] = None, db: Optional[str] = None):
        self.url: str = url or URL
        self.db: str = db or DB
    def login(self) -> UserID:
        return mock_uid
    def from_login(self) -> UserID:
        return mock_uid
    def for_user(self, name: str) -> "Odoo":
        return self
    def databases(self) -> List[str]:
        return [mock_db]
    def projects(self) -> JSONList:
        return [{"proj_id": proj_id, "proj_name": proj_name
                 } for proj_id, proj_name in enumerate(db_projlist)]
    def project_tasks(self, proj_id: int = 89) -> JSONList:
        return list(self.each_project_tasks(proj_id))
    def each_project_tasks(self, proj_id: int = 89) -> Generator[JSONDict, None, None]:
        for p_id, p_name in enumerate(db_projlist):
            if proj_id and p_id != proj_id:
                continue
            if p_name not in db_tasklist:
                continue
            for t_id, t_name in enumerate(db_tasklist[p_name]):
                yield {"proj_id": p_id, "proj_name": p_name,
                       "task_id": t_id, "task_name": t_name}
    def proj_id(self, proj_id: ProjREF) -> int:
        if isinstance(proj_id, int):
            return proj_id
        for p_id, p_name in enumerate(db_projlist):
            if p_name == proj_id:
                return p_id
        logg.warning("could not resolve proj_id '%s'", proj_id)
        return cast(int, proj_id)
    def task_id(self, proj_id: ProjREF, task_id: TaskREF) -> int:
        if isinstance(task_id, int):
            return task_id
        for p_id, p_name in enumerate(db_projlist):
            if str(proj_id) == p_name or str(proj_id) == str(p_id):
                for t_id, t_name in enumerate(db_tasklist[p_name]):
                    if t_name == task_id:
                        return t_id
        logg.warning("could not resolve task_id '%s' for proj_id '%s'", task_id, proj_id)
        return cast(int, task_id)
    def proj_name(self, proj_name: ProjREF) -> str:
        if isinstance(proj_name, str):
            return proj_name
        for p_id, p_name in enumerate(db_projlist):
            if p_id == proj_name:
                return p_name
        logg.warning("could not resolve proj_name '%s'", proj_name)
        return cast(str, proj_name)
    def task_name(self, proj_name: ProjREF, task_name: TaskREF) -> str:
        if isinstance(task_name, str):
            return task_name
        for p_id, p_name in enumerate(db_projlist):
            if str(proj_name) == p_name or str(proj_name) == str(p_id):
                for t_id, t_name in enumerate(db_tasklist[p_name]):
                    if t_id == task_name:
                        return t_name
        logg.warning("could not resolve task_name '%s' for proj_name '%s'", task_name, proj_name)
        return cast(str, task_name)
    def timesheet_records(self, date: Optional[Date] = None) -> JSONList:
        return list(self.each_timesheet_records(date))
    def each_timesheet_records(self, date: Optional[Date] = None) -> Generator[JSONDict, None, None]:
        for record in db_records:
            if not date or record["entry_date"] == date:
                yield record
    def timesheet_record(self, proj: str, task: str, date: Optional[Date] = None) -> JSONList:
        return list(self.each_timesheet_record(proj, task, date))
    def each_timesheet_record(self, proj: str, task: str, date: Optional[Date] = None) -> Generator[JSONDict, None, None]:
        for record in db_records:
            if record["proj_id"] == proj or record["proj_name"] == proj:
                if record["task_id"] == task or record["task_name"] == task:
                    if not date or record["entry_date"] == date:
                        yield record
    def timesheet_write(self, entry_id: EntryID, proj: ProjREF, task: TaskREF, date: Day, time: Num, desc: str) -> bool:
        proj_id = self.proj_id(proj)
        task_id = self.task_id(proj_id, task)
        proj_name = self.proj_name(proj)
        task_name = self.task_name(proj_name, task)
        record: JSONDict = {
            "proj_id": proj_id, "proj_name": proj_name,
            "task_id": task_id, "task_name": task_name,
            "user_id": mock_uid, "user_name": str(mock_uid),
            "entry_size": time, "entry_desc": desc,
            "entry_id": entry_id, "entry_date": date}
        db_records[entry_id] = record
        return True
    def timesheet_create(self, proj: ProjREF, task: TaskREF, date: Day, time: Num, desc: str) -> bool:
        proj_id = self.proj_id(proj)
        task_id = self.task_id(proj_id, task)
        proj_name = self.proj_name(proj)
        task_name = self.task_name(proj_name, task)
        record: JSONDict = {
            "proj_id": proj_id, "proj_name": proj_name,
            "task_id": task_id, "task_name": task_name,
            "user_id": mock_uid, "user_name": str(mock_uid),
            "entry_size": time, "entry_desc": desc,
            "entry_id": len(db_records), "entry_date": date}
        db_records.append(record)
        return True
    def timesheet_update(self, proj: ProjREF, task: TaskREF, date: Day, time: Num, desc: str) -> bool:
        done = 0
        for record in db_records:
            if record["proj_id"] == proj or record["proj_name"] == proj:
                if record["task_id"] == task or record["task_name"] == task:
                    if not date or record["entry_date"] == date:
                        record["entry_size"] = time
                        record["entry_desc"] = desc
                        done += 1
        if done:
            return True
        return self.timesheet_create(proj, task, date, time, desc)
    def timesheet(self, after: Day, before: Optional[Day] = None) -> JSONList:
        if not before:
            before = datetime.date.today()
        if after > before:
            logg.error("--after=DAY must be --before=DAY")
            raise OdooException("bad timespan for timesheet()")
        timespan = before - after
        if timespan.days > 33:
            logg.warning("--after=%s --before=%s is %s days", after.isoformat(), before.isoformat(), timespan.days)
        else:
            logg.info("--after=%s --before=%s is %s days", after.isoformat(), before.isoformat(), timespan.days)
        ondate = after
        records: JSONList = []
        for attempt in range(366):
            # logg.debug("ondate %s   (after %s before %s)", ondate.isoformat(), after.isoformat(), before.isoformat())
            found = self.timesheet_records(ondate)
            if found:
                for record in found:
                    records.append(record)
            if ondate == before:
                break
            ondate += datetime.timedelta(days=1)
        return records
