## FEATURES

### zeit2json

The project was initially created as "zeit2excel.py".

* using ~/zeit2023.txt as input and writing ~/zeit2023.txt.csv and ~/zeit2023.txt.xlsx
* the specific format of the csv/xlsx file has the columns for the Odoo import button
* "ID", "Project", "Task", "User", "Description", "Quantity"

The ID column is actually an ExternalID which did allow to overwrite existing records
with new data. However since Odoo-10 this option was dropped and every imported line
from the file did create a new record.

The original script was imported to timetrack as "zeit2json.py".

* using ~/zeit2023.txt as input and writing ~/zeit2023.txt.csv and ~/zeit2023.txt.json
* the csv can still be used for the Odoo import button (if not disabled as usual)
* it dropped the "ID" column but it has an additional "Topic" column.

It is assumed per day the "Topic" is only used once which allows other script to
update existing records. If a logical topic needs to be used multiple times per day
then it can have number at the end, "my-topic1" and "my-topic2". They will be both
mapped to the same Odoo "Project"/"Task" base. 

Using the topic-per-day approach allows to change the "Project"/"Task" later. This
is actually very common if a software feature will be subject to additional contract 
which was agreed informally already whereas the paperwork is underwritten only later 
and then becoming a seperate Odoo Project/Task.

### zeit2odoo

There are files like "odoo2data_api.py" and "odoo2data_api_mockup.py" which access 
the Odoo timesheet database via its API.

* zeit2odoo.py calls a function from zeit2json.py to get the json data in-memory
* zeit2odoo.py then calls functions from odoo2data_api.py to read/write Odoo records
* using an existing "Topic" in an Odoo record it can update it with new data

Note that "update" is in dryrun mode by default, and "-y" is need to actually
write to Odoo.

The "zeit2odoo" script has some statistics like "topics" and "summary" which
can show if there is a difference between the local Zeit data and the remote
Odoo data.

### odoo2data

The odoo2data has "topics" and "summary" statistics as well, but it only has
the column for "odoo". (However there is a simulation mode "-z" where the
input records come from zeit2json instead of the odoo API).

The commands "report" and "reports" is used to build an excel file that can
be used for invoices by freelancers.

The command "zeit" can convert Odoo data back into a similar Zeit format.
However the conversion is unrealiable and the outshould only be used as 
a starting point.

### jira2data

The jira2data.py script does the same as odoo2data but it uses Jira worklog
entries. Use "topics" and "summary" to some statistics. Use "zeit" to convert
into a similar Zeit format (again unreliable) and it will probably need a
mapping file (option "-m") as input. Having a mapping file is required for the
"odoo" command which outputs data for the "zeit2odoo" script.

### zeit2jira

The zeit2jira.py script does the same as zeit2data but instead of a target
Project/Task it needs the information which Jira issue should be used to 
the worklogs to.

### configuration

The original file "zeit2excel.py" has a number of hardcoded values in it.
These were removed for timetrack-odoo and "zeit2json" uses helper scripts.

* dotnetrc.py is used to retrieve username/password files in ~/.netrc
* dotnetrc.py can be used used to write username/password into ~/.net-credentials
* dotgitconfig.py is used to retrieve user name and email from ~/.gitconfig
* dotgitconfig.py is used to get connection information for Odoo and Jira

### output formats

The tabtotext.py and tabtoxlsx.py modules are used to convert table data
into different output formats (and to read them back again). Every script
in timetrack-odoo has "-o format" and "-O filename".

* "-o gfm" is the default for "github flavourd markdown" tables
* "-o wide" is the default for the "zeit" output
* Use "json" and "csv" and "tabs" to exchange data with other programs
* Use "html" to upload to confluence as a table (automatically sortable there)
* You can not use "-o xlsx" but the xlsx output is triggered with "-X filename".

The zeit2odoo script can also use "-x filename" to read xlsx files as input.
If there are already other scripts that were producing the Odoo import button
format then this allows to update the records with the Odoo API instead. The
"-D" and "-d" option are equally used for csv-style data meant originally for
the Odoo import button in the Odoo web UI.

### daysrange specifications

The zeit2odoo script can take a while to query the existing Odoo database.

Instead of comparing all data (actually the current year) one should try
to limit the days that may get summarized or updated.

* use "M01" ... "M12" for single months
* use "M01-M03" .... "M10-M12" for quarters
* use "lastweek" for the last week
* use "last" for beforelastweek up to the current day
* use "latest" for lastweek up to the current day

These are actually shorthands for "-a 12.01." beginning to "-b 30.01." for
the last day to be synchronized. Using "-b 99.01." is a shorthand for the
last day in that month. (Note that "-a 01.01. -b 01.02." is a dayrange of
32 days and may not do the expected thing).

* jira2data.py M01 -m ~/mapping.zeit.txt odoo

### account mapping

The account mapping file has this format

    >> topic [Odoo Project Name]
    >> topic "Odoo Task Name"
    >> topic BUGS-1 MAKE-3 JIRAISSUES-4

In the Zeit format the topic is the first word in the description of a day.

    mo 2:00 topic updated
