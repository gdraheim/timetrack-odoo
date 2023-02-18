#! /usr/bin/make -f

BASEYEAR= 2021
FOR=today

FILES = *.py *.cfg
PYTHON3 = python3
COVERAGE3 = $(PYTHON3) -m coverage
TWINE = twine

MAIN_PROG = zeit2odoo.py
ZEIT_PROG = zeit2json.py
DATA_PROG = odoo2data.py
ODOO_APIS = odoo_rest.py
ODOO_MOCK = odoo_rest_mockup.py
ODOOTOPIC = odootopic.py
TRACKPROG = timetrack.py

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
	$(MAKE) track

x tabt: ; $(PYTHON3) $(TAB_UTILS:.py=.tests.py) -v $V
x_%: ;    $(PYTHON3) $(TAB_UTILS:.py=.tests.py) $@ -v $V

n nett: ; $(PYTHON3) $(NET_UTILS:.py=.tests.py) -v $V
n_%: ;    $(PYTHON3) $(NET_UTILS:.py=.tests.py) $@ -v $V

d dayt: ; $(PYTHON3) $(DAY_UTILS:.py=.tests.py) -v $V
d_%: ;    $(PYTHON3) $(DAY_UTILS:.py=.tests.py) $@ -v $V

o odoo: ; $(PYTHON3) $(DATA_PROG:.py=.tests.py) -v $V
o_%: ;    $(PYTHON3) $(DATA_PROG:.py=.tests.py) $@ -v $V

z zeit: ; $(PYTHON3) $(ZEIT_PROG:.py=.tests.py) -v $V
z_%: ;    $(PYTHON3) $(ZEIT_PROG:.py=.tests.py) $@ -v $V

t test: ; $(PYTHON3) $(MAIN_PROG:.py=.tests.py) -v $V
t_%: ;    $(PYTHON3) $(MAIN_PROG:.py=.tests.py) $@ -v $V

k track: ; $(PYTHON3) $(TRACKPROG:.py=.tests.py) -v $V
k_%: ;     $(PYTHON3) $(TRACKPROG:.py=.tests.py) $@ -v $V

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

TESTSUITE = $(MAIN_PROG:.py=.tests.py)

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
MYPY_STRICT = --strict --show-error-codes --show-error-context --no-warn-unused-ignores --python-version 3.6 --implicit-reexport
AUTOPEP8=autopep8
AUTOPEP8_INPLACE= --in-place

%.type:
	$(MYPY) $(MYPY_STRICT) $(MYPY_OPTIONS) $(@:.type=)

%.pep8:
	$(AUTOPEP8) $(AUTOPEP8_INPLACE) $(AUTOPEP8_OPTIONS) $(@:.pep8=)
	git --no-pager diff $(@:.pep8=)

type: 
	$(MAKE) $(PARALLEL) \
	                 $(ODOO_APIS).type $(ODOO_MOCK).type \
	                 $(ODOOTOPIC).type $(ODOOTOPIC:.py=.tests.py).type \
	                 $(MAIN_PROG).type $(MAIN_PROG:.py=.tests.py).type \
	                 $(ZEIT_PROG).type $(ZEIT_PROG:.py=.tests.py).type \
	                 $(DATA_PROG).type $(DATA_PROG:.py=.tests.py).type \
	                 $(TAB_UTILS).type $(TAB_UTILS:.py=.tests.py).type \
	                 $(NET_UTILS).type $(NET_UTILS:.py=.tests.py).type \
	                 $(DAY_UTILS).type $(DAY_UTILS:.py=.tests.py).type \
	                 $(TRACKPROG).type $(TRACKPROG:.py=.tests.py).type 

style pep8:
	$(MAKE) $(PARALLEL) \
	                 $(ODOO_APIS).pep8 $(ODOO_MOCK).pep8 \
	                 $(ODOOTOPIC).pep8 $(ODOOTOPIC:.py=.tests.py).pep8 \
	                 $(MAIN_PROG).pep8 $(MAIN_PROG:.py=.tests.py).pep8 \
	                 $(ZEIT_PROG).pep8 $(ZEIT_PROG:.py=.tests.py).pep8 \
	                 $(DATA_PROG).pep8 $(DATA_PROG:.py=.tests.py).pep8 \
	                 $(TAB_UTILS).pep8 $(TAB_UTILS:.py=.tests.py).pep8 \
	                 $(NET_UTILS).pep8 $(NET_UTILS:.py=.tests.py).pep8 \
	                 $(DAY_UTILS).pep8 $(DAY_UTILS:.py=.tests.py).pep8 \
	                 $(TRACKPROG).pep8 $(TRACKPROG:.py=.tests.py).pep8 
