#! /usr/bin/env python3
# pylint: disable=missing-function-docstring,missing-class-docstring
# pylint: disable=global-statement,global-variable-not-assigned,import-outside-toplevel

from typing import Optional
from pathlib import Path
from timerange import Day
import os.path as path

DEFAULT_FILENAME = "~/zeit{YEAR}.txt"
ZEIT_FILENAME = ""
ZEIT_USER_NAME = ""
NIX = ""

class ZeitConfig:
    pathspec: str
    username: Optional[str]
    site: Optional[str]
    def __init__(self, pathspec: Optional[str] = None, username: Optional[str] = None):
        self.pathspec = pathspec or ""
        self.username = username
    def for_user(self, user: str) -> "ZeitConfig":
        self.username = user
        return self
    def from_file(self, spec: str) -> "ZeitConfig":
        self.pathspec = spec
        return self
    def on_site(self, site: str) -> "ZeitConfig":
        self.site = site
        return self
    def name(self) -> str:
        if self.site:
            return self.site
        return path.basename(path.dirname(self.pathspec))
    def user_name(self) -> Optional[str]:
        global ZEIT_USER_NAME
        if ZEIT_USER_NAME:
            return ZEIT_USER_NAME
        import dotgitconfig
        return dotgitconfig.git_config_value("user.name")
    def filespec(self) -> str:
        if self.pathspec:
            return self.pathspec
        global ZEIT_FILENAME
        if ZEIT_FILENAME:
            return ZEIT_FILENAME
        import dotgitconfig
        found = dotgitconfig.git_config_value("zeit.filename")
        if found:
            return found
        return DEFAULT_FILENAME
    def filename(self, after: Optional[Day]) -> Path:
        filename = self.filespec()
        return self.expand(filename, after)
    def expand(self, filename: str, after: Optional[Day]) -> Path:
        YEAR = after.year if after else Day.today().year
        return Path(filename.format(**locals())).expanduser()
    def default_user_name(self, newdefault: str = NIX) -> str:
        return default_user_name(newdefault)
    def default_filename(self, newdefault: str = NIX) -> str:
        return default_filename(newdefault)

def default_user_name(newdefault: str = NIX) -> str:
    global ZEIT_USER_NAME
    if newdefault:
        ZEIT_USER_NAME = newdefault
    return ZEIT_USER_NAME

def default_filename(newdefault: str = NIX) -> str:
    global ZEIT_FILENAME
    if newdefault:
        ZEIT_FILENAME = newdefault
    return ZEIT_FILENAME

def zeit_user_name(newdefault: str = NIX) -> Optional[str]: # obsolete
    zeit = ZeitConfig()
    zeit.default_user_name(newdefault)
    return zeit.user_name()

def zeit_filename(newdefault: str = NIX, after: Optional[Day] = None) -> Path: # obsolete
    zeit = ZeitConfig()
    zeit.default_filename(newdefault)
    return zeit.filename(after)
