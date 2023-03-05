Version 0.9 has seen usage by coworkers.

Timetrack has support for Jira Worklogs now being a
fully developed secondary data channel. There had been 
code to read worklogs and other activity on a jira ticket 
for quite some time. The integration to Timetrack supports 
that zeit and odoo records can be fully synchronized. 
The support for multiple jira instances exists but it can
only have one active connection, ie. Timetrack can not 
relate different jira trackers to different connections.

The odooproject prefix logic has been refactored:
* a final number in a prefix finds odoo spec without
** prefix dev-project1 can find odoo spec `>> dev-project`
** prefix dev-project2 can find odoo spec `>> dev-project`
* multiple jira-tickets can be attached to an odoo topic
** `>> dev-project SAND-4 BUGS-5`
* the final number selects the jira-project on push
** prefix dev-project1 would go to SAND-4 in the example
** prefix dev-project2 would go to BUGS-5 in the example
* it is possible to write files having only odoo spec lines
** this is called a mappingfile for `jira2data odoo`
** with multiple jira tickets per odoo spec the topic can be summarized
* a prefix with a dash can find a default base odoo spec
** prefix dev-project can find odoo spec `>> dev`
** prefix dev-project1 can find odoo spec `>> dev`

The commandline interface has been harmonized. All the tools
use the tabtotext variant formatting with "-o wide" format
and "-O output" redirection. The excel support is excluded
from the format (so that openpyxl is an optional dependency),
so each tool has an "-X file.xlsx" option. This works also
in parallel with output redirection. Otherwise "-J data.json"
is recommended to save away results for further processing.
The zeit2x tools allow to read such a data file processing
its content instead of using the implicit zeit2json parser.
Here the "-x file.xlsx" and "-d file.csv" options are 
supported as input overrides.

The prereleases in 2022 did already support for symbolic 
dayranges instead of requiring "-a after -b before" that 
had been introduced back in 2017 with zeit2excel. The usage 
of M01 month names and M01-M03 quarters has become the 
usual way to work with the data. As such the symbolic 
dayranges are now accepted s "-a M01" and even a second 
argument to the commandline (showing a warning however).

Some code for showing quarters of an hour with the extended
ascii codes (man iso-8859-1) had existed for some time
already. Here it is refactored to be a general column format
specification in tabtotext using `{:h}`. More formatting
column formating codes were invented as `{:H}` and `{:M}`
and `{:Q}` an `{:R}`. The most important of the extras
is however `'{:$}'` which results in euro symbol by
default (use `'{:US$}'` for the dollar symbol). In the
tabtoxlsx it makes for a different native format type which
is better to allow copy-n-paste prices values from Excel 
(or oocalc) into other documents like invoices.

Note that some tools like odoo2data and jira2data accept
a user filter. That way the worklog from one or more people 
can be assembled into a single report which is great if the
customer requires a single document for the group of people
who had worked on a project. This is not generic however
and not all the subcommands respect the provided options.

To allow for quicker start the tools have a subcommand 'zeit'
to presents existing remote data in Jira or Odoo in the
text format which the project was originally using. This is
an alternative to the subcommand `'x.py odoo -X saved.xlsx'` 
which shows the data ready for `'zeit2odoo -x saved.xlsx'`.
The 'init' subcommand is automatically saving to the default
location of the zeit.txt file as currently configured.

The '-z' (--onlyzeit) is still used may change in future
versions, just like '--addfooter' and '--shortname' options.
The usage of '-y' to actually write data to Odoo or Jira is
kept, so that some subcommands are in dryrun mode by default.
The output of 'x.py help' shows more hints for each of the
subcommands.
