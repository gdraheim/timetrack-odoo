#! /usr/bin/env python3

__copyright__ = "(C) 2021-2024 Guido Draheim, licensed under the Apache License 2.0"""
__version__ = "0.4.3361"

from typing import Any, Dict, List
from dotnetrc import set_password_filename, get_username_password, str_get_username_password, str_username_password
import sys
import os.path as path
import json
import urllib.request
import random
from dotgitconfig import git_config_value

import logging
logg = logging.getLogger(__name__ == "__main__" and path.basename(sys.argv[0]) or __name__)

ODOO_URL = ""
ODOO_DB = ""
ODOO_USERNAME = ""


# https://www.odoo.com/documentation/master/developer/howtos/web_services.html
def json_rpc(url: str, method: str, params: Any) -> Any:
    data = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": random.randint(0, 1000000000),
    }
    req = urllib.request.Request(url=url, data=json.dumps(data).encode(), headers={
        "Content-Type":"application/json",
    })
    reply = json.loads(urllib.request.urlopen(req).read().decode('UTF-8'))
    if reply.get("error"):
        raise Exception(reply["error"])
    return reply["result"]

def call(url: str, service: str, method: str, *args: Any):
    return json_rpc(url, "call", {"service": service, "method": method, "args": args})

def odoo_username() -> str:
    """ see https://o2sheet.com/docs/retrieve-odoo-database-name/ """
    if ODOO_USERNAME:
        return ODOO_USERNAME
    value = git_config_value("user.name")
    if value:
        return value
    return "Max Mustermann"

def odoo_url() -> str:
    if ODOO_URL:
        return ODOO_URL
    value = git_config_value("odoo.url")
    if value:
        return value
    value = git_config_value("zeit.url")
    if value:
        return value
    return "https://example.odoo.com"

def odoo_db() -> str:
    """ see https://o2sheet.com/docs/retrieve-odoo-database-name/ """
    if ODOO_DB:
        return ODOO_DB
    value = git_config_value("odoo.db")
    if value:
        return value
    value = git_config_value("zeit.db")
    if value:
        return value
    return "prod-example"

def odoo_login() -> int:
    url = odoo_url() + "/jsonrpc"
    username, password = get_username_password(url)
    logg.info("using %s", str_username_password(username, password))
    db = odoo_db()
    uid = call(url, "common", "login", db, username, password)
    return uid

def odoo_version() -> str:
    uid = odoo_login()
    url = odoo_url() + "/jsonrpc"
    info = call(url, "common", "version")
    return info.get("server_version")

def odoo_schema() -> Dict[str, str]:
    uid = odoo_login()
    url = odoo_url() + "/jsonrpc"
    db = odoo_db()
    username, password = get_username_password(url)
    info = call(url, "object", "execute", db, uid, password, "ir.model", "fields_get", [], ['string', 'help', 'type'])
    return info

def odoo_userschema() -> List[str]:
    uid = odoo_login()
    url = odoo_url() + "/jsonrpc"
    db = odoo_db()
    username, password = get_username_password(url)
    info = call(url, "object", "execute", db, uid, password, "hr.employee.public", "fields_get", [], ['string', 'type'])
    view = [ "%s:%s" % (name, info[name]['type']) for name in sorted(info)]
    return view

def odoo_user() -> List[Dict[str, Any]]:
    uid = odoo_login()
    url = odoo_url() + "/jsonrpc"
    db = odoo_db()
    username, password = get_username_password(url)
    name = odoo_username()
    info = call(url, "object", "execute", db, uid, password, "hr.employee.public", "search_read", [["name","=",name]], ['id', 'name', 'work_email','active'])
    return info

def odoo_user_id() -> int:
    return odoo_user()[0]["id"]

def odoo_sheetschema() -> List[str]:
    uid = odoo_login()
    url = odoo_url() + "/jsonrpc"
    db = odoo_db()
    username, password = get_username_password(url)
    info = call(url, "object", "execute", db, uid, password, "account.analytic.line", "fields_get", [], ['string', 'type'])
    view = [ "%s:%s" % (name, info[name]['type']) for name in sorted(info)]
    return view

def odoo_sheet() -> List[Dict[str, Any]]:
    user = odoo_user_id()
    logg.info("user %s", user)
    uid = odoo_login()
    url = odoo_url() + "/jsonrpc"
    db = odoo_db()
    username, password = get_username_password(url)
    info = call(url, "object", "execute", db, uid, password, "account.analytic.line", "search_read", [["employee_id","=",user],['is_timesheet','=',True]],['duration_unit_amount','project_id','task_id','unit_amount','date','name'])
    logg.info("fields %s", info)
    return info

def run(arg: str) -> None:
    if arg in ["help"]:
        cmdline.print_help()
        print("\nCommands:")
        previous = ""
        for line in open(__file__):
            if previous.strip().replace("elif arg", "if arg").startswith("if arg in"):
                if "#" in line:
                    print(previous.strip().split(" arg in")[1], line.strip().split("#")[1])
                else:
                    print(previous.strip().split(" arg in")[1], line.strip())
            previous = line
        raise SystemExit()
    elif arg in ["login"]:
        print(odoo_login())
    elif arg in ["version"]:
        print(odoo_version())
    elif arg in ["scheme", "schema", "irxx"]:
        print(odoo_schema())
    elif arg in ["sheetschema", "shxx"]:
        print(odoo_sheetschema())
    elif arg in ["sheet", "sh"]:
        print(odoo_sheet())
    elif arg in ["userschema", "mexx"]:
        print(odoo_userschema())
    elif arg in ["user", "me"]:
        print(odoo_user())
    else:
        logg.error("unknown command '%s'", arg)

if __name__ == "__main__":
    from optparse import OptionParser
    cmdline = OptionParser("%prog [-options] [help|commands...]", version=__version__)
    cmdline.add_option("-v", "--verbose", action="count", default=0, help="more verbose logging")
    cmdline.add_option("-^", "--quiet", action="count", default=0, help="less verbose logging")
    cmdline.add_option("-g", "--gitcredentials", metavar="FILE", default="~/.netrc")
    opt, args = cmdline.parse_args()
    logging.basicConfig(level = max(0, logging.WARNING - 10 * opt.verbose + 10 * opt.quiet))
    set_password_filename(opt.gitcredentials)
    for arg in args:
        run(arg)
