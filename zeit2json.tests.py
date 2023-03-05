#! /usr/bin/env python3

__copyright__ = "(C) 2017-2023 Guido Draheim, licensed under the Apache License 2.0"""
__version__ = "1.0.2097"

import zeit2json as zeit
from typing import Optional

import os
import sys
import unittest
import tempfile
import os.path as path
from fnmatch import fnmatchcase as fnmatch
from datetime import date as Date
from datetime import timedelta as Delta

import netrc

import logging
logg = logging.getLogger("TEST")


class zeit2jsonTest(unittest.TestCase):
    def last_sunday(self) -> Date:
        today = Date.today()
        for earlier in range(8):
            day = today - Delta(days=earlier)
            logg.debug("weekday %s earlier %s", day.isoweekday(), earlier)
            if day.isoweekday() in [0, 7]:
                return day
        logg.error("could not find sunday before %s", today)
        return today
    def test_101(self) -> None:
        on_day = Date(2022, 1, 1)
        data = zeit.scan_data("""
        >> dev1 [Development]
        >> dev1 "project1"
        so **** WEEK 02.01.2022-09.01.
        so 1:15 dev1 started
        """.splitlines(), on_day)
        logg.debug("data = %s", data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["Date"], Date(2022, 1, 2))
        self.assertEqual(data[0]["Project"], "Development")
        self.assertEqual(data[0]["Task"], "project1")
        self.assertEqual(data[0]["Topic"], "dev1")
    def test_111(self) -> None:
        sunday = self.last_sunday()
        data = zeit.scan_data(f"""
        >> dev1 [Development]
        >> dev1 "project1"
        so **** WEEK {sunday.day}.{sunday.month}.-09.01.
        so 1:15 dev1 started
        """.splitlines())
        logg.debug("data = %s", data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["Date"], sunday)
        self.assertEqual(data[0]["Project"], "Development")
        self.assertEqual(data[0]["Task"], "project1")
        self.assertEqual(data[0]["Topic"], "dev1")
    def test_112(self) -> None:
        sunday = self.last_sunday()
        monday = sunday + Delta(days=1)
        data = zeit.scan_data(f"""
        >> dev1 [Development]
        >> dev1 "project1"
        so **** WEEK {sunday.day}.{sunday.month}.-09.01.
        mo 1:15 dev1 started
        """.splitlines())
        logg.debug("data = %s", data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["Date"], monday)
        self.assertEqual(data[0]["Project"], "Development")
        self.assertEqual(data[0]["Task"], "project1")
        self.assertEqual(data[0]["Topic"], "dev1")
    def test_113(self) -> None:
        sunday = self.last_sunday()
        tue = sunday + Delta(days=2)
        data = zeit.scan_data(f"""
        >> dev1 [Development]
        >> dev1 "project1"
        so **** WEEK {sunday.day}.{sunday.month}.-09.01.
        di 1:15 dev1 started
        """.splitlines())
        logg.debug("data = %s", data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["Date"], tue)
        self.assertEqual(data[0]["Project"], "Development")
        self.assertEqual(data[0]["Task"], "project1")
        self.assertEqual(data[0]["Topic"], "dev1")
    def test_114(self) -> None:
        sunday = self.last_sunday()
        wed = sunday + Delta(days=3)
        data = zeit.scan_data(f"""
        >> dev1 [Development]
        >> dev1 "project1"
        so **** WEEK {sunday.day}.{sunday.month}.-09.01.
        mi 1:15 dev1 started
        """.splitlines())
        logg.debug("data = %s", data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["Date"], wed)
        self.assertEqual(data[0]["Project"], "Development")
        self.assertEqual(data[0]["Task"], "project1")
        self.assertEqual(data[0]["Topic"], "dev1")
    def test_115(self) -> None:
        sunday = self.last_sunday()
        thu = sunday + Delta(days=4)
        data = zeit.scan_data(f"""
        >> dev1 [Development]
        >> dev1 "project1"
        so **** WEEK {sunday.day}.{sunday.month}.-09.01.
        do 1:15 dev1 started
        """.splitlines())
        logg.debug("data = %s", data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["Date"], thu)
        self.assertEqual(data[0]["Project"], "Development")
        self.assertEqual(data[0]["Task"], "project1")
        self.assertEqual(data[0]["Topic"], "dev1")
    def test_116(self) -> None:
        sunday = self.last_sunday()
        fri = sunday + Delta(days=5)
        data = zeit.scan_data(f"""
        >> dev1 [Development]
        >> dev1 "project1"
        so **** WEEK {sunday.day}.{sunday.month}.-09.01.
        fr 1:15 dev1 started
        """.splitlines())
        logg.debug("data = %s", data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["Date"], fri)
        self.assertEqual(data[0]["Project"], "Development")
        self.assertEqual(data[0]["Task"], "project1")
        self.assertEqual(data[0]["Topic"], "dev1")
    def test_117(self) -> None:
        sunday = self.last_sunday()
        sat = sunday + Delta(days=6)
        data = zeit.scan_data(f"""
        >> dev1 [Development]
        >> dev1 "project1"
        so **** WEEK {sunday.day}.{sunday.month}.-09.01.
        sa 1:15 dev1 started
        """.splitlines())
        logg.debug("data = %s", data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["Date"], sat)
        self.assertEqual(data[0]["Project"], "Development")
        self.assertEqual(data[0]["Task"], "project1")
        self.assertEqual(data[0]["Topic"], "dev1")
    @unittest.expectedFailure
    def test_121(self) -> None:
        monday = self.last_sunday() + Delta(days=1)
        data = zeit.scan_data(f"""
        >> dev1 [Development]
        >> dev1 "project1"
        mo **** WEEK {monday.day}.{monday.month}.-09.01.
        mo 1:15 dev1 started""".splitlines())
        logg.debug("data = %s", data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["Date"], monday)
        self.assertEqual(data[0]["Project"], "Development")
        self.assertEqual(data[0]["Task"], "project1")
        self.assertEqual(data[0]["Topic"], "dev1")
        self.assertEqual(len(data), 1)

if __name__ == "__main__":
    # unittest.main()
    from optparse import OptionParser
    cmdline = OptionParser("%prog [z_]test...")
    cmdline.add_option("-v", "--verbose", action="count", default=0)
    cmdline.add_option("--xmlresults", metavar="FILE", default=None,
                       help="capture results as a junit xml file [%default]")
    opt, args = cmdline.parse_args()
    logging.basicConfig(level=max(0, logging.WARNING - 10 * opt.verbose))
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
