#! /usr/bin/python3

from typing import List, Dict, Union, Optional, Tuple, Iterator, Iterable, cast

import logging
import re
import csv
import datetime
import os.path as path

import tabtotext
from tabtotext import JSONList, JSONDict, JSONItem
from dayrange import get_date, Day
from collections import namedtuple

OdooValues = namedtuple("OdooValues", ["proj", "task", "pref", "ticket"])

logg = logging.getLogger("odootopics")

# format to map a topic to the proj/task
_zeit_topics_mapping = """
>> odoo [GUIDO (Private Investigations)]
>> odoo "Odoo Automation",
"""

class OdooValuesForTopic:
    prefixed: Dict[str, str]
    customer: Dict[str, str]
    projects: Dict[str, str]
    proj_ids: Dict[str, str]  # obsolete
    custname: Dict[str, str]
    projname: Dict[str, str]
    ticket4: Dict[str, List[str]]
    shortnames: bool
    def __init__(self, shortnames: bool = False) -> None:
        self.shortnames = shortnames
        self.prefixed = {}  # zeit-topic to odoo description-prefix
        self.customer = {}  # called "Project" in Odoo
        self.projects = {}  # called "Task" in Odoo
        self.custname = {}  # a shorthand for "Project" in Odoo
        self.projname = {}  # a shorthand for "Task" in Odoo
        self.proj_ids = {}  # obsolete - used for old Odoo to generate foreign-refkey
        self.ticket4 = {}  # allow to sync to jira trackers as well
        self.as_prefixed = re.compile(r'^(\S+)\s+=\s*(\S+)')
        self.as_customer = re.compile(r'^(\S+)\s+\[(.*)\](.*)')
        self.as_project0 = re.compile(r'^(\S+)\s+["](AS-(\d+):.*)["](.*)')  # obsolete
        self.as_project1 = re.compile(r'^(\S+)\s+["](.*)["](.*)')
        self.as_project2 = re.compile(r'^(\S+)\s+(\w[\w-]*\w):\s+["](.*)["](.*)')
        self.as_ticket1 = re.compile(r'^(\S+)\s+(\w[\w-]*\w):?\s*$')
        self.as_ticket2 = re.compile(r'^(\S+)\s+(\w[\w-]*\w):\s+(\w.*)')
        self.as_ticket3 = re.compile(r'^(\S+)\s+(\w[\w-]*\w)\s+(\w.*)')

    def scanline(self, line: str) -> None:
        """ expecting a line with >> first two chars, 
            followed by topic name, then definitions to be stored"""
        check = False
        m = self.as_prefixed.match(line[2:].strip())
        if m:
            self.prefixed[m.group(1)] = m.group(2)
            return
        m = self.as_customer.match(line[2:].strip())
        if m:
            if check: logg.error("customer %s", line)
            self.customer[m.group(1)] = m.group(2)
            self.customer[m.group(1).upper()] = m.group(2)
            self.projects[m.group(1)] = ""  # empty is always allowed (as of 2021)
            self.projects[m.group(1).upper()] = ""
            shorthand = m.group(3).strip().replace("#", ":")
            if shorthand:
                self.custname[m.group(2)] = shorthand
            return
        m = self.as_project0.match(line[2:].strip())
        if m:
            if check: logg.error("project0 %s", line)
            self.projects[m.group(1)] = m.group(2)
            self.proj_ids[m.group(1)] = m.group(3)  # obsolete
            shorthand = m.group(4).strip().replace("#", ":")
            if not shorthand: shorthand = m.group(2)
            self.projname[m.group(1)] = shorthand
            return
        m = self.as_project1.match(line[2:].strip())
        if m:
            if check: logg.error("project1 %s", line)
            self.projects[m.group(1)] = m.group(2)
            shorthand = m.group(3).strip().replace("#", ":")
            if not shorthand: shorthand = m.group(2)
            self.projname[m.group(1)] = shorthand
            return
        m = self.as_project2.match(line[2:].strip())
        if m:
            if check: logg.error("project2 %s", line)
            self.projects[m.group(1)] = m.group(3)
            self.proj_ids[m.group(1)] = m.group(2)  # obsolete
            shorthand = m.group(4).strip().replace("#", ":")
            if not shorthand: shorthand = m.group(3)
            self.projname[m.group(1)] = shorthand
            self.ticket4[m.group(1)] = [m.group(2)]  # repurpose
            return
        m = self.as_ticket1.match(line[2:].strip())
        if m:
            if check: logg.error("ticket1 %s", line)
            self.ticket4[m.group(1)] = [m.group(2)]
            return
        m = self.as_ticket2.match(line[2:].strip())
        if m:
            if check: logg.error("ticket2 %s", line)
            self.ticket4[m.group(1)] = [m.group(2)]
            self.projname[m.group(1)] = m.group(3)
            return
        m = self.as_ticket3.match(line[2:].strip())
        if m:
            if check: logg.error("ticket3 %s", line)
            self.ticket4[m.group(1)] = [m.group(2)] + m.group(3).split(" ")
            return
        if check:
            raise Exception("can not parse %s", line.strip())
        logg.error("??? %s", line)
    def lookup(self, topic: str, daydate: Optional[Day] = None) -> Optional[OdooValues]:
        """ from a topic try to find the odoo values to be used. """
        prefix = topic
        # if desc.strip().startswith(":"):
        # desc = topic
        if topic[-1] not in "0123456789" and len(topic) > 4:
            prefix = topic
        elif topic in self.prefixed:
            prefix = self.prefixed[topic]
        ticket = None
        proj = topic
        if proj in self.ticket4:
            ticket = self.ticket4[proj][0]
        if proj not in self.projects and proj[-1] in "0123456789" and proj[:-1] in self.projects:
            numm = int(proj[-1])
            proj = proj[:-1]
            if proj[-1] in [".", "-"]:
                proj = proj[:-1]
            if not ticket and proj in self.ticket4:
                if numm and numm <= len(self.ticket4[proj]):
                    ticket = self.ticket4[proj][numm - 1]
                else:
                    ticket = self.ticket4[proj][0]
        if proj not in self.projects and '-' in proj and proj[:proj.index('-')] in self.projects:
            proj = proj[:proj.index('-')]
            if not ticket and proj in self.ticket4:
                ticket = self.ticket4[proj][0]
        if proj not in self.projects:
            logg.info("can not find odoo values for %s [%s]", topic, proj)
            if not ticket and proj[-1] in "0123456789" and proj[:-1] in self.ticket4:
                numm = int(proj[-1])
                proj = proj[:-1]
                if numm and numm <= len(self.ticket4[proj]):
                    ticket = self.ticket4[proj][numm - 1]
                else:
                    ticket = self.ticket4[proj][0]
            if not ticket:
                return None
            itemPref = prefix
            itemTask = ticket
            itemProj = ticket.split("-", 1)[0]
        else:
            itemPref = prefix
            itemProj = self.customer[proj]
            itemTask = self.projects[proj]
        if self.shortnames:
            if self.customer[proj] in self.custname:
                itemProj = self.custname[self.customer[proj]]
            if proj in self.projname:
                itemTask = self.projname[proj]
        return OdooValues(itemProj, itemTask, itemPref, ticket)
    def values(self, issue: str) -> List[OdooValues]:
        data: Dict[Tuple[str, str], OdooValues] = {}
        for proj, tickets in self.ticket4.items():
            for ticket in tickets:
                if ticket == issue:
                    prefix = proj
                    if proj not in self.projects and proj[-1] in "0123456789" and proj[:-1] in self.projects:
                        numm = int(proj[-1])
                        proj = proj[:-1]
                        if proj[-1] in [".", "-"]:
                            proj = proj[:-1]
                    itemProj = self.customer[proj]
                    itemTask = self.projects[proj]
                    value = OdooValues(itemProj, itemTask, prefix, ticket)
                    key = (itemProj, itemTask)
                    data[key] = value
        return list(data.values())

def scanning(lines: Iterable[str]) -> OdooValuesForTopic:
    """ fast way of topics scanning: `x = scanning(open(filename))` """
    odoomap = OdooValuesForTopic()
    for numbered, nextline in enumerate(lines):
        line = nextline.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith(">>"):
            odoomap.scanline(line)
            continue
        if line.startswith("--"):
            if line in ["--short", "--nolong"]:
                odoomap.shortnames = True
            if line in ["--noshort", "--long"]:
                odoomap.shortnames = False
    return odoomap

def mapping(lines: Iterable[str]) -> Iterator[JSONDict]:
    """ fast way of scan and test - see our.tests.py """
    odoomap = OdooValuesForTopic()
    for numbered, nextline in enumerate(lines):
        line = nextline.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith(">>"):
            odoomap.scanline(line)
            continue
        if line.startswith(".."):
            m = re.match(r"[.]*\s(\S+)(?:\s+(\S+))?(.*)", line)
            if not m:
                logg.error("can not parse query: %s", line.strip())
                continue
            ontopic = m.group(1)
            ondate = None
            if m.group(2):
                ondate = get_date(m.group(2))
            found = odoomap.lookup(ontopic, ondate)
            item: JSONDict = {"line": numbered + 1, "ontopic": ontopic, "ondate": ondate}
            if found:
                item["pref"] = found.pref
                item["proj"] = found.proj
                item["task"] = found.task
                item["ticket"] = found.ticket
            yield item
            continue
        if line.startswith("--"):
            if line in ["--short", "--nolong"]:
                odoomap.shortnames = True
            if line in ["--noshort", "--long"]:
                odoomap.shortnames = False
        logg.error("did not recognize line: %s", line)
        logg.debug("lines must start with either '>>' or '..'")

def run(filename: str) -> None:
    results = mapping(open(filename))
    print(tabtotext.tabToGFM(list(results)))

if __name__ == "__main__":
    from optparse import OptionParser
    cmdline = OptionParser("%prog files...")
    cmdline.add_option("-v", "--verbose", action="count", default=0,
                       help="more verbose logging")
    cmdline.add_option("-a", "--after", metavar="DATE", default="",
                       help="only evaluate entrys on and after [first of year]")
    cmdline.add_option("-b", "--before", metavar="DATE", default="",
                       help="only evaluate entrys on and before [last of year]")
    cmdline.add_option("-f", "--filename", metavar="TEXT", default="",
                       help="choose input filename [may be path/zeit{YEAR}.txt]")
    opt, args = cmdline.parse_args()
    logging.basicConfig(level=max(0, logging.WARNING - 10 * opt.verbose))
    logg.setLevel(level=max(0, logging.WARNING - 10 * opt.verbose))
    #
    import zeit2json
    zeit2json.ZEIT_FILENAME = opt.filename
    zeit2json.ZEIT_AFTER = opt.after
    zeit2json.ZEIT_BEFORE = opt.before
    if not args:
        args = [zeit2json.get_zeit_filename()]
        logg.info(" %s ", args)
    for arg in args:
        run(arg)
