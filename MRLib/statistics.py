# ---------------------------------------------------------------------------- #
#                               Statistics Module                              #
#                               Mathurin Roulier                               #
# ---------------------------------------------------------------------------- #

"""
Provides functions used to perform statistical operations.

Functions
---------
mov_avg
    Calculates the moving average of a list of numbers.
        >>> mov_avg([1, 2, 3, 4, 5], 3)
        [2.0, 3.0, 4.0]

"""


def mov_avg(data:list, n:int) -> list[float]:
    """Calculates the moving average of a list of numbers."""
    return [sum(data[i:i+n])/n for i in range(len(data)-n+1)]