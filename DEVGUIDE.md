# DEVELOPMENT GUIDELINES

* workplace setup
* makefile targets
* release process

## WORKPLACE SETUP

Development can be done with a pure text editor and a terminal session.

### VSCode setup

Use python and mypy extensions for Visual Studio Code (from Microsoft).

* Control-P: "ext list"
  * look for "Python", "Pylance" (style checker), "Mypy Type Checker" (type checker)
* Control-P: "ext install ms-python.mypy-type-checker"
  * this one pulls the latest mypy from the visualstudio marketplace
  * https://marketplace.visualstudio.com/items?itemName=ms-python.mypy-type-checker

The make targets are defaulting to tests with python3.6 but the mypy plugin
for vscode requires atleast python3.8. All current Linux distros provide an
additional package with a higher version number, e.g "zypper install python311".
Be sure to also install "python311-mypy" or compile "pip3 install mypy". 
Implant the paths to those tools into the workspace settings = `.vscode/settings.json`

    {
        "mypy-type-checker.reportingScope": "workspace",
        "mypy-type-checker.interpreter": [
                "/usr/bin/python3.11"
        ],
        "mypy-type-checker.path": [
                "mypy-3.11"
        ],
        "mypy-type-checker.args": [
                "--strict",
                "--show-error-codes",
                "--show-error-context",
                "--no-warn-unused-ignores",
                "--ignore-missing-imports",
                "--exclude=build"
        ],
        "python.defaultInterpreterPath": "python3"
    }

The python files at the toplevel are not checked in vscode. I dont know why (yet).

### Makefile setup

Common distro packages are:
* `zypper install python3 python3-pip` # atleast python3.6
* `zypper install python3-wheel python3-twine`
* `zypper install python3-coverage python3-unittest-xml-reporting`
* `zypper install python3-mypy python3-mypy_extensions python3-typing_extensions`
* `zypper install python3-autopep8`

For ubuntu you can check the latest Github workflows under
* `grep apt-get .github/workflows/*.yml`

## Makefile targets

### static code checking

* `make type`
* `make style`

### testing targets

There are a dozen `XX.tests.py` files in the project which are `unittest` testcases.
You can run each seperately with a shortname, e.g. `make x` runs tabtotext.tests.py
and `make x_9020` runs "test_9020" in that tests.py.

* `make check` # runs all the XX.tests.py targets 
* `make install` and `make uninstalls` # for updating a `~/.local/bin` setup

### release targets

* `make version`
* `make build`

## RELEASE PROCESS

### steps
* `make type`   # python mypy
* `make style`  # python style
* `make check`
* `make version` # based on the current week+day
* `make build` # default build
* `make ins` 
* `make uns`
* `make xlsx` # special tabxlsx
* `make insxlsx` 
* `make unsxlsx`
* `make coverage` 
   * update README.md with the result from coverage
* `git push` # if necessary
   * wait for github workflows to be okay
* prepare a tmp.changes.txt 
* `make tag`
   * `git tag -F tmp.changes.txt v1.x` to the version in zziplib.spec
* `git push --tags`
* update the short description on github
* `make xlsx` 
  * execute shown `twine upload` to pypi.org
* `make build`
  * execute shown `twine upload` to pypi.org

## TODO

* enhance cli

