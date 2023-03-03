#! /usr/bin/env python3
""" This is a wrapper around netrc.py which can read the git-credentials store,
    adding functions to read the generation gitconfig settings. """

from typing import List, Dict, Tuple, Optional

import logging
import sys
import os
import os.path as _path
import stat
import re
import codecs
from urllib.parse import urlparse as _urlparse
from fnmatch import fnmatchcase as _fnmatch
from configparser import RawConfigParser
from collections import OrderedDict

gitrc_logg = logging.getLogger("GITRC")
GIT_CONFIG = "~/.gitconfig"

GITRC_USERNAME = ""
GITRC_PASSWORD = ""
GITRC_CLEARTEXT = False
GIT_CREDENTIALS = "~/.git-credentials"
NETRC_FILENAME = "~/.netrc"

import netrc

def _target(url: str) -> str:
    return netrc._target(url)

def get_username_password(url: str = "") -> Tuple[str, str]:
    return netrc.get_username_password(url)
def get_username(url: str = "") -> str:
    return netrc.get_username(url)
def str_get_username_password(url: str) -> str:
    return netrc.str_get_username_password(url)
def str_username_password(username: str, password: str) -> str:
    return netrc.str_username_password(username, password)
def set_password_filename(*filename: str) -> None:
    netrc.set_password_filename(*filename)
def add_password_filename(*filename: str) -> None:
    netrc.add_password_filename(*filename)
def set_password_cleartext(show: bool) -> None:
    netrc.set_password_cleartext(show)

git_config_overrides : Dict[str, Dict[str, str]] = {}

def git_config_value(key: str, name: str = "") -> Optional[str]:
    if not name:
        section, name = key.split(".", 1)
    else:
        section = key
    value = git_config_override_value(section, name)
    if value is not None:
       return value
    filename = _path.expanduser(GIT_CONFIG)
    try:
        config = RawConfigParser(dict_type=OrderedDict)
        config.read(filename)
        return config.get(section, name)
    except Exception as e:
        gitrc_logg.debug("%s: %s", filename, e)
        return None

def git_config_override_value(key: str, name: str = "") -> Optional[str]:
    global git_config_overrides
    if not name:
        section, name = key.split(".", 1)
    else:
        section = key
    if section in git_config_overrides:
        if name in git_config_overrides[section]:
            return git_config_overrides[section][name]
    gitrc_logg.debug("[%s][%s] -> None", section, name)
    gitrc_logg.debug("overrides = %s", git_config_overrides)
    return None

def git_config_override(line: str) -> None:
    global git_config_overrides
    if "=" in line:
        name, value = line.split("=",1)
    else:
        name = line.strip()
        value = "1"
    if "." in name:
        section, key = name.split(".", 1)
    else:
        section, key = name, "value"
    if section not in git_config_overrides:
        git_config_overrides[section] = {}
    git_config_overrides[section][key] = value
    gitrc_logg.debug("[%s][%s] = '%s' # %s", section, key, value, line.strip())

if __name__ == "__main__":
    from optparse import OptionParser
    o = OptionParser("%prog [-u username] [-p password] url...")
    o.add_option("-v", "--verbose", action="count", default=0)
    o.add_option("-u", "--username", metavar="NAME", default=GITRC_USERNAME)
    o.add_option("-p", "--password", metavar="PASS", default=GITRC_PASSWORD)
    o.add_option("-g", "--gitcredentials", metavar="FILE", default=GIT_CREDENTIALS)
    o.add_option("-G", "--extracredentials", metavar="FILE", default=NETRC_FILENAME)
    o.add_option("-C", "--gitconfig", metavar="FILE", default=GIT_CONFIG)
    o.add_option("-c", "--config", metavar="NAME=VALUE", action="append", default=[])
    o.add_option("-y", "--cleartext", action="store_true", default=False)
    opt, args = o.parse_args()
    logging.basicConfig(level=logging.WARNING - 10 * opt.verbose)
    GIT_CONFIG = opt.gitconfig
    for value in opt.config:
        git_config_override(value)
    netrc.GIT_CREDENTIALS = opt.gitcredentials
    add_password_filename(opt.extracredentials)
    netrc.NETRC_USERNAME = opt.username
    netrc.NETRC_PASSWORD = opt.password
    netrc.NETRC_CLEARTEXT = opt.cleartext
    if not args:
        args = ["help"]
    cmd = args[0]
    if cmd in ["help"]:
        print(netrc.__doc__)
        print(__doc__)
    elif cmd in ["get", "find", "for"]:
        uselogin = get_username_password(args[1])
        if not uselogin: sys.exit(1)
        hostpath = _target(args[1]).split("/", 1) + [""]
        # printing in the style of https://git-scm.com/docs/git-credential
        if hostpath[0]: print("host=" + hostpath[0])
        if hostpath[1]: print("path=" + hostpath[1])
        if uselogin[0]: print("username=" + uselogin[0])
        if uselogin[1]: print("password=" + uselogin[1])
        print("")
    elif cmd.startswith("user.") or cmd.startswith("http."):
        value = git_config_value(cmd)
        if value:
            print(value)
    elif cmd.startswith("odoo.") or cmd.startswith("zeit."):
        value = git_config_value(cmd)
        if value:
            print(value)
        else:
            gitrc_logg.error("# not found")
    else:
        uselogin = get_username_password(args[0])
        if not uselogin: sys.exit(1)
        print("--username '%s' --password '%s'" % (uselogin[0], uselogin[1]))
