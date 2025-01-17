#! /usr/bin/env python3

__copyright__ = "(C) 2017-2025 Guido Draheim, licensed under the Apache License 2.0"""
__version__ = "1.6.4023"

from typing import Optional, Union, Dict, List, Any, Sequence, Callable, Iterable
from tabtotext import JSONList, JSONDict, JSONItem, DataList, DataItem
from tabtotext import loadJSON, loadCSV, loadGFM, loadHTML, loadYAML, loadTOML, StrToDate, StrToTime
from tabtotext import print_tabtotext, print_tablist, StrToTime, StrToDate
from tabtotext import tablistfile, tablistmap, tablistfor, tablistscanGFM, tablistscanJSON
from tabtotext import TabSheet
import tabtotext
import unittest
import sys
from datetime import date as Date
from datetime import datetime as Time
from datetime import timezone as TimeZone
from datetime import timedelta as Plus
from fnmatch import fnmatchcase as fnmatch
import os
import os.path as path
import shutil
import json
import inspect
from subprocess import getoutput
from zipfile import ZipFile
from dataclasses import dataclass
from io import StringIO

import logging
logg = logging.getLogger("TESTS")
NIX = ""
LIST: List[str] = []
JSONLIST: List[Dict[str, str]] = []
KEEP = 0
TABTO = "./tabtotext.py"
FIXME = True
BIGFILE = 100000

try:
    from tabtools import currency_default
    def X(line: str) -> str:
        return line.replace("$", chr(currency_default))
except ImportError as e:
    def X(line: str) -> str:
        return line

try:
    from tabtoxlsx import tabtoXLSX, readFromXLSX  # type: ignore
    skipXLSX = False
except Exception as e:
    logg.warning("skipping tabtoxlsx: %s", e)
    skipXLSX = True
    def tabtoXLSX(filename: str, data: Iterable[JSONDict], headers: List[str] = [], selected: List[str] = [],  # ..
                  *, legend: List[str] = [], minwidth: int = 0, section: str = NIX) -> str:
        return "skipped"
    def readFromXLSX(filename: str, section: str = NIX) -> JSONList:
        return []
def sh(cmd: str, *args: Any) -> str:
    logg.debug("sh %s", cmd)
    return getoutput(cmd, *args)
def get_caller_name() -> str:
    frame = inspect.currentframe().f_back.f_back  # type: ignore
    return frame.f_code.co_name  # type: ignore
def get_caller_caller_name() -> str:
    frame = inspect.currentframe().f_back.f_back.f_back  # type: ignore
    return frame.f_code.co_name  # type: ignore

def rev(data: List[JSONDict]) -> JSONList:
    return list(reversed(data))

@dataclass
class Item1(DataItem):
    b: JSONItem

@dataclass
class Item2(DataItem):
    a: str
    b: int
    def foo(self, a: str) -> None:
        pass

#######################################################################

test003: JSONList = []
test004: JSONList = [{}]
test004Q: JSONList = []
test005: JSONList = [{"a": "x"}]
test006: JSONList = [{"a": "x", "b": "y"}]
test007: JSONList = [{"b": "y", "a": "x"}, {"b": "v"}]
test007Q: JSONList = [{"b": "y", "a": "x"}, {"b": "v", "a": None}]
test008: JSONList = [{"a": "x"}, {"b": "v"}]
test008N1: JSONList = [{"b": None, "a": "x"}, {"b": "v"}]
test008N2: JSONList = [{"a": "x"}, {"a": None, "b": "v"}]
test008Q: JSONList = [{"b": None, "a": "x"}, {"b": "v", "a": None}]
test009: JSONList = [{}, {"b": "v"}]
test009Q: JSONList = [{"b": None}, {"b": "v"}]
test011: JSONList = [{"b": None}]
test011Q: JSONList = []
test012: JSONList = [{"b": False}]
test013: JSONList = [{"b": True}]
test014: JSONList = [{"b": ""}]
test015: JSONList = [{"b": "5678"}]
test015Q: JSONList = [{"b": 5678}]
test016: JSONList = [{"b": 123}]
test017: JSONList = [{"b": 123.4}]
test018: JSONList = [{"b": Date(2021, 12, 31)}]
test018Q: JSONList = [{"b": Time(2021, 12, 31, 0, 0)}]
test019Q: JSONList = [{"b": Date(2021, 12, 31)}]
test019: JSONList = [{"b": Time(2021, 12, 31, 23, 34, 45)}]

data011: DataList = [Item1(None)]
data012: DataList = [Item1(False)]
data013: DataList = [Item1(True)]
data014: DataList = [Item1("")]
data015: DataList = [Item1("5678")]
data016: DataList = [Item1(123)]
data017: DataList = [Item1(123.4)]
data018: DataList = [Item1(Date(2021, 12, 31))]
data019: DataList = [Item1(Time(2021, 12, 31))]

table01: JSONList = [{"a": "x y"}, {"b": 1}]
table01N1: JSONList = [{'a': 'x y', 'b': None, }, {'b': 1}]
table01N2: JSONList = [{'a': 'x y'}, {'a': None, 'b': 1}]
table01N: JSONList = [{'a': 'x y', 'b': None}, {'a': None, 'b': 1}]
table02: JSONList = [{"a": "x", "b": 0}, {"b": 2}]
table02N: JSONList = [{'a': 'x', 'b': 0}, {'a': None, 'b': 2}]
table22: JSONList = [{"a": "x", "b": 3}, {"b": 2, "a": "y"}]
table33: JSONList = [{"a": "x", "b": 3, "c": Date(2021, 12, 31)},
                     {"b": 2, "a": "y", "c": Date(2021, 12, 30)},
                     {"a": None, "c": Time(2021, 12, 31, 23, 34)}]
table33N: JSONList = [{"a": "x", "b": 3, "c": Date(2021, 12, 31)},
                      {"b": 2, "a": "y", "c": Date(2021, 12, 30)},
                      {"a": None, "b": None, "c": Time(2021, 12, 31, 23, 34)}]
table33Q: JSONList = [{"a": "x", "b": 3, "c": Date(2021, 12, 31)},
                      {"b": 2, "a": "y", "c": Date(2021, 12, 30)},
                      {"a": None, "b": None, "c": Date(2021, 12, 31)}]
table44: JSONList = [{"a": "x", "b": 3, "c": True, "d": 0.4},
                     {"b": 2, "a": "y", "c": False, "d": 0.3},
                     {"a": None, "b": None, "c": True, "d": 0.2},
                     {"a": "y", "b": 1, "d": 0.1}]
table44N: JSONList = [{"a": "x", "b": 3, "c": True, "d": 0.4},
                      {"b": 2, "a": "y", "c": False, "d": 0.3},
                      {"a": None, "b": None, "c": True, "d": 0.2},
                      {"a": "y", "b": 1, "c": None, "d": 0.1}]

def _no_none(data: JSONList, none: str = "") -> JSONList:
    rows: JSONList = []
    for datarow in data:
        row: JSONDict = datarow.copy()
        for name, value in datarow.items():
            if value is None:
                del row[name]
        rows.append(row)
    return rows
def _none(data: JSONList, none: str = "") -> JSONList:
    rows: JSONList = []
    for datarow in data:
        row: JSONDict = datarow.copy()
        for name, value in datarow.items():
            if value is None:
                row[name] = none
        rows.append(row)
    return rows
def _date(data: JSONList, none: str = "") -> JSONList:
    rows: JSONList = []
    for datarow in data:
        row: JSONDict = datarow.copy()
        for name, value in datarow.items():
            if isinstance(value, Time):
                row[name] = value.date()
        rows.append(row)
    return rows

class TabToTextTest(unittest.TestCase):
    def caller_testname(self) -> str:
        name = get_caller_caller_name()
        x1 = name.find("_")
        if x1 < 0: return name
        x2 = name.find("_", x1 + 1)
        if x2 < 0: return name
        return name[:x2]
    def testname(self, suffix: Optional[str] = None) -> str:
        name = self.caller_testname()
        if suffix:
            return name + "_" + suffix
        return name
    def testdir(self, testname: Optional[str] = None, keep: bool = False) -> str:
        testname = testname or self.caller_testname()
        newdir = "tmp/tmp." + testname
        if path.isdir(newdir) and not keep:
            shutil.rmtree(newdir)
        if not path.isdir(newdir):
            os.makedirs(newdir)
        return newdir
    def rm_testdir(self, testname: Optional[str] = None) -> str:
        testname = testname or self.caller_testname()
        newdir = "tmp/tmp." + testname
        if path.isdir(newdir):
            if not KEEP:
                shutil.rmtree(newdir)
        return newdir
    #
    def test_1018(self) -> None:
        item = "abcdefghijklmnopqrstuvwxyz123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        text = tabtotext.str18(item)
        logg.debug("%s => %s", item, text)
        cond = 'abcdefgh...TUVWXYZ'
        self.assertEqual(cond, text)
        self.assertEqual(len(text), 18)
        item = "abcdefghijklmnopqr"
        text = tabtotext.str18(item)
        logg.debug("%s => %s", item, text)
        cond = item
        self.assertEqual(cond, text)
        self.assertEqual(len(text), 18)
        item = "abcdefghijklmnopqrs"
        text = tabtotext.str18(item)
        logg.debug("%s => %s", item, text)
        cond = "abcdefgh...mnopqrs"
        self.assertEqual(cond, text)
        self.assertEqual(len(text), 18)
    def test_1027(self) -> None:
        item = "abcdefghijklmnopqrstuvwxyz123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        text = tabtotext.str27(item)
        logg.debug("%s => %s", item, text)
        cond = 'abcdefghijklmnopq...TUVWXYZ'
        self.assertEqual(cond, text)
        self.assertEqual(len(text), 27)
        item = "abcdefghijklmnopqruvwxyzABC"
        text = tabtotext.str27(item)
        logg.debug("%s => %s", item, text)
        cond = item
        self.assertEqual(cond, text)
        self.assertEqual(len(text), 27)
        item = "abcdefghijklmnopqruvwxyzABCD"
        text = tabtotext.str27(item)
        logg.debug("%s => %s", item, text)
        cond = "abcdefghijklmnopq...xyzABCD"
        self.assertEqual(cond, text)
        self.assertEqual(len(text), 27)
    def test_1040(self) -> None:
        item = "abcdefghijklmnopqrstuvwxyz123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        text = tabtotext.str40(item)
        logg.debug("%s => %s", item, text)
        cond = 'abcdefghijklmnopqrstuvwxyz1234...TUVWXYZ'
        self.assertEqual(cond, text)
        self.assertEqual(len(text), 40)
        item = "abcdefghijklmnopqruvwxyz123456789ABCDEFG"
        text = tabtotext.str40(item)
        logg.debug("%s => %s", item, text)
        cond = item
        self.assertEqual(cond, text)
        self.assertEqual(len(text), 40)
        item = "abcdefghijklmnopqruvwxyz123456789ABCDEFGH"
        text = tabtotext.str40(item)
        logg.debug("%s => %s", item, text)
        cond = "abcdefghijklmnopqruvwxyz123456...BCDEFGH"
        self.assertEqual(cond, text)
        self.assertEqual(len(text), 40)
    def test_1100(self) -> None:
        time = StrToTime()
        want = Date(2022, 12, 23)
        have = time("2022-12-23")
        self.assertEqual(have, want)
        have = time("2022-12-23.")
        self.assertEqual(have, want)
    def test_1101(self) -> None:
        time = StrToTime()
        want = "2022-12-23T"
        have = time(want)
        self.assertEqual(have, want)
        want = "2022-12-2"
        have = time(want)
        self.assertEqual(have, want)
    def test_1102(self) -> None:
        time = StrToTime()
        want = Time(2022, 12, 23, 14, 45)
        have = time("2022-12-23T14:45")
        self.assertEqual(have, want)
        have = time("2022-12-23.14:45:00")
        self.assertEqual(have, want)
    def test_1103(self) -> None:
        time = StrToTime()
        want = "2022-12-23T14"
        have = time(want)
        self.assertEqual(have, want)
        want = "2022-12-23.14:"
        have = time(want)
        self.assertEqual(have, want)
        want = "2022-12-23.14:45:"
        have = time(want)
        self.assertEqual(have, want)
    def test_1104(self) -> None:
        time = StrToTime()
        want = Time(2022, 12, 23, 14, 45, tzinfo=TimeZone.utc)
        have = time("2022-12-23T14:45Z")
        self.assertEqual(have, want)
        have = time("2022-12-23.14:45:00 Z")
        self.assertEqual(have, want)
        have = time("2022-12-23.14:45:00 +00")
        self.assertEqual(have, want)
    def test_1105(self) -> None:
        time = StrToTime()
        want = "2022-12-23T14Z"
        have = time(want)
        self.assertEqual(have, want)
        want = "2022-12-23.14:45:Z"
        have = time(want)
        self.assertEqual(have, want)
        want = "2022-12-23.14:45:.Z"
        have = time(want)
        self.assertEqual(have, want)
    def test_1106(self) -> None:
        time = StrToTime()
        want = Time(2022, 12, 23, 14, 45, tzinfo=TimeZone(Plus(hours=1)))
        have = time("2022-12-23T14:45+01")
        self.assertEqual(have, want)
        have = time("2022-12-23.14:45:00 +0100")
        self.assertEqual(have, want)
        have = time("2022-12-23.14:45:00 +01:00")
        self.assertEqual(have, want)
    def test_1107(self) -> None:
        time = StrToTime()
        want = "2022-12-23T14+01"
        have = time(want)
        self.assertEqual(have, want)
        want = "2022-12-23.14:45:+01"
        have = time(want)
        self.assertEqual(have, want)
        want = "2022-12-23.14:45:+01.00"
        have = time(want)
        self.assertEqual(have, want)
    def test_1109(self) -> None:
        BB = 880 * 1000
        time = StrToTime()
        want = Time(2022, 12, 23, 14, 45, 55, BB, tzinfo=TimeZone(Plus(hours=-1)))
        have = time("2022-12-23T14:45:55.88-01")
        self.assertEqual(have, want)
        have = time("2022-12-23.14:45:55.880 -0100")
        self.assertEqual(have, want)
        have = time("2022-12-23.14:45:55.880000 -01:00")
        self.assertEqual(have, want)
    def test_1110(self) -> None:
        time = StrToDate()
        want = Date(2022, 12, 23)
        have = time("2022-12-23")
        self.assertEqual(have, want)
        have = time("2022-12-23.")
        self.assertEqual(have, want)
        have = time("2022-12-23T23:45")
        self.assertEqual(have, want)
        have = time("2022-12-23++++")
        self.assertEqual(have, want)
    def test_1111(self) -> None:
        time = StrToDate()
        want = "2022-12-234"
        have = time(want)
        self.assertEqual(have, want)
        want = "2022-12-2"
        have = time(want)
        self.assertEqual(have, want)
    #
    def test_4003(self) -> None:
        text = tabtotext.tabToCSV(test003)
        logg.debug("%s => %s", test003, text)
        want = LIST
        cond = ['']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4004(self) -> None:
        text = tabtotext.tabToCSV(test004)
        logg.debug("%s => %s", test004, text)
        want = LIST
        cond = ['', '', ]
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4005(self) -> None:
        text = tabtotext.tabToCSV(test005)
        logg.debug("%s => %s", test005, text)
        want = test005
        cond = ['a', 'x', ]
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4006(self) -> None:
        text = tabtotext.tabToCSV(test006)
        logg.debug("%s => %s", test006, text)
        want = test006
        cond = ['a;b', 'x;y', ]
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4007(self) -> None:
        text = tabtotext.tabToCSV(test007)
        logg.debug("%s => %s", test007, text)
        want = test007Q
        cond = ['a;b', 'x;y', '~;v']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4008(self) -> None:
        text = tabtotext.tabToCSV(test008)
        logg.debug("%s => %s", test008, text)
        want = test008Q
        cond = ['a;b', 'x;~', '~;v']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4009(self) -> None:
        text = tabtotext.tabToCSV(test009)
        logg.debug("%s => %s", test009, text)
        want = test009Q
        cond = ['b', '~', 'v']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4011(self) -> None:
        text = tabtotext.tabToCSV(test011)
        logg.debug("%s => %s", test011, text)
        want = test011
        cond = ['b', '~']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4012(self) -> None:
        text = tabtotext.tabToCSV(test012)
        logg.debug("%s => %s", test012, text)
        want = test012
        cond = ['b', '(no)']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4013(self) -> None:
        text = tabtotext.tabToCSV(test013)
        logg.debug("%s => %s", test013, text)
        want = test013
        cond = ['b', '(yes)']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4014(self) -> None:
        text = tabtotext.tabToCSV(test014)
        logg.debug("%s => %s", test014, text)
        want = test014
        cond = ['b', '""']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4015(self) -> None:
        text = tabtotext.tabToCSV(test015)
        logg.debug("%s => %s", test015, text)
        want = test015Q
        cond = ['b', '5678']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4016(self) -> None:
        text = tabtotext.tabToCSV(test016)
        logg.debug("%s => %s", test016, text)
        want = test016
        cond = ['b', '123']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        if back[0]['b'] == "123":
            back[0]['b'] = 123
        self.assertEqual(want, back)
    def test_4017(self) -> None:
        text = tabtotext.tabToCSV(test017)
        logg.debug("%s => %s", test017, text)
        want = test017
        cond = ['b', '123.40']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        if back[0]['b'] == "123.40":
            back[0]['b'] = 123.4
        self.assertEqual(want, back)
    def test_4018(self) -> None:
        text = tabtotext.tabToCSV(test018)
        logg.debug("%s => %s", test018, text)
        want = test018
        cond = ['b', '2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4019(self) -> None:
        text = tabtotext.tabToCSV(test019)
        logg.debug("%s => %s", test019, text)
        want = test018  # test019
        cond = ['b', '2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4020(self) -> None:
        text = tabtotext.tabToCSV(table01)
        logg.debug("%s => %s", table01, text)
        want = table01N
        cond = ['a;b', 'x y;~', '~;1']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4021(self) -> None:
        text = tabtotext.tabToCSV(table02)
        logg.debug("%s => %s", table02, text)
        want = table02N
        cond = ['a;b', 'x;0', '~;2']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4022(self) -> None:
        text = tabtotext.tabToCSV(table22)
        logg.debug("%s => %s", table22, text)
        want = table22
        cond = ['a;b', 'x;3', 'y;2']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4023(self) -> None:
        text = tabtotext.tabToCSV(table33)
        logg.debug("%s => %s", table33, text)
        want = table33Q
        cond = ['a;b;c', 'x;3;2021-12-31', 'y;2;2021-12-30', '~;~;2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4024(self) -> None:
        text = tabtotext.tabToCSV(table44)
        logg.debug("%s => %s", table44, text)
        want = table44N
        cond = ['a;b;c;d', 'x;3;(yes);0.40', 'y;2;(no);0.30', '~;~;(yes);0.20', 'y;1;~;0.10']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4030(self) -> None:
        """ legend is ignored for CSV """
        text = tabtotext.tabToCSV(test011, legend="a result")
        logg.debug("%s => %s", test011, text)
        want = test011
        cond = ['b', '~']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4031(self) -> None:
        """ legend is ignored for CSV """
        text = tabtotext.tabToCSV(test011, legend=["a result", "was found"])
        logg.debug("%s => %s", test011, text)
        want = test011
        cond = ['b', '~']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4044(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        text = tabtotext.tabToCSV(itemlist, sorts=['b', 'a'])
        logg.debug("%s => %s", test004, text)
        cond = ['b;a', '1;y', '2;x']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        want = [{'a': 'y', 'b': 1}, {'a': 'x', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_4045(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}, {'c': 'h'}]
        text = tabtotext.tabToCSV(itemlist, sorts=['b', 'a'])
        logg.debug("%s => %s", test004, text)
        cond = ['b;a;c', '1;y;~', '2;x;~', '~;~;h', ]
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        want = [{'a': 'y', 'b': 1, 'c': None}, {'a': 'x', 'b': 2, 'c': None}, {'a': None, 'b': None, 'c': "h"}, ]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_4046(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}, {'c': 'h'}]
        text = tabtotext.tabToCSV(itemlist, sorts=['b', 'a'], reorder=['a', 'b'])
        logg.debug("%s => %s", test004, text)
        cond = ['a;b;c', 'y;1;~', 'x;2;~', '~;~;h', ]  # column a is now first
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        want = [{'a': 'y', 'b': 1, 'c': None}, {'a': 'x', 'b': 2, 'c': None}, {'a': None, 'b': None, 'c': "h"}, ]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_4051(self) -> None:
        text = tabtotext.tabToCSVx(data011)
        logg.debug("%s => %s", data011, text)
        want = test011
        cond = ['b', '~']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4052(self) -> None:
        text = tabtotext.tabToCSVx(data012)
        logg.debug("%s => %s", data012, text)
        want = test012
        cond = ['b', '(no)']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4053(self) -> None:
        text = tabtotext.tabToCSVx(data013)
        logg.debug("%s => %s", data013, text)
        want = test013
        cond = ['b', '(yes)']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4054(self) -> None:
        text = tabtotext.tabToCSVx(data014)
        logg.debug("%s => %s", data014, text)
        want = test014
        cond = ['b', '""']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4055(self) -> None:
        text = tabtotext.tabToCSVx(data015)
        logg.debug("%s => %s", data015, text)
        want = test015Q
        cond = ['b', '5678']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4056(self) -> None:
        text = tabtotext.tabToCSVx(data016)
        logg.debug("%s => %s", data016, text)
        want = test016
        cond = ['b', '123']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        if back[0]['b'] == "123":
            back[0]['b'] = 123
        self.assertEqual(want, back)
    def test_4057(self) -> None:
        text = tabtotext.tabToCSVx(data017)
        logg.debug("%s => %s", data017, text)
        want = test017
        cond = ['b', '123.40']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        if back[0]['b'] == "123.40":
            back[0]['b'] = 123.4
        self.assertEqual(want, back)
    def test_4058(self) -> None:
        text = tabtotext.tabToCSVx(data018)
        logg.debug("%s => %s", data018, text)
        want = test018
        cond = ['b', '2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4059(self) -> None:
        text = tabtotext.tabToCSVx(data019)
        logg.debug("%s => %s", data019, text)
        want = test018  # test019
        cond = ['b', '2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4060(self) -> None:
        text = tabtotext.tabToCSV(table01, ["b", "a"])
        logg.debug("%s => %s", table01, text)
        want = rev(table01N)
        cond = ['b;a', '1;~', '~;x y']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4061(self) -> None:
        text = tabtotext.tabToCSV(table02, ["b", "a"])
        logg.debug("%s => %s", table02, text)
        want = table02N
        cond = ['b;a', '0;x', '2;~']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4062(self) -> None:
        text = tabtotext.tabToCSV(table22, ["b", "a"])
        logg.debug("%s => %s", table22, text)
        want = rev(table22)
        cond = ['b;a', '2;y', '3;x']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4063(self) -> None:
        text = tabtotext.tabToCSV(table33, ["b", "a"])
        logg.debug("%s => %s", table33, text)
        want = rev(table33Q[:2]) + table33Q[2:]
        cond = ['b;a;c', '2;y;2021-12-30', '3;x;2021-12-31', '~;~;2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4064(self) -> None:
        text = tabtotext.tabToCSV(table44, ["b", "a"])
        logg.debug("%s => %s", table33, text)
        want = table44N[3:] + table44N[1:2] + table44N[0:1] + table44N[2:3]
        cond = ['b;a;c;d', '1;y;~;0.10', '2;y;(no);0.30', '3;x;(yes);0.40', '~;~;(yes);0.20']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        logg.info("want %s", want)
        logg.info("back %s", back)
        self.assertEqual(want, back)
    def test_4065(self) -> None:
        text = tabtotext.tabToCSV(table33, ["c", "a"])
        logg.debug("%s => %s", table33, text)
        want = rev(table33Q[:2]) + table33Q[2:]
        cond = ['c;a;b', '2021-12-30;y;2', '2021-12-31;x;3', '2021-12-31;~;~']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)

    def test_4071(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        formats = {"a": ' {:}'}
        headers = ['b', 'a']
        text = tabtotext.tabToCSV(itemlist, ['b', 'a'], formats)
        logg.debug("%s => %s", test004, text)
        cond = ['b;a', '1; y', '2; x']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        want = [{'a': ' y', 'b': 1}, {'a': ' x', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_4072(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        formats = {"a": ' %s'}
        headers = ['b', 'a']
        text = tabtotext.tabToCSV(itemlist, ['b', 'a'], formats)
        logg.debug("%s => %s", test004, text)
        cond = ['b;a', '1; y', '2; x']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        want = [{'a': ' y', 'b': 1}, {'a': ' x', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_4073(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        formats = {"a": '(%s)', "b": "%.2f"}
        headers = ['b', 'a']
        text = tabtotext.tabToCSV(itemlist, ['b', 'a'], formats)
        logg.debug("%s => %s", test004, text)
        cond = ['b;a', '1.00;(y)', '2.00;(x)']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        want = [{'a': '(y)', 'b': 1}, {'a': '(x)', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_4074(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        formats = {"a": '({:})', "b": "{:.2f}"}
        headers = ['b', 'a']
        text = tabtotext.tabToCSV(itemlist, ['b', 'a'], formats)
        logg.debug("%s => %s", test004, text)
        cond = ['b;a', '1.00;(y)', '2.00;(x)']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        want = [{'a': '(y)', 'b': 1}, {'a': '(x)', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_4075(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2.}, {'a': "y", 'b': 1.}]
        formats = {"a": '({:})', "b": "%.2f"}
        headers = ['b', 'a']
        text = tabtotext.tabToCSV(itemlist, ['b', 'a'], formats)
        logg.debug("%s => %s", test004, text)
        cond = ['b;a', '1.00;(y)', '2.00;(x)']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        want = [{'a': '(y)', 'b': 1}, {'a': '(x)', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_4076(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2.}, {'a': "y", 'b': 1.}]
        formats = {"a": '({:})', "b": "{:.3f}"}
        headers = ['b', 'a']
        text = tabtotext.tabToCSV(itemlist, ['b', 'a'], formats)
        logg.debug("%s => %s", test004, text)
        cond = ['b;a', '1.000;(y)', '2.000;(x)']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        want = [{'a': '(y)', 'b': 1}, {'a': '(x)', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_4077(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2.}, {'a': "y", 'b': 1.}]
        formats = {"a": '({:5s})', "b": "{:3f}"}
        headers = ['b', 'a']
        text = tabtotext.tabToCSV(itemlist, ['b', 'a'], formats)
        logg.debug("%s => %s", test004, text)
        cond = ['b;a', '1.000000;(y    )', '2.000000;(x    )']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        want = [{'a': '(y    )', 'b': 1.0}, {'a': '(x    )', 'b': 2.0}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_4078(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2.}, {'a': "y", 'b': 1.}]
        formats = {"a": '"{:5s}"', "b": "{:3f}"}
        headers = ['b', 'a']
        text = tabtotext.tabToCSV(itemlist, ['b', 'a'], formats)
        logg.debug("%s => %s", test004, text)
        cond = ['b;a', '1.000000;"""y    """', '2.000000;"""x    """']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        want = [{'a': '"y    "', 'b': 1.0}, {'a': '"x    "', 'b': 2.0}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_4079(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 22.}, {'a': "y", 'b': 1.}]
        formats = {"a": '"{:>5s}"', "b": "{:>3f}"}
        headers = ['b', 'a']
        text = tabtotext.tabToCSV(itemlist, ['b', 'a'], formats)
        logg.debug("%s => %s", test004, text)
        cond = ['b;a', '1.000000;"""    y"""', '22.000000;"""    x"""']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        want = [{'a': '"    y"', 'b': 1.0}, {'a': '"    x"', 'b': 22.0}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_4103(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test003, defaultformat="csv")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test003, text)
        want = LIST
        cond = ['']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4104(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test004, defaultformat="csv")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        want = LIST
        cond = ['', '', ]
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4105(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test005, defaultformat="csv")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test005, text)
        want = test005
        cond = ['a', 'x', ]
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4106(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test006, defaultformat="csv")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test006, text)
        want = test006
        cond = ['a;b', 'x;y', ]
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4107(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test007, defaultformat="csv")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test007, text)
        want = test007Q
        cond = ['a;b', 'x;y', '~;v']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4108(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test008, defaultformat="csv")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test008, text)
        want = test008Q
        cond = ['a;b', 'x;~', '~;v']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4109(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test009, defaultformat="csv")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test009, text)
        want = test009Q
        cond = ['b', '~', 'v']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4111(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test011, defaultformat="csv")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test011, text)
        want = test011
        cond = ['b', '~']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4112(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test012, defaultformat="csv")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test012, text)
        want = test012
        cond = ['b', '(no)']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4113(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test013, defaultformat="csv")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test013, text)
        want = test013
        cond = ['b', '(yes)']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4114(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test014, defaultformat="csv")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test014, text)
        want = test014
        cond = ['b', '""']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4115(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test015, defaultformat="csv")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test015, text)
        want = test015Q
        cond = ['b', '5678']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4116(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test016, defaultformat="csv")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test016, text)
        want = test016
        cond = ['b', '123']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        if back[0]['b'] == "123":
            back[0]['b'] = 123
        self.assertEqual(want, back)
    def test_4117(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test017, defaultformat="csv")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test017, text)
        want = test017
        cond = ['b', '123.40']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        if back[0]['b'] == "123.40":
            back[0]['b'] = 123.4
        self.assertEqual(want, back)
    def test_4118(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test018, defaultformat="csv")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test018, text)
        want = test018
        cond = ['b', '2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4119(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test019, defaultformat="csv")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test019, text)
        want = test018  # test019
        cond = ['b', '2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4131(self) -> None:
        """ legend is ignored for CSV """
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test011, defaultformat="csv", legend=["a result", "was found"])
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test011, text)
        want = test011
        cond = ['b', '~']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4143(self) -> None:
        out = StringIO()
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        res = tabtotext.print_tabtotext(out, itemlist, ['b', 'a'], defaultformat="csv")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['b;a', '2;x', '1;y']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        want = [{'a': 'x', 'b': 2}, {'a': 'y', 'b': 1}, ]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_4144(self) -> None:
        out = StringIO()
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        res = tabtotext.print_tabtotext(out, itemlist, ['b@:1', 'a@:2'], defaultformat="csv")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['b;a', '1;y', '2;x']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        want = [{'a': 'y', 'b': 1}, {'a': 'x', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_4145(self) -> None:
        out = StringIO()
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}, {'c': 'h'}]
        res = tabtotext.print_tabtotext(out, itemlist, ['b@:1', 'a@:2'], defaultformat="csv")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['b;a;c', '1;y;~', '2;x;~', '~;~;h', ]
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        want = [{'a': 'y', 'b': 1, 'c': None}, {'a': 'x', 'b': 2, 'c': None}, {'a': None, 'b': None, 'c': "h"}, ]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_4171(self) -> None:
        out = StringIO()
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        res = tabtotext.print_tabtotext(out, itemlist, ['b@1', 'a: {:}'], defaultformat="csv")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['b;a', '1; y', '2; x']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        want = [{'a': ' y', 'b': 1}, {'a': ' x', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_4172(self) -> None:
        out = StringIO()
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        res = tabtotext.print_tabtotext(out, itemlist, ['b@1', 'a: %s'], defaultformat="csv")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['b;a', '1; y', '2; x']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        want = [{'a': ' y', 'b': 1}, {'a': ' x', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_4173(self) -> None:
        out = StringIO()
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        res = tabtotext.print_tabtotext(out, itemlist, ['b:.2f@1', 'a:(%s)'], defaultformat="csv")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['b;a', '1.00;(y)', '2.00;(x)']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        want = [{'a': '(y)', 'b': 1}, {'a': '(x)', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_4174(self) -> None:
        out = StringIO()
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        res = tabtotext.print_tabtotext(out, itemlist, ['b:.2f@1', 'a:({:})'], defaultformat="csv")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['b;a', '1.00;(y)', '2.00;(x)']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        want = [{'a': '(y)', 'b': 1}, {'a': '(x)', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_4175(self) -> None:
        out = StringIO()
        itemlist: JSONList = [{'a': "x", 'b': 2.}, {'a': "y", 'b': 1.}]
        res = tabtotext.print_tabtotext(out, itemlist, ['b:.2f@1', 'a:({:})'], defaultformat="csv")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['b;a', '1.00;(y)', '2.00;(x)']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        want = [{'a': '(y)', 'b': 1}, {'a': '(x)', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_4176(self) -> None:
        out = StringIO()
        itemlist: JSONList = [{'a': "x", 'b': 2.}, {'a': "y", 'b': 1.}]
        formats = {"a": '({:})', "b": "{:.3f}"}
        headers = ['b', 'a']
        res = tabtotext.print_tabtotext(out, itemlist, ['b:{:.3f}@1', 'a:({:})'], defaultformat="csv")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['b;a', '1.000;(y)', '2.000;(x)']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        want = [{'a': '(y)', 'b': 1}, {'a': '(x)', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_4177(self) -> None:
        out = StringIO()
        itemlist: JSONList = [{'a': "x", 'b': 2.}, {'a': "y", 'b': 1.}]
        formats = {"a": '({:5s})', "b": "{:3f}"}
        headers = ['b', 'a']
        res = tabtotext.print_tabtotext(out, itemlist, ['b:{:3f}@1', 'a:({:5s})'], defaultformat="csv")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['b;a', '1.000000;(y    )', '2.000000;(x    )']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        want = [{'a': '(y    )', 'b': 1.0}, {'a': '(x    )', 'b': 2.0}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_4178(self) -> None:
        out = StringIO()
        itemlist: JSONList = [{'a': "x", 'b': 2.}, {'a': "y", 'b': 1.}]
        formats = {"a": '"{:5s}"', "b": "{:3f}"}
        headers = ['b', 'a']
        res = tabtotext.print_tabtotext(out, itemlist, ['b:{:3f}@1', 'a:"{:5s}"'], defaultformat="csv")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['b;a', '1.000000;"""y    """', '2.000000;"""x    """']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        want = [{'a': '"y    "', 'b': 1.0}, {'a': '"x    "', 'b': 2.0}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_4179(self) -> None:
        out = StringIO()
        itemlist: JSONList = [{'a': "x", 'b': 22.}, {'a': "y", 'b': 1.}]
        formats = {"a": '"{:>5s}"', "b": "{:>3f}"}
        headers = ['b', 'a']
        res = tabtotext.print_tabtotext(out, itemlist, ['b:{:>3f}@1', 'a:"{:>5s}"'], defaultformat="csv")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['b;a', '1.000000;"""    y"""', '22.000000;"""    x"""']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        want = [{'a': '"    y"', 'b': 1.0}, {'a': '"    x"', 'b': 22.0}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_4403(self) -> None:
        text = tabtotext.tabtoCSV(test003)
        logg.debug("%s => %s", test003, text)
        want = LIST
        cond = ['']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4404(self) -> None:
        text = tabtotext.tabtoCSV(test004)
        logg.debug("%s => %s", test004, text)
        want = LIST
        cond = ['', '', ]
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4405(self) -> None:
        text = tabtotext.tabtoCSV(test005)
        logg.debug("%s => %s", test005, text)
        want = test005
        cond = ['a', 'x', ]
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4406(self) -> None:
        text = tabtotext.tabtoCSV(test006)
        logg.debug("%s => %s", test006, text)
        want = test006
        cond = ['a;b', 'x;y', ]
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4407(self) -> None:
        text = tabtotext.tabtoCSV(test007)
        logg.debug("%s => %s", test007, text)
        want = test007Q
        cond = ['a;b', 'x;y', '~;v']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4408(self) -> None:
        text = tabtotext.tabtoCSV(test008)
        logg.debug("%s => %s", test008, text)
        want = test008Q
        cond = ['a;b', 'x;~', '~;v']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4409(self) -> None:
        text = tabtotext.tabtoCSV(test009)
        logg.debug("%s => %s", test009, text)
        want = test009Q
        cond = ['b', '~', 'v']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4411(self) -> None:
        text = tabtotext.tabtoCSV(test011)
        logg.debug("%s => %s", test011, text)
        want = test011
        cond = ['b', '~']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4412(self) -> None:
        text = tabtotext.tabtoCSV(test012)
        logg.debug("%s => %s", test012, text)
        want = test012
        cond = ['b', '(no)']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4413(self) -> None:
        text = tabtotext.tabtoCSV(test013)
        logg.debug("%s => %s", test013, text)
        want = test013
        cond = ['b', '(yes)']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4414(self) -> None:
        text = tabtotext.tabtoCSV(test014)
        logg.debug("%s => %s", test014, text)
        want = test014
        cond = ['b', '""']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4415(self) -> None:
        text = tabtotext.tabtoCSV(test015)
        logg.debug("%s => %s", test015, text)
        want = test015Q
        cond = ['b', '5678']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4416(self) -> None:
        text = tabtotext.tabtoCSV(test016)
        logg.debug("%s => %s", test016, text)
        want = test016
        cond = ['b', '123']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        if back[0]['b'] == "123":
            back[0]['b'] = 123
        self.assertEqual(want, back)
    def test_4417(self) -> None:
        text = tabtotext.tabtoCSV(test017)
        logg.debug("%s => %s", test017, text)
        want = test017
        cond = ['b', '123.40']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        if back[0]['b'] == "123.40":
            back[0]['b'] = 123.4
        self.assertEqual(want, back)
    def test_4418(self) -> None:
        text = tabtotext.tabtoCSV(test018)
        logg.debug("%s => %s", test018, text)
        want = test018
        cond = ['b', '2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4419(self) -> None:
        text = tabtotext.tabtoCSV(test019)
        logg.debug("%s => %s", test019, text)
        want = test018  # test019
        cond = ['b', '2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4420(self) -> None:
        text = tabtotext.tabtoCSV(table01)
        logg.debug("%s => %s", table01, text)
        want = table01N
        cond = ['a;b', 'x y;~', '~;1']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4421(self) -> None:
        text = tabtotext.tabtoCSV(table02)
        logg.debug("%s => %s", table02, text)
        want = table02N
        cond = ['a;b', 'x;0', '~;2']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4422(self) -> None:
        text = tabtotext.tabtoCSV(table22)
        logg.debug("%s => %s", table22, text)
        want = table22
        cond = ['a;b', 'x;3', 'y;2']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4423(self) -> None:
        text = tabtotext.tabtoCSV(table33)
        logg.debug("%s => %s", table33, text)
        want = table33Q
        cond = ['a;b;c', 'x;3;2021-12-31', 'y;2;2021-12-30', '~;~;2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4430(self) -> None:
        """ legend is ignored for CSV """
        text = tabtotext.tabtoCSV(test011, legend="a result")
        logg.debug("%s => %s", test011, text)
        want = test011
        cond = ['b', '~']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4431(self) -> None:
        """ legend is ignored for CSV """
        text = tabtotext.tabtoCSV(test011, legend=["a result", "was found"])
        logg.debug("%s => %s", test011, text)
        want = test011
        cond = ['b', '~']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4444(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        text = tabtotext.tabtoCSV(itemlist, sorts=['b', 'a'])
        logg.debug("%s => %s", test004, text)
        cond = ['b;a', '1;y', '2;x']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        want = [{'a': 'y', 'b': 1}, {'a': 'x', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_4445(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}, {'c': 'h'}]
        text = tabtotext.tabtoCSV(itemlist, sorts=['b', 'a'])
        logg.debug("%s => %s", test004, text)
        cond = ['b;a;c', '1;y;~', '2;x;~', '~;~;h', ]
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        want = [{'a': 'y', 'b': 1, 'c': None}, {'a': 'x', 'b': 2, 'c': None}, {'a': None, 'b': None, 'c': "h"}, ]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_4446(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}, {'c': 'h'}]
        text = tabtotext.tabtoCSV(itemlist, sorts=['b', 'a'], reorder=['a', 'b'])
        logg.debug("%s => %s", test004, text)
        cond = ['a;b;c', 'y;1;~', 'x;2;~', '~;~;h', ]  # column a is now first
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        want = [{'a': 'y', 'b': 1, 'c': None}, {'a': 'x', 'b': 2, 'c': None}, {'a': None, 'b': None, 'c': "h"}, ]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_4460(self) -> None:
        text = tabtotext.tabtoCSV(table01, ["b", "a"])
        logg.debug("%s => %s", table01, text)
        want = table01N
        cond = ['b;a', '~;x y', '1;~']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4461(self) -> None:
        text = tabtotext.tabtoCSV(table02, ["b", "a"])
        logg.debug("%s => %s", table02, text)
        want = table02N
        cond = ['b;a', '0;x', '2;~']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4462(self) -> None:
        text = tabtotext.tabtoCSV(table22, ["b", "a"])
        logg.debug("%s => %s", table22, text)
        want = table22
        cond = ['b;a', '3;x', '2;y']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4463(self) -> None:
        text = tabtotext.tabtoCSV(table33, ["b", "a"])
        logg.debug("%s => %s", table33, text)
        want = table33Q
        cond = ['b;a;c', '3;x;2021-12-31', '2;y;2021-12-30', '~;~;2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4465(self) -> None:
        text = tabtotext.tabtoCSV(table33, ["c", "a"])
        logg.debug("%s => %s", table33, text)
        want = table33Q
        cond = ['c;a;b', '2021-12-31;x;3', '2021-12-30;y;2', '2021-12-31;~;~']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4466(self) -> None:
        text = tabtotext.tabtoCSV(table02, ["b", "a"], ["b", "a"])
        logg.debug("%s => %s", table02, text)
        want = table02N
        cond = ['b;a', '0;x', '2;~']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4467(self) -> None:
        text = tabtotext.tabtoCSV(table22, ["b", "a"], ["b", "a"])
        logg.debug("%s => %s", table22, text)
        want = rev(table22)
        cond = ['b;a', '2;y', '3;x']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4468(self) -> None:
        text = tabtotext.tabtoCSV(table33, ["b", "a"], ["b", "a", "c"])
        logg.debug("%s => %s", table33, text)
        want = rev(table33Q[:2]) + table33Q[2:]
        cond = ['b;a;c', '2;y;2021-12-30', '3;x;2021-12-31', '~;~;2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4469(self) -> None:
        text = tabtotext.tabtoCSV(table33, ["c", "a"], ["c", "a", "b"])
        logg.debug("%s => %s", table33, text)
        want = rev(table33Q[:2]) + table33Q[2:]
        cond = ['c;a;b', '2021-12-30;y;2', '2021-12-31;x;3', '2021-12-31;~;~']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4470(self) -> None:
        text = tabtotext.tabtoCSV(table01, ["b", "a"], ["a"])
        logg.debug("%s => %s", table01, text)
        cond = ['a', '~', 'x y']
        want = [{'a': None}, {'a': 'x y'}]
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4471(self) -> None:
        text = tabtotext.tabtoCSV(table02, ["b", "a"], ["a"])
        logg.debug("%s => %s", table02, text)
        cond = ['a', '~', 'x']
        want = [{'a': None}, {'a': 'x'}]
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4472(self) -> None:
        text = tabtotext.tabtoCSV(table22, ["b", "a"], ["a"])
        logg.debug("%s => %s", table22, text)
        cond = ['a', 'x', 'y']
        want = [{'a': 'x'}, {'a': 'y'}]
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4473(self) -> None:
        text = tabtotext.tabtoCSV(table33, ["b", "a"], ["a"])
        logg.debug("%s => %s", table33, text)
        cond = ['a', '~', 'x', 'y']
        want = [{'a': None}, {'a': 'x'}, {'a': 'y'}]
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4474(self) -> None:
        text = tabtotext.tabtoCSV(table33, ["c", "a"], ["a"])
        logg.debug("%s => %s", table33, text)
        cond = ['a', '~', 'x', 'y']
        want = [{'a': None}, {'a': 'x'}, {'a': 'y'}]
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4475(self) -> None:
        text = tabtotext.tabtoCSV(table02, ["b", "a"], ["b"])
        logg.debug("%s => %s", table02, text)
        cond = ['b', '0', '2']
        want = [{'b': 0}, {'b': 2}]
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4476(self) -> None:
        text = tabtotext.tabtoCSV(table22, ["b", "a"], ["b"])
        logg.debug("%s => %s", table22, text)
        cond = ['b', '2', '3']
        want = [{'b': 2}, {'b': 3}]
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4477(self) -> None:
        text = tabtotext.tabtoCSV(table33, ["b", "a"], ["b"])
        logg.debug("%s => %s", table33, text)
        cond = ['b', '2', '3', '~']
        want = [{'b': 2}, {'b': 3}, {'b': None}]
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4478(self) -> None:
        text = tabtotext.tabtoCSV(table33, ["c", "a"], ["b"])
        logg.debug("%s => %s", table33, text)
        cond = ['b', '2', '3', '~']
        want = [{'b': 2}, {'b': 3}, {'b': None}]
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4479(self) -> None:
        text = tabtotext.tabtoCSV(table33, ["c", "a"], ["c"])
        logg.debug("%s => %s", table33, text)
        cond = ['c', '2021-12-30', '2021-12-31', '2021-12-31']
        want = [{'c': Date(2021, 12, 30)}, {'c': Date(2021, 12, 31)}, {'c': Date(2021, 12, 31)}]
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4530(self) -> None:
        text = tabtotext.tabtoCSV(table01, ["a|b"])
        logg.debug("%s => %s", table01, text.splitlines())
        cond = ['a;b', 'x y;~', '~;1']
        want = table01N
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4531(self) -> None:
        text = tabtotext.tabtoCSV(table02, ["a|b"])
        logg.debug("%s => %s", table02, text.splitlines())
        cond = ['a;b', 'x;0', '~;2']
        want = table02N
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4532(self) -> None:
        text = tabtotext.tabtoCSV(table22, ["a|b"])
        logg.debug("%s => %s", table22, text.splitlines())
        cond = ['a;b', 'x;3', 'y;2']
        self.assertEqual(cond, text.splitlines())
        want = table22
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4533(self) -> None:
        text = tabtotext.tabtoCSV(table33, ["a|b"])
        logg.debug("%s => %s", table33, text.splitlines())
        cond = ['a;b;c', 'x;3;2021-12-31', 'y;2;2021-12-30', '~;~;2021-12-31']
        self.assertEqual(cond, text.splitlines())
        want = table33Q
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4534(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['a;b;c;d', 'x;3;(yes);0.40', 'y;2;(no);0.30', '~;~;(yes);0.20', 'y;1;~;0.10']
        self.assertEqual(cond, text.splitlines())
        want = table44N
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4535(self) -> None:
        text = tabtotext.tabtoCSV(table01, ["b|a"])
        logg.debug("%s => %s", table01, text.splitlines())
        cond = ['b;a', '~;x y', '1;~']
        self.assertEqual(cond, text.splitlines())
        want = table01N
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4536(self) -> None:
        text = tabtotext.tabtoCSV(table02, ["b|a"])
        logg.debug("%s => %s", table02, text.splitlines())
        cond = ['b;a', '0;x', '2;~']
        self.assertEqual(cond, text.splitlines())
        want = table02N
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4537(self) -> None:
        text = tabtotext.tabtoCSV(table22, ["b|a"])
        logg.debug("%s => %s", table22, text.splitlines())
        cond = ['b;a', '3;x', '2;y']
        self.assertEqual(cond, text.splitlines())
        want = table22
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4538(self) -> None:
        text = tabtotext.tabtoCSV(table33, ["b|a"])
        logg.debug("%s => %s", table33, text.splitlines())
        cond = ['b;a;c', '3;x;2021-12-31', '2;y;2021-12-30', '~;~;2021-12-31']
        self.assertEqual(cond, text.splitlines())
        want = table33Q
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4539(self) -> None:
        text = tabtotext.tabtoCSV(table33, ["b|c|a"])
        logg.debug("%s => %s", table33, text.splitlines())
        cond = ['b;c;a', '3;2021-12-31;x', '2;2021-12-30;y', '~;2021-12-31;~']
        self.assertEqual(cond, text.splitlines())
        want = table33Q
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4594(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["a|b"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['a;b', '~;~', 'x;3', 'y;1', 'y;2']
        self.assertEqual(cond, text.splitlines())
    def test_4595(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["b|a"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['b;a', '1;y', '2;y', '3;x', '~;~']
        self.assertEqual(cond, text.splitlines())
    def test_4596(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["b|d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['b;d', '1;0.10', '2;0.30', '3;0.40', '~;0.20']
        self.assertEqual(cond, text.splitlines())
    def test_4598(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["a|b|d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['a;b;d', '~;~;0.20', 'x;3;0.40', 'y;1;0.10', 'y;2;0.30']
        self.assertEqual(cond, text.splitlines())
    def test_4599(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["b|c|a"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['b;c;a', '1;~;y', '2;(no);y', '3;(yes);x', '~;(yes);~']
        self.assertEqual(cond, text.splitlines())
    def test_4600(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["b|d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['b;d', '1;0.10', '2;0.30', '3;0.40', '~;0.20']
        self.assertEqual(cond, text.splitlines())
    def test_4601(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["b:02.1f|d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['b;d', '1.0;0.10', '2.0;0.30', '3.0;0.40', '~;0.20']
        self.assertEqual(cond, text.splitlines())
    def test_4602(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b:02.1f"], ["b|d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['b;d', '1.0;0.10', '2.0;0.30', '3.0;0.40', '~;0.20']
        self.assertEqual(cond, text.splitlines())
    def test_4608(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["#|b|d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['#;b;d', '1;3;0.40', '2;2;0.30', '3;~;0.20', '4;1;0.10']
        self.assertEqual(cond, text.splitlines())
    def test_4609(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["b|d|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['b;d;#', '1;0.10;4', '2;0.30;2', '3;0.40;1', '~;0.20;3']
        self.assertEqual(cond, text.splitlines())
    def test_4610(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["b>|d|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['b;d;#', '1;0.10;4', '2;0.30;2', '3;0.40;1']
        self.assertEqual(cond, text.splitlines())
    def test_4611(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["b>x|d|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['b;d;#', '1;0.10;4', '2;0.30;2', '3;0.40;1', '~;0.20;3']
        self.assertEqual(cond, text.splitlines())
    def test_4612(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["b>1|d|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['b;d;#', '2;0.30;2', '3;0.40;1']
        self.assertEqual(cond, text.splitlines())
    def test_4613(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["b>=2|d|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['b;d;#', '2;0.30;2', '3;0.40;1', ]
        self.assertEqual(cond, text.splitlines())
    def test_4614(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["b>2|d|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['b;d;#', '3;0.40;1']
        self.assertEqual(cond, text.splitlines())
    def test_4615(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["b<=2|d|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['b;d;#', '1;0.10;4', '2;0.30;2', '~;0.20;3']
        self.assertEqual(cond, text.splitlines())
    def test_4616(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["b<2|d|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['b;d;#', '1;0.10;4', '~;0.20;3']
        self.assertEqual(cond, text.splitlines())
    def test_4617(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["b==1|d|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['b;d;#', '1;0.10;4', ]
        self.assertEqual(cond, text.splitlines())
    def test_4618(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["b=~1|d|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['b;d;#', '1;0.10;4', ]
        self.assertEqual(cond, text.splitlines())
    def test_4619(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["b<>1|d|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['b;d;#', '2;0.30;2', '3;0.40;1', '~;0.20;3']
        self.assertEqual(cond, text.splitlines())
    def test_4620(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["b|d>|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['b;d;#', '1;0.10;4', '2;0.30;2', '3;0.40;1', '~;0.20;3']
        self.assertEqual(cond, text.splitlines())
    def test_4621(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["b|d>x|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['b;d;#', '1;0.10;4', '2;0.30;2', '3;0.40;1', '~;0.20;3']
        self.assertEqual(cond, text.splitlines())
    def test_4622(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["b|d>0.1|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['b;d;#', '2;0.30;2', '3;0.40;1', '~;0.20;3']
        self.assertEqual(cond, text.splitlines())
    def test_4623(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["b|d>=0.2|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['b;d;#', '2;0.30;2', '3;0.40;1', '~;0.20;3']
        self.assertEqual(cond, text.splitlines())
    def test_4624(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["b|d>0.2|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['b;d;#', '2;0.30;2', '3;0.40;1']
        self.assertEqual(cond, text.splitlines())
    def test_4625(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["b|d<=0.2|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['b;d;#', '1;0.10;4', '~;0.20;3']
        self.assertEqual(cond, text.splitlines())
    def test_4626(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["b|d<0.2|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['b;d;#', '1;0.10;4']
        self.assertEqual(cond, text.splitlines())
    def test_4627(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["b|d==0.1|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['b;d;#', '1;0.10;4']
        self.assertEqual(cond, text.splitlines())
    def test_4628(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["b|d=~0.1|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['b;d;#', '1;0.10;4']
        self.assertEqual(cond, text.splitlines())
    def test_4629(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["b|d<>0.1|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['b;d;#', '2;0.30;2', '3;0.40;1', '~;0.20;3']
        self.assertEqual(cond, text.splitlines())
    def test_4630(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["b|a>|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['b;a;#', '1;y;4', '2;y;2', '3;x;1']
        self.assertEqual(cond, text.splitlines())
    def test_4632(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["b|a>x|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['b;a;#', '1;y;4', '2;y;2', '~;~;3']
        self.assertEqual(cond, text.splitlines())
    def test_4633(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["b|a>=y|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['b;a;#', '1;y;4', '2;y;2', '~;~;3']
        self.assertEqual(cond, text.splitlines())
    def test_4634(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["b|a>x|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['b;a;#', '1;y;4', '2;y;2', '~;~;3']
        self.assertEqual(cond, text.splitlines())
    def test_4635(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["b|a<=y|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['b;a;#', '1;y;4', '2;y;2', '3;x;1', '~;~;3']
        self.assertEqual(cond, text.splitlines())
    def test_4636(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["b|a<y|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['b;a;#', '3;x;1', '~;~;3']
        self.assertEqual(cond, text.splitlines())
    def test_4637(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["b|a==y|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['b;a;#', '1;y;4', '2;y;2', '~;~;3']
        self.assertEqual(cond, text.splitlines())
    def test_4638(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["b|a=~y|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['b;a;#', '1;y;4', '2;y;2', '~;~;3']
        self.assertEqual(cond, text.splitlines())
    def test_4639(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["b|a<>y|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['b;a;#', '3;x;1', '~;~;3']
        self.assertEqual(cond, text.splitlines())
    def test_4640(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["b|c>|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['b;c;#', '1;~;4', '3;(yes);1', '~;(yes);3']
        self.assertEqual(cond, text.splitlines())
    def test_4641(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["b|c<>|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['b;c;#', '1;~;4', '2;(no);2', '3;(yes);1', '~;(yes);3']
        self.assertEqual(cond, text.splitlines())
    def test_4642(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["b|c>false|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['b;c;#', '1;~;4', '3;(yes);1', '~;(yes);3']
        self.assertEqual(cond, text.splitlines())
    def test_4643(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["b|c>=true|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['b;c;#', '1;~;4', '3;(yes);1', '~;(yes);3']
        self.assertEqual(cond, text.splitlines())
    def test_4644(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["b|c>true|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['b;c;#', '1;~;4']
        self.assertEqual(cond, text.splitlines())
    def test_4645(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["b|c<=true|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['b;c;#', '1;~;4', '2;(no);2', '3;(yes);1', '~;(yes);3']
        self.assertEqual(cond, text.splitlines())
    def test_4646(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["b|c<true|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['b;c;#', '1;~;4', '2;(no);2']
        self.assertEqual(cond, text.splitlines())
    def test_4647(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["b|c==true|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['b;c;#', '1;~;4', '3;(yes);1', '~;(yes);3']
        self.assertEqual(cond, text.splitlines())
    def test_4648(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["b|c=~true|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['b;c;#', '1;~;4', '3;(yes);1', '~;(yes);3']
        self.assertEqual(cond, text.splitlines())
    def test_4649(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["b|c<>true|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['b;c;#', '1;~;4', '2;(no);2', '3;(yes);1', '~;(yes);3']
        self.assertEqual(cond, text.splitlines())
    def test_4660(self) -> None:
        text = tabtotext.tabtoCSV(table33, ["a|b"], ["b|c>|#"])
        logg.debug("%s => %s", table33, text.splitlines())
        cond = ['b;c;#', '2;2021-12-30;2', '3;2021-12-31;1', '~;2021-12-31;3']
        self.assertEqual(cond, text.splitlines())
    def test_4661(self) -> None:
        text = tabtotext.tabtoCSV(table33, ["a|b"], ["b|c<>|#"])
        logg.debug("%s => %s", table33, text.splitlines())
        cond = ['b;c;#', '2;2021-12-30;2', '3;2021-12-31;1', '~;2021-12-31;3']
        self.assertEqual(cond, text.splitlines())
    def test_4662(self) -> None:
        text = tabtotext.tabtoCSV(table33, ["a|b"], ["b|c>2021-12-30|#"])
        logg.debug("%s => %s", table33, text.splitlines())
        cond = ['b;c;#', '3;2021-12-31;1', '~;2021-12-31;3']
        self.assertEqual(cond, text.splitlines())
    def test_4663(self) -> None:
        text = tabtotext.tabtoCSV(table33, ["a|b"], ["b|c>=2021-12-30|#"])
        logg.debug("%s => %s", table33, text.splitlines())
        cond = ['b;c;#', '2;2021-12-30;2', '3;2021-12-31;1', '~;2021-12-31;3']
        self.assertEqual(cond, text.splitlines())
    def test_4664(self) -> None:
        text = tabtotext.tabtoCSV(table33, ["a|b"], ["b|c>2021-12-31|#"])
        logg.debug("%s => %s", table33, text.splitlines())
        cond = ['b;c;#']
        self.assertEqual(cond, text.splitlines())
    def test_4665(self) -> None:
        text = tabtotext.tabtoCSV(table33, ["a|b"], ["b|c<=2021-12-31|#"])
        logg.debug("%s => %s", table33, text.splitlines())
        cond = ['b;c;#', '2;2021-12-30;2', '3;2021-12-31;1', '~;2021-12-31;3']
        self.assertEqual(cond, text.splitlines())
    def test_4666(self) -> None:
        text = tabtotext.tabtoCSV(table33, ["a|b"], ["b|c<2021-12-31|#"])
        logg.debug("%s => %s", table33, text.splitlines())
        cond = ['b;c;#', '2;2021-12-30;2']
        self.assertEqual(cond, text.splitlines())
    def test_4667(self) -> None:
        text = tabtotext.tabtoCSV(table33, ["a|b"], ["b|c==2021-12-31|#"])
        logg.debug("%s => %s", table33, text.splitlines())
        cond = ['b;c;#', '3;2021-12-31;1', '~;2021-12-31;3']
        self.assertEqual(cond, text.splitlines())
    def test_4668(self) -> None:
        text = tabtotext.tabtoCSV(table33, ["a|b"], ["b|c=~2021-12-31|#"])
        logg.debug("%s => %s", table33, text.splitlines())
        cond = ['b;c;#', '3;2021-12-31;1', '~;2021-12-31;3']
        self.assertEqual(cond, text.splitlines())
    def test_4669(self) -> None:
        text = tabtotext.tabtoCSV(table33, ["a|b"], ["b|c<>2021-12-31|#"])
        logg.debug("%s => %s", table33, text.splitlines())
        cond = ['b;c;#', '2;2021-12-30;2']
        self.assertEqual(cond, text.splitlines())
    def test_4702(self) -> None:
        text = tabtotext.tabtoCSV(table02, ["a|b"], ["{a}+{b}"])
        logg.debug("%s => %s", table02, text.splitlines())
        cond = ['a b', 'x+0', '~+2']
        self.assertEqual(cond, text.splitlines())
    def test_4703(self) -> None:
        text = tabtotext.tabtoCSV(table33, ["a|b"], ["{a}+{b} = {c}"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['a b c', 'x+3 = 2021-12-31', 'y+2 = 2021-12-30', '~+~ = 2021-12-31']
        self.assertEqual(cond, text.splitlines())
    def test_4704(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["{a}+{b} = {c}"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['a b c', 'x+3 = (yes)', 'y+1 = ~', 'y+2 = (no)', '~+~ = (yes)']
        self.assertEqual(cond, text.splitlines())
    def test_4705(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["{a}+{b} = {c}", "d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['a b c;d',
                'x+3 = (yes);0.40',
                'y+1 = ~;0.10',
                'y+2 = (no);0.30',
                '~+~ = (yes);0.20']
        self.assertEqual(cond, text.splitlines())
    def test_4706(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["d", "{a}+{b} = {c}"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['d;a b c', '0.10;y+1 = ~', '0.20;~+~ = (yes)',
                '0.30;y+2 = (no)', '0.40;x+3 = (yes)']
        self.assertEqual(cond, text.splitlines())
    def test_4712(self) -> None:
        text = tabtotext.tabtoCSV(table02, ["a|b"], ["{a}+{b}@info"])
        logg.debug("%s => %s", table02, text.splitlines())
        cond = ['info', 'x+0', '~+2']
        self.assertEqual(cond, text.splitlines())
    def test_4713(self) -> None:
        text = tabtotext.tabtoCSV(table33, ["a|b"], ["{a}+{b} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['info', 'x+3 = 2021-12-31', 'y+2 = 2021-12-30', '~+~ = 2021-12-31']
        self.assertEqual(cond, text.splitlines())
    def test_4714(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["{a}+{b} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['info', 'x+3 = (yes)', 'y+1 = ~', 'y+2 = (no)', '~+~ = (yes)']
        self.assertEqual(cond, text.splitlines())
    def test_4715(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["{a}+{b} = {c}@info", "d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['info;d',
                'x+3 = (yes);0.40',
                'y+1 = ~;0.10',
                'y+2 = (no);0.30',
                '~+~ = (yes);0.20']
        self.assertEqual(cond, text.splitlines())
    def test_4716(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a|b"], ["d", "{a}+{b} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['d;info', '0.10;y+1 = ~', '0.20;~+~ = (yes)',
                '0.30;y+2 = (no)', '0.40;x+3 = (yes)']
        self.assertEqual(cond, text.splitlines())
    def test_4722(self) -> None:
        text = tabtotext.tabtoCSV(table02, ["a@x"], ["{a}+{b}@info"])
        logg.debug("%s => %s", table02, text.splitlines())
        cond = ['info', 'x+0', '~+2']
        self.assertEqual(cond, text.splitlines())
    def test_4723(self) -> None:
        text = tabtotext.tabtoCSV(table33, ["a@x"], ["{a}+{b} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['info', 'x+3 = 2021-12-31', 'y+2 = 2021-12-30', '~+~ = 2021-12-31']
        self.assertEqual(cond, text.splitlines())
    def test_4724(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a@x"], ["{a}+{b} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['info', 'x+3 = (yes)', 'y+1 = ~', 'y+2 = (no)', '~+~ = (yes)']
        self.assertEqual(cond, text.splitlines())
    def test_4725(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a@x"], ["{a}+{b} = {c}@info", "d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['info;d',
                'x+3 = (yes);0.40',
                'y+1 = ~;0.10',
                'y+2 = (no);0.30',
                '~+~ = (yes);0.20']
        self.assertEqual(cond, text.splitlines())
    def test_4726(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a@x"], ["d", "{a}+{b} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['d;info', '0.10;y+1 = ~', '0.20;~+~ = (yes)',
                '0.30;y+2 = (no)', '0.40;x+3 = (yes)']
        self.assertEqual(cond, text.splitlines())
    def test_4732(self) -> None:
        text = tabtotext.tabtoCSV(table02, ["a@x"], ["{x}+{b}@info"])
        logg.debug("%s => %s", table02, text.splitlines())
        cond = ['info', 'x+0', '~+2']
        self.assertEqual(cond, text.splitlines())
    def test_4733(self) -> None:
        text = tabtotext.tabtoCSV(table33, ["a@x"], ["{x}+{b} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['info', 'x+3 = 2021-12-31', 'y+2 = 2021-12-30', '~+~ = 2021-12-31']
        self.assertEqual(cond, text.splitlines())
    def test_4734(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a@x"], ["{x}+{b} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['info', 'x+3 = (yes)', 'y+1 = ~', 'y+2 = (no)', '~+~ = (yes)']
        self.assertEqual(cond, text.splitlines())
    def test_4735(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a@x"], ["{x}+{b} = {c}@info", "d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['info;d',
                'x+3 = (yes);0.40',
                'y+1 = ~;0.10',
                'y+2 = (no);0.30',
                '~+~ = (yes);0.20']
        self.assertEqual(cond, text.splitlines())
    def test_4736(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a@x"], ["d", "{x}+{b} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['d;info', '0.10;y+1 = ~', '0.20;~+~ = (yes)',
                '0.30;y+2 = (no)', '0.40;x+3 = (yes)']
        self.assertEqual(cond, text.splitlines())
    def test_4742(self) -> None:
        text = tabtotext.tabtoCSV(table02, ["a@x|b@y"], ["{x}+{y}@info"])
        logg.debug("%s => %s", table02, text.splitlines())
        cond = ['info', 'x+0', '~+2']
        self.assertEqual(cond, text.splitlines())
    def test_4743(self) -> None:
        text = tabtotext.tabtoCSV(table33, ["a@x|b@y"], ["{x}+{y} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['info', 'x+3 = 2021-12-31', 'y+2 = 2021-12-30', '~+~ = 2021-12-31']
        self.assertEqual(cond, text.splitlines())
    def test_4744(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a@x|b@y"], ["{x}+{y} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['info', 'x+3 = (yes)', 'y+1 = ~', 'y+2 = (no)', '~+~ = (yes)']
        self.assertEqual(cond, text.splitlines())
    def test_4745(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a@x|b@y"], ["{x}+{y} = {c}@info", "d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['info;d',
                'x+3 = (yes);0.40',
                'y+1 = ~;0.10',
                'y+2 = (no);0.30',
                '~+~ = (yes);0.20']
        self.assertEqual(cond, text.splitlines())
    def test_4746(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a@x|b@y"], ["d", "{x}+{y} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['d;info', '0.10;y+1 = ~', '0.20;~+~ = (yes)',
                '0.30;y+2 = (no)', '0.40;x+3 = (yes)']
        self.assertEqual(cond, text.splitlines())
    def test_4752(self) -> None:
        text = tabtotext.tabtoCSV(table02, ["a@x|b@y"], ["x@info"])
        logg.debug("%s => %s", table02, text.splitlines())
        cond = ['info', '~', 'x']
        self.assertEqual(cond, text.splitlines())
    def test_4753(self) -> None:
        text = tabtotext.tabtoCSV(table33, ["a@x|b@y"], ["x@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['info', '~', 'x', 'y']
        self.assertEqual(cond, text.splitlines())
    def test_4754(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a@x|b@y"], ["x@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['info', '~', 'x', 'y', 'y']
        self.assertEqual(cond, text.splitlines())
    def test_4755(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a@x|b@y"], ["x@info", "d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['info;d', '~;0.20', 'x;0.40', 'y;0.10', 'y;0.30']
        self.assertEqual(cond, text.splitlines())
    def test_4756(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a@x|b@y"], ["d", "x@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['d;info', '0.10;y', '0.20;~', '0.30;y', '0.40;x']
        self.assertEqual(cond, text.splitlines())
    def test_4762(self) -> None:
        text = tabtotext.tabtoCSV(table02, ["a@x|b@y"], ["x@info|y@mm"])
        logg.debug("%s => %s", table02, text.splitlines())
        cond = ['info;mm', '~;2', 'x;0']
        self.assertEqual(cond, text.splitlines())
    def test_4763(self) -> None:
        text = tabtotext.tabtoCSV(table33, ["a@x|b@y"], ["x@info|y@mm"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['info;mm', '~;~', 'x;3', 'y;2']
        self.assertEqual(cond, text.splitlines())
    def test_4764(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a@x|b@y"], ["x@info|y@mm"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['info;mm', '~;~', 'x;3', 'y;1', 'y;2']
        self.assertEqual(cond, text.splitlines())
    def test_4765(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a@x|b@y"], ["x@info|y@mm", "d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['info;mm;d', '~;~;0.20', 'x;3;0.40', 'y;1;0.10', 'y;2;0.30']
        self.assertEqual(cond, text.splitlines())
    def test_4766(self) -> None:
        text = tabtotext.tabtoCSV(table44, ["a@x|b@y"], ["d", "x@info|y@mm"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['d;info;mm', '0.10;y;1', '0.20;~;~', '0.30;y;2', '0.40;x;3']
        self.assertEqual(cond, text.splitlines())
    def test_4911(self) -> None:
        item1 = Item2("x", 2)
        item2 = Item2("y", 3)
        itemlist: DataList = [item1, item2]
        text = tabtotext.tabToFMTx("csv", itemlist)
        logg.debug("%s => %s", test004, text)
        cond = ['a;b', 'x;2', 'y;3']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        want = [{'a': 'x', 'b': 2}, {'a': 'y', 'b': 3}]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_4920(self) -> None:
        text = tabtotext.tabtotext(table01, [], ["@csv"])
        logg.debug("%s => %s", table01, text)
        want = table01N
        cond = ['a;b', 'x y;~', '~;1']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4921(self) -> None:
        text = tabtotext.tabtotext(table02, [], ["@csv"])
        logg.debug("%s => %s", table02, text)
        want = table02N
        cond = ['a;b', 'x;0', '~;2']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4922(self) -> None:
        text = tabtotext.tabtotext(table22, [], ["@csv"])
        logg.debug("%s => %s", table22, text)
        want = table22
        cond = ['a;b', 'x;3', 'y;2']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4923(self) -> None:
        text = tabtotext.tabtotext(table33, [], ["@csv"])
        logg.debug("%s => %s", table33, text)
        want = table33Q
        cond = ['a;b;c', 'x;3;2021-12-31', 'y;2;2021-12-30', '~;~;2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4924(self) -> None:
        text = tabtotext.tabtotext(table44, [], ["@csv"])
        logg.debug("%s => %s", table44, text)
        want = table44N
        cond = ['a;b;c;d', 'x;3;(yes);0.40', 'y;2;(no);0.30', '~;~;(yes);0.20', 'y;1;~;0.10']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(want, back)
    def test_4930(self) -> None:
        text = tabtotext.tabtotext(table01, [], ["@list"])
        logg.debug("%s => %s", table01, text)
        want = table01N
        cond = ['x y;~', '~;1']
        self.assertEqual(cond, text.splitlines())
    def test_4931(self) -> None:
        text = tabtotext.tabtotext(table02, [], ["@list"])
        logg.debug("%s => %s", table02, text)
        want = table02N
        cond = ['x;0', '~;2']
        self.assertEqual(cond, text.splitlines())
    def test_4932(self) -> None:
        text = tabtotext.tabtotext(table22, [], ["@list"])
        logg.debug("%s => %s", table22, text)
        want = table22
        cond = ['x;3', 'y;2']
        self.assertEqual(cond, text.splitlines())
    def test_4933(self) -> None:
        text = tabtotext.tabtotext(table33, [], ["@list"])
        logg.debug("%s => %s", table33, text)
        want = table33Q
        cond = ['x;3;2021-12-31', 'y;2;2021-12-30', '~;~;2021-12-31']
        self.assertEqual(cond, text.splitlines())
    def test_4934(self) -> None:
        text = tabtotext.tabtotext(table44, [], ["@list"])
        logg.debug("%s => %s", table44, text)
        want = table44N
        cond = ['x;3;(yes);0.40', 'y;2;(no);0.30', '~;~;(yes);0.20', 'y;1;~;0.10']
        self.assertEqual(cond, text.splitlines())
    def test_4940(self) -> None:
        text = tabtotext.tabtotext(table01, [], ["@csv", "@noheaders"])
        logg.debug("%s => %s", table01, text)
        want = table01N
        cond = ['x y;~', '~;1']
        self.assertEqual(cond, text.splitlines())
    def test_4941(self) -> None:
        text = tabtotext.tabtotext(table02, [], ["@csv", "@noheaders"])
        logg.debug("%s => %s", table02, text)
        want = table02N
        cond = ['x;0', '~;2']
        self.assertEqual(cond, text.splitlines())
    def test_4942(self) -> None:
        text = tabtotext.tabtotext(table22, [], ["@csv", "@noheaders"])
        logg.debug("%s => %s", table22, text)
        want = table22
        cond = ['x;3', 'y;2']
        self.assertEqual(cond, text.splitlines())
    def test_4943(self) -> None:
        text = tabtotext.tabtotext(table33, [], ["@csv", "@noheaders"])
        logg.debug("%s => %s", table33, text)
        want = table33Q
        cond = ['x;3;2021-12-31', 'y;2;2021-12-30', '~;~;2021-12-31']
        self.assertEqual(cond, text.splitlines())
    def test_4944(self) -> None:
        text = tabtotext.tabtotext(table44, [], ["@csv", "@noheaders"])
        logg.debug("%s => %s", table44, text)
        want = table44N
        cond = ['x;3;(yes);0.40', 'y;2;(no);0.30', '~;~;(yes);0.20', 'y;1;~;0.10']
        self.assertEqual(cond, text.splitlines())
    def test_4950(self) -> None:
        text = tabtotext.tabtotext(table01, [], ["@data"])
        logg.debug("%s => %s", table01, text)
        want = table01N
        cond = ['x y\t~', '~\t1']
        self.assertEqual(cond, text.splitlines())
    def test_4951(self) -> None:
        text = tabtotext.tabtotext(table02, [], ["@data"])
        logg.debug("%s => %s", table02, text)
        want = table02N
        cond = ['x\t0', '~\t2']
        self.assertEqual(cond, text.splitlines())
    def test_4952(self) -> None:
        text = tabtotext.tabtotext(table22, [], ["@data"])
        logg.debug("%s => %s", table22, text)
        want = table22
        cond = ['x\t3', 'y\t2']
        self.assertEqual(cond, text.splitlines())
    def test_4953(self) -> None:
        text = tabtotext.tabtotext(table33, [], ["@data"])
        logg.debug("%s => %s", table33, text)
        want = table33Q
        cond = ['x\t3\t2021-12-31', 'y\t2\t2021-12-30', '~\t~\t2021-12-31']
        self.assertEqual(cond, text.splitlines())
    def test_4954(self) -> None:
        text = tabtotext.tabtotext(table44, [], ["@data"])
        logg.debug("%s => %s", table44, text)
        want = table44N
        cond = ['x\t3\t(yes)\t0.40', 'y\t2\t(no)\t0.30', '~\t~\t(yes)\t0.20', 'y\t1\t~\t0.10']
        self.assertEqual(cond, text.splitlines())
    def test_4960(self) -> None:
        text = tabtotext.tabtotext(table01, [], ["@xls"])
        logg.debug("%s => %s", table01, text)
        want = table01N
        cond = ['a,b', 'x y,~', '~,1']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text, tab=",")
        self.assertEqual(want, back)
    def test_4961(self) -> None:
        text = tabtotext.tabtotext(table02, [], ["@xls"])
        logg.debug("%s => %s", table02, text)
        want = table02N
        cond = ['a,b', 'x,0', '~,2']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text, tab=",")
        self.assertEqual(want, back)
    def test_4962(self) -> None:
        text = tabtotext.tabtotext(table22, [], ["@xls"])
        logg.debug("%s => %s", table22, text)
        want = table22
        cond = ['a,b', 'x,3', 'y,2']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text, tab=",")
        self.assertEqual(want, back)
    def test_4963(self) -> None:
        text = tabtotext.tabtotext(table33, [], ["@xls"])
        logg.debug("%s => %s", table33, text)
        want = table33Q
        cond = ['a,b,c', 'x,3,2021-12-31', 'y,2,2021-12-30', '~,~,2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text, tab=",")
        self.assertEqual(want, back)
    def test_4964(self) -> None:
        text = tabtotext.tabtotext(table44, [], ["@xls"])
        logg.debug("%s => %s", table44, text)
        want = table44N
        cond = ['a,b,c,d', 'x,3,(yes),0.40', 'y,2,(no),0.30', '~,~,(yes),0.20', 'y,1,~,0.10']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text, tab=",")
        self.assertEqual(want, back)

    def test_5000(self) -> None:
        want = LIST
        back = json.loads("[]")
        self.assertEqual(want, back)
    def test_5001(self) -> None:
        want = JSONLIST + [{}]
        back = json.loads("[{}]")
        self.assertEqual(want, back)
    def test_5002(self) -> None:
        try:
            want = JSONLIST + [{}]
            back = json.loads("[{},]")
            self.assertEqual(want, back)
        except json.decoder.JSONDecodeError as e:
            self.assertIn("Expecting value", str(e))
    # note that json can not encode comments
    def test_5003(self) -> None:
        text = tabtotext.tabToJSON(test003)
        logg.debug("%s => %s", test003, text)
        want = test003
        cond = ['[', '', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5004(self) -> None:
        text = tabtotext.tabToJSON(test004)
        logg.debug("%s => %s", test004, text)
        want = test004
        cond = ['[', ' {}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5005(self) -> None:
        text = tabtotext.tabToJSON(test005)
        logg.debug("%s => %s", test005, text)
        want = test005
        cond = ['[', ' {"a": "x"}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5006(self) -> None:
        text = tabtotext.tabToJSON(test006)
        logg.debug("%s => %s", test006, text)
        want = test006
        cond = ['[', ' {"a": "x", "b": "y"}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5007(self) -> None:
        text = tabtotext.tabToJSON(test007)
        logg.debug("%s => %s", test007, text)
        want = test007
        cond = ['[', ' {"a": "x", "b": "y"},', ' {"b": "v"}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5008(self) -> None:
        text = tabtotext.tabToJSON(test008)
        logg.debug("%s => %s", test008, text)
        want = test008
        cond = ['[', ' {"a": "x"},', ' {"b": "v"}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5009(self) -> None:
        text = tabtotext.tabToJSON(test009)
        logg.debug("%s => %s", test009, text)
        want = test009
        cond = ['[', ' {},', ' {"b": "v"}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5011(self) -> None:
        text = tabtotext.tabToJSON(test011)
        logg.debug("%s => %s", test011, text)
        want = test011
        cond = ['[', ' {"b": null}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5012(self) -> None:
        text = tabtotext.tabToJSON(test012)
        logg.debug("%s => %s", test012, text)
        want = test012
        cond = ['[', ' {"b": false}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5013(self) -> None:
        text = tabtotext.tabToJSON(test013)
        logg.debug("%s => %s", test013, text)
        want = test013
        cond = ['[', ' {"b": true}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5014(self) -> None:
        text = tabtotext.tabToJSON(test014)
        logg.debug("%s => %s", test014, text)
        want = test014
        cond = ['[', ' {"b": ""}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5015(self) -> None:
        text = tabtotext.tabToJSON(test015)
        logg.debug("%s => %s", test015, text)
        want = test015
        cond = ['[', ' {"b": "5678"}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5016(self) -> None:
        text = tabtotext.tabToJSON(test016)
        logg.debug("%s => %s", test016, text)
        want = test016
        cond = ['[', ' {"b": 123}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5017(self) -> None:
        text = tabtotext.tabToJSON(test017)
        logg.debug("%s => %s", test017, text)
        want = test017
        cond = ['[', ' {"b": 123.40}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5018(self) -> None:
        text = tabtotext.tabToJSON(test018)
        logg.debug("%s => %s", test018, text)
        want = test018
        cond = ['[', ' {"b": "2021-12-31"}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5019(self) -> None:
        text = tabtotext.tabToJSON(test019)
        logg.debug("%s => %s", test019, text)
        want = test018  # test019
        cond = ['[', ' {"b": "2021-12-31"}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5021(self) -> None:
        """ legend is ignored for JSON output """
        text = tabtotext.tabToJSON(test011, legend="a result")
        logg.debug("%s => %s", test011, text)
        want = test011
        cond = ['[', ' {"b": null}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5031(self) -> None:
        """ legend is ignored for JSON output """
        text = tabtotext.tabToJSON(test011, legend=["a result", "was found"])
        logg.debug("%s => %s", test011, text)
        want = test011
        cond = ['[', ' {"b": null}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5044(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        text = tabtotext.tabToJSON(itemlist, sorts=['b', 'a'])
        logg.debug("%s => %s", test004, text)
        cond = ['[', ' {"b": 1, "a": "y"},', ' {"b": 2, "a": "x"}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        want = [{'a': 'y', 'b': 1}, {'a': 'x', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_5045(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}, {'c': 'h'}]
        text = tabtotext.tabToJSON(itemlist, sorts=['b', 'a'])
        logg.debug("%s => %s", test004, text)
        cond = ['[', ' {"b": 1, "a": "y"},', ' {"b": 2, "a": "x"},', ' {"c": "h"}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        want = [{'a': 'y', 'b': 1}, {'a': 'x', 'b': 2}, {'c': "h"}, ]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_5046(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}, {'c': 'h'}]
        text = tabtotext.tabToJSON(itemlist, sorts=['b', 'a'], reorder=['a', 'b'])
        logg.debug("%s => %s", test004, text)
        cond = ['[', ' {"a": "y", "b": 1},', ' {"a": "x", "b": 2},', ' {"c": "h"}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        want = [{'a': 'y', 'b': 1}, {'a': 'x', 'b': 2}, {'c': "h"}, ]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_5051(self) -> None:
        text = tabtotext.tabToJSONx(data011)
        logg.debug("%s => %s", data011, text)
        want = test011
        cond = ['[', ' {"b": null}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5052(self) -> None:
        text = tabtotext.tabToJSONx(data012)
        logg.debug("%s => %s", data012, text)
        want = test012
        cond = ['[', ' {"b": false}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5053(self) -> None:
        text = tabtotext.tabToJSONx(data013)
        logg.debug("%s => %s", data013, text)
        want = test013
        cond = ['[', ' {"b": true}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5054(self) -> None:
        text = tabtotext.tabToJSONx(data014)
        logg.debug("%s => %s", data014, text)
        want = test014
        cond = ['[', ' {"b": ""}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5055(self) -> None:
        text = tabtotext.tabToJSONx(data015)
        logg.debug("%s => %s", data015, text)
        want = test015
        cond = ['[', ' {"b": "5678"}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5056(self) -> None:
        text = tabtotext.tabToJSONx(data016)
        logg.debug("%s => %s", data016, text)
        want = test016
        cond = ['[', ' {"b": 123}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5057(self) -> None:
        text = tabtotext.tabToJSONx(data017)
        logg.debug("%s => %s", data017, text)
        want = test017
        cond = ['[', ' {"b": 123.40}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5058(self) -> None:
        text = tabtotext.tabToJSONx(data018)
        logg.debug("%s => %s", data018, text)
        want = test018
        cond = ['[', ' {"b": "2021-12-31"}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5059(self) -> None:
        text = tabtotext.tabToJSONx(data019)
        logg.debug("%s => %s", data019, text)
        want = test018  # test019
        cond = ['[', ' {"b": "2021-12-31"}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5103(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test003, defaultformat="json")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test003, text)
        want = test003
        cond = ['[', '', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5104(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test004, defaultformat="json")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        want = test004
        cond = ['[', ' {}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5105(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test005, defaultformat="json")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test005, text)
        want = test005
        cond = ['[', ' {"a": "x"}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5106(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test006, defaultformat="json")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test006, text)
        want = test006
        cond = ['[', ' {"a": "x", "b": "y"}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5107(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test007, defaultformat="json")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test007, text)
        want = test007
        cond = ['[', ' {"a": "x", "b": "y"},', ' {"b": "v"}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5108(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test008, defaultformat="json")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test008, text)
        want = test008
        cond = ['[', ' {"a": "x"},', ' {"b": "v"}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5109(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test009, defaultformat="json")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test009, text)
        want = test009
        cond = ['[', ' {},', ' {"b": "v"}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5111(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test011, defaultformat="json")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test011, text)
        want = test011
        cond = ['[', ' {"b": null}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5112(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test012, defaultformat="json")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test012, text)
        want = test012
        cond = ['[', ' {"b": false}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5113(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test013, defaultformat="json")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test013, text)
        want = test013
        cond = ['[', ' {"b": true}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5114(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test014, defaultformat="json")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test014, text)
        want = test014
        cond = ['[', ' {"b": ""}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5115(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test015, defaultformat="json")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test015, text)
        want = test015
        cond = ['[', ' {"b": "5678"}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5116(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test016, defaultformat="json")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test016, text)
        want = test016
        cond = ['[', ' {"b": 123}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5117(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test017, defaultformat="json")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test017, text)
        want = test017
        cond = ['[', ' {"b": 123.40}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5118(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test018, defaultformat="json")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test018, text)
        want = test018
        cond = ['[', ' {"b": "2021-12-31"}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5119(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test019, defaultformat="json")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test019, text)
        want = test018  # test019
        cond = ['[', ' {"b": "2021-12-31"}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5131(self) -> None:
        """ legend is ignored for JSON output """
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test011, legend=["a result", "was found"], defaultformat="json")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test011, text)
        want = test011
        cond = ['[', ' {"b": null}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5143(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        out = StringIO()
        res = tabtotext.print_tabtotext(out, itemlist, ['b', 'a'], defaultformat="json")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['[', ' {"b": 2, "a": "x"},', ' {"b": 1, "a": "y"}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        want = [{'a': 'x', 'b': 2}, {'a': 'y', 'b': 1}, ]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_5144(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        out = StringIO()
        res = tabtotext.print_tabtotext(out, itemlist, ['b@1', 'a'], defaultformat="json")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['[', ' {"b": 1, "a": "y"},', ' {"b": 2, "a": "x"}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        want = [{'a': 'y', 'b': 1}, {'a': 'x', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_5145(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}, {'c': 'h'}]
        out = StringIO()
        res = tabtotext.print_tabtotext(out, itemlist, ['b@1', 'a'], defaultformat="json")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['[', ' {"b": 1, "a": "y"},', ' {"b": 2, "a": "x"},', ' {"c": "h"}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        want = [{'a': 'y', 'b': 1}, {'a': 'x', 'b': 2}, {'c': "h"}, ]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_5146(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}, {'c': 'h'}]
        out = StringIO()
        res = tabtotext.print_tabtotext(out, itemlist, ['a@:2', 'b@:1'], defaultformat="json")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['[', ' {"a": "y", "b": 1},', ' {"a": "x", "b": 2},', ' {"c": "h"}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        want = [{'a': 'y', 'b': 1}, {'a': 'x', 'b': 2}, {'c': "h"}, ]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_5149(self) -> None:
        """ jsn is more compact that json """
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}, {'c': 'h'}]
        out = StringIO()
        res = tabtotext.print_tabtotext(out, itemlist, ['a@:2', 'b@:1'], defaultformat="jsn")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        # = ['[', ' {"a": "y", "b": 1},', ' {"a": "x", "b": 2},', ' {"c": "h"}', ']']
        cond = ['[', ' {"a":"y","b":1},', ' {"a":"x","b":2},', ' {"c":"h"}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        want = [{'a': 'y', 'b': 1}, {'a': 'x', 'b': 2}, {'c': "h"}, ]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)

    def test_5200(self) -> None:
        try:
            import yaml  # type: ignore[import]
            cond = ['data:', '- a: "x"', '- b: "v"']
            text = "\n".join(cond)
            back = yaml.safe_load(text)
            logg.debug("%s => %s", text, back)
            want = {'data': test008}
            self.assertEqual(want, back)
        except ImportError as e:
            logg.info("yaml %s - %s", "ImportError", e)
            raise unittest.SkipTest("no yaml lib")
    def test_5201(self) -> None:
        try:
            import yaml  # type: ignore[import]
            cond = ['data:', '- a: "x"', '  b: null', '- a: null', '  b: "v"']
            text = "\n".join(cond)
            back = yaml.safe_load(text)
            logg.debug("%s => %s", text, back)
            want = {'data': test008Q}
            self.assertEqual(want, back)
        except ImportError as e:
            logg.info("yaml %s - %s", "ImportError", e)
            raise unittest.SkipTest("no yaml lib")
    def test_5202(self) -> None:
        try:
            import yaml  # type: ignore[import]
            cond = ['data:', '- a: "x"', '  b: "y"']
            text = "\n".join(cond)
            back = yaml.safe_load(text)
            logg.debug("%s => %s", text, back)
            want = {'data': test006}
            self.assertEqual(want, back)
        except ImportError as e:
            logg.info("yaml %s - %s", "ImportError", e)
            raise unittest.SkipTest("no yaml lib")
    def test_5204(self) -> None:
        try:
            import yaml  # type: ignore[import]
            cond = ['# some comment', 'data:', '- b: false', ]
            text = "\n".join(cond)
            back = yaml.safe_load(text)
            logg.debug("%s => %s", text, back)
            want = {'data': test012}
            self.assertEqual(want, back)
        except ImportError as e:
            logg.info("yaml %s - %s", "ImportError", e)
            raise unittest.SkipTest("no yaml lib")
    def test_5205(self) -> None:
        try:
            import toml  # type: ignore[import]
            cond = ['[[data]]', 'a = "x"', 'b = "y"']
            text = "\n".join(cond)
            back = toml.loads(text)
            logg.debug("%s => %s", text, back)
            want = {'data': test006}
            self.assertEqual(want, back)
        except ImportError as e:
            logg.info("toml %s - %s", "ImportError", e)
            raise unittest.SkipTest("no toml lib")
    def test_5206(self) -> None:
        try:
            import toml  # type: ignore[import]
            cond = ['[[data]]', 'a = "x"', 'b = null', '[[data]]', 'a = null', '  b = "v"']
            text = "\n".join(cond)
            back = toml.loads(text)
            logg.debug("%s => %s", text, back)
            want = {'data': test008Q}
            self.assertEqual(want, back)
        except ImportError as e:
            logg.info("toml %s - %s", "ImportError", e)
            raise unittest.SkipTest("no toml lib")
        except ValueError as e:
            logg.debug("toml %s - %s", "ValueError", e)
            raise unittest.SkipTest("toml can not encode null")
    def test_5207(self) -> None:
        try:
            import toml  # type: ignore[import]
            cond = ['[[data]]', 'b = 2021-12-31']
            text = "\n".join(cond)
            back = toml.loads(text)
            logg.debug("%s => %s", text, back)
            want = {'data': test018}
            self.assertEqual(want, back)
        except ImportError as e:
            logg.info("toml %s - %s", "ImportError", e)
            raise unittest.SkipTest("no toml lib")
    def test_5208(self) -> None:
        try:
            import toml
            cond = ['[[data]]', 'b = 2021-12-31T23:34:45']
            text = "\n".join(cond)
            back = toml.loads(text)
            logg.debug("%s => %s", text, back)
            want = {'data': test019}
            self.assertEqual(want, back)
        except ImportError as e:
            logg.info("toml %s - %s", "ImportError", e)
            raise unittest.SkipTest("no toml lib")
    def test_5209(self) -> None:
        try:
            import toml
            cond = ['# some comment', '[[data]]', 'b = false']
            text = "\n".join(cond)
            back = toml.loads(text)
            logg.debug("%s => %s", text, back)
            want = {'data': test012}
            self.assertEqual(want, back)
        except ImportError as e:
            logg.info("toml %s - %s", "ImportError", e)
            raise unittest.SkipTest("no toml lib")
    def test_5211(self) -> None:
        text = tabtotext.tabToYAML(test011)
        logg.debug("%s => %s", test011, text)
        want = test011
        cond = ['data:', '- b: null']
        self.assertEqual(cond, text.splitlines())
        back = loadYAML(text)
        self.assertEqual(want, back)
    def test_5212(self) -> None:
        text = tabtotext.tabToYAML(test012)
        logg.debug("%s => %s", test012, text)
        want = test012
        cond = ['data:', '- b: false']
        self.assertEqual(cond, text.splitlines())
        back = loadYAML(text)
        self.assertEqual(want, back)
    def test_5213(self) -> None:
        text = tabtotext.tabToYAML(test013)
        logg.debug("%s => %s", test013, text)
        want = test013
        cond = ['data:', '- b: true']
        self.assertEqual(cond, text.splitlines())
        back = loadYAML(text)
        self.assertEqual(want, back)
    def test_5214(self) -> None:
        text = tabtotext.tabToYAML(test014)
        logg.debug("%s => %s", test014, text)
        want = test014
        cond = ['data:', '- b: ""']
        self.assertEqual(cond, text.splitlines())
        back = loadYAML(text)
        self.assertEqual(want, back)
    def test_5215(self) -> None:
        text = tabtotext.tabToYAML(test015)
        logg.debug("%s => %s", test015, text)
        want = test015
        cond = ['data:', '- b: "5678"']
        self.assertEqual(cond, text.splitlines())
        back = loadYAML(text)
        self.assertEqual(want, back)
    def test_5216(self) -> None:
        text = tabtotext.tabToYAML(test016)
        logg.debug("%s => %s", test016, text)
        want = test016
        cond = ['data:', '- b: 123']
        self.assertEqual(cond, text.splitlines())
        back = loadYAML(text)
        self.assertEqual(want, back)
    def test_5217(self) -> None:
        text = tabtotext.tabToYAML(test017)
        logg.debug("%s => %s", test017, text)
        want = test017
        cond = ['data:', '- b: 123.40']
        self.assertEqual(cond, text.splitlines())
        back = loadYAML(text)
        self.assertEqual(want, back)
    def test_5218(self) -> None:
        text = tabtotext.tabToYAML(test018)
        logg.debug("%s => %s", test018, text)
        want = test018
        cond = ['data:', '- b: 2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadYAML(text)
        self.assertEqual(want, back)
    def test_5219(self) -> None:
        text = tabtotext.tabToYAML(test019)
        logg.debug("%s => %s", test019, text)
        want = test018  # test019
        cond = ['data:', '- b: 2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadYAML(text)
        self.assertEqual(want, back)
    def test_5221(self) -> None:
        text = tabtotext.tabToTOML(test011)
        logg.debug("%s => %s", test011, text)
        want = test011Q
        cond = ['[[data]]', '']  # toml can not encode null
        self.assertEqual(cond, text.splitlines())
        back = loadTOML(text)
        self.assertEqual(want, back)
    def test_5222(self) -> None:
        text = tabtotext.tabToTOML(test012)
        logg.debug("%s => %s", test012, text)
        want = test012
        cond = ['[[data]]', 'b = false']
        self.assertEqual(cond, text.splitlines())
        back = loadTOML(text)
        self.assertEqual(want, back)
    def test_5223(self) -> None:
        text = tabtotext.tabToTOML(test013)
        logg.debug("%s => %s", test013, text)
        want = test013
        cond = ['[[data]]', 'b = true']
        self.assertEqual(cond, text.splitlines())
        back = loadTOML(text)
        self.assertEqual(want, back)
    def test_5224(self) -> None:
        text = tabtotext.tabToTOML(test014)
        logg.debug("%s => %s", test014, text)
        want = test014
        cond = ['[[data]]', 'b = ""']
        self.assertEqual(cond, text.splitlines())
        back = loadTOML(text)
        self.assertEqual(want, back)
    def test_5225(self) -> None:
        text = tabtotext.tabToTOML(test015)
        logg.debug("%s => %s", test015, text)
        want = test015
        cond = ['[[data]]', 'b = "5678"']
        self.assertEqual(cond, text.splitlines())
        back = loadTOML(text)
        self.assertEqual(want, back)
    def test_5226(self) -> None:
        text = tabtotext.tabToTOML(test016)
        logg.debug("%s => %s", test016, text)
        want = test016
        cond = ['[[data]]', 'b = 123']
        self.assertEqual(cond, text.splitlines())
        back = loadTOML(text)
        self.assertEqual(want, back)
    def test_5227(self) -> None:
        text = tabtotext.tabToTOML(test017)
        logg.debug("%s => %s", test017, text)
        want = test017
        cond = ['[[data]]', 'b = 123.40']
        self.assertEqual(cond, text.splitlines())
        back = loadTOML(text)
        self.assertEqual(want, back)
    def test_5228(self) -> None:
        text = tabtotext.tabToTOML(test018)
        logg.debug("%s => %s", test018, text)
        want = test018
        cond = ['[[data]]', 'b = 2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadTOML(text)
        self.assertEqual(want, back)
    def test_5229(self) -> None:
        text = tabtotext.tabToTOML(test019)
        logg.debug("%s => %s", test019, text)
        want = test018  # test019
        cond = ['[[data]]', 'b = 2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadTOML(text)
        self.assertEqual(want, back)

    def test_5241(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 3}]
        text = tabtotext.tabToYAML(itemlist)
        logg.debug("%s => %s", test004, text)
        cond = ['data:', '- a: "x"', '  b: 2', '- a: "y"', '  b: 3', ]
        self.assertEqual(cond, text.splitlines())
        back = loadYAML(text)
        want = [{'a': 'x', 'b': 2}, {'a': 'y', 'b': 3}]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_5242(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 3}]
        text = tabtotext.tabToTOMLx(itemlist)
        logg.debug("%s => %s", test004, text)
        cond = ['[[data]]', 'a = "x"', 'b = 2', '[[data]]', 'a = "y"', 'b = 3', ]
        self.assertEqual(cond, text.splitlines())
        back = loadTOML(text)
        want = [{'a': 'x', 'b': 2}, {'a': 'y', 'b': 3}]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_5243(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        text = tabtotext.tabToYAML(itemlist, sorts=['b', 'a'])
        logg.debug("%s => %s", test004, text)
        cond = ['data:', '- b: 1', '  a: "y"', '- b: 2', '  a: "x"', ]
        self.assertEqual(cond, text.splitlines())
        back = loadYAML(text)
        want = [{'a': "y", 'b': 1}, {'a': "x", 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_5244(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        text = tabtotext.tabToTOML(itemlist, sorts=['b', 'a'])
        logg.debug("%s => %s", test004, text)
        cond = ['[[data]]', 'b = 1', 'a = "y"', '[[data]]', 'b = 2', 'a = "x"', ]
        self.assertEqual(cond, text.splitlines())
        back = loadTOML(text)
        want = [{'a': 'y', 'b': 1}, {'a': 'x', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_5245(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        text = tabtotext.tabToYAML(itemlist, sorts=['b', 'a'], reorder=['a', 'b'])
        logg.debug("%s => %s", test004, text)
        cond = ['data:', '- a: "y"', '  b: 1', '- a: "x"', '  b: 2', ]
        self.assertEqual(cond, text.splitlines())
        back = loadYAML(text)
        want = [{'a': "y", 'b': 1}, {'a': "x", 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_5246(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        text = tabtotext.tabToTOML(itemlist, sorts=['b', 'a'], reorder=['a', 'b'])
        logg.debug("%s => %s", test004, text)
        cond = ['[[data]]', 'a = "y"', 'b = 1', '[[data]]', 'a = "x"', 'b = 2', ]
        self.assertEqual(cond, text.splitlines())
        back = loadTOML(text)
        want = [{'a': 'y', 'b': 1}, {'a': 'x', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_5247(self) -> None:
        item1 = Item2("x", 2)
        item2 = Item2("y", 3)
        itemlist: DataList = [item1, item2]
        text = tabtotext.tabToYAMLx(itemlist)
        logg.debug("%s => %s", test004, text)
        cond = ['data:', '- a: "x"', '  b: 2', '- a: "y"', '  b: 3', ]
        self.assertEqual(cond, text.splitlines())
        back = loadYAML(text)
        want = [{'a': 'x', 'b': 2}, {'a': 'y', 'b': 3}]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_5248(self) -> None:
        item1 = Item2("x", 2)
        item2 = Item2("y", 3)
        itemlist: DataList = [item1, item2]
        text = tabtotext.tabToTOMLx(itemlist)
        logg.debug("%s => %s", test004, text)
        cond = ['[[data]]', 'a = "x"', 'b = 2', '[[data]]', 'a = "y"', 'b = 3', ]
        self.assertEqual(cond, text.splitlines())
        back = loadTOML(text)
        want = [{'a': 'x', 'b': 2}, {'a': 'y', 'b': 3}]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)

    def test_5251(self) -> None:
        text = tabtotext.tabToYAMLx(data011)
        logg.debug("%s => %s", data011, text)
        want = test011
        cond = ['data:', '- b: null']
        self.assertEqual(cond, text.splitlines())
        back = loadYAML(text)
        self.assertEqual(want, back)
    def test_5252(self) -> None:
        text = tabtotext.tabToYAMLx(data012)
        logg.debug("%s => %s", data012, text)
        want = test012
        cond = ['data:', '- b: false']
        self.assertEqual(cond, text.splitlines())
        back = loadYAML(text)
        self.assertEqual(want, back)
    def test_5253(self) -> None:
        text = tabtotext.tabToYAMLx(data013)
        logg.debug("%s => %s", data013, text)
        want = test013
        cond = ['data:', '- b: true']
        self.assertEqual(cond, text.splitlines())
        back = loadYAML(text)
        self.assertEqual(want, back)
    def test_5254(self) -> None:
        text = tabtotext.tabToYAMLx(data014)
        logg.debug("%s => %s", data014, text)
        want = test014
        cond = ['data:', '- b: ""']
        self.assertEqual(cond, text.splitlines())
        back = loadYAML(text)
        self.assertEqual(want, back)
    def test_5255(self) -> None:
        text = tabtotext.tabToYAMLx(data015)
        logg.debug("%s => %s", data015, text)
        want = test015
        cond = ['data:', '- b: "5678"']
        self.assertEqual(cond, text.splitlines())
        back = loadYAML(text)
        self.assertEqual(want, back)
    def test_5256(self) -> None:
        text = tabtotext.tabToYAMLx(data016)
        logg.debug("%s => %s", data016, text)
        want = test016
        cond = ['data:', '- b: 123']
        self.assertEqual(cond, text.splitlines())
        back = loadYAML(text)
        self.assertEqual(want, back)
    def test_5257(self) -> None:
        text = tabtotext.tabToYAMLx(data017)
        logg.debug("%s => %s", data017, text)
        want = test017
        cond = ['data:', '- b: 123.40']
        self.assertEqual(cond, text.splitlines())
        back = loadYAML(text)
        self.assertEqual(want, back)
    def test_5258(self) -> None:
        text = tabtotext.tabToYAMLx(data018)
        logg.debug("%s => %s", data018, text)
        want = test018
        cond = ['data:', '- b: 2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadYAML(text)
        self.assertEqual(want, back)
    def test_5259(self) -> None:
        text = tabtotext.tabToYAMLx(data019)
        logg.debug("%s => %s", data019, text)
        want = test018  # test019
        cond = ['data:', '- b: 2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadYAML(text)
        self.assertEqual(want, back)
    def test_5261(self) -> None:
        text = tabtotext.tabToTOMLx(data011)
        logg.debug("%s => %s", data011, text)
        want = test011Q
        cond = ['[[data]]', '']  # toml can not encode null
        self.assertEqual(cond, text.splitlines())
        back = loadTOML(text)
        self.assertEqual(want, back)
    def test_5262(self) -> None:
        text = tabtotext.tabToTOMLx(data012)
        logg.debug("%s => %s", data012, text)
        want = test012
        cond = ['[[data]]', 'b = false']
        self.assertEqual(cond, text.splitlines())
        back = loadTOML(text)
        self.assertEqual(want, back)
    def test_5263(self) -> None:
        text = tabtotext.tabToTOMLx(data013)
        logg.debug("%s => %s", data013, text)
        want = test013
        cond = ['[[data]]', 'b = true']
        self.assertEqual(cond, text.splitlines())
        back = loadTOML(text)
        self.assertEqual(want, back)
    def test_5264(self) -> None:
        text = tabtotext.tabToTOMLx(data014)
        logg.debug("%s => %s", data014, text)
        want = test014
        cond = ['[[data]]', 'b = ""']
        self.assertEqual(cond, text.splitlines())
        back = loadTOML(text)
        self.assertEqual(want, back)
    def test_5265(self) -> None:
        text = tabtotext.tabToTOMLx(data015)
        logg.debug("%s => %s", data015, text)
        want = test015
        cond = ['[[data]]', 'b = "5678"']
        self.assertEqual(cond, text.splitlines())
        back = loadTOML(text)
        self.assertEqual(want, back)
    def test_5266(self) -> None:
        text = tabtotext.tabToTOMLx(data016)
        logg.debug("%s => %s", data016, text)
        want = test016
        cond = ['[[data]]', 'b = 123']
        self.assertEqual(cond, text.splitlines())
        back = loadTOML(text)
        self.assertEqual(want, back)
    def test_5267(self) -> None:
        text = tabtotext.tabToTOMLx(data017)
        logg.debug("%s => %s", data017, text)
        want = test017
        cond = ['[[data]]', 'b = 123.40']
        self.assertEqual(cond, text.splitlines())
        back = loadTOML(text)
        self.assertEqual(want, back)
    def test_5268(self) -> None:
        text = tabtotext.tabToTOMLx(data018)
        logg.debug("%s => %s", data018, text)
        want = test018
        cond = ['[[data]]', 'b = 2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadTOML(text)
        self.assertEqual(want, back)
    def test_5269(self) -> None:
        text = tabtotext.tabToTOMLx(data019)
        logg.debug("%s => %s", data019, text)
        want = test018  # test019
        cond = ['[[data]]', 'b = 2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadTOML(text)
        self.assertEqual(want, back)
    def test_5311(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test011, defaultformat="yaml")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test011, text)
        want = test011
        cond = ['data:', '- b: null']
        self.assertEqual(cond, text.splitlines())
        back = loadYAML(text)
        self.assertEqual(want, back)
    def test_5312(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test012, defaultformat="yaml")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test012, text)
        want = test012
        cond = ['data:', '- b: false']
        self.assertEqual(cond, text.splitlines())
        back = loadYAML(text)
        self.assertEqual(want, back)
    def test_5313(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test013, defaultformat="yaml")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test013, text)
        want = test013
        cond = ['data:', '- b: true']
        self.assertEqual(cond, text.splitlines())
        back = loadYAML(text)
        self.assertEqual(want, back)
    def test_5314(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test014, defaultformat="yaml")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test014, text)
        want = test014
        cond = ['data:', '- b: ""']
        self.assertEqual(cond, text.splitlines())
        back = loadYAML(text)
        self.assertEqual(want, back)
    def test_5315(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test015, defaultformat="yaml")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test015, text)
        want = test015
        cond = ['data:', '- b: "5678"']
        self.assertEqual(cond, text.splitlines())
        back = loadYAML(text)
        self.assertEqual(want, back)
    def test_5316(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test016, defaultformat="yaml")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test016, text)
        want = test016
        cond = ['data:', '- b: 123']
        self.assertEqual(cond, text.splitlines())
        back = loadYAML(text)
        self.assertEqual(want, back)
    def test_5317(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test017, defaultformat="yaml")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test017, text)
        want = test017
        cond = ['data:', '- b: 123.40']
        self.assertEqual(cond, text.splitlines())
        back = loadYAML(text)
        self.assertEqual(want, back)
    def test_5318(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test018, defaultformat="yaml")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test018, text)
        want = test018
        cond = ['data:', '- b: 2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadYAML(text)
        self.assertEqual(want, back)
    def test_5319(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test019, defaultformat="yaml")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test019, text)
        want = test018  # test019
        cond = ['data:', '- b: 2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadYAML(text)
        self.assertEqual(want, back)
    def test_5324(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, table44, defaultformat="yaml")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", table44, text.splitlines())
        want = table44
        cond = ['data:',
                '- a: "x"', '  b: 3', '  c: true', '  d: 0.40',
                '- a: "y"', '  b: 2', '  c: false', '  d: 0.30',
                '- a: null', '  b: null', '  c: true', '  d: 0.20',
                '- a: "y"', '  b: 1', '  d: 0.10']
        self.assertEqual(cond, text.splitlines())
        back = loadYAML(text)
        self.assertEqual(want, back)
    def test_5329(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, table44, defaultformat="yml")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", table44, text.splitlines())
        want = table44
        cond = ['data:',
                '- a:"x"', '  b:3', '  c:true', '  d:0.40',
                '- a:"y"', '  b:2', '  c:false', '  d:0.30',
                '- a:null', '  b:null', '  c:true', '  d:0.20',
                '- a:"y"', '  b:1', '  d:0.10']
        self.assertEqual(cond, text.splitlines())
        back = loadYAML(text)
        self.assertEqual(want, back)
    def test_5361(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test011, defaultformat="toml")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test011, text)
        want = test011Q
        cond = ['[[data]]', '']  # toml can not encode null
        self.assertEqual(cond, text.splitlines())
        back = loadTOML(text)
        self.assertEqual(want, back)
    def test_5362(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test012, defaultformat="toml")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test012, text)
        want = test012
        cond = ['[[data]]', 'b = false']
        self.assertEqual(cond, text.splitlines())
        back = loadTOML(text)
        self.assertEqual(want, back)
    def test_5363(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test013, defaultformat="toml")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test013, text)
        want = test013
        cond = ['[[data]]', 'b = true']
        self.assertEqual(cond, text.splitlines())
        back = loadTOML(text)
        self.assertEqual(want, back)
    def test_5364(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test014, defaultformat="toml")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test014, text)
        want = test014
        cond = ['[[data]]', 'b = ""']
        self.assertEqual(cond, text.splitlines())
        back = loadTOML(text)
        self.assertEqual(want, back)
    def test_5365(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test015, defaultformat="toml")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test015, text)
        want = test015
        cond = ['[[data]]', 'b = "5678"']
        self.assertEqual(cond, text.splitlines())
        back = loadTOML(text)
        self.assertEqual(want, back)
    def test_5366(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test016, defaultformat="toml")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test016, text)
        want = test016
        cond = ['[[data]]', 'b = 123']
        self.assertEqual(cond, text.splitlines())
        back = loadTOML(text)
        self.assertEqual(want, back)
    def test_5367(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test017, defaultformat="toml")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test017, text)
        want = test017
        cond = ['[[data]]', 'b = 123.40']
        self.assertEqual(cond, text.splitlines())
        back = loadTOML(text)
        self.assertEqual(want, back)
    def test_5368(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test018, defaultformat="toml")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test018, text)
        want = test018
        cond = ['[[data]]', 'b = 2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadTOML(text)
        self.assertEqual(want, back)
    def test_5369(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test019, defaultformat="toml")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test019, text)
        want = test018  # test019
        cond = ['[[data]]', 'b = 2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadTOML(text)
        self.assertEqual(want, back)
    def test_5374(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, table44, defaultformat="toml")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", table44, text.splitlines())
        want = _no_none(table44)
        cond = ['[[data]]', 'a = "x"', 'b = 3', 'c = true', 'd = 0.40',
                '[[data]]', 'a = "y"', 'b = 2', 'c = false', 'd = 0.30',
                '[[data]]', 'c = true', 'd = 0.20',
                '[[data]]', 'a = "y"', 'b = 1', 'd = 0.10']
        self.assertEqual(cond, text.splitlines())
        back = loadTOML(text)
        self.assertEqual(want, back)
    def test_5379(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, table44, defaultformat="tml")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", table44, text.splitlines())
        want = _no_none(table44)
        cond = ['[[data]]', 'a="x"', 'b=3', 'c=true', 'd=0.40',
                '[[data]]', 'a="y"', 'b=2', 'c=false', 'd=0.30',
                '[[data]]', 'c=true', 'd=0.20',
                '[[data]]', 'a="y"', 'b=1', 'd=0.10']
        self.assertEqual(cond, text.splitlines())
        back = loadTOML(text)
        self.assertEqual(want, back)
    def test_5403(self) -> None:
        text = tabtotext.tabtoJSON(test003)
        logg.debug("%s => %s", test003, text)
        want = test003
        cond = ['[', '', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5404(self) -> None:
        text = tabtotext.tabtoJSON(test004)
        logg.debug("%s => %s", test004, text)
        want = test004
        cond = ['[', ' {}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5405(self) -> None:
        text = tabtotext.tabtoJSON(test005)
        logg.debug("%s => %s", test005, text)
        want = test005
        cond = ['[', ' {"a": "x"}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5406(self) -> None:
        text = tabtotext.tabtoJSON(test006)
        logg.debug("%s => %s", test006, text)
        want = test006
        cond = ['[', ' {"a": "x", "b": "y"}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5407(self) -> None:
        text = tabtotext.tabtoJSON(test007)
        logg.debug("%s => %s", test007, text)
        want = test007
        cond = ['[', ' {"a": "x", "b": "y"},', ' {"b": "v"}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5408(self) -> None:
        text = tabtotext.tabtoJSON(test008)
        logg.debug("%s => %s", test008, text)
        want = test008
        cond = ['[', ' {"a": "x"},', ' {"b": "v"}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5409(self) -> None:
        text = tabtotext.tabtoJSON(test009)
        logg.debug("%s => %s", test009, text)
        want = test009
        cond = ['[', ' {},', ' {"b": "v"}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5411(self) -> None:
        text = tabtotext.tabtoJSON(test011)
        logg.debug("%s => %s", test011, text)
        want = test011
        cond = ['[', ' {"b": null}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5412(self) -> None:
        text = tabtotext.tabtoJSON(test012)
        logg.debug("%s => %s", test012, text)
        want = test012
        cond = ['[', ' {"b": false}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5413(self) -> None:
        text = tabtotext.tabtoJSON(test013)
        logg.debug("%s => %s", test013, text)
        want = test013
        cond = ['[', ' {"b": true}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5414(self) -> None:
        text = tabtotext.tabtoJSON(test014)
        logg.debug("%s => %s", test014, text)
        want = test014
        cond = ['[', ' {"b": ""}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5415(self) -> None:
        text = tabtotext.tabtoJSON(test015)
        logg.debug("%s => %s", test015, text)
        want = test015
        cond = ['[', ' {"b": "5678"}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5416(self) -> None:
        text = tabtotext.tabtoJSON(test016)
        logg.debug("%s => %s", test016, text)
        want = test016
        cond = ['[', ' {"b": 123}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5417(self) -> None:
        text = tabtotext.tabtoJSON(test017)
        logg.debug("%s => %s", test017, text)
        want = test017
        cond = ['[', ' {"b": 123.40}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5418(self) -> None:
        text = tabtotext.tabtoJSON(test018)
        logg.debug("%s => %s", test018, text)
        want = test018
        cond = ['[', ' {"b": "2021-12-31"}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5419(self) -> None:
        text = tabtotext.tabtoJSON(test019)
        logg.debug("%s => %s", test019, text)
        want = test018  # test019
        cond = ['[', ' {"b": "2021-12-31"}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5421(self) -> None:
        """ legend is ignored for JSON output """
        text = tabtotext.tabtoJSON(test011, legend="a result")
        logg.debug("%s => %s", test011, text)
        want = test011
        cond = ['[', ' {"b": null}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5431(self) -> None:
        """ legend is ignored for JSON output """
        text = tabtotext.tabtoJSON(test011, legend=["a result", "was found"])
        logg.debug("%s => %s", test011, text)
        want = test011
        cond = ['[', ' {"b": null}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5444(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        text = tabtotext.tabtoJSON(itemlist, sorts=['b', 'a'])
        logg.debug("%s => %s", test004, text)
        cond = ['[', ' {"b": 1, "a": "y"},', ' {"b": 2, "a": "x"}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        want = [{'a': 'y', 'b': 1}, {'a': 'x', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_5445(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}, {'c': 'h'}]
        text = tabtotext.tabtoJSON(itemlist, sorts=['b', 'a'])
        logg.debug("%s => %s", test004, text)
        cond = ['[', ' {"b": 1, "a": "y"},', ' {"b": 2, "a": "x"},', ' {"c": "h"}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        want = [{'a': 'y', 'b': 1}, {'a': 'x', 'b': 2}, {'c': "h"}, ]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_5446(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}, {'c': 'h'}]
        text = tabtotext.tabtoJSON(itemlist, sorts=['b', 'a'], reorder=['a', 'b'])
        logg.debug("%s => %s", test004, text)
        cond = ['[', ' {"a": "y", "b": 1},', ' {"a": "x", "b": 2},', ' {"c": "h"}', ']']
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        want = [{'a': 'y', 'b': 1}, {'a': 'x', 'b': 2}, {'c': "h"}, ]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_5470(self) -> None:
        text = tabtotext.tabtoJSON(table01, ["b", "a"], ["a"])
        logg.debug("%s => %s", table01, text)
        cond = ['[', ' {},', ' {"a": "x y"}', ']']
        want = [{}, {'a': 'x y'}]
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5471(self) -> None:
        text = tabtotext.tabtoJSON(table02, ["b", "a"], ["a"])
        logg.debug("%s => %s", table02, text)
        cond = ['[', ' {},', ' {"a": "x"}', ']']
        want = [{}, {'a': 'x'}]
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5472(self) -> None:
        text = tabtotext.tabtoJSON(table22, ["b", "a"], ["a"])
        logg.debug("%s => %s", table22, text)
        cond = ['[', ' {"a": "x"},', ' {"a": "y"}', ']']
        want = [{'a': 'x'}, {'a': 'y'}]
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5473(self) -> None:
        text = tabtotext.tabtoJSON(table33, ["b", "a"], ["a"])
        logg.debug("%s => %s", table33, text)
        cond = ['[', ' {"a": null},', ' {"a": "x"},', ' {"a": "y"}', ']']
        want = [{'a': None}, {'a': 'x'}, {'a': 'y'}]
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5474(self) -> None:
        text = tabtotext.tabtoJSON(table33, ["c", "a"], ["a"])
        logg.debug("%s => %s", table33, text)
        cond = ['[', ' {"a": null},', ' {"a": "x"},', ' {"a": "y"}', ']']
        want = [{'a': None}, {'a': 'x'}, {'a': 'y'}]
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5475(self) -> None:
        text = tabtotext.tabtoJSON(table02, ["b", "a"], ["b"])
        logg.debug("%s => %s", table02, text)
        cond = ['[', ' {"b": 0},', ' {"b": 2}', ']']
        want = [{'b': 0}, {'b': 2}]
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5476(self) -> None:
        text = tabtotext.tabtoJSON(table22, ["b", "a"], ["b"])
        logg.debug("%s => %s", table22, text)
        cond = ['[', ' {"b": 2},', ' {"b": 3}', ']']
        want = [{'b': 2}, {'b': 3}]
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5477(self) -> None:
        text = tabtotext.tabtoJSON(table33, ["b", "a"], ["b"])
        logg.debug("%s => %s", table33, text)
        cond = ['[', ' {"b": 2},', ' {"b": 3},', ' {}', ']']
        want = [{'b': 2}, {'b': 3}, {}]
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5478(self) -> None:
        text = tabtotext.tabtoJSON(table33, ["c", "a"], ["b"])
        logg.debug("%s => %s", table33, text)
        cond = ['[', ' {"b": 2},', ' {"b": 3},', ' {}', ']']
        want = [{'b': 2}, {'b': 3}, {}]
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5479(self) -> None:
        text = tabtotext.tabtoJSON(table33, ["c", "a"], ["c"])
        logg.debug("%s => %s", table33, text)
        cond = ['[', ' {"c": "2021-12-30"},', ' {"c": "2021-12-31"},', ' {"c": "2021-12-31"}', ']']
        want = [{'c': Date(2021, 12, 30)}, {'c': Date(2021, 12, 31)}, {'c': Date(2021, 12, 31)}]
        self.assertEqual(cond, text.splitlines())
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5530(self) -> None:
        text = tabtotext.tabtoJSON(table01, ["a|b"])
        logg.debug("%s => %s", table01, text.splitlines())
        cond = ['[', ' {"a": "x y"},', ' {"b": 1}', ']']
        self.assertEqual(cond, text.splitlines())
        want = table01
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5531(self) -> None:
        text = tabtotext.tabtoJSON(table02, ["a|b"])
        logg.debug("%s => %s", table02, text.splitlines())
        cond = ['[', ' {"a": "x", "b": 0},', ' {"b": 2}', ']']
        self.assertEqual(cond, text.splitlines())
        want = table02
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5532(self) -> None:
        text = tabtotext.tabtoJSON(table22, ["a|b"])
        logg.debug("%s => %s", table22, text.splitlines())
        cond = ['[', ' {"a": "x", "b": 3},', ' {"a": "y", "b": 2}', ']']
        self.assertEqual(cond, text.splitlines())
        want = table22
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5533(self) -> None:
        text = tabtotext.tabtoJSON(table33, ["a|b"])
        logg.debug("%s => %s", table33, text.splitlines())
        cond = ['[', ' {"a": "x", "b": 3, "c": "2021-12-31"},',
                ' {"a": "y", "b": 2, "c": "2021-12-30"},',
                ' {"a": null, "c": "2021-12-31"}', ']']
        self.assertEqual(cond, text.splitlines())
        want = table33
        back = loadJSON(text)
        self.assertEqual(_date(want), back)
    def test_5534(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[', ' {"a": "x", "b": 3, "c": true, "d": 0.40},',
                ' {"a": "y", "b": 2, "c": false, "d": 0.30},',
                ' {"a": null, "b": null, "c": true, "d": 0.20},',
                ' {"a": "y", "b": 1, "d": 0.10}', ']']
        self.assertEqual(cond, text.splitlines())
        want = table44
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5535(self) -> None:
        text = tabtotext.tabtoJSON(table01, ["b|a"])
        logg.debug("%s => %s", table01, text.splitlines())
        cond = ['[', ' {"a": "x y"},', ' {"b": 1}', ']']
        self.assertEqual(cond, text.splitlines())
        want = table01
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5536(self) -> None:
        text = tabtotext.tabtoJSON(table02, ["b|a"])
        logg.debug("%s => %s", table02, text.splitlines())
        cond = ['[', ' {"b": 0, "a": "x"},', ' {"b": 2}', ']']
        self.assertEqual(cond, text.splitlines())
        want = table02
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5537(self) -> None:
        text = tabtotext.tabtoJSON(table22, ["b|a"])
        logg.debug("%s => %s", table22, text.splitlines())
        cond = ['[', ' {"b": 3, "a": "x"},', ' {"b": 2, "a": "y"}', ']']
        self.assertEqual(cond, text.splitlines())
        want = table22
        back = loadJSON(text)
        self.assertEqual(want, back)
    def test_5538(self) -> None:
        text = tabtotext.tabtoJSON(table33, ["b|a"])
        logg.debug("%s => %s", table33, text.splitlines())
        cond = ['[', ' {"b": 3, "a": "x", "c": "2021-12-31"},',
                ' {"b": 2, "a": "y", "c": "2021-12-30"},',
                ' {"a": null, "c": "2021-12-31"}', ']']
        self.assertEqual(cond, text.splitlines())
        want = table33
        back = loadJSON(text)
        self.assertEqual(_date(want), back)
    def test_5539(self) -> None:
        text = tabtotext.tabtoJSON(table33, ["b|c|a"])
        logg.debug("%s => %s", table33, text.splitlines())
        cond = ['[', ' {"b": 3, "c": "2021-12-31", "a": "x"},',
                ' {"b": 2, "c": "2021-12-30", "a": "y"},',
                ' {"c": "2021-12-31", "a": null}', ']']
        self.assertEqual(cond, text.splitlines())
        want = table33
        back = loadJSON(text)
        self.assertEqual(_date(want), back)
    def test_5594(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["a|b"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[', ' {"a": null, "b": null},', ' {"a": "x", "b": 3},',
                ' {"a": "y", "b": 1},', ' {"a": "y", "b": 2}', ']']
        self.assertEqual(cond, text.splitlines())
    def test_5595(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["b|a"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[', ' {"b": 1, "a": "y"},', ' {"b": 2, "a": "y"},',
                ' {"b": 3, "a": "x"},', ' {"b": null, "a": null}', ']']
        self.assertEqual(cond, text.splitlines())
    def test_5596(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["b|d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[', ' {"b": 1, "d": 0.10},', ' {"b": 2, "d": 0.30},',
                ' {"b": 3, "d": 0.40},', ' {"b": null, "d": 0.20}', ']']
        self.assertEqual(cond, text.splitlines())
    def test_5598(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["a|b|d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[', ' {"a": null, "b": null, "d": 0.20},', ' {"a": "x", "b": 3, "d": 0.40},',
                ' {"a": "y", "b": 1, "d": 0.10},', ' {"a": "y", "b": 2, "d": 0.30}', ']']
        self.assertEqual(cond, text.splitlines())
    def test_5599(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["b|c|a"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[', ' {"b": 1, "a": "y"},', ' {"b": 2, "c": false, "a": "y"},',
                ' {"b": 3, "c": true, "a": "x"},', ' {"b": null, "c": true, "a": null}', ']']
        self.assertEqual(cond, text.splitlines())
    def test_5600(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["b|d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[', ' {"b": 1, "d": 0.10},', ' {"b": 2, "d": 0.30},',
                ' {"b": 3, "d": 0.40},', ' {"b": null, "d": 0.20}', ']']
        self.assertEqual(cond, text.splitlines())
    def test_5601(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["b:02.1f|d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[', ' {"b": 1, "d": 0.10},', ' {"b": 2, "d": 0.30},',
                ' {"b": 3, "d": 0.40},', ' {"b": null, "d": 0.20}', ']']
        self.assertEqual(cond, text.splitlines())
    def test_5602(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b:02.1f"], ["b|d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[', ' {"b": 1, "d": 0.10},', ' {"b": 2, "d": 0.30},',
                ' {"b": 3, "d": 0.40},', ' {"b": null, "d": 0.20}', ']']
        self.assertEqual(cond, text.splitlines())
    def test_5608(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["#|b|d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"#": 1, "b": 3, "d": 0.40},',
                ' {"#": 2, "b": 2, "d": 0.30},',
                ' {"#": 3, "b": null, "d": 0.20},',
                ' {"#": 4, "b": 1, "d": 0.10}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5609(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["b|d|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"b": 1, "d": 0.10, "#": 4},',
                ' {"b": 2, "d": 0.30, "#": 2},',
                ' {"b": 3, "d": 0.40, "#": 1},',
                ' {"b": null, "d": 0.20, "#": 3}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5610(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["b>|d|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"b": 1, "d": 0.10, "#": 4},',
                ' {"b": 2, "d": 0.30, "#": 2},',
                ' {"b": 3, "d": 0.40, "#": 1}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5611(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["b>x|d|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"b": 1, "d": 0.10, "#": 4},',
                ' {"b": 2, "d": 0.30, "#": 2},',
                ' {"b": 3, "d": 0.40, "#": 1},',
                ' {"b": null, "d": 0.20, "#": 3}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5612(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["b>1|d|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[', ' {"b": 2, "d": 0.30, "#": 2},', ' {"b": 3, "d": 0.40, "#": 1}', ']']
        self.assertEqual(cond, text.splitlines())
    def test_5613(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["b>=2|d|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[', ' {"b": 2, "d": 0.30, "#": 2},', ' {"b": 3, "d": 0.40, "#": 1}', ']']
        self.assertEqual(cond, text.splitlines())
    def test_5614(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["b>2|d|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[', ' {"b": 3, "d": 0.40, "#": 1}', ']']
        self.assertEqual(cond, text.splitlines())
    def test_5615(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["b<=2|d|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"b": 1, "d": 0.10, "#": 4},',
                ' {"b": 2, "d": 0.30, "#": 2},',
                ' {"b": null, "d": 0.20, "#": 3}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5616(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["b<2|d|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[', ' {"b": 1, "d": 0.10, "#": 4},', ' {"b": null, "d": 0.20, "#": 3}', ']']
        self.assertEqual(cond, text.splitlines())
    def test_5617(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["b==1|d|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[', ' {"b": 1, "d": 0.10, "#": 4}', ']']
        self.assertEqual(cond, text.splitlines())
    def test_5618(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["b=~1|d|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[', ' {"b": 1, "d": 0.10, "#": 4}', ']']
        self.assertEqual(cond, text.splitlines())
    def test_5619(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["b<>1|d|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"b": 2, "d": 0.30, "#": 2},',
                ' {"b": 3, "d": 0.40, "#": 1},',
                ' {"b": null, "d": 0.20, "#": 3}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5620(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["b|d>|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"b": 1, "d": 0.10, "#": 4},',
                ' {"b": 2, "d": 0.30, "#": 2},',
                ' {"b": 3, "d": 0.40, "#": 1},',
                ' {"b": null, "d": 0.20, "#": 3}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5621(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["b|d>x|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"b": 1, "d": 0.10, "#": 4},',
                ' {"b": 2, "d": 0.30, "#": 2},',
                ' {"b": 3, "d": 0.40, "#": 1},',
                ' {"b": null, "d": 0.20, "#": 3}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5622(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["b|d>0.1|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"b": 2, "d": 0.30, "#": 2},',
                ' {"b": 3, "d": 0.40, "#": 1},',
                ' {"b": null, "d": 0.20, "#": 3}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5623(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["b|d>=0.2|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"b": 2, "d": 0.30, "#": 2},',
                ' {"b": 3, "d": 0.40, "#": 1},',
                ' {"b": null, "d": 0.20, "#": 3}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5624(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["b|d>0.2|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[', ' {"b": 2, "d": 0.30, "#": 2},', ' {"b": 3, "d": 0.40, "#": 1}', ']']
        self.assertEqual(cond, text.splitlines())
    def test_5625(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["b|d<=0.2|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[', ' {"b": 1, "d": 0.10, "#": 4},', ' {"b": null, "d": 0.20, "#": 3}', ']']
        self.assertEqual(cond, text.splitlines())
    def test_5626(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["b|d<0.2|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[', ' {"b": 1, "d": 0.10, "#": 4}', ']']
        self.assertEqual(cond, text.splitlines())
    def test_5627(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["b|d==0.1|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['b;d;#', '1;0.10;4']
        cond = ['[', ' {"b": 1, "d": 0.10, "#": 4}', ']']
        self.assertEqual(cond, text.splitlines())
    def test_5628(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["b|d=~0.1|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[', ' {"b": 1, "d": 0.10, "#": 4}', ']']
        self.assertEqual(cond, text.splitlines())
    def test_5629(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["b|d<>0.1|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"b": 2, "d": 0.30, "#": 2},',
                ' {"b": 3, "d": 0.40, "#": 1},',
                ' {"b": null, "d": 0.20, "#": 3}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5630(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["b|a>|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"b": 1, "a": "y", "#": 4},',
                ' {"b": 2, "a": "y", "#": 2},',
                ' {"b": 3, "a": "x", "#": 1}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5632(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["b|a>x|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"b": 1, "a": "y", "#": 4},',
                ' {"b": 2, "a": "y", "#": 2},',
                ' {"b": null, "a": null, "#": 3}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5633(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["b|a>=y|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"b": 1, "a": "y", "#": 4},',
                ' {"b": 2, "a": "y", "#": 2},',
                ' {"b": null, "a": null, "#": 3}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5634(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["b|a>x|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"b": 1, "a": "y", "#": 4},',
                ' {"b": 2, "a": "y", "#": 2},',
                ' {"b": null, "a": null, "#": 3}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5635(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["b|a<=y|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"b": 1, "a": "y", "#": 4},',
                ' {"b": 2, "a": "y", "#": 2},',
                ' {"b": 3, "a": "x", "#": 1},',
                ' {"b": null, "a": null, "#": 3}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5636(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["b|a<y|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[', ' {"b": 3, "a": "x", "#": 1},', ' {"b": null, "a": null, "#": 3}', ']']
        self.assertEqual(cond, text.splitlines())
    def test_5637(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["b|a==y|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"b": 1, "a": "y", "#": 4},',
                ' {"b": 2, "a": "y", "#": 2},',
                ' {"b": null, "a": null, "#": 3}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5638(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["b|a=~y|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"b": 1, "a": "y", "#": 4},',
                ' {"b": 2, "a": "y", "#": 2},',
                ' {"b": null, "a": null, "#": 3}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5639(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["b|a<>y|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[', ' {"b": 3, "a": "x", "#": 1},', ' {"b": null, "a": null, "#": 3}', ']']
        self.assertEqual(cond, text.splitlines())
    def test_5640(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["b|c>|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"b": 1, "#": 4},',
                ' {"b": 3, "c": true, "#": 1},',
                ' {"b": null, "c": true, "#": 3}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5641(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["b|c<>|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"b": 1, "#": 4},',
                ' {"b": 2, "c": false, "#": 2},',
                ' {"b": 3, "c": true, "#": 1},',
                ' {"b": null, "c": true, "#": 3}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5642(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["b|c>false|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"b": 1, "#": 4},',
                ' {"b": 3, "c": true, "#": 1},',
                ' {"b": null, "c": true, "#": 3}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5643(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["b|c>=true|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"b": 1, "#": 4},',
                ' {"b": 3, "c": true, "#": 1},',
                ' {"b": null, "c": true, "#": 3}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5644(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["b|c>true|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[', ' {"b": 1, "#": 4}', ']']
        self.assertEqual(cond, text.splitlines())
    def test_5645(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["b|c<=true|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"b": 1, "#": 4},',
                ' {"b": 2, "c": false, "#": 2},',
                ' {"b": 3, "c": true, "#": 1},',
                ' {"b": null, "c": true, "#": 3}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5646(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["b|c<true|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[', ' {"b": 1, "#": 4},', ' {"b": 2, "c": false, "#": 2}', ']']
        self.assertEqual(cond, text.splitlines())
    def test_5647(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["b|c==true|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"b": 1, "#": 4},',
                ' {"b": 3, "c": true, "#": 1},',
                ' {"b": null, "c": true, "#": 3}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5648(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["b|c=~true|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"b": 1, "#": 4},',
                ' {"b": 3, "c": true, "#": 1},',
                ' {"b": null, "c": true, "#": 3}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5649(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["b|c<>true|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"b": 1, "#": 4},',
                ' {"b": 2, "c": false, "#": 2},',
                ' {"b": 3, "c": true, "#": 1},',
                ' {"b": null, "c": true, "#": 3}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5660(self) -> None:
        text = tabtotext.tabtoJSON(table33, ["a|b"], ["b|c>|#"])
        logg.debug("%s => %s", table33, text.splitlines())
        cond = ['[',
                ' {"b": 2, "c": "2021-12-30", "#": 2},',
                ' {"b": 3, "c": "2021-12-31", "#": 1},',
                ' {"c": "2021-12-31", "#": 3}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5661(self) -> None:
        text = tabtotext.tabtoJSON(table33, ["a|b"], ["b|c<>|#"])
        logg.debug("%s => %s", table33, text.splitlines())
        cond = ['[',
                ' {"b": 2, "c": "2021-12-30", "#": 2},',
                ' {"b": 3, "c": "2021-12-31", "#": 1},',
                ' {"c": "2021-12-31", "#": 3}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5662(self) -> None:
        text = tabtotext.tabtoJSON(table33, ["a|b"], ["b|c>2021-12-30|#"])
        logg.debug("%s => %s", table33, text.splitlines())
        cond = ['[',
                ' {"b": 3, "c": "2021-12-31", "#": 1},',
                ' {"c": "2021-12-31", "#": 3}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5663(self) -> None:
        text = tabtotext.tabtoJSON(table33, ["a|b"], ["b|c>=2021-12-30|#"])
        logg.debug("%s => %s", table33, text.splitlines())
        cond = ['[',
                ' {"b": 2, "c": "2021-12-30", "#": 2},',
                ' {"b": 3, "c": "2021-12-31", "#": 1},',
                ' {"c": "2021-12-31", "#": 3}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5664(self) -> None:
        text = tabtotext.tabtoJSON(table33, ["a|b"], ["b|c>2021-12-31|#"])
        logg.debug("%s => %s", table33, text.splitlines())
        cond = ['[', '', ']']
        self.assertEqual(cond, text.splitlines())
    def test_5665(self) -> None:
        text = tabtotext.tabtoJSON(table33, ["a|b"], ["b|c<=2021-12-31|#"])
        logg.debug("%s => %s", table33, text.splitlines())
        cond = ['[',
                ' {"b": 2, "c": "2021-12-30", "#": 2},',
                ' {"b": 3, "c": "2021-12-31", "#": 1},',
                ' {"c": "2021-12-31", "#": 3}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5666(self) -> None:
        text = tabtotext.tabtoJSON(table33, ["a|b"], ["b|c<2021-12-31|#"])
        logg.debug("%s => %s", table33, text.splitlines())
        cond = ['[', ' {"b": 2, "c": "2021-12-30", "#": 2}', ']']
        self.assertEqual(cond, text.splitlines())
    def test_5667(self) -> None:
        text = tabtotext.tabtoJSON(table33, ["a|b"], ["b|c==2021-12-31|#"])
        logg.debug("%s => %s", table33, text.splitlines())
        cond = ['[',
                ' {"b": 3, "c": "2021-12-31", "#": 1},',
                ' {"c": "2021-12-31", "#": 3}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5668(self) -> None:
        text = tabtotext.tabtoJSON(table33, ["a|b"], ["b|c=~2021-12-31|#"])
        logg.debug("%s => %s", table33, text.splitlines())
        cond = ['[',
                ' {"b": 3, "c": "2021-12-31", "#": 1},',
                ' {"c": "2021-12-31", "#": 3}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5669(self) -> None:
        text = tabtotext.tabtoJSON(table33, ["a|b"], ["b|c<>2021-12-31|#"])
        logg.debug("%s => %s", table33, text.splitlines())
        cond = ['[', ' {"b": 2, "c": "2021-12-30", "#": 2}', ']']
        self.assertEqual(cond, text.splitlines())
    def test_5702(self) -> None:
        text = tabtotext.tabtoJSON(table02, ["a|b"], ["{a}+{b}"])
        logg.debug("%s => %s", table02, text.splitlines())
        cond = ['[', ' {"a b": "\\"x\\"+0"},', ' {"a b": "~+2"}', ']']
        self.assertEqual(cond, text.splitlines())
    def test_5703(self) -> None:
        text = tabtotext.tabtoJSON(table33, ["a|b"], ["{a}+{b} = {c}"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"a b c": "\\"x\\"+3 = \\"2021-12-31\\""},',
                ' {"a b c": "\\"y\\"+2 = \\"2021-12-30\\""},',
                ' {"a b c": "null+~ = \\"2021-12-31\\""}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5704(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["{a}+{b} = {c}"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"a b c": "\\"x\\"+3 = true"},',
                ' {"a b c": "\\"y\\"+1 = ~"},',
                ' {"a b c": "\\"y\\"+2 = false"},',
                ' {"a b c": "null+null = true"}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5705(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["{a}+{b} = {c}", "d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"a b c": "\\"x\\"+3 = true", "d": 0.40},',
                ' {"a b c": "\\"y\\"+1 = ~", "d": 0.10},',
                ' {"a b c": "\\"y\\"+2 = false", "d": 0.30},',
                ' {"a b c": "null+null = true", "d": 0.20}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5706(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["d", "{a}+{b} = {c}"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"d": 0.10, "a b c": "\\"y\\"+1 = ~"},',
                ' {"d": 0.20, "a b c": "null+null = true"},',
                ' {"d": 0.30, "a b c": "\\"y\\"+2 = false"},',
                ' {"d": 0.40, "a b c": "\\"x\\"+3 = true"}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5712(self) -> None:
        text = tabtotext.tabtoJSON(table02, ["a|b"], ["{a}+{b}@info"])
        logg.debug("%s => %s", table02, text.splitlines())
        cond = ['[', ' {"info": "\\"x\\"+0"},', ' {"info": "~+2"}', ']']
        self.assertEqual(cond, text.splitlines())
    def test_5713(self) -> None:
        text = tabtotext.tabtoJSON(table33, ["a|b"], ["{a}+{b} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"info": "\\"x\\"+3 = \\"2021-12-31\\""},',
                ' {"info": "\\"y\\"+2 = \\"2021-12-30\\""},',
                ' {"info": "null+~ = \\"2021-12-31\\""}',
                ']']
    def test_5714(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["{a}+{b} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"info": "\\"x\\"+3 = true"},',
                ' {"info": "\\"y\\"+1 = ~"},',
                ' {"info": "\\"y\\"+2 = false"},',
                ' {"info": "null+null = true"}',
                ']']
    def test_5715(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["{a}+{b} = {c}@info", "d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"info": "\\"x\\"+3 = true", "d": 0.40},',
                ' {"info": "\\"y\\"+1 = ~", "d": 0.10},',
                ' {"info": "\\"y\\"+2 = false", "d": 0.30},',
                ' {"info": "null+null = true", "d": 0.20}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5716(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a|b"], ["d", "{a}+{b} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"d": 0.10, "info": "\\"y\\"+1 = ~"},',
                ' {"d": 0.20, "info": "null+null = true"},',
                ' {"d": 0.30, "info": "\\"y\\"+2 = false"},',
                ' {"d": 0.40, "info": "\\"x\\"+3 = true"}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5722(self) -> None:
        text = tabtotext.tabtoJSON(table02, ["a@x"], ["{a}+{b}@info"])
        logg.debug("%s => %s", table02, text.splitlines())
        cond = ['[', ' {"info": "\\"x\\"+0"},', ' {"info": "~+2"}', ']']
        self.assertEqual(cond, text.splitlines())
    def test_5723(self) -> None:
        text = tabtotext.tabtoJSON(table33, ["a@x"], ["{a}+{b} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"info": "\\"x\\"+3 = \\"2021-12-31\\""},',
                ' {"info": "\\"y\\"+2 = \\"2021-12-30\\""},',
                ' {"info": "null+~ = \\"2021-12-31\\""}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5724(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a@x"], ["{a}+{b} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"info": "\\"x\\"+3 = true"},',
                ' {"info": "\\"y\\"+1 = ~"},',
                ' {"info": "\\"y\\"+2 = false"},',
                ' {"info": "null+null = true"}',
                ']']
    def test_5725(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a@x"], ["{a}+{b} = {c}@info", "d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"info": "\\"x\\"+3 = true", "d": 0.40},',
                ' {"info": "\\"y\\"+1 = ~", "d": 0.10},',
                ' {"info": "\\"y\\"+2 = false", "d": 0.30},',
                ' {"info": "null+null = true", "d": 0.20}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5726(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a@x"], ["d", "{a}+{b} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"d": 0.10, "info": "\\"y\\"+1 = ~"},',
                ' {"d": 0.20, "info": "null+null = true"},',
                ' {"d": 0.30, "info": "\\"y\\"+2 = false"},',
                ' {"d": 0.40, "info": "\\"x\\"+3 = true"}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5732(self) -> None:
        text = tabtotext.tabtoJSON(table02, ["a@x"], ["{x}+{b}@info"])
        logg.debug("%s => %s", table02, text.splitlines())
        cond = ['[', ' {"info": "\\"x\\"+0"},', ' {"info": "~+2"}', ']']
        self.assertEqual(cond, text.splitlines())
    def test_5733(self) -> None:
        text = tabtotext.tabtoJSON(table33, ["a@x"], ["{x}+{b} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"info": "\\"x\\"+3 = \\"2021-12-31\\""},',
                ' {"info": "\\"y\\"+2 = \\"2021-12-30\\""},',
                ' {"info": "null+~ = \\"2021-12-31\\""}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5734(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a@x"], ["{x}+{b} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"info": "\\"x\\"+3 = true"},',
                ' {"info": "\\"y\\"+1 = ~"},',
                ' {"info": "\\"y\\"+2 = false"},',
                ' {"info": "null+null = true"}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5735(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a@x"], ["{x}+{b} = {c}@info", "d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"info": "\\"x\\"+3 = true", "d": 0.40},',
                ' {"info": "\\"y\\"+1 = ~", "d": 0.10},',
                ' {"info": "\\"y\\"+2 = false", "d": 0.30},',
                ' {"info": "null+null = true", "d": 0.20}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5736(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a@x"], ["d", "{x}+{b} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"d": 0.10, "info": "\\"y\\"+1 = ~"},',
                ' {"d": 0.20, "info": "null+null = true"},',
                ' {"d": 0.30, "info": "\\"y\\"+2 = false"},',
                ' {"d": 0.40, "info": "\\"x\\"+3 = true"}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5742(self) -> None:
        text = tabtotext.tabtoJSON(table02, ["a@x|b@y"], ["{x}+{y}@info"])
        logg.debug("%s => %s", table02, text.splitlines())
        cond = ['[', ' {"info": "\\"x\\"+0"},', ' {"info": "~+2"}', ']']
        self.assertEqual(cond, text.splitlines())
    def test_5743(self) -> None:
        text = tabtotext.tabtoJSON(table33, ["a@x|b@y"], ["{x}+{y} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"info": "\\"x\\"+3 = \\"2021-12-31\\""},',
                ' {"info": "\\"y\\"+2 = \\"2021-12-30\\""},',
                ' {"info": "null+~ = \\"2021-12-31\\""}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5744(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a@x|b@y"], ["{x}+{y} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"info": "\\"x\\"+3 = true"},',
                ' {"info": "\\"y\\"+1 = ~"},',
                ' {"info": "\\"y\\"+2 = false"},',
                ' {"info": "null+null = true"}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5745(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a@x|b@y"], ["{x}+{y} = {c}@info", "d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"info": "\\"x\\"+3 = true", "d": 0.40},',
                ' {"info": "\\"y\\"+1 = ~", "d": 0.10},',
                ' {"info": "\\"y\\"+2 = false", "d": 0.30},',
                ' {"info": "null+null = true", "d": 0.20}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5746(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a@x|b@y"], ["d", "{x}+{y} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"d": 0.10, "info": "\\"y\\"+1 = ~"},',
                ' {"d": 0.20, "info": "null+null = true"},',
                ' {"d": 0.30, "info": "\\"y\\"+2 = false"},',
                ' {"d": 0.40, "info": "\\"x\\"+3 = true"}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5752(self) -> None:
        text = tabtotext.tabtoJSON(table02, ["a@x|b@y"], ["x@info"])
        logg.debug("%s => %s", table02, text.splitlines())
        cond = ['[', ' {},', ' {"info": "x"}', ']']
        self.assertEqual(cond, text.splitlines())
    def test_5753(self) -> None:
        text = tabtotext.tabtoJSON(table33, ["a@x|b@y"], ["x@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[', ' {"info": null},', ' {"info": "x"},', ' {"info": "y"}', ']']
        self.assertEqual(cond, text.splitlines())
    def test_5754(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a@x|b@y"], ["x@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"info": null},',
                ' {"info": "x"},',
                ' {"info": "y"},',
                ' {"info": "y"}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5755(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a@x|b@y"], ["x@info", "d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"info": null, "d": 0.20},',
                ' {"info": "x", "d": 0.40},',
                ' {"info": "y", "d": 0.10},',
                ' {"info": "y", "d": 0.30}',
                ']']
    def test_5756(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a@x|b@y"], ["d", "x@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"d": 0.10, "info": "y"},',
                ' {"d": 0.20, "info": null},',
                ' {"d": 0.30, "info": "y"},',
                ' {"d": 0.40, "info": "x"}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5762(self) -> None:
        text = tabtotext.tabtoJSON(table02, ["a@x|b@y"], ["x@info|y@mm"])
        logg.debug("%s => %s", table02, text.splitlines())
        cond = ['[', ' {"mm": 2},', ' {"info": "x", "mm": 0}', ']']
        self.assertEqual(cond, text.splitlines())
    def test_5763(self) -> None:
        text = tabtotext.tabtoJSON(table33, ["a@x|b@y"], ["x@info|y@mm"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"info": null},',
                ' {"info": "x", "mm": 3},',
                ' {"info": "y", "mm": 2}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5764(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a@x|b@y"], ["x@info|y@mm"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"info": null, "mm": null},',
                ' {"info": "x", "mm": 3},',
                ' {"info": "y", "mm": 1},',
                ' {"info": "y", "mm": 2}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5765(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a@x|b@y"], ["x@info|y@mm", "d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"info": null, "mm": null, "d": 0.20},',
                ' {"info": "x", "mm": 3, "d": 0.40},',
                ' {"info": "y", "mm": 1, "d": 0.10},',
                ' {"info": "y", "mm": 2, "d": 0.30}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5766(self) -> None:
        text = tabtotext.tabtoJSON(table44, ["a@x|b@y"], ["d", "x@info|y@mm"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['[',
                ' {"d": 0.10, "info": "y", "mm": 1},',
                ' {"d": 0.20, "info": null, "mm": null},',
                ' {"d": 0.30, "info": "y", "mm": 2},',
                ' {"d": 0.40, "info": "x", "mm": 3}',
                ']']
        self.assertEqual(cond, text.splitlines())
    def test_5811(self) -> None:
        tablist = {"table01": table01, "table02": table02}
        text = tabtotext.tablistmakeFMT("json", tabtotext.tablistfor(tablist))
        logg.debug("%s => %s", tablist, text.splitlines())
        cond = ['{"table01": [', ' {"a": "x y"},', ' {"b": 1}',
                '],"table02": [', ' {"a": "x", "b": 0},', ' {"b": 2}', ']}']
        self.assertEqual(cond, text.splitlines())
        want = tablist
        scan = tabtotext.tablistscanJSON(text)
        back = tabtotext.tablistmap(scan)
        self.assertEqual(want, back)
    def test_5812(self) -> None:
        tablist = {"table22": table22, "table33": table33}
        text = tabtotext.tablistmakeFMT("json", tabtotext.tablistfor(tablist))
        logg.debug("%s => %s", tablist, text.splitlines())
        cond = ['{"table22": [', ' {"a": "x", "b": 3},', ' {"a": "y", "b": 2}',
                '],"table33": [', ' {"a": "x", "b": 3, "c": "2021-12-31"},',
                ' {"a": "y", "b": 2, "c": "2021-12-30"},',
                ' {"a": null, "c": "2021-12-31"}', ']}']
        self.assertEqual(cond, text.splitlines())
        want = {"table22": table22, "table33": _date(table33)}
        scan = tabtotext.tablistscanJSON(text)
        back = dict(tabtotext.tablistmap(scan))
        logg.debug("\n>> %s\n<< %s", want, back)
        self.assertEqual(want, back)
    def test_5815(self) -> None:
        tablist = {"table01": table01, "table02": table02}
        text = tabtotext.tablistmakeFMT("yaml", tabtotext.tablistfor(tablist))
        logg.debug("%s => %s", tablist, text.splitlines())
        cond = ['table01:', '- a: "x y"', '- b: 1', 'table02:', '- a: "x"', '  b: 0', '- b: 2']
        self.assertEqual(cond, text.splitlines())
        want = tablist
        scan = tabtotext.tablistscanYAML(text)
        back = dict(tabtotext.tablistmap(scan))
        self.assertEqual(want, back)
    def test_5816(self) -> None:
        tablist = {"table22": table22, "table33": table33}
        text = tabtotext.tablistmakeFMT("yaml", tabtotext.tablistfor(tablist))
        logg.debug("%s => %s", tablist, text.splitlines())
        cond = ['table22:', '- a: "x"', '  b: 3', '- a: "y"', '  b: 2', 'table33:', '- a: "x"', '  b: 3',
                '  c: 2021-12-31', '- a: "y"', '  b: 2', '  c: 2021-12-30', '- a: null', '  c: 2021-12-31']
        self.assertEqual(cond, text.splitlines())
        want = {"table22": table22, "table33": _date(table33)}
        scan = tabtotext.tablistscanYAML(text)
        back = dict(tabtotext.tablistmap(scan))
        logg.debug("\n>> %s\n<< %s", want, back)
        self.assertEqual(want, back)
    def test_5817(self) -> None:
        tablist = {"table01": table01, "table02": table02}
        text = tabtotext.tablistmakeFMT("toml", tabtotext.tablistfor(tablist))
        logg.debug("%s => %s", tablist, text.splitlines())
        cond = ['[[table01]]', 'a = "x y"',
                '[[table01]]', 'b = 1',
                '[[table02]]', 'a = "x"', 'b = 0',
                '[[table02]]', 'b = 2']
        self.assertEqual(cond, text.splitlines())
        want = tablist
        scan = tabtotext.tablistscanTOML(text)
        back = dict(tabtotext.tablistmap(scan))
        self.assertEqual(want, back)
    def test_5818(self) -> None:
        tablist = {"table22": table22, "table33": table33}
        text = tabtotext.tablistmakeFMT("toml", tabtotext.tablistfor(tablist))
        logg.debug("%s => %s", tablist, text.splitlines())
        cond = ['[[table22]]', 'a = "x"', 'b = 3',
                '[[table22]]', 'a = "y"', 'b = 2',
                '[[table33]]', 'a = "x"', 'b = 3', 'c = 2021-12-31',
                '[[table33]]', 'a = "y"', 'b = 2', 'c = 2021-12-30',
                '[[table33]]', 'c = 2021-12-31']
        self.assertEqual(cond, text.splitlines())
        want = {"table22": table22, "table33": _no_none(_date(table33))}
        scan = tabtotext.tablistscanTOML(text)
        back = dict(tabtotext.tablistmap(scan))
        logg.debug("\n>> %s\n<< %s", want, back)
        self.assertEqual(want, back)
    def test_5821(self) -> None:
        tmp = self.testdir()
        tablist = {"table01": table01, "table02": table02}
        filename = path.join(tmp, "output.json")
        text = tabtotext.print_tablist(filename, tabtotext.tablistfor(tablist))
        sz = path.getsize(filename)
        self.assertGreater(sz, 10)
        self.assertGreater(100, sz)
        want = {"table01": table01, "table02": _date(table02)}
        scan = tabtotext.tablistfile(filename)
        back = dict(tabtotext.tablistmap(scan))
        logg.debug("\n>> %s\n<< %s", want, back)
        self.assertEqual(want, back)
    def test_5822(self) -> None:
        tmp = self.testdir()
        tablist = {"table22": table22, "table33": table33}
        filename = path.join(tmp, "output.json")
        text = tabtotext.print_tablist(filename, tabtotext.tablistfor(tablist))
        sz = path.getsize(filename)
        self.assertGreater(sz, 100)
        self.assertGreater(600, sz)
        want = {"table22": table22, "table33": _date(table33)}
        scan = tabtotext.tablistfile(filename)
        back = dict(tabtotext.tablistmap(scan))
        logg.debug("\n>> %s\n<< %s", want, back)
        self.assertEqual(want, back)
    def test_5825(self) -> None:
        tmp = self.testdir()
        tablist = {"table01": table01, "table02": table02}
        filename = path.join(tmp, "output.yaml")
        text = tabtotext.print_tablist(filename, tabtotext.tablistfor(tablist))
        sz = path.getsize(filename)
        self.assertGreater(sz, 10)
        self.assertGreater(100, sz)
        want = {"table01": table01, "table02": _date(table02)}
        scan = tabtotext.tablistfile(filename)
        back = dict(tabtotext.tablistmap(scan))
        logg.debug("\n>> %s\n<< %s", want, back)
        self.assertEqual(want, back)
    def test_5826(self) -> None:
        tmp = self.testdir()
        tablist = {"table22": table22, "table33": table33}
        filename = path.join(tmp, "output.yaml")
        text = tabtotext.print_tablist(filename, tabtotext.tablistfor(tablist))
        sz = path.getsize(filename)
        self.assertGreater(sz, 100)
        self.assertGreater(600, sz)
        want = {"table22": table22, "table33": _date(table33)}
        scan = tabtotext.tablistfile(filename)
        back = dict(tabtotext.tablistmap(scan))
        logg.debug("\n>> %s\n<< %s", want, back)
        self.assertEqual(want, back)
    def test_5827(self) -> None:
        tmp = self.testdir()
        tablist = {"table01": table01, "table02": table02}
        filename = path.join(tmp, "output.toml")
        text = tabtotext.print_tablist(filename, tabtotext.tablistfor(tablist))
        sz = path.getsize(filename)
        self.assertGreater(sz, 10)
        self.assertGreater(100, sz)
        want = {"table01": table01, "table02": _date(table02)}
        scan = tabtotext.tablistfile(filename)
        back = dict(tabtotext.tablistmap(scan))
        logg.debug("\n>> %s\n<< %s", want, back)
        self.assertEqual(want, back)
    def test_5828(self) -> None:
        tmp = self.testdir()
        tablist = {"table22": table22, "table33": table33}
        filename = path.join(tmp, "output.toml")
        text = tabtotext.print_tablist(filename, tabtotext.tablistfor(tablist))
        sz = path.getsize(filename)
        self.assertGreater(sz, 100)
        self.assertGreater(600, sz)
        want = {"table22": table22, "table33": _no_none(_date(table33))}
        scan = tabtotext.tablistfile(filename)
        back = dict(tabtotext.tablistmap(scan))
        logg.debug("\n>> %s\n<< %s", want, back)
        self.assertEqual(want, back)
    def test_5915(self) -> None:
        item1 = Item2("x", 2)
        item2 = Item2("y", 3)
        itemlist: DataList = [item1, item2]
        text = tabtotext.tabToFMTx("yaml", itemlist)
        logg.debug("%s => %s", test004, text)
        cond = ['data:', '- a: "x"', '  b: 2', '- a: "y"', '  b: 3', ]
        self.assertEqual(cond, text.splitlines())
        back = loadYAML(text)
        want = [{'a': 'x', 'b': 2}, {'a': 'y', 'b': 3}]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_5916(self) -> None:
        item1 = Item2("x", 2)
        item2 = Item2("y", 3)
        itemlist: DataList = [item1, item2]
        text = tabtotext.tabToFMTx("toml", itemlist)
        logg.debug("%s => %s", test004, text)
        cond = ['[[data]]', 'a = "x"', 'b = 2', '[[data]]', 'a = "y"', 'b = 3', ]
        self.assertEqual(cond, text.splitlines())
        back = loadTOML(text)
        want = [{'a': 'x', 'b': 2}, {'a': 'y', 'b': 3}]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)

    def test_6003(self) -> None:
        text = tabtotext.tabToGFM(test003)
        logg.debug("%s => %s", test003, text)
        want = LIST
        cond = ['', '']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6004(self) -> None:
        text = tabtotext.tabToGFM(test004)
        logg.debug("%s => %s", test004, text)
        want = LIST
        cond = ['', '', '']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6005(self) -> None:
        text = tabtotext.tabToGFM(test005)
        logg.debug("%s => %s", test005, text)
        want = test005
        cond = ['| a', '| -----', '| x']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6006(self) -> None:
        text = tabtotext.tabToGFM(test006)
        logg.debug("%s => %s", test006, text)
        want = test006
        cond = ['| a     | b', '| ----- | -----', '| x     | y']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6007(self) -> None:
        text = tabtotext.tabToGFM(test007)
        logg.debug("%s => %s", test007, text)
        want = test007Q
        cond = ['| a     | b', '| ----- | -----', '| x     | y', '| ~     | v']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6008(self) -> None:
        text = tabtotext.tabToGFM(test008)
        logg.debug("%s => %s", test008, text)
        want = test008Q
        cond = ['| a     | b', '| ----- | -----', '| x     | ~', '| ~     | v']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6009(self) -> None:
        text = tabtotext.tabToGFM(test009)
        logg.debug("%s => %s", test009, text)
        want = test009Q
        cond = ['| b', '| -----', '| ~', '| v']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6011(self) -> None:
        text = tabtotext.tabToGFM(test011)
        logg.debug("%s => %s", test011, text)
        want = test011
        cond = ['| b', '| -----', '| ~']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6012(self) -> None:
        text = tabtotext.tabToGFM(test012)
        logg.debug("%s => %s", test012, text)
        want = test012
        cond = ['| b', '| -----', '| (no)']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6013(self) -> None:
        text = tabtotext.tabToGFM(test013)
        logg.debug("%s => %s", test013, text)
        want = test013
        cond = ['| b', '| -----', '| (yes)']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6014(self) -> None:
        text = tabtotext.tabToGFM(test014)
        logg.debug("%s => %s", test014, text)
        want = test014
        cond = ['| b', '| -----', '|']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6015(self) -> None:
        text = tabtotext.tabToGFM(test015)
        logg.debug("%s => %s", test015, text)
        want = test015Q
        cond = ['| b', '| -----', '| 5678']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6016(self) -> None:
        text = tabtotext.tabToGFM(test016)
        logg.debug("%s => %s", test016, text)
        want = test016
        cond = ['| b', '| -----', '| 123']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6017(self) -> None:
        text = tabtotext.tabToGFM(test017)
        logg.debug("%s => %s", test017, text)
        want = test017
        cond = ['| b', '| ------', '| 123.40']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6018(self) -> None:
        text = tabtotext.tabToGFM(test018)
        logg.debug("%s => %s", test018, text)
        want = test018
        cond = ['| b', '| ----------', '| 2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6019(self) -> None:
        text = tabtotext.tabToGFM(test019)
        logg.debug("%s => %s", test019, text)
        want = test019Q
        cond = ['| b', '| ----------', '| 2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6020(self) -> None:
        text = tabtotext.tabToGFM(table01)
        logg.debug("%s => %s", table01, text)
        want = table01N
        cond = ['| a     | b', '| ----- | -----', '| x y   | ~', '| ~     | 1']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6021(self) -> None:
        text = tabtotext.tabToGFM(table02)
        logg.debug("%s => %s", table02, text)
        want = table02N
        cond = ['| a     | b', '| ----- | -----', '| x     | 0', '| ~     | 2']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6022(self) -> None:
        text = tabtotext.tabToGFM(table22)
        logg.debug("%s => %s", table22, text)
        want = table22
        cond = ['| a     | b', '| ----- | -----', '| x     | 3', '| y     | 2']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6023(self) -> None:
        text = tabtotext.tabToGFM(table33)
        logg.debug("%s => %s", table33, text)
        want = table33Q
        cond = ['| a     | b     | c', '| ----- | ----- | ----------',
                '| x     | 3     | 2021-12-31', '| y     | 2     | 2021-12-30',
                '| ~     | ~     | 2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6024(self) -> None:
        text = tabtotext.tabToGFM(table44)
        logg.debug("%s => %s", table44, text)
        want = table44N
        cond = ['| a     | b     | c     | d', '| ----- | ----- | ----- | -----',
                '| x     | 3     | (yes) | 0.40',
                '| y     | 2     | (no)  | 0.30',
                '| ~     | ~     | (yes) | 0.20',
                '| y     | 1     | ~     | 0.10']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6031(self) -> None:
        text = tabtotext.tabToGFM(test011, legend=["a result", "was found"])
        logg.debug("%s => %s", test011, text)
        want = test011
        cond = ['| b', '| -----', '| ~', '', '- a result', '- was found']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6032(self) -> None:
        text = tabtotext.tabToGFM(test012, legend=["a result", "was found"])
        logg.debug("%s => %s", test012, text)
        want = test012
        cond = ['| b', '| -----', '| (no)', '', '- a result', '- was found']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6033(self) -> None:
        text = tabtotext.tabToGFM(test013, legend=["a result", "was found"])
        logg.debug("%s => %s", test013, text)
        want = test013
        cond = ['| b', '| -----', '| (yes)', '', '- a result', '- was found']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6034(self) -> None:
        text = tabtotext.tabToGFM(test014, legend=["a result", "was found"])
        logg.debug("%s => %s", test014, text)
        want = test014
        cond = ['| b', '| -----', '|', '', '- a result', '- was found']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6035(self) -> None:
        text = tabtotext.tabToGFM(test015, legend=["a result", "was found"])
        logg.debug("%s => %s", test015, text)
        want = test015Q
        cond = ['| b', '| -----', '| 5678', '', '- a result', '- was found']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6036(self) -> None:
        text = tabtotext.tabToGFM(test016, legend=["a result", "was found"])
        logg.debug("%s => %s", test016, text)
        want = test016
        cond = ['| b', '| -----', '| 123', '', '- a result', '- was found']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6037(self) -> None:
        text = tabtotext.tabToGFM(test017, legend=["a result", "was found"])
        logg.debug("%s => %s", test017, text)
        want = test017
        cond = ['| b', '| ------', '| 123.40', '', '- a result', '- was found']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6038(self) -> None:
        text = tabtotext.tabToGFM(test018, legend=["a result", "was found"])
        logg.debug("%s => %s", test018, text)
        want = test018
        cond = ['| b', '| ----------', '| 2021-12-31', '', '- a result', '- was found']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6039(self) -> None:
        text = tabtotext.tabToGFM(test019, legend=["a result", "was found"])
        logg.debug("%s => %s", test019, text)
        want = test019Q
        cond = ['| b', '| ----------', '| 2021-12-31', '', '- a result', '- was found']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)

    def test_6044(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        text = tabtotext.tabToGFM(itemlist, sorts=['b', 'a'])
        logg.debug("%s => %s", test004, text)
        cond = ['| b     | a', '| ----- | -----', '| 1     | y', '| 2     | x']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        want = [{'a': 'y', 'b': 1}, {'a': 'x', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_6045(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}, {'c': 'h'}]
        text = tabtotext.tabToGFM(itemlist, sorts=['b', 'a'])
        logg.debug("%s => %s", test004, text)
        cond = ['| b     | a     | c', '| ----- | ----- | -----',
                '| 1     | y     | ~', '| 2     | x     | ~', '| ~     | ~     | h', ]
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        want = [{'a': 'y', 'b': 1, 'c': None}, {'a': 'x', 'b': 2, 'c': None}, {'a': None, 'b': None, 'c': "h"}, ]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_6046(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}, {'c': 'h'}]
        text = tabtotext.tabToGFM(itemlist, sorts=['b', 'a'], reorder=['a', 'b'])
        logg.debug("%s => %s", test004, text)
        cond = ['| a     | b     | c', '| ----- | ----- | -----',
                '| y     | 1     | ~', '| x     | 2     | ~', '| ~     | ~     | h', ]
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        want = [{'a': 'y', 'b': 1, 'c': None}, {'a': 'x', 'b': 2, 'c': None}, {'a': None, 'b': None, 'c': "h"}, ]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_6048(self) -> None:
        item = Item2("x", 2)
        text = tabtotext.tabToGFMx(item)
        logg.debug("%s => %s", test004, text)
        want = test011
        cond = ['| a     | b', '| ----- | -----', '| x     | 2']
        self.assertEqual(cond, text.splitlines())
    def test_6049(self) -> None:
        item = Item2("x", 2)
        itemlist: DataList = [item]
        text = tabtotext.tabToGFMx(itemlist)
        logg.debug("%s => %s", test004, text)
        cond = ['| a     | b', '| ----- | -----', '| x     | 2']
        self.assertEqual(cond, text.splitlines())
    def test_6051(self) -> None:
        text = tabtotext.tabToGFMx(data011)
        logg.debug("%s => %s", data011, text)
        want = test011
        cond = ['| b', '| -----', '| ~']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6052(self) -> None:
        text = tabtotext.tabToGFMx(data012)
        logg.debug("%s => %s", data012, text)
        want = test012
        cond = ['| b', '| -----', '| (no)']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6053(self) -> None:
        text = tabtotext.tabToGFMx(data013)
        logg.debug("%s => %s", data013, text)
        want = test013
        cond = ['| b', '| -----', '| (yes)']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6054(self) -> None:
        text = tabtotext.tabToGFMx(data014)
        logg.debug("%s => %s", data014, text)
        want = test014
        cond = ['| b', '| -----', '|']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6055(self) -> None:
        text = tabtotext.tabToGFMx(data015)
        logg.debug("%s => %s", data015, text)
        want = test015Q
        cond = ['| b', '| -----', '| 5678']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6056(self) -> None:
        text = tabtotext.tabToGFMx(data016)
        logg.debug("%s => %s", data016, text)
        want = test016
        cond = ['| b', '| -----', '| 123']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6057(self) -> None:
        text = tabtotext.tabToGFMx(data017)
        logg.debug("%s => %s", data017, text)
        want = test017
        cond = ['| b', '| ------', '| 123.40']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6058(self) -> None:
        text = tabtotext.tabToGFMx(data018)
        logg.debug("%s => %s", data018, text)
        want = test018
        cond = ['| b', '| ----------', '| 2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6059(self) -> None:
        text = tabtotext.tabToGFMx(data019)
        logg.debug("%s => %s", data019, text)
        want = test019Q
        cond = ['| b', '| ----------', '| 2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6060(self) -> None:
        text = tabtotext.tabToGFM(table01, ["b", "a"])
        logg.debug("%s => %s", table01, text)
        want = rev(table01N)
        cond = ['| b     | a', '| ----- | -----', '| 1     | ~', '| ~     | x y']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6061(self) -> None:
        text = tabtotext.tabToGFM(table02, ["b", "a"])
        logg.debug("%s => %s", table02, text)
        want = table02N
        cond = ['| b     | a', '| ----- | -----', '| 0     | x', '| 2     | ~']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6062(self) -> None:
        text = tabtotext.tabToGFM(table22, ["b", "a"])
        logg.debug("%s => %s", table22, text)
        want = rev(table22)
        cond = ['| b     | a', '| ----- | -----', '| 2     | y', '| 3     | x']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6063(self) -> None:
        text = tabtotext.tabToGFM(table33, ["b", "a"])
        logg.debug("%s => %s", table33, text)
        want = rev(table33Q[:2]) + table33Q[2:]
        cond = ['| b     | a     | c', '| ----- | ----- | ----------',
                '| 2     | y     | 2021-12-30', '| 3     | x     | 2021-12-31',
                '| ~     | ~     | 2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6064(self) -> None:
        text = tabtotext.tabToGFM(table44, ["b", "a"])
        logg.debug("%s => %s", table44, text.splitlines())
        want = table44N[3:] + table44N[1:2] + table44N[0:1] + table44N[2:3]
        cond = ['| b     | a     | c     | d', '| ----- | ----- | ----- | -----',
                '| 1     | y     | ~     | 0.10', '| 2     | y     | (no)  | 0.30',
                '| 3     | x     | (yes) | 0.40', '| ~     | ~     | (yes) | 0.20']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6065(self) -> None:
        text = tabtotext.tabToGFM(table33, ["c", "a"])
        logg.debug("%s => %s", table33, text)
        want = rev(table33Q[:2]) + table33Q[2:]
        cond = ['| c          | a     | b',
                '| ---------- | ----- | -----',
                '| 2021-12-30 | y     | 2',
                '| 2021-12-31 | x     | 3',
                '| 2021-12-31 | ~     | ~']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)

    def test_6071(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        formats = {"a": ' {:}'}
        headers = ['b', 'a']
        text = tabtotext.tabToGFM(itemlist, ['b', 'a'], formats)
        logg.debug("%s => %s", test004, text)
        cond = ['| b     |     a', '| ----- | ----:', '| 1     |     y', '| 2     |     x']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        want = [{'a': 'y', 'b': 1}, {'a': 'x', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_6072(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        formats = {"a": ' %s'}
        headers = ['b', 'a']
        text = tabtotext.tabToGFM(itemlist, ['b', 'a'], formats)
        logg.debug("%s => %s", test004, text)
        cond = ['| b     |     a', '| ----- | ----:', '| 1     |     y', '| 2     |     x']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        want = [{'a': 'y', 'b': 1}, {'a': 'x', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_6073(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        formats = {"a": '"%s"', "b": "%.2f"}
        headers = ['b', 'a']
        text = tabtotext.tabToGFM(itemlist, ['b', 'a'], formats)
        logg.debug("%s => %s", test004, text)
        cond = ['|     b | a', '| ----: | -----', '|  1.00 | "y"', '|  2.00 | "x"']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        want = [{'a': '"y"', 'b': 1}, {'a': '"x"', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_6074(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        formats = {"a": '"{:}"', "b": "{:.2f}"}
        headers = ['b', 'a']
        text = tabtotext.tabToGFM(itemlist, ['b', 'a'], formats)
        logg.debug("%s => %s", test004, text)
        cond = ['|     b | a', '| ----: | -----', '|  1.00 | "y"', '|  2.00 | "x"']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        want = [{'a': '"y"', 'b': 1}, {'a': '"x"', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_6075(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2.}, {'a': "y", 'b': 1.}]
        formats = {"a": '"{:}"', "b": "%.2f"}
        headers = ['b', 'a']
        text = tabtotext.tabToGFM(itemlist, ['b', 'a'], formats)
        logg.debug("%s => %s", test004, text)
        cond = ['|     b | a', '| ----: | -----', '|  1.00 | "y"', '|  2.00 | "x"']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        want = [{'a': '"y"', 'b': 1}, {'a': '"x"', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_6076(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2.}, {'a': "y", 'b': 1.}]
        formats = {"a": '"{:}"', "b": "{:.2f}"}
        headers = ['b', 'a']
        text = tabtotext.tabToGFM(itemlist, ['b', 'a'], formats)
        logg.debug("%s => %s", test004, text)
        cond = ['|     b | a', '| ----: | -----', '|  1.00 | "y"', '|  2.00 | "x"']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        want = [{'a': '"y"', 'b': 1}, {'a': '"x"', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_6077(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2.}, {'a': "y", 'b': 1.}]
        formats = {"a": '"{:}"', "b": "{:$}"}
        headers = ['b', 'a']
        text = tabtotext.tabToGFM(itemlist, ['b', 'a'], formats)
        logg.debug("%s => %s", test004, text)
        cond = ['|     b | a', '| ----: | -----', X('| 1.00$ | "y"'), X('| 2.00$ | "x"')]
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        want = [{'a': '"y"', 'b': 1}, {'a': '"x"', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_6078(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2.}, {'a': "y", 'b': 1.}]
        formats = {"a": '"{:5s}"', "b": "{:3f}"}
        headers = ['b', 'a']
        text = tabtotext.tabToGFM(itemlist, ['b', 'a'], formats)
        logg.debug("%s => %s", test004, text)
        cond = ['|        b | a', '| -------: | -------', '| 1.000000 | "y    "', '| 2.000000 | "x    "']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        want = [{'a': '"y    "', 'b': 1.0}, {'a': '"x    "', 'b': 2.0}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_6079(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 22.}, {'a': "y", 'b': 1.}]
        formats = {"a": '"{:>5s}"', "b": "{:>3f}"}
        headers = ['b', 'a']
        text = tabtotext.tabToGFM(itemlist, ['b', 'a'], formats)
        logg.debug("%s => %s", test004, text)
        cond = ['|         b |       a', '| --------: | ------:', '|  1.000000 | "    y"', '| 22.000000 | "    x"']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        want = [{'a': '"    y"', 'b': 1.0}, {'a': '"    x"', 'b': 22.0}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_6103(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test003)  # defaultformat="md"
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test003, text)
        want = LIST
        cond = ['', '']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6104(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test004)  # defaultformat="md"
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        want = LIST
        cond = ['', '', '']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6105(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test005)  # defaultformat="md"
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test005, text)
        want = test005
        cond = ['| a', '| -----', '| x']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6106(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test006)  # defaultformat="md"
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test006, text)
        want = test006
        cond = ['| a     | b', '| ----- | -----', '| x     | y']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6107(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test007)  # defaultformat="md"
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test007, text)
        want = test007Q
        cond = ['| a     | b', '| ----- | -----', '| x     | y', '| ~     | v']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6108(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test008)  # defaultformat="md"
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test008, text)
        want = test008Q
        cond = ['| a     | b', '| ----- | -----', '| x     | ~', '| ~     | v']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6109(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test009)  # defaultformat="md"
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test009, text)
        want = test009Q
        cond = ['| b', '| -----', '| ~', '| v']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6111(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test011)  # defaultformat="md"
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test011, text)
        want = test011
        cond = ['| b', '| -----', '| ~']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6112(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test012)  # defaultformat="md"
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test012, text)
        want = test012
        cond = ['| b', '| -----', '| (no)']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6113(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test013)  # defaultformat="md"
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test013, text)
        want = test013
        cond = ['| b', '| -----', '| (yes)']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6114(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test014)  # defaultformat="md"
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test014, text)
        want = test014
        cond = ['| b', '| -----', '|']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6115(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test015)  # defaultformat="md"
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test015, text)
        want = test015Q
        cond = ['| b', '| -----', '| 5678']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6116(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test016)  # defaultformat="md"
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test016, text)
        want = test016
        cond = ['| b', '| -----', '| 123']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6117(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test017)  # defaultformat="md"
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test017, text)
        want = test017
        cond = ['| b', '| ------', '| 123.40']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6118(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test018)  # defaultformat="md"
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test018, text)
        want = test018
        cond = ['| b', '| ----------', '| 2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6119(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test019)  # defaultformat="md"
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test019, text)
        want = test019Q
        cond = ['| b', '| ----------', '| 2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6131(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test011, legend=["a result", "was found"])
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test011, text)
        want = test011
        cond = ['| b', '| -----', '| ~', '', '- a result', '- was found']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6132(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test012, legend=["a result", "was found"])
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test012, text)
        want = test012
        cond = ['| b', '| -----', '| (no)', '', '- a result', '- was found']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6133(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test013, legend=["a result", "was found"])
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test013, text)
        want = test013
        cond = ['| b', '| -----', '| (yes)', '', '- a result', '- was found']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6134(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test014, legend=["a result", "was found"])
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test014, text)
        want = test014
        cond = ['| b', '| -----', '|', '', '- a result', '- was found']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6135(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test015, legend=["a result", "was found"])
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test015, text)
        want = test015Q
        cond = ['| b', '| -----', '| 5678', '', '- a result', '- was found']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6136(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test016, legend=["a result", "was found"])
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test016, text)
        want = test016
        cond = ['| b', '| -----', '| 123', '', '- a result', '- was found']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6137(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test017, legend=["a result", "was found"])
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test017, text)
        want = test017
        cond = ['| b', '| ------', '| 123.40', '', '- a result', '- was found']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6138(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test018, legend=["a result", "was found"])
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test018, text)
        want = test018
        cond = ['| b', '| ----------', '| 2021-12-31', '', '- a result', '- was found']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6139(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test019, legend=["a result", "was found"])
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test019, text)
        want = test019Q
        cond = ['| b', '| ----------', '| 2021-12-31', '', '- a result', '- was found']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6143(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        out = StringIO()
        res = tabtotext.print_tabtotext(out, itemlist, ['b', 'a'])
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['| b     | a', '| ----- | -----', '| 2     | x', '| 1     | y']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        want = [{'a': 'x', 'b': 2}, {'a': 'y', 'b': 1}, ]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_6144(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        out = StringIO()
        res = tabtotext.print_tabtotext(out, itemlist, ['b@1', 'a'])
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['| b     | a', '| ----- | -----', '| 1     | y', '| 2     | x']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        want = [{'a': 'y', 'b': 1}, {'a': 'x', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_6145(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}, {'c': 'h'}]
        out = StringIO()
        res = tabtotext.print_tabtotext(out, itemlist, ['b@1', 'a@2'])
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['| b     | a     | c',
                '| ----- | ----- | -----',
                '| 1     | y     | ~',
                '| 2     | x     | ~',
                '| ~     | ~     | h', ]
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        want = [{'a': 'y', 'b': 1, 'c': None}, {'a': 'x', 'b': 2, 'c': None}, {'a': None, 'b': None, 'c': "h"}, ]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_6149(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}, {'c': 'h'}]
        out = StringIO()
        res = tabtotext.print_tabtotext(out, itemlist, ['b@1', 'a@2'], defaultformat="markdown")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", itemlist, text.splitlines())
        cond = ['| b     | a     | c     |',
                '| ----- | ----- | ----- |',
                '| 1     | y     | ~     |',
                '| 2     | x     | ~     |',
                '| ~     | ~     | h     |']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        want = [{'a': 'y', 'b': 1, 'c': None}, {'a': 'x', 'b': 2, 'c': None}, {'a': None, 'b': None, 'c': "h"}, ]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_6171(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        out = StringIO()
        res = tabtotext.print_tabtotext(out, itemlist, ['b@1', 'a: {:}'])
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['| b     |     a', '| ----- | ----:', '| 1     |     y', '| 2     |     x']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        want = [{'a': 'y', 'b': 1}, {'a': 'x', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_6172(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        out = StringIO()
        res = tabtotext.print_tabtotext(out, itemlist, ['b@1', 'a: %s'])
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['| b     |     a', '| ----- | ----:', '| 1     |     y', '| 2     |     x']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        want = [{'a': 'y', 'b': 1}, {'a': 'x', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_6173(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        out = StringIO()
        res = tabtotext.print_tabtotext(out, itemlist, ['b:<.2n@1', 'a:"%s"'])
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['| b     | a', '| ----- | -----', '| 1     | "y"', '| 2     | "x"']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        want = [{'a': '"y"', 'b': 1}, {'a': '"x"', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_6174(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        out = StringIO()
        res = tabtotext.print_tabtotext(out, itemlist, ['b:{:.2f}@1', 'a:"{:}"'])
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['|     b | a', '| ----: | -----', '|  1.00 | "y"', '|  2.00 | "x"']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        want = [{'a': '"y"', 'b': 1}, {'a': '"x"', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_6175(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2.}, {'a': "y", 'b': 1.}]
        out = StringIO()
        res = tabtotext.print_tabtotext(out, itemlist, ['b:{:<.2f}@1', 'a:"{:}"'])
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        # text = tabtotext.tabToGFM(itemlist, ['b', 'a'], formats)
        logg.debug("%s => %s", test004, text)
        cond = ['| b     | a', '| ----- | -----', '| 1.00  | "y"', '| 2.00  | "x"']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        want = [{'a': '"y"', 'b': 1}, {'a': '"x"', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_6176(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2.}, {'a': "y", 'b': 1.}]
        out = StringIO()
        res = tabtotext.print_tabtotext(out, itemlist, ['b:{:.2f}@1', 'a:"{:}"'])
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['|     b | a', '| ----: | -----', '|  1.00 | "y"', '|  2.00 | "x"']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        want = [{'a': '"y"', 'b': 1}, {'a': '"x"', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_6177(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2.}, {'a': "y", 'b': 1.}]
        out = StringIO()
        res = tabtotext.print_tabtotext(out, itemlist, ['b:{:$}@1', 'a:"{:}"'])
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['|     b | a', '| ----: | -----', X('| 1.00$ | "y"'), X('| 2.00$ | "x"')]
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        want = [{'a': '"y"', 'b': 1}, {'a': '"x"', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_6178(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2.}, {'a': "y", 'b': 1.}]
        out = StringIO()
        res = tabtotext.print_tabtotext(out, itemlist, ['b:{:3f}@1', 'a:"{:5s}"'])
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['|        b | a', '| -------: | -------', '| 1.000000 | "y    "', '| 2.000000 | "x    "']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        want = [{'a': '"y    "', 'b': 1.0}, {'a': '"x    "', 'b': 2.0}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_6179(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 22.}, {'a': "y", 'b': 1.}]
        out = StringIO()
        res = tabtotext.print_tabtotext(out, itemlist, ['b:{:>3f}@1', 'a:"{:>5s}"'])
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['|         b |       a', '| --------: | ------:', '|  1.000000 | "    y"', '| 22.000000 | "    x"']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        want = [{'a': '"    y"', 'b': 1.0}, {'a': '"    x"', 'b': 22.0}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)

    date_for_6220: JSONList = [{"a": "x", "b": 0}, {"b": 2}]
    def test_6220(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, self.date_for_6220, ["b", "a"])  # defaultformat="md"
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", res, text)
        want = self.date_for_6220
        cond = ['| b     | a', '| ----- | -----', '| 0     | x', '| 2     | ~']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        del back[1]["a"]
        self.assertEqual(want, back)
    date_for_6221: JSONList = [{"a": "x", "b": 3}, {"b": 2}]
    def test_6221(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, self.date_for_6221, ["b@1", "a"])  # defaultformat="md"
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", res, text)
        want = rev(self.date_for_6221)
        cond = ['| b     | a', '| ----- | -----', '| 2     | ~', '| 3     | x']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        del back[0]["a"]
        self.assertEqual(want, back)
    date_for_6222: JSONList = [{"a": "x", "b": 3}, {"b": 2}]
    def test_6222(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, self.date_for_6222, ["b", "a@1"])  # defaultformat="md"
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", res, text)
        want = rev(self.date_for_6222)
        cond = ['| b     | a', '| ----- | -----', '| 2     | ~', '| 3     | x']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        del back[0]["a"]
        self.assertEqual(want, back)
    date_for_6223: JSONList = [{"a": "x", "b": 1}, {"b": 2}]
    def test_6223(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, self.date_for_6223, ["b", "a@1"])  # defaultformat="md"
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", res, text)
        want = rev(self.date_for_6223)
        cond = ['| b     | a', '| ----- | -----', '| 2     | ~', '| 1     | x']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        del back[0]["a"]
        self.assertEqual(want, back)
    date_for_6224: JSONList = [{"a": "x", "b": 1}, {"b": 2}]
    def test_6224(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, self.date_for_6224, ["b", "a@@1"])  # defaultformat="md"
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", res, text)
        want = rev(self.date_for_6224)
        cond = ['| b     | a', '| ----- | -----', '| 2     | ~', '| 1     | x']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        del back[0]["a"]
        self.assertEqual(want, back)
    date_for_6225: JSONList = [{"a": "x", "b": 3}, {"b": 2}]
    def test_6225(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, self.date_for_6225, ["b", "a@@:1"])  # defaultformat="md"
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", res, text)
        want = rev(self.date_for_6225)
        cond = ['| b     | a', '| ----- | -----', '| 2     | ~', '| 3     | x']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        del back[0]["a"]
        self.assertEqual(want, back)
    date_for_6226: JSONList = [{"a": "x", "b": 1}, {"b": 2}]
    def test_6226(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, self.date_for_6226, ["b@@:3", "a@@:1"])  # defaultformat="md"
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", res, text)
        want = rev(self.date_for_6226)
        cond = ['| b     | a', '| ----- | -----', '| 2     | ~', '| 1     | x']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        del back[0]["a"]
        self.assertEqual(want, back)
    date_for_6231: JSONList = [{"a": "x", "b": 3}, {"b": 2, "a": "y"}]
    def test_6231(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, self.date_for_6231, ["b@@:1", "a@@:3"])  # defaultformat="md"
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", res, text)
        want = rev(self.date_for_6231)
        cond = ['| b     | a', '| ----- | -----', '| 2     | y', '| 3     | x']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    date_for_6232: JSONList = [{"a": "x", "b": 3}, {"b": 2, "a": "y"}]
    def test_6232(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, self.date_for_6232, ["b@@:3", "a@@:1"])  # defaultformat="md"
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", res, text)
        want = self.date_for_6232
        cond = ['| b     | a', '| ----- | -----', '| 3     | x', '| 2     | y']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    date_for_6241: JSONList = [{"a": "x", "b": 3}, {"b": 2, "a": "y"}]
    def test_6241(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, self.date_for_6241, ["b:02i@@:1", "a:s@@:3"])  # defaultformat="md"
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", res, text)
        want = rev(self.date_for_6241)
        cond = ['| b     | a', '| ----- | -----', '| 02    | y', '| 03    | x']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    date_for_6242: JSONList = [{"a": "x", "b": 3}, {"b": 2, "a": "y"}]
    def test_6242(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, self.date_for_6242, ["b:02i@@:3", "a:s@@:1"])  # defaultformat="md"
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", res, text)
        want = self.date_for_6242
        cond = ['| b     | a', '| ----- | -----', '| 03    | x', '| 02    | y']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    date_for_6243: JSONList = [{"a": "x", "b": 3}, {"b": 2, "a": "y"}]
    def test_6243(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, self.date_for_6243, ["b@@:1", "a@@:3"], [
                                        "b:02i", "a:s"])  # defaultformat="md"
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", res, text)
        want = rev(self.date_for_6243)
        # cond = ['| a     | b', '| ----- | -----', '| y     | 02', '| x     | 03']
        cond = ['| b     | a', '| ----- | -----', '| 02    | y', '| 03    | x']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    date_for_6244: JSONList = [{"a": "x", "b": 3}, {"b": 2, "a": "y"}]
    def test_6244(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, self.date_for_6244, ["b@@:3", "a@@:1"], [
                                        "b:02i", "a:s"])  # defaultformat="md"
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", res, text)
        cond = ['| b     | a', '| ----- | -----', '| 02    | y', '| 03    | x']
        want = rev(self.date_for_6244)
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    date_for_6245: JSONList = [{"a": "x", "b": 3}, {"b": 2, "a": "y"}]
    def test_6245(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, self.date_for_6245, ["b@@:1", "a@@:3"], [
                                        "a:s", "b:02i", ])  # defaultformat="md"
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", res, text)
        cond = ['| a     | b', '| ----- | -----', '| x     | 03', '| y     | 02']
        want = self.date_for_6245
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    date_for_6246: JSONList = [{"a": "x", "b": 3}, {"b": 2, "a": "y"}]
    def test_6246(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, self.date_for_6246, ["b@@:3", "a@@:1"], [
                                        "a:s", "b:02i"])  # defaultformat="md"
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", res, text)
        want = self.date_for_6246
        # cond = ['| b     | a', '| ----- | -----', '| 03    | x', '| 02    | y']
        cond = ['| a     | b', '| ----- | -----', '| x     | 03', '| y     | 02']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    date_for_6247: JSONList = [{"a": "x", "b": 3}, {"b": 2, "a": "y"}]
    def test_6247(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, self.date_for_6247, ["b@@:1", "a@@:3"], [
                                        "a:s@@4:1", "b:02i", ])  # defaultformat="md"
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", res, text)
        want = self.date_for_6247
        cond = ['| a     | b', '| ----- | -----', '| x     | 03', '| y     | 02']
        want = self.date_for_6247
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    date_for_6248: JSONList = [{"a": "x", "b": 3}, {"b": 2, "a": "y"}]
    def test_6248(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, self.date_for_6248, ["b@@:3", "a@@:1"], [
                                        "a:s@@1:4", "b:02i"])  # defaultformat="md"
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", res, text)
        want = self.date_for_6248
        cond = ['| a     | b', '| ----- | -----', '| x     | 03', '| y     | 02']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    date_for_6251: JSONList = [{"a": "x", "b": 3}, {"b": 2, "a": "y"}]
    def test_6251(self) -> None:
        tmp = self.testdir()
        out = path.join(tmp, "output.md")
        res = tabtotext.print_tabtotext(out, self.date_for_6251, ["b:02i@@:1", "a:s@@:3"])
        logg.info("print_tabtotext %s", res)
        size = path.getsize(out)
        logg.info("generated [%s] %s", size, out)
        text = open(out).read()
        logg.debug("%s => %s", res, text)
        want = rev(self.date_for_6251)
        cond = ['| b     | a', '| ----- | -----', '| 02    | y', '| 03    | x']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    date_for_6252: JSONList = [{"a": "x", "b": 3}, {"b": 2, "a": "y"}]
    def test_6252(self) -> None:
        tmp = self.testdir()
        out = path.join(tmp, "output.md")
        res = tabtotext.print_tabtotext(out, self.date_for_6252, ["b:02i@@:3", "a:s@@:1"])
        logg.info("print_tabtotext %s", res)
        size = path.getsize(out)
        logg.info("generated [%s] %s", size, out)
        text = open(out).read()
        logg.debug("%s => %s", res, text)
        want = self.date_for_6252
        cond = ['| b     | a', '| ----- | -----', '| 03    | x', '| 02    | y']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    date_for_6253: JSONList = [{"a": "x", "b": 3}, {"b": 2, "a": "y"}]
    def test_6253(self) -> None:
        tmp = self.testdir()
        out = path.join(tmp, "output.md")
        res = tabtotext.print_tabtotext(out, self.date_for_6253, ["b@@:1", "a@@:3"], ["b:02i", "a:s"])
        logg.info("print_tabtotext %s", res)
        size = path.getsize(out)
        logg.info("generated [%s] %s", size, out)
        text = open(out).read()
        logg.debug("%s => %s", res, text)
        want = rev(self.date_for_6253)
        # cond = ['| a     | b', '| ----- | -----', '| y     | 02', '| x     | 03']
        cond = ['| b     | a', '| ----- | -----', '| 02    | y', '| 03    | x']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    date_for_6254: JSONList = [{"a": "x", "b": 3}, {"b": 2, "a": "y"}]
    def test_6254(self) -> None:
        tmp = self.testdir()
        out = path.join(tmp, "output.md")
        res = tabtotext.print_tabtotext(out, self.date_for_6254, ["b@@:3", "a@@:1"], ["b:02i", "a:s"])
        logg.info("print_tabtotext %s", res)
        size = path.getsize(out)
        logg.info("generated [%s] %s", size, out)
        text = open(out).read()
        logg.debug("%s => %s", res, text)
        cond = ['| b     | a', '| ----- | -----', '| 02    | y', '| 03    | x']
        want = rev(self.date_for_6254)
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6403(self) -> None:
        text = tabtotext.tabtoGFM(test003)
        logg.debug("%s => %s", test003, text)
        want = LIST
        cond = ['', '']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6404(self) -> None:
        text = tabtotext.tabtoGFM(test004)
        logg.debug("%s => %s", test004, text)
        want = LIST
        cond = ['', '', '']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6405(self) -> None:
        text = tabtotext.tabtoGFM(test005)
        logg.debug("%s => %s", test005, text)
        want = test005
        cond = ['| a', '| -----', '| x']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6406(self) -> None:
        text = tabtotext.tabtoGFM(test006)
        logg.debug("%s => %s", test006, text)
        want = test006
        cond = ['| a     | b', '| ----- | -----', '| x     | y']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6407(self) -> None:
        text = tabtotext.tabtoGFM(test007)
        logg.debug("%s => %s", test007, text)
        want = test007Q
        cond = ['| a     | b', '| ----- | -----', '| x     | y', '| ~     | v']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6408(self) -> None:
        text = tabtotext.tabtoGFM(test008)
        logg.debug("%s => %s", test008, text)
        want = test008Q
        cond = ['| a     | b', '| ----- | -----', '| x     | ~', '| ~     | v']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6409(self) -> None:
        text = tabtotext.tabtoGFM(test009)
        logg.debug("%s => %s", test009, text)
        want = test009Q
        cond = ['| b', '| -----', '| ~', '| v']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6411(self) -> None:
        text = tabtotext.tabtoGFM(test011)
        logg.debug("%s => %s", test011, text)
        want = test011
        cond = ['| b', '| -----', '| ~']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6412(self) -> None:
        text = tabtotext.tabtoGFM(test012)
        logg.debug("%s => %s", test012, text)
        want = test012
        cond = ['| b', '| -----', '| (no)']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6413(self) -> None:
        text = tabtotext.tabtoGFM(test013)
        logg.debug("%s => %s", test013, text)
        want = test013
        cond = ['| b', '| -----', '| (yes)']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6414(self) -> None:
        text = tabtotext.tabtoGFM(test014)
        logg.debug("%s => %s", test014, text)
        want = test014
        cond = ['| b', '| -----', '|']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6415(self) -> None:
        text = tabtotext.tabtoGFM(test015)
        logg.debug("%s => %s", test015, text)
        want = test015Q
        cond = ['| b', '| -----', '| 5678']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6416(self) -> None:
        text = tabtotext.tabtoGFM(test016)
        logg.debug("%s => %s", test016, text)
        want = test016
        cond = ['| b', '| -----', '| 123']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6417(self) -> None:
        text = tabtotext.tabtoGFM(test017)
        logg.debug("%s => %s", test017, text)
        want = test017
        cond = ['| b', '| ------', '| 123.40']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6418(self) -> None:
        text = tabtotext.tabtoGFM(test018)
        logg.debug("%s => %s", test018, text)
        want = test018
        cond = ['| b', '| ----------', '| 2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6419(self) -> None:
        text = tabtotext.tabtoGFM(test019)
        logg.debug("%s => %s", test019, text)
        want = test019Q
        cond = ['| b', '| ----------', '| 2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6420(self) -> None:
        text = tabtotext.tabtoGFM(table01)
        logg.debug("%s => %s", table01, text)
        want = table01N
        cond = ['| a     | b', '| ----- | -----', '| x y   | ~', '| ~     | 1']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6421(self) -> None:
        text = tabtotext.tabtoGFM(table02)
        logg.debug("%s => %s", table02, text)
        want = table02N
        cond = ['| a     | b', '| ----- | -----', '| x     | 0', '| ~     | 2']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6422(self) -> None:
        text = tabtotext.tabtoGFM(table22)
        logg.debug("%s => %s", table22, text)
        want = table22
        cond = ['| a     | b', '| ----- | -----', '| x     | 3', '| y     | 2']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6423(self) -> None:
        text = tabtotext.tabtoGFM(table33)
        logg.debug("%s => %s", table33, text)
        want = table33Q
        cond = ['| a     | b     | c', '| ----- | ----- | ----------',
                '| x     | 3     | 2021-12-31', '| y     | 2     | 2021-12-30',
                '| ~     | ~     | 2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6431(self) -> None:
        text = tabtotext.tabtoGFM(test011, legend=["a result", "was found"])
        logg.debug("%s => %s", test011, text)
        want = test011
        cond = ['| b', '| -----', '| ~', '', '- a result', '- was found']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6432(self) -> None:
        text = tabtotext.tabtoGFM(test012, legend=["a result", "was found"])
        logg.debug("%s => %s", test012, text)
        want = test012
        cond = ['| b', '| -----', '| (no)', '', '- a result', '- was found']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6433(self) -> None:
        text = tabtotext.tabtoGFM(test013, legend=["a result", "was found"])
        logg.debug("%s => %s", test013, text)
        want = test013
        cond = ['| b', '| -----', '| (yes)', '', '- a result', '- was found']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6434(self) -> None:
        text = tabtotext.tabtoGFM(test014, legend=["a result", "was found"])
        logg.debug("%s => %s", test014, text)
        want = test014
        cond = ['| b', '| -----', '|', '', '- a result', '- was found']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6435(self) -> None:
        text = tabtotext.tabtoGFM(test015, legend=["a result", "was found"])
        logg.debug("%s => %s", test015, text)
        want = test015Q
        cond = ['| b', '| -----', '| 5678', '', '- a result', '- was found']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6436(self) -> None:
        text = tabtotext.tabtoGFM(test016, legend=["a result", "was found"])
        logg.debug("%s => %s", test016, text)
        want = test016
        cond = ['| b', '| -----', '| 123', '', '- a result', '- was found']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6437(self) -> None:
        text = tabtotext.tabtoGFM(test017, legend=["a result", "was found"])
        logg.debug("%s => %s", test017, text)
        want = test017
        cond = ['| b', '| ------', '| 123.40', '', '- a result', '- was found']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6438(self) -> None:
        text = tabtotext.tabtoGFM(test018, legend=["a result", "was found"])
        logg.debug("%s => %s", test018, text)
        want = test018
        cond = ['| b', '| ----------', '| 2021-12-31', '', '- a result', '- was found']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6439(self) -> None:
        text = tabtotext.tabtoGFM(test019, legend=["a result", "was found"])
        logg.debug("%s => %s", test019, text)
        want = test019Q
        cond = ['| b', '| ----------', '| 2021-12-31', '', '- a result', '- was found']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)

    def test_6444(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        text = tabtotext.tabtoGFM(itemlist, sorts=['b', 'a'])
        logg.debug("%s => %s", test004, text)
        cond = ['| b     | a', '| ----- | -----', '| 1     | y', '| 2     | x']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        want = [{'a': 'y', 'b': 1}, {'a': 'x', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_6445(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}, {'c': 'h'}]
        text = tabtotext.tabtoGFM(itemlist, sorts=['b', 'a'])
        logg.debug("%s => %s", test004, text)
        cond = ['| b     | a     | c', '| ----- | ----- | -----',
                '| 1     | y     | ~', '| 2     | x     | ~', '| ~     | ~     | h', ]
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        want = [{'a': 'y', 'b': 1, 'c': None}, {'a': 'x', 'b': 2, 'c': None}, {'a': None, 'b': None, 'c': "h"}, ]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_6446(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}, {'c': 'h'}]
        text = tabtotext.tabtoGFM(itemlist, sorts=['b', 'a'], reorder=['a', 'b'])
        logg.debug("%s => %s", test004, text)
        cond = ['| a     | b     | c', '| ----- | ----- | -----',
                '| y     | 1     | ~', '| x     | 2     | ~', '| ~     | ~     | h', ]
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        want = [{'a': 'y', 'b': 1, 'c': None}, {'a': 'x', 'b': 2, 'c': None}, {'a': None, 'b': None, 'c': "h"}, ]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_6460(self) -> None:
        text = tabtotext.tabtoGFM(table01, ["b", "a"])
        logg.debug("%s => %s", table01, text)
        want = table01N
        cond = ['| b     | a', '| ----- | -----', '| ~     | x y', '| 1     | ~']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6461(self) -> None:
        text = tabtotext.tabtoGFM(table02, ["b", "a"])
        logg.debug("%s => %s", table02, text)
        want = table02N
        cond = ['| b     | a', '| ----- | -----', '| 0     | x', '| 2     | ~']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6462(self) -> None:
        text = tabtotext.tabtoGFM(table22, ["b", "a"])
        logg.debug("%s => %s", table22, text)
        want = table22
        cond = ['| b     | a', '| ----- | -----', '| 3     | x', '| 2     | y']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6463(self) -> None:
        text = tabtotext.tabtoGFM(table33, ["b", "a"])
        logg.debug("%s => %s", table33, text)
        want = table33Q
        cond = ['| b     | a     | c',
                '| ----- | ----- | ----------',
                '| 3     | x     | 2021-12-31',
                '| 2     | y     | 2021-12-30',
                '| ~     | ~     | 2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6465(self) -> None:
        text = tabtotext.tabtoGFM(table33, ["c", "a"])
        logg.debug("%s => %s", table33, text)
        want = table33Q
        cond = ['| c          | a     | b',
                '| ---------- | ----- | -----',
                '| 2021-12-31 | x     | 3',
                '| 2021-12-30 | y     | 2',
                '| 2021-12-31 | ~     | ~']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6466(self) -> None:
        text = tabtotext.tabtoGFM(table02, ["b", "a"], ["b", "a"])
        logg.debug("%s => %s", table02, text)
        want = table02N
        cond = ['| b     | a', '| ----- | -----', '| 0     | x', '| 2     | ~']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6467(self) -> None:
        text = tabtotext.tabtoGFM(table22, ["b", "a"], ["b", "a"])
        logg.debug("%s => %s", table22, text)
        want = rev(table22)
        cond = ['| b     | a', '| ----- | -----', '| 2     | y', '| 3     | x']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6468(self) -> None:
        text = tabtotext.tabtoGFM(table33, ["b", "a"], ["b", "a", "c"])
        logg.debug("%s => %s", table33, text)
        want = rev(table33Q[:2]) + table33Q[2:]
        cond = ['| b     | a     | c', '| ----- | ----- | ----------',
                '| 2     | y     | 2021-12-30', '| 3     | x     | 2021-12-31',
                '| ~     | ~     | 2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6469(self) -> None:
        text = tabtotext.tabtoGFM(table33, ["c", "a"], ["c", "a", "b"])
        logg.debug("%s => %s", table33, text.splitlines())
        want = rev(table33Q[:2]) + table33Q[2:]
        cond = ['| c          | a     | b', '| ---------- | ----- | -----',
                '| 2021-12-30 | y     | 2', '| 2021-12-31 | x     | 3',
                '| 2021-12-31 | ~     | ~']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6530(self) -> None:
        text = tabtotext.tabtoGFM(table01, ["a|b"])
        logg.debug("%s => %s", table01, text.splitlines())
        want = table01N
        cond = ['| a     | b', '| ----- | -----', '| x y   | ~', '| ~     | 1']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6531(self) -> None:
        text = tabtotext.tabtoGFM(table02, ["a|b"])
        logg.debug("%s => %s", table02, text.splitlines())
        want = table02N
        cond = ['| a     | b', '| ----- | -----', '| x     | 0', '| ~     | 2']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6532(self) -> None:
        text = tabtotext.tabtoGFM(table22, ["a|b"])
        logg.debug("%s => %s", table22, text.splitlines())
        want = table22
        cond = ['| a     | b', '| ----- | -----', '| x     | 3', '| y     | 2']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6533(self) -> None:
        text = tabtotext.tabtoGFM(table33, ["a|b"])
        logg.debug("%s => %s", table33, text.splitlines())
        want = table33Q
        cond = ['| a     | b     | c', '| ----- | ----- | ----------',
                '| x     | 3     | 2021-12-31', '| y     | 2     | 2021-12-30',
                '| ~     | ~     | 2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(_date(want), back)
    def test_6534(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"])
        logg.debug("%s => %s", table44, text.splitlines())
        want = table44N
        cond = ['| a     | b     | c     | d', '| ----- | ----- | ----- | -----',
                '| x     | 3     | (yes) | 0.40', '| y     | 2     | (no)  | 0.30',
                '| ~     | ~     | (yes) | 0.20', '| y     | 1     | ~     | 0.10']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6535(self) -> None:
        text = tabtotext.tabtoGFM(table01, ["b|a"])
        logg.debug("%s => %s", table01, text.splitlines())
        want = table01N
        cond = ['| b     | a', '| ----- | -----', '| ~     | x y', '| 1     | ~']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6536(self) -> None:
        text = tabtotext.tabtoGFM(table02, ["b|a"])
        logg.debug("%s => %s", table02, text.splitlines())
        want = table02N
        cond = ['| b     | a', '| ----- | -----', '| 0     | x', '| 2     | ~']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6537(self) -> None:
        text = tabtotext.tabtoGFM(table22, ["b|a"])
        logg.debug("%s => %s", table22, text.splitlines())
        want = table22
        cond = ['| b     | a', '| ----- | -----', '| 3     | x', '| 2     | y']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6538(self) -> None:
        text = tabtotext.tabtoGFM(table33, ["b|a"])
        logg.debug("%s => %s", table33, text.splitlines())
        want = table33Q
        cond = ['| b     | a     | c', '| ----- | ----- | ----------',
                '| 3     | x     | 2021-12-31', '| 2     | y     | 2021-12-30',
                '| ~     | ~     | 2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6539(self) -> None:
        text = tabtotext.tabtoGFM(table33, ["b|c|a"])
        logg.debug("%s => %s", table33, text.splitlines())
        want = table33Q
        cond = ['| b     | c          | a', '| ----- | ---------- | -----',
                '| 3     | 2021-12-31 | x', '| 2     | 2021-12-30 | y',
                '| ~     | 2021-12-31 | ~']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6594(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["a|b"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| a     | b', '| ----- | -----',
                '| ~     | ~', '| x     | 3',
                '| y     | 1', '| y     | 2']
        self.assertEqual(cond, text.splitlines())
    def test_6595(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["b|a"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| b     | a', '| ----- | -----',
                '| 1     | y', '| 2     | y',
                '| 3     | x', '| ~     | ~']
        self.assertEqual(cond, text.splitlines())
    def test_6596(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["b|d"])
        logg.debug("%s => %s", table44, text.splitlines())

        cond = ['| b     | d', '| ----- | -----',
                '| 1     | 0.10', '| 2     | 0.30',
                '| 3     | 0.40', '| ~     | 0.20']
        self.assertEqual(cond, text.splitlines())
    def test_6598(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["a|b|d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| a     | b     | d', '| ----- | ----- | -----',
                '| ~     | ~     | 0.20', '| x     | 3     | 0.40',
                '| y     | 1     | 0.10', '| y     | 2     | 0.30']
        self.assertEqual(cond, text.splitlines())
    def test_6599(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["b|c|a"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| b     | c     | a', '| ----- | ----- | -----',
                '| 1     | ~     | y', '| 2     | (no)  | y',
                '| 3     | (yes) | x', '| ~     | (yes) | ~']
        self.assertEqual(cond, text.splitlines())
    def test_6600(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["b|d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| b     | d', '| ----- | -----',
                '| 1     | 0.10', '| 2     | 0.30',
                '| 3     | 0.40', '| ~     | 0.20']
        self.assertEqual(cond, text.splitlines())
    def test_6601(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["b:02.1f|d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['|     b | d', '| ----: | -----',
                '|   1.0 | 0.10', '|   2.0 | 0.30',
                '|   3.0 | 0.40', '|     ~ | 0.20']
        self.assertEqual(cond, text.splitlines())
    def test_6602(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b:02.1f"], ["b|d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['|     b | d', '| ----: | -----',
                '|   1.0 | 0.10', '|   2.0 | 0.30',
                '|   3.0 | 0.40', '|     ~ | 0.20']
        self.assertEqual(cond, text.splitlines())
    def test_6608(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["#|b|d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| # | b     | d',
                '| - | ----- | -----',
                '| 1 | 3     | 0.40',
                '| 2 | 2     | 0.30',
                '| 3 | ~     | 0.20',
                '| 4 | 1     | 0.10']
        self.assertEqual(cond, text.splitlines())
    def test_6609(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["b|d|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| b     | d     | #',
                '| ----- | ----- | -',
                '| 1     | 0.10  | 4',
                '| 2     | 0.30  | 2',
                '| 3     | 0.40  | 1',
                '| ~     | 0.20  | 3']
        self.assertEqual(cond, text.splitlines())
    def test_6610(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["b>|d|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| b     | d     | #',
                '| ----- | ----- | -',
                '| 1     | 0.10  | 4',
                '| 2     | 0.30  | 2',
                '| 3     | 0.40  | 1']
        self.assertEqual(cond, text.splitlines())
    def test_6611(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["b>x|d|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| b     | d     | #',
                '| ----- | ----- | -',
                '| 1     | 0.10  | 4',
                '| 2     | 0.30  | 2',
                '| 3     | 0.40  | 1',
                '| ~     | 0.20  | 3']
        self.assertEqual(cond, text.splitlines())
    def test_6612(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["b>1|d|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| b     | d     | #',
                '| ----- | ----- | -',
                '| 2     | 0.30  | 2',
                '| 3     | 0.40  | 1']
        self.assertEqual(cond, text.splitlines())
    def test_6613(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["b>=2|d|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| b     | d     | #',
                '| ----- | ----- | -',
                '| 2     | 0.30  | 2',
                '| 3     | 0.40  | 1']
        self.assertEqual(cond, text.splitlines())
    def test_6614(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["b>2|d|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| b     | d     | #', '| ----- | ----- | -', '| 3     | 0.40  | 1']
        self.assertEqual(cond, text.splitlines())
    def test_6615(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["b<=2|d|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| b     | d     | #',
                '| ----- | ----- | -',
                '| 1     | 0.10  | 4',
                '| 2     | 0.30  | 2',
                '| ~     | 0.20  | 3']
        self.assertEqual(cond, text.splitlines())
    def test_6616(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["b<2|d|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| b     | d     | #',
                '| ----- | ----- | -',
                '| 1     | 0.10  | 4',
                '| ~     | 0.20  | 3']
        self.assertEqual(cond, text.splitlines())
    def test_6617(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["b==1|d|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| b     | d     | #', '| ----- | ----- | -', '| 1     | 0.10  | 4']
        self.assertEqual(cond, text.splitlines())
    def test_6618(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["b=~1|d|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| b     | d     | #', '| ----- | ----- | -', '| 1     | 0.10  | 4']
        self.assertEqual(cond, text.splitlines())
    def test_6619(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["b<>1|d|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| b     | d     | #',
                '| ----- | ----- | -',
                '| 2     | 0.30  | 2',
                '| 3     | 0.40  | 1',
                '| ~     | 0.20  | 3']
        self.assertEqual(cond, text.splitlines())
    def test_6620(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["b|d>|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| b     | d     | #',
                '| ----- | ----- | -',
                '| 1     | 0.10  | 4',
                '| 2     | 0.30  | 2',
                '| 3     | 0.40  | 1',
                '| ~     | 0.20  | 3']
        self.assertEqual(cond, text.splitlines())
    def test_6621(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["b|d>x|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| b     | d     | #',
                '| ----- | ----- | -',
                '| 1     | 0.10  | 4',
                '| 2     | 0.30  | 2',
                '| 3     | 0.40  | 1',
                '| ~     | 0.20  | 3']
        self.assertEqual(cond, text.splitlines())
    def test_6622(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["b|d>0.1|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| b     | d     | #',
                '| ----- | ----- | -',
                '| 2     | 0.30  | 2',
                '| 3     | 0.40  | 1',
                '| ~     | 0.20  | 3']
        self.assertEqual(cond, text.splitlines())
    def test_6623(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["b|d>=0.2|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| b     | d     | #',
                '| ----- | ----- | -',
                '| 2     | 0.30  | 2',
                '| 3     | 0.40  | 1',
                '| ~     | 0.20  | 3']
        self.assertEqual(cond, text.splitlines())
    def test_6624(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["b|d>0.2|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| b     | d     | #',
                '| ----- | ----- | -',
                '| 2     | 0.30  | 2',
                '| 3     | 0.40  | 1']
        self.assertEqual(cond, text.splitlines())
    def test_6625(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["b|d<=0.2|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| b     | d     | #',
                '| ----- | ----- | -',
                '| 1     | 0.10  | 4',
                '| ~     | 0.20  | 3']
        self.assertEqual(cond, text.splitlines())
    def test_6626(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["b|d<0.2|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| b     | d     | #', '| ----- | ----- | -', '| 1     | 0.10  | 4']
        self.assertEqual(cond, text.splitlines())
    def test_6627(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["b|d==0.1|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| b     | d     | #', '| ----- | ----- | -', '| 1     | 0.10  | 4']
        self.assertEqual(cond, text.splitlines())
    def test_6628(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["b|d=~0.1|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| b     | d     | #', '| ----- | ----- | -', '| 1     | 0.10  | 4']
        self.assertEqual(cond, text.splitlines())
    def test_6629(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["b|d<>0.1|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| b     | d     | #',
                '| ----- | ----- | -',
                '| 2     | 0.30  | 2',
                '| 3     | 0.40  | 1',
                '| ~     | 0.20  | 3']
        self.assertEqual(cond, text.splitlines())
    def test_6630(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["b|a>|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| b     | a     | #',
                '| ----- | ----- | -',
                '| 1     | y     | 4',
                '| 2     | y     | 2',
                '| 3     | x     | 1']
        self.assertEqual(cond, text.splitlines())
    def test_6632(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["b|a>x|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| b     | a     | #',
                '| ----- | ----- | -',
                '| 1     | y     | 4',
                '| 2     | y     | 2',
                '| ~     | ~     | 3']
        self.assertEqual(cond, text.splitlines())
    def test_6633(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["b|a>=y|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| b     | a     | #',
                '| ----- | ----- | -',
                '| 1     | y     | 4',
                '| 2     | y     | 2',
                '| ~     | ~     | 3']
        self.assertEqual(cond, text.splitlines())
    def test_6634(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["b|a>x|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| b     | a     | #',
                '| ----- | ----- | -',
                '| 1     | y     | 4',
                '| 2     | y     | 2',
                '| ~     | ~     | 3']
        self.assertEqual(cond, text.splitlines())
    def test_6635(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["b|a<=y|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| b     | a     | #',
                '| ----- | ----- | -',
                '| 1     | y     | 4',
                '| 2     | y     | 2',
                '| 3     | x     | 1',
                '| ~     | ~     | 3']
        self.assertEqual(cond, text.splitlines())
    def test_6636(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["b|a<y|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| b     | a     | #',
                '| ----- | ----- | -',
                '| 3     | x     | 1',
                '| ~     | ~     | 3']
        self.assertEqual(cond, text.splitlines())
    def test_6637(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["b|a==y|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| b     | a     | #',
                '| ----- | ----- | -',
                '| 1     | y     | 4',
                '| 2     | y     | 2',
                '| ~     | ~     | 3']
        self.assertEqual(cond, text.splitlines())
    def test_6638(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["b|a=~y|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| b     | a     | #',
                '| ----- | ----- | -',
                '| 1     | y     | 4',
                '| 2     | y     | 2',
                '| ~     | ~     | 3']
        self.assertEqual(cond, text.splitlines())
    def test_6639(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["b|a<>y|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| b     | a     | #',
                '| ----- | ----- | -',
                '| 3     | x     | 1',
                '| ~     | ~     | 3']
        self.assertEqual(cond, text.splitlines())
    def test_6640(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["b|c>|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| b     | c     | #',
                '| ----- | ----- | -',
                '| 1     | ~     | 4',
                '| 3     | (yes) | 1',
                '| ~     | (yes) | 3']
        self.assertEqual(cond, text.splitlines())
    def test_6641(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["b|c<>|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| b     | c     | #',
                '| ----- | ----- | -',
                '| 1     | ~     | 4',
                '| 2     | (no)  | 2',
                '| 3     | (yes) | 1',
                '| ~     | (yes) | 3']
        self.assertEqual(cond, text.splitlines())
    def test_6642(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["b|c>false|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| b     | c     | #',
                '| ----- | ----- | -',
                '| 1     | ~     | 4',
                '| 3     | (yes) | 1',
                '| ~     | (yes) | 3']
        self.assertEqual(cond, text.splitlines())
    def test_6643(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["b|c>=true|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| b     | c     | #',
                '| ----- | ----- | -',
                '| 1     | ~     | 4',
                '| 3     | (yes) | 1',
                '| ~     | (yes) | 3']
        self.assertEqual(cond, text.splitlines())
    def test_6644(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["b|c>true|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| b     | c     | #', '| ----- | ----- | -', '| 1     | ~     | 4']
        self.assertEqual(cond, text.splitlines())
    def test_6645(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["b|c<=true|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| b     | c     | #',
                '| ----- | ----- | -',
                '| 1     | ~     | 4',
                '| 2     | (no)  | 2',
                '| 3     | (yes) | 1',
                '| ~     | (yes) | 3']
        self.assertEqual(cond, text.splitlines())
    def test_6646(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["b|c<true|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| b     | c     | #',
                '| ----- | ----- | -',
                '| 1     | ~     | 4',
                '| 2     | (no)  | 2']
        self.assertEqual(cond, text.splitlines())
    def test_6647(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["b|c==true|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| b     | c     | #',
                '| ----- | ----- | -',
                '| 1     | ~     | 4',
                '| 3     | (yes) | 1',
                '| ~     | (yes) | 3']
        self.assertEqual(cond, text.splitlines())
    def test_6648(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["b|c=~true|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| b     | c     | #',
                '| ----- | ----- | -',
                '| 1     | ~     | 4',
                '| 3     | (yes) | 1',
                '| ~     | (yes) | 3']
        self.assertEqual(cond, text.splitlines())
    def test_6649(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["b|c<>true|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| b     | c     | #',
                '| ----- | ----- | -',
                '| 1     | ~     | 4',
                '| 2     | (no)  | 2',
                '| 3     | (yes) | 1',
                '| ~     | (yes) | 3']
        self.assertEqual(cond, text.splitlines())
    def test_6660(self) -> None:
        text = tabtotext.tabtoGFM(table33, ["a|b"], ["b|c>|#"])
        logg.debug("%s => %s", table33, text.splitlines())
        cond = ['| b     | c          | #',
                '| ----- | ---------- | -',
                '| 2     | 2021-12-30 | 2',
                '| 3     | 2021-12-31 | 1',
                '| ~     | 2021-12-31 | 3']
        self.assertEqual(cond, text.splitlines())
    def test_6661(self) -> None:
        text = tabtotext.tabtoGFM(table33, ["a|b"], ["b|c<>|#"])
        logg.debug("%s => %s", table33, text.splitlines())
        cond = ['| b     | c          | #',
                '| ----- | ---------- | -',
                '| 2     | 2021-12-30 | 2',
                '| 3     | 2021-12-31 | 1',
                '| ~     | 2021-12-31 | 3']
        self.assertEqual(cond, text.splitlines())
    def test_6662(self) -> None:
        text = tabtotext.tabtoGFM(table33, ["a|b"], ["b|c>2021-12-30|#"])
        logg.debug("%s => %s", table33, text.splitlines())
        cond = ['| b     | c          | #',
                '| ----- | ---------- | -',
                '| 3     | 2021-12-31 | 1',
                '| ~     | 2021-12-31 | 3']
        self.assertEqual(cond, text.splitlines())
    def test_6663(self) -> None:
        text = tabtotext.tabtoGFM(table33, ["a|b"], ["b|c>=2021-12-30|#"])
        logg.debug("%s => %s", table33, text.splitlines())
        cond = ['| b     | c          | #',
                '| ----- | ---------- | -',
                '| 2     | 2021-12-30 | 2',
                '| 3     | 2021-12-31 | 1',
                '| ~     | 2021-12-31 | 3']
        self.assertEqual(cond, text.splitlines())
    def test_6664(self) -> None:
        text = tabtotext.tabtoGFM(table33, ["a|b"], ["b|c>2021-12-31|#"])
        logg.debug("%s => %s", table33, text.splitlines())
        cond = ['| b     | c          | #', '| ----- | ---------- | -']
        self.assertEqual(cond, text.splitlines())
    def test_6665(self) -> None:
        text = tabtotext.tabtoGFM(table33, ["a|b"], ["b|c<=2021-12-31|#"])
        logg.debug("%s => %s", table33, text.splitlines())
        cond = ['| b     | c          | #',
                '| ----- | ---------- | -',
                '| 2     | 2021-12-30 | 2',
                '| 3     | 2021-12-31 | 1',
                '| ~     | 2021-12-31 | 3']
        self.assertEqual(cond, text.splitlines())
    def test_6666(self) -> None:
        text = tabtotext.tabtoGFM(table33, ["a|b"], ["b|c<2021-12-31|#"])
        logg.debug("%s => %s", table33, text.splitlines())
        cond = ['| b     | c          | #',
                '| ----- | ---------- | -',
                '| 2     | 2021-12-30 | 2']
        self.assertEqual(cond, text.splitlines())
    def test_6667(self) -> None:
        text = tabtotext.tabtoGFM(table33, ["a|b"], ["b|c==2021-12-31|#"])
        logg.debug("%s => %s", table33, text.splitlines())
        cond = ['| b     | c          | #',
                '| ----- | ---------- | -',
                '| 3     | 2021-12-31 | 1',
                '| ~     | 2021-12-31 | 3']
        self.assertEqual(cond, text.splitlines())
    def test_6668(self) -> None:
        text = tabtotext.tabtoGFM(table33, ["a|b"], ["b|c=~2021-12-31|#"])
        logg.debug("%s => %s", table33, text.splitlines())
        cond = ['| b     | c          | #',
                '| ----- | ---------- | -',
                '| 3     | 2021-12-31 | 1',
                '| ~     | 2021-12-31 | 3']
        self.assertEqual(cond, text.splitlines())
    def test_6669(self) -> None:
        text = tabtotext.tabtoGFM(table33, ["a|b"], ["b|c<>2021-12-31|#"])
        logg.debug("%s => %s", table33, text.splitlines())
        cond = ['| b     | c          | #',
                '| ----- | ---------- | -',
                '| 2     | 2021-12-30 | 2']
        self.assertEqual(cond, text.splitlines())
    def test_6702(self) -> None:
        text = tabtotext.tabtoGFM(table02, ["a|b"], ["{a}+{b}"])
        logg.debug("%s => %s", table02, text.splitlines())
        cond = ['| a b', '| -----', '| x+0', '| ~+2']
        self.assertEqual(cond, text.splitlines())
    def test_6703(self) -> None:
        text = tabtotext.tabtoGFM(table33, ["a|b"], ["{a}+{b} = {c}"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| a b c',
                '| ----------------',
                '| x+3 = 2021-12-31',
                '| y+2 = 2021-12-30',
                '| ~+~ = 2021-12-31']
        self.assertEqual(cond, text.splitlines())
    def test_6704(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["{a}+{b} = {c}"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| a b c',
                '| -----------',
                '| x+3 = (yes)',
                '| y+1 = ~',
                '| y+2 = (no)',
                '| ~+~ = (yes)']
        self.assertEqual(cond, text.splitlines())
    def test_6705(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["{a}+{b} = {c}", "d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| a b c       | d', '| ----------- | -----',
                '| x+3 = (yes) | 0.40', '| y+1 = ~     | 0.10',
                '| y+2 = (no)  | 0.30', '| ~+~ = (yes) | 0.20']
        self.assertEqual(cond, text.splitlines())
    def test_6706(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["d", "{a}+{b} = {c}"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| d     | a b c', '| ----- | -----------',
                '| 0.10  | y+1 = ~', '| 0.20  | ~+~ = (yes)',
                '| 0.30  | y+2 = (no)', '| 0.40  | x+3 = (yes)']
        self.assertEqual(cond, text.splitlines())
    def test_6712(self) -> None:
        text = tabtotext.tabtoGFM(table02, ["a|b"], ["{a}+{b}@info"])
        logg.debug("%s => %s", table02, text.splitlines())
        cond = ['| info', '| -----', '| x+0', '| ~+2']
        self.assertEqual(cond, text.splitlines())
    def test_6713(self) -> None:
        text = tabtotext.tabtoGFM(table33, ["a|b"], ["{a}+{b} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| info', '| ----------------', '| x+3 = 2021-12-31', '| y+2 = 2021-12-30', '| ~+~ = 2021-12-31']
        self.assertEqual(cond, text.splitlines())
    def test_6714(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["{a}+{b} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| info', '| -----------',
                '| x+3 = (yes)', '| y+1 = ~',
                '| y+2 = (no)', '| ~+~ = (yes)']
        self.assertEqual(cond, text.splitlines())
    def test_6715(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["{a}+{b} = {c}@info", "d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| info        | d', '| ----------- | -----',
                '| x+3 = (yes) | 0.40', '| y+1 = ~     | 0.10',
                '| y+2 = (no)  | 0.30', '| ~+~ = (yes) | 0.20']
        self.assertEqual(cond, text.splitlines())
    def test_6716(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a|b"], ["d", "{a}+{b} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| d     | info', '| ----- | -----------',
                '| 0.10  | y+1 = ~', '| 0.20  | ~+~ = (yes)',
                '| 0.30  | y+2 = (no)', '| 0.40  | x+3 = (yes)']
        self.assertEqual(cond, text.splitlines())
    def test_6722(self) -> None:
        text = tabtotext.tabtoGFM(table02, ["a@x"], ["{a}+{b}@info"])
        logg.debug("%s => %s", table02, text.splitlines())
        cond = ['| info', '| -----', '| x+0', '| ~+2']
        self.assertEqual(cond, text.splitlines())
    def test_6723(self) -> None:
        text = tabtotext.tabtoGFM(table33, ["a@x"], ["{a}+{b} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| info', '| ----------------',
                '| x+3 = 2021-12-31', '| y+2 = 2021-12-30', '| ~+~ = 2021-12-31']
        self.assertEqual(cond, text.splitlines())
    def test_6724(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a@x"], ["{a}+{b} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| info', '| -----------',
                '| x+3 = (yes)', '| y+1 = ~', '| y+2 = (no)', '| ~+~ = (yes)']
        self.assertEqual(cond, text.splitlines())
    def test_6725(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a@x"], ["{a}+{b} = {c}@info", "d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| info        | d', '| ----------- | -----',
                '| x+3 = (yes) | 0.40', '| y+1 = ~     | 0.10',
                '| y+2 = (no)  | 0.30', '| ~+~ = (yes) | 0.20']
        self.assertEqual(cond, text.splitlines())
    def test_6726(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a@x"], ["d", "{a}+{b} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| d     | info', '| ----- | -----------',
                '| 0.10  | y+1 = ~', '| 0.20  | ~+~ = (yes)',
                '| 0.30  | y+2 = (no)', '| 0.40  | x+3 = (yes)']
        self.assertEqual(cond, text.splitlines())
    def test_6732(self) -> None:
        text = tabtotext.tabtoGFM(table02, ["a@x"], ["{x}+{b}@info"])
        logg.debug("%s => %s", table02, text.splitlines())
        cond = ['| info', '| -----', '| x+0', '| ~+2']
        self.assertEqual(cond, text.splitlines())
    def test_6733(self) -> None:
        text = tabtotext.tabtoGFM(table33, ["a@x"], ["{x}+{b} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| info', '| ----------------', '| x+3 = 2021-12-31',
                '| y+2 = 2021-12-30', '| ~+~ = 2021-12-31']
        self.assertEqual(cond, text.splitlines())
    def test_6734(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a@x"], ["{x}+{b} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| info', '| -----------', '| x+3 = (yes)',
                '| y+1 = ~', '| y+2 = (no)', '| ~+~ = (yes)']
        self.assertEqual(cond, text.splitlines())
    def test_6735(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a@x"], ["{x}+{b} = {c}@info", "d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| info        | d', '| ----------- | -----',
                '| x+3 = (yes) | 0.40',
                '| y+1 = ~     | 0.10',
                '| y+2 = (no)  | 0.30',
                '| ~+~ = (yes) | 0.20']
        self.assertEqual(cond, text.splitlines())
    def test_6736(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a@x"], ["d", "{x}+{b} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| d     | info', '| ----- | -----------',
                '| 0.10  | y+1 = ~', '| 0.20  | ~+~ = (yes)',
                '| 0.30  | y+2 = (no)', '| 0.40  | x+3 = (yes)']
        self.assertEqual(cond, text.splitlines())
    def test_6742(self) -> None:
        text = tabtotext.tabtoGFM(table02, ["a@x|b@y"], ["{x}+{y}@info"])
        logg.debug("%s => %s", table02, text.splitlines())
        cond = ['| info', '| -----', '| x+0', '| ~+2']
        self.assertEqual(cond, text.splitlines())
    def test_6743(self) -> None:
        text = tabtotext.tabtoGFM(table33, ["a@x|b@y"], ["{x}+{y} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| info',
                '| ----------------',
                '| x+3 = 2021-12-31',
                '| y+2 = 2021-12-30',
                '| ~+~ = 2021-12-31']
        self.assertEqual(cond, text.splitlines())
    def test_6744(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a@x|b@y"], ["{x}+{y} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| info',
                '| -----------',
                '| x+3 = (yes)',
                '| y+1 = ~',
                '| y+2 = (no)',
                '| ~+~ = (yes)']
        self.assertEqual(cond, text.splitlines())
    def test_6745(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a@x|b@y"], ["{x}+{y} = {c}@info", "d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| info        | d', '| ----------- | -----',
                '| x+3 = (yes) | 0.40',
                '| y+1 = ~     | 0.10',
                '| y+2 = (no)  | 0.30',
                '| ~+~ = (yes) | 0.20']
        self.assertEqual(cond, text.splitlines())
    def test_6746(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a@x|b@y"], ["d", "{x}+{y} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| d     | info', '| ----- | -----------',
                '| 0.10  | y+1 = ~', '| 0.20  | ~+~ = (yes)',
                '| 0.30  | y+2 = (no)', '| 0.40  | x+3 = (yes)']
        self.assertEqual(cond, text.splitlines())
    def test_6752(self) -> None:
        text = tabtotext.tabtoGFM(table02, ["a@x|b@y"], ["x@info"])
        logg.debug("%s => %s", table02, text.splitlines())
        cond = ['| info', '| -----', '| ~', '| x']
        self.assertEqual(cond, text.splitlines())
    def test_6753(self) -> None:
        text = tabtotext.tabtoGFM(table33, ["a@x|b@y"], ["x@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| info', '| -----', '| ~', '| x', '| y']
        self.assertEqual(cond, text.splitlines())
    def test_6754(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a@x|b@y"], ["x@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| info', '| -----', '| ~', '| x', '| y', '| y']
        self.assertEqual(cond, text.splitlines())
    def test_6755(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a@x|b@y"], ["x@info", "d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| info  | d',
                '| ----- | -----',
                '| ~     | 0.20',
                '| x     | 0.40',
                '| y     | 0.10',
                '| y     | 0.30']
        self.assertEqual(cond, text.splitlines())
    def test_6756(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a@x|b@y"], ["d", "x@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| d     | info',
                '| ----- | -----',
                '| 0.10  | y',
                '| 0.20  | ~',
                '| 0.30  | y',
                '| 0.40  | x']
        self.assertEqual(cond, text.splitlines())
    def test_6762(self) -> None:
        text = tabtotext.tabtoGFM(table02, ["a@x|b@y"], ["x@info|y@mm"])
        logg.debug("%s => %s", table02, text.splitlines())
        cond = ['| info  | mm', '| ----- | -----', '| ~     | 2', '| x     | 0']
        self.assertEqual(cond, text.splitlines())
    def test_6763(self) -> None:
        text = tabtotext.tabtoGFM(table33, ["a@x|b@y"], ["x@info|y@mm"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| info  | mm', '| ----- | -----', '| ~     | ~', '| x     | 3', '| y     | 2']
        self.assertEqual(cond, text.splitlines())
    def test_6764(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a@x|b@y"], ["x@info|y@mm"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| info  | mm',
                '| ----- | -----',
                '| ~     | ~',
                '| x     | 3',
                '| y     | 1',
                '| y     | 2']
        self.assertEqual(cond, text.splitlines())
    def test_6765(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a@x|b@y"], ["x@info|y@mm", "d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| info  | mm    | d',
                '| ----- | ----- | -----',
                '| ~     | ~     | 0.20',
                '| x     | 3     | 0.40',
                '| y     | 1     | 0.10',
                '| y     | 2     | 0.30']
        self.assertEqual(cond, text.splitlines())
    def test_6766(self) -> None:
        text = tabtotext.tabtoGFM(table44, ["a@x|b@y"], ["d", "x@info|y@mm"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['| d     | info  | mm',
                '| ----- | ----- | -----',
                '| 0.10  | y     | 1',
                '| 0.20  | ~     | ~',
                '| 0.30  | y     | 2',
                '| 0.40  | x     | 3']
        self.assertEqual(cond, text.splitlines())
    def test_6801(self) -> None:
        data: JSONList = [{"a": "a b", "c": "c d|e"}, {"a": "g\nh", "c": "s\\t"}]
        text = tabtotext.tabtotext(data, defaultformat="md")
        logg.debug("%s => %s", data, text.splitlines())
        cond = ['| a     | c', '| ----- | ------', '| a b   | c d\\|e', '| g\\', 'h  | s\\\\t']
        self.assertEqual(cond, text.splitlines())
        # scan = tabtotext.tablistscanGFM(text)
        # back = dict(tabtotext.tablistmap(scan))
        back = tabtotext.loadGFM(text)
        want = data
        logg.debug("\n>> %s\n<< %s", data, back)
        self.assertEqual(want, back)
    def test_6802(self) -> None:
        data: JSONList = [{"a": "a b", "c": "c d|e"}, {"a": "g\nh", "c": "s\\t"}]
        tabs: Dict[str, JSONList] = {"data": data}
        text = tabtotext.tablistmakeFMT("md", tabtotext.tablistfor(tabs))
        logg.debug("%s => %s", data, text.splitlines())
        cond = ['| a     | c', '| ----- | ------', '| a b   | c d\\|e', '| g\\', 'h  | s\\\\t']
        self.assertEqual(cond, text.splitlines())
        scan = tabtotext.tablistscanGFM(text)
        back = dict(tabtotext.tablistmap(scan))
        want = {"-1": data}
        logg.debug("\n>> %s\n<< %s", data, back)
        self.assertEqual(want, back)
    def test_6803(self) -> None:
        data: JSONList = [{"a": "a b", "c": "c d|e"}, {"a": "g\nh", "c": "s\\t"}]
        tabs: Dict[str, JSONList] = {"data": data}
        buff = StringIO()
        done = print_tablist(buff, tabtotext.tablistfor(tabs), defaultformat="md")
        text = buff.getvalue()
        logg.debug("%s => %s", data, text.splitlines())
        cond = ['| a     | c', '| ----- | ------', '| a b   | c d\\|e', '| g\\', 'h  | s\\\\t']
        self.assertEqual(cond, text.splitlines())
        scan = tabtotext.tablistscanGFM(text)
        back = dict(tablistmap(scan))
        want = {"-1": data}
        logg.debug("\n>> %s\n<< %s", data, back)
        self.assertEqual(want, back)
    def test_6804(self) -> None:
        test = self.testdir()
        data: JSONList = [{"a": "a b", "c": "c d|e"}, {"a": "g\nh", "c": "s\\t"}]
        tabs: Dict[str, JSONList] = {"data": data}
        filename = F"{test}/tabs.md"
        done = print_tablist(filename, tabtotext.tablistfor(tabs), defaultformat="md")
        text = open(filename).read()
        logg.debug("%s => %s", data, text.splitlines())
        cond = ['| a     | c', '| ----- | ------', '| a b   | c d\\|e', '| g\\', 'h  | s\\\\t']
        self.assertEqual(cond, text.splitlines())
        scan = tabtotext.tablistfile(filename)
        back = dict(tablistmap(scan))
        want = {"-1": data}
        logg.debug("\n>> %s\n<< %s", data, back)
        self.assertEqual(want, back)
        self.rm_testdir()
    def test_6811(self) -> None:
        tablist = {"table01": table01, "table02": table02}
        text = tabtotext.tablistmakeFMT("md", tabtotext.tablistfor(tablist))
        logg.debug("%s => %s", tablist, text.splitlines())
        cond = ['',
                '## table01',
                '| a     | b',
                '| ----- | -----',
                '| x y   | ~',
                '| ~     | 1',
                '',
                '## table02',
                '| a     | b',
                '| ----- | -----',
                '| x     | 0',
                '| ~     | 2']

        self.assertEqual(cond, text.splitlines())
        want = {"table01": table01N, "table02": table02N}
        scan = tabtotext.tablistscanGFM(text)
        back = dict(tabtotext.tablistmap(scan))
        logg.debug("\n>> %s\n<< %s", tablist, back)
        self.assertEqual(want, back)
    def test_6812(self) -> None:
        tablist = {"table22": table22, "table33": table33}
        text = tabtotext.tablistmakeFMT("md", tabtotext.tablistfor(tablist))
        logg.debug("%s => %s", tablist, text.splitlines())
        cond = ['',
                '## table22',
                '| a     | b',
                '| ----- | -----',
                '| x     | 3',
                '| y     | 2',
                '',
                '## table33',
                '| a     | b     | c',
                '| ----- | ----- | ----------',
                '| x     | 3     | 2021-12-31',
                '| y     | 2     | 2021-12-30',
                '| ~     | ~     | 2021-12-31']
        self.assertEqual(cond, text.splitlines())
        want = {"table22": table22, "table33": table33Q}
        scan = tabtotext.tablistscanGFM(text)
        back = dict(tabtotext.tablistmap(scan))
        logg.debug("\n>> %s\n<< %s", tablist, back)
        self.assertEqual(want, back)
    def test_6821(self) -> None:
        tmp = self.testdir()
        tablist = {"table01": table01, "table02": table02}
        filename = path.join(tmp, "output.md")
        text = tabtotext.print_tablist(filename, tabtotext.tablistfor(tablist))
        sz = path.getsize(filename)
        self.assertGreater(sz, 100)
        self.assertGreater(200, sz)
        want = {"table01": table01N, "table02": _date(table02N)}
        scan = tabtotext.tablistfile(filename)
        back = dict(tabtotext.tablistmap(scan))
        logg.debug("\n>> %s\n<< %s", want, back)
        self.assertEqual(want, back)
    def test_6822(self) -> None:
        tmp = self.testdir()
        tablist = {"table22": table22, "table33": table33}
        filename = path.join(tmp, "output.md")
        text = tabtotext.print_tablist(filename, tabtotext.tablistfor(tablist))
        sz = path.getsize(filename)
        self.assertGreater(sz, 100)
        self.assertGreater(600, sz)
        want = {"table22": table22, "table33": _date(table33Q)}
        scan = tabtotext.tablistfile(filename)
        back = dict(tabtotext.tablistmap(scan))
        logg.debug("\n>> %s\n<< %s", want, back)
        self.assertEqual(want, back)

    def test_6910(self) -> None:
        item = Item2("x", 2)
        text = tabtotext.tabToFMTx("def", item)
        logg.debug("%s => %s", test004, text)
        cond = ['| a     | b', '| ----- | -----', '| x     | 2']
        self.assertEqual(cond, text.splitlines())
    def test_6911(self) -> None:
        item = Item2("x", 2)
        itemlist: DataList = [item]
        text = tabtotext.tabToFMTx("def", itemlist)
        logg.debug("%s => %s", test004, text)
        cond = ['| a     | b', '| ----- | -----', '| x     | 2']
        self.assertEqual(cond, text.splitlines())
    def test_6918(self) -> None:
        item1 = Item2("x", 2)
        item2 = Item2("y", 3)
        itemlist: DataList = [item1, item2]
        text = tabtotext.tabToFMTx("tabs", itemlist)
        logg.debug("%s => %s", test004, text)
        cond = ['\t a     \t b', '\t ----- \t -----', '\t x     \t 2', '\t y     \t 3']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text, tab='\t')
        want = [{'a': 'x', 'b': 2}, {'a': 'y', 'b': 3}]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_6919(self) -> None:
        item1 = Item2("x", 2)
        item2 = Item2("y", 3)
        itemlist: DataList = [item1, item2]
        text = tabtotext.tabToFMTx("wide", itemlist)
        logg.debug("%s => %s", test004, text)
        cond = ['a     b', 'x     2', 'y     3']
        self.assertEqual(cond, text.splitlines())
    def test_6920(self) -> None:
        text = tabtotext.tabtotext(table01, [], ["@md"])
        logg.debug("%s => %s", table01, text)
        want = table01N
        cond = ['| a     | b', '| ----- | -----', '| x y   | ~', '| ~     | 1']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6921(self) -> None:
        text = tabtotext.tabtotext(table02, [], ["@md"])
        logg.debug("%s => %s", table02, text)
        want = table02N
        cond = ['| a     | b', '| ----- | -----', '| x     | 0', '| ~     | 2']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6922(self) -> None:
        text = tabtotext.tabtotext(table22, [], ["@md"])
        logg.debug("%s => %s", table22, text)
        want = table22
        cond = ['| a     | b', '| ----- | -----', '| x     | 3', '| y     | 2']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6923(self) -> None:
        text = tabtotext.tabtotext(table33, [], ["@md"])
        logg.debug("%s => %s", table33, text)
        want = table33Q
        cond = ['| a     | b     | c', '| ----- | ----- | ----------',
                '| x     | 3     | 2021-12-31', '| y     | 2     | 2021-12-30',
                '| ~     | ~     | 2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6924(self) -> None:
        text = tabtotext.tabtotext(table44, [], ["@md"])
        logg.debug("%s => %s", table44, text)
        want = table44N
        cond = ['| a     | b     | c     | d', '| ----- | ----- | ----- | -----',
                '| x     | 3     | (yes) | 0.40',
                '| y     | 2     | (no)  | 0.30',
                '| ~     | ~     | (yes) | 0.20',
                '| y     | 1     | ~     | 0.10']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6930(self) -> None:
        text = tabtotext.tabtotext(table01, [], ["@md3"])
        logg.debug("%s => %s", table01, text)
        want = table01N
        cond = ['| a   | b', '| --- | ---', '| x y | ~', '| ~   | 1']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6931(self) -> None:
        text = tabtotext.tabtotext(table02, [], ["@md3"])
        logg.debug("%s => %s", table02, text)
        want = table02N
        cond = ['| a   | b', '| --- | ---', '| x   | 0', '| ~   | 2']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6932(self) -> None:
        text = tabtotext.tabtotext(table22, [], ["@md3"])
        logg.debug("%s => %s", table22, text)
        want = table22
        cond = ['| a   | b', '| --- | ---', '| x   | 3', '| y   | 2']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6933(self) -> None:
        text = tabtotext.tabtotext(table33, [], ["@md3"])
        logg.debug("%s => %s", table33, text)
        want = table33Q
        cond = ['| a   | b   | c', '| --- | --- | ----------',
                '| x   | 3   | 2021-12-31', '| y   | 2   | 2021-12-30',
                '| ~   | ~   | 2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6934(self) -> None:
        text = tabtotext.tabtotext(table44, [], ["@md3"])
        logg.debug("%s => %s", table44, text)
        want = table44N
        cond = ['| a   | b   | c     | d',
                '| --- | --- | ----- | ----',
                '| x   | 3   | (yes) | 0.40',
                '| y   | 2   | (no)  | 0.30',
                '| ~   | ~   | (yes) | 0.20',
                '| y   | 1   | ~     | 0.10']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6940(self) -> None:
        text = tabtotext.tabtotext(table01, [], ["@md6"])
        logg.debug("%s => %s", table01, text)
        want = table01N
        cond = ['| a      | b', '| ------ | ------', '| x y    | ~', '| ~      | 1']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6941(self) -> None:
        text = tabtotext.tabtotext(table02, [], ["@md6"])
        logg.debug("%s => %s", table02, text)
        want = table02N
        cond = ['| a      | b', '| ------ | ------', '| x      | 0', '| ~      | 2']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6942(self) -> None:
        text = tabtotext.tabtotext(table22, [], ["@md6"])
        logg.debug("%s => %s", table22, text)
        want = table22
        cond = ['| a      | b', '| ------ | ------', '| x      | 3', '| y      | 2']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6943(self) -> None:
        text = tabtotext.tabtotext(table33, [], ["@md6"])
        logg.debug("%s => %s", table33, text)
        want = table33Q
        cond = ['| a      | b      | c',
                '| ------ | ------ | ----------',
                '| x      | 3      | 2021-12-31',
                '| y      | 2      | 2021-12-30',
                '| ~      | ~      | 2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6944(self) -> None:
        text = tabtotext.tabtotext(table44, [], ["@md6"])
        logg.debug("%s => %s", table44, text)
        want = table44N
        cond = ['| a      | b      | c      | d',
                '| ------ | ------ | ------ | ------',
                '| x      | 3      | (yes)  | 0.40',
                '| y      | 2      | (no)   | 0.30',
                '| ~      | ~      | (yes)  | 0.20',
                '| y      | 1      | ~      | 0.10']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6950(self) -> None:
        text = tabtotext.tabtotext(table01, [], ["@tabs"])
        logg.debug("%s => %s", table01, text)
        want = table01N
        cond = ['\ta    \tb', '\tx y  \t~', '\t~    \t1']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text, tab="\t")
        self.assertEqual(want, back)
    def test_6951(self) -> None:
        text = tabtotext.tabtotext(table02, [], ["@tabs"])
        logg.debug("%s => %s", table02, text)
        want = table02N
        cond = ['\ta    \tb', '\tx    \t0', '\t~    \t2']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text, tab="\t")
        self.assertEqual(want, back)
    def test_6952(self) -> None:
        text = tabtotext.tabtotext(table22, [], ["@tabs"])
        logg.debug("%s => %s", table22, text)
        want = table22
        cond = ['\ta    \tb', '\tx    \t3', '\ty    \t2']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text, tab="\t")
        self.assertEqual(want, back)
    def test_6953(self) -> None:
        text = tabtotext.tabtotext(table33, [], ["@tabs"])
        logg.debug("%s => %s", table33, text.splitlines())
        want = table33Q
        cond = ['\ta    \tb    \tc', '\tx    \t3    \t2021-12-31',
                '\ty    \t2    \t2021-12-30', '\t~    \t~    \t2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text, tab="\t")
        self.assertEqual(want, back)
    def test_6954(self) -> None:
        text = tabtotext.tabtotext(table44, [], ["@tabs"])
        logg.debug("%s => %s", table44, text.splitlines())
        want = table44N
        cond = ['\ta    \tb    \tc    \td',
                '\tx    \t3    \t(yes)\t0.40',
                '\ty    \t2    \t(no) \t0.30',
                '\t~    \t~    \t(yes)\t0.20',
                '\ty    \t1    \t~    \t0.10']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text, tab="\t")
        self.assertEqual(want, back)
    def test_6960(self) -> None:
        text = tabtotext.tabtotext(table01, [], ["@tabs", "@delim=:"])
        logg.debug("%s => %s", table01, text)
        want = table01N
        cond = [':a    :b', ':x y  :~', ':~    :1']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text, tab=":")
        self.assertEqual(want, back)
    def test_6961(self) -> None:
        text = tabtotext.tabtotext(table02, [], ["@tabs", "@delim=:"])
        logg.debug("%s => %s", table02, text)
        want = table02N
        cond = [':a    :b', ':x    :0', ':~    :2']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text, tab=":")
        self.assertEqual(want, back)
    def test_6962(self) -> None:
        text = tabtotext.tabtotext(table22, [], ["@tabs", "@delim=:"])
        logg.debug("%s => %s", table22, text)
        want = table22
        cond = [':a    :b', ':x    :3', ':y    :2']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text, tab=":")
        self.assertEqual(want, back)
    def test_6970(self) -> None:
        text = tabtotext.tabtotext(table01, [], ["@wide"])
        logg.debug("%s => %s", table01, text)
        want = table01N
        cond = ['a     b', 'x y   ~', '~     1']
        self.assertEqual(cond, text.splitlines())
    def test_6971(self) -> None:
        text = tabtotext.tabtotext(table02, [], ["@wide"])
        logg.debug("%s => %s", table02, text)
        want = table02N
        cond = ['a     b', 'x     0', '~     2']
        self.assertEqual(cond, text.splitlines())
    def test_6972(self) -> None:
        text = tabtotext.tabtotext(table22, [], ["@wide"])
        logg.debug("%s => %s", table22, text)
        want = table22
        cond = ['a     b', 'x     3', 'y     2']
        self.assertEqual(cond, text.splitlines())
    def test_6973(self) -> None:
        text = tabtotext.tabtotext(table33, [], ["@wide"])
        logg.debug("%s => %s", table33, text)
        want = table33Q
        cond = ['a     b     c',
                'x     3     2021-12-31', 'y     2     2021-12-30',
                '~     ~     2021-12-31']
        self.assertEqual(cond, text.splitlines())
    def test_6974(self) -> None:
        text = tabtotext.tabtotext(table44, [], ["@wide"])
        logg.debug("%s => %s", table44, text)
        want = table44N
        cond = ['a     b     c     d',
                'x     3     (yes) 0.40',
                'y     2     (no)  0.30',
                '~     ~     (yes) 0.20',
                'y     1     ~     0.10']
        self.assertEqual(cond, text.splitlines())
    def test_6975(self) -> None:
        text = tabtotext.tabtotext(table01, [], ["@read"])
        logg.debug("%s => %s", table01, text)
        want = table01N
        cond = [' x\\ y  ~', ' ~     1']
        self.assertEqual(cond, text.splitlines())
    def test_6976(self) -> None:
        data: JSONList = [{"a": "a b", "c": "c d e"}, {"a": "g\nh", "c": "s\\t"}]
        text = tabtotext.tabtotext(data, [], ["@read"])
        logg.debug("%s => %s", data, text)
        cond = [' a\\ b  c\\ d\\ e', ' g\\', 'h  s\\\\t']
        self.assertEqual(cond, text.splitlines())
        real = sh("{ echo ' a\\ b  c\\ d\\ e'; echo ' g\\'; echo 'h  s\\\\t'; } | while read a c e; do echo a=$a; echo c=$c; echo e=$e; done")
        logg.info("real\n%s", real)
        back = real.splitlines()
        want = ["a=a b", 'c=c d e', 'e=', 'a=gh', 'c=s\\t', 'e=']  # NOTE: bash-read swallows \n between gh ?
        self.assertEqual(want, back)
    def test_6980(self) -> None:
        text = tabtotext.tabtotext(table01, [], ["@text"])
        logg.debug("%s => %s", table01, text)
        want = table01N
        cond = ['|x y  |~', '|~    |1']
        self.assertEqual(cond, text.splitlines())
    def test_6981(self) -> None:
        text = tabtotext.tabtotext(table02, [], ["@text"])
        logg.debug("%s => %s", table02, text)
        want = table02N
        cond = ['|x    |0', '|~    |2']
        self.assertEqual(cond, text.splitlines())
    def test_6982(self) -> None:
        text = tabtotext.tabtotext(table22, [], ["@text"])
        logg.debug("%s => %s", table22, text)
        want = table22
        cond = ['|x    |3', '|y    |2']
        self.assertEqual(cond, text.splitlines())
    def test_6983(self) -> None:
        text = tabtotext.tabtotext(table33, [], ["@text"])
        logg.debug("%s => %s", table33, text)
        want = table33Q
        cond = ['|x    |3    |2021-12-31',
                '|y    |2    |2021-12-30',
                '|~    |~    |2021-12-31']
    def test_6984(self) -> None:
        text = tabtotext.tabtotext(table44, [], ["@text"])
        logg.debug("%s => %s", table44, text)
        want = table44N
        cond = ['|x    |3    |(yes)|0.40',
                '|y    |2    |(no) |0.30',
                '|~    |~    |(yes)|0.20',
                '|y    |1    |~    |0.10']
        self.assertEqual(cond, text.splitlines())
    def test_6990(self) -> None:
        text = tabtotext.tabtotext(table01, [], ["@txt"])
        logg.debug("%s => %s", table01, text)
        want = table01N
        cond = ['|a    |b', '|x y  |~', '|~    |1']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6991(self) -> None:
        text = tabtotext.tabtotext(table02, [], ["@txt"])
        logg.debug("%s => %s", table02, text)
        want = table02N
        cond = ['|a    |b', '|x    |0', '|~    |2']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6992(self) -> None:
        text = tabtotext.tabtotext(table22, [], ["@txt"])
        logg.debug("%s => %s", table22, text)
        want = table22
        cond = ['|a    |b', '|x    |3', '|y    |2']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6993(self) -> None:
        text = tabtotext.tabtotext(table33, [], ["@txt"])
        logg.debug("%s => %s", table33, text.splitlines())
        want = table33Q
        cond = ['|x    |3    |2021-12-31',
                '|y    |2    |2021-12-30',
                '|~    |~    |2021-12-31']
        back = loadGFM(text)
        self.assertEqual(want, back)
    def test_6994(self) -> None:
        text = tabtotext.tabtotext(table44, [], ["@txt"])
        logg.debug("%s => %s", table44, text.splitlines())
        want = table44N
        cond = ['|a    |b    |c    |d',
                '|x    |3    |(yes)|0.40',
                '|y    |2    |(no) |0.30',
                '|~    |~    |(yes)|0.20',
                '|y    |1    |~    |0.10']
        self.assertEqual(cond, text.splitlines())
        back = loadGFM(text)
        self.assertEqual(want, back)


#  HTML
    def test_7003(self) -> None:
        text = tabtotext.tabToHTML(test003)
        logg.debug("%s => %s", test003, text)
        want = table01N
        cond = ['<table border="1" cellpadding="8">', '<tr></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7004(self) -> None:
        text = tabtotext.tabToHTML(test004)
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">', '<tr></tr>', '<tr></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7005(self) -> None:
        text = tabtotext.tabToHTML(test005)
        logg.debug("%s => %s", test005, text)
        cond = ['<table border="1" cellpadding="8">', '<tr><th>a</th></tr>', '<tr><td>x</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7006(self) -> None:
        text = tabtotext.tabToHTML(test006)
        logg.debug("%s => %s", test006, text)
        cond = ['<table border="1" cellpadding="8">',  # -
                '<tr><th>a</th><th>b</th></tr>',  # -
                '<tr><td>x</td><td>y</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7007(self) -> None:
        text = tabtotext.tabToHTML(test007)
        logg.debug("%s => %s", test007, text)
        cond = ['<table border="1" cellpadding="8">',  # -
                '<tr><th>a</th><th>b</th></tr>',  # -
                '<tr><td>x</td><td>y</td></tr>',  # -
                '<tr><td></td><td>v</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7008(self) -> None:
        text = tabtotext.tabToHTML(test008)
        logg.debug("%s => %s", test008, text)
        cond = ['<table border="1" cellpadding="8">',  # -
                '<tr><th>a</th><th>b</th></tr>',  # -
                '<tr><td>x</td><td></td></tr>',  # -
                '<tr><td></td><td>v</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7009(self) -> None:
        text = tabtotext.tabToHTML(test009)
        logg.debug("%s => %s", test009, text)
        cond = ['<table border="1" cellpadding="8">',  # -
                '<tr><th>b</th></tr>',  # -
                '<tr><td></td></tr>',  # -
                '<tr><td>v</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7011(self) -> None:
        text = tabtotext.tabToHTML(test011)
        logg.debug("%s => %s", test011, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>~</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7012(self) -> None:
        text = tabtotext.tabToHTML(test012)
        logg.debug("%s => %s", test012, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>(no)</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7013(self) -> None:
        text = tabtotext.tabToHTML(test013)
        logg.debug("%s => %s", test013, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>(yes)</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7014(self) -> None:
        text = tabtotext.tabToHTML(test014)
        logg.debug("%s => %s", test014, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td></td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7015(self) -> None:
        text = tabtotext.tabToHTML(test015)
        logg.debug("%s => %s", test015, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>5678</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7016(self) -> None:
        text = tabtotext.tabToHTML(test016)
        logg.debug("%s => %s", test016, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>123</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7017(self) -> None:
        text = tabtotext.tabToHTML(test017)
        logg.debug("%s => %s", test017, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>123.40</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7018(self) -> None:
        text = tabtotext.tabToHTML(test018)
        logg.debug("%s => %s", test018, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>2021-12-31</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7019(self) -> None:
        text = tabtotext.tabToHTML(test019)
        logg.debug("%s => %s", test019, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>2021-12-31</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7020(self) -> None:
        text = tabtotext.tabToHTML(table01)
        logg.debug("%s => %s", table01, text)
        want = table01N
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>a</th><th>b</th></tr>',
                '<tr><td>x y</td><td></td></tr>',
                '<tr><td></td><td>1</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7021(self) -> None:
        text = tabtotext.tabToHTML(table02)
        logg.debug("%s => %s", table02, text)
        want = table02N
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>a</th><th>b</th></tr>', '<tr><td>x</td><td>0</td></tr>',
                '<tr><td></td><td>2</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7022(self) -> None:
        text = tabtotext.tabToHTML(table22)
        logg.debug("%s => %s", table22, text)
        want = table22
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>a</th><th>b</th></tr>', '<tr><td>x</td><td>3</td></tr>',
                '<tr><td>y</td><td>2</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7023(self) -> None:
        text = tabtotext.tabToHTML(table33)
        logg.debug("%s => %s", table33, text)
        want = table33Q
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>a</th><th>b</th><th>c</th></tr>',
                '<tr><td>x</td><td>3</td><td>2021-12-31</td></tr>',
                '<tr><td>y</td><td>2</td><td>2021-12-30</td></tr>',
                '<tr><td>~</td><td></td><td>2021-12-31</td></tr>', '</table>']
        ['a;b;c', 'x;3;2021-12-31', 'y;2;2021-12-30', '~;~;2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)

    def test_7031(self) -> None:
        text = tabtotext.tabToHTML(test011, legend=["a result", "was found"])
        logg.debug("%s => %s", test011, text)
        cond = ['<table border="1" cellpadding="8">', '<tr><th>b</th></tr>', '<tr><td>~</td></tr>', '</table>',
                '', '<ul>', '<li>a result</li>', '<li>was found</li>', '</ul>']
        self.assertEqual(cond, text.splitlines())
    def test_7032(self) -> None:
        text = tabtotext.tabToHTML(test012, legend=["a result", "was found"])
        logg.debug("%s => %s", test012, text)
        cond = ['<table border="1" cellpadding="8">', '<tr><th>b</th></tr>',
                '<tr><td>(no)</td></tr>', '</table>', '', '<ul>', '<li>a result</li>', '<li>was found</li>', '</ul>']
        self.assertEqual(cond, text.splitlines())
    def test_7033(self) -> None:
        text = tabtotext.tabToHTML(test013, legend=["a result", "was found"])
        logg.debug("%s => %s", test013, text)
        cond = ['<table border="1" cellpadding="8">', '<tr><th>b</th></tr>',
                '<tr><td>(yes)</td></tr>', '</table>', '', '<ul>', '<li>a result</li>', '<li>was found</li>', '</ul>']
        self.assertEqual(cond, text.splitlines())
    def test_7034(self) -> None:
        text = tabtotext.tabToHTML(test014, legend=["a result", "was found"])
        logg.debug("%s => %s", test014, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td></td></tr>', '</table>',
                '', '<ul>', '<li>a result</li>', '<li>was found</li>', '</ul>']
        self.assertEqual(cond, text.splitlines())
    def test_7035(self) -> None:
        text = tabtotext.tabToHTML(test015, legend=["a result", "was found"])
        logg.debug("%s => %s", test015, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>5678</td></tr>',
                '</table>', '', '<ul>', '<li>a result</li>', '<li>was found</li>', '</ul>']
        self.assertEqual(cond, text.splitlines())
    def test_7036(self) -> None:
        text = tabtotext.tabToHTML(test016, legend=["a result", "was found"])
        logg.debug("%s => %s", test016, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>123</td></tr>', '</table>',
                '', '<ul>', '<li>a result</li>', '<li>was found</li>', '</ul>']
        self.assertEqual(cond, text.splitlines())
    def test_7037(self) -> None:
        text = tabtotext.tabToHTML(test017, legend=["a result", "was found"])
        logg.debug("%s => %s", test017, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>123.40</td></tr>',
                '</table>', '', '<ul>', '<li>a result</li>', '<li>was found</li>', '</ul>']
        self.assertEqual(cond, text.splitlines())
    def test_7038(self) -> None:
        text = tabtotext.tabToHTML(test018, legend=["a result", "was found"])
        logg.debug("%s => %s", test018, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>2021-12-31</td></tr>',
                '</table>', '', '<ul>', '<li>a result</li>', '<li>was found</li>', '</ul>']
        self.assertEqual(cond, text.splitlines())
    def test_7039(self) -> None:
        text = tabtotext.tabToHTML(test019, legend=["a result", "was found"])
        logg.debug("%s => %s", test019, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>2021-12-31</td></tr>',
                '</table>', '', '<ul>', '<li>a result</li>', '<li>was found</li>', '</ul>']
        self.assertEqual(cond, text.splitlines())
    def test_7044(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        text = tabtotext.tabToHTML(itemlist, sorts=['b', 'a'])
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th><th>a</th></tr>',
                '<tr><td>1</td><td>y</td></tr>', '<tr><td>2</td><td>x</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': 'y', 'b': 1}, {'a': 'x', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7045(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}, {'c': 'h'}]
        text = tabtotext.tabToHTML(itemlist, sorts=['b', 'a'])
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th><th>a</th><th>c</th></tr>', '<tr><td>1</td><td>y</td><td></td></tr>',
                '<tr><td>2</td><td>x</td><td></td></tr>', '<tr><td></td><td></td><td>h</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': 'y', 'b': 1, 'c': None}, {'a': 'x', 'b': 2, 'c': None}, {'a': None, 'b': None, 'c': 'h'}, ]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7046(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}, {'c': 'h'}]
        text = tabtotext.tabToHTML(itemlist, sorts=['b', 'a'], reorder=['a', 'b'])
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>a</th><th>b</th><th>c</th></tr>', '<tr><td>y</td><td>1</td><td></td></tr>',
                '<tr><td>x</td><td>2</td><td></td></tr>', '<tr><td></td><td></td><td>h</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': 'y', 'b': 1, 'c': None}, {'a': 'x', 'b': 2, 'c': None}, {'a': None, 'b': None, 'c': 'h'}, ]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7051(self) -> None:
        text = tabtotext.tabToHTMLx(data011)
        logg.debug("%s => %s", data011, text)
        want = rev(table01N)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>~</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7052(self) -> None:
        text = tabtotext.tabToHTMLx(data012)
        logg.debug("%s => %s", data012, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>(no)</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7053(self) -> None:
        text = tabtotext.tabToHTMLx(data013)
        logg.debug("%s => %s", data013, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>(yes)</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7054(self) -> None:
        text = tabtotext.tabToHTMLx(data014)
        logg.debug("%s => %s", data014, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td></td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7055(self) -> None:
        text = tabtotext.tabToHTMLx(data015)
        logg.debug("%s => %s", data015, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>5678</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7056(self) -> None:
        text = tabtotext.tabToHTMLx(data016)
        logg.debug("%s => %s", data016, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>123</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7057(self) -> None:
        text = tabtotext.tabToHTMLx(data017)
        logg.debug("%s => %s", data017, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>123.40</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7058(self) -> None:
        text = tabtotext.tabToHTMLx(data018)
        logg.debug("%s => %s", data018, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>2021-12-31</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7059(self) -> None:
        text = tabtotext.tabToHTMLx(data019)
        logg.debug("%s => %s", data019, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>2021-12-31</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7060(self) -> None:
        text = tabtotext.tabToHTML(table01, ["b", "a"])
        logg.debug("%s => %s", table01, text)
        want = rev(table01N)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th><th>a</th></tr>', '<tr><td>1</td><td></td></tr>',
                '<tr><td></td><td>x y</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7061(self) -> None:
        text = tabtotext.tabToHTML(table02, ["b", "a"])
        logg.debug("%s => %s", table02, text)
        want = table02N
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th><th>a</th></tr>', '<tr><td>0</td><td>x</td></tr>',
                '<tr><td>2</td><td></td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7062(self) -> None:
        text = tabtotext.tabToHTML(table22, ["b", "a"])
        logg.debug("%s => %s", table22, text)
        want = rev(table22)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th><th>a</th></tr>', '<tr><td>2</td><td>y</td></tr>',
                '<tr><td>3</td><td>x</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7063(self) -> None:
        text = tabtotext.tabToHTML(table33, ["b", "a"])
        logg.debug("%s => %s", table33, text)
        want = rev(table33Q[:2]) + table33Q[2:]
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th><th>a</th><th>c</th></tr>',
                '<tr><td>2</td><td>y</td><td>2021-12-30</td></tr>',
                '<tr><td>3</td><td>x</td><td>2021-12-31</td></tr>',
                '<tr><td></td><td>~</td><td>2021-12-31</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7064(self) -> None:
        text = tabtotext.tabToHTML(table44, ["b", "a"])
        logg.debug("%s => %s", table44, text.splitlines())
        want = table44N[3:] + table44N[1:2] + table44N[0:1] + table44N[2:3]
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th><th>a</th><th>c</th><th>d</th></tr>',
                '<tr><td>1</td><td>y</td><td></td><td>0.10</td></tr>',
                '<tr><td>2</td><td>y</td><td>(no)</td><td>0.30</td></tr>',
                '<tr><td>3</td><td>x</td><td>(yes)</td><td>0.40</td></tr>',
                '<tr><td>~</td><td>~</td><td>(yes)</td><td>0.20</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7065(self) -> None:
        text = tabtotext.tabToHTML(table33, ["c", "a"])
        logg.debug("%s => %s", table33, text)
        want = rev(table33Q[:2]) + table33Q[2:]
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>c</th><th>a</th><th>b</th></tr>',
                '<tr><td>2021-12-30</td><td>y</td><td>2</td></tr>',
                '<tr><td>2021-12-31</td><td>x</td><td>3</td></tr>',
                '<tr><td>2021-12-31</td><td>~</td><td></td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)

    def test_7071(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        formats = {"a": ' {:}'}
        headers = ['b', 'a']
        text = tabtotext.tabToHTML(itemlist, ['b', 'a'], formats)
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th><th style="text-align: right">a</th></tr>',  # ,
                '<tr><td>1</td><td style="text-align: right"> y</td></tr>',  # ,
                '<tr><td>2</td><td style="text-align: right"> x</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': 'y', 'b': 1}, {'a': 'x', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7072(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        formats = {"a": ' %s'}
        headers = ['b', 'a']
        text = tabtotext.tabToHTML(itemlist, ['b', 'a'], formats)
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th><th style="text-align: right">a</th></tr>',  # ,
                '<tr><td>1</td><td style="text-align: right"> y</td></tr>',  # ,
                '<tr><td>2</td><td style="text-align: right"> x</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': 'y', 'b': 1}, {'a': 'x', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7073(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        formats = {"a": '"%s"', "b": "%.2f"}
        headers = ['b', 'a']
        text = tabtotext.tabToHTML(itemlist, ['b', 'a'], formats)
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th style="text-align: right">b</th><th>a</th></tr>',  # ,
                '<tr><td style="text-align: right">1.00</td><td>&quot;y&quot;</td></tr>',  # ,
                '<tr><td style="text-align: right">2.00</td><td>&quot;x&quot;</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': '"y"', 'b': 1}, {'a': '"x"', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7074(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        formats = {"a": '"{:}"', "b": "{:.2f}"}
        headers = ['b', 'a']
        text = tabtotext.tabToHTML(itemlist, ['b', 'a'], formats)
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th style="text-align: right">b</th><th>a</th></tr>',  # ,
                '<tr><td style="text-align: right">1.00</td><td>&quot;y&quot;</td></tr>',  # ,
                '<tr><td style="text-align: right">2.00</td><td>&quot;x&quot;</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': '"y"', 'b': 1}, {'a': '"x"', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7075(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2.}, {'a': "y", 'b': 1.}]
        formats = {"a": '"{:}"', "b": "%.2f"}
        headers = ['b', 'a']
        text = tabtotext.tabToHTML(itemlist, ['b', 'a'], formats)
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th style="text-align: right">b</th><th>a</th></tr>',  # ,
                '<tr><td style="text-align: right">1.00</td><td>&quot;y&quot;</td></tr>',  # ,
                '<tr><td style="text-align: right">2.00</td><td>&quot;x&quot;</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': '"y"', 'b': 1}, {'a': '"x"', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7076(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2.}, {'a': "y", 'b': 1.}]
        formats = {"a": '"{:}"', "b": "{:.2f}"}
        headers = ['b', 'a']
        text = tabtotext.tabToHTML(itemlist, ['b', 'a'], formats)
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th style="text-align: right">b</th><th>a</th></tr>',  # ,
                '<tr><td style="text-align: right">1.00</td><td>&quot;y&quot;</td></tr>',  # ,
                '<tr><td style="text-align: right">2.00</td><td>&quot;x&quot;</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': '"y"', 'b': 1}, {'a': '"x"', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7077(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2.}, {'a': "y", 'b': 1.}]
        formats = {"a": '"{:}"', "b": "{:$}"}
        headers = ['b', 'a']
        text = tabtotext.tabToHTML(itemlist, ['b', 'a'], formats)
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th style="text-align: right">b</th><th>a</th></tr>',  # ,
                X('<tr><td style="text-align: right">1.00$</td><td>&quot;y&quot;</td></tr>'),  # ,
                X('<tr><td style="text-align: right">2.00$</td><td>&quot;x&quot;</td></tr>'), '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': '"y"', 'b': 1}, {'a': '"x"', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7078(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2.}, {'a': "y", 'b': 1.}]
        formats = {"a": '"{:5s}"', "b": "{:3f}"}
        headers = ['b', 'a']
        text = tabtotext.tabToHTML(itemlist, ['b', 'a'], formats)
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th style="text-align: right">b</th><th>a</th></tr>',  # ,
                '<tr><td style="text-align: right">1.000000</td><td>&quot;y    &quot;</td></tr>',  # ,
                '<tr><td style="text-align: right">2.000000</td><td>&quot;x    &quot;</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': '"y    "', 'b': 1.0}, {'a': '"x    "', 'b': 2.0}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7079(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 22.}, {'a': "y", 'b': 1.}]
        formats = {"a": '"{:>5s}"', "b": "{:>3f}"}
        headers = ['b', 'a']
        text = tabtotext.tabToHTML(itemlist, ['b', 'a'], formats)
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th style="text-align: right">b</th><th style="text-align: right">a</th></tr>',  # ,
                '<tr><td style="text-align: right">1.000000</td><td style="text-align: right">&quot;    y&quot;</td></tr>',  # ,
                '<tr><td style="text-align: right">22.000000</td><td style="text-align: right">&quot;    x&quot;</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': '"    y"', 'b': 1.0}, {'a': '"    x"', 'b': 22.0}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7103(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test003, defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test003, text)
        cond = ['<table border="1" cellpadding="8">', '<tr></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7104(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test004, defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">', '<tr></tr>', '<tr></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7105(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test005, defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test005, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>a</th></tr>', '<tr><td>x</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7106(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test006, defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test006, text)
        cond = ['<table border="1" cellpadding="8">',  # -
                '<tr><th>a</th><th>b</th></tr>',  # -
                '<tr><td>x</td><td>y</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7107(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test007, defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test007, text)
        cond = ['<table border="1" cellpadding="8">',  # -
                '<tr><th>a</th><th>b</th></tr>',  # -
                '<tr><td>x</td><td>y</td></tr>',  # -
                '<tr><td></td><td>v</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7108(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test008, defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        text = tabtotext.tabToHTML(test008)
        logg.debug("%s => %s", test008, text)
        cond = ['<table border="1" cellpadding="8">',  # -
                '<tr><th>a</th><th>b</th></tr>',  # -
                '<tr><td>x</td><td></td></tr>',  # -
                '<tr><td></td><td>v</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7109(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test009, defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test009, text)
        cond = ['<table border="1" cellpadding="8">',  # -
                '<tr><th>b</th></tr>',  # -
                '<tr><td></td></tr>',  # -
                '<tr><td>v</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7111(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test011, defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test011, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>~</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7112(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test012, defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test012, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>(no)</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7113(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test013, defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test013, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>(yes)</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7114(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test014, defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test014, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td></td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7115(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test015, defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test015, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>5678</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7116(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test016, defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test016, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>123</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7117(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test017, defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test017, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>123.40</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7118(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test018, defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test018, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>2021-12-31</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7119(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test019, defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test019, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>2021-12-31</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7131(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test011, legend=["a result", "was found"], defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test011, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>~</td></tr>', '</table>',
                '', '<ul>', '<li>a result</li>', '<li>was found</li>', '</ul>']
        self.assertEqual(cond, text.splitlines())
    def test_7132(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test012, legend=["a result", "was found"], defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test012, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>',
                '<tr><td>(no)</td></tr>', '</table>', '', '<ul>', '<li>a result</li>', '<li>was found</li>', '</ul>']
        self.assertEqual(cond, text.splitlines())
    def test_7133(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test013, legend=["a result", "was found"], defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test013, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>',
                '<tr><td>(yes)</td></tr>', '</table>', '', '<ul>', '<li>a result</li>', '<li>was found</li>', '</ul>']
        self.assertEqual(cond, text.splitlines())
    def test_7134(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test014, legend=["a result", "was found"], defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test014, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td></td></tr>', '</table>',
                '', '<ul>', '<li>a result</li>', '<li>was found</li>', '</ul>']
        self.assertEqual(cond, text.splitlines())
    def test_7135(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test015, legend=["a result", "was found"], defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test015, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>5678</td></tr>',
                '</table>', '', '<ul>', '<li>a result</li>', '<li>was found</li>', '</ul>']
        self.assertEqual(cond, text.splitlines())
    def test_7136(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test016, legend=["a result", "was found"], defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test016, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>123</td></tr>', '</table>',
                '', '<ul>', '<li>a result</li>', '<li>was found</li>', '</ul>']
        self.assertEqual(cond, text.splitlines())
    def test_7137(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test017, legend=["a result", "was found"], defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test017, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>123.40</td></tr>',
                '</table>', '', '<ul>', '<li>a result</li>', '<li>was found</li>', '</ul>']
        self.assertEqual(cond, text.splitlines())
    def test_7138(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test018, legend=["a result", "was found"], defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test018, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>2021-12-31</td></tr>',
                '</table>', '', '<ul>', '<li>a result</li>', '<li>was found</li>', '</ul>']
        self.assertEqual(cond, text.splitlines())
    def test_7139(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test019, legend=["a result", "was found"], defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test019, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>2021-12-31</td></tr>',
                '</table>', '', '<ul>', '<li>a result</li>', '<li>was found</li>', '</ul>']
        self.assertEqual(cond, text.splitlines())
    def test_7143(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        out = StringIO()
        res = tabtotext.print_tabtotext(out, itemlist, ['b', 'a'], defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th><th>a</th></tr>',
                '<tr><td>2</td><td>x</td></tr>', '<tr><td>1</td><td>y</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': 'x', 'b': 2}, {'a': 'y', 'b': 1}]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7144(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        out = StringIO()
        res = tabtotext.print_tabtotext(out, itemlist, ['b@1', 'a'], defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th><th>a</th></tr>',
                '<tr><td>1</td><td>y</td></tr>', '<tr><td>2</td><td>x</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': 'y', 'b': 1}, {'a': 'x', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7145(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}, {'c': 'h'}]
        out = StringIO()
        res = tabtotext.print_tabtotext(out, itemlist, ['b@1', 'a'], defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th><th>a</th><th>c</th></tr>', '<tr><td>1</td><td>y</td><td></td></tr>',
                '<tr><td>2</td><td>x</td><td></td></tr>', '<tr><td></td><td></td><td>h</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': 'y', 'b': 1, 'c': None}, {'a': 'x', 'b': 2, 'c': None}, {'a': None, 'b': None, 'c': 'h'}, ]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7149(self) -> None:
        """ htm is more compact that html """
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}, {'c': 'h'}]
        out = StringIO()
        res = tabtotext.print_tabtotext(out, itemlist, ['b@1', 'a'], defaultformat="htm")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['<table>',
                '<tr><th>b</th><th>a</th><th>c</th></tr>', '<tr><td>1</td><td>y</td><td></td></tr>',
                '<tr><td>2</td><td>x</td><td></td></tr>', '<tr><td></td><td></td><td>h</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': 'y', 'b': 1, 'c': None}, {'a': 'x', 'b': 2, 'c': None}, {'a': None, 'b': None, 'c': 'h'}, ]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7158(self) -> None:
        """ htm is more compact that html """
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}, {'c': 'h'}]
        out = StringIO()
        res = tabtotext.print_tabtotext(out, itemlist, ['b@1', 'a'], defaultformat="xhtml")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['<html xmlns="http://www.w3.org/1999/xhtml">',
                '<table border="1" cellpadding="8">',
                '<tr><th>b</th><th>a</th><th>c</th></tr>', '<tr><td>1</td><td>y</td><td></td></tr>',
                '<tr><td>2</td><td>x</td><td></td></tr>', '<tr><td></td><td></td><td>h</td></tr>',
                '</table>', '</html>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': 'y', 'b': 1, 'c': None}, {'a': 'x', 'b': 2, 'c': None}, {'a': None, 'b': None, 'c': 'h'}, ]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7159(self) -> None:
        """ htm is more compact that html """
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}, {'c': 'h'}]
        out = StringIO()
        res = tabtotext.print_tabtotext(out, itemlist, ['b@1', 'a'], defaultformat="xhtm")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['<html xmlns="http://www.w3.org/1999/xhtml">',
                '<table>',
                '<tr><th>b</th><th>a</th><th>c</th></tr>', '<tr><td>1</td><td>y</td><td></td></tr>',
                '<tr><td>2</td><td>x</td><td></td></tr>', '<tr><td></td><td></td><td>h</td></tr>',
                '</table>', '</html>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': 'y', 'b': 1, 'c': None}, {'a': 'x', 'b': 2, 'c': None}, {'a': None, 'b': None, 'c': 'h'}, ]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7171(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        out = StringIO()
        res = tabtotext.print_tabtotext(out, itemlist, ['b@1', 'a: {:}'], defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th><th style="text-align: right">a</th></tr>',  # ,
                '<tr><td>1</td><td style="text-align: right"> y</td></tr>',  # ,
                '<tr><td>2</td><td style="text-align: right"> x</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': 'y', 'b': 1}, {'a': 'x', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7172(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        out = StringIO()
        res = tabtotext.print_tabtotext(out, itemlist, ['b@1', 'a: %s'], defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th><th style="text-align: right">a</th></tr>',  # ,
                '<tr><td>1</td><td style="text-align: right"> y</td></tr>',  # ,
                '<tr><td>2</td><td style="text-align: right"> x</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': 'y', 'b': 1}, {'a': 'x', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7173(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        out = StringIO()
        res = tabtotext.print_tabtotext(out, itemlist, ['b:.2n@1', 'a:"%s"'], defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th><th>a</th></tr>',  # ,
                '<tr><td>1</td><td>&quot;y&quot;</td></tr>',  # ,
                '<tr><td>2</td><td>&quot;x&quot;</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': '"y"', 'b': 1}, {'a': '"x"', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7174(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        out = StringIO()
        res = tabtotext.print_tabtotext(out, itemlist, ['b:.2f@1', 'a:"{:}"'], defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th style="text-align: right">b</th><th>a</th></tr>',  # ,
                '<tr><td style="text-align: right">1.00</td><td>&quot;y&quot;</td></tr>',  # ,
                '<tr><td style="text-align: right">2.00</td><td>&quot;x&quot;</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': '"y"', 'b': 1}, {'a': '"x"', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7175(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2.}, {'a': "y", 'b': 1.}]
        out = StringIO()
        res = tabtotext.print_tabtotext(out, itemlist, ['b:<.2f@1', 'a:"{:}"'], defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th><th>a</th></tr>',  # ,
                '<tr><td>1.00</td><td>&quot;y&quot;</td></tr>',  # ,
                '<tr><td>2.00</td><td>&quot;x&quot;</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': '"y"', 'b': 1}, {'a': '"x"', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7176(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2.}, {'a': "y", 'b': 1.}]
        out = StringIO()
        res = tabtotext.print_tabtotext(out, itemlist, ['b:{:.2f}@1', 'a:"{:}"'], defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th style="text-align: right">b</th><th>a</th></tr>',  # ,
                '<tr><td style="text-align: right">1.00</td><td>&quot;y&quot;</td></tr>',  # ,
                '<tr><td style="text-align: right">2.00</td><td>&quot;x&quot;</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': '"y"', 'b': 1}, {'a': '"x"', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7177(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2.}, {'a': "y", 'b': 1.}]
        out = StringIO()
        res = tabtotext.print_tabtotext(out, itemlist, ['b:{:$}@1', 'a:"{:}"'], defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th style="text-align: right">b</th><th>a</th></tr>',  # ,
                X('<tr><td style="text-align: right">1.00$</td><td>&quot;y&quot;</td></tr>'),  # ,
                X('<tr><td style="text-align: right">2.00$</td><td>&quot;x&quot;</td></tr>'), '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': '"y"', 'b': 1}, {'a': '"x"', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7178(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2.}, {'a': "y", 'b': 1.}]
        out = StringIO()
        res = tabtotext.print_tabtotext(out, itemlist, ['b:{:3f}@1', 'a:"{:5s}"'], defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th style="text-align: right">b</th><th>a</th></tr>',  # ,
                '<tr><td style="text-align: right">1.000000</td><td>&quot;y    &quot;</td></tr>',  # ,
                '<tr><td style="text-align: right">2.000000</td><td>&quot;x    &quot;</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': '"y    "', 'b': 1.0}, {'a': '"x    "', 'b': 2.0}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7179(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 22.}, {'a': "y", 'b': 1.}]
        out = StringIO()
        res = tabtotext.print_tabtotext(out, itemlist, ['b:{:>3f}@1', 'a:"{:>5s}"'], defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th style="text-align: right">b</th><th style="text-align: right">a</th></tr>',  # ,
                '<tr><td style="text-align: right">1.000000</td><td style="text-align: right">&quot;    y&quot;</td></tr>',  # ,
                '<tr><td style="text-align: right">22.000000</td><td style="text-align: right">&quot;    x&quot;</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': '"    y"', 'b': 1.0}, {'a': '"    x"', 'b': 22.0}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7403(self) -> None:
        text = tabtotext.tabtoHTML(test003)
        logg.debug("%s => %s", test003, text)
        want = table01N
        cond = ['<table border="1" cellpadding="8">', '<tr></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7404(self) -> None:
        text = tabtotext.tabtoHTML(test004)
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">', '<tr></tr>', '<tr></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7405(self) -> None:
        text = tabtotext.tabtoHTML(test005)
        logg.debug("%s => %s", test005, text)
        cond = ['<table border="1" cellpadding="8">', '<tr><th>a</th></tr>', '<tr><td>x</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7406(self) -> None:
        text = tabtotext.tabtoHTML(test006)
        logg.debug("%s => %s", test006, text)
        cond = ['<table border="1" cellpadding="8">',  # -
                '<tr><th>a</th><th>b</th></tr>',  # -
                '<tr><td>x</td><td>y</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7407(self) -> None:
        text = tabtotext.tabtoHTML(test007)
        logg.debug("%s => %s", test007, text)
        cond = ['<table border="1" cellpadding="8">',  # -
                '<tr><th>a</th><th>b</th></tr>',  # -
                '<tr><td>x</td><td>y</td></tr>',  # -
                '<tr><td></td><td>v</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7408(self) -> None:
        text = tabtotext.tabtoHTML(test008)
        logg.debug("%s => %s", test008, text)
        cond = ['<table border="1" cellpadding="8">',  # -
                '<tr><th>a</th><th>b</th></tr>',  # -
                '<tr><td>x</td><td></td></tr>',  # -
                '<tr><td></td><td>v</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7409(self) -> None:
        text = tabtotext.tabtoHTML(test009)
        logg.debug("%s => %s", test009, text)
        cond = ['<table border="1" cellpadding="8">',  # -
                '<tr><th>b</th></tr>',  # -
                '<tr><td></td></tr>',  # -
                '<tr><td>v</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7411(self) -> None:
        text = tabtotext.tabtoHTML(test011)
        logg.debug("%s => %s", test011, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>~</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7412(self) -> None:
        text = tabtotext.tabtoHTML(test012)
        logg.debug("%s => %s", test012, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>(no)</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7413(self) -> None:
        text = tabtotext.tabtoHTML(test013)
        logg.debug("%s => %s", test013, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>(yes)</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7414(self) -> None:
        text = tabtotext.tabtoHTML(test014)
        logg.debug("%s => %s", test014, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td></td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7415(self) -> None:
        text = tabtotext.tabtoHTML(test015)
        logg.debug("%s => %s", test015, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>5678</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7416(self) -> None:
        text = tabtotext.tabtoHTML(test016)
        logg.debug("%s => %s", test016, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>123</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7417(self) -> None:
        text = tabtotext.tabtoHTML(test017)
        logg.debug("%s => %s", test017, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>123.40</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7418(self) -> None:
        text = tabtotext.tabtoHTML(test018)
        logg.debug("%s => %s", test018, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>2021-12-31</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7419(self) -> None:
        text = tabtotext.tabtoHTML(test019)
        logg.debug("%s => %s", test019, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>2021-12-31</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7420(self) -> None:
        text = tabtotext.tabtoHTML(table01)
        logg.debug("%s => %s", table01, text)
        want = table01N
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>a</th><th>b</th></tr>',
                '<tr><td>x y</td><td></td></tr>',
                '<tr><td></td><td>1</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7421(self) -> None:
        text = tabtotext.tabtoHTML(table02)
        logg.debug("%s => %s", table02, text)
        want = table02N
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>a</th><th>b</th></tr>', '<tr><td>x</td><td>0</td></tr>',
                '<tr><td></td><td>2</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7422(self) -> None:
        text = tabtotext.tabtoHTML(table22)
        logg.debug("%s => %s", table22, text)
        want = table22
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>a</th><th>b</th></tr>', '<tr><td>x</td><td>3</td></tr>',
                '<tr><td>y</td><td>2</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7423(self) -> None:
        text = tabtotext.tabtoHTML(table33)
        logg.debug("%s => %s", table33, text)
        want = table33Q
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>a</th><th>b</th><th>c</th></tr>',
                '<tr><td>x</td><td>3</td><td>2021-12-31</td></tr>',
                '<tr><td>y</td><td>2</td><td>2021-12-30</td></tr>',
                '<tr><td>~</td><td></td><td>2021-12-31</td></tr>', '</table>']
        ['a;b;c', 'x;3;2021-12-31', 'y;2;2021-12-30', '~;~;2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)

    def test_7431(self) -> None:
        text = tabtotext.tabtoHTML(test011, legend=["a result", "was found"])
        logg.debug("%s => %s", test011, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>~</td></tr>', '</table>',
                '', '<ul>', '<li>a result</li>', '<li>was found</li>', '</ul>']
        self.assertEqual(cond, text.splitlines())
    def test_7432(self) -> None:
        text = tabtotext.tabtoHTML(test012, legend=["a result", "was found"])
        logg.debug("%s => %s", test012, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>',
                '<tr><td>(no)</td></tr>', '</table>', '', '<ul>', '<li>a result</li>', '<li>was found</li>', '</ul>']
        self.assertEqual(cond, text.splitlines())
    def test_7433(self) -> None:
        text = tabtotext.tabtoHTML(test013, legend=["a result", "was found"])
        logg.debug("%s => %s", test013, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>',
                '<tr><td>(yes)</td></tr>', '</table>', '', '<ul>', '<li>a result</li>', '<li>was found</li>', '</ul>']
        self.assertEqual(cond, text.splitlines())
    def test_7434(self) -> None:
        text = tabtotext.tabtoHTML(test014, legend=["a result", "was found"])
        logg.debug("%s => %s", test014, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td></td></tr>', '</table>',
                '', '<ul>', '<li>a result</li>', '<li>was found</li>', '</ul>']
        self.assertEqual(cond, text.splitlines())
    def test_7435(self) -> None:
        text = tabtotext.tabtoHTML(test015, legend=["a result", "was found"])
        logg.debug("%s => %s", test015, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>5678</td></tr>',
                '</table>', '', '<ul>', '<li>a result</li>', '<li>was found</li>', '</ul>']
        self.assertEqual(cond, text.splitlines())
    def test_7436(self) -> None:
        text = tabtotext.tabtoHTML(test016, legend=["a result", "was found"])
        logg.debug("%s => %s", test016, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>123</td></tr>', '</table>',
                '', '<ul>', '<li>a result</li>', '<li>was found</li>', '</ul>']
        self.assertEqual(cond, text.splitlines())
    def test_7437(self) -> None:
        text = tabtotext.tabtoHTML(test017, legend=["a result", "was found"])
        logg.debug("%s => %s", test017, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>123.40</td></tr>',
                '</table>', '', '<ul>', '<li>a result</li>', '<li>was found</li>', '</ul>']
        self.assertEqual(cond, text.splitlines())
    def test_7438(self) -> None:
        text = tabtotext.tabtoHTML(test018, legend=["a result", "was found"])
        logg.debug("%s => %s", test018, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>2021-12-31</td></tr>',
                '</table>', '', '<ul>', '<li>a result</li>', '<li>was found</li>', '</ul>']
        self.assertEqual(cond, text.splitlines())
    def test_7439(self) -> None:
        text = tabtotext.tabtoHTML(test019, legend=["a result", "was found"])
        logg.debug("%s => %s", test019, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th></tr>', '<tr><td>2021-12-31</td></tr>',
                '</table>', '', '<ul>', '<li>a result</li>', '<li>was found</li>', '</ul>']
        self.assertEqual(cond, text.splitlines())
    def test_7444(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        text = tabtotext.tabtoHTML(itemlist, sorts=['b', 'a'])
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th><th>a</th></tr>',
                '<tr><td>1</td><td>y</td></tr>', '<tr><td>2</td><td>x</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': 'y', 'b': 1}, {'a': 'x', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7445(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}, {'c': 'h'}]
        text = tabtotext.tabtoHTML(itemlist, sorts=['b', 'a'])
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th><th>a</th><th>c</th></tr>', '<tr><td>1</td><td>y</td><td></td></tr>',
                '<tr><td>2</td><td>x</td><td></td></tr>', '<tr><td></td><td></td><td>h</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': 'y', 'b': 1, 'c': None}, {'a': 'x', 'b': 2, 'c': None}, {'a': None, 'b': None, 'c': 'h'}, ]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7446(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}, {'c': 'h'}]
        text = tabtotext.tabtoHTML(itemlist, sorts=['b', 'a'], reorder=['a', 'b'])
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>a</th><th>b</th><th>c</th></tr>', '<tr><td>y</td><td>1</td><td></td></tr>',
                '<tr><td>x</td><td>2</td><td></td></tr>', '<tr><td></td><td></td><td>h</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': 'y', 'b': 1, 'c': None}, {'a': 'x', 'b': 2, 'c': None}, {'a': None, 'b': None, 'c': 'h'}, ]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7460(self) -> None:
        text = tabtotext.tabtoHTML(table01, ["b", "a"])
        logg.debug("%s => %s", table01, text)
        want = table01N
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th><th>a</th></tr>', '<tr><td></td><td>x y</td></tr>',
                '<tr><td>1</td><td></td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7461(self) -> None:
        text = tabtotext.tabtoHTML(table02, ["b", "a"])
        logg.debug("%s => %s", table02, text)
        want = table02N
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th><th>a</th></tr>', '<tr><td>0</td><td>x</td></tr>',
                '<tr><td>2</td><td></td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7462(self) -> None:
        text = tabtotext.tabtoHTML(table22, ["b", "a"])
        logg.debug("%s => %s", table22, text)
        want = table22
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th><th>a</th></tr>',
                '<tr><td>3</td><td>x</td></tr>', '<tr><td>2</td><td>y</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7463(self) -> None:
        text = tabtotext.tabtoHTML(table33, ["b", "a"])
        logg.debug("%s => %s", table33, text)
        want = table33Q
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th><th>a</th><th>c</th></tr>',
                '<tr><td>3</td><td>x</td><td>2021-12-31</td></tr>',
                '<tr><td>2</td><td>y</td><td>2021-12-30</td></tr>',
                '<tr><td></td><td>~</td><td>2021-12-31</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7465(self) -> None:
        text = tabtotext.tabtoHTML(table33, ["c", "a"])
        logg.debug("%s => %s", table33, text)
        want = table33Q
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>c</th><th>a</th><th>b</th></tr>',
                '<tr><td>2021-12-31</td><td>x</td><td>3</td></tr>',
                '<tr><td>2021-12-30</td><td>y</td><td>2</td></tr>',
                '<tr><td>2021-12-31</td><td>~</td><td></td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7466(self) -> None:
        text = tabtotext.tabtoHTML(table02, ["b", "a"], ["b", "a"])
        logg.debug("%s => %s", table02, text)
        want = table02N
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th><th>a</th></tr>', '<tr><td>0</td><td>x</td></tr>',
                '<tr><td>2</td><td></td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7467(self) -> None:
        text = tabtotext.tabtoHTML(table22, ["b", "a"], ["b", "a"])
        logg.debug("%s => %s", table22, text)
        want = rev(table22)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th><th>a</th></tr>', '<tr><td>2</td><td>y</td></tr>',
                '<tr><td>3</td><td>x</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7468(self) -> None:
        text = tabtotext.tabtoHTML(table33, ["b", "a"], ["b", "a", "c"])
        logg.debug("%s => %s", table33, text)
        want = rev(table33Q[:2]) + table33Q[2:]
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b</th><th>a</th><th>c</th></tr>',
                '<tr><td>2</td><td>y</td><td>2021-12-30</td></tr>',
                '<tr><td>3</td><td>x</td><td>2021-12-31</td></tr>',
                '<tr><td></td><td>~</td><td>2021-12-31</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7469(self) -> None:
        text = tabtotext.tabtoHTML(table33, ["c", "a"], ["c", "a", "b"])
        logg.debug("%s => %s", table33, text)
        want = rev(table33Q[:2]) + table33Q[2:]
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>c</th><th>a</th><th>b</th></tr>',
                '<tr><td>2021-12-30</td><td>y</td><td>2</td></tr>',
                '<tr><td>2021-12-31</td><td>x</td><td>3</td></tr>',
                '<tr><td>2021-12-31</td><td>~</td><td></td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)

    def test_7503(self) -> None:
        text = tabtotext.tabToHTML(test003, ["a|b"])
        logg.debug("%s => %s", test003, text)
        want = test003
        cond = ['<table border="1" cellpadding="8">', '<tr></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7504(self) -> None:
        text = tabtotext.tabToHTML(test004, ["a|b"])
        logg.debug("%s => %s", test004, text)
        want = test004Q
        cond = ['<table border="1" cellpadding="8">', '<tr></tr>', '<tr></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7505(self) -> None:
        text = tabtotext.tabToHTML(test005, ["a|b"])
        logg.debug("%s => %s", test005, text)
        want = test005
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>a</th></tr>', '<tr><td>x</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7506(self) -> None:
        text = tabtotext.tabToHTML(test006, ["a|b"])
        logg.debug("%s => %s", test006, text)
        want = test006
        cond = ['<table border="1" cellpadding="8">',  # -
                '<tr><th>a<br />b</th></tr>',  # -
                '<tr><td>x<br />y</td></tr>',  # -
                '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7507(self) -> None:
        text = tabtotext.tabToHTML(test007, ["a|b"])
        logg.debug("%s => %s", test007, text)
        want = rev(test007Q)
        cond = ['<table border="1" cellpadding="8">',  # -
                '<tr><th>a<br />b</th></tr>',  # -
                '<tr><td><br />v</td></tr>',  # -
                '<tr><td>x<br />y</td></tr>',  # -
                '</table>']
        logg.debug("cond => %s", cond)
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7508(self) -> None:
        text = tabtotext.tabToHTML(test008, ["a|b"])
        logg.debug("%s => %s", test008, text)
        want = rev(test008N2)
        cond = ['<table border="1" cellpadding="8">',  # -
                '<tr><th>a<br />b</th></tr>',  # -
                '<tr><td><br />v</td></tr>',  # -
                '<tr><td>x<br /></td></tr>',  # -
                '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7509(self) -> None:
        text = tabtotext.tabToHTML(test009, ["a|b"])
        logg.debug("%s => %s", test009, text)
        want = test009Q
        cond = ['<table border="1" cellpadding="8">',  # -
                '<tr><th>b</th></tr>',  # -
                '<tr><td></td></tr>',  # -
                '<tr><td>v</td></tr>',  # -
                '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7513(self) -> None:
        text = tabtotext.tabToHTML(test003, ["a|b"])
        logg.debug("%s => %s", test003, text)
        want = test003
        cond = ['<table border="1" cellpadding="8">', '<tr></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7514(self) -> None:
        text = tabtotext.tabToHTML(test004, ["b|a"])
        logg.debug("%s => %s", test004, text)
        want = test004Q
        cond = ['<table border="1" cellpadding="8">', '<tr></tr>', '<tr></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7515(self) -> None:
        text = tabtotext.tabToHTML(test005, ["b|a"])
        logg.debug("%s => %s", test005, text)
        want = test005
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>a</th></tr>', '<tr><td>x</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7516(self) -> None:
        text = tabtotext.tabToHTML(test006, ["b|a"])
        logg.debug("%s => %s", test006, text)
        want = test006
        cond = ['<table border="1" cellpadding="8">',  # -
                '<tr><th>b<br />a</th></tr>',  # -
                '<tr><td>y<br />x</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7517(self) -> None:
        text = tabtotext.tabToHTML(test007, ["b|a"])
        logg.debug("%s => %s", test007, text)
        want = rev(test007)
        cond = ['<table border="1" cellpadding="8">',  # -
                '<tr><th>b<br />a</th></tr>',  # -
                '<tr><td>v<br /></td></tr>',  # -
                '<tr><td>y<br />x</td></tr>',  # -
                '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7518(self) -> None:
        text = tabtotext.tabToHTML(test008, ["b|a"])
        logg.debug("%s => %s", test008, text)
        want = test008N1
        cond = ['<table border="1" cellpadding="8">',  # -
                '<tr><th>b<br />a</th></tr>',  # -
                '<tr><td><br />x</td></tr>',  # -
                '<tr><td>v<br /></td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7519(self) -> None:
        text = tabtotext.tabToHTML(test009, ["b|a"])
        logg.debug("%s => %s", test009, text)
        want = test009Q
        cond = ['<table border="1" cellpadding="8">',  # -
                '<tr><th>b</th></tr>',  # -
                '<tr><td></td></tr>',  # -
                '<tr><td>v</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7523(self) -> None:
        text = tabtotext.tabtoHTML(test003, ["a|b"])
        logg.debug("%s => %s", test003, text)
        cond = ['<table border="1" cellpadding="8">', '<tr></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7524(self) -> None:
        text = tabtotext.tabtoHTML(test004, ["b|a"])
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">', '<tr></tr>', '<tr></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7525(self) -> None:
        text = tabtotext.tabtoHTML(test005, ["b|a"])
        logg.debug("%s => %s", test005, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>a</th></tr>', '<tr><td>x</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7526(self) -> None:
        text = tabtotext.tabtoHTML(test006, ["b|a"])
        logg.debug("%s => %s", test006, text)
        cond = ['<table border="1" cellpadding="8">',  # -
                '<tr><th>b<br />a</th></tr>',  # -
                '<tr><td>y<br />x</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7527(self) -> None:
        text = tabtotext.tabtoHTML(test007, ["b|a"])
        logg.debug("%s => %s", test007, text)
        cond = ['<table border="1" cellpadding="8">',  # -
                '<tr><th>b<br />a</th></tr>',  # -
                '<tr><td>y<br />x</td></tr>',  # -
                '<tr><td>v<br /></td></tr>',  # -
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7528(self) -> None:
        text = tabtotext.tabtoHTML(test008, ["b|a"])
        logg.debug("%s => %s", test008, text)
        cond = ['<table border="1" cellpadding="8">',  # -
                '<tr><th>b<br />a</th></tr>',  # -
                '<tr><td><br />x</td></tr>',  # -
                '<tr><td>v<br /></td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7529(self) -> None:
        text = tabtotext.tabtoHTML(test009, ["b|a"])
        logg.debug("%s => %s", test009, text)
        cond = ['<table border="1" cellpadding="8">',  # -
                '<tr><th>b</th></tr>',  # -
                '<tr><td></td></tr>',  # -
                '<tr><td>v</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7530(self) -> None:
        text = tabtotext.tabtoHTML(table01, ["a|b"])
        logg.debug("%s => %s", table01, text.splitlines())
        want = table01N2
        cond = ['<table border="1" cellpadding="8">', '<tr><th>a<br />b</th></tr>',
                '<tr><td>x y<br /></td></tr>', '<tr><td><br />1</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7531(self) -> None:
        text = tabtotext.tabtoHTML(table02, ["a|b"])
        logg.debug("%s => %s", table02, text.splitlines())
        want = table02N
        cond = ['<table border="1" cellpadding="8">', '<tr><th>a<br />b</th></tr>',
                '<tr><td>x<br />0</td></tr>', '<tr><td><br />2</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7532(self) -> None:
        text = tabtotext.tabtoHTML(table22, ["a|b"])
        logg.debug("%s => %s", table22, text.splitlines())
        want = table22
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>a<br />b</th></tr>', '<tr><td>x<br />3</td></tr>', '<tr><td>y<br />2</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7533(self) -> None:
        text = tabtotext.tabtoHTML(table33, ["a|b"])
        logg.debug("%s => %s", table33, text.splitlines())
        want = table33
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>a<br />b</th><th>c</th></tr>',
                '<tr><td>x<br />3</td><td>2021-12-31</td></tr>',
                '<tr><td>y<br />2</td><td>2021-12-30</td></tr>',
                '<tr><td>~<br /></td><td>2021-12-31</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(_date(want), back)
    def test_7534(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"])
        logg.debug("%s => %s", table44, text.splitlines())
        want = table44N
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>a<br />b</th><th>c</th><th>d</th></tr>',
                '<tr><td>x<br />3</td><td>(yes)</td><td>0.40</td></tr>',
                '<tr><td>y<br />2</td><td>(no)</td><td>0.30</td></tr>',
                '<tr><td>~<br />~</td><td>(yes)</td><td>0.20</td></tr>',
                '<tr><td>y<br />1</td><td></td><td>0.10</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7535(self) -> None:
        text = tabtotext.tabtoHTML(table01, ["b|a"])
        logg.debug("%s => %s", table01, text.splitlines())
        want = table01N1
        cond = ['<table border="1" cellpadding="8">', '<tr><th>b<br />a</th></tr>',
                '<tr><td><br />x y</td></tr>', '<tr><td>1<br /></td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7536(self) -> None:
        text = tabtotext.tabtoHTML(table02, ["b|a"])
        logg.debug("%s => %s", table02, text.splitlines())
        want = table02
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />a</th></tr>', '<tr><td>0<br />x</td></tr>',
                '<tr><td>2<br /></td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7537(self) -> None:
        text = tabtotext.tabtoHTML(table22, ["b|a"])
        logg.debug("%s => %s", table22, text.splitlines())
        want = table22
        cond = ['<table border="1" cellpadding="8">', '<tr><th>b<br />a</th></tr>',
                '<tr><td>3<br />x</td></tr>', '<tr><td>2<br />y</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7538(self) -> None:
        text = tabtotext.tabtoHTML(table33, ["b|a"])
        logg.debug("%s => %s", table33, text.splitlines())
        want = table33Q
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />a</th><th>c</th></tr>',
                '<tr><td>3<br />x</td><td>2021-12-31</td></tr>',
                '<tr><td>2<br />y</td><td>2021-12-30</td></tr>',
                '<tr><td><br />~</td><td>2021-12-31</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(_date(want), back)
    @unittest.expectedFailure
    def test_7539(self) -> None:
        text = tabtotext.tabtoHTML(table33, ["b|c|a"])
        logg.debug("%s => %s", table33, text.splitlines())
        want = table33
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />c<br />a</th></tr>',
                '<tr><td>3<br />2021-12-31<br />x</td></tr>',
                '<tr><td>2<br />2021-12-30<br />y</td></tr>',
                '<tr><td><br />2021-12-31<br />~</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(_date(want), back)

    def test_7544(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        text = tabtotext.tabToHTML(itemlist, sorts=['b', 'a'], combine={'b': 'a'})
        logg.debug("%s => %s", itemlist, text)
        cond = ['<table border="1" cellpadding="8">', '<tr><th>b<br />a</th></tr>',
                '<tr><td>1<br />y</td></tr>', '<tr><td>2<br />x</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': 'y', 'b': 1}, {'a': 'x', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7545(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}, {'c': 'h'}]
        text = tabtotext.tabToHTML(itemlist, sorts=['b', 'a'], combine={'b': 'a'})
        logg.debug("%s => %s", itemlist, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />a</th><th>c</th></tr>', '<tr><td>1<br />y</td><td></td></tr>',
                '<tr><td>2<br />x</td><td></td></tr>', '<tr><td><br /></td><td>h</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': 'y', 'b': 1, 'c': None}, {'a': 'x', 'b': 2, 'c': None}, {'b': None, 'c': 'h'}, ]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)

    def test_7554(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        text = tabtotext.tabToHTML(itemlist, sorts=['b', 'a'], combine={'a': 'b'})
        logg.debug("%s => %s", itemlist, text)
        cond = ['<table border="1" cellpadding="8">', '<tr><th>a<br />b</th></tr>',
                '<tr><td>y<br />1</td></tr>', '<tr><td>x<br />2</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': 'y', 'b': 1}, {'a': 'x', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7555(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}, {'c': 'h'}]
        text = tabtotext.tabToHTML(itemlist, sorts=['b', 'a'], combine={'a': 'b'})
        logg.debug("%s => %s", itemlist, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>a<br />b</th><th>c</th></tr>', '<tr><td>y<br />1</td><td></td></tr>',
                '<tr><td>x<br />2</td><td></td></tr>', '<tr><td><br /></td><td>h</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': 'y', 'b': 1, 'c': None}, {'a': 'x', 'b': 2, 'c': None}, {'a': None, 'c': 'h'}, ]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)

    def test_7571(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        formats = {"a": ' {:}'}
        headers = ['b', 'a']
        text = tabtotext.tabToHTML(itemlist, ['b', 'a'], formats, combine={'a': 'b'})
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th style="text-align: right">a<br />b</th></tr>',  # ,
                '<tr><td style="text-align: right"> y<br />1</td></tr>',  # ,
                '<tr><td style="text-align: right"> x<br />2</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': ' y', 'b': 1}, {'a': ' x', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7572(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        formats = {"a": ' %s'}
        headers = ['b', 'a']
        text = tabtotext.tabToHTML(itemlist, ['b', 'a'], formats, combine={'b': 'a'})
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">', '<tr><th>b<br />a</th></tr>',  # ,
                '<tr><td>1<br /> y</td></tr>',  # ,
                '<tr><td>2<br /> x</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': ' y', 'b': 1}, {'a': ' x', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7573(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        formats = {"a": '"%s"', "b": "%.2f"}
        headers = ['b', 'a']
        text = tabtotext.tabToHTML(itemlist, ['b', 'a'], formats, combine={'b': 'a'})
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th style="text-align: right">b<br />a</th></tr>',  # ,
                '<tr><td style="text-align: right">1.00<br />&quot;y&quot;</td></tr>',  # ,
                '<tr><td style="text-align: right">2.00<br />&quot;x&quot;</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': '"y"', 'b': 1}, {'a': '"x"', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7574(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        formats = {"a": '"{:}"', "b": "{:.2f}"}
        headers = ['b', 'a']
        text = tabtotext.tabToHTML(itemlist, ['b', 'a'], formats, combine={'b': 'a'})
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th style="text-align: right">b<br />a</th></tr>',  # ,
                '<tr><td style="text-align: right">1.00<br />&quot;y&quot;</td></tr>',  # ,
                '<tr><td style="text-align: right">2.00<br />&quot;x&quot;</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': '"y"', 'b': 1}, {'a': '"x"', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7575(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2.}, {'a': "y", 'b': 1.}]
        formats = {"a": '"{:}"', "b": "%.2f"}
        headers = ['b', 'a']
        text = tabtotext.tabToHTML(itemlist, ['b', 'a'], formats, combine={'b': 'a'})
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th style="text-align: right">b<br />a</th></tr>',  # ,
                '<tr><td style="text-align: right">1.00<br />&quot;y&quot;</td></tr>',  # ,
                '<tr><td style="text-align: right">2.00<br />&quot;x&quot;</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': '"y"', 'b': 1}, {'a': '"x"', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7576(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2.}, {'a': "y", 'b': 1.}]
        formats = {"a": '"{:}"', "b": "{:.2f}"}
        headers = ['b', 'a']
        text = tabtotext.tabToHTML(itemlist, ['b', 'a'], formats, combine={'b': 'a'})
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th style="text-align: right">b<br />a</th></tr>',  # ,
                '<tr><td style="text-align: right">1.00<br />&quot;y&quot;</td></tr>',  # ,
                '<tr><td style="text-align: right">2.00<br />&quot;x&quot;</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': '"y"', 'b': 1}, {'a': '"x"', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7577(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2.}, {'a': "y", 'b': 1.}]
        formats = {"a": '"{:}"', "b": "{:$}"}
        headers = ['b', 'a']
        text = tabtotext.tabToHTML(itemlist, ['b', 'a'], formats, combine={'b': 'a'})
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th style="text-align: right">b<br />a</th></tr>',  # ,
                X('<tr><td style="text-align: right">1.00$<br />&quot;y&quot;</td></tr>'),  # ,
                X('<tr><td style="text-align: right">2.00$<br />&quot;x&quot;</td></tr>'), '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': '"y"', 'b': 1}, {'a': '"x"', 'b': 2}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7578(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2.}, {'a': "y", 'b': 1.}]
        formats = {"a": '"{:5s}"', "b": "{:3f}"}
        headers = ['b', 'a']
        text = tabtotext.tabToHTML(itemlist, ['b', 'a'], formats, combine={'b': 'a'})
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th style="text-align: right">b<br />a</th></tr>',  # ,
                '<tr><td style="text-align: right">1.000000<br />&quot;y    &quot;</td></tr>',  # ,
                '<tr><td style="text-align: right">2.000000<br />&quot;x    &quot;</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': '"y    "', 'b': 1.0}, {'a': '"x    "', 'b': 2.0}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7579(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 22.}, {'a': "y", 'b': 1.}]
        formats = {"a": '"{:>5s}"', "b": "{:>3f}"}
        headers = ['b', 'a']
        text = tabtotext.tabToHTML(itemlist, ['b', 'a'], formats, combine={'a': 'b'})
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th style="text-align: right">a<br />b</th></tr>',  # ,
                '<tr><td style="text-align: right">&quot;    y&quot;<br />1.000000</td></tr>',  # ,
                '<tr><td style="text-align: right">&quot;    x&quot;<br />22.000000</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': '"    y"', 'b': 1.0}, {'a': '"    x"', 'b': 22.0}, ]  # order of rows swapped
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7594(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["a|b"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>a<br />b</th></tr>', '<tr><td>~<br />~</td></tr>',
                '<tr><td>x<br />3</td></tr>', '<tr><td>y<br />1</td></tr>',
                '<tr><td>y<br />2</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7595(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["b|a"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />a</th></tr>', '<tr><td>1<br />y</td></tr>',
                '<tr><td>2<br />y</td></tr>', '<tr><td>3<br />x</td></tr>',
                '<tr><td>~<br />~</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7596(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["b|d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />d</th></tr>', '<tr><td>1<br />0.10</td></tr>',
                '<tr><td>2<br />0.30</td></tr>', '<tr><td>3<br />0.40</td></tr>',
                '<tr><td>~<br />0.20</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7598(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["a|b|d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>a<br />b<br />d</th></tr>',
                '<tr><td>~<br />~<br />0.20</td></tr>',
                '<tr><td>x<br />3<br />0.40</td></tr>',
                '<tr><td>y<br />1<br />0.10</td></tr>',
                '<tr><td>y<br />2<br />0.30</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7599(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["b|c|a"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />c<br />a</th></tr>',
                '<tr><td>1<br /><br />y</td></tr>',
                '<tr><td>2<br />(no)<br />y</td></tr>',
                '<tr><td>3<br />(yes)<br />x</td></tr>',
                '<tr><td>~<br />(yes)<br />~</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7600(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["b|d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />d</th></tr>', '<tr><td>1<br />0.10</td></tr>',
                '<tr><td>2<br />0.30</td></tr>', '<tr><td>3<br />0.40</td></tr>',
                '<tr><td>~<br />0.20</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7601(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["b:02.1f|d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th style="text-align: right">b<br />d</th></tr>',
                '<tr><td style="text-align: right">1.0<br />0.10</td></tr>',
                '<tr><td style="text-align: right">2.0<br />0.30</td></tr>',
                '<tr><td style="text-align: right">3.0<br />0.40</td></tr>',
                '<tr><td style="text-align: right">~<br />0.20</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7602(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b:02.1f"], ["b|d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th style="text-align: right">b<br />d</th></tr>',
                '<tr><td style="text-align: right">1.0<br />0.10</td></tr>',
                '<tr><td style="text-align: right">2.0<br />0.30</td></tr>',
                '<tr><td style="text-align: right">3.0<br />0.40</td></tr>',
                '<tr><td style="text-align: right">~<br />0.20</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7608(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["#|b|d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>#<br />b<br />d</th></tr>',
                '<tr><td>1<br />3<br />0.40</td></tr>',
                '<tr><td>2<br />2<br />0.30</td></tr>',
                '<tr><td>3<br />~<br />0.20</td></tr>',
                '<tr><td>4<br />1<br />0.10</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7609(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["b|d|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />d<br />#</th></tr>',
                '<tr><td>1<br />0.10<br />4</td></tr>',
                '<tr><td>2<br />0.30<br />2</td></tr>',
                '<tr><td>3<br />0.40<br />1</td></tr>',
                '<tr><td>~<br />0.20<br />3</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7610(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["b>|d|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />d<br />#</th></tr>',
                '<tr><td>1<br />0.10<br />4</td></tr>',
                '<tr><td>2<br />0.30<br />2</td></tr>',
                '<tr><td>3<br />0.40<br />1</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7611(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["b>x|d|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />d<br />#</th></tr>',
                '<tr><td>1<br />0.10<br />4</td></tr>',
                '<tr><td>2<br />0.30<br />2</td></tr>',
                '<tr><td>3<br />0.40<br />1</td></tr>',
                '<tr><td>~<br />0.20<br />3</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7612(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["b>1|d|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />d<br />#</th></tr>',
                '<tr><td>2<br />0.30<br />2</td></tr>',
                '<tr><td>3<br />0.40<br />1</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7613(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["b>=2|d|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />d<br />#</th></tr>',
                '<tr><td>2<br />0.30<br />2</td></tr>',
                '<tr><td>3<br />0.40<br />1</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7614(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["b>2|d|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />d<br />#</th></tr>',
                '<tr><td>3<br />0.40<br />1</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7615(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["b<=2|d|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />d<br />#</th></tr>',
                '<tr><td>1<br />0.10<br />4</td></tr>',
                '<tr><td>2<br />0.30<br />2</td></tr>',
                '<tr><td>~<br />0.20<br />3</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7616(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["b<2|d|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />d<br />#</th></tr>',
                '<tr><td>1<br />0.10<br />4</td></tr>',
                '<tr><td>~<br />0.20<br />3</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7617(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["b==1|d|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />d<br />#</th></tr>',
                '<tr><td>1<br />0.10<br />4</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7618(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["b=~1|d|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />d<br />#</th></tr>',
                '<tr><td>1<br />0.10<br />4</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7619(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["b<>1|d|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />d<br />#</th></tr>',
                '<tr><td>2<br />0.30<br />2</td></tr>',
                '<tr><td>3<br />0.40<br />1</td></tr>',
                '<tr><td>~<br />0.20<br />3</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7620(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["b|d>|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />d<br />#</th></tr>',
                '<tr><td>1<br />0.10<br />4</td></tr>',
                '<tr><td>2<br />0.30<br />2</td></tr>',
                '<tr><td>3<br />0.40<br />1</td></tr>',
                '<tr><td>~<br />0.20<br />3</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7621(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["b|d>x|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />d<br />#</th></tr>',
                '<tr><td>1<br />0.10<br />4</td></tr>',
                '<tr><td>2<br />0.30<br />2</td></tr>',
                '<tr><td>3<br />0.40<br />1</td></tr>',
                '<tr><td>~<br />0.20<br />3</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7622(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["b|d>0.1|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />d<br />#</th></tr>',
                '<tr><td>2<br />0.30<br />2</td></tr>',
                '<tr><td>3<br />0.40<br />1</td></tr>',
                '<tr><td>~<br />0.20<br />3</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7623(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["b|d>=0.2|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />d<br />#</th></tr>',
                '<tr><td>2<br />0.30<br />2</td></tr>',
                '<tr><td>3<br />0.40<br />1</td></tr>',
                '<tr><td>~<br />0.20<br />3</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7624(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["b|d>0.2|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />d<br />#</th></tr>',
                '<tr><td>2<br />0.30<br />2</td></tr>',
                '<tr><td>3<br />0.40<br />1</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7625(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["b|d<=0.2|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />d<br />#</th></tr>',
                '<tr><td>1<br />0.10<br />4</td></tr>',
                '<tr><td>~<br />0.20<br />3</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7626(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["b|d<0.2|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />d<br />#</th></tr>',
                '<tr><td>1<br />0.10<br />4</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7627(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["b|d==0.1|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />d<br />#</th></tr>',
                '<tr><td>1<br />0.10<br />4</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7628(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["b|d=~0.1|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />d<br />#</th></tr>',
                '<tr><td>1<br />0.10<br />4</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7629(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["b|d<>0.1|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />d<br />#</th></tr>',
                '<tr><td>2<br />0.30<br />2</td></tr>',
                '<tr><td>3<br />0.40<br />1</td></tr>',
                '<tr><td>~<br />0.20<br />3</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7630(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["b|a>|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />a<br />#</th></tr>',
                '<tr><td>1<br />y<br />4</td></tr>',
                '<tr><td>2<br />y<br />2</td></tr>',
                '<tr><td>3<br />x<br />1</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7632(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["b|a>x|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />a<br />#</th></tr>',
                '<tr><td>1<br />y<br />4</td></tr>',
                '<tr><td>2<br />y<br />2</td></tr>',
                '<tr><td>~<br />~<br />3</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7633(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["b|a>=y|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />a<br />#</th></tr>',
                '<tr><td>1<br />y<br />4</td></tr>',
                '<tr><td>2<br />y<br />2</td></tr>',
                '<tr><td>~<br />~<br />3</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7634(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["b|a>x|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />a<br />#</th></tr>',
                '<tr><td>1<br />y<br />4</td></tr>',
                '<tr><td>2<br />y<br />2</td></tr>',
                '<tr><td>~<br />~<br />3</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7635(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["b|a<=y|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />a<br />#</th></tr>',
                '<tr><td>1<br />y<br />4</td></tr>',
                '<tr><td>2<br />y<br />2</td></tr>',
                '<tr><td>3<br />x<br />1</td></tr>',
                '<tr><td>~<br />~<br />3</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7636(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["b|a<y|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />a<br />#</th></tr>',
                '<tr><td>3<br />x<br />1</td></tr>',
                '<tr><td>~<br />~<br />3</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7637(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["b|a==y|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />a<br />#</th></tr>',
                '<tr><td>1<br />y<br />4</td></tr>',
                '<tr><td>2<br />y<br />2</td></tr>',
                '<tr><td>~<br />~<br />3</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7638(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["b|a=~y|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />a<br />#</th></tr>',
                '<tr><td>1<br />y<br />4</td></tr>',
                '<tr><td>2<br />y<br />2</td></tr>',
                '<tr><td>~<br />~<br />3</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7639(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["b|a<>y|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />a<br />#</th></tr>',
                '<tr><td>3<br />x<br />1</td></tr>',
                '<tr><td>~<br />~<br />3</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7640(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["b|c>|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />c<br />#</th></tr>',
                '<tr><td>1<br /><br />4</td></tr>',
                '<tr><td>3<br />(yes)<br />1</td></tr>',
                '<tr><td>~<br />(yes)<br />3</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7641(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["b|c<>|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />c<br />#</th></tr>',
                '<tr><td>1<br /><br />4</td></tr>',
                '<tr><td>2<br />(no)<br />2</td></tr>',
                '<tr><td>3<br />(yes)<br />1</td></tr>',
                '<tr><td>~<br />(yes)<br />3</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7642(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["b|c>false|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />c<br />#</th></tr>',
                '<tr><td>1<br /><br />4</td></tr>',
                '<tr><td>3<br />(yes)<br />1</td></tr>',
                '<tr><td>~<br />(yes)<br />3</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7643(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["b|c>=true|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />c<br />#</th></tr>',
                '<tr><td>1<br /><br />4</td></tr>',
                '<tr><td>3<br />(yes)<br />1</td></tr>',
                '<tr><td>~<br />(yes)<br />3</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7644(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["b|c>true|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />c<br />#</th></tr>',
                '<tr><td>1<br /><br />4</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7645(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["b|c<=true|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />c<br />#</th></tr>',
                '<tr><td>1<br /><br />4</td></tr>',
                '<tr><td>2<br />(no)<br />2</td></tr>',
                '<tr><td>3<br />(yes)<br />1</td></tr>',
                '<tr><td>~<br />(yes)<br />3</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7646(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["b|c<true|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />c<br />#</th></tr>',
                '<tr><td>1<br /><br />4</td></tr>',
                '<tr><td>2<br />(no)<br />2</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7647(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["b|c==true|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />c<br />#</th></tr>',
                '<tr><td>1<br /><br />4</td></tr>',
                '<tr><td>3<br />(yes)<br />1</td></tr>',
                '<tr><td>~<br />(yes)<br />3</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7648(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["b|c=~true|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />c<br />#</th></tr>',
                '<tr><td>1<br /><br />4</td></tr>',
                '<tr><td>3<br />(yes)<br />1</td></tr>',
                '<tr><td>~<br />(yes)<br />3</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7649(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["b|c<>true|#"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />c<br />#</th></tr>',
                '<tr><td>1<br /><br />4</td></tr>',
                '<tr><td>2<br />(no)<br />2</td></tr>',
                '<tr><td>3<br />(yes)<br />1</td></tr>',
                '<tr><td>~<br />(yes)<br />3</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7660(self) -> None:
        text = tabtotext.tabtoHTML(table33, ["a|b"], ["b|c>|#"])
        logg.debug("%s => %s", table33, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />c<br />#</th></tr>',
                '<tr><td>2<br />2021-12-30<br />2</td></tr>',
                '<tr><td>3<br />2021-12-31<br />1</td></tr>',
                '<tr><td><br />2021-12-31<br />3</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7661(self) -> None:
        text = tabtotext.tabtoHTML(table33, ["a|b"], ["b|c<>|#"])
        logg.debug("%s => %s", table33, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />c<br />#</th></tr>',
                '<tr><td>2<br />2021-12-30<br />2</td></tr>',
                '<tr><td>3<br />2021-12-31<br />1</td></tr>',
                '<tr><td><br />2021-12-31<br />3</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7662(self) -> None:
        text = tabtotext.tabtoHTML(table33, ["a|b"], ["b|c>2021-12-30|#"])
        logg.debug("%s => %s", table33, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />c<br />#</th></tr>',
                '<tr><td>3<br />2021-12-31<br />1</td></tr>',
                '<tr><td><br />2021-12-31<br />3</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7663(self) -> None:
        text = tabtotext.tabtoHTML(table33, ["a|b"], ["b|c>=2021-12-30|#"])
        logg.debug("%s => %s", table33, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />c<br />#</th></tr>',
                '<tr><td>2<br />2021-12-30<br />2</td></tr>',
                '<tr><td>3<br />2021-12-31<br />1</td></tr>',
                '<tr><td><br />2021-12-31<br />3</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7664(self) -> None:
        text = tabtotext.tabtoHTML(table33, ["a|b"], ["b|c>2021-12-31|#"])
        logg.debug("%s => %s", table33, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />c<br />#</th></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7665(self) -> None:
        text = tabtotext.tabtoHTML(table33, ["a|b"], ["b|c<=2021-12-31|#"])
        logg.debug("%s => %s", table33, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />c<br />#</th></tr>',
                '<tr><td>2<br />2021-12-30<br />2</td></tr>',
                '<tr><td>3<br />2021-12-31<br />1</td></tr>',
                '<tr><td><br />2021-12-31<br />3</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7666(self) -> None:
        text = tabtotext.tabtoHTML(table33, ["a|b"], ["b|c<2021-12-31|#"])
        logg.debug("%s => %s", table33, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />c<br />#</th></tr>',
                '<tr><td>2<br />2021-12-30<br />2</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7667(self) -> None:
        text = tabtotext.tabtoHTML(table33, ["a|b"], ["b|c==2021-12-31|#"])
        logg.debug("%s => %s", table33, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />c<br />#</th></tr>',
                '<tr><td>3<br />2021-12-31<br />1</td></tr>',
                '<tr><td><br />2021-12-31<br />3</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7668(self) -> None:
        text = tabtotext.tabtoHTML(table33, ["a|b"], ["b|c=~2021-12-31|#"])
        logg.debug("%s => %s", table33, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />c<br />#</th></tr>',
                '<tr><td>3<br />2021-12-31<br />1</td></tr>',
                '<tr><td><br />2021-12-31<br />3</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7669(self) -> None:
        text = tabtotext.tabtoHTML(table33, ["a|b"], ["b|c<>2021-12-31|#"])
        logg.debug("%s => %s", table33, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>b<br />c<br />#</th></tr>',
                '<tr><td>2<br />2021-12-30<br />2</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7702(self) -> None:
        text = tabtotext.tabtoHTML(table02, ["a|b"], ["{a}+{b}"])
        logg.debug("%s => %s", table02, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>a b</th></tr>',
                '<tr><td>x+0</td></tr>',
                '<tr><td>~+2</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7703(self) -> None:
        text = tabtotext.tabtoHTML(table33, ["a|b"], ["{a}+{b} = {c}"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>a b c</th></tr>',
                '<tr><td>x+3 = 2021-12-31</td></tr>',
                '<tr><td>y+2 = 2021-12-30</td></tr>',
                '<tr><td>~+~ = 2021-12-31</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7704(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["{a}+{b} = {c}"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>a b c</th></tr>',
                '<tr><td>x+3 = (yes)</td></tr>',
                '<tr><td>y+1 = ~</td></tr>',
                '<tr><td>y+2 = (no)</td></tr>',
                '<tr><td>~+~ = (yes)</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7705(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["{a}+{b} = {c}", "d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>a b c</th><th>d</th></tr>',
                '<tr><td>x+3 = (yes)</td><td>0.40</td></tr>',
                '<tr><td>y+1 = ~</td><td>0.10</td></tr>',
                '<tr><td>y+2 = (no)</td><td>0.30</td></tr>',
                '<tr><td>~+~ = (yes)</td><td>0.20</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7706(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["d", "{a}+{b} = {c}"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>d</th><th>a b c</th></tr>',
                '<tr><td>0.10</td><td>y+1 = ~</td></tr>',
                '<tr><td>0.20</td><td>~+~ = (yes)</td></tr>',
                '<tr><td>0.30</td><td>y+2 = (no)</td></tr>',
                '<tr><td>0.40</td><td>x+3 = (yes)</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7712(self) -> None:
        text = tabtotext.tabtoHTML(table02, ["a|b"], ["{a}+{b}@info"])
        logg.debug("%s => %s", table02, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>info</th></tr>',
                '<tr><td>x+0</td></tr>',
                '<tr><td>~+2</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7713(self) -> None:
        text = tabtotext.tabtoHTML(table33, ["a|b"], ["{a}+{b} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>info</th></tr>',
                '<tr><td>x+3 = 2021-12-31</td></tr>',
                '<tr><td>y+2 = 2021-12-30</td></tr>',
                '<tr><td>~+~ = 2021-12-31</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7714(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["{a}+{b} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>info</th></tr>',
                '<tr><td>x+3 = (yes)</td></tr>',
                '<tr><td>y+1 = ~</td></tr>',
                '<tr><td>y+2 = (no)</td></tr>',
                '<tr><td>~+~ = (yes)</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7715(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["{a}+{b} = {c}@info", "d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>info</th><th>d</th></tr>',
                '<tr><td>x+3 = (yes)</td><td>0.40</td></tr>',
                '<tr><td>y+1 = ~</td><td>0.10</td></tr>',
                '<tr><td>y+2 = (no)</td><td>0.30</td></tr>',
                '<tr><td>~+~ = (yes)</td><td>0.20</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7716(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a|b"], ["d", "{a}+{b} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>d</th><th>info</th></tr>',
                '<tr><td>0.10</td><td>y+1 = ~</td></tr>',
                '<tr><td>0.20</td><td>~+~ = (yes)</td></tr>',
                '<tr><td>0.30</td><td>y+2 = (no)</td></tr>',
                '<tr><td>0.40</td><td>x+3 = (yes)</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7722(self) -> None:
        text = tabtotext.tabtoHTML(table02, ["a@x"], ["{a}+{b}@info"])
        logg.debug("%s => %s", table02, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>info</th></tr>',
                '<tr><td>x+0</td></tr>',
                '<tr><td>~+2</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7723(self) -> None:
        text = tabtotext.tabtoHTML(table33, ["a@x"], ["{a}+{b} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">', '<tr><th>info</th></tr>',
                '<tr><td>x+3 = 2021-12-31</td></tr>',
                '<tr><td>y+2 = 2021-12-30</td></tr>',
                '<tr><td>~+~ = 2021-12-31</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7724(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a@x"], ["{a}+{b} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>info</th></tr>',
                '<tr><td>x+3 = (yes)</td></tr>',
                '<tr><td>y+1 = ~</td></tr>',
                '<tr><td>y+2 = (no)</td></tr>',
                '<tr><td>~+~ = (yes)</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7725(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a@x"], ["{a}+{b} = {c}@info", "d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>info</th><th>d</th></tr>',
                '<tr><td>x+3 = (yes)</td><td>0.40</td></tr>',
                '<tr><td>y+1 = ~</td><td>0.10</td></tr>',
                '<tr><td>y+2 = (no)</td><td>0.30</td></tr>',
                '<tr><td>~+~ = (yes)</td><td>0.20</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7726(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a@x"], ["d", "{a}+{b} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>d</th><th>info</th></tr>',
                '<tr><td>0.10</td><td>y+1 = ~</td></tr>',
                '<tr><td>0.20</td><td>~+~ = (yes)</td></tr>',
                '<tr><td>0.30</td><td>y+2 = (no)</td></tr>',
                '<tr><td>0.40</td><td>x+3 = (yes)</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7732(self) -> None:
        text = tabtotext.tabtoHTML(table02, ["a@x"], ["{x}+{b}@info"])
        logg.debug("%s => %s", table02, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>info</th></tr>',
                '<tr><td>x+0</td></tr>',
                '<tr><td>~+2</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7733(self) -> None:
        text = tabtotext.tabtoHTML(table33, ["a@x"], ["{x}+{b} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>info</th></tr>',
                '<tr><td>x+3 = 2021-12-31</td></tr>',
                '<tr><td>y+2 = 2021-12-30</td></tr>',
                '<tr><td>~+~ = 2021-12-31</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7734(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a@x"], ["{x}+{b} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>info</th></tr>',
                '<tr><td>x+3 = (yes)</td></tr>',
                '<tr><td>y+1 = ~</td></tr>',
                '<tr><td>y+2 = (no)</td></tr>',
                '<tr><td>~+~ = (yes)</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7735(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a@x"], ["{x}+{b} = {c}@info", "d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>info</th><th>d</th></tr>',
                '<tr><td>x+3 = (yes)</td><td>0.40</td></tr>',
                '<tr><td>y+1 = ~</td><td>0.10</td></tr>',
                '<tr><td>y+2 = (no)</td><td>0.30</td></tr>',
                '<tr><td>~+~ = (yes)</td><td>0.20</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7736(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a@x"], ["d", "{x}+{b} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>d</th><th>info</th></tr>',
                '<tr><td>0.10</td><td>y+1 = ~</td></tr>',
                '<tr><td>0.20</td><td>~+~ = (yes)</td></tr>',
                '<tr><td>0.30</td><td>y+2 = (no)</td></tr>',
                '<tr><td>0.40</td><td>x+3 = (yes)</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7742(self) -> None:
        text = tabtotext.tabtoHTML(table02, ["a@x|b@y"], ["{x}+{y}@info"])
        logg.debug("%s => %s", table02, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>info</th></tr>',
                '<tr><td>x+0</td></tr>',
                '<tr><td>~+2</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7743(self) -> None:
        text = tabtotext.tabtoHTML(table33, ["a@x|b@y"], ["{x}+{y} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>info</th></tr>',
                '<tr><td>x+3 = 2021-12-31</td></tr>',
                '<tr><td>y+2 = 2021-12-30</td></tr>',
                '<tr><td>~+~ = 2021-12-31</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7744(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a@x|b@y"], ["{x}+{y} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['info', 'x+3 = (yes)', 'y+1 = ~', 'y+2 = (no)', '~+~ = (yes)']
        cond = ['<table border="1" cellpadding="8">', '<tr><th>info</th></tr>',
                '<tr><td>x+3 = (yes)</td></tr>',
                '<tr><td>y+1 = ~</td></tr>',
                '<tr><td>y+2 = (no)</td></tr>',
                '<tr><td>~+~ = (yes)</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7745(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a@x|b@y"], ["{x}+{y} = {c}@info", "d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>info</th><th>d</th></tr>',
                '<tr><td>x+3 = (yes)</td><td>0.40</td></tr>',
                '<tr><td>y+1 = ~</td><td>0.10</td></tr>',
                '<tr><td>y+2 = (no)</td><td>0.30</td></tr>',
                '<tr><td>~+~ = (yes)</td><td>0.20</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7746(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a@x|b@y"], ["d", "{x}+{y} = {c}@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>d</th><th>info</th></tr>',
                '<tr><td>0.10</td><td>y+1 = ~</td></tr>',
                '<tr><td>0.20</td><td>~+~ = (yes)</td></tr>',
                '<tr><td>0.30</td><td>y+2 = (no)</td></tr>',
                '<tr><td>0.40</td><td>x+3 = (yes)</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7752(self) -> None:
        text = tabtotext.tabtoHTML(table02, ["a@x|b@y"], ["x@info"])
        logg.debug("%s => %s", table02, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>info</th></tr>',
                '<tr><td></td></tr>',
                '<tr><td>x</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7753(self) -> None:
        text = tabtotext.tabtoHTML(table33, ["a@x|b@y"], ["x@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>info</th></tr>',
                '<tr><td>~</td></tr>',
                '<tr><td>x</td></tr>',
                '<tr><td>y</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7754(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a@x|b@y"], ["x@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>info</th></tr>',
                '<tr><td>~</td></tr>',
                '<tr><td>x</td></tr>',
                '<tr><td>y</td></tr>',
                '<tr><td>y</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7755(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a@x|b@y"], ["x@info", "d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>info</th><th>d</th></tr>',
                '<tr><td>~</td><td>0.20</td></tr>',
                '<tr><td>x</td><td>0.40</td></tr>',
                '<tr><td>y</td><td>0.10</td></tr>',
                '<tr><td>y</td><td>0.30</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7756(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a@x|b@y"], ["d", "x@info"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>d</th><th>info</th></tr>',
                '<tr><td>0.10</td><td>y</td></tr>',
                '<tr><td>0.20</td><td>~</td></tr>',
                '<tr><td>0.30</td><td>y</td></tr>',
                '<tr><td>0.40</td><td>x</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7762(self) -> None:
        text = tabtotext.tabtoHTML(table02, ["a@x|b@y"], ["x@info|y@mm"])
        logg.debug("%s => %s", table02, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>info</th><th>mm</th></tr>',
                '<tr><td></td><td>2</td></tr>',
                '<tr><td>x</td><td>0</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7763(self) -> None:
        text = tabtotext.tabtoHTML(table33, ["a@x|b@y"], ["x@info|y@mm"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>info</th><th>mm</th></tr>',
                '<tr><td>~</td><td></td></tr>',
                '<tr><td>x</td><td>3</td></tr>',
                '<tr><td>y</td><td>2</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7764(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a@x|b@y"], ["x@info|y@mm"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>info</th><th>mm</th></tr>',
                '<tr><td>~</td><td>~</td></tr>',
                '<tr><td>x</td><td>3</td></tr>',
                '<tr><td>y</td><td>1</td></tr>',
                '<tr><td>y</td><td>2</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7765(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a@x|b@y"], ["x@info|y@mm", "d"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['info;mm;d', '~;~;0.20', 'x;3;0.40', 'y;1;0.10', 'y;2;0.30']
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>info</th><th>mm</th><th>d</th></tr>',
                '<tr><td>~</td><td>~</td><td>0.20</td></tr>',
                '<tr><td>x</td><td>3</td><td>0.40</td></tr>',
                '<tr><td>y</td><td>1</td><td>0.10</td></tr>',
                '<tr><td>y</td><td>2</td><td>0.30</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7766(self) -> None:
        text = tabtotext.tabtoHTML(table44, ["a@x|b@y"], ["d", "x@info|y@mm"])
        logg.debug("%s => %s", table44, text.splitlines())
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>d</th><th>info</th><th>mm</th></tr>',
                '<tr><td>0.10</td><td>y</td><td>1</td></tr>',
                '<tr><td>0.20</td><td>~</td><td>~</td></tr>',
                '<tr><td>0.30</td><td>y</td><td>2</td></tr>',
                '<tr><td>0.40</td><td>x</td><td>3</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())

    def test_7803(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test003, ['a|b'], defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test003, text)
        cond = ['<table border="1" cellpadding="8">', '<tr></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())

    def test_7804(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test004, ['a|b'], defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        want = test004Q
        cond = ['<table border="1" cellpadding="8">', '<tr></tr>', '<tr></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7805(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test005, ['a|b'], defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test005, text)
        want = test005
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>a</th></tr>', '<tr><td>x</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7806(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test006, ['a|b'], defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test006, text)
        want = test006
        cond = ['<table border="1" cellpadding="8">',  # -
                '<tr><th>a<br />b</th></tr>',  # -
                '<tr><td>x<br />y</td></tr>',  # -
                '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7807(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test007, ['a|b'], defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test007, text)
        want = test007Q
        cond = ['<table border="1" cellpadding="8">',  # -
                '<tr><th>a<br />b</th></tr>',  # -
                '<tr><td>x<br />y</td></tr>',  # -
                '<tr><td><br />v</td></tr>',  # -
                '</table>']
        # note that tabtotext does always sort but old-style without headers did not
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7808(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test008, ['a|b'], defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test008, text)
        want = test008N2
        cond = ['<table border="1" cellpadding="8">',  # -
                '<tr><th>a<br />b</th></tr>',  # -
                '<tr><td>x<br /></td></tr>',  # -
                '<tr><td><br />v</td></tr>',  # -
                '</table>']
        # note that tabtotext does always sort but old-style without headers did not
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7809(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test009, ['a|b'], defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test009, text)
        want = test009Q
        cond = ['<table border="1" cellpadding="8">',  # -
                '<tr><th>b</th></tr>',  # -
                '<tr><td></td></tr>',  # -
                '<tr><td>v</td></tr>',  # -
                '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7823(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test003, ['a|b'], defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test003, text)
        want = test003
        cond = ['<table border="1" cellpadding="8">', '<tr></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7824(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test004, ['b|a'], defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        want = test004Q
        cond = ['<table border="1" cellpadding="8">', '<tr></tr>', '<tr></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7825(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test005, ['b|a'], defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test005, text)
        want = test005
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th>a</th></tr>', '<tr><td>x</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7826(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test006, ['b|a'], defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test006, text)
        want = test006
        cond = ['<table border="1" cellpadding="8">',  # -
                '<tr><th>b<br />a</th></tr>',  # -
                '<tr><td>y<br />x</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7827(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test007, ['b|a'], defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test007, text)
        want = test007
        cond = ['<table border="1" cellpadding="8">',  # -
                '<tr><th>b<br />a</th></tr>',  # -
                '<tr><td>y<br />x</td></tr>',  # -
                '<tr><td>v<br /></td></tr>',  # -
                '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7828(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test008, ['b|a'], defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test008, text)
        want = test008N1
        cond = ['<table border="1" cellpadding="8">',  # -
                '<tr><th>b<br />a</th></tr>',  # -
                '<tr><td><br />x</td></tr>',  # -
                '<tr><td>v<br /></td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7829(self) -> None:
        out = StringIO()
        res = tabtotext.print_tabtotext(out, test009, ['b|a'], defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test009, text)
        want = test009Q
        cond = ['<table border="1" cellpadding="8">',  # -
                '<tr><th>b</th></tr>',  # -
                '<tr><td></td></tr>',  # -
                '<tr><td>v</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        self.assertEqual(want, back)
    def test_7844(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        out = StringIO()
        res = tabtotext.print_tabtotext(out, itemlist, ['b|a'], defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        # text = tabtotext.tabToHTML(itemlist, sorts=['b', 'a'], combine={'b': 'a'})
        logg.debug("%s => %s", itemlist, text)
        want = itemlist
        cond = ['<table border="1" cellpadding="8">', '<tr><th>b<br />a</th></tr>',
                '<tr><td>2<br />x</td></tr>', '<tr><td>1<br />y</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7845(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}, {'c': 'h'}]
        out = StringIO()
        res = tabtotext.print_tabtotext(out, itemlist, ['b|a'], defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        # text = tabtotext.tabToHTML(itemlist, sorts=['b', 'a'], combine={'b': 'a'})
        logg.debug("%s => %s", itemlist, text)
        want: JSONList = [{'a': "x", 'b': 2, 'c': None}, {'a': "y", 'b': 1, 'c': None}, {'c': 'h', 'b': None}]
        cond = ['<table border="1" cellpadding="8">', '<tr><th>b<br />a</th><th>c</th></tr>',
                '<tr><td>2<br />x</td><td></td></tr>',
                '<tr><td>1<br />y</td><td></td></tr>',
                '<tr><td><br /></td><td>h</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7846(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}, {'c': 'h'}]
        out = StringIO()
        res = tabtotext.print_tabtotext(out, itemlist, ['b|a'], ["b|a"], defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        # text = tabtotext.tabToHTML(itemlist, sorts=['b', 'a'], combine={'b': 'a'})
        logg.debug("%s => %s", itemlist, text.splitlines())
        want: JSONList = [{'a': "y", 'b': 1, }, {'a': "x", 'b': 2, }, {'b': None}]
        cond = ['<table border="1" cellpadding="8">', '<tr><th>b<br />a</th></tr>',
                '<tr><td>1<br />y</td></tr>', '<tr><td>2<br />x</td></tr>',
                '<tr><td><br /></td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7871(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        out = StringIO()
        res = tabtotext.print_tabtotext(out, itemlist, ['a: {:}|b'], defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th style="text-align: right">a<br />b</th></tr>',  # ,
                '<tr><td style="text-align: right"> x<br />2</td></tr>',  # -
                '<tr><td style="text-align: right"> y<br />1</td></tr>',  # ,
                '</table>']
        # this is ordered differently!
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': ' x', 'b': 2}, {'a': ' y', 'b': 1}, ]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7872(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        out = StringIO()
        res = tabtotext.print_tabtotext(out, itemlist, ['b|a: %s'], defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">', '<tr><th>b<br />a</th></tr>',  # ,
                '<tr><td>2<br /> x</td></tr>',
                '<tr><td>1<br /> y</td></tr>',  # ,
                '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': ' x', 'b': 2}, {'a': ' y', 'b': 1}, ]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7873(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        out = StringIO()
        res = tabtotext.print_tabtotext(out, itemlist, ['b:<2.f|a:"%s"'], defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">', '<tr><th>b<br />a</th></tr>',  # ,
                '<tr><td>2<br />&quot;x&quot;</td></tr>',
                '<tr><td>1<br />&quot;y&quot;</td></tr>',  # ,
                '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': '"x"', 'b': 2}, {'a': '"y"', 'b': 1}, ]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7874(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2}, {'a': "y", 'b': 1}]
        out = StringIO()
        res = tabtotext.print_tabtotext(out, itemlist, ['b:{:.2f}|a:"{:}"'], defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th style="text-align: right">b<br />a</th></tr>',  # ,
                '<tr><td style="text-align: right">2.00<br />&quot;x&quot;</td></tr>',
                '<tr><td style="text-align: right">1.00<br />&quot;y&quot;</td></tr>',  # ,
                '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': '"x"', 'b': 2}, {'a': '"y"', 'b': 1}, ]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7875(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2.}, {'a': "y", 'b': 1.}]
        out = StringIO()
        res = tabtotext.print_tabtotext(out, itemlist, ['b:<.2f|a:"{:}"'], defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">', '<tr><th>b<br />a</th></tr>',  # ,
                '<tr><td>2.00<br />&quot;x&quot;</td></tr>',
                '<tr><td>1.00<br />&quot;y&quot;</td></tr>',  # ,
                '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': '"x"', 'b': 2}, {'a': '"y"', 'b': 1}, ]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7876(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2.}, {'a': "y", 'b': 1.}]
        out = StringIO()
        res = tabtotext.print_tabtotext(out, itemlist, ['b:{:.2f}|a:"{:}"'], defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th style="text-align: right">b<br />a</th></tr>',  # ,
                '<tr><td style="text-align: right">2.00<br />&quot;x&quot;</td></tr>',
                '<tr><td style="text-align: right">1.00<br />&quot;y&quot;</td></tr>',  # ,
                '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': '"x"', 'b': 2}, {'a': '"y"', 'b': 1}, ]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7877(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2.}, {'a': "y", 'b': 1.}]
        out = StringIO()
        res = tabtotext.print_tabtotext(out, itemlist, ['b:{:$}|a:"{:}"'], defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th style="text-align: right">b<br />a</th></tr>',  # ,
                X('<tr><td style="text-align: right">2.00$<br />&quot;x&quot;</td></tr>'),
                X('<tr><td style="text-align: right">1.00$<br />&quot;y&quot;</td></tr>'),  # ,
                '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': '"x"', 'b': 2}, {'a': '"y"', 'b': 1}, ]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7878(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 2.}, {'a': "y", 'b': 1.}]
        out = StringIO()
        res = tabtotext.print_tabtotext(out, itemlist, ['b:{:3f}|a:"{:5s}"'], defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th style="text-align: right">b<br />a</th></tr>',  # ,
                '<tr><td style="text-align: right">2.000000<br />&quot;x    &quot;</td></tr>',
                '<tr><td style="text-align: right">1.000000<br />&quot;y    &quot;</td></tr>',  # ,
                '</table>']
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': '"x    "', 'b': 2.0}, {'a': '"y    "', 'b': 1.0}, ]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7879(self) -> None:
        itemlist: JSONList = [{'a': "x", 'b': 22.}, {'a': "y", 'b': 1.}]
        formats = {"a": '"{:>5s}"', "b": "{:>3f}"}
        headers = ['b', 'a']
        out = StringIO()
        res = tabtotext.print_tabtotext(out, itemlist, ['a:"{:>5s}"|b:{:>3f}'], defaultformat="html")
        logg.info("print_tabtotext %s", res)
        text = out.getvalue()
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">',
                '<tr><th style="text-align: right">a<br />b</th></tr>',  # ,
                '<tr><td style="text-align: right">&quot;    x&quot;<br />22.000000</td></tr>',  # -
                '<tr><td style="text-align: right">&quot;    y&quot;<br />1.000000</td></tr>',  # ,
                '</table>']
        # sorted differently!
        self.assertEqual(cond, text.splitlines())
        back = loadHTML(text)
        want = [{'a': '"    x"', 'b': 22.0}, {'a': '"    y"', 'b': 1.0}, ]
        logg.info("%s => %s", want, back)
        self.assertEqual(want, back)
    def test_7901(self) -> None:
        item1 = Item2("x", 2)
        item2 = Item2("y", 3)
        itemlist: DataList = [item1, item2]
        text = tabtotext.tabToFMTx("html", itemlist)
        logg.debug("%s => %s", test004, text)
        cond = ['<table border="1" cellpadding="8">', '<tr><th>a</th><th>b</th></tr>',
                '<tr><td>x</td><td>2</td></tr>',
                '<tr><td>y</td><td>3</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
    def test_7911(self) -> None:
        tablist = {"table01": table01, "table02": table02}
        text = tabtotext.tablistmakeFMT("html", tabtotext.tablistfor(tablist))
        logg.debug("%s => %s", tablist, text.splitlines())
        cond = ['<table border="1" cellpadding="8"><caption>table01</caption>',
                '<tr><th>a</th><th>b</th></tr>',
                '<tr><td>x y</td><td></td></tr>',
                '<tr><td></td><td>1</td></tr>',
                '</table>',
                '<table border="1" cellpadding="8"><caption>table02</caption>',
                '<tr><th>a</th><th>b</th></tr>',
                '<tr><td>x</td><td>0</td></tr>',
                '<tr><td></td><td>2</td></tr>',
                '</table>']
        self.assertEqual(cond, text.splitlines())
        want = {"table01": table01N, "table02": table02N}
        scan = tabtotext.tablistscanHTML(text)
        back = dict(tabtotext.tablistmap(scan))
        logg.debug("\n>> %s\n<< %s", want, back)
        self.assertEqual(want, back)
    def test_7912(self) -> None:
        tablist = {"table22": table22, "table33": table33}
        text = tabtotext.tablistmakeFMT("html", tabtotext.tablistfor(tablist))
        logg.debug("%s => %s", tablist, text.splitlines())
        cond = ['<table border="1" cellpadding="8"><caption>table22</caption>',
                '<tr><th>a</th><th>b</th></tr>',
                '<tr><td>x</td><td>3</td></tr>',
                '<tr><td>y</td><td>2</td></tr>', '</table>',
                '<table border="1" cellpadding="8"><caption>table33</caption>',
                '<tr><th>a</th><th>b</th><th>c</th></tr>',
                '<tr><td>x</td><td>3</td><td>2021-12-31</td></tr>',
                '<tr><td>y</td><td>2</td><td>2021-12-30</td></tr>',
                '<tr><td>~</td><td></td><td>2021-12-31</td></tr>', '</table>']
        self.assertEqual(cond, text.splitlines())
        want = {"table22": table22, "table33": _date(table33Q)}
        scan = tabtotext.tablistscanHTML(text)
        back = dict(tabtotext.tablistmap(scan))
        logg.debug("\n>> %s\n<< %s", want, back)
        self.assertEqual(want, back)
    def test_7921(self) -> None:
        tmp = self.testdir()
        tablist = {"table01": table01, "table02": table02}
        filename = path.join(tmp, "output.html")
        text = tabtotext.print_tablist(filename, tabtotext.tablistfor(tablist))
        sz = path.getsize(filename)
        self.assertGreater(sz, 100)
        self.assertGreater(400, sz)
        want = {"table01": table01N, "table02": _date(table02N)}
        scan = tabtotext.tablistfile(filename)
        back = dict(tabtotext.tablistmap(scan))
        logg.debug("\n>> %s\n<< %s", want, back)
        self.assertEqual(want, back)
    def test_7922(self) -> None:
        tmp = self.testdir()
        tablist = {"table22": table22, "table33": table33}
        filename = path.join(tmp, "output.html")
        text = tabtotext.print_tablist(filename, tabtotext.tablistfor(tablist))
        sz = path.getsize(filename)
        self.assertGreater(sz, 100)
        self.assertGreater(600, sz)
        want = {"table22": table22, "table33": _date(table33N)}
        scan = tabtotext.tablistfile(filename)
        back = dict(tabtotext.tablistmap(scan))
        logg.debug("\n>> %s\n<< %s", want, back)
        self.assertEqual(want, back)

    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_8011(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "output.xlsx")
        tabtoXLSX(filename, test011)
        sz = path.getsize(filename)
        logg.info("generated [%s] %s", sz, filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        want = test011
        back = readFromXLSX(filename)
        self.assertEqual(_none(want), back)
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_8012(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "output.xlsx")
        tabtoXLSX(filename, test012)
        sz = path.getsize(filename)
        logg.info("generated [%s] %s", sz, filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        want = test012
        back = readFromXLSX(filename)
        self.assertEqual(want, back)
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_8013(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "output.xlsx")
        tabtoXLSX(filename, test013)
        sz = path.getsize(filename)
        logg.info("generated [%s] %s", sz, filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        want = test013
        back = readFromXLSX(filename)
        self.assertEqual(want, back)
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_8014(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "output.xlsx")
        tabtoXLSX(filename, test014)
        sz = path.getsize(filename)
        logg.info("generated [%s] %s", sz, filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        want = test014
        back = readFromXLSX(filename)
        self.assertEqual(want, back)
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_8015(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "output.xlsx")
        tabtoXLSX(filename, test015)
        sz = path.getsize(filename)
        logg.info("generated [%s] %s", sz, filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        want = test015
        back = readFromXLSX(filename)
        self.assertEqual(want, back)
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_8016(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "output.xlsx")
        tabtoXLSX(filename, test016)
        sz = path.getsize(filename)
        logg.info("generated [%s] %s", sz, filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        want = test016
        back = readFromXLSX(filename)
        self.assertEqual(want, back)
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_8017(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "output.xlsx")
        tabtoXLSX(filename, test017)
        sz = path.getsize(filename)
        logg.info("generated [%s] %s", sz, filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        want = test017
        back = readFromXLSX(filename)
        self.assertEqual(want, back)
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_8018(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "output.xlsx")
        tabtoXLSX(filename, test018)
        sz = path.getsize(filename)
        logg.info("generated [%s] %s", sz, filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        want = test018Q
        back = readFromXLSX(filename)
        self.assertEqual(_date(want), _date(back))
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_8019(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "output.xlsx")
        tabtoXLSX(filename, test019)
        sz = path.getsize(filename)
        logg.info("generated [%s] %s", sz, filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        want = test019
        back = readFromXLSX(filename)
        self.assertEqual(want, back)
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_8020(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "table01.xlsx")
        tabtoXLSX(filename, table01)
        sz = path.getsize(filename)
        logg.info("generated [%s] %s", sz, filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        want = table01N
        back = readFromXLSX(filename)
        self.assertEqual(_none(want), back)
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_8021(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "table02.xlsx")
        tabtoXLSX(filename, table02)
        sz = path.getsize(filename)
        logg.info("generated [%s] %s", sz, filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        want = table02N
        back = readFromXLSX(filename)
        self.assertEqual(_none(want), back)
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_8022(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "table22.xlsx")
        tabtoXLSX(filename, table22)
        sz = path.getsize(filename)
        logg.info("generated [%s] %s", sz, filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        want = table22
        back = readFromXLSX(filename)
        self.assertEqual(_none(want), back)
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_8023(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "table33.xlsx")
        tabtoXLSX(filename, table33)
        sz = path.getsize(filename)
        logg.info("generated [%s] %s", sz, filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        want = table33Q
        back = readFromXLSX(filename)
        self.assertEqual(_none(want), _none(_date(back)))
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_8024(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "table44.xlsx")
        tabtoXLSX(filename, table44)
        sz = path.getsize(filename)
        logg.info("generated [%s] %s", sz, filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        want = table44N
        back = readFromXLSX(filename)
        self.assertEqual(_none(want), _none(back))
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_8031(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "output.xlsx")
        tabtoXLSX(filename, test011, legend=["a result"])
        sz = path.getsize(filename)
        logg.info("generated [%s] %s", sz, filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        want = test011
        back = readFromXLSX(filename)
        self.assertEqual(_none(want), back)
        # self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_8032(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "output.xlsx")
        tabtoXLSX(filename, test012, legend=["a result"])
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        want = test012
        back = readFromXLSX(filename)
        self.assertEqual(want, back)
        logg.info("data = %s", back)
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_8033(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "output.xlsx")
        tabtoXLSX(filename, test013, legend=["a result"])
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        want = test013
        back = readFromXLSX(filename)
        self.assertEqual(want, back)
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_8034(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "output.xlsx")
        tabtoXLSX(filename, test014, legend=["a result"])
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        want = test014
        back = readFromXLSX(filename)
        self.assertEqual(want, back)
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_8035(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "output.xlsx")
        tabtoXLSX(filename, test015, legend=["a result"])
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        want = test015
        back = readFromXLSX(filename)
        self.assertEqual(want, back)
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_8036(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "output.xlsx")
        tabtoXLSX(filename, test016, legend=["a result"])
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        want = test016
        back = readFromXLSX(filename)
        self.assertEqual(want, back)
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_8037(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "output.xlsx")
        tabtoXLSX(filename, test017, legend=["a result"])
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        want = test017
        back = readFromXLSX(filename)
        self.assertEqual(want, back)
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_8038(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "output.xlsx")
        tabtoXLSX(filename, test018, legend=["a result"])
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        #
        with ZipFile(filename) as zipped:
            with zipped.open("xl/worksheets/sheet1.xml") as zipdata:
                xmldata = zipdata.read()
                logg.info("xmldata = %s", xmldata)
        #
        want = test018Q
        back = readFromXLSX(filename)
        self.assertEqual(_date(want), _date(back))
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_8039(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "output.xlsx")
        tabtoXLSX(filename, test019, legend=["a result"])
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        #
        with ZipFile(filename) as zipped:
            with zipped.open("xl/worksheets/sheet1.xml") as zipdata:
                xmldata = zipdata.read()
                logg.info("xmldata = %s", xmldata)
        #
        want = test019
        back = readFromXLSX(filename)
        self.assertEqual(want, back)
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_8060(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "tabl01.xlsx")
        tabtoXLSX(filename, table01, ["b", "a"])
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        #
        with ZipFile(filename) as zipped:
            with zipped.open("xl/worksheets/sheet1.xml") as zipdata:
                xmldata = zipdata.read()
                logg.info("xmldata = %s", xmldata)
        #
        want = table01N
        back = readFromXLSX(filename)
        self.assertEqual(_none(want), back)
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_8061(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "tabl02.xlsx")
        tabtoXLSX(filename, table02, ["b", "a"])
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        #
        with ZipFile(filename) as zipped:
            with zipped.open("xl/worksheets/sheet1.xml") as zipdata:
                xmldata = zipdata.read()
                logg.info("xmldata = %s", xmldata)
        #
        want = table02N
        back = readFromXLSX(filename)
        self.assertEqual(_none(want), back)
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_8062(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "tabl22.xlsx")
        tabtoXLSX(filename, table22, ["b", "a"])
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        #
        with ZipFile(filename) as zipped:
            with zipped.open("xl/worksheets/sheet1.xml") as zipdata:
                xmldata = zipdata.read()
                logg.info("xmldata = %s", xmldata)
        #
        want = table22
        back = readFromXLSX(filename)
        self.assertEqual(_none(want), back)
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_8063(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "tabl33.xlsx")
        tabtoXLSX(filename, table33, ["b", "a"])
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        #
        with ZipFile(filename) as zipped:
            with zipped.open("xl/worksheets/sheet1.xml") as zipdata:
                xmldata = zipdata.read()
                logg.info("xmldata = %s", xmldata)
        #
        want = table33Q
        back = readFromXLSX(filename)
        self.assertEqual(_none(want), _none(_date(back)))
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_8064(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "table44.xlsx")
        tabtoXLSX(filename, table44, ["b", "a"])
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        #
        with ZipFile(filename) as zipped:
            with zipped.open("xl/worksheets/sheet1.xml") as zipdata:
                xmldata = zipdata.read()
                logg.info("xmldata = %s", xmldata)
        #
        want = table44N
        back = readFromXLSX(filename)
        self.assertEqual(_none(want), _none(back))
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_8065(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "table33.xlsx")
        tabtoXLSX(filename, table33, ["c", "a"])
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        #
        with ZipFile(filename) as zipped:
            with zipped.open("xl/worksheets/sheet1.xml") as zipdata:
                xmldata = zipdata.read()
                logg.info("xmldata = %s", xmldata)
        #
        want = table33Q
        back = readFromXLSX(filename)
        self.assertEqual(_none(want), _none(_date(back)))
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_8467(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "table22.xlsx")
        tabtoXLSX(filename, table22, ["b", "a"], ["b", "a"])
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        #
        with ZipFile(filename) as zipped:
            with zipped.open("xl/worksheets/sheet1.xml") as zipdata:
                xmldata = zipdata.read()
                logg.info("xmldata = %s", xmldata)
        #
        want = rev(table22)
        back = readFromXLSX(filename)
        self.assertEqual(_none(want), _none(_date(back)))
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_8468(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "table33.xlsx")
        tabtoXLSX(filename, table33, ["b", "a"], ["b", "a", "c"])
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        #
        with ZipFile(filename) as zipped:
            with zipped.open("xl/worksheets/sheet1.xml") as zipdata:
                xmldata = zipdata.read()
                logg.info("xmldata = %s", xmldata)
        #
        want = rev(table33Q[:2]) + table33Q[2:]
        back = readFromXLSX(filename)
        self.assertEqual(_none(want), _none(_date(back)))
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_8469(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "table33.xlsx")
        tabtoXLSX(filename, table33, ["b", "a"], ["c", "a", "b"])
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        #
        with ZipFile(filename) as zipped:
            with zipped.open("xl/worksheets/sheet1.xml") as zipdata:
                xmldata = zipdata.read()
                logg.info("xmldata = %s", xmldata)
        #
        want = rev(table33Q[:2]) + table33Q[2:]
        back = readFromXLSX(filename)
        self.assertEqual(_none(want), _none(_date(back)))
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_8470(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "table01.xlsx")
        tabtoXLSX(filename, table01, ["b", "a"], ["a"])
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        #
        with ZipFile(filename) as zipped:
            with zipped.open("xl/worksheets/sheet1.xml") as zipdata:
                xmldata = zipdata.read()
                logg.info("xmldata = %s", xmldata)
        #
        want: JSONList
        want = list(reversed(table01))
        want = [{'a': None}, {'a': 'x y'}]  # FIXME
        back = readFromXLSX(filename)
        self.assertEqual(_none(want), _none(_date(back)))
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_8471(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "table02.xlsx")
        tabtoXLSX(filename, table02, ["b", "a"], ["a"])
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        #
        with ZipFile(filename) as zipped:
            with zipped.open("xl/worksheets/sheet1.xml") as zipdata:
                xmldata = zipdata.read()
                logg.info("xmldata = %s", xmldata)
        #
        want: JSONList
        want = [{'a': None}, {'a': 'x'}]
        back = readFromXLSX(filename)
        self.assertEqual(_none(want), _none(_date(back)))
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_8472(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "table22.xlsx")
        tabtoXLSX(filename, table22, ["b", "a"], ["a"])
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        #
        with ZipFile(filename) as zipped:
            with zipped.open("xl/worksheets/sheet1.xml") as zipdata:
                xmldata = zipdata.read()
                logg.info("xmldata = %s", xmldata)
        #
        want: JSONList
        want = [{'a': 'x'}, {'a': 'y'}]
        back = readFromXLSX(filename)
        self.assertEqual(_none(want), _none(_date(back)))
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_8473(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "table33.xlsx")
        tabtoXLSX(filename, table33, ["b", "a"], ["a"])
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        #
        with ZipFile(filename) as zipped:
            with zipped.open("xl/worksheets/sheet1.xml") as zipdata:
                xmldata = zipdata.read()
                logg.info("xmldata = %s", xmldata)
        #
        want: JSONList
        want = [{'a': None}, {'a': 'x'}, {'a': 'y'}]
        back = readFromXLSX(filename)
        self.assertEqual(_none(want), _none(_date(back)))
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_8474(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "table33.xlsx")
        tabtoXLSX(filename, table33, ["c", "a"], ["a"])
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        #
        with ZipFile(filename) as zipped:
            with zipped.open("xl/worksheets/sheet1.xml") as zipdata:
                xmldata = zipdata.read()
                logg.info("xmldata = %s", xmldata)
        #
        want: JSONList
        want = [{'a': None}, {'a': 'x'}, {'a': 'y'}]
        back = readFromXLSX(filename)
        self.assertEqual(_none(want), _none(_date(back)))
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_8475(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "table02.xlsx")
        tabtoXLSX(filename, table02, ["b", "a"], ["b"])
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        #
        with ZipFile(filename) as zipped:
            with zipped.open("xl/worksheets/sheet1.xml") as zipdata:
                xmldata = zipdata.read()
                logg.info("xmldata = %s", xmldata)
        #
        want: JSONList
        want = [{'b': 0}, {'b': 2}]
        back = readFromXLSX(filename)
        self.assertEqual(_none(want), _none(_date(back)))
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_8476(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "table22.xlsx")
        tabtoXLSX(filename, table22, ["b", "a"], ["b"])
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        #
        with ZipFile(filename) as zipped:
            with zipped.open("xl/worksheets/sheet1.xml") as zipdata:
                xmldata = zipdata.read()
                logg.info("xmldata = %s", xmldata)
        #
        want: JSONList
        want = [{'b': 2}, {'b': 3}]
        back = readFromXLSX(filename)
        self.assertEqual(_none(want), _none(_date(back)))
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_8477(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "table33.xlsx")
        tabtoXLSX(filename, table33, ["b", "a"], ["b"])
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        #
        with ZipFile(filename) as zipped:
            with zipped.open("xl/worksheets/sheet1.xml") as zipdata:
                xmldata = zipdata.read()
                logg.info("xmldata = %s", xmldata)
        #
        want: JSONList
        want = [{'b': 2}, {'b': 3}, {'b': None}]
        back = readFromXLSX(filename)
        self.assertEqual(_none(want), _none(_date(back)))
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_8478(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "table33.xlsx")
        tabtoXLSX(filename, table33, ["c", "a"], ["b"])
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        #
        with ZipFile(filename) as zipped:
            with zipped.open("xl/worksheets/sheet1.xml") as zipdata:
                xmldata = zipdata.read()
                logg.info("xmldata = %s", xmldata)
        #
        want: JSONList
        want = [{'b': 2}, {'b': 3}, {'b': None}]
        back = readFromXLSX(filename)
        self.assertEqual(_none(want), _none(_date(back)))
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_8479(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "table33.xlsx")
        tabtoXLSX(filename, table33, ["c", "a"], ["c"])
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        #
        with ZipFile(filename) as zipped:
            with zipped.open("xl/worksheets/sheet1.xml") as zipdata:
                xmldata = zipdata.read()
                logg.info("xmldata = %s", xmldata)
        #
        want: JSONList
        want = [{'c': Date(2021, 12, 30)}, {'c': Date(2021, 12, 31)}, {'c': Date(2021, 12, 31)}]
        back = readFromXLSX(filename)
        self.assertEqual(_none(want), _none(_date(back)))
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_8530(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "table01.xlsx")
        tabtoXLSX(filename, table01, ["a|b"])
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        #
        with ZipFile(filename) as zipped:
            with zipped.open("xl/worksheets/sheet1.xml") as zipdata:
                xmldata = zipdata.read()
                logg.info("xmldata = %s", xmldata)
        #
        want = table01N
        back = readFromXLSX(filename)
        self.assertEqual(_none(want), _none(_date(back)))
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_8535(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "table01.xlsx")
        tabtoXLSX(filename, table01, ["b|a"])
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        #
        with ZipFile(filename) as zipped:
            with zipped.open("xl/worksheets/sheet1.xml") as zipdata:
                xmldata = zipdata.read()
                logg.info("xmldata = %s", xmldata)
        #
        want = table01N
        back = readFromXLSX(filename)
        self.assertEqual(_none(want), _none(_date(back)))
        self.rm_testdir()
    def test_8821(self) -> None:
        tmp = self.testdir()
        tablist = {"table22": table22, "table33": table33}
        filename = path.join(tmp, "output.xlsx")
        text = tabtotext.print_tablist(filename, tabtotext.tablistfor(tablist))
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        want = {"table22": table22, "table33": _date(_none(table33Q))}
        scan = tabtotext.tablistfile(filename)
        back = dict(tabtotext.tablistmap(scan))
        if FIXME and "table33" in back:
            back["table33"] = _date(back["table33"])  # FIXME: openpyxl returns .999999 sec
        logg.debug("\n>> %s\n<< %s", want, back)
        self.assertEqual(want, back)

# sh

    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_9018(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "table44.xlsx")
        tabtoXLSX(filename, table44)
        sz = path.getsize(filename)
        logg.info("generated [%s] %s", sz, filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        text = sh(F"{TABTO} -^ {filename} a b")
        logg.info("text = %s", text)
        cond = ['| a     | b', '| ----- | -----', '|       |',
                '| x     | 3', '| y     | 1', '| y     | 2']
        self.assertEqual(cond, text.splitlines())
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_9019(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "table44.xlsx")
        tabtoXLSX(filename, table44)
        sz = path.getsize(filename)
        logg.info("generated [%s] %s", sz, filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        text = sh(F"{TABTO} -^ {filename} a b:.2f")
        logg.info("text = %s", text)
        cond = ['| a     |     b', '| ----- | ----:', '|       |',
                '| x     |  3.00', '| y     |  1.00', '| y     |  2.00']
        self.assertEqual(cond, text.splitlines())
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_9020(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "table01.xlsx")
        tabtoXLSX(filename, table01)
        sz = path.getsize(filename)
        logg.info("generated [%s] %s", sz, filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        text = sh(F"{TABTO} -^ {filename} @csv")
        cond = ['a;b', 'x y;~', '~;1']
        cond = ['a;b', 'x y;', ';1']
        want = table01N
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(_none(want), back)
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_9021(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "table02.xlsx")
        tabtoXLSX(filename, table02)
        sz = path.getsize(filename)
        logg.info("generated [%s] %s", sz, filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        text = sh(F"{TABTO} -^ {filename} @csv")
        want = table02N
        cond = ['a;b', 'x;0', '~;2']
        cond = ['a;b', 'x;0', ';2']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(_none(want), back)
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_9022(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "table22.xlsx")
        tabtoXLSX(filename, table22)
        sz = path.getsize(filename)
        logg.info("generated [%s] %s", sz, filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        text = sh(F"{TABTO} -^ {filename} @csv")
        want = table22
        cond = ['a;b', 'x;3', 'y;2']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(_none(want), back)
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_9023(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "table33.xlsx")
        tabtoXLSX(filename, table33)
        sz = path.getsize(filename)
        logg.info("generated [%s] %s", sz, filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        text = sh(F"{TABTO} -^ {filename} @csv")
        want = table33Q
        cond = ['a;b;c', 'x;3;2021-12-31', 'y;2;2021-12-30', '~;~;2021-12-31']
        cond = ['a;b;c', 'x;3;2021-12-31', 'y;2;2021-12-30', ';;2021-12-31']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(_none(want), _none(_date(back)))
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_9024(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "table44.xlsx")
        tabtoXLSX(filename, table44)
        sz = path.getsize(filename)
        logg.info("generated [%s] %s", sz, filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        text = sh(F"{TABTO} -^ {filename} @csv")
        logg.info("text = %s", text)
        want = table44N
        cond = ['a;b;c;d', 'x;3;(yes);0.40', 'y;2;(no);0.30', ';;(yes);0.20', 'y;1;;0.10']
        self.assertEqual(cond, text.splitlines())
        back = loadCSV(text)
        self.assertEqual(_none(want), _none(back))
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_9028(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "table44.xlsx")
        tabtoXLSX(filename, table44)
        sz = path.getsize(filename)
        logg.info("generated [%s] %s", sz, filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        text = sh(F"{TABTO} -^ {filename} @csv a b")
        logg.info("text = %s", text)
        cond = ['a;b;c;d', 'x;3;(yes);0.40', 'y;2;(no);0.30', ';;(yes);0.20', 'y;1;;0.10']
        cond = ['a;b', ';', 'x;3', 'y;1', 'y;2']
        self.assertEqual(cond, text.splitlines())
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_9029(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "table44.xlsx")
        tabtoXLSX(filename, table44)
        sz = path.getsize(filename)
        logg.info("generated [%s] %s", sz, filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        text = sh(F"{TABTO} -^ {filename} @csv a b:.2f")
        logg.info("text = %s", text)
        cond = ['a;b;c;d', 'x;3;(yes);0.40', 'y;2;(no);0.30', ';;(yes);0.20', 'y;1;;0.10']
        cond = ['a;b', ';', 'x;3', 'y;1', 'y;2']
        cond = ['a;b', ';', 'x;3.00', 'y;1.00', 'y;2.00']
        self.assertEqual(cond, text.splitlines())
        self.rm_testdir()
    @unittest.skipIf(skipXLSX, "no openpyxl")
    def test_9039(self) -> None:
        tmp = self.testdir()
        filename = path.join(tmp, "table44.xlsx")
        tabtoXLSX(filename, table44)
        sz = path.getsize(filename)
        logg.info("generated [%s] %s", sz, filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        text = sh(F"{TABTO} -^ {filename} @csv a 'b:{{:.1f}}in@wide'")
        logg.info("text = %s", text)
        cond = ['a;b;c;d', 'x;3;(yes);0.40', 'y;2;(no);0.30', ';;(yes);0.20', 'y;1;;0.10']
        cond = ['a;b', ';', 'x;3', 'y;1', 'y;2']
        cond = ['a;b', ';', 'x;3.00', 'y;1.00', 'y;2.00']
        cond = ['a;wide', ';', 'x;3.0in', 'y;1.0in', 'y;2.0in']
        self.assertEqual(cond, text.splitlines())
        self.rm_testdir()
    def test_9810(self) -> None:
        tmp = self.testdir()
        tablist = {"table22": table22, "table33": table33}
        filename = path.join(tmp, "input.xlsx")
        output = path.join(tmp, "output.xlsx")
        text = print_tablist(filename, tablistfor(tablist))
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        text = sh(F"{TABTO} -^ {filename} -o {output}")
        have = sh(F"{TABTO} -^ {output} --onlypages")
        logg.info("pages => %s", have.splitlines())
        want = ['table22', 'table33']
        self.assertEqual(want, have.splitlines())
    def test_9811(self) -> None:
        tmp = self.testdir()
        tablist = {"table22": table22, "table33": table33}
        filename = path.join(tmp, "input.xlsx")
        output = path.join(tmp, "output.xlsx")
        text = print_tablist(filename, tablistfor(tablist))
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        text = sh(F"{TABTO} -^ {filename} -o {output}")
        with ZipFile(output) as zipped:
            with zipped.open("xl/worksheets/sheet1.xml") as zipdata:
                xmldata = zipdata.read()
        logg.info("xmldata=>\n%s", xmldata)
        self.assertIn(b"</worksheet>", xmldata)
        want = {"table22": table22, "table33": _date(_none(table33Q))}
        scan = tablistfile(output)
        back = dict(tablistmap(scan))
        if FIXME and "table33" in back:
            back["table33"] = _date(back["table33"])  # FIXME: openpyxl returns .999999 sec
        logg.debug("\n>> %s\n<< %s", want, back)
        self.assertEqual(want, back)
    def test_9812(self) -> None:
        tmp = self.testdir()
        tablist = {"table22": table22, "table33": table33}
        filename = path.join(tmp, "input.xlsx")
        output = path.join(tmp, "output.xlsx")
        text = print_tablist(filename, tablistfor(tablist))
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        text = sh(F"{TABTO} -^ {filename} -o {output} -: table22")
        with ZipFile(output) as zipped:
            with zipped.open("xl/worksheets/sheet1.xml") as zipdata:
                xmldata = zipdata.read()
        logg.info("xmldata=>\n%s", xmldata)
        self.assertIn(b"</worksheet>", xmldata)
        want = {"table22": table22, }
        scan = tablistfile(output)
        back = dict(tablistmap(scan))
        logg.debug("\n>> %s\n<< %s", want, back)
        self.assertEqual(want, back)
    def test_9813(self) -> None:
        tmp = self.testdir()
        tablist = {"table22": table22, "table33": table33}
        filename = path.join(tmp, "input.xlsx")
        output = path.join(tmp, "output.xlsx")
        text = print_tablist(filename, tablistfor(tablist))
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        text = sh(F"{TABTO} -^ {filename} -o {output} -: table33")
        with ZipFile(output) as zipped:
            with zipped.open("xl/worksheets/sheet1.xml") as zipdata:
                xmldata = zipdata.read()
        logg.info("xmldata=>\n%s", xmldata)
        self.assertIn(b"</worksheet>", xmldata)
        want = {"table33": _none(table33Q), }
        scan = tablistfile(output)
        back = dict(tablistmap(scan))
        if FIXME and "table33" in back:
            back["table33"] = _date(back["table33"])  # FIXME: openpyxl returns .999999 sec
        logg.debug("\n>> %s\n<< %s", want, back)
        self.assertEqual(want, back)
    def test_9814(self) -> None:
        tmp = self.testdir()
        tablist = {"table22": table22, "table33": table33}
        filename = path.join(tmp, "input.xlsx")
        output = path.join(tmp, "output.xlsx")
        text = print_tablist(filename, tablistfor(tablist))
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        text = sh(F"{TABTO} -^ {filename} -o {output} -2")
        with ZipFile(output) as zipped:
            with zipped.open("xl/worksheets/sheet1.xml") as zipdata:
                xmldata = zipdata.read()
        logg.info("xmldata=>\n%s", xmldata)
        self.assertIn(b"</worksheet>", xmldata)
        want = {"data": _none(table33Q), }
        scan = tablistfile(output)
        back = dict(tablistmap(scan))
        if FIXME and "data" in back:
            back["data"] = _date(back["data"])  # FIXME: openpyxl returns .999999 sec
        logg.debug("\n>> %s\n<< %s", want, back)
        self.assertEqual(want, back)
    def test_9815(self) -> None:
        tmp = self.testdir()
        tablist = {"table22": table22, "table33": table33}
        filename = path.join(tmp, "input.xlsx")
        output = path.join(tmp, "output.xlsx")
        text = print_tablist(filename, tablistfor(tablist))
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        text = sh(F"{TABTO} -^ {filename} -o {output} -2 -: newdata")
        with ZipFile(output) as zipped:
            with zipped.open("xl/worksheets/sheet1.xml") as zipdata:
                xmldata = zipdata.read()
        logg.info("xmldata=>\n%s", xmldata)
        self.assertIn(b"</worksheet>", xmldata)
        want = {"newdata": _none(table33Q), }
        scan = tablistfile(output)
        back = dict(tablistmap(scan))
        if FIXME and "newdata" in back:
            back["newdata"] = _date(back["newdata"])  # FIXME: openpyxl returns .999999 sec
        logg.debug("\n>> %s\n<< %s", want, back)
        self.assertEqual(want, back)
    def test_9816(self) -> None:
        tmp = self.testdir()
        tablist = {"table22": table22, "table33": table33}
        filename = path.join(tmp, "input.xlsx")
        output = path.join(tmp, "output.xlsx")
        text = print_tablist(filename, tablistfor(tablist))
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        text = sh(F"{TABTO} -^ {filename} -o {output} -2 -:newdata")
        with ZipFile(output) as zipped:
            with zipped.open("xl/worksheets/sheet1.xml") as zipdata:
                xmldata = zipdata.read()
        logg.info("xmldata=>\n%s", xmldata)
        self.assertIn(b"</worksheet>", xmldata)
        want = {"newdata": _none(table33Q), }
        scan = tablistfile(output)
        back = dict(tablistmap(scan))
        if FIXME and "newdata" in back:
            back["newdata"] = _date(back["newdata"])  # FIXME: openpyxl returns .999999 sec
        logg.debug("\n>> %s\n<< %s", want, back)
        self.assertEqual(want, back)
    def test_9821(self) -> None:
        tmp = self.testdir()
        tablist = {"table22": table22, "table33": table33}
        filename = path.join(tmp, "input.xlsx")
        text = print_tablist(filename, tablistfor(tablist))
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        text = sh(F"{TABTO} -^ {filename}")
        logg.info("=>\n%s", text)
        want = {"table22": table22, "table33": _date(_none(table33Q))}
        scan = tablistscanGFM(text)
        back = dict(tablistmap(scan))
        logg.debug("\n>> %s\n<< %s", want, back)
        self.assertEqual(want, back)
    def test_9822(self) -> None:
        tmp = self.testdir()
        tablist = {"table22": table22, "table33": table33}
        filename = path.join(tmp, "input.xlsx")
        text = print_tablist(filename, tablistfor(tablist))
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        text = sh(F"{TABTO} -^ {filename} -: table22")
        logg.info("=>\n%s", text)
        want = {"table22": table22, }
        scan = tablistscanGFM(text)
        back = dict(tablistmap(scan))
        logg.debug("\n>> %s\n<< %s", want, back)
        self.assertEqual(want, back)
    def test_9823(self) -> None:
        tmp = self.testdir()
        tablist = {"table22": table22, "table33": table33}
        filename = path.join(tmp, "input.xlsx")
        text = print_tablist(filename, tablistfor(tablist))
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        text = sh(F"{TABTO} -^ {filename} -: table33")
        logg.info("=>\n%s", text)
        want = {"table33": _none(table33Q), }
        scan = tablistscanGFM(text)
        back = dict(tablistmap(scan))
        logg.debug("\n>> %s\n<< %s", want, back)
        self.assertEqual(want, back)
    def test_9824(self) -> None:
        tmp = self.testdir()
        tablist = {"table22": table22, "table33": table33}
        filename = path.join(tmp, "input.xlsx")
        text = print_tablist(filename, tablistfor(tablist))
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        text = sh(F"{TABTO} -^ {filename} -2")
        logg.info("=>\n%s", text)
        want = {"-1": _none(table33Q), }
        scan = tablistscanGFM(text)
        back = dict(tablistmap(scan))
        logg.debug("\n>> %s\n<< %s", want, back)
        self.assertEqual(want, back)
    def test_9825(self) -> None:
        tmp = self.testdir()
        tablist1 = {"table22": table22, "table33": table33}
        filename1 = path.join(tmp, "input1.xlsx")
        tablist2 = {"table01": table01, "table02": table02}
        filename2 = path.join(tmp, "input2.xlsx")
        inp1 = print_tablist(filename1, tablistfor(tablist1))
        inp2 = print_tablist(filename2, tablistfor(tablist2))
        text = sh(F"{TABTO} -^ -f {filename1} -f {filename2} -2")
        logg.info("=>\n%s", text)
        want = {"-1": _date(_none(table33N)), }
        scan = tablistscanGFM(text)
        back = dict(tablistmap(scan))
        logg.debug("\n>> %s\n<< %s", want, back)
        self.assertEqual(want, back)
        text = sh(F"{TABTO} -^ -f {filename1} -f {filename2} -3")
        logg.info("=>\n%s", text)
        want = {"-1": _date(_none(table01N)), }
        scan = tablistscanGFM(text)
        back = dict(tablistmap(scan))
        logg.debug("\n>> %s\n<< %s", want, back)
        self.assertEqual(want, back)
    def test_9830(self) -> None:
        tmp = self.testdir()
        tablist = {"table22": table22, "table33": table33}
        filename = path.join(tmp, "input.xlsx")
        output = path.join(tmp, "output.md")
        text = print_tablist(filename, tablistfor(tablist))
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        text = sh(F"{TABTO} -^ {filename} -o {output}")
        have = sh(F"{TABTO} -^ {output} --onlypages")
        logg.info("pages => %s", have.splitlines())
        want = ['table22', 'table33']
        self.assertEqual(want, have.splitlines())
    def test_9831(self) -> None:
        tmp = self.testdir()
        tablist = {"table22": table22, "table33": table33}
        filename = path.join(tmp, "input.xlsx")
        output = path.join(tmp, "output.md")
        text = print_tablist(filename, tablistfor(tablist))
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        text = sh(F"{TABTO} -^ {filename} -o {output}")
        text = open(output).read()
        logg.info("=>\n%s", text)
        test = tablistscanGFM(text)
        want = {"table22": table22, "table33": _date(_none(table33Q))}
        scan = tablistfile(output)
        back = dict(tablistmap(scan))
        logg.debug("\n>> %s\n<< %s", want, back)
        self.assertEqual(want, back)
        self.assertEqual(test, scan)
    def test_9832(self) -> None:
        tmp = self.testdir()
        tablist = {"table22": table22, "table33": table33}
        filename = path.join(tmp, "input.xlsx")
        output = path.join(tmp, "output.md")
        text = print_tablist(filename, tablistfor(tablist))
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        text = sh(F"{TABTO} -^ {filename} -o {output} -: table22")
        text = open(output).read()
        logg.info("=>\n%s", text)
        test = tablistscanGFM(text)
        want = {"table22": table22, }
        scan = tablistfile(output)
        back = dict(tablistmap(scan))
        logg.debug("\n>> %s\n<< %s", want, back)
        self.assertEqual(want, back)
        self.assertEqual(test, scan)
    def test_9833(self) -> None:
        tmp = self.testdir()
        tablist = {"table22": table22, "table33": table33}
        filename = path.join(tmp, "input.xlsx")
        output = path.join(tmp, "output.md")
        text = print_tablist(filename, tablistfor(tablist))
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        text = sh(F"{TABTO} -^ {filename} -o {output} -: table33")
        text = open(output).read()
        logg.info("=>\n%s", text)
        test = tablistscanGFM(text)
        want = {"table33": _none(table33Q), }
        scan = tablistfile(output)
        back = dict(tablistmap(scan))
        logg.debug("\n>> %s\n<< %s", want, back)
        self.assertEqual(want, back)
        self.assertEqual(test, scan)
    def test_9834(self) -> None:
        tmp = self.testdir()
        tablist = {"table22": table22, "table33": table33}
        filename = path.join(tmp, "input.xlsx")
        output = path.join(tmp, "output.md")
        text = print_tablist(filename, tablistfor(tablist))
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        text = sh(F"{TABTO} -^ {filename} -o {output} -2")
        text = open(output).read()
        logg.info("=>\n%s", text)
        test = tablistscanGFM(text)
        want = {"-1": _none(table33Q), }
        scan = tablistfile(output)
        back = dict(tablistmap(scan))
        logg.debug("\n>> %s\n<< %s", want, back)
        self.assertEqual(want, back)
        self.assertEqual(test, scan)
    def test_9835(self) -> None:
        tmp = self.testdir()
        tablist = {"table22": table22, "table33": table33}
        filename = path.join(tmp, "input.xlsx")
        output = path.join(tmp, "output.md")
        text = print_tablist(filename, tablistfor(tablist))
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        text = sh(F"{TABTO} -^ {filename} -o {output} -2 -: newdata")
        text = open(output).read()
        logg.info("=>\n%s", text)
        test = tablistscanGFM(text)
        want = {"newdata": _none(table33Q), }
        scan = tablistfile(output)
        back = dict(tablistmap(scan))
        logg.debug("\n>> %s\n<< %s", want, back)
        self.assertEqual(want, back)
        self.assertEqual(test, scan)
    def test_9836(self) -> None:
        tmp = self.testdir()
        tablist = {"table22": table22, "table33": table33}
        filename = path.join(tmp, "input.xlsx")
        output = path.join(tmp, "output.md")
        text = print_tablist(filename, tablistfor(tablist))
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        text = sh(F"{TABTO} -^ {filename} -o {output} -2 :newdata")
        text = open(output).read()
        logg.info("=>\n%s", text)
        test = tablistscanGFM(text)
        want = {"newdata": _none(table33Q), }
        scan = tablistfile(output)
        back = dict(tablistmap(scan))
        logg.debug("\n>> %s\n<< %s", want, back)
        self.assertEqual(want, back)
        self.assertEqual(test, scan)
    def test_9851(self) -> None:
        tmp = self.testdir()
        tablist = {"table22": table22, "table33": table33}
        filename = path.join(tmp, "input.xlsx")
        text = print_tablist(filename, tablistfor(tablist))
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        text = sh(F"{TABTO} -^ {filename}  @json")
        logg.info("=>\n%s", text)
        want = {"table22": table22, "table33": _date(_none(table33Q))}
        scan = tablistscanJSON(text)
        back = dict(tablistmap(scan))
        logg.debug("\n>> %s\n<< %s", want, back)
        self.assertEqual(want, back)
    def test_9852(self) -> None:
        tmp = self.testdir()
        tablist = {"table22": table22, "table33": table33}
        filename = path.join(tmp, "input.xlsx")
        text = print_tablist(filename, tablistfor(tablist))
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        text = sh(F"{TABTO} -^ {filename} -: table22  @json")
        logg.info("=>\n%s", text)
        want = {"table22": table22, }
        scan = tablistscanJSON(text)
        back = dict(tablistmap(scan))
        logg.debug("\n>> %s\n<< %s", want, back)
        self.assertEqual(want, back)
    def test_9853(self) -> None:
        tmp = self.testdir()
        tablist = {"table22": table22, "table33": table33}
        filename = path.join(tmp, "input.xlsx")
        text = print_tablist(filename, tablistfor(tablist))
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        text = sh(F"{TABTO} -^ {filename} -: table33  @json")
        logg.info("=>\n%s", text)
        want = {"table33": _none(table33Q), }
        scan = tablistscanJSON(text)
        back = dict(tablistmap(scan))
        logg.debug("\n>> %s\n<< %s", want, back)
        self.assertEqual(want, back)
    def test_9854(self) -> None:
        tmp = self.testdir()
        tablist = {"table22": table22, "table33": table33}
        filename = path.join(tmp, "input.xlsx")
        text = print_tablist(filename, tablistfor(tablist))
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        text = sh(F"{TABTO} -^ {filename} -2 @json")
        logg.info("=>\n%s", text)
        want = {"data": _none(table33Q), }
        scan = tablistscanJSON(text)
        back = dict(tablistmap(scan))
        logg.debug("\n>> %s\n<< %s", want, back)
        self.assertEqual(want, back)
    def test_9855(self) -> None:
        tmp = self.testdir()
        tablist1 = {"table22": table22, "table33": table33}
        filename1 = path.join(tmp, "input1.xlsx")
        tablist2 = {"table01": table01, "table02": table02}
        filename2 = path.join(tmp, "input2.xlsx")
        inp1 = print_tablist(filename1, tablistfor(tablist1))
        inp2 = print_tablist(filename2, tablistfor(tablist2))
        text = sh(F"{TABTO} -^ -f {filename1} -f {filename2} -2 @json")
        logg.info("=>\n%s", text)
        want = {"data": _date(_none(table33N)), }
        scan = tablistscanJSON(text)
        back = dict(tablistmap(scan))
        logg.debug("\n>> %s\n<< %s", want, back)
        self.assertEqual(want, back)
        text = sh(F"{TABTO} -^ -f {filename1} -f {filename2} -3 @json")
        logg.info("=>\n%s", text)
        want = {"data": _date(_none(table01N)), }
        scan = tablistscanJSON(text)
        back = dict(tablistmap(scan))
        logg.debug("\n>> %s\n<< %s", want, back)
        self.assertEqual(want, back)
    def test_9860(self) -> None:
        tmp = self.testdir()
        tablist = {"table22": table22, "table33": table33}
        filename = path.join(tmp, "input.xlsx")
        output = path.join(tmp, "output.json")
        text = print_tablist(filename, tablistfor(tablist))
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        text = sh(F"{TABTO} -^ {filename} -o {output}")
        have = sh(F"{TABTO} -^ {output} --onlypages")
        logg.info("pages => %s", have.splitlines())
        want = ['table22', 'table33']
        self.assertEqual(want, have.splitlines())
    def test_9861(self) -> None:
        tmp = self.testdir()
        tablist = {"table22": table22, "table33": table33}
        filename = path.join(tmp, "input.xlsx")
        output = path.join(tmp, "output.json")
        text = print_tablist(filename, tablistfor(tablist))
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        text = sh(F"{TABTO} -^ {filename} -o {output}")
        text = open(output).read()
        logg.info("=>\n%s", text)
        test = tablistscanJSON(text)
        want = {"table22": table22, "table33": _date(_none(table33Q))}
        scan = tablistfile(output)
        back = dict(tablistmap(scan))
        logg.debug("\n>> %s\n<< %s", want, back)
        self.assertEqual(want, back)
        self.assertEqual(test, scan)
    def test_9862(self) -> None:
        tmp = self.testdir()
        tablist = {"table22": table22, "table33": table33}
        filename = path.join(tmp, "input.xlsx")
        output = path.join(tmp, "output.json")
        text = print_tablist(filename, tablistfor(tablist))
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        text = sh(F"{TABTO} -^ {filename}  -o {output} -: table22")
        text = open(output).read()
        logg.info("=>\n%s", text)
        test = tablistscanJSON(text)
        want = {"table22": table22, }
        scan = tablistfile(output)
        back = dict(tablistmap(scan))
        logg.debug("\n>> %s\n<< %s", want, back)
        self.assertEqual(want, back)
        self.assertEqual(test, scan)
    def test_9863(self) -> None:
        tmp = self.testdir()
        tablist = {"table22": table22, "table33": table33}
        filename = path.join(tmp, "input.xlsx")
        output = path.join(tmp, "output.json")
        text = print_tablist(filename, tablistfor(tablist))
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        text = sh(F"{TABTO} -^ {filename}  -o {output} -: table33")
        text = open(output).read()
        logg.info("=>\n%s", text)
        test = tablistscanJSON(text)
        want = {"table33": _none(table33Q), }
        scan = tablistfile(output)
        back = dict(tablistmap(scan))
        logg.debug("\n>> %s\n<< %s", want, back)
        self.assertEqual(want, back)
        self.assertEqual(test, scan)
    def test_9864(self) -> None:
        tmp = self.testdir()
        tablist = {"table22": table22, "table33": table33}
        filename = path.join(tmp, "input.xlsx")
        output = path.join(tmp, "output.json")
        text = print_tablist(filename, tablistfor(tablist))
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        text = sh(F"{TABTO} -^ {filename} -o {output} -2")
        text = open(output).read()
        logg.info("=>\n%s", text)
        test = tablistscanJSON(text)
        want = {"data": _none(table33Q), }
        scan = tablistfile(output)
        back = dict(tablistmap(scan))
        logg.debug("\n>> %s\n<< %s", want, back)
        self.assertEqual(want, back)
        self.assertEqual(test, scan)
    def test_9865(self) -> None:
        tmp = self.testdir()
        tablist = {"table22": table22, "table33": table33}
        filename = path.join(tmp, "input.xlsx")
        output = path.join(tmp, "output.json")
        text = print_tablist(filename, tablistfor(tablist))
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        text = sh(F"{TABTO} -^ {filename} -o {output} -2 -: newdata")
        text = open(output).read()
        logg.info("=>\n%s", text)
        test = tablistscanJSON(text)
        want = {"newdata": _none(table33Q), }
        scan = tablistfile(output)
        back = dict(tablistmap(scan))
        logg.debug("\n>> %s\n<< %s", want, back)
        self.assertEqual(want, back)
        self.assertEqual(test, scan)
    def test_9866(self) -> None:
        tmp = self.testdir()
        tablist = {"table22": table22, "table33": table33}
        filename = path.join(tmp, "input.xlsx")
        output = path.join(tmp, "output.json")
        text = print_tablist(filename, tablistfor(tablist))
        sz = path.getsize(filename)
        self.assertGreater(sz, 3000)
        self.assertGreater(6000, sz)
        text = sh(F"{TABTO} -^ {filename} -o {output} -2 :newdata")
        text = open(output).read()
        logg.info("=>\n%s", text)
        test = tablistscanJSON(text)
        want = {"newdata": _none(table33Q), }
        scan = tablistfile(output)
        back = dict(tablistmap(scan))
        logg.debug("\n>> %s\n<< %s", want, back)
        self.assertEqual(want, back)
        self.assertEqual(test, scan)
    def test_9888(self) -> None:
        tmp = self.testdir()
        tabs: List[TabSheet] = []
        for sheet in range(5):
            rows: JSONList = []
            for row in range(BIGFILE//10):
                num = sheet * BIGFILE + row
                vals: JSONDict = {"a":  num, "b": BIGFILE+num}
                rows.append(vals)
            title = "data%i" % sheet
            tabs.append(TabSheet(rows, [], title))
        filename = path.join(tmp, "bigfile.xlsx")
        output = path.join(tmp, "bigfile.json")
        starting = Time.now()
        text = print_tablist(filename, tabs)
        generated = Time.now()
        text = sh(F"{TABTO} -^ {filename} -o {output}")
        converted = Time.now()
        logg.info("| %i numbers openpyxl write xlsx time | %s", BIGFILE, generated - starting)
        logg.info("| %i numbers read xlsx and write json | %s", BIGFILE, converted - generated)
        text = open(output).read()
        # logg.debug("=>\n%s", text)
        test = tablistscanJSON(text)
        scan = tablistfile(output)
        back = dict(tablistmap(scan))
        # logg.debug("\n>> %s\n<< %s", want, back)
        self.assertEqual(test, scan)

if __name__ == "__main__":
    # unittest.main()
    from optparse import OptionParser
    cmdline = OptionParser("%s test...")
    cmdline.add_option("-v", "--verbose", action="count", default=0, help="more verbose logging")
    cmdline.add_option("-^", "--quiet", action="count", default=0, help="less verbose logging")
    cmdline.add_option("-k", "--keep", action="count", default=0, help="keep testdir")
    cmdline.add_option("--bigfile", metavar=str(BIGFILE), default=BIGFILE)
    cmdline.add_option("--failfast", action="store_true", default=False,
                       help="Stop the test run on the first error or failure. [%default]")
    cmdline.add_option("--xmlresults", metavar="FILE", default=None,
                       help="capture results as a junit xml file [%default]")
    opt, args = cmdline.parse_args()
    logging.basicConfig(level=max(0, logging.WARNING - 10 * opt.verbose + 10 * opt.quiet))
    BIGFILE = int(opt.bigfile)
    KEEP = opt.keep
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
