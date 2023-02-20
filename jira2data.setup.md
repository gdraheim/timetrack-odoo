## SETUP

### gitconfig

Edit your ~/.gitconfig 

    [jira]
        url= https://jira.host

You can manage multiple jira instances by having different sections in gitconfig.

    [jiradev]
        url= https://jiradev.host

and select a different `--remote` with each script.

    ./jira2data.py -r jiradev

### credentials

    ./netrc.py set https://jira.host myself Example.2022

### check jira

If you have a Jira to copy worklogs to.

    ./jira2data.py help
    ./jira2data.py tickets
    | SAND-4 | 17863   | Task      | SAND  | testing timetrack

### synchronize to jira

With the zeit2022.txt ready, you can check if there is anything
to be updated in Jira. This is similar to the synchronisation 
with Odoo but you can not change the target ticket where the
worklogs should be added to. You can only change the time and
description later.

    ./zeit2jira.py M01 update
    DONE:zeit2jira:M01 -> 2023-01-01 2023-01-31

    | act   | at task | date       | desc                    |  zeit
    | ----- | ------- | ---------- | ----------------------- | ----:
    | NEW   | SAND-4  | 2022-01-03 | testing more timetrack  |  1.00

## generating zeit.txt from existing data

Both the Odoo and Jira interface have an option to pull older data
and to present it in the zeit.txt format. In order for the synchronisation
to work, you should have atleast a mapping file that binds Odoo accounts
and Jira tickets.

    # mapping.txt
    >> app1 [PRJ Contract 2022]
    >> app1 "App1 Development"
    >> app1 APP-1234
    >> app2 [PRJ Contract 2022]
    >> app2 "App2 Development"
    >> app2 APP-1456
 
Then have it exported.

    ./jira2data.py zeit -m mapping.txt
    ./jira2data.py odoo -m mapping.txt

## todo

* You can not change a worklog from one ticket to another (like in Odoo booking)
* You can not assign multiple tickets to a prefix topic
* Multiple jira instances will provoke problems with non-existant tickets.
