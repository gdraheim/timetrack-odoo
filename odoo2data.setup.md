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

./odoo2data week
./odoo2data week work
./odoo2data last days
./odoo2data this summary
./odoo2data -a 01.01. -b 31.03. report --xlsxfile report.Q1.xlsx

