#! /usr/bin/python3

from xmlrpc import client as odoo
from netrc import *
import sys
import os.path as path
import json

import logging
logg = logging.getLogger(__name__ == "__main__" and path.basename(sys.argv[0]) or __name__)

URL = "https://erp.aservo.com"
DB = "prod-aservo" # https://o2sheet.com/docs/retrieve-odoo-database-name/

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
    if arg in ["version"]:
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
    cmdline = OptionParser("%prog [options] command...")
    cmdline.add_option("-g", "--gitcredentials", metavar="FILE", default="~/.netrc")
    cmdline.add_option("-v", "--verbose", action="count", default=0)
    opt, args = cmdline.parse_args()
    logging.basicConfig(level = logging.WARNING - 10 * opt.verbose)
    set_password_filename(opt.gitcredentials)
    for arg in args:
        run(arg)
