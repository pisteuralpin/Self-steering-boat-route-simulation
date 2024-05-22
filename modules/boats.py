"""This module contains the boat class, which is used to store the boats' data"""

import numpy as np

from typing import Callable

import modules.models as models

class Boat:
    """Boat class"""
    def __init__(self, name: str, startPos: tuple[float, float], baseSpeed: float, hydrodynamic_efficiency: float, steeringModel: callable = None, modelParams: dict = None, precision: float = 1, color: str = '#373737', calculations_tick: int = 1):
        """Initialize the boat with its starting position and its base speed
        name: boat's name
        xStart: in meters
        yStart: in meters
        baseSpeed: in m/s
        hydrodynamic_efficiency: between 0 and 1
        steeringModel: steering model (optional)
        modelParams: route following parameters (optional)
        color: boat's color (optional)
        calculations_tick: calculations tick (optional)
        """
        self.name = name
        self.position = startPos
        self.positions = np.array([startPos])
        self.speeds = np.array([])
        self.directions = np.array([])
        self.powers = np.array([])
        self.start_pos = startPos
        self.base_speed = baseSpeed
        self.hydrodynamic_efficiency = hydrodynamic_efficiency
        self.steering_model = steeringModel
        self.precision = precision
        self.color = color
        self.model_params = modelParams
        self.calculations_tick = calculations_tick
        self.calculations_duration = 0
        self.arrived = False
    
    def move(self, speed, direction):
        """"Move the boat with a given speed and direction
        speed: in m/s
        direction: in radians"""
        self.speeds.append(speed)
        self.directions.append(direction)
        self.position[0] += speed * np.cos(direction)
        self.position[1] += speed * np.sin(direction)

    def calculate(self, currents_map: np.ndarray, end: tuple):
        """Start the boat's steering model
        currents_map: currents map
        end: end point coordinates (x, y) in meters
        """
        if self.steering_model == None:
            models.inert(self, currents_map, self.hydrodynamic_efficiency, self.calculations_tick)
        else:
            self.steering_model(self, currents_map, end, self.hydrodynamic_efficiency, self.calculations_tick)
    
    def add_position(self, position: tuple[float, float]):
        """Add a position to the boat's positions
        position: (x, y) in meters"""
        self.positions = np.append(self.positions, [(position)], axis=0)
        self.position = position
    
    def add_speed(self, speed: float):
        """Add a speed to the boat's speeds
        speed: in m/s"""
        self.speeds = np.append(self.speeds, [speed])
    
    def add_direction(self, direction: float):
        """Add a direction to the boat's directions
        direction: in radians
        """
        self.directions = np.append(self.directions, [direction])
    
    def add_power(self, power: float):
        """Add a power to the boat's powers
        power: arbitrary unit"""
        self.powers = np.append(self.powers, [power])

    def add(self, position: tuple[float, float], currents_map: np.ndarray, heading: float):
        """Add a position to the boat's positions
        position: (x, y) in meters"""
        self.add_power(np.dot(currents_map[int(self.position[1]), int(self.position[0]), :], np.subtract(position, self.position)))
        self.add_speed(np.sqrt((position[0] - self.positions[-1][0])**2 + (position[1] - self.positions[-1][1])**2/self.calculations_tick))
        self.add_position(position)
        self.add_direction(heading)

    def reset(self):
        """Reset the boat's data"""
        self.position = self.start_pos
        self.positions = np.array([self.start_pos])
        self.speeds = np.array([])
        self.directions = np.array([])
        self.powers = np.array([])
        self.arrived = False