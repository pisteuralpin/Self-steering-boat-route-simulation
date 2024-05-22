# ---------------------------------------------------------------------------- #
#                                Geometry Module                               #
#                               Mathurin Roulier                               #
# ---------------------------------------------------------------------------- #

"""
Provides functions used to perform operations.

Functions
---------
direction
    Calculates the direction of a segment.
        >>> direction((0, 0), (1, 1))
        0.7853981633974483
distance
    Calculates the distance between two points.
        >>> distance((0, 0), (1, 1))
        1.4142135623730951
nearest_point
    Finds the nearest point to a given point in a list of points.
        >>> nearest_point((0, 0), [(1, 1), (1, 0), (0, 1)])
        (1, 0)
"""

from numpy import arctan, pi


def direction(A: tuple[float, float], B: tuple[float, float], last_direction: float = None) -> float:
    if A[0] == B[0]:
        if A[1] > B[1]:
            return -pi/2
        else:
            return pi/2
    angle = arctan( ( (A[1] - B[1]) /
                      (A[0] - B[0])  ) )
    if last_direction == None:
        return angle
    if (last_direction - angle) > pi/2:
        return angle + pi
    elif (last_direction - angle) < -pi/2:
        return angle - pi
    else:
        return angle
    
def distance(A: tuple[float, float], B: tuple[float, float]) -> float:
    return ((A[0] - B[0])**2 + (A[1] - B[1])**2)**.5

def nearest_point(A: tuple[float, float], points: list[tuple[float, float]]) -> tuple[float, float]:
    distances = [distance(A, point) for point in points]
    return points[distances.index(min(distances))]