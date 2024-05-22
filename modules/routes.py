import numpy as np

from typing import Callable

import modules.models as models
import modules.score as score

class Route:
    """Route class"""
    def __init__(self, name: str, startPos: tuple[float, float], routeModel: Callable[[object, np.ndarray, tuple, tuple], np.ndarray] = None, color: str = '#373737'):
        """Initialize the boat with its starting position and its base speed
        name: boat's name
        startPos: (x, y) in meters
        routeModel: route model (optional)
        color: boat's color (optional)
        """
        self.name = name
        self.positions = np.array([])
        self.start = startPos
        self.route_model = routeModel
        self.color = color
        self.history = []
        self.calculations_duration = 0

    def calculate(self, currents_map: np.ndarray, end: tuple):
        """Start the boat's steering model
        currents_map: currents map
        end: end point coordinates (x, y) in meters
        """
        self.route_model(self, currents_map, self.start, end)