[![Style Check](https://github.com/gdraheim/timetrack-odoo/actions/workflows/stylecheck.yml/badge.svg?event=push&branch=main)](https://github.com/gdraheim/timetrack-odoo/actions/workflows/stylecheck.yml)
[![Type Check](https://github.com/gdraheim/timetrack-odoo/actions/workflows/typecheck.yml/badge.svg?event=push&branch=main)](https://github.com/gdraheim/timetrack-odoo/actions/workflows/typecheck.yml)

## TIMETRACK ODOO (and JIRA and more)

Timetrack is a synchronisation tool for working hours. It can read, write and
update different data bases.

* [Odoo Timesheet](https://www.odoo.com/app/timesheet-features) via REST API
* [Jira Issue Worklogs](https://confluence.atlassian.com/jirasoftwareserver/logging-work-on-issues-939938944.html) via REST API
* local zeit.txt as a local file

It was originally used to push local working notes to Odoo timesheet tracking.
If all working notes (in the description field) have a symbolic prefix then the
data can also be updated later - for every day the tool assumes that the 
symbolic prefix is used only once. Here's a mapping definition in two lines
followed by two lines for the working notes.

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

* [odoo2data.setup](odoo2data.setup.md)
* [zeit2odoo.setup](zeit2odoo.setup.md)
* [zeit2json.setup](zeit2json.setup.md)
* [jira2data.setup](jira2data.setup.md)
* [odoo_rest.setup](odoo_rest.setup.md)
* [tabtotext.setup](tabtotext.setup.md)
* [netrc.setup](netrc.setup.md)

and some [HISTORY](HISTORY.md)
