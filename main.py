import random
import math
import time
from threading import Thread

import pyaudio

import numpy as np
import scipy.sparse.csgraph as sgraph

import grid_map as gm

from bell import Bell

mode = None

MODE_DRAWING = 0
MODE_RUNNING = 1

NODE_START = (0, 0)
NODE_GOAL = None

def on_line(edge1, edge2):
    a = np.array(edge1[0])
    b = np.array(edge1[1])
    c = np.array(edge2[0])
    d = np.array(edge2[1])
    ab = b - a
    ac = c - a
    ad = d - a
    return np.linalg.matrix_rank(np.vstack([ab, ac, ad])) != 2

def intersected(edge1, edge2):
    if on_line(edge1, edge2):
        a = np.array(edge1[0])
        b = np.array(edge1[1])
        c = np.array(edge2[0])
        d = np.array(edge2[1])

        ab = np.linalg.norm(b - a)
        ac = np.linalg.norm(c - a)
        ad = np.linalg.norm(d - a)

        ba = np.linalg.norm(a - b)
        bc = np.linalg.norm(c - b)
        bd = np.linalg.norm(d - b)

        return not ((ac > ab and ad > ab) or (bd > ba and bc > ba))

    a = np.array(edge1[0])
    b = np.array(edge1[1])
    c = np.array(edge2[0])
    d = np.array(edge2[1])

    ab = b - a
    ac = c - a
    ad = d - a
    cond1 = np.cross(ab, ac) * np.cross(ab, ad) <= 0

    cd = d - c
    ca = a - c
    cb = b - c
    cond2 = np.cross(cd, ca) * np.cross(cd, cb) <= 0

    return cond1 and cond2

def get_edges_around(x, y):
    x_index, y_index = gm.get_index(x, y)
    point_lt = (x_index - 0.5, y_index - 0.5)
    point_rt = (x_index + 0.5, y_index - 0.5)
    point_rb = (x_index + 0.5, y_index + 0.5)
    point_lb = (x_index - 0.5, y_index + 0.5)
    return [(point_rt, point_lt),
            (point_rb, point_rt),
            (point_lb, point_rb),
            (point_lt, point_lb)]

def set_unset_obstacles_handler(event):
    global mode
    if mode != MODE_DRAWING:
        return
    x, y = event.xdata, event.ydata
    if x is None or y is None:
        return
    if event.button == gm.BUTTON_LEFTCLICK:
        gm.set_cell(x, y, gm.CELL_OBSTACLE)
        gm.set_title('DRAWING')
    elif event.button == gm.BUTTON_RIGHTCLICK:
        gm.set_cell(x, y, gm.CELL_EMPTY)
        gm.set_title('DRAWING')
    gm.set_cell(*NODE_START, gm.CELL_START)
    gm.set_cell(*NODE_GOAL, gm.CELL_GOAL)

def switch_mode(new_mode, title=None):
    MODE_TITLE = {MODE_RUNNING: 'RUNNING', MODE_DRAWING: 'DRAWING'}
    if new_mode not in (MODE_RUNNING, MODE_DRAWING):
        raise ValueError('unexpected mode given')

    global mode
    mode = new_mode

    if title is None:
        gm.set_title(MODE_TITLE[mode])
    else:
        gm.set_title(title)

    if mode == MODE_RUNNING:
        global thread_algorithm
        thread_algorithm = Thread(target=algorithm)
        thread_algorithm.start()
    if mode == MODE_DRAWING:
        gm.set_cell(*NODE_START, gm.CELL_START)
        gm.set_cell(*NODE_GOAL, gm.CELL_GOAL)

def switch_mode_handler(event):
    global mode
    if event.key == 'enter':
        if mode == MODE_RUNNING:
            switch_mode(MODE_DRAWING)
        elif mode == MODE_DRAWING:
            switch_mode(MODE_RUNNING)
        else:
            NotImplementedError('unexpected mode detected')

def distance_of_nodes(n1, n2):
    return math.sqrt((n1[0] - n2[0]) ** 2 + (n1[1] - n2[1]) ** 2)

INTERVAL_ALGORITHM = 0.1
GOAL_RATIO_ALGORITHM = 0.25
STEP_LENGTH_ALGORITHM = 3
TIMEOUT_ALGORITHM = 1000
COLOR_EDGE_ALGORITHM = 'tab:red'
WIDTH_EDGE_ALGORITHM = 10
COLOR_SHORTESTEDGE_ALGORITHM = 'tab:green'
WIDTH_SHORTESTEDGE_ALGORITHM = 15
thread_algorithm = None
def try_to_connect(new_node, base_node, nodes, edges, obstacles):
    if new_node in nodes or new_node in obstacles:
        return False, nodes, edges
    new_edge = (base_node, new_node)
    for obstacle in obstacles:
        for edge in get_edges_around(*obstacle):
            if intersected(edge, new_edge):
                return False, nodes, edges
    try:
        gm.set_cell(*new_node, gm.CELL_NODE)
        gm.ax.plot([new_node[0], base_node[0]], [new_node[1], base_node[1]], linewidth=WIDTH_EDGE_ALGORITHM, color=COLOR_EDGE_ALGORITHM)
    except RuntimeError:
        return False, nodes, edges
    plot_node_bell.play()
    nodes.append(new_node)
    edges.append(new_edge)
    return True, nodes, edges

def find_nodes_of_path_with_dijkstra(nodes, edges):
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

    return [nodes[idx] for idx in reversed(indices_of_path)]

def algorithm():
    clear_all_nodes()
    clear_all_edges()

    try:
        gm.set_cell(*NODE_START, gm.CELL_START)
        gm.set_cell(*NODE_GOAL, gm.CELL_GOAL)
    except RuntimeError:
        return
    time.sleep(INTERVAL_ALGORITHM)

    nodes = [NODE_START]
    edges = []
    try:
        obstacles = [(x, y) for x in range(gm.width) for y in range(gm.height) if gm.get_cell(x, y) == gm.CELL_OBSTACLE]
    except RuntimeError:
        return

    global mode
    retry_count = 0
    while mode == MODE_RUNNING and retry_count < TIMEOUT_ALGORITHM:
        if random.random() <= GOAL_RATIO_ALGORITHM:
            target_to_extend = NODE_GOAL
        else:
            try:
                target_to_extend = (random.randint(0, gm.width - 1), random.randint(0, gm.height - 1))
            except RuntimeError:
                return

        if target_to_extend in nodes:
            retry_count += 1
            continue

        # targetの最近傍ノード
        node_nearest = sorted(nodes, key=lambda n: distance_of_nodes(n, target_to_extend))[0]

        # 最近傍ノードからターゲットへSTEP_LENGTH_ALGORITHM分移動したノード（候補ノード）
        distance = distance_of_nodes(target_to_extend, node_nearest)
        if distance < STEP_LENGTH_ALGORITHM:
            scale = 1
        else:
            scale = STEP_LENGTH_ALGORITHM / distance
        x_candidate = node_nearest[0] + scale * (target_to_extend[0] - node_nearest[0])
        y_candidate = node_nearest[1] + scale * (target_to_extend[1] - node_nearest[1])
        try:
            node_candidate = gm.get_index(x_candidate, y_candidate)
        except RuntimeError:
            return

        ok, nodes, edges = try_to_connect(node_candidate, node_nearest, nodes, edges, obstacles)
        if not ok:
            retry_count += 1
            continue
        if node_candidate == NODE_GOAL:
            nodes_of_path = find_nodes_of_path_with_dijkstra(nodes, edges)
            for node in nodes_of_path:
                try:
                    gm.set_cell(*node, gm.CELL_SHORTESTNODE)
                except RuntimeError:
                    return
            try:
                gm.set_cell(*NODE_START, gm.CELL_START)
                gm.set_cell(*NODE_GOAL, gm.CELL_GOAL)
                x_series = [node[0] for node in nodes_of_path]
                y_series = [node[1] for node in nodes_of_path]
                gm.ax.plot(x_series, y_series, linewidth=WIDTH_SHORTESTEDGE_ALGORITHM, color=COLOR_SHORTESTEDGE_ALGORITHM)
            except RuntimeError:
                return
            search_succeeded_bell.play()
            switch_mode(MODE_DRAWING, 'SUCCESS ({} steps)'.format(len(nodes_of_path) - 1))
            return
        retry_count = 0
        time.sleep(INTERVAL_ALGORITHM)
    switch_mode(MODE_DRAWING, 'FAILED or ABORTED')

def clear_all_cells():
    for y in range(gm.height):
        for x in range(gm.width):
            gm.set_cell(x, y, gm.CELL_EMPTY)

def clear_all_cells_handler(event):
    global mode
    if event.key == 'c':
        if mode == MODE_DRAWING:
            clear_all_cells()
            clear_all_edges()
            gm.set_title('DRAWING')

def clear_all_nodes():
    objects_like_node = set((gm.CELL_START, gm.CELL_GOAL, gm.CELL_SHORTESTNODE, gm.CELL_NODE))
    for y in range(gm.height):
        for x in range(gm.width):
            if gm.get_cell(x, y) in objects_like_node:
                gm.set_cell(x, y, gm.CELL_EMPTY)
    gm.set_cell(*NODE_START, gm.CELL_START)
    gm.set_cell(*NODE_GOAL, gm.CELL_GOAL)

def clear_all_nodes_handler(event):
    global mode
    if event.key == 'n':
        if mode == MODE_DRAWING:
            clear_all_nodes()
            gm.set_title('DRAWING')

def clear_all_edges():
    for ln in gm.ax.get_lines():
        ln.remove()

def clear_all_edges_handler(event):
    global mode
    if event.key == 'e':
        if mode == MODE_DRAWING:
            clear_all_edges()
            gm.set_title('DRAWING')

INTERVAL_DRAWER = 0.02
def _drawer():
    while True:
        time.sleep(INTERVAL_DRAWER)
        try:
            gm.draw()
        except RuntimeError:
            return

if __name__ == '__main__':
    try:
        pa = pyaudio.PyAudio()
        plot_node_bell = Bell(pa, './type01.wav')
        search_succeeded_bell = Bell(pa, './type10.wav')
        gm.init(30, 15)
        NODE_GOAL = (gm.width - 1, gm.height - 1)
        switch_mode(MODE_DRAWING)
        gm.connect('button_press_event', set_unset_obstacles_handler)
        gm.connect('motion_notify_event', set_unset_obstacles_handler)
        gm.connect('key_press_event', switch_mode_handler)
        gm.connect('key_press_event', clear_all_cells_handler)
        gm.connect('key_press_event', clear_all_nodes_handler)
        gm.connect('key_press_event', clear_all_edges_handler)
        thread_drawer = Thread(target=_drawer)
        thread_drawer.start()
        gm.plt.show()
    finally:
        gm.quit()
        thread_drawer.join()
        if thread_algorithm is not None:
            thread_algorithm.join()
        search_succeeded_bell.close()
        plot_node_bell.close()
        pa.terminate()
