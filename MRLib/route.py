# ---------------------------------------------------------------------------- #
#                                 Route Module                                 #
#                               Mathurin Roulier                               #
# ---------------------------------------------------------------------------- #

"""
Provides functions used to compute routes.

Functions
---------
route_cost
    Calculates the cost of a route.
        >>> route_cost([(0, 0), (0, 1), (1, 1)], currents_map)
        1.5
"""


import numpy as np


def route_cost(route: list[list], currents_map: np.array):
    cost = 0

    for k in range(len(route)-1):
        cost += np.dot(np.array(route[k+1]) - np.array(route[k]), currents_map[route[k][1], route[k][0]])

    return cost
