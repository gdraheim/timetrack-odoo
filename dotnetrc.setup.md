## NETRC

The dotnetrc util is a password storage utility that handles the formats 
of dot-netrc ($HOME/.netrc) and dot-gitcredentials ($HOME/.git-credentials).

### dot-netrc

The dot-netrc configuration file seems to have been born on BSD systems and 
it is implicitly read by both "git" and "curl" tools to get login information 
for remote sites.

It's format is described in "man 5 netrc" = https://linux.die.net/man/5/netrc

There is a python3 standard library module netrc as well.
That's the reason why netrc.py was later renamed to this dotnetrc.py

The implementation here is extended that "machine" can also include a following
prefix and both machine and prefix can use fnmatch "*" "?" to catch multiple
remote machine names and paths.

If you are working with a jira on "https://my.site/jira" you can setup a file
named "$HOME/.netrc" with

    machine my.site login myname password P@ssw0rd

or you can put the elements on seperated lines but make sure "machine" starts
the block.

    machine my.site 
    login myname 
    password P@ssw0rd

For a login to Odoo or Qtest the login is a mail-adress

    machine qtest.site login myname@company password P@ssw0rd

Be sure to set the file "chmod 0400 ~/.netrc". The script will warn about it.

### dot-gitcredentials

The dot-gitcredentials was invented by the Git team to store credentials in
cleartext. You need to enable it with 

    git config --global credential.helper store

This has the advantage that login information is always kept uptodate when
you use git regularly. On the downside the git tool respects the auth path
that was sent from the remote server which usually means that a match on the
actually path after the machine name gets deleted.

The implementation here is extended that a match can include a following
prefix and both machine and prefix can use fnmatch "*" "?" to catch multiple
remote machine names and paths.

If you are working with a jira on "https://my.site/jira" you can setup a file
named "$HOME/.git-credentials" with

    https://myname:P@ssw0rd@my.site

### Usage 

Make sure to allow the credentials file to be set by the user on the commandline.

    from dotnetrc import set_password_filename
    from optparse import OptionParser
    cmdline = OptionParser("%prog files...")
    cmdline.add_option("-g", "--gitcredentials", metavar="FILE", default="~/.netrc")
    set_password_filename(opt.gitcredentials)

Use a target url to ask for the username/password tuple

    import requests
    from dotnetrc import get_username_password
    requests.get(url, auth=get_username_password(url))

