#! /usr/bin/env python3

__copyright__ = "(C) 2019-2024 Guido Draheim, licensed under the Apache License 2.0"""
__version__ = "0.2.3321"

import timetrack as track
from typing import Optional
import datetime
import unittest
import tempfile
import os
import os.path as path
import sys
from configparser import ConfigParser
from fnmatch import fnmatchcase as fnmatch

import logging
logg = logging.getLogger("TEST")

SCRIPT = "./timetrack.py"

class timetrackTest(unittest.TestCase):
    def setUp(self) -> None:
        track.OUTPUT = ""
    def default_conf(self) -> ConfigParser:
        config = track.default_config()
        conf = ConfigParser()
        conf.read_string(config)
        return conf
    def conf1(self) -> ConfigParser:
        config = """[odoo]
        type = odoo
        url = https://example.com
        db  = testdb"""
        conf = ConfigParser()
        conf.read_string(config)
        return conf
    def test_100(self) -> None:
        conf = self.default_conf()
        data = track.run(conf, ["help"])
        logg.info("data %s", data)
        want = [{"done": "help"}]
        self.assertEqual(want, data)
    def test_101(self) -> None:
        data = track.run(self.conf1(), ["help"])
        logg.info("data %s", data)
        want = [{"done": "help"}]
        self.assertEqual(want, data)
    def test_102(self) -> None:
        conf = self.default_conf()
        data = track.run(self.conf1(), ["get"])
        logg.info("data %s", data)
        types = [item["type"] for item in data]
        want = ["jira", "odoo", "odoo", "proxy", "user", "zeit"]
        self.assertEqual(want, sorted(types))
    def test_103(self) -> None:
        data = track.run(self.conf1(), ["get", "odoo"])
        logg.info("data %s", data)
        want = [{'db': 'testdb', 'name': 'odoo', 'type': 'odoo', 'url': 'https://example.com'}]
        self.assertEqual(want, data)

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
    track.logg.setLevel(max(0, logging.INFO - 10 * opt.verbose + 10 * opt.quiet))
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
