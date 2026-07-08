from ursina import *
from panda3d.core import ClockObject # pyrefly: ignore [missing-import]
import math
import random

app = Ursina()
window.color = color.black

class SpaceDust:
    def __init__(self, num_particles=600, radius=200):
        self.radius = radius
        self.particles = []
        for _ in range(num_particles):
            p = Entity(
                model='sphere',
                color=color.rgba(200, 220, 255, 180),
                scale=random.uniform(0.02, 0.08),
                position=self.get_random_pos(Vec3(0,0,0)),
                unlit=True # Make it visible regardless of lighting
            )
            self.particles.append(p)

    def get_random_pos(self, center):
        return center + Vec3(
            random.uniform(-self.radius, self.radius),
            random.uniform(-self.radius, self.radius),
            random.uniform(-self.radius, self.radius)
        )

    def update(self):
        cam_pos = camera.position
        for p in self.particles:
            if p.x - cam_pos.x > self.radius: p.x -= self.radius * 2
            elif p.x - cam_pos.x < -self.radius: p.x += self.radius * 2
            
            if p.y - cam_pos.y > self.radius: p.y -= self.radius * 2
            elif p.y - cam_pos.y < -self.radius: p.y += self.radius * 2
            
            if p.z - cam_pos.z > self.radius: p.z -= self.radius * 2
            elif p.z - cam_pos.z < -self.radius: p.z += self.radius * 2

space_dust = SpaceDust()

mouse.visible = False
# mouse.locked = False

box = Entity(
    model='cube',
    name='front_object',
    color=color.azure,
    scale=(5.0, 5.0, 5.0),
    position=(0.0, 0.0, 30.0),
    rotation=(25, 45, 0)
)

lumina = DirectionalLight()
lumina.look_at(Vec3(1, -1, 1))

# Fixed center crosshair
center_crosshair = Text(
    text='+',
    origin=(0, 0),
    scale=2,
    color=color.cyan,
    parent=camera.ui
)

# Arrow pointing in the direction of the mouse
direction_arrow = Text(
    text='^',
    color=color.cyan,
    scale=2.5,
    origin=(0, 0),
    parent=camera.ui
)

DEADZONE = 0.005

# GUI Sliders Background
slider_bg = Entity(
    model='quad',
    color=color.rgba(255, 255, 255, 180),
    scale=(0.7, 0.2),
    position=(-0.55, -0.4),
    parent=camera.ui,
    z=1
)

# GUI Sliders
sensitivity_slider = Slider(min=100, max=300, default=200, text='Sensitivity', dynamic=True, position=(-0.65, -0.35), scale=0.7)
sensitivity_slider.label.color = color.black
sensitivity_slider.knob.text_entity.color = color.black

acceleration_slider = Slider(min=300, max=600, default=400, text='Acceleration', dynamic=True, position=(-0.65, -0.40), scale=0.7)
acceleration_slider.label.color = color.black
acceleration_slider.knob.text_entity.color = color.black

max_speed_slider = Slider(min=0, max=200, default=100, text='Max Speed', dynamic=True, position=(-0.65, -0.45), scale=0.7)
max_speed_slider.label.color = color.black
max_speed_slider.knob.text_entity.color = color.black

# Physics configuration
velocity = Vec3(0, 0, 0)
roll_velocity = 0.0
DRAG = 2.0  # Deceleration when coupled mode is on

coupled_mode = True

clock_obj = ClockObject.get_global_clock()

def input(key):
    global coupled_mode
    if key == 'c':
        coupled_mode = not coupled_mode
        print(f"Coupled Mode: {'ON' if coupled_mode else 'OFF'}")

def update():
    global velocity, roll_velocity, coupled_mode

    if held_keys['escape']:
        application.quit()

    # Slider key bindings
    if held_keys['t']: sensitivity_slider.value += 100 * time.dt
    if held_keys['g']: sensitivity_slider.value -= 100 * time.dt
    
    if held_keys['y']: acceleration_slider.value += 50 * time.dt
    if held_keys['h']: acceleration_slider.value -= 50 * time.dt
    
    if held_keys['u']: max_speed_slider.value += 150 * time.dt
    if held_keys['j']: max_speed_slider.value -= 150 * time.dt

    joy_x = mouse.position.x
    joy_y = mouse.position.y

    distance = math.sqrt(joy_x**2 + joy_y**2)
    
    if distance > DEADZONE:
        direction_arrow.position = (joy_x, joy_y)
        angle = math.degrees(math.atan2(joy_y, joy_x))
        direction_arrow.rotation_z = 90 - angle
        direction_arrow.color = color.cyan
    else:
        direction_arrow.color = color.clear

    if abs(joy_x) < DEADZONE: joy_x = 0
    if abs(joy_y) < DEADZONE: joy_y = 0

    current_sens = sensitivity_slider.value
    delta_yaw = joy_x * current_sens * time.dt
    delta_pitch = -joy_y * current_sens * time.dt

    current_accel = acceleration_slider.value
    current_max_speed = max_speed_slider.value

    roll_acceleration = current_accel * 5.0
    roll_input = 0
    if held_keys['q']: roll_input -= 1
    if held_keys['e']: roll_input += 1

    if roll_input != 0:
        roll_velocity += roll_input * roll_acceleration * time.dt
    else:
        roll_velocity = lerp(roll_velocity, 0, DRAG * 2 * time.dt)
        if abs(roll_velocity) < 0.1:
            roll_velocity = 0

    max_roll_speed = current_max_speed * 1.5
    roll_velocity = clamp(roll_velocity, -max_roll_speed, max_roll_speed)

    delta_roll = roll_velocity * time.dt
    camera.rotate((delta_pitch, delta_yaw, delta_roll))

    # --- Physics / Translation ---
    acceleration = Vec3(0, 0, 0)
    if held_keys['w']: acceleration += camera.forward
    if held_keys['s']: acceleration += camera.back
    if held_keys['d']: acceleration += camera.right
    if held_keys['a']: acceleration += camera.left
    if held_keys['space']: acceleration += camera.up
    if held_keys['left shift'] or held_keys['control']: acceleration += camera.down

    # Normalize acceleration so diagonal isn't faster
    if acceleration.length() > 0:
        acceleration = acceleration.normalized() * current_accel * time.dt
        velocity += acceleration

    # Apply drag if coupled mode is on and no keys are pressed
    if coupled_mode:
        if acceleration.length() == 0:
            velocity = lerp(velocity, Vec3(0, 0, 0), DRAG * time.dt)
            if velocity.length() < 0.1:
                velocity = Vec3(0, 0, 0)

    # Cap max speed
    if velocity.length() > current_max_speed:
        velocity = velocity.normalized() * current_max_speed

    # Apply velocity to camera position
    camera.position += velocity * time.dt
    
    space_dust.update()

app.run()