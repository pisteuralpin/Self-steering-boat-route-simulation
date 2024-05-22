# ----------------------------------------------------------- #
#         SELF-STEERING BOAT AND CURRENTS SIMULATION          #
#  ©2023 Mathurin Roulier, PTSI Lycée Lesage, Vannes, France  #
# ----------------------------------------------------------- #

# ----------------------------------------------------------- #
#                       Import modules                        #
# ----------------------------------------------------------- #
import matplotlib.pyplot as plt
import numpy as np
import random as rd
import sys
sys.path.insert(0, "C:\\Users\\rouli\\Documents\\Dev\\py-packages")
import MRLib                                                                    # Import my own library
import modules.currents as crt                                                  # Import currents module

plt.ion()                                                                       # Interactive mode

# ----------------------------------------------------------- #
#                   Currents parameters                       #
# ----------------------------------------------------------- #

size = (160,90)                                                                 # Size of the map (X, Y)
dispersion = 0.3                                                                # Dispersion of currents
currents_vmax = 1                                                               # Max current speed

X_current, Y_current = np.meshgrid(np.arange(size[0]), np.arange(size[1]))      # Meshgrid for currents

print(f"Currents max step : {round(currents_vmax,2)} m/s")                      # Print currents max speed

currents_models = ["None", "Uniform currents", "Random currents"]               # Currents models list
ask_for_currents_model = False                                                  # Does the user want to choose the currents model ?
if ask_for_currents_model: selected_currents_model = MRLib.menu(currents_models, "Choose currents type :")[0]-1 # Ask for currents model
else: selected_currents_model = 2                                               # Else, here is the currents model

if selected_currents_model == 0:
    currents_map = crt.noCurrents(size)                                         # If no currents, set currents to 0
elif selected_currents_model == 1:
    currents_map = crt.uniformCurrents(size, currents_vmax)                     # If uniform currents, set currents to currents_vmax
elif selected_currents_model == 2:
    currents_map = crt.randomCurrents(size, currents_vmax, dispersion)          # If random currents, generate currents
    currents_speeds = currents_map[0]**2 + currents_map[1]**2                   # Compute currents speed
else:
    currents_map = crt.noCurrents(size)                                         # Else, set currents to 0

# # ----------------------------------------------------------- #
# #                       Boat parameters                       #
# # ----------------------------------------------------------- #
start_pos = (5,size[1]//2-5)                                                        # Initial position of the boat
goal_pos = (size[0]-5, size[1]//2-5)                                                # Goal position of the boat

ini_dir = np.arctan((goal_pos[1]-start_pos[1])/(goal_pos[0]-start_pos[0]))          # Initial direction of the boat
print(f"Initial heading : {round(360 - ini_dir/np.pi*180,1)}°")                     # Print initial heading

drift = 1                                                                           # Drift coefficient
step = 1                                                                            # Simulation step

times0, times1, times2, times3 = [], [], [], []                                         # time list for each model
directions2, directions3 = [], []                                                       # Directions list for model 2
distances0, distances1, distances2, distances3 = [], [], [], []                     # Distance list for each model
speeds0, speeds1, speeds2, speeds3 = [], [], [], []                                 # Speed list for each model

# # ----------------------------------------------------------- #
# #                   Boat movement - Inert                     #
# #                No movement, just drifting                   #
# # ----------------------------------------------------------- #

boat_pos_inert = np.array([[start_pos[0]], [start_pos[1]]])

if selected_currents_model != 0:
    i = 0
    ini_dir = np.pi / 2
    # Repeat while boat is inside the plot or far from the goal
    while (0 <= int(boat_pos_inert[0, -1:]) < size[0]) and (0 <= int(boat_pos_inert[1, -1:]) < size[1]) and (np.sqrt((boat_pos_inert[0, -1:]-goal_pos[0])**2 + (boat_pos_inert[1, -1:]-goal_pos[1])**2) > 1):
        # Append to boat_pos array the future position : last + current drift
        boat_pos_inert = np.append(boat_pos_inert,
                            boat_pos_inert[:,-1:] \
                                + currents_map[:, int(boat_pos_inert[0,i:i+1]), int(boat_pos_inert[1,i:i+1])] * drift,
                            axis=1)
        distances0.append(np.sqrt((boat_pos_inert[0, -1:]-goal_pos[0])**2 + (boat_pos_inert[1, -1:]-goal_pos[1])**2))
        speeds0.append(np.sqrt((boat_pos_inert[0, -1:]-boat_pos_inert[0, -2:-1])**2 + (boat_pos_inert[1, -1:]-boat_pos_inert[1, -2:-1])**2))
        i+=1

        times0.append(i*step)

# # ----------------------------------------------------------- #
# #                  Boat movement - Model 1                    #
# #         The boat just follow the initial heading            #
# # ----------------------------------------------------------- #
boat_pos = np.array([[start_pos[0]], [start_pos[1]]])                           # Boat position array with initial position

i = 0
ini_dir = np.pi / 2                                                             # Initial direction
# Repeat while boat is inside the plot or far from the goal
while (0 <= int(boat_pos[0, -1:]) < size[0]) and (0 <= int(boat_pos[1, -1:]) < size[1]) and (np.sqrt((boat_pos[0, -1:]-goal_pos[0])**2 + (boat_pos[1, -1:]-goal_pos[1])**2) > 1):
    # Append to boat_pos array the future position : last + current drift + initial heading
    boat_pos = np.append(boat_pos,
                        boat_pos[:,-1:] \
                            + currents_map[:, int(boat_pos[0,i:i+1]), int(boat_pos[1,i:i+1])] * drift \
                            + step * np.array([[np.sin(ini_dir)], [np.cos(ini_dir)]]),
                        axis=1)
    i+=1
    
    distances1.append(np.sqrt((boat_pos[0, -1:]-goal_pos[0])**2 + (boat_pos[1, -1:]-goal_pos[1])**2))
    speeds1.append(np.sqrt((boat_pos[0, -1:]-boat_pos[0, -2:-1])**2 + (boat_pos[1, -1:]-boat_pos[1, -2:-1])**2))
    times1.append(i*step)

# # ----------------------------------------------------------- #
# #                  Boat movement - Model 2                    #
# #   The boat continually adapt its heading towards the goal   #
# # ----------------------------------------------------------- #
boat_pos2 = np.array([[start_pos[0]], [start_pos[1]]])                          # Boat position array
i         = 0

# Repeat while boat is inside the plot or far from the goal
while (0 <= int(boat_pos2[0, -1:]) < size[0]) and \
      (0 <= int(boat_pos2[1, -1:]) < size[1]) and \
      (np.sqrt((boat_pos2[0, -1:]-goal_pos[0])**2 + (boat_pos2[1, -1:]-goal_pos[1])**2) > 1):
    
    if directions2 == []:
        direction = MRLib.direction(goal_pos, boat_pos2[:,-1:])
    else:
        direction = MRLib.direction(goal_pos, boat_pos2[:,-1:], directions2[-1])
    
    # Append to boat_pos array the future position : last + current drift + direction to goal
    boat_pos2 = np.append(boat_pos2,
                        boat_pos2[:,-1:] \
                            + currents_map[:, int(boat_pos[1,i:i+1]), int(boat_pos[0,i:i+1])] * drift \
                            + step * np.array([np.cos(direction), np.sin(direction)]),
                        axis = 1)
    distances2.append(np.sqrt((boat_pos2[0, -1:]-goal_pos[0])**2 + (boat_pos2[1, -1:]-goal_pos[1])**2))
    speeds2.append(np.sqrt((boat_pos2[0, -1:]-boat_pos2[0, -2:-1])**2 + (boat_pos2[1, -1:]-boat_pos2[1, -2:-1])**2))
    i += 1

    directions2.append(float(direction))
    times2.append(i*step)

# # ----------------------------------------------------------- #
# #                  Boat movement - Model 3                    #
# #             The boat anticipates the currents               #
# # ----------------------------------------------------------- #

# boat_pos3 = np.array([[start_pos[0]], [start_pos[1]]])                          # Boat position array
# i         = 0

# # Repeat while boat is inside the plot or far from the goal
# while (0 <= int(boat_pos3[0, -1:]) < size[0]) and \
#       (0 <= int(boat_pos3[1, -1:]) < size[1]) and \
#       (np.sqrt((boat_pos3[0, -1:]-goal_pos[0])**2 + (boat_pos3[1, -1:]-goal_pos[1])**2) > 1):
    
#     if directions3 == []:
#         direction = MRLib.direction(goal_pos, boat_pos3[:,-1:])
#     else:
#         direction = MRLib.direction(goal_pos, boat_pos3[:,-1:], directions2[-1])
    
#     # Append to boat_pos array the future position : last + current drift + direction to goal
#     boat_pos2 = np.append(boat_pos3,
#                         boat_pos3[:,-1:] \
#                             + currents_map[:, int(boat_pos[1,i:i+1]), int(boat_pos[0,i:i+1])] * drift \
#                             + step * np.array([np.cos(direction), np.sin(direction)]),
#                         axis = 1)
#     distances3.append(np.sqrt((boat_pos2[0, -1:]-goal_pos[0])**2 + (boat_pos3[1, -1:]-goal_pos[1])**2))
#     speeds3.append(np.sqrt((boat_pos3[0, -1:]-boat_pos3[0, -2:-1])**2 + (boat_pos3[1, -1:]-boat_pos3[1, -2:-1])**2))
#     i += 1

#     directions3.append(float(direction))
#     times2.append(i*step)

# ----------------------------------------------------------- #
#                       Plot currents                         #
# ----------------------------------------------------------- #
plt.figure("Self-steering boat within a currents field")                        # Create a new figure

# plt.imshow(currents_map[0,:,:], cmap='gray', interpolation='none')

if selected_currents_model > 0:
    plt.streamplot(X_current, Y_current, currents_map[0], currents_map[1], color='k', density=1.5, linewidth=0.5, arrowsize=0.5)    # Plot currents direction
if selected_currents_model > 1:
    plt.contourf(X_current, Y_current, currents_speeds, \
                levels = np.linspace(np.min(currents_speeds), \
                                    np.max(currents_speeds), 20))                            # Plot currents speed
    plt.colorbar(label=r"$Vitesse\ (m/s)$", extend='neither', ticks=np.linspace(0, currents_vmax, 5))                                          # Add a colorbar
plt.gca().set_aspect('equal', adjustable='box')                                 # Set the plot aspect ratio to 1

# ----------------------------------------------------------- #
#                         Plot boat                           #
# ----------------------------------------------------------- #
plt.plot([start_pos[0], goal_pos[0]], [start_pos[1], goal_pos[1]], ':r', label='Direct path')   # Plot direct path between start and goal
plt.plot(boat_pos_inert[0], boat_pos_inert[1], 'gray', label='Drifting inert boat')             # Plot inert boat trajectory
plt.plot(boat_pos[0], boat_pos[1], 'g', label='Model 1')                                        # Plot model 1 boat trajectory
plt.plot(boat_pos2[0], boat_pos2[1], 'm', label='Model 2')                                      # Plot model 2 boat trajectory
plt.plot(start_pos[0], start_pos[1], '*g', markersize=10)                                       # Plot start position
plt.plot(goal_pos[0], goal_pos[1], '*r', markersize=10)                                         # Plot goal position

# ----------------------------------------------------------- #
#                         Plot style                          #
# ----------------------------------------------------------- #

plt.xticks(np.arange(0,size[0],10))                                                             # Set x ticks
plt.yticks(np.arange(0,size[1],10))                                                             # Set y ticks

plt.xlabel("x (m)")                                                                             # Set x label
plt.ylabel("y (m)")                                                                             # Set y label
plt.title('Self-steering boat trajectory simulation')                                           # Set title
if selected_currents_model == 2:
    plt.legend(loc = 'upper center', bbox_to_anchor = (0.5, -0.2),
                fancybox = True, ncol = 3)                                                      # Set legend
else:
    plt.legend(loc = 'upper center', bbox_to_anchor = (0.5, -0.15),
                fancybox = True, ncol = 2)                                                      # Set legend

plt.xlim(0,size[0]-1)                                                                           # Set x limits
plt.ylim(0,size[1]-1)                                                                           # Set y limits
plt.grid(True)                                                                                  # Set grid

plt.savefig('230607 result.png', dpi=300, transparent=True)                                     # Save figure

# ----------------------------------------------------------- #
#                          Plot data                          #
# ----------------------------------------------------------- #

plt.figure("Self steering boat data")                                                           # Create a new figure

if selected_currents_model == 2:
    plt.subplot(2,1,1)                                                                              # Create a subplot
    plt.subplots_adjust(hspace=0.5)                                                                 # Adjust subplots
    plt.plot(times0[:150], distances0[:150], 'gray', label='Inert boat distance')                               # Plot inert boat distance
    plt.plot(times1[:150], distances1[:150], 'g', label='Model 1 Distance')                                     # Plot model 1 boat distance
    plt.plot(times2[:150], distances2[:150], 'm', label='Model 2 Distance')                                     # Plot model 2 boat distance
    plt.xlabel("Time (s)")                                                                          # Set x label
    plt.ylabel("Distance (m)")                                                                      # Set y label
    plt.title('Self-steering boat distances')                                                       # Set title

    plt.subplot(2,1,2)                                                                              # Create a subplot
    plt.plot(times0[:150], speeds0[:150], linestyle=':', color='gray', label='Inert boat speed')                # Plot inert boat speed
    plt.plot(times1[:150], speeds1[:150], linestyle=':', color='green', label='Model 1 Speed')                  # Plot model 1 boat speed
    plt.plot(times2[:150], speeds2[:150], linestyle=':', color='magenta', label='Model 2 Speed')                # Plot model 2 boat speed
    plt.xlabel("Time (s)")                                                                          # Set x label
    plt.ylabel("Speed (m/s)")                                                                       # Set y label
    plt.title('Self-steering boat speeds')                                                          # Set title
else:
    plt.subplots_adjust(hspace=0.5)                                                                 # Adjust subplots
    plt.plot(times0, distances0, 'gray', label='Inert boat distance')                               # Plot inert boat distance
    plt.plot(times1, distances1, 'g', label='Model 1 Distance')                                     # Plot model 1 boat distance
    plt.plot(times2, distances2, 'm', label='Model 2 Distance')                                     # Plot model 2 boat distance
    plt.xlabel("Time (s)")                                                                          # Set x label
    plt.ylabel("Distance (m)")                                                                      # Set y label
    plt.title('Self-steering boat distances')                                                       # Set title


plt.savefig('230607 datas.png', dpi=300, transparent=True)

plt.pause(-1)