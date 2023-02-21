## ZEIT2ODOO

This is a synchronisatoin program of timetrack-odoo

It can load JSONList from zeit2json. See [zeit2json.setup](zeit2json.setup.md).

It can load records from Odoo. See [odoo2data.setup](odoo2data.setup.md).

It can push the data to Odoo with odoo_rest API

It uses ~/.netrc for storing the login credentials to Odoo.

### FIRST STEPS

    ./zeit2odoo.py last days
    ./zeit2odoo.py this summary -z
    ./zeit2odoo.py help
    ./zeit2odoo.py last sync
    ./zeit2odoo.py last update

The `update` action is in --dryrun mode by default. Use `-y` to actually write to Odoo.


