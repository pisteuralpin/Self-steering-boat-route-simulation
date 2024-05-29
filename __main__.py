# ---------------------------------------------------------------------------- #
#                               Import libraries                               #
# ---------------------------------------------------------------------------- #

import time
start_time = time.perf_counter()

import numpy as np
import datetime
import json

import matplotlib.pyplot as plt

from modules.currents import CurrentMap
from modules.boats import Boat
from modules.routes import Route
from modules import models

import MRLib as mrl

plt.ion()                                                                      # Interactive mode

# ---------------------------------------------------------------------------- #
#                                 Parameters                                   #
# ---------------------------------------------------------------------------- #

# ----------------------------------- Map ------------------------------------ #

size = (160, 90)                                                               # (x, y) in meters

currents_mesh_X, currents_mesh_Y = np.meshgrid(np.arange(size[0]),
                                               np.arange(size[1]))             # Meshgrid for currents

# ----------------------------------- POI ------------------------------------ #

start = (5, 45)                                                                # (x, y) in meters
end = (155, 45)                                                                # (x, y) in meters

# -------------------------------- Currents ---------------------------------- #

currents_max_speed = 2
currents_dispersion = .3

currents_models = ["No currents", "Uniform currents", "Random currents"]
# currents_model = mrl.display.menu(currents_models, "Currents model")[0]-1
currents_model = 2

# ----------------------------- Boats parameters ----------------------------- #

boats_base_speed = 2 # m/s
calculations_tick = .1 # s
precision = .25 # m

hydrodynamic_efficiency = 1
# ----------------------------- Prints parameters ---------------------------- #

print("---- Parameters: ----")
print(f"🗺️  Map size: {size[0]}x{size[1]} m")
print(f"🏳️  Start: {start}, 🏁 End: {end}")
print(f"🌊 Currents model: {currents_models[currents_model]}")
print(f"⏱️  Currents max speed: {currents_max_speed} m/s")
print(f"🔀 Currents dispersion: {currents_dispersion}")
print(f"⛵ Boats base speed: {boats_base_speed} m/s")
print(f"🚤 Hydrodynamic efficiency: {hydrodynamic_efficiency}")
print(f"🕐 Calculations tick: {calculations_tick}s")
print(f"🧭 Initial heading: {90 - (mrl.geometry.direction(start, end) / np.pi * 180):.2f}°")

# ---------------------------------- Routes ---------------------------------- #

adaptedRoute = Route("Route adaptée aux courants", start,
                     models.adaptedRoute, color='#7800CB')
directRoute = Route("Ligne directe", start,
                    models.directRoute, color='#CB00C7')

routes = [adaptedRoute, directRoute]

# -------------------------------- Print routes ------------------------------ #
print("----- 🧭 Routes -----")
for r in routes:
    print(f"- {r.name}")

# ---------------------------------- Boats ----------------------------------- #

inertBoat = Boat("Bateau inerte", start,
                 boats_base_speed, hydrodynamic_efficiency, calculations_tick=calculations_tick)

initialHeadedBoat = Boat("Maintien de cap", start,
                         boats_base_speed, hydrodynamic_efficiency,
                         models.directionKeeping, precision=precision, color='#CC2D2D',
                         modelParams={'model': models.directionKeeping},
                         calculations_tick=calculations_tick)

GPSheadedBoat = Boat("Guidage GPS", start,
                     boats_base_speed, hydrodynamic_efficiency,
                     models.controlledPositionPICorrector, precision=precision, color='#88BE1B',
                     calculations_tick=calculations_tick)

driftCorrectionBoat = Boat("Correction de la dérive", start,
                           boats_base_speed, hydrodynamic_efficiency,
                           models.driftCorrection, precision=precision, color='#941BBE',
                           calculations_tick=calculations_tick)

currentsAdaptedBoatPI = Boat("Suivi de la route adaptée", start,
                            boats_base_speed, hydrodynamic_efficiency,
                            models.routeFollowing, precision=precision, color='#72FF70',
                            modelParams={'route': adaptedRoute, 'model': models.controlledPositionPICorrector},
                            calculations_tick=calculations_tick)

directRouteBoat = Boat("Suivi de la ligne directe", start,
                          boats_base_speed, hydrodynamic_efficiency,
                          models.routeFollowing, precision=precision, color='#BE1B88',
                          modelParams={'route': directRoute, 'model': models.controlledPositionPICorrector},
                          calculations_tick=calculations_tick)


boats = [inertBoat, initialHeadedBoat, GPSheadedBoat, currentsAdaptedBoatPI, directRouteBoat]

# -------------------------------- Print boats ------------------------------- #

print("----- ⛵ Boats -----")
for b in boats:
    print(f"- {b.name}")

# ---------------------------------------------------------------------------- #
#                               Generate currents                              #
# ---------------------------------------------------------------------------- #

print("---- 📟 Calculations ----")

step_time = time.perf_counter()

print("▶ Currents")
print("Generating currents...")

with open(f"results/231220 currents.npy", "rb") as f: #{datetime.datetime.now().strftime('%y%m%d')}
    currents_map = np.load(f)

currents = CurrentMap(size, currents_model, currents_max_speed,
                      currents_dispersion, currents_map=currents_map)
currents_map = currents.get_currents()
currents_speeds = currents.speeds

# with open(f"results/{datetime.datetime.now().strftime('%y%m%d')} currents.npy", "wb") as f:
#     np.save(f, currents_map)

print(f"✅ Currents generated in {time.perf_counter()-step_time:.2f}s")

# ---------------------------------------------------------------------------- #
#                                   Calculate                                  #
# ---------------------------------------------------------------------------- #

# ---------------------------------- Routes ---------------------------------- #

step_time = time.perf_counter()

print("▶ Routes")
print("Calculating routes...")
for r in routes:
    model_time = time.perf_counter()
    r.calculate(currents_map, end)
    r.calculations_duration = time.perf_counter()-model_time
    print(f"✔ {r.name} in {time.perf_counter()-model_time:.3f}s")
print(f"✅ Routes calculated in {time.perf_counter()-step_time:.2f}s")

# ----------------------------------- Boats ---------------------------------- #

step_time = time.perf_counter()

print("▶ Boats")
print("Calculating boats trajectories...")
for b in boats:
    model_time = time.perf_counter()
    b.calculate(currents_map, end)
    b.calculations_duration = time.perf_counter()-model_time
    print(f"✔ {b.name} in {time.perf_counter()-model_time:.3f}s")
print(f"✅ Boats trajectories calculated in {time.perf_counter()-step_time:.3f}s")

# ---------------------------------------------------------------------------- #
#                                   Plot map                                   #
# ---------------------------------------------------------------------------- #

step_time = time.perf_counter()

print("---- 📈 Plotting ----")
print("Plotting map...")

plt.figure("Map")
# plt.title("Self steering boat simulation")
plt.xlim(0, size[0]-1)
plt.xticks(np.arange(0, size[0], 10))
plt.xlabel(r"$x \ (m)$")
plt.ylim(0, size[1]-1)
plt.yticks(np.arange(0, size[1], 10))
plt.ylabel(r"$y \ (m)$")
plt.gca().set_aspect(1)
plt.grid(which='major', alpha=0.5)
plt.minorticks_on()
plt.grid(which='minor', alpha=0.2)

print("✔ Map set-up")

# ------------------------------- Plot currents ------------------------------ #

if currents_model <= 1:
    plt.gca().set_facecolor('#88E7EA')

if currents_model >= 1:
    plt.streamplot(currents_mesh_X, currents_mesh_Y, currents_map[:,:,0],
                   currents_map[:,:,1],
                   color='k', density=1.5, linewidth=0.5, arrowsize=0.5)       # Plot currents direction

if currents_model >= 2:
    plt.contourf(currents_mesh_X, currents_mesh_Y, currents_speeds,
                levels = np.linspace(np.min(currents_speeds),
                                     np.max(currents_speeds), 20))             # Plot currents speed
    plt.colorbar(label=r"$Vitesse \ des \ courants\ (m/s)$", extend='neither',
                 ticks=np.linspace(0, currents_max_speed, 5))

print("✔ Currents plotted")

# -------------------------------- Plot routes ------------------------------- #

# for i in range(len(adaptedRoute.history)):
#     plt.plot(adaptedRoute.history[i][:,0], adaptedRoute.history[i][:,1],
#              label=f'Étape {i}', linestyle=':')
    
for r in routes:
    plt.plot(r.positions[:,0], r.positions[:,1], r.color,
             label=r.name, linestyle='--')

print("✔ Routes plotted")

# -------------------------------- Plot boats -------------------------------- #

for b in boats:
    plt.plot(b.positions[:,0], b.positions[:,1], b.color, label=b.name)

print("✔ Boats plotted")

# ---------------------------------------------------------------------------- #

plt.plot([start[0]], [start[1]], 'w*')
plt.plot([end[0]], [end[1]], 'r*')

plt.legend(loc = 'lower center', bbox_to_anchor = (0.5, 0),
           fancybox = True, ncols = 3, fontsize = 6)

plt.savefig(f'results/{datetime.datetime.now().strftime("%y%m%d")} map.png',
            dpi=300, transparent=True, bbox_inches='tight')

print("✔ Map saved")
print(f"✅ Map plotted in {time.perf_counter()-step_time:.3f}s")

# ---------------------------------------------------------------------------- #
#                                 Plot minimap                                 #
# ---------------------------------------------------------------------------- #

step_time = time.perf_counter()

print("Plotting minimap...")

plt.figure("Minimap")
plt.xticks(np.arange(0, size[0], 10))
plt.yticks(np.arange(0, size[1], 10))
plt.gca().set_aspect(1)
plt.grid(which='major', alpha=0.5)
plt.minorticks_on()
plt.grid(which='minor', alpha=0.2)
# plt.yticks(np.arange(0, size[1], 1), minor=True)
# plt.xticks(np.arange(0, size[0], 1), minor=True)

print("✔ Map set-up")

# ------------------------------- Plot currents ------------------------------ #

if currents_model <= 1:
    plt.gca().set_facecolor('#88E7EA')

if currents_model >= 1:
    plt.streamplot(currents_mesh_X, currents_mesh_Y, currents_map[:,:,0],
                   currents_map[:,:,1],
                   color='k', density=1.5, linewidth=0.5, arrowsize=0.5)       # Plot currents direction

if currents_model >= 2:
    plt.contourf(currents_mesh_X, currents_mesh_Y, currents_speeds,
                levels = np.linspace(np.min(currents_speeds),
                                     np.max(currents_speeds), 20))             # Plot currents speed

print("✔ Currents plotted")

# -------------------------------- Plot routes ------------------------------- #

plt.plot([start[0], end[0]], [start[1], end[1]], 'r--',
         label="Ligne directe", linewidth=0.5)

# for i in range(len(adaptedRoute.history)):
#     plt.plot(adaptedRoute.history[i][:,0], adaptedRoute.history[i][:,1],
#              label=f'Step {i}', linestyle=':')
    
for r in routes:
    plt.plot(r.positions[:,0], r.positions[:,1], r.color,
             label=r.name, linestyle='--')

print("✔ Routes plotted")

# -------------------------------- Plot boats -------------------------------- #

for b in boats:
    plt.plot(b.positions[:,0], b.positions[:,1], b.color, label=b.name)

print("✔ Boats plotted")

# ---------------------------------------------------------------------------- #

plt.plot([start[0], end[0]], [start[1], end[1]], 'r*')

plt.xlim(44,68)
plt.ylim(34,50)

# plt.xlim(95, 100)
# plt.ylim(30, 35)

plt.savefig(f'results/{datetime.datetime.now().strftime("%y%m%d")} minimap.png',
            dpi=300, transparent=True, bbox_inches='tight')

print("✔ Map saved")
print(f"✅ Map plotted in {time.perf_counter()-step_time:.3f}s")

# ---------------------------------------------------------------------------- #
#                                  Plot datas                                  #
# ---------------------------------------------------------------------------- #

step_time = time.perf_counter()

print("Plotting datas...")

fig, axs = plt.subplots(4, 1, sharex=True)
# plt.suptitle("Self steering boat simulation datas")

Mx = calculations_tick * max(len(b.speeds) for b in boats)

# ----------------------------------- Speed ---------------------------------- #
for b in boats:
    axs[0].plot(np.arange(0,len(b.speeds)*calculations_tick, calculations_tick),
                b.speeds, color=b.color, label=b.name)


axs[0].set_ylabel(r"$Speed\ (m/s)$")
m, M = int(np.min(np.concatenate([b.speeds for b in boats])))-.5, \
        int(np.max(np.concatenate([b.speeds for b in boats])))+.5
axs[0].set_yticks(np.arange(-10, 10.1, 1))
axs[0].set_yticks(np.arange(-10, 10.1, .5), minor=True)
axs[0].minorticks_on()
axs[0].grid(which='major', alpha=0.7, axis='y')
axs[0].grid(which='minor', alpha=0.3, axis='y')
axs[0].set_ylim(m, M)

print("✔ Speed plotted")

# --------------------------------- Direction -------------------------------- #
for b in boats:
    axs[1].plot(np.arange(0,len(b.directions)*calculations_tick, calculations_tick),
                b.directions*180/np.pi, color=b.color, label=b.name)


axs[1].set_ylabel(r"$Direction\ (^\circ)$")
m, M = int(np.min(np.concatenate([b.directions*180/np.pi for b in boats])) / (90)-1), \
        int(np.max(np.concatenate([b.directions*180/np.pi for b in boats])) / (90)+1)
axs[1].set_yticks(np.arange(-360, 360.1, 90))
axs[1].set_yticks(np.arange(-360, 360.1, 45), minor=True)
axs[1].minorticks_on()
axs[1].grid(which='major', alpha=0.7, axis='y')
axs[1].grid(which='minor', alpha=0.3, axis='y')
axs[1].set_ylim(m*90, M*90)

print("✔ Direction plotted")

# ------------------------------- Currents work ------------------------------ #
for b in boats:
    axs[2].plot(np.arange(0,len(b.powers)*calculations_tick, calculations_tick),
                b.powers, color=b.color, label=b.name)


axs[2].set_ylabel(r"$Currents \ work\ (UA)$")
m, M = int(np.min(np.concatenate([b.powers for b in boats]))-1), \
        int(np.max(np.concatenate([b.powers for b in boats]))+1)
axs[2].set_yticks(np.arange(-10, 10.1, 2))
axs[2].set_yticks(np.arange(10, 10.1, 1), minor=True)
axs[2].minorticks_on()
axs[2].grid(which='major', alpha=0.7, axis='y')
axs[2].grid(which='minor', alpha=0.3, axis='y')
axs[2].set_ylim(m, M)

print("✔ Currents work plotted")

# ------------------------------ Currents speed ------------------------------ #
for b in boats:
    axs[3].plot(np.arange(0,(len(b.speeds)+1)*calculations_tick, calculations_tick),
                currents_speeds[b.positions[:,1].astype(int), b.positions[:,0].astype(int)],
                b.color, label=b.name)


axs[3].set_ylabel(r"$Currents \ speed \ (m/s)$")
m, M = int(np.min(np.concatenate([currents_speeds[
                                                    b.positions[:,1].astype(int),
                                                    b.positions[:,0].astype(int)
                                                 ] for b in boats]))-1), \
    int(np.max(np.concatenate([currents_speeds[
                                                b.positions[:,1].astype(int),
                                                b.positions[:,0].astype(int)
                                              ] for b in boats]))+1)
axs[3].set_yticks(np.arange(-10, 10.1, 1))
axs[3].set_yticks(np.arange(-10, 10.1, .5), minor=True)
axs[3].minorticks_on()
axs[3].grid(which='major', alpha=0.7, axis='y')
axs[3].grid(which='minor', alpha=0.3, axis='y')
axs[3].set_ylim(m, M)

print("✔ Currents speed plotted")

# ---------------------------------------------------------------------------- #

for i in range(4): axs[i].set_xlim(0,Mx)

handles, labels = plt.gca().get_legend_handles_labels()
fig.legend(handles, labels, loc="outside lower center",
           fancybox = True, ncols = 3, fontsize = 'small')

plt.subplots_adjust(bottom=0.2)

plt.xlabel(r"$Temps\ (s)$")

plt.savefig(f'results/{datetime.datetime.now().strftime("%y%m%d")} datas.png',
            dpi=300, transparent=True, bbox_inches='tight')

print(f"✅ Datas plotted in {time.perf_counter()-step_time:.2f}s")

# ---------------------------------------------------------------------------- #
#                                 Plot stats 1                                 #
# ---------------------------------------------------------------------------- #

step_time = time.perf_counter()

print("Plotting stats 1...")

fig, axs = plt.subplots(3, 1, sharex=True)
# plt.suptitle("Self steering boat simulation stats")

# ------------------------------ Time of arrival ----------------------------- #
for b in boats:
    if b.arrived:
        print(b.name, calculations_tick * len(b.positions))
        axs[0].bar(b.name, calculations_tick * len(b.positions),
                   color=b.color, label=b.name)

# axs[0].set_ylabel(r"$Arrival \ time\ (s)$")
axs[0].minorticks_on()
axs[0].grid(which='major', alpha=0.7, axis='y')
axs[0].grid(which='minor', alpha=0.3, axis='y')

print("✔ Time of arrival plotted")

# ---------------------------- Total negative work --------------------------- #
for b in boats:
    if b.steering_model != None:
        print(b.name, np.sum([p for p in b.powers if p<0]))
        axs[1].bar(b.name, np.abs(np.sum([p for p in b.powers if p<0])),
                   color=b.color, label=b.name)

# axs[1].set_ylabel(r"$Total \ negative \ work\ (UA)$")
axs[1].minorticks_on()
axs[1].grid(which='major', alpha=0.7, axis='y')
axs[1].grid(which='minor', alpha=0.3, axis='y')

print("✔ Total work plotted")

# ----------------------------- Direction changes ---------------------------- #
for b in boats:
    if b.steering_model != None:
        print(b.name, np.sum(np.abs(np.diff(b.directions)))*180/np.pi)
        axs[2].bar(b.name, np.sum(np.abs(np.diff(b.directions)))*180/np.pi,
                   color=b.color, label=b.name)

# axs[2].set_ylabel(r"$\sum \left| d\theta \right| \ (deg)$")
axs[2].minorticks_on()
axs[2].grid(which='major', alpha=0.7, axis='y')
axs[2].grid(which='minor', alpha=0.3, axis='y')

print("✔ Direction changes plotted")

# ---------------------------------------------------------------------------- #

handles, labels = plt.gca().get_legend_handles_labels()
fig.legend(handles, labels, loc="outside lower center", 
           fancybox = True, ncols = 3, fontsize = 'small')
plt.gca().set_xticklabels([])

# plt.subplots_adjust(bottom=0.2)

plt.savefig(f'results/{datetime.datetime.now().strftime("%y%m%d")} stats_1.png',
            dpi=300, transparent=True, bbox_inches='tight')

print(f"✅ Stats 1 plotted in {time.perf_counter()-step_time:.2f}s")

# ---------------------------------------------------------------------------- #
#                                 Plot stats 2                                 #
# ---------------------------------------------------------------------------- #

step_time = time.perf_counter()

print("Plotting stats 2...")

fig, axs = plt.subplots(1, 1, sharex=True)
# plt.suptitle("Self steering boat simulation stats 2")

# --------------------------------- Distance --------------------------------- #
for b in boats:
    if b.steering_model != None:
        axs.plot(np.arange(0,(len(b.speeds)+1)*calculations_tick, calculations_tick),
                 np.sqrt((end[0]-b.positions[:,0])**2 + (end[1]-b.positions[:,1])**2),
                 color=b.color, label=b.name)

axs.set_ylabel(r"$Distance \ (m)$")
axs.minorticks_on()
axs.grid(which='major', alpha=0.7, axis='y')
axs.grid(which='minor', alpha=0.3, axis='y')
# axs[0].legend(fancybox = True, ncols = 3, fontsize = 'small')

print("✔ Distance plotted")

# ---------------------------------------------------------------------------- #

handles, labels = plt.gca().get_legend_handles_labels()
fig.legend(handles, labels, loc="outside lower center", 
           fancybox = True, ncols = 3, fontsize = 'small')

plt.subplots_adjust(bottom=0.2)

plt.savefig(f'results/{datetime.datetime.now().strftime("%y%m%d")} stats_2.png',
            dpi=300, transparent=True, bbox_inches='tight')

print(f"✅ Stats 2 plotted in {time.perf_counter()-step_time:.2f}s")

# ---------------------------------------------------------------------------- #
#                                 Models stats                                 #
# ---------------------------------------------------------------------------- #

step_time = time.perf_counter()

print("Plotting models stats...")

fig, axs = plt.subplots(1, 1, sharex=True)
# plt.suptitle("Self steering boat simulation models stats")

# ----------------------------- Calculation time ----------------------------- #
for b in boats:
    axs.bar(b.name, b.calculations_duration, color=b.color, label=b.name)

for r in routes:
    axs.bar(r.name, r.calculations_duration, color=r.color, label=r.name)

axs.set_ylabel(r"$Calculation \ time \ (s)$")
axs.minorticks_on()
axs.grid(which='major', alpha=0.7, axis='y')
axs.grid(which='minor', alpha=0.3, axis='y')
# axs[0].legend(fancybox = True, ncols = 3, fontsize = 'small')

print("✔ Calculation time plotted")

# ---------------------------------------------------------------------------- #

handles, labels = plt.gca().get_legend_handles_labels()
fig.legend(handles, labels, loc="outside lower center", 
           fancybox = True, ncols = 3, fontsize = 'small')
plt.gca().set_xticklabels([])

plt.subplots_adjust(bottom=0.2)

plt.savefig(f'results/{datetime.datetime.now().strftime("%y%m%d")} models_stats.png',
            dpi=300, transparent=True, bbox_inches='tight')

print(f"✅ Models stats plotted in {time.perf_counter()-step_time:.2f}s")

# ---------------------------------------------------------------------------- #
#                                  Data export                                 #
# ---------------------------------------------------------------------------- #

step_time = time.perf_counter()

print("Exporting datas...")

datas = {}
for b in boats:
    datas[b.name] = {
        # 'speed': list(b.speeds),
        'max_speed': np.max(b.speeds),
        # 'direction': list(b.directions),
        'direction_changes': np.sum(np.abs(np.diff(b.directions)))*180/np.pi,
        # 'power': list(b.powers),
        'total_negative_work': np.sum([p for p in b.powers if p<0]),
        # 'currents_speed': list(currents_speeds[b.positions[:,1].astype(int), b.positions[:,0].astype(int)]),
        'time_of_arrival': len(b.positions)*calculations_tick,
    }

with open(f"results/{datetime.datetime.now().strftime('%y%m%d')} datas.csv", "w") as f:
    f.write(mrl.export.dictToCSV(datas))
print("✔ CSV datas exported")

with open(f"results/{datetime.datetime.now().strftime('%y%m%d')} datas.json", "w") as f:
    f.write(json.dumps(datas, indent=2))
print("✔ JSON datas exported")

print(f"✅ Datas exported in {time.perf_counter()-step_time:.2f}s")

# ---------------------------------------------------------------------------- #
#                               End of the script                              #
# ---------------------------------------------------------------------------- #

print(f"✅ Simulation done in {time.perf_counter()-start_time:.2f}s")

plt.show(block=True)
