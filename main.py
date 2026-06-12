from ursina import *
from panda3d.core import ClockObject

app = Ursina()

mouse.locked = False
mouse.visible = True

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

MAX_ROTATION_SPEED = 90

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

    DEADZONE = 0.03
    if abs(joy_x) < DEADZONE: joy_x = 0
    if abs(joy_y) < DEADZONE: joy_y = 0

    
    yaw += joy_x * MAX_ROTATION_SPEED * time.dt
    pitch -= joy_y * MAX_ROTATION_SPEED * time.dt

    yaw = yaw % 360
    pitch = clamp(pitch, -89, 89)

    camera.rotation = (pitch, yaw, 0)

app.run()