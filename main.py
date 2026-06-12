from ursina import *
from panda3d.core import ClockObject
import math

app = Ursina()

mouse.visible = False
# mouse.locked = False

box = Entity(
    model='cube',
    name='front_object',
    color=color.azure,
    scale=(0.5, 0.5, 0.5),
    position=(0.0, 0.0, 5.0),
    rotation=(25, 45, 0)
)

lumina = DirectionalLight()
lumina.look_at(Vec3(1, -1, 1))

crosshair = Text(
    text='+',
    origin=(0, 0),
    scale=2,
    color=color.green,
    parent=camera.ui
)

tether_line = Entity(
    model='quad',
    color=color.rgba(0, 255, 0, 150),
    origin=(0, -0.5, 0),
    scale=(0.003, 0, 1),
    parent=camera.ui
)

MAX_ROTATION_SPEED = 90  
DEADZONE = 0.005

yaw = 0
pitch = 0
camera.rotation = (pitch, yaw, 0)
clock_obj = ClockObject.get_global_clock()

def update():
    global yaw, pitch

    if held_keys['escape']:
        application.quit()

    joy_x = mouse.position.x
    joy_y = mouse.position.y

    crosshair.position = (joy_x, joy_y)

    distance = math.sqrt(joy_x**2 + joy_y**2)
    
    if distance > 0:
        angle = math.degrees(math.atan2(joy_y, joy_x))
        tether_line.rotation_z = 90-angle
        tether_line.scale_y = distance
    else:
        tether_line.scale_y = 0

    if abs(joy_x) < DEADZONE: joy_x = 0
    if abs(joy_y) < DEADZONE: joy_y = 0

    yaw += joy_x * MAX_ROTATION_SPEED * time.dt
    pitch -= joy_y * MAX_ROTATION_SPEED * time.dt

    yaw = yaw % 360
    pitch = clamp(pitch, -89, 89)

    camera.rotation = (pitch, yaw, 0)

app.run()