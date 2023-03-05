#! /usr/bin/env python3

__copyright__ = "(C) 2022-2023 Guido Draheim, licensed under the Apache License 2.0"""
__version__ = "1.0.2096"

import tabtotext
import jira_rest_mockup
import zeit2jira as sync
from typing import Optional
from tabtotext import JSONList, JSONDict
from dayrange import dayrange
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

sync.jira_api = jira_rest_mockup

Day = datetime.date
USER = "myself"

Q = "Quantity"
D = "Description"

Day1212 = Day(2020, 12, 12)
ticket1: JSONDict = {"Ticket": "SAND-4", "Date": Day1212, "Topic": "local", Q: 1., D: "local ticket1"}
ticket2: JSONDict = {"Ticket": "BUGS-5", "Date": Day1212, "Topic": "local", Q: 2., D: "local ticket2"}

class zeit2jiraTest(unittest.TestCase):
    def setUp(self) -> None:
        sync.jira_api.reset()
    def test_100(self) -> None:
        sync.DAYS = dayrange("2020-12-10", "2020-12-15")
        have = [ticket1, ticket2]
        found = sync.summary_per_project(have)
        logg.info("found %s", found)
        want = [{'at proj': 'SAND', 'jira': 2, 'zeit': 1.0},
                {'at proj': 'BUGS', 'jira': 3, 'zeit': 2.0}]
        self.assertEqual(want, found)
    def test_200(self) -> None:
        sync.DAYS = dayrange("2020-12-10", "2020-12-15")
        have = [ticket1, ticket2]
        found = sync.summary_per_topic(have)
        logg.info("found %s", found)
        want = [{'at topic': 'local', 'jira': 5, 'zeit': 3.0}]
        self.assertEqual(want, found)
    def test_500(self) -> None:
        sync.DAYS = dayrange("2020-12-10", "2020-12-15")
        have = [ticket1, ticket2]
        found = sync.update_per_days(have)
        logg.info("found %s", found)
        want = [{'act': 'UPD', 'at task': 'SAND-4', 'date': Day1212, 'desc': 'local ticket1', 'zeit': 1.0},
                {'act': 'UPD', 'at task': 'BUGS-5', 'date': Day1212, 'desc': 'local ticket2', 'zeit': 2.0}]
        self.assertEqual(want, found)

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
    if xmlresults:
        import xmlrunner  # type: ignore[import]
        Runner = xmlrunner.XMLTestRunner
        result = Runner(xmlresults).run(suite)
        logg.info(" XML reports written to %s", opt.xmlresults)
    else:
        Runner = unittest.TextTestRunner
        result = Runner(verbosity=opt.verbose).run(suite)
    if not result.wasSuccessful():
        sys.exit(1)
