## SETUP

### gitconfig

Edit your ~/.gitconfig 

    [user]
        name = John Doe

    [zeit]
        filename = ~/mycompany/zeit{YEAR}.txt
    [odoo]
        url= https://mycompany.odoo.com
        db= prod-mycompany

### credentials

    ./netrc.py set https://mycompany.odoo.com john.doe@example.com whatever
