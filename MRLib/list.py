# ---------------------------------------------------------------------------- #
#                                  List module                                 #
#                               Mathurin Roulier                               #
# ---------------------------------------------------------------------------- #

"""
Provides functions used to manipulate lists.

Functions
---------
remove_duplicates
    Removes duplicates from a list.
        >>> remove_duplicates([1, 2, 3, 2, 1])
        [1, 2, 3]
"""

def remove_duplicates(L:list) -> list:
    """Removes duplicates from a list."""
    return list(set(L))