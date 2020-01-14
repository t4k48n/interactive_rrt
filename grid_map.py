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
CELL_EDGE = 3
CELL_NODE = 4
CELL_OBSTACLE = 5

# 状態に対応する色。
COLOR_EMPTY = "white"
COLOR_START = "red"     # nodeと重複。
COLOR_GOAL = "red"      # nodeと重複。
COLOR_EDGE = "blue"
COLOR_NODE = "red"
COLOR_OBSTACLE = "black"

# セルの状態と色の対応
GRID_CMAP = colors.ListedColormap([COLOR_EMPTY, COLOR_START, COLOR_GOAL, COLOR_EDGE, COLOR_NODE, COLOR_OBSTACLE])
# セルの色境界。6色の境界は6 + 1 = 7個ある。
# セル状態が1間隔のiotaであることを仮定。
GRID_BOUNDS = [CELL_EMPTY, CELL_START, CELL_GOAL, CELL_EDGE, CELL_NODE, CELL_OBSTACLE, CELL_OBSTACLE+1]
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

    initialized = True

def set_cell(x, y, value):
    validate_initialized()

    x_index = int(round(x))
    y_index = int(round(y))

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

def quit():
    validate_initialized()

    global fig
    plt.close(fig)

    global initialized
    initialized = False
