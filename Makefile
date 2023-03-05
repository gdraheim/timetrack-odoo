#! /usr/bin/make -f

BASEYEAR=2021
FOR=today

FILES = *.py *.cfg
PYTHON3 = python3
COVERAGE3 = $(PYTHON3) -m coverage
TWINE = twine

MAIN_PROG = zeit2odoo.py
ZEIT_PROG = zeit2json.py
DATA_PROG = odoo2data.py
ODOO_APIS = odoo2data_api.py
ODOO_MOCK = odoo2data_api_mockup.py
ODOOTOPIC = odootopic.py
JIRA_PROG = jira2data.py
JIRA_APIS = jira2data_api.py
JIRA_MOCK = jira2data_api_mockup.py
JIRA_ZEIT = zeit2jira.py
TRACKPROG = timetrack.py

TAB_TOOLS = tabtools.py
DAY_UTILS = dayrange.py
NET_UTILS = netrc.py
TAB_TOOLS = tabtools.py
TAB_UTILS = tabtotext.py
TAB_2XLSX = tabtoxlsx.py

PARALLEL = -j2

default: help

check:
	$(MAKE) frac
	$(MAKE) tabt
	$(MAKE) nett
	$(MAKE) dayt
	$(MAKE) topt
	$(MAKE) odoo
	$(MAKE) zeit
	$(MAKE) test
	$(MAKE) jira
	$(MAKE) track

tests:
	$(MAKE) f.frac
	$(MAKE) x.tabt
	$(MAKE) n.nett
	$(MAKE) d.dayt
	$(MAKE) r.topt
	$(MAKE) o.odoo
	$(MAKE) z.zeit
	$(MAKE) t.test
	$(MAKE) j.jira
	: $(MAKE) k.track
	wc -l TEST-*.xml

tabtools.tests: frac
f.frac: ; $(PYTHON3) $(TAB_TOOLS:.py=.tests.py) -v $V  --xmlresults=TEST-$@.xml
f frac: ; $(PYTHON3) $(TAB_TOOLS:.py=.tests.py) -v $V
f_%: ;    $(PYTHON3) $(TAB_TOOLS:.py=.tests.py) $@ -v $V

tabtotext.tests: tabt
x.tabt: ; $(PYTHON3) $(TAB_UTILS:.py=.tests.py) -v $V  --xmlresults=TEST-$@.xml
x tabt: ; $(PYTHON3) $(TAB_UTILS:.py=.tests.py) -v $V
x_%: ;    $(PYTHON3) $(TAB_UTILS:.py=.tests.py) $@ -v $V

netrc.tests: nett
n.nett: ; $(PYTHON3) $(NET_UTILS:.py=.tests.py) -v $V  --xmlresults=TEST-$@.xml
n nett: ; $(PYTHON3) $(NET_UTILS:.py=.tests.py) -v $V
n_%: ;    $(PYTHON3) $(NET_UTILS:.py=.tests.py) $@ -v $V

dayrange.tests: dayt
d.dayt: ; $(PYTHON3) $(DAY_UTILS:.py=.tests.py) -v $V  --xmlresults=TEST-$@.xml
d dayt: ; $(PYTHON3) $(DAY_UTILS:.py=.tests.py) -v $V
d_%: ;    $(PYTHON3) $(DAY_UTILS:.py=.tests.py) $@ -v $V

odootopic.tests: topt
r.topt: ; $(PYTHON3) $(ODOOTOPIC:.py=.tests.py) -v $V  --xmlresults=TEST-$@.xml
r topt: ; $(PYTHON3) $(ODOOTOPIC:.py=.tests.py) -v $V
r_%: ;    $(PYTHON3) $(ODOOTOPIC:.py=.tests.py) $@ -v $V

odoo2data.tests: odoo
o.odoo: ; $(PYTHON3) $(DATA_PROG:.py=.tests.py) -v $V  --xmlresults=TEST-$@.xml
o odoo: ; $(PYTHON3) $(DATA_PROG:.py=.tests.py) -v $V
o_%: ;    $(PYTHON3) $(DATA_PROG:.py=.tests.py) $@ -v $V

zeit2json.tests: zeit
z.zeit: ; $(PYTHON3) $(ZEIT_PROG:.py=.tests.py) -v $V  --xmlresults=TEST-$@.xml
z zeit: ; $(PYTHON3) $(ZEIT_PROG:.py=.tests.py) -v $V
z_%: ;    $(PYTHON3) $(ZEIT_PROG:.py=.tests.py) $@ -v $V

zeit2odoo.tests: test
t.test: ; $(PYTHON3) $(MAIN_PROG:.py=.tests.py) -v $V  --xmlresults=TEST-$@.xml
t test: ; $(PYTHON3) $(MAIN_PROG:.py=.tests.py) -v $V
t_%: ;    $(PYTHON3) $(MAIN_PROG:.py=.tests.py) $@ -v $V

zeit2jira.tests: jira
j.jira: ; $(PYTHON3) $(JIRA_ZEIT:.py=.tests.py) -v $V  --xmlresults=TEST-$@.xml
j jira: ; $(PYTHON3) $(JIRA_ZEIT:.py=.tests.py) -v $V
j_%: ;    $(PYTHON3) $(JIRA_ZEIT:.py=.tests.py) $@ -v $V

timetrack.tests: track
k.track: ; $(PYTHON3) $(TRACKPROG:.py=.tests.py) -v $V --xmlresults=TEST-$@.xml
k track: ; $(PYTHON3) $(TRACKPROG:.py=.tests.py) -v $V
k_%: ;     $(PYTHON3) $(TRACKPROG:.py=.tests.py) $@ -v $V

####################################################################################
verfiles:
	@ grep -l __version__ $(FILES) | grep -v .tests.py | { while read f; do echo $$f; done; } 

version:
	@ grep -l __version__ $(FILES) | { while read f; do : \
	; THISYEAR=`date +%Y -d "$(FOR)"` ; YEARS=$$(expr $$THISYEAR - $(BASEYEAR)) \
        ; WEEKnDAY=`date +%W%u -d "$(FOR)"` ; sed -i \
	-e "/^version /s/[.]-*[0123456789][0123456789][0123456789]*/.$$YEARS$$WEEKnDAY/" \
	-e "/^ *__version__/s/[.]-*[0123456789][0123456789][0123456789]*\"/.$$YEARS$$WEEKnDAY\"/" \
	-e "/^ *__version__/s/[.]\\([0123456789]\\)\"/.\\1.$$YEARS$$WEEKnDAY\"/" \
	-e "/^ *__copyright__/s/(C) \\([123456789][0123456789]*\\)-[123456789][0123456789]*/(C) \\1-$$THISYEAR/" \
	-e "/^ *__copyright__/s/(C) [123456789][0123456789]* /(C) $$THISYEAR /" \
	$$f; done; }
	@ grep ^__version__ $(FILES) | grep -v .tests.py
	@ ver=`cat $(MAIN_PROG) | sed -e '/__version__/!d' -e 's/.*= *"//' -e 's/".*//' -e q` \
	; echo "# $(GIT) commit -m v$$ver"

TESTSUITE = $(MAIN_PROG:.py=.tests.py)

help:
	$(PYTHON3) $(SCRIPT) --help

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

txt: ; for i in *.py; do cp -v $$i ../tmp.$$i.txt; done
tab: ; for i in tab*.py frac*.py; do cp -v $$i ../tmp.$$i.txt; done
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
	                 $(TAB_TOOLS).type $(TAB_TOOLS:.py=.tests.py).type \
	                 $(TAB_UTILS).type $(TAB_UTILS:.py=.tests.py).type \
	                 $(TAB_2XLSX).type \
	                 $(NET_UTILS).type $(NET_UTILS:.py=.tests.py).type \
	                 $(DAY_UTILS).type $(DAY_UTILS:.py=.tests.py).type \
	                 $(JIRA_PROG).type $(JIRA_APIS).type $(JIRA_MOCK).type \
	                 $(JIRA_ZEIT).type $(JIRA_ZEIT:.py=.tests.py).type \
	                 $(TRACKPROG).type $(TRACKPROG:.py=.tests.py).type 

style pep8:
	$(MAKE) $(PARALLEL) \
	                 $(ODOO_APIS).pep8 $(ODOO_MOCK).pep8 \
	                 $(ODOOTOPIC).pep8 $(ODOOTOPIC:.py=.tests.py).pep8 \
	                 $(MAIN_PROG).pep8 $(MAIN_PROG:.py=.tests.py).pep8 \
	                 $(ZEIT_PROG).pep8 $(ZEIT_PROG:.py=.tests.py).pep8 \
	                 $(DATA_PROG).pep8 $(DATA_PROG:.py=.tests.py).pep8 \
	                 $(TAB_TOOLS).pep8 $(TAB_TOOLS:.py=.tests.py).pep8 \
	                 $(TAB_UTILS).pep8 $(TAB_UTILS:.py=.tests.py).pep8 \
	                 $(TAB_2XLSX).pep8 \
	                 $(NET_UTILS).pep8 $(NET_UTILS:.py=.tests.py).pep8 \
	                 $(DAY_UTILS).pep8 $(DAY_UTILS:.py=.tests.py).pep8 \
	                 $(JIRA_PROG).pep8 $(JIRA_APIS).pep8 \
	                 $(JIRA_ZEIT).pep8 $(JIRA_ZEIT:.py=.tests.py).pep8 \
	                 $(TRACKPROG).pep8 $(TRACKPROG:.py=.tests.py).pep8 
