#! /usr/bin/env python3
""" This function can store username/password tuples either as default or specific
for a root url. It follows in style the dot-netc model from BSD and actually the
code does inspect ~/.netrc for matching entries if a url is specified. The script
can also read the ~/.git-credentials format. Even a mix of entries is possible
where extensions should only be used in a ~/.net-credentials filename. ////
Use command './dotnetrc.py set <url> <name> <pass>' to write entries."""

__version__ = "0.4.4023"

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
import re
import codecs
from base64 import b64encode, b64decode
from collections import OrderedDict
from urllib.parse import urlparse as _urlparse
from fnmatch import fnmatchcase as _fnmatch

netrc_logg = logging.getLogger("NETRC")
HINT = (logging.DEBUG + logging.INFO) // 2
logging.addLevelName(HINT, "HINT")

NETRC_USERNAME = ""
NETRC_PASSWORD = ""
NETRC_CLEARTEXT = False

NETRC_OVERRIDE: Dict[str, Tuple[str, str]] = OrderedDict()
NET_CREDENTIALS = "~/.net-credentials"
GIT_CREDENTIALS = "~/.git-credentials"
NETRC_FILENAME = "~/.netrc"
NETRC_FILENAMES = [GIT_CREDENTIALS, NETRC_FILENAME]

NETRC_CRYPT = "46"

def _target(url: str) -> str:
    if "://" not in url:
        url = f"https://{url}"
    machine = _urlparse(url)
    port = ""
    if machine.port and machine.port not in [80, 443]:
        port = f":{machine.port}"
    if machine.path:
        return f"{machine.hostname}{port}/{machine.path}".replace("//", "/")
    return f"{machine.hostname}{port}"

def _encode64(text: str) -> str:
    """ echo -n pw | base64 """
    return codecs.decode(b64encode(text.encode('utf-8')), 'ascii').strip()
def _decode64(text: str) -> str:
    return codecs.decode(b64decode(text.encode('ascii')), 'utf-8')
def _encode63(text: str) -> str:
    """ echo -n pw | base64 | tr A-Za-z M-ZA-Nm-za-n """
    return codecs.encode(codecs.decode(b64encode(text.encode('utf-8')), 'ascii'), 'rot13').strip()
def _decode63(text: str) -> str:
    return codecs.decode(b64decode(codecs.decode(text, 'rot13').encode('ascii')), 'utf-8')
def _encode46(text: str) -> str:
    """ echo -n pw | base64 | rev """
    return codecs.decode(b64encode(text.encode('utf-8'))[::-1], 'ascii').strip()
def _decode46(text: str) -> str:
    return codecs.decode(b64decode(text.encode('ascii')[::-1]), 'utf-8')
def _encode36(text: str) -> str:
    """ echo -n pw | base64 | rev | tr A-Za-z M-ZA-Nm-za-n """
    # return codecs.decode(codecs.encode(b64encode(text.encode('utf-8')), 'rot13')[::-1], 'ascii').strip()
    return codecs.encode(codecs.decode(b64encode(text.encode('utf-8')), 'ascii')[::-1], 'rot13').strip()
def _decode36(text: str) -> str:
    return codecs.decode(b64decode(codecs.decode(text, 'rot13').encode('ascii')[::-1]), 'utf-8')
def _encode32(text: str) -> str:
    return codecs.decode(b64encode(cryptData(text.encode('utf-8'))).replace(b"\n", b""), 'ascii')
def _decode32(text: str) -> str:
    return codecs.decode(decryptData(b64decode(text.encode('ascii'))), 'utf-8')

def _decode(text: str, encoding: Optional[str] = None) -> str:
    encoding = encoding if encoding is not None else NETRC_CRYPT
    if encoding.endswith("64"): return _decode64(text).strip()
    if encoding.endswith("63"): return _decode63(text).strip()
    if encoding.endswith("46"): return _decode46(text).strip()
    if encoding.endswith("36"): return _decode36(text).strip()
    if encoding.endswith("32"): return _decode32(text).strip()
    return text
def _encode(text: str, encoding: Optional[str] = None) -> str:
    encoding = encoding if encoding is not None else NETRC_CRYPT
    if encoding.endswith("64"): return _encode64(text).strip()
    if encoding.endswith("63"): return _encode63(text).strip()
    if encoding.endswith("46"): return _encode46(text).strip()
    if encoding.endswith("36"): return _encode36(text).strip()
    if encoding.endswith("32"): return _encode32(text).strip()
    return text

# ...............................................................................................................
if os.name in ['nt']:
    # https://stackoverflow.com/questions/463832/using-dpapi-with-python
    # DPAPI access library
    # This file uses code originally created by Crusher Joe:
    # http://article.gmane.org/gmane.comp.python.ctypes/420
    #

    from ctypes import *
    from ctypes.wintypes import DWORD

    LocalFree = windll.kernel32.LocalFree  # type: ignore[name-defined]
    memcpy = cdll.msvcrt.memcpy  # type: ignore[name-defined]
    CryptProtectData = windll.crypt32.CryptProtectData  # type: ignore[name-defined]
    CryptUnprotectData = windll.crypt32.CryptUnprotectData  # type: ignore[name-defined]
    CRYPTPROTECT_UI_FORBIDDEN = 0x01
    extraEntropy = b"cl;ad13 \0al;323kjd #(adl;k$#ajsd"

    class DATA_BLOB(Structure):
        _fields_ = [("cbData", DWORD), ("pbData", POINTER(c_char))]

    def getData(blobOut: DATA_BLOB) -> bytes:
        cbData = int(blobOut.cbData)
        pbData = blobOut.pbData
        buffer = c_buffer(cbData)
        memcpy(buffer, pbData, cbData)
        LocalFree(pbData)
        return buffer.raw

    def Win32CryptProtectData(plainText: bytes, entropy: bytes) -> bytes:
        bufferIn = c_buffer(plainText, len(plainText))
        blobIn = DATA_BLOB(len(plainText), bufferIn)
        bufferEntropy = c_buffer(entropy, len(entropy))
        blobEntropy = DATA_BLOB(len(entropy), bufferEntropy)
        blobOut = DATA_BLOB()

        if CryptProtectData(byref(blobIn), u"python_data", byref(blobEntropy),
                            None, None, CRYPTPROTECT_UI_FORBIDDEN, byref(blobOut)):
            return getData(blobOut)
        else:
            return b""

    def Win32CryptUnprotectData(cipherText: bytes, entropy: bytes) -> bytes:
        bufferIn = c_buffer(cipherText, len(cipherText))
        blobIn = DATA_BLOB(len(cipherText), bufferIn)
        bufferEntropy = c_buffer(entropy, len(entropy))
        blobEntropy = DATA_BLOB(len(entropy), bufferEntropy)
        blobOut = DATA_BLOB()
        if CryptUnprotectData(byref(blobIn), None, byref(blobEntropy), None, None,
                              CRYPTPROTECT_UI_FORBIDDEN, byref(blobOut)):
            return getData(blobOut)
        else:
            return b""

    def cryptData(text: bytes) -> bytes:
        return Win32CryptProtectData(text, extraEntropy)

    def decryptData(cipher_text: bytes) -> bytes:
        return Win32CryptUnprotectData(cipher_text, extraEntropy)

    NETRC_CRYPT = '32'
# ...............................................................................................................

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
    credentials = CredentialsStore()
    auth = credentials.lookup(url)
    if auth is not None:
        return auth
    for filename in reversed(get_password_filenames()):
        credentials = Credentials(filename)
        auth = credentials.lookup(url)
        if auth is not None:
            return auth
    return credentials.default()

def get_username(url: str = "") -> str:
    return get_username_password(url)[0]

class CredentialsStore:
    def __init__(self, username: Optional[str] = None, password: Optional[str] = None, override: Optional[Dict[str, Tuple[str, str]]] = None):
        self.USERNAME = username or NETRC_USERNAME
        self.PASSWORD = password or NETRC_PASSWORD
        self.OVERRIDE = OrderedDict()
        if override is not None:
            for key, val in override.items():
                self.OVERRIDE[key] = val
        else:
            for key, val in NETRC_OVERRIDE.items():
                self.OVERRIDE[key] = val
        self.USEOVERRIDES = True
    def set(self, username: str, password: str) -> 'CredentialsStore':
        if ":" in username:
            self.PASSWORD = username.split(':', 1)[1]
            self.USERNAME = username.split(':', 1)[0]
        else:
            self.USERNAME = username
            self.PASSWORD = password
        return self
    def add(self, username: str, password: str, url: str) -> 'CredentialsStore':
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
        return self.search(_target(url))
    def search(self, target: str) -> Optional[Tuple[str, str]]:
        matches: Dict[str, Tuple[str, str]] = {}
        for machine in self.OVERRIDE:
            # netrc_logg.debug("target %s override %s", target, machine)
            if _fnmatch(target, machine) or _fnmatch(target, machine + "/*"):
                matches[machine] = self.OVERRIDE[machine]
        if matches:
            best = ""
            for match in matches:
                if len(match) >= len(best):
                    best = match
            username, password = matches[best]
            netrc_logg.log(HINT, "using %s from %s override machine %s",  #
                           str_username_password(username, password), len(matches), best)
            return username, password
        return None

class Credentials(CredentialsStore):
    """ lookup for a single credentials store. The default() value can be provided as well. """
    def __init__(self, filename: str,  #
                 username: Optional[str] = None, password: Optional[str] = None, override: Optional[Dict[str, Tuple[str, str]]] = None):
        CredentialsStore.__init__(self, username, password, override)
        self.FILENAME = filename
    def lookup(self, url: str = "") -> Optional[Tuple[str, str]]:
        return self.search(_target(url))
    def search(self, target: str) -> Optional[Tuple[str, str]]:
        return self._search(target, self.FILENAME)
    def _search(self, target: str, filename: str) -> Optional[Tuple[str, str]]:
        netrc = _path.expanduser(filename)
        block = ""
        if _path.isfile(netrc):
            if os.stat(netrc).st_mode & 0o77 and os.name not in ['nt']:
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
                    elif block.strip():  # not empty
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
            if self.USEOVERRIDES:
                for machine in self.OVERRIDE:
                    # netrc_logg.debug("target %s override %s", target, machine)
                    if _fnmatch(target, machine) or _fnmatch(target, machine + "/*"):
                        username, password = self.OVERRIDE[machine]
                        matches[machine] = (username, password, "")
            if matches:
                best = ""
                for match in matches:
                    if len(match) >= len(best):
                        best = match
                username, password, aliased = matches[best]
                if aliased:
                    return self._search(aliased, filename)
                netrc_logg.log(HINT, "using %s from %s netrc machine %s",  #
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
    lines: List[str] = []
    if os.path.isfile(filename):
        with open(filename) as f:
            for line in f:
                if _fnmatch(line, matching0) or _fnmatch(line, matching1):
                    continue  # delete
                lines.append(line.rstrip())
    with open(filename, "w") as f:
        crypt: str = NETRC_CRYPT
        cryptpassword = _encode(password, crypt)
        f.write(f"machine {machine} login {username} password{crypt} {cryptpassword}\n")
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
    cmdline = OptionParser("%prog [-u username] [-p password] url | HELP | DEL url | SET url name pass",
                           epilog=__doc__, version=__version__)
    cmdline.formatter.max_help_position = 36
    cmdline.add_option("-v", "--verbose", action="count", default=0, help="more verbose logging")
    cmdline.add_option("-^", "--quiet", action="count", default=0, help="less verbose logging")
    cmdline.add_option("-u", "--username", metavar="NAME", default=NETRC_USERNAME, help="fallback to default user")
    cmdline.add_option("-p", "--password", metavar="PASS", default=NETRC_PASSWORD, help="fallback to default pass")
    cmdline.add_option("-f", "--fromcredentials", metavar="FILE", default="", help="scan this instead of:")
    cmdline.add_option("-N", "--netcredentials", metavar="FILE", default=NET_CREDENTIALS, help="[%default]")
    cmdline.add_option("-g", "--gitcredentials", metavar="FILE", default=GIT_CREDENTIALS, help="[%default]")
    cmdline.add_option("-G", "--extracredentials", metavar="FILE", default=NETRC_FILENAME, help="[%default]")
    cmdline.add_option("-e", "--extrafile", metavar="NAME", default="")
    cmdline.add_option("-y", "--cleartext", action="store_true", default=NETRC_CLEARTEXT)
    cmdline.add_option("-2", "--crypt32", action="store_true", default=False, help="use win32crypt (default if available)")
    cmdline.add_option("-3", "--crypt36", action="store_true", default=False, help="use triple obfuscation with rot13")
    cmdline.add_option("-4", "--crypt46", action="store_true", default=False, help="use double obfuscation with rev")
    cmdline.add_option("-6", "--crypt64", action="store_true", default=False, help="use single obfuscation with base64")
    cmdline.add_option("-9", "--nocrypt", action="store_true", default=False, help="use no obfusction for passwords")
    cmdline.add_option("-a", "--as-username", action="store_true", help="as  '--username user --password pass'")
    cmdline.add_option("--as-user", action="store_true", help="show as '--user user --password pass'")
    cmdline.add_option("--as-ac", action="store_true", help="show as '-a user -c pass'")
    cmdline.add_option("--as-up", action="store_true", help="show as '-u user -p pass'")
    cmdline.add_option("--as-u", action="store_true", help="show as '-u user:pass'")
    opt, args = cmdline.parse_args()
    logging.basicConfig(level=max(0, logging.WARNING - 10 * opt.verbose + 10 * opt.quiet))
    if opt.fromcredentials:
        NET_CREDENTIALS = opt.fromcredentials
        net_password_filename(opt.fromcredentials)
    else:
        GIT_CREDENTIALS = opt.gitcredentials
        NET_CREDENTIALS = opt.netcredentials
        net_password_filename(opt.netcredentials)
        set_password_filename(opt.gitcredentials)
    add_password_filename(opt.extracredentials)
    NETRC_USERNAME = opt.username
    NETRC_PASSWORD = opt.password
    NETRC_CLEARTEXT = opt.cleartext
    if opt.nocrypt:
        NETRC_CRYPT = ""
    if opt.crypt46:
        NETRC_CRYPT = "64"
    if opt.crypt46:
        NETRC_CRYPT = "46"
    if opt.crypt36:
        NETRC_CRYPT = "36"
    if opt.crypt32:
        NETRC_CRYPT = "32"
    if not args:
        args = ["help"]
    elif len(args) == 1 and "." in args[0]:
        args = ["GET"] + args
    elif len(args) >= 3 and "." in args[0]:
        args = ["SET"] + args
    cmd = args[0]
    if cmd in ["help", "HELP"]:
        cmdline.print_help()
        print("\nCommands:")
        previous = ""
        for line in open(__file__):
            if previous.strip().replace("elif cmd", "if cmd").startswith("if cmd in"):
                if "#" in line:
                    print(previous.strip().split(" cmd in")[1], line.strip().split("#")[1])
                else:
                    print(previous.strip().split(" cmd in")[1], line.strip())
            previous = line
        raise SystemExit()
    elif cmd in ["get", "find", "for", "GET"]:
        uselogin = get_username_password(args[1])
        if not uselogin: sys.exit(1)
        hostpath = _target(args[1]).split("/", 1) + [""]
        # printing in the style of https://git-scm.com/docs/git-credential
        if opt.as_username:
            print(" --username " + uselogin[0] + " --password " + uselogin[1])
        elif opt.as_user:
            print(" --user " + uselogin[0] + " --password " + uselogin[1])
        elif opt.as_ac:
            print(" -a " + uselogin[0] + " -c " + uselogin[1])
        elif opt.as_up:
            print(" -u " + uselogin[0] + " -p " + uselogin[1])
        elif opt.as_u:
            print(" -u " + uselogin[0] + ":" + uselogin[1])
        else:
            if hostpath[0]: print("host=" + hostpath[0])
            if hostpath[1]: print("path=" + hostpath[1])
            if uselogin[0]: print("username=" + uselogin[0])
            if uselogin[1]: print("password=" + uselogin[1])
        print("")
    elif cmd in ["store", "write", "set", "SET"]:
        references = store_username_password(args[1], args[2], args[3])
        print("written to", references)
    elif cmd in ["erase", "delete", "del", "DEL"]:
        references = erase_username_password(args[1])
        print("erased in", references)
    else:
        netrc_logg.error("unknown command '%s'", cmd)
        sys.exit(1)
