## ZEIT2JSON

The implementation is a variant of "zeit2excel.py" which has been used to convert a
text file "zeit.txt" into a zeit.csv and zeit.xlsx that can be used by the Odoo import
function as available on the UI of the Timesheet module.

The Odoo import function was able to check the header line of a csv/xlsx file and if a
column did match the target field names then it was able to create timesheet records
from the follwing lines. See this csv:


   ID;Date;Quantity;Project;Task;Description;User
   220102PM4;2022-01-02;2.75;MGMT;Project Management;orga: tech call

Note that the "foreign ID" column named "ID" is disregarded after Odoo 10. Originally
it did allow to overwrite older entries. Because of that change a few double entries
did occur after import and some support crews have disabled the odoo-import function
after that.

The new implementation does not generate xlsx any more (it was useful as non-ascii
characters were always read correctly). Instead it writes a json fiel in the style
of tabToJSON as it has a reader loadJSON that can load back data from zeit2json
for later import to Odoo. Other than Python json.loads it can read/write the date
and time types correctly (datetime.date and datetime.datetime).

### zeit.txt format

The ">>" lines are used to map a topic-shorthand to Odoo Project/Task coordinates.
As an extension the prefix to the Description can be changed so that it does not
use a short-code anymore - be sure however to make prefixes unique to ensure that
you can change old timesheet entries to a different project/task if needed. If the
topic-shorthand does not include numbers then it always the prefix.

    >> dev1 [Project-1]
    >> dev1 "Developments"
    >> dev1 = development:

The zeit records are given per week. Each week is introduced with "**" where the
first date is the references for the following timesheet notes given by weekday.
You can choose whether to have that base date starting a week on sunday or monday.
The weekdays can be given in the German or English two-letter abbreviation.

    so **** WEEK 02.01.-09.01.
    so 2:45 PM4 tech session
    mo 0:15 dev1 role accounts
    di 1:00 dev1 morning scrum, discussions
    di 3:00 dev4 dev planning meetings
    fr 0:30 PM4 odoo problems 

Note that for each weekday each topic may occur only once. If you want to differentiate
then use numbered topic-shorthands like "dev1" to "dev4" in the example.

### SETUP

The script will pick up your user name from ~/.gitconfig

    [user]
        name = John Doe

You have probably configured that to push git commits.
