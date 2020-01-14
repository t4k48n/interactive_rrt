import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np

from matplotlib.backend_bases import MouseButton

plt.close("all")

# 0 -> white
# 1 -> red
# 2 -> blue
# 3 -> black
cmap = colors.ListedColormap(["white", "red", "blue", "black"])
bounds = [0, 0.5, 1.5, 2.5, 3.0]
norm = colors.BoundaryNorm(bounds, cmap.N)

width = 40
height = 30

data = np.round(np.random.rand(height, width) * (cmap.N - 1))
fig, ax = plt.subplots()
ax.imshow(data, cmap=cmap, norm=norm)
ax.set_xticks(np.linspace(-0.5, (width - 1) + 0.5, width + 1))
ax.set_yticks(np.linspace(-0.5, (height - 1) + 0.5, height + 1))
ax.set_xticklabels([])
ax.set_yticklabels([])
ax.grid()
cursor_plot, = ax.plot([], [], "x")
def on_move(ev):
    if ev.button:
        if ev.button is MouseButton.LEFT:
            print("LEFT DRAG")
        elif ev.button is MouseButton.RIGHT:
            print("RIGHT DRAG")
        x = ev.xdata
        y = ev.ydata
        cursor_plot.set_data(x, y)
        plt.draw()
def on_click(ev):
    if ev.button:
        if ev.button is MouseButton.LEFT:
            print("LEFT CLICK")
        elif ev.button is MouseButton.RIGHT:
            print("RIGHT CLICK")
        x = ev.xdata
        y = ev.ydata
        cursor_plot.set_data(x, y)
        plt.draw()
def on_input(ev):
    if ev.key == "enter":
        print("State switch")
    elif ev.key == "c":
        print("Cleared")
def on_input_(ev):
    if ev.key == "enter":
        print("State switch2")
    elif ev.key == "c":
        print("Cleared2")
fig.canvas.mpl_connect("motion_notify_event", on_move)
fig.canvas.mpl_connect('button_press_event', on_click)
fig.canvas.mpl_connect('key_press_event', on_input)
fig.canvas.mpl_connect('key_press_event', on_input_)
plt.show()
