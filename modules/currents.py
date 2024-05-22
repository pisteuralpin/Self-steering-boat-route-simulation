"""Currents module for the self steering boat simulation"""

import numpy as np
import random as rd

class CurrentMap:
    """Currents map class"""
    def __init__(self, size: tuple, model: int, max_speed: float, dispersion: float = None, min_speed: float = 0, direction: float = 0, currents_map: np.ndarray = None):
        self.size = size
        self.model = model
        self.min_speed = min_speed
        self.max_speed = max_speed
        self.dispersion = dispersion
        self.direction = direction
        self.speeds = np.zeros((size[1],size[0]))

        if currents_map is None:
            if model == 0:
                self.map = NoCurrents(self.size)
            elif model == 1:
                self.map = UniformCurrents(self.size, self.max_speed, self.direction)
            elif model == 2:
                self.map = RandomCurrents(self.size, self.max_speed, self.dispersion, self.direction)
            else:
                raise ValueError("Currents model not found")
        else:
            self.map = currents_map
        
        self.speeds = np.sqrt(self.map[:,:,0]**2 + self.map[:,:,1]**2)
        if model != 0:
            self.map = self.map / np.max(self.speeds) * self.max_speed
        self.speeds = np.sqrt(self.map[:,:,0]**2 + self.map[:,:,1]**2)
        
    def get_currents(self) -> np.ndarray:
        """Return the currents map"""
        return self.map
    
    def get_speeds(self) -> np.ndarray:
        """Return the currents speeds map"""
        return self.speeds

# ----------------------------------------------------------- #
#                      Currents model 0                       #
#                         No currents                         #
# ----------------------------------------------------------- #

def NoCurrents(size: tuple) -> np.ndarray:
    """Generate no currents
    size: (x, y) in meters
    """
    return np.zeros((size[1], size[0], 2))

# ----------------------------------------------------------- #
#                      Currents model 1                       #
#                     Uniform currents                        #
# ----------------------------------------------------------- #

def UniformCurrents(size: tuple, speed: float, direction: float = 0) -> np.ndarray:
    """Generate uniform currents
    size: (x, y) in meters
    speed: in m/s
    direction: in radians
    """
    currents = np.zeros((size[1], size[0], 2))
    currents[:,:,:] = speed
    return currents

# ----------------------------------------------------------- #
#                      Currents model 2                       #
#                  Generate random currents                   #
# ----------------------------------------------------------- #

def RandomCurrents(size: tuple, max_speed: float, dispersion: float, direction: float = 0) -> np.ndarray:
    """Generate random currents
    size: (x, y) in meters
    max_speed: in m/s
    dispersion: in [0, 1]
    direction: in radians
    """
    dispermin = 1 - dispersion
    dispermax = 1 + dispersion
    currents_map = np.zeros((size[1],size[0], 2))
    currents_map[0,:,:] = np.random.uniform(dispermin, dispermax, (size[0],2))      # Generate currents at the bottom line
    currents_map[:,0,:] = np.random.uniform(dispermin, dispermax, (size[1],2))      # Generate currents at the left line


    for i in range(size[1]-1):                                       # Generate currents - line by line
        for j in range(size[0]-1):                                   # Generate currents - column by column
            currents_map[i+1,j+1,:] = np.average(
                    [currents_map[i,j,:],
                     currents_map[i+1,j,:],
                     currents_map[i,j+1,:]] 
                    * np.random.uniform(dispermin, dispermax, (3,2)))                 # Generate currents - average of the currents at the left, bottom and bottom-left with a random dispersion - X composant
            
    return currents_map