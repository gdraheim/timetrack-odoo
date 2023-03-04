## TIMETRACK HISTORY

The project has three different sources. One was an odoo-import script, which was 
converting some zeit.txt timesheet into excel (or csv) for the Odoo import button.
Until Odoo 10 it was also possible to define an external reference ID, so that you
were able to update older entries. The old converer lives on as the zeit2json.py
script - with json being an intermediate data representation for zeit2odoo.py

The second source comes from the odoo-otter project which allowed to push timesheet
entries to Odoo using its ResT API. The odoo_rest.py part has the API interface 
along with a class wrapper. The zeit2odoo.py combines odoo_rest.py with zeit2json.py
so that zeit.txt entries can be synchronized to Odoo via its ResT API.

When Odoo lost the ability to track externacal reference, the concept of a topic
marker was introduced for synchronization. Formerly, there was a shorthand notation
of an Odoo account in the zeit.txt file which was NOT put into the target Odoo
instance. With Odoo-10 and Odoo-ResT synchronization, each of the Odoo entries has 
a desription field that starts with a topic marker. It can be quite long like 
"project-travel" but it is not simple text but part of the syntax to be able to 
update older entries in Odoo with updated text that follows this first long-word.

The third source comes the timetrack project that allows to read different event
sources like Jira worklogs and Git commits. These can be mirrored and combined
for a timesheet data sink where Odoo is one possibility. No code came over but
the class wrappers are modelled for that. Instead our timetrack-odoo project
has the option to use Odoo has a data source as well which you can see in the
odoo2data.py part which otherwise covers extra reports summarizing times.

Some readers may recognize tabtotext and gitrc being used in other projects as
well but actually they were first written for zeit2excel / zeit2json. Later
extensions outside of timetrack-odoo were merged back however.
