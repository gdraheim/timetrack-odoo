#! /usr/bin/python3

import dayrange as zeit
from typing import Optional

import os
import sys
import unittest
import tempfile
import os.path as path
from fnmatch import fnmatchcase as fnmatch
import subprocess
from datetime import date as Day
from datetime import timedelta as Delta

import netrc

import logging
logg = logging.getLogger("TEST")


class dayrangeTest(unittest.TestCase):
    def last_sunday(self) -> Day:
        today = Day.today()
        for earlier in range(8):
            day = today - Delta(days=earlier)
            logg.debug("weekday %s earlier %s", day.isoweekday(), earlier)
            if day.isoweekday() in [0, 7]:
                return day
        logg.error("could not find sunday before %s", today)
        return today
    def test_011(self) -> None:
        day = zeit.date_isoformat("2019-12-11")
        logg.info("day = %s", day)
        self.assertEqual(day, Day(2019, 12, 11))
    def test_012(self) -> None:
        day = zeit.date_isoformat("2019-12-99")
        logg.info("day = %s", day)
        self.assertEqual(day, Day(2019, 12, 31))
    def test_013(self) -> None:
        day = zeit.date_isoformat("2019-11-99")
        logg.info("day = %s", day)
        self.assertEqual(day, Day(2019, 11, 30))
    def test_014(self) -> None:
        day = zeit.date_isoformat("2019-02-99")
        logg.info("day = %s", day)
        self.assertEqual(day, Day(2019, 2, 28))
    def test_015(self) -> None:
        day = zeit.date_isoformat("2020-02-99")
        logg.info("day = %s", day)
        self.assertEqual(day, Day(2020, 2, 29))
    def test_021(self) -> None:
        day = zeit.date_dotformat("11.12.2019")
        logg.info("day = %s", day)
        self.assertEqual(day, Day(2019, 12, 11))
    def test_022(self) -> None:
        day = zeit.date_dotformat("99.12.2019")
        logg.info("day = %s", day)
        self.assertEqual(day, Day(2019, 12, 31))
    def test_023(self) -> None:
        day = zeit.date_dotformat("99.11.2019")
        logg.info("day = %s", day)
        self.assertEqual(day, Day(2019, 11, 30))
    def test_024(self) -> None:
        day = zeit.date_dotformat("99.02.2019")
        logg.info("day = %s", day)
        self.assertEqual(day, Day(2019, 2, 28))
    def test_025(self) -> None:
        day = zeit.date_dotformat("99.02.2020")
        logg.info("day = %s", day)
        self.assertEqual(day, Day(2020, 2, 29))
    def test_041(self) -> None:
        day = zeit.get_date("2019-12-11")
        logg.info("day = %s", day)
        self.assertEqual(day, Day(2019, 12, 11))
    def test_042(self) -> None:
        day = zeit.get_date("2019-12-99")
        logg.info("day = %s", day)
        self.assertEqual(day, Day(2019, 12, 31))
    def test_043(self) -> None:
        day = zeit.get_date("2019-11-99")
        logg.info("day = %s", day)
        self.assertEqual(day, Day(2019, 11, 30))
    def test_044(self) -> None:
        day = zeit.get_date("2019-02-99")
        logg.info("day = %s", day)
        self.assertEqual(day, Day(2019, 2, 28))
    def test_045(self) -> None:
        day = zeit.get_date("2020-02-99")
        logg.info("day = %s", day)
        self.assertEqual(day, Day(2020, 2, 29))
    def test_051(self) -> None:
        day = zeit.get_date("11.12.2019")
        logg.info("day = %s", day)
        self.assertEqual(day, Day(2019, 12, 11))
    def test_052(self) -> None:
        day = zeit.get_date("99.12.2019")
        logg.info("day = %s", day)
        self.assertEqual(day, Day(2019, 12, 31))
    def test_053(self) -> None:
        day = zeit.get_date("99.11.2019")
        logg.info("day = %s", day)
        self.assertEqual(day, Day(2019, 11, 30))
    def test_054(self) -> None:
        day = zeit.get_date("99.02.2019")
        logg.info("day = %s", day)
        self.assertEqual(day, Day(2019, 2, 28))
    def test_055(self) -> None:
        day = zeit.get_date("99.02.2020")
        logg.info("day = %s", day)
        self.assertEqual(day, Day(2020, 2, 29))
    def test_501(self) -> None:
        days = zeit.dayrange("2020-02-01", "2020-02-29")
        self.assertEqual(days.after, Day(2020, 2, 1))
        self.assertEqual(days.before, Day(2020, 2, 29))
        self.assertEqual(len(days), 29)
    def test_502(self) -> None:
        days = zeit.dayrange("2020-02-01", "2020-02-02")
        self.assertEqual(days.after, Day(2020, 2, 1))
        self.assertEqual(days.before, Day(2020, 2, 2))
        self.assertEqual(len(days), 2)
        logg.info("days = %s", days)
        values = [day for day in days]
        logg.info("values %s", values)
        self.assertEqual(len(values), 2)
        daynum = [val.day for val in values]
        self.assertEqual(daynum, [1, 2])
        months = [val.month for val in values]
        self.assertEqual(months, [2, 2])
    def test_503(self) -> None:
        days = zeit.dayrange("2020-02-01", "2020-02-29")
        self.assertEqual(days.after, Day(2020, 2, 1))
        self.assertEqual(days.before, Day(2020, 2, 29))
        self.assertEqual(len(days), 29)
        day2 = zeit.dayrange("2020-02-01", "2020-02-02")
        self.assertEqual(day2.after, Day(2020, 2, 1))
        self.assertEqual(day2.before, Day(2020, 2, 2))
        self.assertEqual(len(day2), 2)
        self.assertLessEqual(day2, days)
        self.assertGreaterEqual(days, day2)
        self.assertLess(day2, days)
        self.assertGreater(days, day2)

if __name__ == "__main__":
    # unittest.main()
    from optparse import OptionParser
    cmdline = OptionParser("%prog [z_]test [d_]test...")
    cmdline.add_option("-v", "--verbose", action="count", default=0)
    opt, args = cmdline.parse_args()
    logging.basicConfig(level=max(0, logging.WARNING - 10 * opt.verbose))
    if not args:
        args = ["z_*"]
    suite = unittest.TestSuite()
    for arg in args:
        if arg.startswith("z_"):
            arg = "test_" + arg[2:]
        if arg.startswith("d_"):
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
    Runner = unittest.TextTestRunner
    result = Runner(verbosity=opt.verbose).run(suite)
    if not result.wasSuccessful():
        sys.exit(1)
