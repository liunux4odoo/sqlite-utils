try:
    import pysqlite3 as sqlite3
    import pysqlite3.dbapi2

    OperationalError = pysqlite3.dbapi2.OperationalError
except ImportError:
    import sqlite3

    OperationalError = sqlite3.OperationalError


def suggest_column_types(records):
    all_column_types = {}
    for record in records:
        for key, value in record.items():
            all_column_types.setdefault(key, set()).add(type(value))
    column_types = {}
    for key, types in all_column_types.items():
        if len(types) == 1:
            t = list(types)[0]
            # But if it's a subclass of list / tuple / dict, use str
            # instead as we will be storing it as JSON in the table
            for superclass in (list, tuple, dict):
                if issubclass(t, superclass):
                    t = str
        elif {int, bool}.issuperset(types):
            t = int
        elif {int, float, bool}.issuperset(types):
            t = float
        elif {bytes, str}.issuperset(types):
            t = bytes
        else:
            t = str
        column_types[key] = t
    return column_types


def column_affinity(column_type):
    # Implementation of SQLite affinity rules from
    # https://www.sqlite.org/datatype3.html#determination_of_column_affinity
    assert isinstance(column_type, str)
    column_type = column_type.upper().strip()
    if column_type == "":
        return str  # We differ from spec, which says it should be BLOB
    if "INT" in column_type:
        return int
    if "CHAR" in column_type or "CLOB" in column_type or "TEXT" in column_type:
        return str
    if "BLOB" in column_type:
        return bytes
    if "REAL" in column_type or "FLOA" in column_type or "DOUB" in column_type:
        return float
    # Default is 'NUMERIC', which we currently also treat as float
    return float
