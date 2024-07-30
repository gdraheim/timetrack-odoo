
## TABXLSX - minimal Excel support

TabXLSX reads and writes Excel xlsx files. It does not depend on other libraries.The output defaults to a markdown table and csv-like output
is available as well. This allows piping the data into other scripts.

A number of output format options are available but less than the tabtotext.py module. The export to xlsx was orginally written with
openpyx1 for tabtotext but it is possible to write simple tables
just with Python's zip and xml.etree builtin modules. That is also
faster.
