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
from modules.score import create_score_matrix
from modules import models

import MRLib as mrl


# ---------------------------------------------------------------------------- #
#                                 Parameters                                   #
# ---------------------------------------------------------------------------- #

loops = 100

# ----------------------------------- Map ------------------------------------ #

size = (160, 90)                                                               # (x, y) in meters

currents_mesh_X, currents_mesh_Y = np.meshgrid(np.arange(size[0]),
                                               np.arange(size[1]))             # Meshgrid for currents

# ----------------------------------- POI ------------------------------------ #

start = (5, 45)                                                                # (x, y) in meters
end = (155, 45)                                                                # (x, y) in meters

# -------------------------------- Currents ---------------------------------- #

currents_max_speed = 2.5
currents_dispersion = .3

currents_models = ["No currents", "Uniform currents", "Random currents"]
# currents_model = mrl.display.menu(currents_models, "Currents model")[0]-1
currents_model = 2

# ----------------------------- Boats parameters ----------------------------- #

boats_base_speed = 2 # m/s
hydrodynamic_efficiency = .7
calculations_tick = .1 # s
precision = .25 # m

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
#                                  Loop start                                  #
# ---------------------------------------------------------------------------- #
    
print("---- 📟 Calculations ----")
print("Calculating steps...")

datas= {
    "datas": []
}

for k in range(loops):

    datas['datas'].append({})

    step_time = time.perf_counter()

    # ------------------------------- Currents ------------------------------- #

    currents = CurrentMap(size, currents_model, currents_max_speed,
                        currents_dispersion)
    currents_map = currents.get_currents()
    currents_speeds = currents.speeds

    # -------------------------------- Routes -------------------------------- #

    for r in routes:
        model_time = time.perf_counter()
        r.calculate(currents_map, end)
        r.calculations_duration = time.perf_counter()-model_time

    # --------------------------------- Boats -------------------------------- #

    for b in boats:
        model_time = time.perf_counter()
        b.calculate(currents_map, end)
        b.calculations_duration = time.perf_counter()-model_time

        datas['datas'][k][b.name] = {
            # 'speed': list(b.speeds),
            'max_speed': np.max(b.speeds),
            # 'direction': list(b.directions),
            'direction_changes': np.sum(np.abs(np.diff(b.directions)))*180/np.pi,
            # 'power': list(b.powers),
            'total_negative_work': np.sum([p for p in b.powers if p<0]),
            # 'currents_speed': list(currents_speeds[b.positions[:,1].astype(int), b.positions[:,0].astype(int)]),
            'time_of_arrival': len(b.positions)*calculations_tick,
        }

    # -------------------------------- Reset boat -------------------------------- #
        
    for b in boats:
        b.reset()

    print(f"✔ Step {k+1} calculated in {time.perf_counter()-step_time:.2f}s")

# ---------------------------------------------------------------------------- #
#                              End of simulations                              #
# ---------------------------------------------------------------------------- #

with open(f"results/{datetime.datetime.now().strftime('%y%m%d')} loop_datas.json", "w") as f:
    f.write(json.dumps(datas, indent=2))

print(f"✅ Simulations done in {time.perf_counter()-start_time:.2f}s")

# ---------------------------------------------------------------------------- #
#                                 File parsing                                 #
# ---------------------------------------------------------------------------- #

step_time = time.perf_counter()

with open(f"results/{datetime.datetime.now().strftime('%y%m%d')} loop_datas.json", "r") as f:
    datas = json.loads(f.read())

parsed_datas = {}

for k in range(len(datas['datas'])):
    for boat in datas['datas'][k]:
        if boat not in ['Bateau inerte', 'Maintien de cap']:
            if boat not in parsed_datas:
                parsed_datas[boat] = {
                    'direction_changes': [],
                    'total_negative_work': [],
                    'time_of_arrival': [],
                }
            parsed_datas[boat]['direction_changes'].append(
                datas['datas'][k][boat]['direction_changes'] 
                / datas['datas'][k]['Guidage GPS']['direction_changes'] 
                if datas['datas'][k]['Guidage GPS']['direction_changes'] != 0 
                else 0)
            parsed_datas[boat]['total_negative_work'].append(
                datas['datas'][k][boat]['total_negative_work'] 
                / datas['datas'][k]['Guidage GPS']['total_negative_work'] 
                if datas['datas'][k]['Guidage GPS']['total_negative_work'] != 0 
                else 0)
            parsed_datas[boat]['time_of_arrival'].append(
                datas['datas'][k][boat]['time_of_arrival'] 
                / datas['datas'][k]['Guidage GPS']['time_of_arrival'] 
                if datas['datas'][k]['Guidage GPS']['time_of_arrival'] != 0 
                else 0)

print(f"File parsed in {time.perf_counter()-step_time:.2f}s")

# ---------------------------------------------------------------------------- #
#                           Plot average models stats                          #
# ---------------------------------------------------------------------------- #

step_time = time.perf_counter()

print("Plotting average models stats...")

fig, axs = plt.subplots(3, 1, sharex=True)
# plt.suptitle("Self steering boat simulation stats")

# ------------------------------ Time of arrival ----------------------------- #
for b in parsed_datas:
    color = [boat.color for boat in boats if boat.name == b][0]
    axs[0].bar(b, np.mean(parsed_datas[b]['time_of_arrival']),
               yerr=np.std(parsed_datas[b]['time_of_arrival']),
                color=color, label=b)

# axs[0].set_ylabel(r"$Arrival \ time\ (s)$")
axs[0].minorticks_on()
axs[0].grid(which='major', alpha=0.7, axis='y')
axs[0].grid(which='minor', alpha=0.3, axis='y')

print("✔ Time of arrival plotted")

# ---------------------------- Total negative work --------------------------- #
for b in parsed_datas:
    color = [boat.color for boat in boats if boat.name == b][0]
    axs[1].bar(b, np.mean(parsed_datas[b]['total_negative_work']),
                yerr=np.std(parsed_datas[b]['total_negative_work']),
                color=color, label=b)

# axs[1].set_ylabel(r"$Total \ negative \ work\ (UA)$")
axs[1].set_yscale('log')
axs[1].minorticks_on()
axs[1].grid(which='major', alpha=0.7, axis='y')
axs[1].grid(which='minor', alpha=0.3, axis='y')

print("✔ Total work plotted")

# ----------------------------- Direction changes ---------------------------- #
for b in parsed_datas:
    color = [boat.color for boat in boats if boat.name == b][0]
    axs[2].bar(b, np.mean(parsed_datas[b]['direction_changes']),
                yerr=np.std(parsed_datas[b]['direction_changes']),          
                color=color, label=b)

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

plt.savefig(f'results/{datetime.datetime.now().strftime("%y%m%d")} avg_model_stats.png',
            dpi=300, transparent=True, bbox_inches='tight')

print(f"✅ Average models stats plotted in {time.perf_counter()-step_time:.2f}s")

# ---------------------------------------------------------------------------- #

print(f"✅ Script executed in {time.perf_counter()-start_time:.2f}s")

plt.show(block= True)