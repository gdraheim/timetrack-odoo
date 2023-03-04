#! /usr/bin/env python3

__copyright__ = "(C) Guido Draheim, licensed under the Apache License 2.0"""
__version__ = "0.9.2096"

import tabtotext
import odoo_rest_mockup
import odoo2data as sync
from typing import Optional
from tabtotext import JSONList
import datetime

import os
import sys
import unittest
import tempfile
import os.path as path
from fnmatch import fnmatchcase as fnmatch
import netrc

import logging
logg = logging.getLogger("TEST")

sync.odoo_api = odoo_rest_mockup

class odoo2dataTest(unittest.TestCase):
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
    def test_101(self) -> None:
        weekago = datetime.date.today() - datetime.timedelta(days=10)
        nextweek = datetime.date.today() + datetime.timedelta(days=10)
        sunday = self.last_sunday()
        data: JSONList = []
        data += [{"proj_name": "Development", "task_name": "project1", "entry_date": sunday, "entry_size": 1.25}]
        results = sync.summary_per_project_task(data)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["at proj"], "Development")
        self.assertEqual(results[0]["at task"], "project1")
        self.assertEqual(results[0]["odoo"], 1.25)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 3)
    def test_102(self) -> None:
        weekago = datetime.date.today() - datetime.timedelta(days=10)
        nextweek = datetime.date.today() + datetime.timedelta(days=10)
        sunday = self.last_sunday()
        data: JSONList = []
        data += [{"proj_name": "Development", "task_name": "project1", "entry_date": sunday, "entry_size": 1.25}]
        data += [{"proj_name": "Development", "task_name": "project2", "entry_date": sunday, "entry_size": 0.25}]
        logg.debug("data = %s", data)
        results = sync.summary_per_project_task(data)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["at proj"], "Development")
        self.assertEqual(results[0]["at task"], "project1")
        self.assertEqual(results[0]["odoo"], 1.25)
        self.assertEqual(results[1]["at proj"], "Development")
        self.assertEqual(results[1]["at task"], "project2")
        self.assertEqual(results[1]["odoo"], 0.25)
        self.assertEqual(len(results), 2)
        self.assertEqual(len(results[0]), 3)
    def test_103(self) -> None:
        weekago = datetime.date.today() - datetime.timedelta(days=10)
        nextweek = datetime.date.today() + datetime.timedelta(days=10)
        sunday = self.last_sunday()
        data: JSONList = []
        data += [{"proj_name": "Development", "task_name": "project1", "entry_date": sunday, "entry_size": 1.25}]
        logg.debug("data = %s", data)
        results = sync.summary_per_project(data)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["at proj"], "Development")
        self.assertNotIn("at task", results[0])
        self.assertEqual(results[0]["odoo"], 1.25)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 2)
    def test_104(self) -> None:
        weekago = datetime.date.today() - datetime.timedelta(days=10)
        nextweek = datetime.date.today() + datetime.timedelta(days=10)
        sunday = self.last_sunday()
        data: JSONList = []
        data += [{"proj_name": "Development", "task_name": "project1", "entry_date": sunday, "entry_size": 1.25}]
        data += [{"proj_name": "Development", "task_name": "project2", "entry_date": sunday, "entry_size": 0.25}]
        logg.debug("data = %s", data)
        results = sync.summary_per_project(data)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["at proj"], "Development")
        self.assertNotIn("at task", results[0])
        self.assertEqual(results[0]["odoo"], 1.50)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 2)
    def test_105(self) -> None:
        weekago = datetime.date.today() - datetime.timedelta(days=10)
        nextweek = datetime.date.today() + datetime.timedelta(days=10)
        sunday = self.last_sunday()
        data: JSONList = []
        data += [{"proj_name": "Development", "task_name": "project1", "entry_date": sunday, "entry_size": 1.25}]
        data[0]["entry_desc"] = "dev1 started"
        logg.debug("data = %s", data)
        results = sync.summary_per_topic(data)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["at topic"], "dev1")
        self.assertEqual(results[0]["odoo"], 1.25)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 2)
    def test_106(self) -> None:
        weekago = datetime.date.today() - datetime.timedelta(days=10)
        nextweek = datetime.date.today() + datetime.timedelta(days=10)
        sunday = self.last_sunday()
        data: JSONList = []
        data += [{"proj_name": "Development", "task_name": "project1", "entry_date": sunday, "entry_size": 1.25}]
        data += [{"proj_name": "Development", "task_name": "project2", "entry_date": sunday, "entry_size": 0.25}]
        data[0]["entry_desc"] = "dev1 started"
        data[1]["entry_desc"] = "dev2 started"
        logg.debug("data = %s", data)
        results = sync.summary_per_topic(data)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["at topic"], "dev1")
        self.assertEqual(results[0]["odoo"], 1.25)
        self.assertEqual(results[1]["at topic"], "dev2")
        self.assertEqual(results[1]["odoo"], 0.25)
        self.assertEqual(len(results), 2)
        self.assertEqual(len(results[0]), 2)
    def test_107(self) -> None:
        weekago = datetime.date.today() - datetime.timedelta(days=10)
        nextweek = datetime.date.today() + datetime.timedelta(days=10)
        sunday = self.last_sunday()
        data: JSONList = []
        data += [{"proj_name": "Development", "task_name": "project1", "entry_date": sunday, "entry_size": 1.25}]
        logg.debug("data = %s", data)
        results = sync.summary_per_day(data)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["date"], sunday)
        self.assertEqual(results[0]["odoo"], 1.25)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 3)
    def test_108(self) -> None:
        weekago = datetime.date.today() - datetime.timedelta(days=10)
        nextweek = datetime.date.today() + datetime.timedelta(days=10)
        sunday = self.last_sunday()
        data: JSONList = []
        data += [{"proj_name": "Development", "task_name": "project1", "entry_date": sunday, "entry_size": 1.25}]
        data += [{"proj_name": "Development", "task_name": "project2", "entry_date": sunday, "entry_size": 0.25}]
        logg.debug("data = %s", data)
        results = sync.summary_per_day(data)
        report = tabtotext.tabToGFM(results)
        logg.info("result:\n%s", report)
        self.assertEqual(results[0]["date"], sunday)
        self.assertEqual(results[0]["odoo"], 1.5)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 3)


if __name__ == "__main__":
    # unittest.main()
    from optparse import OptionParser
    cmdline = OptionParser("%prog [t_]test...")
    cmdline.add_option("-v", "--verbose", action="count", default=0)
    cmdline.add_option("--xmlresults", metavar="FILE", default=None,
                       help="capture results as a junit xml file [%default]")
    opt, args = cmdline.parse_args()
    logging.basicConfig(level=max(0, logging.WARNING - 10 * opt.verbose))
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
        logg.info("xml results into %s", opt.xmlresults)
    if xmlresults:
        import xmlrunner  # type: ignore[import]
        Runner = xmlrunner.XMLTestRunner
        result = Runner(xmlresults).run(suite)
    else:
        Runner = unittest.TextTestRunner
        result = Runner(verbosity=opt.verbose).run(suite)
    if not result.wasSuccessful():
        sys.exit(1)
