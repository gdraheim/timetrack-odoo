#! /usr/bin/python3
""" This function can store username/password tuples either as default or specific
for a root url. It follows in style the dot-netc model from BSD and actually the
code does inspect ~/.netrc for matching entries if a url is specified. The script
can also read the ~/.git-credentials format. Even a mix of entries is possible
where extensions should only be used in a ~/.net-credentials filename."""

# dot git-credentials format:
#   https://<username>:<password>@<hostname>
#
# dot netrc format:
#   machine <hostname> login <username> password <password> protocol <http>
#   machine <hostname> login <username> password <password>
#   machine <hostname> password <password>
#   default login <username> password <password>
#   default password <password>
#
# dot netrc multiline format:
#    machine <hostname>
#    username <username>
#    password <password>
#    protocol <http>
#    default password <password>
#
# where however protocol is ignored and restriction by username not implemented
#
# the net-credentials format supports also:
#   password64 <password|mime64>
#   password46 <password|mime64|rev>
#   password36 <password|mime64|rev|rot13>
#   password63 <password|mime64|rot13>

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

netrc_logg = logging.getLogger("NETRC")

NETRC_USERNAME = ""
NETRC_PASSWORD = ""
NETRC_CLEARTEXT = False

NETRC_OVERRIDE: Dict[str, Tuple[str, str]] = {}
NET_CREDENTIALS = "~/.net-credentials"
GIT_CREDENTIALS = "~/.git-credentials"
NETRC_FILENAME = "~/.netrc"
NETRC_FILENAMES = [GIT_CREDENTIALS, NETRC_FILENAME]

GIT_CONFIG = "~/.gitconfig"

def _target(url: str) -> str:
    if "://" not in url:
        url = f"https://{url}"
    machine = _urlparse(url)
    if machine.path:
        return f"{machine.hostname}/{machine.path}".replace("//", "/")
    return f"{machine.hostname}"
def _targethost(url: str) -> str:
    machine = _urlparse(url)
    return f"{machine.hostname}"

def _encode64(text: str) -> str:
    """ echo -n pw | base64 """
    return codecs.decode(codecs.encode(text.encode('utf-8'), 'base64'), 'ascii').strip()
def _decode64(text: str) -> str:
    return codecs.decode(codecs.decode(text.encode('ascii'), 'base64'), 'utf-8')
def _encode63(text: str) -> str:
    """ echo -n pw | base64 | tr A-Za-z M-ZA-Nm-za-n """
    return codecs.encode(codecs.decode(codecs.encode(text.encode('utf-8'), 'base64'), 'ascii'), 'rot13').strip()
def _decode63(text: str) -> str:
    return codecs.decode(codecs.decode(codecs.decode(text, 'rot13').encode('ascii'), 'base64'), 'utf-8')
def _encode46(text: str) -> str:
    """ echo -n pw | base64 | rev """
    return codecs.decode(codecs.encode(text.encode('utf-8'), 'base64')[::-1], 'ascii').strip()
def _decode46(text: str) -> str:
    return codecs.decode(codecs.decode(text.encode('ascii')[::-1], 'base64'), 'utf-8')
def _encode36(text: str) -> str:
    """ echo -n pw | base64 | rev | tr A-Za-z M-ZA-Nm-za-n """
    # return codecs.decode(codecs.encode(codecs.encode(text.encode('utf-8'), 'base64'), 'rot13')[::-1], 'ascii').strip()
    return codecs.encode(codecs.decode(codecs.encode(text.encode('utf-8'), 'base64'), 'ascii')[::-1], 'rot13').strip()
def _decode36(text: str) -> str:
    return codecs.decode(codecs.decode(codecs.decode(text, 'rot13').encode('ascii')[::-1], 'base64'), 'utf-8')
def _decode(text: str, encoding: str) -> str:
    if encoding.endswith("64"): return _decode64(text).strip()
    if encoding.endswith("63"): return _decode63(text).strip()
    if encoding.endswith("46"): return _decode46(text).strip()
    if encoding.endswith("36"): return _decode36(text).strip()
    return text

def set_username_password(username: str, password: str) -> Tuple[str, str]:
    global NETRC_USERNAME, NETRC_PASSWORD
    if ":" in username:
        NETRC_PASSWORD = username.split(':', 1)[1]
        NETRC_USERNAME = username.split(':', 1)[0]
    else:
        NETRC_USERNAME = username
        NETRC_PASSWORD = password
    return (NETRC_USERNAME, NETRC_PASSWORD)

def add_username_password(username: str, password: str, url: str) -> Tuple[str, str]:
    global NETRC_OVERRIDE, NETRC_USERNAME, NETRC_PASSWORD
    if not url:
        return set_username_password(username, password)
    if ":" in username:
        password = username.split(':', 1)[1]
        username = username.split(':', 1)[0]
    target = _target(url)
    NETRC_OVERRIDE[target] = (username, password)
    return (username, password)

def get_username_password(url: str = "") -> Tuple[str, str]:
    for filename in reversed(get_password_filenames()):
        credentials = Credentials(filename)
        auth = credentials.lookup(url)
        if auth is not None:
            return auth
    return credentials.default()

def get_username(url: str = "") -> str:
    return get_username_password(url)[0]

class Credentials:
    """ lookup for a single credentials store. The default() value can be provided as well. """
    def __init__(self, filename: str,  #
                 username: Optional[str] = None, password: Optional[str] = None, override: Dict[str, Tuple[str, str]] = {}):
        self.FILENAME = filename
        self.USERNAME = username or NETRC_USERNAME
        self.PASSWORD = password or NETRC_PASSWORD
        self.OVERRIDE = override or NETRC_OVERRIDE.copy()
    def set(self, username: str, password: str) -> 'Credentials':
        if ":" in username:
            self.PASSWORD = username.split(':', 1)[1]
            self.USERNAME = username.split(':', 1)[0]
        else:
            self.USERNAME = username
            self.PASSWORD = password
        return self
    def add(self, username: str, password: str, url: str) -> 'Credentials':
        if not url:
            return self.set(username, password)
        if ":" in username:
            password = username.split(':', 1)[1]
            username = username.split(':', 1)[0]
        target = _target(url)
        self.OVERRIDE[target] = (username, password)
        return self
    def get(self, url: str = "") -> Tuple[str, str]:
        if not url:
            return self.username(), self.PASSWORD
        auth = self.lookup(url)
        if auth is None:
            return self.default()
        return auth
    def username(self) -> str:
        return self.USERNAME or os.environ.get("USER") or "anonymous"
    def default(self) -> Tuple[str, str]:
        if self.USERNAME and not self.PASSWORD:
            netrc_logg.warning("no password given and not configured in ~/.netrc")
        return self.username(), self.PASSWORD
    def lookup(self, url: str = "") -> Optional[Tuple[str, str]]:
        target = _target(url)
        if target in self.OVERRIDE:
            return self.OVERRIDE[target]
        return self.search(target)
    def search(self, target: str) -> Optional[Tuple[str, str]]:
        return self._search(target, self.FILENAME)
    def _search(self, target: str, filename: str) -> Optional[Tuple[str, str]]:
        netrc = _path.expanduser(filename)
        block = ""
        if _path.isfile(netrc):
            if os.stat(netrc).st_mode & 0o77:
                netrc_logg.warning(" !! netrc file should be private - chmod 600 %s", netrc)
            netrc_logg.debug("looking for 'machine %s' in %s", target, netrc)
            with open(netrc) as f:
                netrc_text = f.read()
            matches: Dict[str, Tuple[str, str, str]] = {}
            for line in (netrc_text + "\ndefault").splitlines():
                if not line.strip() or line.strip().startswith("#"):
                    continue
                machine = ""
                username: str
                password: str
                encoding = ""
                aliased = ""
                endofblock = False
                if re.match("[a-z][a-z+]*[a-z]://.*", line.strip()):
                    endofblock = True
                    entry = None
                    try:
                        entry = _urlparse(line)
                    except Exception as e:
                        netrc_logg.warning("not a url: '%s': %s", line, e)
                    if entry:
                        pattern = _target(line)
                        if _fnmatch(target, pattern) or _fnmatch(target, pattern + "/*"):
                            username = entry.username or self.username()
                            password = entry.password or ""
                            netrc_logg.debug("matches %s from git credentials %s",
                                             str_username_password(username, password), pattern)
                            matches[pattern] = (username, password, "")
                        else:
                            netrc_logg.debug("skipped %s for %s", target, _target(line))
                if line.strip().startswith("machine") or line.strip().startswith("default"):
                    endofblock = True
                if endofblock:
                    login = re.match(r"\s*machine\s+(\S+)\s+(?:login\s+(\S+)\s+)?(password\d*)\s+(\S+)\s*", block)
                    alias = re.match(r"\s*machine\s+(\S+)\s+(alias|aliased|takefrom)\s+(\S+)\s*", block)
                    if login:
                        machine = (login.group(1) or "").strip()
                        username = (login.group(2) or "").strip() or self.username()
                        encoding = (login.group(3) or "").strip()
                        password = (login.group(4) or "").strip()
                    elif alias:
                        machine = (alias.group(1) or "").strip()
                        aliased = (alias.group(3) or "").strip()
                        encoding = (alias.group(2) or "").strip()
                        password = ""
                    else:
                        netrc_logg.debug("invalid machine block: %s", block)
                    block = ""
                if line.strip().startswith("machine"):
                    block = line
                if line.strip().startswith("login"):
                    block += " " + line.strip()
                if line.strip().startswith("password"):
                    block += " " + line.strip()
                if line.strip().startswith("protocol"):
                    block += " " + line.strip()
                if line.strip().startswith("default"):
                    m = re.match(r"\s*default\s+(?:login\s+(\S+)\s+)?(password\d*)\s+(\S+)\s*", block)
                    if m:
                        machine = "*"
                        username = (m.group(1) or "").strip() or self.username()
                        encoding = (m.group(2) or "").strip()
                        password = (m.group(3) or "").strip()
                if machine:
                    if _fnmatch(target, machine) or _fnmatch(target, machine + "/*"):
                        try:
                            pw = _decode(password, encoding)
                            netrc_logg.debug("matches %s from machine %s in %s",  #
                                             aliased or str_username_password(username, pw), machine, filename)
                            matches[machine] = (username, pw, aliased)
                        except Exception as e:
                            netrc_logg.debug("skipped %s for %s: %s", machine, target, e)
                    else:
                        netrc_logg.debug("skipped %s for %s", machine, target)
            if matches:
                best = ""
                for match in matches:
                    if len(match) >= len(best):
                        best = match
                username, password, aliased = matches[best]
                if aliased:
                    return self._search(aliased, filename)
                netrc_logg.debug("using %s from %s netrc machine %s",  #
                                 str_username_password(username, password), len(matches), best)
                return username, password
        else:
            netrc_logg.debug("no such files: %s", netrc)
        return None

def str_get_username_password(url: str) -> str:
    username, password = get_username_password(url)
    return str_username_password(username, password)
def str_username_password(username: str, password: str) -> str:
    pw = ''.join(["*#%$"[ord(c) & 3] for c in password])
    if NETRC_CLEARTEXT: pw = password
    if not pw: pw = "(no-password)"
    return username + ":" + pw

def get_password_filenames() -> List[str]:
    """ from low to high priority """
    global NET_CREDENTIALS, NETRC_FILENAMES
    filenames = NETRC_FILENAMES[:]
    if NET_CREDENTIALS:
        filenames.append(NET_CREDENTIALS)
    return filenames
def net_password_filename(filename: str) -> None:
    global NET_CREDENTIALS
    if filename:
        NET_CREDENTIALS = filename
def set_password_filename(*filename: str) -> None:
    global NETRC_FILENAMES
    if filename:
        NETRC_FILENAMES = list(filename)
def add_password_filename(*filename: str) -> None:
    global NETRC_FILENAMES
    if filename:
        NETRC_FILENAMES += list(filename)
def set_password_cleartext(show: bool) -> None:
    global NETRC_CLEARTEXT
    NETRC_CLEARTEXT = show

def store_username_password(url: str, username: str, password: str) -> str:
    filename = _path.expanduser(NET_CREDENTIALS)
    machine = _target(url)
    matching0 = f"machine {machine} *"
    matching1 = f"machine {machine}/*"
    lines = []
    if os.path.isfile(filename):
        with open(filename) as f:
            for line in f:
                if _fnmatch(line, matching0) or _fnmatch(line, matching1):
                    continue  # delete
                lines.append(line.rstrip())
    with open(filename, "w") as f:
        password46 = _encode46(password)
        f.write(f"machine {machine} login {username} password46 {password46}\n")
        for line in lines:
            if line.strip():
                f.write(line + "\n")
    os.chmod(filename, 0o600)
    return filename

def erase_username_password(url: str) -> str:
    filename = _path.expanduser(NET_CREDENTIALS)
    machine = _target(url)
    matching0 = f"machine {machine} *"
    matching1 = f"machine {machine}/*"
    lines = []
    if os.path.isfile(filename):
        with open(filename) as f:
            for line in f:
                if _fnmatch(line, matching0) or _fnmatch(line, matching1):
                    continue  # delete
                lines.append(line.rstrip())
    with open(filename, "w") as f:
        for line in lines:
            if line.strip():
                f.write(line + "\n")
    os.chmod(filename, 0o600)
    return filename

if __name__ == "__main__":
    from optparse import OptionParser
    o = OptionParser("%prog [-u username] [-p password] url...")
    o.add_option("-v", "--verbose", action="count", default=0)
    o.add_option("-u", "--username", metavar="NAME", default=NETRC_USERNAME)
    o.add_option("-p", "--password", metavar="PASS", default=NETRC_PASSWORD)
    o.add_option("-N", "--netcredentials", metavar="FILE", default=NET_CREDENTIALS)
    o.add_option("-g", "--gitcredentials", metavar="FILE", default=GIT_CREDENTIALS)
    o.add_option("-G", "--extracredentials", metavar="FILE", default=NETRC_FILENAME)
    o.add_option("-e", "--extrafile", metavar="NAME", default="")
    o.add_option("-y", "--cleartext", action="store_true", default=NETRC_CLEARTEXT)
    opt, args = o.parse_args()
    logging.basicConfig(level=logging.WARNING - 10 * opt.verbose)
    GIT_CREDENTIALS = opt.gitcredentials
    NET_CREDENTIALS = opt.netcredentials
    net_password_filename(opt.netcredentials)
    set_password_filename(opt.gitcredentials)
    add_password_filename(opt.extracredentials)
    NETRC_USERNAME = opt.username
    NETRC_PASSWORD = opt.password
    NETRC_CLEARTEXT = opt.cleartext
    if not args:
        args = ["help"]
    cmd = args[0]
    if cmd in ["help"]:
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
    elif cmd in ["store", "write", "set"]:
        references = store_username_password(args[1], args[2], args[3])
        print("written to", references)
    elif cmd in ["erase", "delete", "del"]:
        references = erase_username_password(args[1])
        print("erased in", references)
    else:
        netrc_logg.error("unknown command '%s'", cmd)
        sys.exit(1)
