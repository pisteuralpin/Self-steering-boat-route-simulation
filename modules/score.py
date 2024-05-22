import numpy as np

def create_score_matrix(currents_map: np.ndarray):
    """Create the score matrix. The score matrix contains the score of each cell of the currents map to reach their neighbors, score is calculated by a dot product of relative direction and currents direction (and its speed).
    currents_map: currents map
    """
    cm_size = currents_map.shape[:2]
    score_matrix = np.inf * np.ones([cm_size[0] * cm_size[1]]*2)

    for i in range(cm_size[0]):
        for j in range(cm_size[1]):
            k = i*cm_size[1] + j                        # Current cell index
            if i == j:
                score_matrix[k, k] = 0
            if i > 0:                                   # Up cell
                score_matrix[k, k-cm_size[0]] = np.dot(currents_map[i, j, :], np.array([0, -1]))
            if i < cm_size[0]-1:                        # Down cell
                score_matrix[k, k+cm_size[0]] = np.dot(currents_map[i, j, :], np.array([0, 1]))
            if j > 0:                                   # Left cell
                score_matrix[k, k-1] = np.dot(currents_map[i, j, :], np.array([-1, 0]))
            if j < cm_size[1]-1:                        # Right cell
                score_matrix[k, k+1] = np.dot(currents_map[i, j, :], np.array([1, 0]))
            if i > 0 and j > 0:                         # Up left cell
                score_matrix[k, k-cm_size[0]-1] = np.dot(currents_map[i, j, :], np.array([-1, -1]))
            if i > 0 and j < cm_size[1]-1:              # Up right cell
                score_matrix[k, k-cm_size[0]+1] = np.dot(currents_map[i, j, :], np.array([1, -1]))
            if i < cm_size[0]-1 and j > 0:              # Down left cell
                score_matrix[k, k+cm_size[0]-1] = np.dot(currents_map[i, j, :], np.array([-1, 1]))
            if i < cm_size[0]-1 and j < cm_size[1]-1:   # Down right cell
                score_matrix[k, k+cm_size[0]+1] = np.dot(currents_map[i, j, :], np.array([1, 1]))

    score_matrix[score_matrix != np.inf] *= -1

    return score_matrix


def map_coords_to_index(coords: tuple[int, int], map_size: tuple[int, int]):
    """Map coordinates to index
    coords: coordinates (x, y)
    map_size: map size (width, height)
    """
    return coords[0] + coords[1] * map_size[0]

def index_to_map_coords(index: int, map_size: tuple[int, int]):
    """Map index to coordinates
    index: index
    map_size: map size (width, height)
    """
    return (index % map_size[0], index // map_size[0])