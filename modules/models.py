"""Self-steering boat models"""

import numpy as np
import scipy.interpolate as spint
import MRLib as mrl

# ---------------------------------------------------------------------------- #
#                                     Boats                                    #
# ---------------------------------------------------------------------------- #

# ----------------------------------- Inert ---------------------------------- #
def inert(boat: object, currents_map: np.ndarray, hydrodynamic_efficiency: float, calculations_tick: float):
    """Inert boat model
    boat: boat object
    currents_map: currents map
    """
    position = boat.position
    while (position[0] < currents_map.shape[1] and position[1] < currents_map.shape[0]):
        next_position = position + calculations_tick * currents_map[int(position[1]), int(position[0]), :] * hydrodynamic_efficiency

        if (next_position[0] >= currents_map.shape[1] or next_position[1] >= currents_map.shape[0]):
            break

        if position[0] == next_position[0] and position[1] == next_position[1]:
            break

        boat.add(next_position, currents_map, 0)

        position = boat.position

# ----------------------------- Direction Keeping ---------------------------- #
def directionKeeping(boat: object, currents_map: np.ndarray, end: tuple[float, float], hydrodynamic_efficiency: float, calculations_tick: float):
    """Initial headed boat model
    boat: boat object
    currents_map: currents map
    end: end point coordinates (x, y) in meters
    hydrodynamic_efficiency: hydrodynamic efficiency
    calculations_tick: calculations tick in seconds
    """
    position = boat.position
    initial_head = mrl.geometry.direction(position, end)
    precision = boat.precision
    while (position[0] < currents_map.shape[1]
           and position[1] < currents_map.shape[0]
           and np.sqrt((position[0] - end[0])**2
                       + (position[1] - end[1])**2) > precision):

        next_position = position + calculations_tick * currents_map[int(position[1]), int(position[0]), :] * hydrodynamic_efficiency + calculations_tick * boat.base_speed * np.array([np.cos(initial_head), np.sin(initial_head)])

        if (next_position[0] >= currents_map.shape[1]
            or next_position[1] >= currents_map.shape[0]
            or mrl.geometry.distance(next_position, position) < .1):
            break

        boat.add(next_position, currents_map, initial_head)

        position = boat.position
    
    if np.sqrt((position[0] - end[0])**2 + (position[1] - end[1])**2) <= precision:
        boat.arrived = True
        

# --------------------- Controlled Position PI Correction -------------------- #
def controlledPositionPICorrector(boat: object, currents_map: np.ndarray, goal_pos: tuple[float, float], hydrodynamic_efficiency: float, calculations_tick: float, can_pass: bool = False, end: tuple[float, float] = None, last: bool = False):
    """Controlled position PI corrector boat model
    boat: boat object
    currents_map: currents map
    goal_pos: goal pos point coordinates (x, y) in meters
    hydrodynamic_efficiency: hydrodynamic efficiency
    calculations_tick: calculations tick in seconds
    """
    heading = -(np.arctan2(boat.position[0]-goal_pos[0], boat.position[1]-goal_pos[1]) + np.pi/2)
    precision = boat.precision
    while (0 < boat.position[0] < currents_map.shape[1] and 0 < boat.position[1] < currents_map.shape[0]
           and np.sqrt((boat.position[0] - goal_pos[0])**2 + (boat.position[1] - goal_pos[1])**2) > precision):

        next_position = boat.position + calculations_tick * currents_map[int(boat.position[1]), int(boat.position[0]), :] * hydrodynamic_efficiency + calculations_tick * boat.base_speed * np.array([np.cos(heading), np.sin(heading)])

        if (not 0 <= next_position[0] <= currents_map.shape[1]) or not (0 <= next_position[1] <= currents_map.shape[0]):
            break
        
        if can_pass and (abs(heading + np.arctan2(boat.position[0]-end[0], boat.position[1]-end[1]) + np.pi/2) > np.pi/4) and not last:
            break

        boat.add(next_position, currents_map, heading)

        heading = -(np.arctan2(boat.position[0]-goal_pos[0], boat.position[1]-goal_pos[1]) + np.pi/2)
        
    if np.sqrt((boat.position[0] - goal_pos[0])**2 + (boat.position[1] - goal_pos[1])**2) <= precision and not can_pass: 
        boat.arrived = True

# ------------------------------ Route Following ----------------------------- #
def routeFollowing(boat: object, currents_map: np.ndarray, end: tuple[float, float], hydrodynamic_efficiency: float, calculations_tick: float):
    """Route following boat model
    boat: boat object
    currents_map: currents map
    end: end point coordinates (x, y) in meters
    hydrodynamic_efficiency: hydrodynamic efficiency
    calculations_tick: calculations tick in seconds
    """

    route = boat.model_params['route'].positions
    precision = boat.precision
    model = boat.model_params['model']

    for goal_pos in route:
        model(boat, currents_map, goal_pos, hydrodynamic_efficiency, calculations_tick, can_pass=True, end=end, last=np.all(goal_pos==route[-1]))
            
    if np.sqrt((boat.position[0] - end[0])**2 + (boat.position[1] - end[1])**2) <= precision: boat.arrived = True

# ----------------------------- Drift Correction ----------------------------- #
def driftCorrection(boat: object, currents_map: np.ndarray, end: tuple[float, float], hydrodynamic_efficiency: float):
    """Drift correction boat model
    boat: boat object
    currents_map: currents map
    end: end point coordinates (x, y) in meters
    """
    route = np.linspace(boat.position, end, 100)
    
    
# ---------------------------------------------------------------------------- #
#                                    Routes                                    #
# ---------------------------------------------------------------------------- #

# ------------------------------- Adapted Route ------------------------------ #
def adaptedRoute(routeObject: object, currents_map: np.ndarray, start: tuple[float, float], end: tuple[float, float]):
    """Adapt route from direct one
    route: route object
    currents_map: currents map
    start: (x, y) in meters
    end: (x, y) in meters
    """

    step = 10

    start, end = np.array(start), np.array(end)
    direct_route = [list(i/100 * (end-start) + start) for i in range(101)]
    direct_route = np.array([[int(i[0]), int(i[1])] for i in direct_route])
    routes = [direct_route]

    for k in range(step):
        routes.append(routes[-1].copy())
        for i in range(1,len(direct_route)-1):
            candidate_route = np.copy(routes[-1])
            candidate_route[i,1] -= 1
            if mrl.route.route_cost(candidate_route, currents_map) \
                < mrl.route.route_cost(routes[-1], currents_map):
                routes[-1] = candidate_route.copy()

    route = [(int(i[0]), int(i[1])) for i in routes[-1]]

    routeObject.history = routes


    smoothing_level = 15

    tck, u = spint.splprep(np.vstack((routeObject.history[-1][:,0],
                                      routeObject.history[-1][:,1])), s=0.0)
    u_new = np.linspace(u.min(), u.max(), smoothing_level)
    x_new, y_new = spint.splev(u_new, tck)

    routeObject.positions = np.array([x_new, y_new]).T

# ------------------------------- Direct route ------------------------------- #
def directRoute(routeObject: object, currents_map: np.ndarray, start: tuple[float, float], end: tuple[float, float]):
    """Direct route
    route: route object
    currents_map: currents map
    start: (x, y) in meters
    end: (x, y) in meters
    """
    start, end = np.array(start), np.array(end)
    direct_route = np.linspace(start, end, 30)

    routeObject.positions = direct_route
