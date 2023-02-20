## SETUP

### gitconfig

Edit your ~/.gitconfig 

    [user]
        name = John Doe

    [zeit]
        filename = ~/my/home/company/zeit{YEAR}.txt
    [odoo]
        url= https://erp.mycompany.corp
        db= prod-mycompany
    [jira]
        url= https://jira.host

Make sure that "name" is the full name as used in Odoo. The path for 
the `zeit*.txt` files is generally different for everyone - be aware
that there are usually multiple files with on for every year. So in
your home/company folder you have zeit2023.txt zeit2024.txt etcetera.

### credentials

    ./netrc.py set https://erp.mycompany.corp myself@mycompany.corp Example.2022
    ./netrc.py set https://jira.host myself Example.2022

Or create a file `$HOME/.netrc` with content like

    machine erp.mycompany.corp user myself@mycompany.corp login Example.2022

Note that most Odoo services will use your email adress as the login
user. For Jira services however the general corporate user directory
is used.

### optional: check jira

This is optional. If you have a Jira to copy worklogs to.

    ./jira2data.py help
    ./jira2data.py tickets
    | SAND-4 | 17863   | Task      | SAND  | testing timetrack

### look for project and task

With the gitconfig and credentials ready, you can check if you have
access to Odoo already.

    ./odoo2data.py help
    ./odoo2data.py projects
    1 | PRJ Contract 2022

You can filter the list by using `--projonly` or just `-P prj`. This
comes handy when looking for an Odoo task that you want to book your
time to.

    ./odoo2data.py oo -P prj
    1  | PRJ Contract 2022 | 42 | "Support Efforts"

If the account owner changes the projects-tasks names then you have
to take it over into your zeit2022.txt file later.

### setup a zeit file

The timesheet entries in the zeit file have the general format

    <weekday> <hours> <topic> <description>

The weekday+topic is a unique tuple, which allows you to update
an existing entry in Odoo later as the tool can recognize an old
entry from the topic appearing at the start of the Odoo description.

From the projects-tasks above, you need to define where the topic
should be booked to. So an initial zeit2022.txt file could look
like this:

   >> app1 [PRJ Contract 2022]
   >> app1 "App1 Development"
   >> app2 [PRJ Contract 2022]
   >> app2 "App2 Development"
   # comment: each week must start giving the first date
   so **** WEEK 02.01.-09.01.
   mo (09:00-17:00) - this line is ignored (like a comment)
   mo 5:00 app1 extended frontend
   mo 3:00 app2 extended backend

The syntax has evolved over time, so it has some special features.
The Odoo specifications start with `>>`. Each topic should have
atleast two lines for `[Project]` and `"Task"`. If the task changes
throughout the year (perhaps at the end of quarter) then you can
redo the `>>` assignment - so the `>>` Odoo specifications do not
need to be at the start of file, just have them before using the
topic in a timesheet entry.

The timesheet entries start with the weekday. The weekdays are in
German or English, ie. mo (monday), di/tu (tuesday), mi/we (wednesday), 
do/th (thursday), fr (friday), sa (saturday), so/su (sunday). This comes 
from the habit to add missing entries at the end of the week. You don't 
need to know the exact calendar date - it is computed as the offset of 
the weekday from the `WEEK` specification before it.

The `WEEK` specification requires a date following this special
word. The second date after it is ignored but I tend to write
it down always pointing to the weekstart of the next week. The
four stars and the weekday before `WEEK` are required. A week
may start on sundays (which I usually choose) or on mondays.
The parser will check if the given so/mo weekday matches with 
date given after `WEEK`.

### synchronize to odoo

With the zeit2022.txt ready, you can check if there is anything
to be updated.

   ./zeit2odoo.py M01 topics
   | at topic   |   odoo |   zeit
   | ---------- | -----: | -----:
   | app1       |   0.00 |   5.00
   | app2       |   0.00 |   3.00

The M01 represents a timespan to be checked or synchronized. The
`M01` is a shorthand for `-a 01.01. -b 99.01.` (where 99 is a 
generic term for the last day of the month). The default is the
full year - however for every day in the year, an Odoo ResT call
is made, so it is better to restrict the span to a month or week.

The `topics` is a report type which is summarizing the given month 
group-by topics. Check out `zeit2odoo.py help` for other reports
that are available. The zeros on the odoo side say that we have
never synched any zeit2022.txt entry to the Odoo database. Let's
check what would be done:

    ./zeit2odoo.py M01 update

    | act   | at proj           | at task          | date       | desc      |  zeit
    | ----- | ----------------- | ---------------- | ---------- | --------- | ----:
    | NEW   | PRJ Contract 2022 | App1 Development | 2022-01-03 | app1 ...  |  5.00
    | NEW   | PRJ Contract 2022 | App2 Development | 2022-01-03 | app2 ...  |  3.00

This was just a dryrun which says that it would create NEW Odoo timesheet
records. There is also "UPD" for updates and "-OK" if nothing needs to be
done. When it looks okay the push it for real.

    ./zeit2odoo.py M01 update -y

Remember that "app1" and "app2" may only be used once for every weekday. But
you do not need to specify a hundred topics if you know there are just subtopics
which can attach with an "-hyphen". So some "app1-frontend" and "app1-backend"
topic will both find the Odoo specification for "app1". However you may override
"app1-frontend" later with a different value. And after re-update the existing
Odoo timesheet gets booked to the different account.

   >> app1 [PRJ Contract 2022]
   >> app1 "App1 Development"
   >> app2 [PRJ Contract 2022]
   >> app2 "App2 Development"
   # comment: each week must start giving the first date
   so **** WEEK 02.01.-09.01.
   mo (09:00-17:00) - this line is ignored (like a comment)
   mo 4:00 app1-frontend extended
   mo 1:00 app1-backend extende
   mo 3:00 app2 extended backend

So if you have a jira tracker BUGS then you could also make a topic BUGS
writing a timesheet entry for every bug ticket number on that weekday.

   >> BUGS [PRJ Contract 2022]
   >> BUGS "App1 Development"
   so **** WEEK 02.01.-09.01.
   mo 4:00 BUGS-1777 fixed
   mo 1:00 BUGS-1842 analyzed

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

   mapping.txt
   >> app1 [PRJ Contract 2022]
   >> app1 "App1 Development"
   >> app1 APP-1234
   >> app2 [PRJ Contract 2022]
   >> app2 "App2 Development"
   >> app2 APP-1456
 
Then have it exported.

    ./odoo2data.py zeit -m mapping.txt
    ./jira2data.py zeit -m mapping.txt
    ./jira2data.py odoo -m mapping.txt

Remember that you can save the output to a file for further editing.

    ./jira2data.py zeit -m mapping.txt -O check.txt
    ./jira2data.py odoo -m mapping.txt -X check.xlsx

The edited data can be used as the source again.

    ./zeit2odoo update -x check.xlsx
