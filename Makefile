#! /usr/bin/make -f

BASEYEAR= 2021
FOR=today

FILES = *.py *.cfg
PYTHON3 = python3
COVERAGE3 = $(PYTHON3) -m coverage
TWINE = twine

SCRIPT = zeit2odoo.py
TESTSUITE = zeit2odoo.tests.py
GENSCRIPT = zeit2json.py
GEN_TESTS = zeit2json.tests.py
DATSCRIPT = odoo2data.py
DAT_TESTS = odoo2data.tests.py
APISCRIPT = odoo_rest.py
# API_TESTS = odoo_tests.tests.py
API_TESTS = odoo_rest_mockup.py

DAY_UTILS = dayrange.py
DAY_TESTS = dayrange.tests.py
NET_UTILS = netrc.py
NET_TESTS = netrc.tests.py
TAB_UTILS = tabtotext.py
TAB_TESTS = tabtotext.tests.py
TAB_XLSX = tabtoxlsx.py

PARALLEL = -j2

default: help

check:
	$(MAKE) tabt
	$(MAKE) nett
	$(MAKE) dayt
	$(MAKE) odoo
	$(MAKE) zeit
	$(MAKE) test

x tabt:
	$(PYTHON3) $(TAB_TESTS) -v $V
x_%:
	$(PYTHON3) $(TAB_TESTS) $@ -v $V

n nett:
	$(PYTHON3) $(NET_TESTS) -v $V
n_%:
	$(PYTHON3) $(NET_TESTS) $@ -v $V

d dayt:
	$(PYTHON3) $(DAY_TESTS) -v $V
d_%:
	$(PYTHON3) $(DAY_TESTS) $@ -v $V

o odoo:
	$(PYTHON3) $(DAT_TESTS) -v $V
o_%:
	$(PYTHON3) $(DAT_TESTS) $@ -v $V

z zeit:
	$(PYTHON3) $(GEN_TESTS) -v $V
z_%:
	$(PYTHON3) $(GEN_TESTS) $@ -v $V

t test:
	$(PYTHON3) $(TESTSUITE) -v $V
t_%:
	$(PYTHON3) $(TESTSUITE) $@ -v $V

####################################################################################

version1:
	@ grep -l __version__ $(FILES) | { while read f; do echo $$f; done; } 

version:
	@ grep -l __version__ $(FILES) | { while read f; do : \
	; THISYEAR=`date +%Y -d "$(FOR)"` ; YEARS=$$(expr $$THISYEAR - $(BASEYEAR)) \
        ; WEEKnDAY=`date +%W%u -d "$(FOR)"` ; sed -i \
	-e "/^version /s/[.]-*[0123456789][0123456789][0123456789]*/.$$YEARS$$WEEKnDAY/" \
	-e "/^ *__version__/s/[.]-*[0123456789][0123456789][0123456789]*\"/.$$YEARS$$WEEKnDAY\"/" \
	-e "/^ *__version__/s/[.]\\([0123456789]\\)\"/.\\1.$$YEARS$$WEEKnDAY\"/" \
	-e "/^ *__copyright__/s/(C) [0123456789]*-[0123456789]*/(C) $(BASEYEAR)-$$THISYEAR/" \
	-e "/^ *__copyright__/s/(C) [0123456789]* /(C) $$THISYEAR /" \
	$$f; done; }
	@ grep ^__version__ $(FILES)

help:
	$(PYTHON3) $(SCRIPT) --help

tests: ;  $(PYTHON3) $(TESTSUITE) -vvv $(TESTFLAGS)
test_%: ; $(PYTHON3) $(TESTSUITE) -vvv $(TESTFLAGS) $@

ests: ;  $(COVERAGE3) run $(TESTSUITE) -vvv $(TESTFLAGS)
est_%: ; $(COVERAGE3) run $(TESTSUITE) -vvv $(TESTFLAGS) t$@

COVERAGEFILES = $(SCRIPT)
cov coverage: 
	$(COVERAGE3) erase 
	$(MAKE) ests 
	$(COVERAGE3) xml $(COVERAGEFLAGS) $(COVERAGEFILES)
	$(COVERAGE3) annotate $(COVERAGEFLAGS) $(COVERAGEFILES)
	$(COVERAGE3) report $(COVERAGEFLAGS) $(COVERAGEFILES)
	@ wc -l $(SCRIPT),cover | sed -e "s/^\\([^ ]*\\)  *\\(.*\\)/\\2      \\1 lines/"


clean:
	- rm *.pyc 
	- rm -rf *.tmp
	- rm -rf tmp tmp.files
	- rm TEST-*.xml
	- rm setup.py README
	- rm -rf build dist *.egg-info

############## https://pypi.org/...

README: README.md Makefile
	cat README.md | sed -e "/\\/badge/d" > README
setup.py: Makefile
	{ echo '#!/usr/bin/env python3' \
	; echo 'import setuptools' \
	; echo 'setuptools.setup()' ; } > setup.py
	chmod +x setup.py
setup.py.tmp: Makefile
	echo "import setuptools ; setuptools.setup()" > setup.py

.PHONY: build
build:
	rm -rf build dist *.egg-info
	$(MAKE) $(PARALLEL) README setup.py
	# pip install --root=~/local . -v
	$(PYTHON3) setup.py sdist
	- rm -v setup.py README
	$(TWINE) check dist/*
	: $(TWINE) upload dist/*

tar:
	- rm -f ../timetrack-odoo-20*.tgz
	tar czvf ../timetrack-odoo-`date -I`.tgz *.py *.md *.cfg LICENSE
	@ ls -sh ../timetrack-odoo-`date -I`.tgz

txt:
	for i in *.py; do cp -v $$i ../tmp.$$i.txt; done
# ------------------------------------------------------------

mypy:
	zypper install -y mypy
	zypper install -y python3-click python3-pathspec

MYPY = mypy
MYPY_STRICT = --strict --show-error-codes --show-error-context --no-warn-unused-ignores --python-version 3.6
AUTOPEP8=autopep8
AUTOPEP8_INPLACE= --in-place

type: 
	$(MAKE) $(PARALLEL) $(SCRIPT).type $(TESTSUITE).type \
	                 $(GENSCRIPT).type $(GEN_TESTS).type \
	                 $(DATSCRIPT).type $(DAT_TESTS).type \
	                 $(TAB_UTILS).type $(TAB_TESTS).type \
	                 $(NET_UTILS).type $(NET_TESTS).type \
	                 $(DAY_UTILS).type $(DAY_TESTS).type

%.type:
	$(MYPY) $(MYPY_STRICT) $(MYPY_OPTIONS) $(@:.type=)

%.pep:
	$(AUTOPEP8) $(AUTOPEP8_INPLACE) $(AUTOPEP8_OPTIONS) $(@:.pep=)
	git --no-pager diff $(@:.pep=)

pep:
	$(MAKE) $(PARALLEL) $(SCRIPT).pep $(TESTSUITE).pep \
	                 $(GENSCRIPT).pep $(GEN_TESTS).pep \
	                 $(DATSCRIPT).pep $(DAT_TESTS).pep \
	                 $(TAB_UTILS).pep $(TAB_TESTS).pep \
	                 $(NET_UTILS).pep $(NET_TESTS).pep \
	                 $(DAY_UTILS).pep $(DAY_TESTS).pep
