from ursina import *

app = Ursina()

# FPS counter in the corner
fps_counter = Entity(parent=camera.ui)
Text(text='', position=(-0.85, 0.45), scale=1, origin=(0, 0), parent=fps_counter, name='fps_text')

# Update FPS text every frame
fps_text = fps_counter.children[0]

# Use Panda3D's global clock (works with Ursina)
from panda3d.core import ClockObject
clock_obj = ClockObject.get_global_clock()


def update():
    fps_text.text = f'FPS: {int(clock_obj.get_average_frame_rate())}'
    if held_keys['escape']:
        application.quit()









app.run()

