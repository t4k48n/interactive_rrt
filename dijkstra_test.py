import math
import numpy as np
import scipy.sparse.csgraph as sgraph

def distance_of_nodes(n1, n2):
    return math.sqrt((n1[0] - n2[0]) ** 2 + (n1[1] - n2[1]) ** 2)

edges = [((0, 0), (2, 2)), ((2, 2), (1, 4)), ((0, 0), (0, 2)), ((2, 2), (4, 4))]
nodes = [(0, 0), (2, 2), (1, 4), (0, 2), (4, 4)]

count_of_nodes = len(nodes)

G = np.zeros((count_of_nodes, count_of_nodes))
for edge in edges:
    start, end = edge
    r = nodes.index(start)
    c = nodes.index(end)
    G[r, c] = distance_of_nodes(start, end)

_, predecessors = sgraph.dijkstra(G, indices=0, return_predecessors=True)

indices_of_path = [count_of_nodes - 1]
while True:
    index_next = predecessors[indices_of_path[-1]]
    if index_next < 0:
        break
    indices_of_path.append(index_next)

print(indices_of_path)
nodes_of_path = [nodes[idx] for idx in reversed(indices_of_path)]
print(nodes_of_path)
