[![Style Check](https://github.com/gdraheim/timetrack-odoo/actions/workflows/stylecheck.yml/badge.svg?event=push&branch=main)](https://github.com/gdraheim/timetrack-odoo/actions/workflows/stylecheck.yml)
[![Type Check](https://github.com/gdraheim/timetrack-odoo/actions/workflows/typecheck.yml/badge.svg?event=push&branch=main)](https://github.com/gdraheim/timetrack-odoo/actions/workflows/typecheck.yml)
[![Unit Tests](https://img.shields.io/badge/basic%20unit%20tests-578%20tests-brightgreen)](https://github.com/gdraheim/timetrack-odoo/actions/workflows/unittests.yml)


## TIMETRACK ODOO (and JIRA and more)

Timetrack is a synchronisation tool for work hours. It can read, write and
update different data bases.

* [Odoo Timesheet](https://www.odoo.com/app/timesheet-features) via REST API
* [Jira Issue Worklogs](https://confluence.atlassian.com/jirasoftwareserver/logging-work-on-issues-939938944.html) via REST API
* zeit.txt timetrack notes as a local file

It was originally used to push local timetrack notes to Odoo timesheet tracking.
If all work notes (in the description field) have a symbolic prefix then the
data can also be updated later - for every day the tool assumes that the 
symbolic prefix is used only once. Here's a mapping definition in two lines
followed by two lines for the work notes.

    >> app1 [PRJ Contract 2023]
    >> app1 "App1 Development"
    so **** WEEK 08.01.-15.01.
    mo 5:00 app1 extended frontend

This can be pushed to Odoo with `./zeit2odoo.py -f zeit.txt update`. It defaults
to dryrun and the real write operations are done when adding `-y`. For Jira you
need to to configure a ticket number `>> app1 BUG-1234` so that the tool knows
where to add worklog entries when using `./zeit2jira.py -f zeit.txt update`.

Surley, it only works when the basic setup was done where you have configured 
the urls and login credentials. However for the biggest part you need to setup
the mapping of different work topics to their Odoo and Jira accounts. If you
do already have data in Odoo then you can get a `zeit` summary from it for a
quick start with `./odoo2data.py lastmonth zeit`. Save it with `-O zeit.txt`.

* [setup.quickstart](setup.quickstart.md) - the BASIC SETUP takes about one hour

| Documentation                         | Topic                           |
| ------------------------------------- | ------------------------------- |
| [odoo2data.setup](odoo2data.setup.md) | generate reports for Odoo data  |
| [jira2data.setup](jira2data.setup.md) | generate reports for Jira data  |
| [zeit2json.setup](zeit2json.setup.md) | generate reports for Zeit       |
| [zeit2odoo.setup](zeit2odoo.setup.md) | synchronize Zeit to Odoo        |
| [zeit2jira.setup](zeit2jira.setup.md) | synchronize Zeit to Jira        |
| [odoo_rest.setup](odoo_rest.setup.md) | Odoo API hints                  |
| [tabtotext.setup](tabtotext.setup.md) | how report tables are generated |
| [netrc.setup](netrc.setup.md)         | how credentials are stored      |

and some [HISTORY](HISTORY.md)
