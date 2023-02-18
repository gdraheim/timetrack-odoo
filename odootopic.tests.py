#! /usr/bin/python3

import odootopic as topics
from typing import Optional

import os
import sys
import unittest
import tempfile
import os.path as path
from fnmatch import fnmatchcase as fnmatch
import subprocess
from datetime import date as Date
from datetime import timedelta as Delta

import netrc

import logging
logg = logging.getLogger("TEST")


class odootopicTest(unittest.TestCase):
    def test_101(self) -> None:
        spec = """
        >> dev1 [Development]
        >> dev1 "project1"
        .. dev1
        """.splitlines()
        data = list(topics.mapping(spec))
        logg.debug("data = %s", data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["proj"], "Development")
        self.assertEqual(data[0]["task"], "project1")
        self.assertEqual(data[0]["pref"], "dev1")
    def test_102(self) -> None:
        spec = """
        >> dev1 [Development]
        >> dev1 "project1"
        .. dev1
        .. dev2
        """.splitlines()
        data = list(topics.mapping(spec))
        logg.debug("data = %s", data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["proj"], "Development")
        self.assertEqual(data[0]["task"], "project1")
        self.assertEqual(data[0]["pref"], "dev1")
        self.assertNotIn("proj", data[1])
        self.assertNotIn("task", data[1])
        self.assertNotIn("pref", data[1])

if __name__ == "__main__":
    # unittest.main()
    from optparse import OptionParser
    cmdline = OptionParser("%prog [z_]test...")
    cmdline.add_option("-v", "--verbose", action="count", default=0)
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
    Runner = unittest.TextTestRunner
    result = Runner(verbosity=opt.verbose).run(suite)
    if not result.wasSuccessful():
        sys.exit(1)
