#! /usr/bin/env python3

__copyright__ = "(C) 2021-2024 Guido Draheim, licensed under the Apache License 2.0"""
__version__ = "0.4.3321"

from xmlrpc import client as odoo
from dotnetrc import set_password_filename, get_username_password, str_get_username_password
import sys
import os.path as path
import json

import logging
logg = logging.getLogger(__name__ == "__main__" and path.basename(sys.argv[0]) or __name__)

URL = "https://odoo.host"
DB = "prod-db" # https://o2sheet.com/docs/retrieve-odoo-database-name/

def odoo_version():
    common = odoo.ServerProxy(f'{URL}/xmlrpc/2/common')
    return common.version().get("server_version")

def odoo_schema():
    common = odoo.ServerProxy(f'{URL}/xmlrpc/2/common')
    username, password = get_username_password(URL)
    logg.info("using %s", str_username_password(username, password))
    uid = common.authenticate(DB, username, password, {})
    models = odoo.ServerProxy(f'{URL}/xmlrpc/2/object')
    logg.info("uid %s", uid)
    logg.info("models %s", models)
    r = models.execute_kw(DB, uid, password, 'ir.model', 'fields_get', [], {'attributes': ['string', 'help', 'type']})
    # r = models.execute_kw(DB, uid, password, 'ir.model.fields', 'fields_get', [], {'attributes': ['string', 'help', 'type']})
    # r = models.execute_kw(DB, uid, password, 'hr_timesheet_sheet', 'fields_get', [], {'attributes': ['string', 'help', 'type']})
    # r = models.execute_kw(DB, uid, password, 'hr_timesheet_sheet', 'search_read',[])
    logg.info("fields %s", r)

def odoo_user():
    common = odoo.ServerProxy(f'{URL}/xmlrpc/2/common')
    username, password = get_username_password(URL)
    logg.info("using %s", str_username_password(username, password))
    uid = common.authenticate(DB, username, password, {})
    models = odoo.ServerProxy(f'{URL}/xmlrpc/2/object')
    logg.info("uid %s", uid)
    logg.info("models %s", models)
    # r = models.execute_kw(DB, uid, password, 'res.users', 'search_read',[], {"limit": 5})
    r = models.execute_kw(DB, uid, password, 'hr.employee.public', 'search_read',[[["name","=","Guido Draheim"]]], {"limit": 5})
    logg.info("fields %s", json.dumps(r, indent=1))
    logg.info("user %s = %s", r[0]["name"], r[0]["id"])

def odoo_sheet():
    common = odoo.ServerProxy(f'{URL}/xmlrpc/2/common')
    username, password = get_username_password(URL)
    logg.info("using %s", str_username_password(username, password))
    uid = common.authenticate(DB, username, password, {})
    models = odoo.ServerProxy(f'{URL}/xmlrpc/2/object')
    logg.info("uid %s", uid)
    logg.info("models %s", models)
    # r = models.execute_kw(DB, uid, password, 'ir.model', 'fields_get', [], {'attributes': ['string', 'help', 'type']})
    # r = models.execute_kw(DB, uid, password, 'ir.model.fields', 'fields_get', [], {'attributes': ['string', 'help', 'type']})
    # r = models.execute_kw(DB, uid, password, 'hr_timesheet.sheet', 'fields_get', [], {'attributes': ['string', 'help', 'type']})
    # r = models.execute_kw(DB, uid, password, 'hr_timesheet.sheet.line', 'search_read',[], {"limit": 5})
    # r = models.execute_kw(DB, uid, password, 'res.users', 'search_read',[], {"limit": 5})
    r = models.execute_kw(DB, uid, password, 'hr.employee.public', 'search_read',[[["name","=","Guido Draheim"]]], {"limit": 5})
    user = r[0]["id"]
    logg.info("user %s", user)
    # r = models.execute_kw(DB, uid, password, 'account.analytic.line', 'fields_get', [], {'attributes': ['string', 'help', 'type']})
    r = models.execute_kw(DB, uid, password, 'account.analytic.line', 'search_read',[[['is_timesheet','=',True],["employee_id", "=", user]]],{"limit": 5})
    # r = models.execute_kw(DB, uid, password, 'account.analytic.line', 'search_read',[[['is_timesheet','=',True],["user_id", "=", "Guido Draheim"]]],{"limit": 5})
    logg.info("fields %s", json.dumps(r, indent=1))

def run(arg):
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
    elif arg in ["version"]:
        print(odoo_version())
    elif arg in ["scheme", "schema", "sch"]:
        print(odoo_schema())
    elif arg in ["scheet", "sh"]:
        print(odoo_sheet())
    elif arg in ["user", "me"]:
        print(odoo_user())
    else:
        log.error("unknown command '%s'", arg)

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
