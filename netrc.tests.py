#! /usr/bin/env python3

from typing import Optional

import os
import sys
import unittest
import tempfile
import os.path as path
import subprocess
from fnmatch import fnmatchcase as fnmatch
from urllib.parse import urlparse

import netrc

import logging
logg = logging.getLogger("TEST")


url_div = "https://pforgeipt.intra"
url_k8s = "https://k8s.pforgeipt-docker.intra"
dev_div = "https://dev.pforgeipt.intra"
dev_k8s = "https://devk8s.pforgeipt-docker.intra"

TEMP_NETRC: Optional[str] = None

def netloc(url: str) -> str:
    return urlparse(url).netloc

class netcTest(unittest.TestCase):
    def netrc(self) -> str:
        return TEMP_NETRC or "/dev/null"
    def setUp(self) -> None:
        logg.info("setUp")
        global TEMP_NETRC
        F, TEMP_NETRC = tempfile.mkstemp(suffix=".netrc")
        assert TEMP_NETRC
        netrc.NETRC_FILENAMES = [TEMP_NETRC]
        logg.info("netrc -> %s", netrc.NETRC_FILENAMES)
        os.environ["USER"] = "testuser"
    def tearDown(self) -> None:
        logg.info("tearDown")
        global TEMP_NETRC
        if TEMP_NETRC and path.exists(TEMP_NETRC):
            os.unlink(TEMP_NETRC)
        TEMP_NETRC = None
        netrc.NETRC_OVERRIDE = {}
        netrc.NETRC_USERNAME = ""
        netrc.NETRC_PASSWORD = ""
        netrc.NETRC_CLEARTEXT = True
    def test_034(self) -> None:
        obf = netrc._encode64("your text")
        self.assertEqual(obf, 'eW91ciB0ZXh0')
        txt = netrc._decode64(obf)
        self.assertEqual(txt, "your text")
    def test_035(self) -> None:
        obf = netrc._encode46("your text")
        self.assertEqual(obf, '0hXZ0Bic19We')
        txt = netrc._decode46(obf)
        self.assertEqual(txt, "your text")
    def test_036(self) -> None:
        obf = netrc._encode36("your text")
        self.assertEqual(obf, '0uKM0Ovp19Jr')
        txt = netrc._decode36(obf)
        self.assertEqual(txt, "your text")
    def test_037(self) -> None:
        obf = netrc._encode63("your text")
        self.assertEqual(obf, 'rJ91pvO0MKu0')
        txt = netrc._decode63(obf)
        self.assertEqual(txt, "your text")
    def test_040(self) -> None:
        us, pw = netrc.get_username_password(url_div)
        self.assertEqual(us, "testuser")
        self.assertEqual(pw, "")
    def test_050(self) -> None:
        netrc.set_username_password("abc", "xyz")
        us, pw = netrc.get_username_password(url_div)
        self.assertEqual(us, "abc")
        self.assertEqual(pw, "xyz")
    def test_051(self) -> None:
        netrc.set_username_password("abc", "xyz")
        us, pw = netrc.get_username_password(url_k8s)
        self.assertEqual(us, "abc")
        self.assertEqual(pw, "xyz")
    def test_052(self) -> None:
        netrc.set_username_password("abc", "xyz")
        netrc.set_username_password("abc", "uvw")
        us, pw = netrc.get_username_password(url_div)
        self.assertEqual(us, "abc")
        self.assertEqual(pw, "uvw")
    def test_060(self) -> None:
        netrc.set_username_password("abc", "xyz")
        netrc.set_username_password("abc", "uvw")
        netrc.add_username_password("abc", "123", url_div)
        us, pw = netrc.get_username_password(url_div)
        self.assertEqual(us, "abc")
        self.assertEqual(pw, "123")
        us, pw = netrc.get_username_password(url_k8s)
        self.assertEqual(us, "abc")
        self.assertEqual(pw, "uvw")
    def test_061(self) -> None:
        netrc.set_username_password("abc", "xyz")
        netrc.set_username_password("abc", "uvw")
        netrc.add_username_password("abc", "123", url_div)
        us, pw = netrc.get_username_password(url_div)
        self.assertEqual(us, "abc")
        self.assertEqual(pw, "123")
        us, pw = netrc.get_username_password(url_k8s)
        self.assertEqual(us, "abc")
        self.assertEqual(pw, "uvw")
        #
        netrc.set_username_password("abc", "pqr")
        netrc.add_username_password("abc", "345", url_div)
        us, pw = netrc.get_username_password(url_div)
        self.assertEqual(us, "abc")
        self.assertEqual(pw, "345")
        us, pw = netrc.get_username_password(url_k8s)
        self.assertEqual(us, "abc")
        self.assertEqual(pw, "pqr")
    def test_201(self) -> None:
        netrc.set_username_password("abc", "xyz")
        netrc.set_username_password("abc", "uvw")
        with open(self.netrc(), "w") as f:
            f.write(f"https://foo:pqr@{netloc(url_div)}")
        us, pw = netrc.get_username_password(url_div)
        self.assertEqual(us, "foo")
        self.assertEqual(pw, "pqr")
        us, pw = netrc.get_username_password(url_k8s)
        self.assertEqual(us, "abc")
        self.assertEqual(pw, "uvw")
    def test_211(self) -> None:
        netrc.set_username_password("abc", "xyz")
        netrc.set_username_password("abc", "uvw")
        with open(self.netrc(), "w") as f:
            f.write(f"https://foo:pqr@*.intra")
        us, pw = netrc.get_username_password(url_div)
        self.assertEqual(us, "foo")
        self.assertEqual(pw, "pqr")
        us, pw = netrc.get_username_password(url_k8s)
        self.assertEqual(us, "foo")
        self.assertEqual(pw, "pqr")
    def test_221(self) -> None:
        netrc.set_username_password("abc", "xyz")
        netrc.set_username_password("abc", "uvw")
        with open(self.netrc(), "w") as f:
            f.write(f"https://foo:pqr@{netloc(url_div)}\n")
            f.write(f"https://foo:ijk@*.intra\n")
        us, pw = netrc.get_username_password(url_div)
        self.assertEqual(us, "foo")
        self.assertEqual(pw, "pqr")
        us, pw = netrc.get_username_password(url_k8s)
        self.assertEqual(us, "foo")
        self.assertEqual(pw, "ijk")
    def test_231(self) -> None:
        netrc.set_username_password("abc", "xyz")
        netrc.set_username_password("abc", "uvw")
        with open(self.netrc(), "w") as f:
            f.write(f"https://foo:pqr@{netloc(url_div)}\n")
            f.write(f"https://foo:ijk@*.intra\n")
        us, pw = netrc.get_username_password(url_div)
        self.assertEqual(us, "foo")
        self.assertEqual(pw, "pqr")
        us, pw = netrc.get_username_password(url_k8s)
        self.assertEqual(us, "foo")
        self.assertEqual(pw, "ijk")
    def test_301(self) -> None:
        netrc.set_username_password("abc", "xyz")
        netrc.set_username_password("abc", "uvw")
        with open(self.netrc(), "w") as f:
            f.write(f"machine {netloc(url_div)} login foo password pqr")
        us, pw = netrc.get_username_password(url_div)
        self.assertEqual(us, "foo")
        self.assertEqual(pw, "pqr")
        us, pw = netrc.get_username_password(url_k8s)
        self.assertEqual(us, "abc")
        self.assertEqual(pw, "uvw")
    def test_311(self) -> None:
        netrc.set_username_password("abc", "xyz")
        netrc.set_username_password("abc", "uvw")
        with open(self.netrc(), "w") as f:
            f.write(f"machine *.intra login foo password pqr")
        us, pw = netrc.get_username_password(url_div)
        self.assertEqual(us, "foo")
        self.assertEqual(pw, "pqr")
        us, pw = netrc.get_username_password(url_k8s)
        self.assertEqual(us, "foo")
        self.assertEqual(pw, "pqr")
    def test_312(self) -> None:
        netrc.set_username_password("abc", "xyz")
        netrc.set_username_password("abc", "uvw")
        with open(self.netrc(), "w") as f:
            f.write(f"machine *.intra password pqr")
        us, pw = netrc.get_username_password(url_div)
        self.assertEqual(us, "abc")
        self.assertEqual(pw, "pqr")
        us, pw = netrc.get_username_password(url_k8s)
        self.assertEqual(us, "abc")
        self.assertEqual(pw, "pqr")
    def test_313(self) -> None:
        with open(self.netrc(), "w") as f:
            f.write(f"machine *.intra password pqr")
        us, pw = netrc.get_username_password(url_div)
        self.assertEqual(us, "testuser")
        self.assertEqual(pw, "pqr")
        us, pw = netrc.get_username_password(url_k8s)
        self.assertEqual(us, "testuser")
        self.assertEqual(pw, "pqr")
    def test_316(self) -> None:
        with open(self.netrc(), "w") as f:
            f.write(f"machine *.intra password64 cHFy")
        us, pw = netrc.get_username_password(url_div)
        self.assertEqual(us, "testuser")
        self.assertEqual(pw, "pqr")
        us, pw = netrc.get_username_password(url_k8s)
        self.assertEqual(us, "testuser")
        self.assertEqual(pw, "pqr")
    def test_317(self) -> None:
        with open(self.netrc(), "w") as f:
            f.write(f"machine *.intra password46 yFHc")
        us, pw = netrc.get_username_password(url_div)
        self.assertEqual(us, "testuser")
        self.assertEqual(pw, "pqr")
        us, pw = netrc.get_username_password(url_k8s)
        self.assertEqual(us, "testuser")
        self.assertEqual(pw, "pqr")
    def test_318(self) -> None:
        with open(self.netrc(), "w") as f:
            f.write(f"machine *.intra password36 lSUp")
        us, pw = netrc.get_username_password(url_div)
        self.assertEqual(us, "testuser")
        self.assertEqual(pw, "pqr")
        us, pw = netrc.get_username_password(url_k8s)
        self.assertEqual(us, "testuser")
        self.assertEqual(pw, "pqr")
    def test_319(self) -> None:
        with open(self.netrc(), "w") as f:
            f.write(f"machine *.intra password63 pUSl")
        us, pw = netrc.get_username_password(url_div)
        self.assertEqual(us, "testuser")
        self.assertEqual(pw, "pqr")
        us, pw = netrc.get_username_password(url_k8s)
        self.assertEqual(us, "testuser")
        self.assertEqual(pw, "pqr")
    def test_321(self) -> None:
        netrc.set_username_password("abc", "xyz")
        netrc.set_username_password("abc", "uvw")
        with open(self.netrc(), "w") as f:
            f.write(f"machine {netloc(url_div)} login foo password pqr\n")
            f.write(f"machine *.intra login foo password ijk\n")
        us, pw = netrc.get_username_password(url_div)
        self.assertEqual(us, "foo")
        self.assertEqual(pw, "pqr")
        us, pw = netrc.get_username_password(url_k8s)
        self.assertEqual(us, "foo")
        self.assertEqual(pw, "ijk")
    def test_322(self) -> None:
        netrc.set_username_password("abc", "xyz")
        netrc.set_username_password("abc", "uvw")
        with open(self.netrc(), "w") as f:
            f.write(f"machine {netloc(url_div)} password pqr\n")
            f.write(f"machine *.intra password ijk\n")
        us, pw = netrc.get_username_password(url_div)
        self.assertEqual(us, "abc")
        self.assertEqual(pw, "pqr")
        us, pw = netrc.get_username_password(url_k8s)
        self.assertEqual(us, "abc")
        self.assertEqual(pw, "ijk")
    def test_323(self) -> None:
        with open(self.netrc(), "w") as f:
            f.write(f"machine {netloc(url_div)} password pqr\n")
            f.write(f"machine *.intra password ijk\n")
        us, pw = netrc.get_username_password(url_div)
        self.assertEqual(us, "testuser")
        self.assertEqual(pw, "pqr")
        us, pw = netrc.get_username_password(url_k8s)
        self.assertEqual(us, "testuser")
        self.assertEqual(pw, "ijk")
    def test_331(self) -> None:
        netrc.set_username_password("abc", "xyz")
        netrc.set_username_password("abc", "uvw")
        with open(self.netrc(), "w") as f:
            f.write(f"machine {netloc(url_div)} \n login foo  \npassword pqr\n")
            f.write(f"machine *.intra \n login foo  \npassword ijk\n")
        us, pw = netrc.get_username_password(url_div)
        self.assertEqual(us, "foo")
        self.assertEqual(pw, "pqr")
        us, pw = netrc.get_username_password(url_k8s)
        self.assertEqual(us, "foo")
        self.assertEqual(pw, "ijk")
    def test_332(self) -> None:
        netrc.set_username_password("abc", "xyz")
        netrc.set_username_password("abc", "uvw")
        with open(self.netrc(), "w") as f:
            f.write(f"machine {netloc(url_div)} \n password pqr\n")
            f.write(f"machine *.intra \n password ijk\n")
        us, pw = netrc.get_username_password(url_div)
        self.assertEqual(us, "abc")
        self.assertEqual(pw, "pqr")
        us, pw = netrc.get_username_password(url_k8s)
        self.assertEqual(us, "abc")
        self.assertEqual(pw, "ijk")
    def test_333(self) -> None:
        with open(self.netrc(), "w") as f:
            f.write(f"machine {netloc(url_div)} \n password pqr\n")
            f.write(f"machine *.intra \n password ijk\n")
        us, pw = netrc.get_username_password(url_div)
        self.assertEqual(us, "testuser")
        self.assertEqual(pw, "pqr")
        us, pw = netrc.get_username_password(url_k8s)
        self.assertEqual(us, "testuser")
        self.assertEqual(pw, "ijk")
    def test_421(self) -> None:
        netrc.set_username_password("abc", "xyz")
        netrc.set_username_password("abc", "uvw")
        with open(self.netrc(), "w") as f:
            f.write(f"machine {netloc(url_div)} login foo password pqr\n")
            f.write(f"machine {netloc(url_k8s)} alias {netloc(url_div)}\n")
            f.write(f"machine *.intra password ijk\n")
        us, pw = netrc.get_username_password(url_div)
        self.assertEqual(us, "foo")
        self.assertEqual(pw, "pqr")
        us, pw = netrc.get_username_password(url_k8s)
        self.assertEqual(us, "foo")
        self.assertEqual(pw, "pqr")  # not "ijk"
    def test_422(self) -> None:
        netrc.set_username_password("abc", "xyz")
        netrc.set_username_password("abc", "uvw")
        with open(self.netrc(), "w") as f:
            f.write(f"machine {netloc(url_div)} password pqr\n")
            f.write(f"machine {netloc(url_k8s)} alias {netloc(url_div)}\n")
            f.write(f"machine *.intra password ijk\n")
        us, pw = netrc.get_username_password(url_div)
        self.assertEqual(us, "abc")
        self.assertEqual(pw, "pqr")
        us, pw = netrc.get_username_password(url_k8s)
        self.assertEqual(us, "abc")
        self.assertEqual(pw, "pqr")  # not "ijk"
    def test_423(self) -> None:
        with open(self.netrc(), "w") as f:
            f.write(f"machine {netloc(url_div)} password pqr\n")
            f.write(f"machine {netloc(url_k8s)} alias {netloc(url_div)}\n")
            f.write(f"machine *.intra password ijk\n")
        us, pw = netrc.get_username_password(url_div)
        self.assertEqual(us, "testuser")
        self.assertEqual(pw, "pqr")
        us, pw = netrc.get_username_password(url_k8s)
        self.assertEqual(us, "testuser")
        self.assertEqual(pw, "pqr")  # not "ijk"
    def test_431(self) -> None:
        netrc.set_username_password("abc", "xyz")
        netrc.set_username_password("abc", "uvw")
        with open(self.netrc(), "w") as f:
            f.write(f"machine {netloc(dev_div)} login foo password pqr\n")
            f.write(f"machine {netloc(dev_k8s)} alias {netloc(dev_div)}\n")
            f.write(f"machine *.intra password ijk\n")
        us, pw = netrc.get_username_password(dev_div)
        self.assertEqual(us, "foo")
        self.assertEqual(pw, "pqr")
        us, pw = netrc.get_username_password(dev_k8s)
        self.assertEqual(us, "foo")
        self.assertEqual(pw, "pqr")  # not "ijk"
    def test_432(self) -> None:
        netrc.set_username_password("abc", "xyz")
        netrc.set_username_password("abc", "uvw")
        with open(self.netrc(), "w") as f:
            f.write(f"machine {netloc(dev_div)} password pqr\n")
            f.write(f"machine {netloc(dev_k8s)} alias {netloc(dev_div)}\n")
            f.write(f"machine *.intra password ijk\n")
        us, pw = netrc.get_username_password(dev_div)
        self.assertEqual(us, "abc")
        self.assertEqual(pw, "pqr")
        us, pw = netrc.get_username_password(dev_k8s)
        self.assertEqual(us, "abc")
        self.assertEqual(pw, "pqr")  # not "ijk"
    def test_433(self) -> None:
        with open(self.netrc(), "w") as f:
            f.write(f"machine {netloc(dev_div)} password pqr\n")
            f.write(f"machine {netloc(dev_k8s)} alias {netloc(dev_div)}\n")
            f.write(f"machine *.intra password ijk\n")
        us, pw = netrc.get_username_password(dev_div)
        self.assertEqual(us, "testuser")
        self.assertEqual(pw, "pqr")
        us, pw = netrc.get_username_password(dev_k8s)
        self.assertEqual(us, "testuser")
        self.assertEqual(pw, "pqr")  # not "ijk"
    def test_901(self) -> None:
        cmd = ["./netrc.py", "help"]
        out = subprocess.check_output(cmd)
        logg.info("OUT:\n%s", out)
        self.assertIn(b"x", out)
    def test_902(self) -> None:
        filename = netrc.NETRC_FILENAMES[0]
        cmd = ["./netrc.py", "help"]
        out = subprocess.check_output(cmd)
        logg.info("OUT:\n%s", out)
        self.assertIn(b"x", out)
    def test_903(self) -> None:
        filename = netrc.NETRC_FILENAMES[0]
        cmd = ["./netrc.py", "help", "--netcredentials", filename]
        out = subprocess.check_output(cmd)
        logg.info("OUT:\n%s", out)
        self.assertIn(b"x", out)
    def test_910(self) -> None:
        filename = netrc.NETRC_FILENAMES[0]
        cmd = ["./netrc.py", "--netcredentials", filename, "get", "extra.example"]
        out = subprocess.check_output(cmd)
        logg.info("OUT:\n%s", out)
        self.assertIn(b"host=extra", out)
        self.assertIn(b"username=testuser", out)
        self.assertNotIn(b"password=", out)
    def test_911(self) -> None:
        filename = netrc.NETRC_FILENAMES[0]
        cmd = ["./netrc.py", "--netcredentials", filename, "store", "extra.example", "someuser", "somepass"]
        out = subprocess.check_output(cmd)
        logg.info("OUT:\n%s", out)
        self.assertIn(b"written to", out)
        cmd = ["./netrc.py", "--netcredentials", filename, "get", "extra.example"]
        out = subprocess.check_output(cmd)
        logg.info("OUT:\n%s", out)
        self.assertIn(b"host=extra", out)
        self.assertIn(b"username=someuser", out)
        self.assertIn(b"password=somepass", out)
    def test_912(self) -> None:
        filename = netrc.NETRC_FILENAMES[0]
        cmd = ["./netrc.py", "--netcredentials", filename, "store", "extra.example", "someuser", "somepass"]
        out = subprocess.check_output(cmd)
        logg.info("OUT:\n%s", out)
        self.assertIn(b"written to", out)
        cmd = ["./netrc.py", "--netcredentials", filename, "get", "extra.example"]
        out = subprocess.check_output(cmd)
        logg.info("OUT:\n%s", out)
        self.assertIn(b"host=extra", out)
        self.assertIn(b"username=someuser", out)
        self.assertIn(b"password=somepass", out)
        cmd = ["./netrc.py", "--netcredentials", filename, "erase", "extra.example"]
        out = subprocess.check_output(cmd)
        logg.info("OUT:\n%s", out)
        self.assertIn(b"erased in", out)
        cmd = ["./netrc.py", "--netcredentials", filename, "get", "extra.example"]
        out = subprocess.check_output(cmd)
        logg.info("OUT:\n%s", out)
        self.assertIn(b"host=extra", out)
        self.assertIn(b"username=testuser", out)
        self.assertNotIn(b"password=", out)

if __name__ == "__main__":
    # logging.basicConfig(level=("-v" not in sys.argv and logging.WARNING or logging.INFO))
    # netrc.netrc_logg.setLevel(("-v" not in sys.argv and logging.INFO or logging.DEBUG))
    # unittest.main()
    from optparse import OptionParser
    cmdline = OptionParser("%prog [n_]test...")
    cmdline.add_option("-v", "--verbose", action="count", default=0)
    cmdline.add_option("--xmlresults", metavar="FILE", default=None,
        help="capture results as a junit xml file [%default]")
    opt, args = cmdline.parse_args()
    logging.basicConfig(level=max(0, logging.WARNING - 10 * opt.verbose))
    netrc.netrc_logg.setLevel(max(0, logging.INFO - 10 * opt.verbose))
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
