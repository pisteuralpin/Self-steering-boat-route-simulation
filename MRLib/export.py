# ---------------------------------------------------------------------------- #
#                                 Export module                                #
#                               Mathurin Roulier                               #
# ---------------------------------------------------------------------------- #

"""
Provides functions used to export data.

Functions
---------
dictToCSV
    Convert a dictionnary to a CSV string.
        >>> dictToCSV({"a": 1, "b": 2.2, "c": "hello world"})
        "a,1\\nb,2.2\\nc,hello world\\n"
"""

import warnings


def dictToCSV(dictionnary: dict) -> str:
    """Convert a dictionnary to a CSV string"""
    csv = ""
    for key in dictionnary:
        if type(dictionnary[key]) not in [int, float, str]:
            warnings.warn("The dictionnary must only contain int, float or str values. Others types will be converted to str.")
        csv += str(key) + "," + str(dictionnary[key]) + "\n"
    return csv