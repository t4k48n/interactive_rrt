import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np

from matplotlib.backend_bases import MouseButton
BUTTON_LEFTCLICK = MouseButton.LEFT
BUTTON_RIGHTCLICK = MouseButton.RIGHT

# 値は1間隔のiotaにすること。
CELL_EMPTY = 0
CELL_START = 1
CELL_GOAL = 2
CELL_SHORTESTNODE = 3
CELL_NODE = 4
CELL_OBSTACLE = 5

# 状態に対応する色。
COLOR_EMPTY = "white"
COLOR_START = "tab:cyan"     # nodeと重複。
COLOR_GOAL = "tab:orange"      # nodeと重複。
COLOR_SHORTESTNODE = "tab:green"
COLOR_NODE = "tab:blue"
COLOR_OBSTACLE = "black"

# セルの状態と色の対応
GRID_CMAP = colors.ListedColormap([COLOR_EMPTY, COLOR_START, COLOR_GOAL, COLOR_SHORTESTNODE, COLOR_NODE, COLOR_OBSTACLE])
# セルの色境界。6色の境界は6 + 1 = 7個ある。
# セル状態が1間隔のiotaであることを仮定。
GRID_BOUNDS = [CELL_EMPTY, CELL_START, CELL_GOAL, CELL_SHORTESTNODE, CELL_NODE, CELL_OBSTACLE, CELL_OBSTACLE+1]
# GRID_CMAP, GRID_BOUNDSを使った色標本。
GRID_NORM = colors.BoundaryNorm(GRID_BOUNDS, GRID_CMAP.N)

initialized = False
width, height = 0, 0
fig, ax, im = None, None, None
data = None

def validate_initialized():
    global initialized
    if not initialized:
        raise RuntimeError("map not initialized")

def init(width_, height_):
    global initialized
    if initialized:
        raise RuntimeError("map already initialized")

    for k in plt.rcParams:
        if k.split(".")[0] == "keymap":
            plt.rcParams[k] = []
    plt.rcParams["keymap.fullscreen"].append("f")
    plt.rcParams["keymap.quit"].append("q")

    global width, height
    width = width_
    height = height_

    global data
    data = np.ones((height, width), dtype=int) * CELL_EMPTY

    global fig, ax
    fig, ax = plt.subplots()
    ax.set_xticks(np.linspace(-0.5, width - 0.5, width + 1))
    ax.set_yticks(np.linspace(-0.5, height - 0.5, height + 1))
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.grid()

    global im
    im = ax.imshow(data, cmap=GRID_CMAP, norm=GRID_NORM)

    fig.subplots_adjust()

    initialized = True

def get_index(x, y):
    validate_initialized()

    x_index = int(round(x))
    y_index = int(round(y))

    return (x_index, y_index)

def get_linspace_indices(start_xy, end_xy, num):
    xs, ys = start_xy
    xe, ye = end_xy
    x_series = np.linspace(xs, xe, num)
    y_series = np.linspace(ys, ye, num)
    indices_with_duplication = [get_index(*xy) for xy in zip(x_series, y_series)]
    indices = list(dict.fromkeys(indices_with_duplication))
    return indices

def get_cell(x, y):
    validate_initialized()

    x_index, y_index = get_index(x, y)

    global data
    return data[y_index, x_index]


def set_cell(x, y, value):
    validate_initialized()

    x_index, y_index = get_index(x, y)

    global data
    data[y_index, x_index] = value

def set_title(title_str):
    validate_initialized()

    global ax
    ax.set_title(title_str)

def draw():
    validate_initialized()

    global im, data
    im.set_array(data)
    plt.draw()

def pause(interval):
    validate_initialized()

    global im, data
    im.set_array(data)
    plt.pause(interval)

def connect(event_name, handler):
    validate_initialized()

    global fig
    fig.canvas.mpl_connect(event_name, handler)

# 生成したフィギュアを閉じて、initializedフラグをオフ。二重呼び出し可能。
def quit():
    global fig
    if fig is not None:
        plt.close(fig)

    global initialized
    initialized = False
