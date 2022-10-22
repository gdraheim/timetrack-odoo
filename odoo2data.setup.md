## ODOO2DATA

Make sure to have the odoo login data ready in ~/.netrc

See [netrc.setup.md](netrc.setup.md) for details.

    machine erp.example.com login me@example.com password Example.2022

### SETUP

The script will pick up your user name from ~/.gitconfig

    [user]
        name = John Doe

You have probably configured that to push git commits.

### FIRST STEPS

./odoo2data.py week
./odoo2data.py week work
./odoo2data.py last days
./odoo2data.py this summary -z
./odoo2data.py help
./odoo2data.py -a 01.01. -b 31.03. report --xlsxfile report.Q1.xlsx


