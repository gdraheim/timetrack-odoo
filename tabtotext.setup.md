## TABTOTEXT

The tabtotext functions are using a universal format to store a table.

    The table is a List of records. (see python typing.List)
    Each record is a Dict of items. (see python typing.Dict)
    Each item is a Union of basic types including str, int, float, date.

The item type is useful when handling JSON data so that the actual type names are

    JSONItem = Union[str, int, float, bool, date, None, Dict[str, Any], List[Any]]
    JSONDict = Dict[str, JSONItem]
    JSONList = List[JSONDict]

Note that an Item can also contain more structured values but that is NOT considered
for the conversion process of tabtotext. It is just useful when getting json.loads
data printing them with the tabtotext utility just easily.

### tabToGFM markdown

GFM is the github-flavoured Markdown format. This reference is needed because the
original Markdown format did NOT define a table markup. This has been an extension
and it was impelemented differently in different markdown tools. However the Github
style has ensured a defacto standardization.

### tabToHTML confluence

The html format here is ready to be uploaded to Confluence as a wiki page.

### tabToJSON storage

The tabToJSON format is extended over the python "json" library as it can handle
date / datetime items. The loadJSON routine can load back the textual representation.
Note that tabToJSON is a thin layer over json.loads and json.dumps routines.

### tabToCSV storage

The tabToCSV format is extended over the python "csv" library as it can handle
date / datetime items. The loadCSV routine can load back the textual representation.
Note that tabToCSV is a thin layer csv.DictReader and csv.DictWriter routines.


