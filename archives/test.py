import numpy as np
import heapq

def heuristic(a, b):
    return np.dot(a, b)

def astar_search(field, start, goal):
    rows, cols, _ = field.shape
    open_list = []
    closed_set = set()

    # Chaque nœud dans la file d'attente est un tuple contenant (coût, position, chemin)
    heapq.heappush(open_list, (0, start, []))

    while open_list:
        cost, current, path = heapq.heappop(open_list)

        if current == goal:
            return path

        if current in closed_set:
            continue

        closed_set.add(current)

        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue

                r, c = current[0] + dr, current[1] + dc

                if 0 <= r < rows and 0 <= c < cols:
                    new_cost = cost + heuristic(field[r, c], goal - field[current])
                    heapq.heappush(open_list, (new_cost, (r, c), path + [(r, c)]))

    return None

# Exemple d'utilisation
field = np.random.rand(90, 160, 2)  # Remplacez cela par votre champ de vecteur
start = (0, 0)
goal = (89, 159)
path = astar_search(field, start, goal)
print("Chemin optimal:", path)
