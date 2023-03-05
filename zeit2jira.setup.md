## ZEIT2JIRA

This is a synchronisation program of timetrack-odoo

It can load JSONList from zeit2json. See [zeit2json.setup]([zeit2json.setup.md).

It can load records from Jira. See [jira2data.setup](jira2data.setup.md).

It can push the data to Jira with the [jira API setup](jira2data_api.setup.md).

It uses ~/.netrc for storing the login credentials to Jira. See [dotnetrc setup](dotnetrc.setup.md).

### FIRST STEPS

    ./zeit2jira.py last days
    ./zeit2jira.py this summary -z
    ./zeit2jira.py help
    ./zeit2jira.py last update

The `update` action is in --dryrun mode by default. Use `-y` to actually write to Odoo.
