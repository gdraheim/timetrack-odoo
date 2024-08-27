#! /usr/bin/env python3

__copyright__ = "(C) 2021-2024 Guido Draheim, licensed under the Apache License 2.0"""
__version__ = "1.1.3352"

import tabtotext
import odoo2data_api_mockup as odoo_api_mockup
import zeit2odoo as sync
import zeit2json as zeit
from typing import Optional
import datetime

import os
import sys
import unittest
import tempfile
import os.path as path
from fnmatch import fnmatchcase as fnmatch
import subprocess

import logging
logg = logging.getLogger("TEST")

SCRIPT = "./zeit2odoo.py"


sync.odoo_api = odoo_api_mockup

zeit2020 = """
>> dev1 [Development]
>> dev1 "project1"
** **** WEEK 05.01.-11.01.
so 1:15 dev1 started
"""

class zeit2odooTest(unittest.TestCase):
    def last_sunday(self) -> datetime.date:
        today = datetime.date.today()
        for earlier in range(8):
            day = today - datetime.timedelta(days=earlier)
            logg.debug("weekday %s earlier %s", day.isoweekday(), earlier)
            if day.isoweekday() in [0, 7]:
                return day
        logg.error("could not find sunday before %s", today)
        return today
    def setUp(self) -> None:
        sync.odoo_api.reset()
        sync.UPDATE = False
    def mk_zeit2020_txt(self, text: Optional[str] = None) -> str:
        text = text or zeit2020
        filename = "tmp.zeit2020.txt"
        with open(filename, "w") as f:
            f.write(text + "\n")
        return filename
    def rm_zeit2020_txt(self) -> None:
        filename = "tmp.zeit2020.txt"
        if os.path.exists(filename):
            os.remove(filename)
    def test_001_check(self) -> None:
        txt = self.mk_zeit2020_txt()
        cmd = f"{SCRIPT} -a 01.01.2020 -b 10.01.2020 -v check --mockup -f {txt}"
        subprocess.call(cmd, shell=True)
        logg.info("you need to add -y to update Odoo")
        self.rm_zeit2020_txt()
    def test_002_valid(self) -> None:
        txt = self.mk_zeit2020_txt()
        cmd = f"{SCRIPT} -a 01.01.2020 -b 10.01.2020 -v valid --mockup -f {txt}"
        subprocess.call(cmd, shell=True)
        logg.info("it summarizes the hours per day")
        self.rm_zeit2020_txt()
    def test_003_update(self) -> None:
        txt = self.mk_zeit2020_txt()
        cmd = f"{SCRIPT} -a 01.01.2020 -b 10.01.2020 -v update --mockup -f {txt}"
        subprocess.call(cmd, shell=True)
        logg.info("you need to add -y to update Odoo")
        self.rm_zeit2020_txt()
    def test_131(self) -> None:
        weekago = datetime.date.today() - datetime.timedelta(days=10)
        nextweek = datetime.date.today() + datetime.timedelta(days=10)
        sunday = self.last_sunday()
        data = zeit.scan_data(f"""
        >> dev1 [Development]
        >> dev1 "project1"
        so **** WEEK {sunday.day}.{sunday.month}.-09.01.
        so 1:15 dev1 started
        """.splitlines())
        logg.debug("data = %s", data)
        # sync.AFTER = (weekago).strftime("%Y-%m-%d")
        # sync.BEFORE = (nextweek).strftime("%Y-%m-%d")
        # sync.run("projects")
        results = sync.summary_per_project_task(data)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["at proj"], "Development")
        self.assertEqual(results[0]["at task"], "project1")
        self.assertEqual(results[0]["odoo"], 0)
        self.assertEqual(results[0]["zeit"], 1.25)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 4)
    def test_132(self) -> None:
        weekago = datetime.date.today() - datetime.timedelta(days=10)
        nextweek = datetime.date.today() + datetime.timedelta(days=10)
        sunday = self.last_sunday()
        data = zeit.scan_data(f"""
        >> dev1 [Development]
        >> dev1 "project1"
        >> dev2 [Development]
        >> dev2 "project2"
        so **** WEEK {sunday.day}.{sunday.month}.-09.01.
        so 1:15 dev1 started
        so 0:15 dev2 started
        """.splitlines())
        logg.debug("data = %s", data)
        # sync.AFTER = (weekago).strftime("%Y-%m-%d")
        # sync.BEFORE = (nextweek).strftime("%Y-%m-%d")
        # sync.run("projects")
        results = sync.summary_per_project_task(data)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["at proj"], "Development")
        self.assertEqual(results[0]["at task"], "project1")
        self.assertEqual(results[0]["odoo"], 0)
        self.assertEqual(results[0]["zeit"], 1.25)
        self.assertEqual(results[1]["at proj"], "Development")
        self.assertEqual(results[1]["at task"], "project2")
        self.assertEqual(results[1]["odoo"], 0)
        self.assertEqual(results[1]["zeit"], 0.25)
        self.assertEqual(len(results), 2)
        self.assertEqual(len(results[0]), 4)
    def test_133(self) -> None:
        weekago = datetime.date.today() - datetime.timedelta(days=10)
        nextweek = datetime.date.today() + datetime.timedelta(days=10)
        sunday = self.last_sunday()
        data = zeit.scan_data(f"""
        >> dev1 [Development]
        >> dev1 "project1"
        so **** WEEK {sunday.day}.{sunday.month}.-09.01.
        so 1:15 dev1 started
        """.splitlines())
        logg.debug("data = %s", data)
        # sync.AFTER = (weekago).strftime("%Y-%m-%d")
        # sync.BEFORE = (nextweek).strftime("%Y-%m-%d")
        # sync.run("projects")
        results = sync.summary_per_project(data)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["at proj"], "Development")
        self.assertNotIn("at task", results[0])
        self.assertEqual(results[0]["odoo"], 0)
        self.assertEqual(results[0]["zeit"], 1.25)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 3)
    def test_134(self) -> None:
        weekago = datetime.date.today() - datetime.timedelta(days=10)
        nextweek = datetime.date.today() + datetime.timedelta(days=10)
        sunday = self.last_sunday()
        data = zeit.scan_data(f"""
        >> dev1 [Development]
        >> dev1 "project1"
        >> dev2 [Development]
        >> dev2 "project2"
        so **** WEEK {sunday.day}.{sunday.month}.-09.01.
        so 1:15 dev1 started
        so 0:15 dev2 started
        """.splitlines())
        logg.debug("data = %s", data)
        # sync.AFTER = (weekago).strftime("%Y-%m-%d")
        # sync.BEFORE = (nextweek).strftime("%Y-%m-%d")
        # sync.run("projects")
        results = sync.summary_per_project(data)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["at proj"], "Development")
        self.assertNotIn("at task", results[0])
        self.assertEqual(results[0]["odoo"], 0)
        self.assertEqual(results[0]["zeit"], 1.50)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 3)
    def test_135(self) -> None:
        weekago = datetime.date.today() - datetime.timedelta(days=10)
        nextweek = datetime.date.today() + datetime.timedelta(days=10)
        sunday = self.last_sunday()
        data = zeit.scan_data(f"""
        >> dev1 [Development]
        >> dev1 "project1"
        so **** WEEK {sunday.day}.{sunday.month}.-09.01.
        so 1:15 dev1 started
        """.splitlines())
        logg.debug("data = %s", data)
        # sync.AFTER = (weekago).strftime("%Y-%m-%d")
        # sync.BEFORE = (nextweek).strftime("%Y-%m-%d")
        # sync.run("projects")
        results = sync.summary_per_topic(data)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["at topic"], "dev1")
        self.assertEqual(results[0]["odoo"], 0)
        self.assertEqual(results[0]["zeit"], 1.25)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 3)
    def test_136(self) -> None:
        weekago = datetime.date.today() - datetime.timedelta(days=10)
        nextweek = datetime.date.today() + datetime.timedelta(days=10)
        sunday = self.last_sunday()
        data = zeit.scan_data(f"""
        >> dev1 [Development]
        >> dev1 "project1"
        >> dev2 [Development]
        >> dev2 "project2"
        so **** WEEK {sunday.day}.{sunday.month}.-09.01.
        so 1:15 dev1 started
        so 0:15 dev2 started
        """.splitlines())
        logg.debug("data = %s", data)
        # sync.AFTER = (weekago).strftime("%Y-%m-%d")
        # sync.BEFORE = (nextweek).strftime("%Y-%m-%d")
        # sync.run("projects")
        results = sync.summary_per_topic(data)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["at topic"], "dev1")
        self.assertEqual(results[0]["odoo"], 0)
        self.assertEqual(results[0]["zeit"], 1.25)
        self.assertEqual(results[1]["at topic"], "dev2")
        self.assertEqual(results[1]["odoo"], 0)
        self.assertEqual(results[1]["zeit"], 0.25)
        self.assertEqual(len(results), 2)
        self.assertEqual(len(results[0]), 3)
    def test_137(self) -> None:
        weekago = datetime.date.today() - datetime.timedelta(days=10)
        nextweek = datetime.date.today() + datetime.timedelta(days=10)
        sunday = self.last_sunday()
        data = zeit.scan_data(f"""
        >> dev1 [Development]
        >> dev1 "project1"
        so **** WEEK {sunday.day}.{sunday.month}.-09.01.
        so 1:15 dev1 started
        """.splitlines())
        logg.debug("data = %s", data)
        # sync.AFTER = (weekago).strftime("%Y-%m-%d")
        # sync.BEFORE = (nextweek).strftime("%Y-%m-%d")
        # sync.run("projects")
        results = sync.summary_per_day(data)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["date"], sunday)
        self.assertEqual(results[0]["odoo"], 0)
        self.assertEqual(results[0]["zeit"], 1.25)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 3)
    def test_138(self) -> None:
        weekago = datetime.date.today() - datetime.timedelta(days=10)
        nextweek = datetime.date.today() + datetime.timedelta(days=10)
        sunday = self.last_sunday()
        data = zeit.scan_data(f"""
        >> dev1 [Development]
        >> dev1 "project1"
        >> dev2 [Development]
        >> dev2 "project2"
        so **** WEEK {sunday.day}.{sunday.month}.-09.01.
        so 1:15 dev1 started
        so 0:15 dev2 started
        """.splitlines())
        logg.debug("data = %s", data)
        # sync.AFTER = (weekago).strftime("%Y-%m-%d")
        # sync.BEFORE = (nextweek).strftime("%Y-%m-%d")
        # sync.run("projects")
        results = sync.summary_per_day(data)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["date"], sunday)
        self.assertEqual(results[0]["odoo"], 0)
        self.assertEqual(results[0]["zeit"], 1.5)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 3)
    def test_210(self) -> None:
        weekago = datetime.date.today() - datetime.timedelta(days=10)
        nextweek = datetime.date.today() + datetime.timedelta(days=10)
        sunday = self.last_sunday()
        data = zeit.scan_data(f"""
        >> dev1 [Development]
        >> dev1 "project1"
        so **** WEEK {sunday.day}.{sunday.month}.-09.01.
        so 1:15 dev1 started
        """.splitlines())
        logg.debug("data = %s", data)
        # sync.AFTER = (weekago).strftime("%Y-%m-%d")
        # sync.BEFORE = (nextweek).strftime("%Y-%m-%d")
        # sync.run("projects")
        results = sync.valid_per_days(data)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["date"], sunday)
        self.assertEqual(results[0]["odoo"], 0)
        self.assertEqual(results[0]["zeit"], 1.25)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 3)
    def test_211(self) -> None:
        weekago = datetime.date.today() - datetime.timedelta(days=10)
        nextweek = datetime.date.today() + datetime.timedelta(days=10)
        sunday = self.last_sunday()
        data = zeit.scan_data(f"""
        >> dev1 [Development]
        >> dev1 "project1"
        so **** WEEK {sunday.day}.{sunday.month}.-09.01.
        so 1:15 dev1 started
        """.splitlines())
        logg.debug("data = %s", data)
        # sync.AFTER = (weekago).strftime("%Y-%m-%d")
        # sync.BEFORE = (nextweek).strftime("%Y-%m-%d")
        # sync.run("projects")
        results = sync.update_per_days(data)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["act"], "NEW")
        self.assertEqual(results[0]["date"], sunday)
        self.assertEqual(results[0]["desc"], "dev1 started")
        self.assertEqual(results[0]["zeit"], 1.25)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 6)
    def test_212(self) -> None:
        weekago = datetime.date.today() - datetime.timedelta(days=10)
        nextweek = datetime.date.today() + datetime.timedelta(days=10)
        sunday = self.last_sunday()
        data = zeit.scan_data(f"""
        >> dev1 [Development]
        >> dev1 "project1"
        so **** WEEK {sunday.day}.{sunday.month}.-09.01.
        so 1:15 dev1 started
        """.splitlines())
        logg.debug("data = %s", data)
        # sync.AFTER = (weekago).strftime("%Y-%m-%d")
        # sync.BEFORE = (nextweek).strftime("%Y-%m-%d")
        # sync.run("projects")
        results = sync.check_in_sync(data)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["act"], "NEW")
        self.assertEqual(results[0]["date"], sunday)
        self.assertEqual(results[0]["desc"], "dev1 started")
        self.assertEqual(results[0]["zeit"], 1.25)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 6)
    def test_221(self) -> None:
        weekago = datetime.date.today() - datetime.timedelta(days=10)
        nextweek = datetime.date.today() + datetime.timedelta(days=10)
        sunday = self.last_sunday()
        data = zeit.scan_data(f"""
        >> dev1 [Development]
        >> dev1 "project1"
        so **** WEEK {sunday.day}.{sunday.month}.-09.01.
        so 1:15 dev1 started
        """.splitlines())
        logg.debug("data = %s", data)
        # sync.AFTER = (weekago).strftime("%Y-%m-%d")
        # sync.BEFORE = (nextweek).strftime("%Y-%m-%d")
        sync.UPDATE = True
        # sync.run("projects")
        results = sync.update_per_days(data)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["act"], "NEW")
        self.assertEqual(results[0]["date"], sunday)
        self.assertEqual(results[0]["desc"], "dev1 started")
        self.assertEqual(results[0]["zeit"], 1.25)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 6)
        # -->
        results = sync.summary_per_day(data)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["date"], sunday)
        self.assertEqual(results[0]["odoo"], 1.25)
        self.assertEqual(results[0]["zeit"], 1.25)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 3)
    def test_222(self) -> None:
        weekago = datetime.date.today() - datetime.timedelta(days=10)
        nextweek = datetime.date.today() + datetime.timedelta(days=10)
        sunday = self.last_sunday()
        data = zeit.scan_data(f"""
        >> dev1 [Development]
        >> dev1 "project1"
        so **** WEEK {sunday.day}.{sunday.month}.-09.01.
        so 1:15 dev1 started
        """.splitlines())
        logg.debug("data = %s", data)
        # sync.AFTER = (weekago).strftime("%Y-%m-%d")
        # sync.BEFORE = (nextweek).strftime("%Y-%m-%d")
        sync.UPDATE = True
        # sync.run("projects")
        results = sync.check_in_sync(data)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["act"], "NEW")
        self.assertEqual(results[0]["date"], sunday)
        self.assertEqual(results[0]["desc"], "dev1 started")
        self.assertEqual(results[0]["zeit"], 1.25)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 6)
        # -->
        results = sync.summary_per_day(data)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["date"], sunday)
        self.assertEqual(results[0]["odoo"], 1.25)
        self.assertEqual(results[0]["zeit"], 1.25)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 3)
    def test_231(self) -> None:
        """ split an existing value making an UPD + NEW #"""
        weekago = datetime.date.today() - datetime.timedelta(days=10)
        nextweek = datetime.date.today() + datetime.timedelta(days=10)
        sunday = self.last_sunday()
        data = zeit.scan_data(f"""
        >> dev1 [Development]
        >> dev1 "project1"
        so **** WEEK {sunday.day}.{sunday.month}.-09.01.
        so 1:15 dev1 started
        """.splitlines())
        logg.debug("data = %s", data)
        # sync.AFTER = (weekago).strftime("%Y-%m-%d")
        # sync.BEFORE = (nextweek).strftime("%Y-%m-%d")
        sync.UPDATE = True
        # sync.run("projects")
        results = sync.update_per_days(data)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["act"], "NEW")
        self.assertEqual(results[0]["date"], sunday)
        self.assertEqual(results[0]["desc"], "dev1 started")
        self.assertEqual(results[0]["zeit"], 1.25)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 6)
        # -->
        results = sync.summary_per_day(data)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["date"], sunday)
        self.assertEqual(results[0]["odoo"], 1.25)
        self.assertEqual(results[0]["zeit"], 1.25)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 3)
        # ****************************************
        data2 = zeit.scan_data(f"""
        >> dev1 [Development]
        >> dev1 "project1"
        >> dev2 [Development]
        >> dev2 "project2"
        so **** WEEK {sunday.day}.{sunday.month}.-09.01.
        so 1:00 dev1 started
        so 0:15 dev2 started
        """.splitlines())
        logg.debug("data = %s", data)
        results = sync.update_per_days(data2)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["act"], "UPD")
        self.assertEqual(results[0]["date"], sunday)
        self.assertEqual(results[0]["desc"], "dev1 started")
        self.assertEqual(results[0]["zeit"], 1.00)
        self.assertEqual(results[1]["act"], "NEW")
        self.assertEqual(results[1]["date"], sunday)
        self.assertEqual(results[1]["desc"], "dev2 started")
        self.assertEqual(results[1]["zeit"], 0.25)
        self.assertEqual(len(results), 2)
        self.assertEqual(len(results[0]), 6)
        # -->
        results = sync.summary_per_day(data)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["date"], sunday)
        self.assertEqual(results[0]["odoo"], 1.25)
        self.assertEqual(results[0]["zeit"], 1.25)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 3)
    def test_232(self) -> None:
        """ split an existing value making an UPD + NEW #"""
        weekago = datetime.date.today() - datetime.timedelta(days=10)
        nextweek = datetime.date.today() + datetime.timedelta(days=10)
        sunday = self.last_sunday()
        data = zeit.scan_data(f"""
        >> dev1 [Development]
        >> dev1 "project1"
        so **** WEEK {sunday.day}.{sunday.month}.-09.01.
        so 1:15 dev1 started
        """.splitlines())
        logg.debug("data = %s", data)
        # sync.AFTER = (weekago).strftime("%Y-%m-%d")
        # sync.BEFORE = (nextweek).strftime("%Y-%m-%d")
        sync.UPDATE = True
        # sync.run("projects")
        results = sync.check_in_sync(data)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["act"], "NEW")
        self.assertEqual(results[0]["date"], sunday)
        self.assertEqual(results[0]["desc"], "dev1 started")
        self.assertEqual(results[0]["zeit"], 1.25)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 6)
        # -->
        results = sync.summary_per_day(data)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["date"], sunday)
        self.assertEqual(results[0]["odoo"], 1.25)
        self.assertEqual(results[0]["zeit"], 1.25)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 3)
        # ****************************************
        data2 = zeit.scan_data(f"""
        >> dev1 [Development]
        >> dev1 "project1"
        >> dev2 [Development]
        >> dev2 "project2"
        so **** WEEK {sunday.day}.{sunday.month}.-09.01.
        so 1:00 dev1 started
        so 0:15 dev2 started
        """.splitlines())
        logg.debug("data = %s", data)
        results = sync.check_in_sync(data2)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["act"], "UPD")
        self.assertEqual(results[0]["date"], sunday)
        self.assertEqual(results[0]["desc"], "dev1 started")
        self.assertEqual(results[0]["zeit"], 1.00)
        self.assertEqual(results[1]["act"], "NEW")
        self.assertEqual(results[1]["date"], sunday)
        self.assertEqual(results[1]["desc"], "dev2 started")
        self.assertEqual(results[1]["zeit"], 0.25)
        self.assertEqual(len(results), 2)
        self.assertEqual(len(results[0]), 6)
        # -->
        results = sync.summary_per_day(data)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["date"], sunday)
        self.assertEqual(results[0]["odoo"], 1.25)
        self.assertEqual(results[0]["zeit"], 1.25)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 3)
    def test_241(self) -> None:
        """ add a NEW entry #"""
        weekago = datetime.date.today() - datetime.timedelta(days=10)
        nextweek = datetime.date.today() + datetime.timedelta(days=10)
        sunday = self.last_sunday()
        data = zeit.scan_data(f"""
        >> dev1 [Development]
        >> dev1 "project1"
        so **** WEEK {sunday.day}.{sunday.month}.-09.01.
        so 1:15 dev1 started
        """.splitlines())
        logg.debug("data = %s", data)
        # sync.AFTER = (weekago).strftime("%Y-%m-%d")
        # sync.BEFORE = (nextweek).strftime("%Y-%m-%d")
        sync.UPDATE = True
        # sync.run("projects")
        results = sync.update_per_days(data)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["act"], "NEW")
        self.assertEqual(results[0]["date"], sunday)
        self.assertEqual(results[0]["desc"], "dev1 started")
        self.assertEqual(results[0]["zeit"], 1.25)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 6)
        # -->
        results = sync.summary_per_day(data)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["date"], sunday)
        self.assertEqual(results[0]["odoo"], 1.25)
        self.assertEqual(results[0]["zeit"], 1.25)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 3)
        # ****************************************
        data2 = zeit.scan_data(f"""
        >> dev1 [Development]
        >> dev1 "project1"
        >> dev2 [Development]
        >> dev2 "project2"
        so **** WEEK {sunday.day}.{sunday.month}.-09.01.
        so 1:15 dev1 started
        so 0:15 dev2 started
        """.splitlines())
        logg.debug("data = %s", data)
        results = sync.update_per_days(data2)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["act"], "NEW")
        self.assertEqual(results[0]["date"], sunday)
        self.assertEqual(results[0]["desc"], "dev2 started")
        self.assertEqual(results[0]["zeit"], 0.25)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 6)
        # -->
        results = sync.summary_per_day(data2)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["date"], sunday)
        self.assertEqual(results[0]["odoo"], 1.50)
        self.assertEqual(results[0]["zeit"], 1.50)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 3)
    def test_242(self) -> None:
        """ add a NEW entry #"""
        weekago = datetime.date.today() - datetime.timedelta(days=10)
        nextweek = datetime.date.today() + datetime.timedelta(days=10)
        sunday = self.last_sunday()
        data = zeit.scan_data(f"""
        >> dev1 [Development]
        >> dev1 "project1"
        so **** WEEK {sunday.day}.{sunday.month}.-09.01.
        so 1:15 dev1 started
        """.splitlines())
        logg.debug("data = %s", data)
        # sync.AFTER = (weekago).strftime("%Y-%m-%d")
        # sync.BEFORE = (nextweek).strftime("%Y-%m-%d")
        sync.UPDATE = True
        # sync.run("projects")
        results = sync.check_in_sync(data)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["act"], "NEW")
        self.assertEqual(results[0]["date"], sunday)
        self.assertEqual(results[0]["desc"], "dev1 started")
        self.assertEqual(results[0]["zeit"], 1.25)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 6)
        # -->
        results = sync.summary_per_day(data)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["date"], sunday)
        self.assertEqual(results[0]["odoo"], 1.25)
        self.assertEqual(results[0]["zeit"], 1.25)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 3)
        # ****************************************
        data2 = zeit.scan_data(f"""
        >> dev1 [Development]
        >> dev1 "project1"
        >> dev2 [Development]
        >> dev2 "project2"
        so **** WEEK {sunday.day}.{sunday.month}.-09.01.
        so 1:15 dev1 started
        so 0:15 dev2 started
        """.splitlines())
        logg.debug("data = %s", data)
        results = sync.check_in_sync(data2)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["act"], "NEW")
        self.assertEqual(results[0]["date"], sunday)
        self.assertEqual(results[0]["desc"], "dev2 started")
        self.assertEqual(results[0]["zeit"], 0.25)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 6)
        # -->
        results = sync.summary_per_day(data2)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["date"], sunday)
        self.assertEqual(results[0]["odoo"], 1.50)
        self.assertEqual(results[0]["zeit"], 1.50)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 3)
    def test_251(self) -> None:
        """ add a NEW entry #"""
        weekago = datetime.date.today() - datetime.timedelta(days=10)
        nextweek = datetime.date.today() + datetime.timedelta(days=10)
        sunday = self.last_sunday()
        data = zeit.scan_data(f"""
        >> dev1 [Development]
        >> dev1 "projectX"
        so **** WEEK {sunday.day}.{sunday.month}.-09.01.
        so 1:15 dev1 started
        """.splitlines())
        logg.debug("data = %s", data)
        # sync.AFTER = (weekago).strftime("%Y-%m-%d")
        # sync.BEFORE = (nextweek).strftime("%Y-%m-%d")
        sync.UPDATE = True
        # sync.run("projects")
        results = sync.update_per_days(data)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["act"], "NEW")
        self.assertEqual(results[0]["date"], sunday)
        self.assertEqual(results[0]["desc"], "dev1 started")
        self.assertEqual(results[0]["zeit"], 1.25)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 6)
        # -->
        results = sync.summary_per_day(data)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["date"], sunday)
        self.assertEqual(results[0]["odoo"], 1.25)
        self.assertEqual(results[0]["zeit"], 1.25)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 3)
        # ****************************************
        data2 = zeit.scan_data(f"""
        >> dev1 [Development]
        >> dev1 "projectX"
        >> dev2 [Development]
        >> dev2 "projectX"
        so **** WEEK {sunday.day}.{sunday.month}.-09.01.
        so 1:15 dev1 started
        so 0:15 dev2 started
        """.splitlines())
        logg.debug("data = %s", data)
        results = sync.update_per_days(data2)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["act"], "NEW")
        self.assertEqual(results[0]["date"], sunday)
        self.assertEqual(results[0]["desc"], "dev2 started")
        self.assertEqual(results[0]["zeit"], 0.25)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 6)
        # -->
        results = sync.summary_per_day(data2)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["date"], sunday)
        self.assertEqual(results[0]["odoo"], 1.50)
        self.assertEqual(results[0]["zeit"], 1.50)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 3)
    def test_252(self) -> None:
        """ add a NEW entry #"""
        weekago = datetime.date.today() - datetime.timedelta(days=10)
        nextweek = datetime.date.today() + datetime.timedelta(days=10)
        sunday = self.last_sunday()
        data = zeit.scan_data(f"""
        >> dev1 [Development]
        >> dev1 "projectX"
        so **** WEEK {sunday.day}.{sunday.month}.-09.01.
        so 1:15 dev1 started
        """.splitlines())
        logg.debug("data = %s", data)
        # sync.AFTER = (weekago).strftime("%Y-%m-%d")
        # sync.BEFORE = (nextweek).strftime("%Y-%m-%d")
        sync.UPDATE = True
        # sync.run("projects")
        results = sync.check_in_sync(data)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["act"], "NEW")
        self.assertEqual(results[0]["date"], sunday)
        self.assertEqual(results[0]["desc"], "dev1 started")
        self.assertEqual(results[0]["zeit"], 1.25)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 6)
        # -->
        results = sync.summary_per_day(data)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["date"], sunday)
        self.assertEqual(results[0]["odoo"], 1.25)
        self.assertEqual(results[0]["zeit"], 1.25)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 3)
        # ****************************************
        data2 = zeit.scan_data(f"""
        >> dev1 [Development]
        >> dev1 "projectX"
        >> dev2 [Development]
        >> dev2 "projectX"
        so **** WEEK {sunday.day}.{sunday.month}.-09.01.
        so 1:15 dev1 started
        so 0:15 dev2 started
        """.splitlines())
        logg.debug("data = %s", data)
        results = sync.check_in_sync(data2)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["act"], "UPD")
        self.assertEqual(results[0]["date"], sunday)
        self.assertEqual(results[0]["desc"], "dev2 started")
        self.assertEqual(results[0]["zeit"], 0.25)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 6)
        # -->
        results = sync.summary_per_day(data2)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["date"], sunday)
        self.assertEqual(results[0]["odoo"], 0.25)  # !!!!!!!!!!!!!
        self.assertEqual(results[0]["zeit"], 1.50)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 3)
    def test_301(self) -> None:
        """ add a NEW entry and UPD its time #"""
        weekago = datetime.date.today() - datetime.timedelta(days=10)
        nextweek = datetime.date.today() + datetime.timedelta(days=10)
        sunday = self.last_sunday()
        data = zeit.scan_data(f"""
        >> dev1 [Development]
        >> dev1 "projectX"
        so **** WEEK {sunday.day}.{sunday.month}.-09.01.
        so 1:15 dev1 started
        """.splitlines())
        logg.debug("data = %s", data)
        # sync.AFTER = (weekago).strftime("%Y-%m-%d")
        # sync.BEFORE = (nextweek).strftime("%Y-%m-%d")
        sync.UPDATE = True
        # sync.run("projects")
        results = sync.update_per_days(data)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["act"], "NEW")
        self.assertEqual(results[0]["date"], sunday)
        self.assertEqual(results[0]["desc"], "dev1 started")
        self.assertEqual(results[0]["zeit"], 1.25)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 6)
        # -->
        results = sync.summary_per_day(data)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["date"], sunday)
        self.assertEqual(results[0]["odoo"], 1.25)
        self.assertEqual(results[0]["zeit"], 1.25)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 3)
        # --->
        results = sync.summary_per_project_task(data)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["at proj"], "Development")
        self.assertEqual(results[0]["at task"], "projectX")
        self.assertEqual(results[0]["odoo"], 1.25)
        self.assertEqual(results[0]["zeit"], 1.25)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 4)
        # ****************************************
        data2 = zeit.scan_data(f"""
        >> dev1 [Development]
        >> dev1 "projectX"
        >> dev2 [Development]
        >> dev2 "projectX"
        so **** WEEK {sunday.day}.{sunday.month}.-09.01.
        so 1:15 dev1 started
        so 0:15 dev2 started
        """.splitlines())
        logg.debug("data = %s", data)
        results = sync.update_per_days(data2)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["act"], "NEW")
        self.assertEqual(results[0]["date"], sunday)
        self.assertEqual(results[0]["desc"], "dev2 started")
        self.assertEqual(results[0]["zeit"], 0.25)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 6)
        # -->
        results = sync.summary_per_day(data2)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["date"], sunday)
        self.assertEqual(results[0]["odoo"], 1.50)
        self.assertEqual(results[0]["zeit"], 1.50)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 3)
        # --->
        results = sync.summary_per_project_task(data2)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["at proj"], "Development")
        self.assertEqual(results[0]["at task"], "projectX")
        self.assertEqual(results[0]["odoo"], 1.50)
        self.assertEqual(results[0]["zeit"], 1.50)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 4)
        # ****************************************
        data3 = zeit.scan_data(f"""
        >> dev1 [Development]
        >> dev1 "projectX"
        >> dev2 [Development]
        >> dev2 "projectX"
        so **** WEEK {sunday.day}.{sunday.month}.-09.01.
        so 1:15 dev1 started
        so 0:30 dev2 started
        """.splitlines())
        logg.debug("data = %s", data)
        results = sync.update_per_days(data3)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["act"], "UPD")
        self.assertEqual(results[0]["date"], sunday)
        self.assertEqual(results[0]["desc"], "dev2 started")
        self.assertEqual(results[0]["zeit"], 0.50)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 6)
        # -->
        results = sync.summary_per_day(data3)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["date"], sunday)
        self.assertEqual(results[0]["odoo"], 1.75)
        self.assertEqual(results[0]["zeit"], 1.75)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 3)
        # --->
        results = sync.summary_per_project_task(data3)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["at proj"], "Development")
        self.assertEqual(results[0]["at task"], "projectX")
        self.assertEqual(results[0]["odoo"], 1.75)
        self.assertEqual(results[0]["zeit"], 1.75)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 4)
    def test_311(self) -> None:
        """ add a NEW entry and UPD its task #"""
        weekago = datetime.date.today() - datetime.timedelta(days=10)
        nextweek = datetime.date.today() + datetime.timedelta(days=10)
        sunday = self.last_sunday()
        data = zeit.scan_data(f"""
        >> dev1 [Development]
        >> dev1 "projectX"
        so **** WEEK {sunday.day}.{sunday.month}.-09.01.
        so 1:15 dev1 started
        """.splitlines())
        logg.debug("data = %s", data)
        # sync.AFTER = (weekago).strftime("%Y-%m-%d")
        # sync.BEFORE = (nextweek).strftime("%Y-%m-%d")
        sync.UPDATE = True
        # sync.run("projects")
        results = sync.update_per_days(data)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["act"], "NEW")
        self.assertEqual(results[0]["date"], sunday)
        self.assertEqual(results[0]["desc"], "dev1 started")
        self.assertEqual(results[0]["zeit"], 1.25)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 6)
        # -->
        results = sync.summary_per_day(data)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["date"], sunday)
        self.assertEqual(results[0]["odoo"], 1.25)
        self.assertEqual(results[0]["zeit"], 1.25)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 3)
        # --->
        results = sync.summary_per_project_task(data)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["at proj"], "Development")
        self.assertEqual(results[0]["at task"], "projectX")
        self.assertEqual(results[0]["odoo"], 1.25)
        self.assertEqual(results[0]["zeit"], 1.25)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 4)
        # ****************************************
        data2 = zeit.scan_data(f"""
        >> dev1 [Development]
        >> dev1 "projectX"
        >> dev2 [Development]
        >> dev2 "projectX"
        so **** WEEK {sunday.day}.{sunday.month}.-09.01.
        so 1:15 dev1 started
        so 0:15 dev2 started
        """.splitlines())
        logg.debug("data = %s", data)
        results = sync.update_per_days(data2)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["act"], "NEW")
        self.assertEqual(results[0]["date"], sunday)
        self.assertEqual(results[0]["desc"], "dev2 started")
        self.assertEqual(results[0]["zeit"], 0.25)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 6)
        # -->
        results = sync.summary_per_day(data2)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["date"], sunday)
        self.assertEqual(results[0]["odoo"], 1.50)
        self.assertEqual(results[0]["zeit"], 1.50)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 3)
        # --->
        results = sync.summary_per_project_task(data2)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["at proj"], "Development")
        self.assertEqual(results[0]["at task"], "projectX")
        self.assertEqual(results[0]["odoo"], 1.50)
        self.assertEqual(results[0]["zeit"], 1.50)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 4)
        # ****************************************
        data3 = zeit.scan_data(f"""
        >> dev1 [Development]
        >> dev1 "projectX"
        >> dev2 [Development]
        >> dev2 "projectY"
        so **** WEEK {sunday.day}.{sunday.month}.-09.01.
        so 1:15 dev1 started
        so 0:30 dev2 started
        """.splitlines())
        logg.debug("data = %s", data)
        results = sync.update_per_days(data3)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["act"], "UPD")
        self.assertEqual(results[0]["date"], sunday)
        self.assertEqual(results[0]["desc"], "dev2 started")
        self.assertEqual(results[0]["zeit"], 0.50)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 6)
        # -->
        results = sync.summary_per_day(data3)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["date"], sunday)
        self.assertEqual(results[0]["odoo"], 1.75)
        self.assertEqual(results[0]["zeit"], 1.75)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 3)
        # --->
        results = sync.summary_per_project_task(data3)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["at proj"], "Development")
        self.assertEqual(results[0]["at task"], "projectX")
        self.assertEqual(results[0]["odoo"], 1.25)
        self.assertEqual(results[0]["zeit"], 1.25)
        self.assertEqual(results[1]["at proj"], "Development")
        self.assertEqual(results[1]["at task"], "projectY")
        self.assertEqual(results[1]["odoo"], 0.50)
        self.assertEqual(results[1]["zeit"], 0.50)
        self.assertEqual(len(results), 2)
        self.assertEqual(len(results[0]), 4)


if __name__ == "__main__":
    # unittest.main()
    from optparse import OptionParser
    cmdline = OptionParser("%prog [t_]test...")
    cmdline.add_option("-v", "--verbose", action="count", default=0, help="more verbose logging")
    cmdline.add_option("-^", "--quiet", action="count", default=0, help="less verbose logging")
    cmdline.add_option("--failfast", action="store_true", default=False,
                       help="Stop the test run on the first error or failure. [%default]")
    cmdline.add_option("--xmlresults", metavar="FILE", default=None,
                       help="capture results as a junit xml file [%default]")
    opt, args = cmdline.parse_args()
    logging.basicConfig(level=max(0, logging.WARNING - 10 * opt.verbose + 10 * opt.quiet))
    sync.logg.setLevel(max(0, logging.INFO - 10 * opt.verbose))
    if not args:
        args = ["test_*"]
    suite = unittest.TestSuite()
    for arg in args:
        if len(arg) > 2 and arg[0].isalpha() and arg[1] == "_":
            arg = "test_" + arg[2:]
        for classname in sorted(globals()):
            if not classname.endswith("Test"):
                continue
            testclass = globals()[classname]
            for method in sorted(dir(testclass)):
                if "*" not in arg: arg += "*"
                if arg.startswith("_"): arg = arg[1:]
                if fnmatch(method, arg):
                    suite.addTest(testclass(method))
    # running
    xmlresults = None
    if opt.xmlresults:
        if os.path.exists(opt.xmlresults):
            os.remove(opt.xmlresults)
        xmlresults = open(opt.xmlresults, "wb")
    if xmlresults:
        import xmlrunner  # type: ignore[import]
        Runner = xmlrunner.XMLTestRunner
        result = Runner(xmlresults).run(suite)
        logg.info(" XML reports written to %s", opt.xmlresults)
    else:
        Runner = unittest.TextTestRunner
        result = Runner(verbosity=opt.verbose, failfast=opt.failfast).run(suite)
    if not result.wasSuccessful():
        sys.exit(1)
