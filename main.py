import grid_map as gm

def set_obstacle(x, y):
    if x is None or y is None:
        return
    gm.set_cell(x, y, gm.CELL_OBSTACLE)

def unset_obstacle(x, y):
    if x is None or y is None:
        return
    gm.set_cell(x, y, gm.CELL_EMPTY)

def set_unset_obstacles_handler(event):
    global mode
    if mode != MODE_DRAWING:
        return
    if event.button == gm.BUTTON_LEFTCLICK:
        set_obstacle(event.xdata, event.ydata)
        gm.draw()
    elif event.button == gm.BUTTON_RIGHTCLICK:
        unset_obstacle(event.xdata, event.ydata)
        gm.draw()

def switch_mode(new_mode):
    if new_mode == MODE_RUNNING:
        title = "RUNNING"
    elif new_mode == MODE_DRAWING:
        title = "DRAWING"
    global mode
    mode = new_mode
    gm.set_title(title)
    gm.draw()

def switch_mode_handler(event):
    global mode
    if event.key == "enter":
        if mode == MODE_RUNNING:
            switch_mode(MODE_DRAWING)
        elif mode == MODE_DRAWING:
            switch_mode(MODE_RUNNING)
        else:
            NotImplementedError("unexpected mode detected")

def clear_all_cells():
    for y in range(gm.height):
        for x in range(gm.width):
            unset_obstacle(x, y)
    gm.draw()

def clear_all_cells_handler(event):
    global mode
    if event.key == "c":
        if mode == MODE_DRAWING:
            clear_all_cells()

mode = None

MODE_DRAWING = 0
MODE_RUNNING = 1

if __name__ == "__main__":
    gm.init(40, 30)
    switch_mode(MODE_DRAWING)
    gm.connect('button_press_event', set_unset_obstacles_handler)
    gm.connect("motion_notify_event", set_unset_obstacles_handler)
    gm.connect('key_press_event', switch_mode_handler)
    gm.connect('key_press_event', clear_all_cells_handler)
    try:
        gm.plt.show()
    finally:
        gm.quit()
