import matplotlib.pyplot as plt
import numpy as np
import random as rd

plt.ion()

# ----------------------------------------------------------- #
#                   Currents parameters                       #
# ----------------------------------------------------------- #

size = (160,90)                                                                     # Size of the map (X, Y)
dispersion = 0.3                                                                    # Dispersion of currents
vmax = .5                                                                           # Max current speed

dispermin = 1 - dispersion
dispermax = 1 + dispersion

X_current, Y_current = np.meshgrid(np.arange(size[0]), np.arange(size[1]))          # Meshgrid for currents
currents_map = np.ones((2,size[1],size[0]))                                         # Currents map (composante, X, Y)
currents_map[:,0,0] = 1                                                             # Initial current at the bottom left

# ----------------------------------------------------------- #
#                  Generate random currents                   #
# ----------------------------------------------------------- #

for i in range(1,size[1]-1):
    for j in range(1,size[0]-1):
        currents_map[0,i+1,j+1] = np.average([currents_map[0,i,j] * rd.uniform(dispermin, dispermax), currents_map[0,i+1,j] * rd.uniform(dispermin, dispermax), currents_map[0,i,j+1] * rd.uniform(dispermin, dispermax)])
        currents_map[1,i+1,j+1] = np.average([currents_map[1,i,j] * rd.uniform(dispermin, dispermax), currents_map[1,i+1,j] * rd.uniform(dispermin, dispermax), currents_map[1,i,j+1] * rd.uniform(dispermin, dispermax)])

currents_map[:,0,:] = currents_map[:,1,:]
currents_map[:,:,-1] = currents_map[:,:,-2]
    
currents_map[:,:,:] = currents_map[:,:,:] * vmax / np.max(currents_map[:,:,:])

# ----------------------------------------------------------- #
#                       Plot currents                         #
# ----------------------------------------------------------- #

plt.figure("Courants")

plt.contourf(X_current, Y_current, currents_map[0]**2 + currents_map[1]**2, levels=np.linspace(np.min(currents_map[0]**2 + currents_map[1]**2), np.max(currents_map[0]**2 + currents_map[1]**2),20))
plt.colorbar(label=r"Vitesse $(m/s)$")
plt.streamplot(X_current, Y_current, currents_map[0], currents_map[1], color='k', density=1.5, linewidth=0.5, arrowsize=0.5)
plt.gca().set_aspect('equal', adjustable='box')

plt.xticks(np.arange(0,size[0],10))
plt.yticks(np.arange(0,size[1],10))

plt.grid(True)

plt.savefig('archive/230317 result.png', dpi=300)                                                # Save figure

plt.pause(-1)