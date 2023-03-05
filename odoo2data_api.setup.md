## ODOO API

The odoo2data_api implementation uses examples taken from Patrick Hobusch's project

* https://packagegalaxy.com/python/odoo-otter
* https://github.com/pathob/odoo-otter

Specifically it uses the routines from "./otter/odoo/rest.py"

It is however wrapped into "class Odoo" which can store data like target URL
and which allows to create a mockup-class for testing.

While working with the routines a few more variants did emerge which are similar
in style to the search/create routines but they allow write/update of odoo 
timesheet records.

### SETUP

The easiest way is to edit your ~/.gitconfig

    [odoo]
       url = https://mycompany.odoo.com
       db = prod-mycompany

The run

    ./odoo2data_api.py projects
