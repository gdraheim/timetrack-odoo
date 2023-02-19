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
    def test_111(self) -> None:
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
    def test_112(self) -> None:
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
    def test_113(self) -> None:
        spec = """
        >> dev1 [Development]
        >> dev1 "project1"
        >> dev2 [Development]
        >> dev2 "project2"
        .. dev1
        .. dev2
        """.splitlines()
        data = list(topics.mapping(spec))
        logg.debug("data = %s", data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["proj"], "Development")
        self.assertEqual(data[0]["task"], "project1")
        self.assertEqual(data[0]["pref"], "dev1")
        self.assertEqual(data[1]["proj"], "Development")
        self.assertEqual(data[1]["task"], "project2")
        self.assertEqual(data[1]["pref"], "dev2")
    def test_114(self) -> None:
        spec = """
        >> dev1 [Development]
        >> dev1 "project1"
        >> dev2 [Development]
        >> dev2 "project2"
        .. dev1
        .. dev2-frontend
        .. dev2-backend
        """.splitlines()
        data = list(topics.mapping(spec))
        logg.debug("data = %s", data)
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]["proj"], "Development")
        self.assertEqual(data[0]["task"], "project1")
        self.assertEqual(data[0]["pref"], "dev1")
        self.assertEqual(data[1]["proj"], "Development")
        self.assertEqual(data[1]["task"], "project2")
        self.assertEqual(data[1]["pref"], "dev2-frontend")
        self.assertEqual(data[2]["proj"], "Development")
        self.assertEqual(data[2]["task"], "project2")
        self.assertEqual(data[2]["pref"], "dev2-backend")
    def test_144(self) -> None:
        spec = """
        >> dev1 [Development]
        >> dev1 "project1"
        >> dev2 [Development]
        >> dev2 "project2"
        .. dev1
        .. dev2-frontend
        .. dev2-backend
        >> dev2-frontend [Frontends]
        >> dev2-frontend "project2"
        .. dev2-frontend
        .. dev2-backend
        """.splitlines()
        data = list(topics.mapping(spec))
        logg.debug("data = %s", data)
        self.assertEqual(len(data), 5)
        self.assertEqual(data[0]["proj"], "Development")
        self.assertEqual(data[0]["task"], "project1")
        self.assertEqual(data[0]["pref"], "dev1")
        self.assertEqual(data[1]["proj"], "Development")
        self.assertEqual(data[1]["task"], "project2")
        self.assertEqual(data[1]["pref"], "dev2-frontend")
        self.assertEqual(data[2]["proj"], "Development")
        self.assertEqual(data[2]["task"], "project2")
        self.assertEqual(data[2]["pref"], "dev2-backend")
        self.assertEqual(data[3]["proj"], "Frontends")
        self.assertEqual(data[3]["task"], "project2")
        self.assertEqual(data[3]["pref"], "dev2-frontend")
        self.assertEqual(data[4]["proj"], "Development")
        self.assertEqual(data[4]["task"], "project2")
        self.assertEqual(data[4]["pref"], "dev2-backend")
    def test_200(self) -> None:
        spec = """
        >> dev [Development]
        >> dev "projects"
        .. dev
        """.splitlines()
        data = list(topics.mapping(spec))
        logg.debug("data = %s", data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["proj"], "Development")
        self.assertEqual(data[0]["task"], "projects")
        self.assertEqual(data[0]["pref"], "dev")
    def test_201(self) -> None:
        spec = """
        >> dev [Development]
        >> dev "projects"
        .. dev1
        """.splitlines()
        data = list(topics.mapping(spec))
        logg.debug("data = %s", data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["proj"], "Development")
        self.assertEqual(data[0]["task"], "projects")
        self.assertEqual(data[0]["pref"], "dev1")
    def test_202(self) -> None:
        spec = """
        >> dev [Development]
        >> dev "projects"
        .. dev1
        .. dev2
        """.splitlines()
        data = list(topics.mapping(spec))
        logg.debug("data = %s", data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["proj"], "Development")
        self.assertEqual(data[0]["task"], "projects")
        self.assertEqual(data[0]["pref"], "dev1")
        self.assertEqual(data[1]["proj"], "Development")
        self.assertEqual(data[1]["task"], "projects")
        self.assertEqual(data[1]["pref"], "dev2")
    def test_203(self) -> None:
        spec = """
        >> dev [Development]
        >> dev "projects"
        >> dev1 [Development]
        >> dev1 "project1"
        >> dev2 [Development]
        >> dev2 "project2"
        .. dev1
        .. dev2
        """.splitlines()
        data = list(topics.mapping(spec))
        logg.debug("data = %s", data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["proj"], "Development")
        self.assertEqual(data[0]["task"], "project1")
        self.assertEqual(data[0]["pref"], "dev1")
        self.assertEqual(data[1]["proj"], "Development")
        self.assertEqual(data[1]["task"], "project2")
        self.assertEqual(data[1]["pref"], "dev2")
    def test_211(self) -> None:
        spec = """
        >> dev [Development]
        >> dev "projects"
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
    def test_212(self) -> None:
        spec = """
        >> dev [Development]
        >> dev "projects"
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
        self.assertEqual(data[1]["proj"], "Development")
        self.assertEqual(data[1]["task"], "projects")
        self.assertEqual(data[1]["pref"], "dev2")
    def test_213(self) -> None:
        spec = """
        >> dev [Development]
        >> dev "projects"
        >> dev1 [Development]
        >> dev1 "project1"
        >> dev2 [Development]
        >> dev2 "project2"
        .. dev1
        .. dev2
        """.splitlines()
        data = list(topics.mapping(spec))
        logg.debug("data = %s", data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["proj"], "Development")
        self.assertEqual(data[0]["task"], "project1")
        self.assertEqual(data[0]["pref"], "dev1")
        self.assertEqual(data[1]["proj"], "Development")
        self.assertEqual(data[1]["task"], "project2")
        self.assertEqual(data[1]["pref"], "dev2")
    def test_214(self) -> None:
        spec = """
        >> dev [Development]
        >> dev "projects"
        >> dev1 [Development]
        >> dev1 "project1"
        >> dev2 [Development]
        >> dev2 "project2"
        .. dev1
        .. dev2-frontend
        .. dev2-backend
        """.splitlines()
        data = list(topics.mapping(spec))
        logg.debug("data = %s", data)
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]["proj"], "Development")
        self.assertEqual(data[0]["task"], "project1")
        self.assertEqual(data[0]["pref"], "dev1")
        self.assertEqual(data[1]["proj"], "Development")
        self.assertEqual(data[1]["task"], "project2")
        self.assertEqual(data[1]["pref"], "dev2-frontend")
        self.assertEqual(data[2]["proj"], "Development")
        self.assertEqual(data[2]["task"], "project2")
        self.assertEqual(data[2]["pref"], "dev2-backend")
    def test_219(self) -> None:
        spec = """
        >> dev [Development]
        >> dev "projects"
        >> dev1 [Development]
        >> dev1 "project1"
        >> dev2 [Development]
        >> dev2 "project2"
        .. dev1
        .. dev-frontend
        .. dev-backend
        """.splitlines()
        data = list(topics.mapping(spec))
        logg.debug("data = %s", data)
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]["proj"], "Development")
        self.assertEqual(data[0]["task"], "project1")
        self.assertEqual(data[0]["pref"], "dev1")
        self.assertEqual(data[1]["proj"], "Development")
        self.assertEqual(data[1]["task"], "projects")
        self.assertEqual(data[1]["pref"], "dev-frontend")
        self.assertEqual(data[2]["proj"], "Development")
        self.assertEqual(data[2]["task"], "projects")
        self.assertEqual(data[2]["pref"], "dev-backend")
    def test_411(self) -> None:
        spec = """
        >> dev [Development]
        >> dev "projects"
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
        self.assertEqual(data[0]["ticket"], None)
    def test_412(self) -> None:
        spec = """
        >> dev [Development]
        >> dev "projects"
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
        self.assertEqual(data[0]["ticket"], None)
        self.assertEqual(data[1]["proj"], "Development")
        self.assertEqual(data[1]["task"], "projects")
        self.assertEqual(data[1]["pref"], "dev2")
        self.assertEqual(data[1]["ticket"], None)
    def test_413(self) -> None:
        spec = """
        >> dev [Development]
        >> dev "projects"
        >> dev1 [Development]
        >> dev1 "project1"
        >> dev2 [Development]
        >> dev2 "project2"
        .. dev1
        .. dev2
        """.splitlines()
        data = list(topics.mapping(spec))
        logg.debug("data = %s", data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["proj"], "Development")
        self.assertEqual(data[0]["task"], "project1")
        self.assertEqual(data[0]["pref"], "dev1")
        self.assertEqual(data[0]["ticket"], None)
        self.assertEqual(data[1]["proj"], "Development")
        self.assertEqual(data[1]["task"], "project2")
        self.assertEqual(data[1]["pref"], "dev2")
        self.assertEqual(data[1]["ticket"], None)
    def test_414(self) -> None:
        spec = """
        >> dev [Development]
        >> dev "projects"
        >> dev1 [Development]
        >> dev1 "project1"
        >> dev2 [Development]
        >> dev2 "project2"
        .. dev1
        .. dev2-frontend
        .. dev2-backend
        """.splitlines()
        data = list(topics.mapping(spec))
        logg.debug("data = %s", data)
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]["proj"], "Development")
        self.assertEqual(data[0]["task"], "project1")
        self.assertEqual(data[0]["pref"], "dev1")
        self.assertEqual(data[0]["ticket"], None)
        self.assertEqual(data[1]["proj"], "Development")
        self.assertEqual(data[1]["task"], "project2")
        self.assertEqual(data[1]["pref"], "dev2-frontend")
        self.assertEqual(data[1]["ticket"], None)
        self.assertEqual(data[2]["proj"], "Development")
        self.assertEqual(data[2]["task"], "project2")
        self.assertEqual(data[2]["pref"], "dev2-backend")
        self.assertEqual(data[2]["ticket"], None)
    def test_419(self) -> None:
        spec = """
        >> dev [Development]
        >> dev "projects"
        >> dev1 [Development]
        >> dev1 "project1"
        >> dev2 [Development]
        >> dev2 "project2"
        .. dev1
        .. dev-frontend
        .. dev-backend
        """.splitlines()
        data = list(topics.mapping(spec))
        logg.debug("data = %s", data)
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]["proj"], "Development")
        self.assertEqual(data[0]["task"], "project1")
        self.assertEqual(data[0]["pref"], "dev1")
        self.assertEqual(data[0]["ticket"], None)
        self.assertEqual(data[1]["proj"], "Development")
        self.assertEqual(data[1]["task"], "projects")
        self.assertEqual(data[1]["pref"], "dev-frontend")
        self.assertEqual(data[1]["ticket"], None)
        self.assertEqual(data[2]["proj"], "Development")
        self.assertEqual(data[2]["task"], "projects")
        self.assertEqual(data[2]["pref"], "dev-backend")
        self.assertEqual(data[2]["ticket"], None)
    def test_441(self) -> None:
        spec = """
        >> dev [Development]
        >> dev "projects"
        >> dev MAKE-10: "projects"
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
        self.assertEqual(data[0]["ticket"], None)
    def test_442(self) -> None:
        spec = """
        >> dev [Development]
        >> dev MAKE-10: "projects"
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
        self.assertEqual(data[0]["ticket"], None)
        self.assertEqual(data[1]["proj"], "Development")
        self.assertEqual(data[1]["task"], "projects")
        self.assertEqual(data[1]["pref"], "dev2")
        self.assertEqual(data[1]["ticket"], "MAKE-10")
    def test_443(self) -> None:
        spec = """
        >> dev [Development]
        >> dev MAKE-10: "projects"
        >> dev1 [Development]
        >> dev1 "project1"
        >> dev2 [Development]
        >> dev2 "project2"
        .. dev1
        .. dev2
        """.splitlines()
        data = list(topics.mapping(spec))
        logg.debug("data = %s", data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["proj"], "Development")
        self.assertEqual(data[0]["task"], "project1")
        self.assertEqual(data[0]["pref"], "dev1")
        self.assertEqual(data[0]["ticket"], None)
        self.assertEqual(data[1]["proj"], "Development")
        self.assertEqual(data[1]["task"], "project2")
        self.assertEqual(data[1]["pref"], "dev2")
        self.assertEqual(data[1]["ticket"], None)
    def test_444(self) -> None:
        spec = """
        >> dev [Development]
        >> dev MAKE-10: "projects"
        >> dev1 [Development]
        >> dev1 "project1"
        >> dev2 [Development]
        >> dev2 "project2"
        .. dev1
        .. dev2-frontend
        .. dev2-backend
        """.splitlines()
        data = list(topics.mapping(spec))
        logg.debug("data = %s", data)
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]["proj"], "Development")
        self.assertEqual(data[0]["task"], "project1")
        self.assertEqual(data[0]["pref"], "dev1")
        self.assertEqual(data[0]["ticket"], None)
        self.assertEqual(data[1]["proj"], "Development")
        self.assertEqual(data[1]["task"], "project2")
        self.assertEqual(data[1]["pref"], "dev2-frontend")
        self.assertEqual(data[1]["ticket"], None)
        self.assertEqual(data[2]["proj"], "Development")
        self.assertEqual(data[2]["task"], "project2")
        self.assertEqual(data[2]["pref"], "dev2-backend")
        self.assertEqual(data[2]["ticket"], None)
    def test_445(self) -> None:
        spec = """
        >> dev [Development]
        >> dev "projects"
        >> dev MAKE-10
        >> dev1 [Development]
        >> dev1 "project1"
        >> dev2 [Development]
        >> dev2 "project2"
        .. dev1
        .. dev2-frontend
        .. dev2-backend
        """.splitlines()
        data = list(topics.mapping(spec))
        logg.debug("data = %s", data)
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]["proj"], "Development")
        self.assertEqual(data[0]["task"], "project1")
        self.assertEqual(data[0]["pref"], "dev1")
        self.assertEqual(data[0]["ticket"], None)
        self.assertEqual(data[1]["proj"], "Development")
        self.assertEqual(data[1]["task"], "project2")
        self.assertEqual(data[1]["pref"], "dev2-frontend")
        self.assertEqual(data[1]["ticket"], None)
        self.assertEqual(data[2]["proj"], "Development")
        self.assertEqual(data[2]["task"], "project2")
        self.assertEqual(data[2]["pref"], "dev2-backend")
        self.assertEqual(data[2]["ticket"], None)
    def test_448(self) -> None:
        spec = """
        >> dev [Development]
        >> dev "projects"
        >> dev MAKE-10
        >> dev1 [Development]
        >> dev1 "project1"
        >> dev2 [Development]
        >> dev2 "project2"
        .. dev1
        .. dev-frontend
        .. dev-backend
        """.splitlines()
        data = list(topics.mapping(spec))
        logg.debug("data = %s", data)
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]["proj"], "Development")
        self.assertEqual(data[0]["task"], "project1")
        self.assertEqual(data[0]["pref"], "dev1")
        self.assertEqual(data[0]["ticket"], None)
        self.assertEqual(data[1]["proj"], "Development")
        self.assertEqual(data[1]["task"], "projects")
        self.assertEqual(data[1]["pref"], "dev-frontend")
        self.assertEqual(data[1]["ticket"], "MAKE-10")
        self.assertEqual(data[2]["proj"], "Development")
        self.assertEqual(data[2]["task"], "projects")
        self.assertEqual(data[2]["pref"], "dev-backend")
        self.assertEqual(data[2]["ticket"], "MAKE-10")
    def test_449(self) -> None:
        spec = """
        >> dev [Development]
        >> dev MAKE-10: "projects"
        >> dev1 [Development]
        >> dev1 "project1"
        >> dev2 [Development]
        >> dev2 "project2"
        .. dev1
        .. dev-frontend
        .. dev-backend
        """.splitlines()
        data = list(topics.mapping(spec))
        logg.debug("data = %s", data)
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]["proj"], "Development")
        self.assertEqual(data[0]["task"], "project1")
        self.assertEqual(data[0]["pref"], "dev1")
        self.assertEqual(data[0]["ticket"], None)
        self.assertEqual(data[1]["proj"], "Development")
        self.assertEqual(data[1]["task"], "projects")
        self.assertEqual(data[1]["pref"], "dev-frontend")
        self.assertEqual(data[1]["ticket"], "MAKE-10")
        self.assertEqual(data[2]["proj"], "Development")
        self.assertEqual(data[2]["task"], "projects")
        self.assertEqual(data[2]["pref"], "dev-backend")
        self.assertEqual(data[2]["ticket"], "MAKE-10")
    def test_450(self) -> None:
        spec = """
        >> dev [Development]
        >> dev MAKE-10: "projects"
        >> dev1 [Development]
        >> dev1 MAKE-11: "project1"
        >> dev2 [Development]
        >> dev2 MAKE-12: "project2"
        .. dev1
        .. dev-frontend
        .. dev-backend
        """.splitlines()
        data = list(topics.mapping(spec))
        logg.debug("data = %s", data)
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]["proj"], "Development")
        self.assertEqual(data[0]["task"], "project1")
        self.assertEqual(data[0]["pref"], "dev1")
        self.assertEqual(data[0]["ticket"], "MAKE-11")
        self.assertEqual(data[1]["proj"], "Development")
        self.assertEqual(data[1]["task"], "projects")
        self.assertEqual(data[1]["pref"], "dev-frontend")
        self.assertEqual(data[1]["ticket"], "MAKE-10")
        self.assertEqual(data[2]["proj"], "Development")
        self.assertEqual(data[2]["task"], "projects")
        self.assertEqual(data[2]["pref"], "dev-backend")
        self.assertEqual(data[2]["ticket"], "MAKE-10")
    def test_451(self) -> None:
        spec = """
        >> dev [Development]
        >> dev MAKE-10: "projects"
        >> dev1 [Development]
        >> dev1 MAKE-11: "project1"
        >> dev2 [Development]
        >> dev2 MAKE-12: "project2"
        .. dev1
        .. dev1-frontend
        .. dev1-backend
        """.splitlines()
        data = list(topics.mapping(spec))
        logg.debug("data = %s", data)
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]["proj"], "Development")
        self.assertEqual(data[0]["task"], "project1")
        self.assertEqual(data[0]["pref"], "dev1")
        self.assertEqual(data[0]["ticket"], "MAKE-11")
        self.assertEqual(data[1]["proj"], "Development")
        self.assertEqual(data[1]["task"], "project1")
        self.assertEqual(data[1]["pref"], "dev1-frontend")
        self.assertEqual(data[1]["ticket"], "MAKE-11")
        self.assertEqual(data[2]["proj"], "Development")
        self.assertEqual(data[2]["task"], "project1")
        self.assertEqual(data[2]["pref"], "dev1-backend")
        self.assertEqual(data[2]["ticket"], "MAKE-11")
    def test_452(self) -> None:
        spec = """
        >> dev [Development]
        >> dev MAKE-10: "projects"
        >> dev1 [Development]
        >> dev1 MAKE-11: "project1"
        >> dev2 [Development]
        >> dev2 MAKE-12: "project2"
        .. dev1
        .. dev1-frontend
        .. dev2-backend
        """.splitlines()
        data = list(topics.mapping(spec))
        logg.debug("data = %s", data)
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]["proj"], "Development")
        self.assertEqual(data[0]["task"], "project1")
        self.assertEqual(data[0]["pref"], "dev1")
        self.assertEqual(data[0]["ticket"], "MAKE-11")
        self.assertEqual(data[1]["proj"], "Development")
        self.assertEqual(data[1]["task"], "project1")
        self.assertEqual(data[1]["pref"], "dev1-frontend")
        self.assertEqual(data[1]["ticket"], "MAKE-11")
        self.assertEqual(data[2]["proj"], "Development")
        self.assertEqual(data[2]["task"], "project2")
        self.assertEqual(data[2]["pref"], "dev2-backend")
        self.assertEqual(data[2]["ticket"], "MAKE-12")
    def test_453(self) -> None:
        spec = """
        >> dev [Development]
        >> dev MAKE-10: "projects"
        >> dev1 [Development]
        >> dev1 "project1"
        >> dev1 MAKE-11:
        >> dev2 [Development]
        >> dev2 MAKE-12
        >> dev2 "project2"
        .. dev1
        .. dev1-frontend
        .. dev2-backend
        """.splitlines()
        data = list(topics.mapping(spec))
        logg.debug("data = %s", data)
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]["proj"], "Development")
        self.assertEqual(data[0]["task"], "project1")
        self.assertEqual(data[0]["pref"], "dev1")
        self.assertEqual(data[0]["ticket"], "MAKE-11")
        self.assertEqual(data[1]["proj"], "Development")
        self.assertEqual(data[1]["task"], "project1")
        self.assertEqual(data[1]["pref"], "dev1-frontend")
        self.assertEqual(data[1]["ticket"], "MAKE-11")
        self.assertEqual(data[2]["proj"], "Development")
        self.assertEqual(data[2]["task"], "project2")
        self.assertEqual(data[2]["pref"], "dev2-backend")
        self.assertEqual(data[2]["ticket"], "MAKE-12")
    def test_454(self) -> None:
        spec = """
        >> dev [Development]
        >> dev MAKE-10: "projects"
        >> dev1 [Development]
        >> dev1 "project1"
        >> dev1 MAKE-11:
        >> dev2 [Development]
        >> dev2 MAKE-12
        >> dev2 "project2"
        .. dev1
        .. dev1-frontend
        .. dev2-backend
        >> dev2 MAKE-123
        .. dev2-backend
        """.splitlines()
        data = list(topics.mapping(spec))
        logg.debug("data = %s", data)
        self.assertEqual(len(data), 4)
        self.assertEqual(data[0]["proj"], "Development")
        self.assertEqual(data[0]["task"], "project1")
        self.assertEqual(data[0]["pref"], "dev1")
        self.assertEqual(data[0]["ticket"], "MAKE-11")
        self.assertEqual(data[1]["proj"], "Development")
        self.assertEqual(data[1]["task"], "project1")
        self.assertEqual(data[1]["pref"], "dev1-frontend")
        self.assertEqual(data[1]["ticket"], "MAKE-11")
        self.assertEqual(data[2]["proj"], "Development")
        self.assertEqual(data[2]["task"], "project2")
        self.assertEqual(data[2]["pref"], "dev2-backend")
        self.assertEqual(data[2]["ticket"], "MAKE-12")
        self.assertEqual(data[3]["proj"], "Development")
        self.assertEqual(data[3]["task"], "project2")
        self.assertEqual(data[3]["pref"], "dev2-backend")
        self.assertEqual(data[3]["ticket"], "MAKE-123")

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