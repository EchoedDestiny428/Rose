from ursina import *
import math

class UIManager(Entity):
    def __init__(self):
        super().__init__()
        
        self.deadzone = 0.005
        self.cursor_pos = Vec2(0, 0)
        self.max_radius = 0.1
        mouse.locked = True

        # Crosshair
        self.center_crosshair = Text(
            text='+',
            origin=(0, 0),
            scale=2,
            color=color.cyan,
            parent=camera.ui
        )

        # Direction Arrow
        self.direction_arrow = Text(
            text='^',
            color=color.cyan,
            scale=1.5,
            origin=(0, 0),
            parent=camera.ui
        )

        # Background Box
        self.slider_bg = Entity(
            model='quad',
            color=color.rgba(255, 255, 255, 180),
            scale=(0.7, 0.25),
            position=(-0.55, -0.375),
            parent=camera.ui,
            z=1
        )

        # Sliders
        self.sensitivity_slider = Slider(min=100, max=300, default=200, text='Sensitivity', dynamic=True, position=(-0.65, -0.30), scale=0.7)
        self.sensitivity_slider.label.color = color.black
        self.sensitivity_slider.knob.text_entity.color = color.black

        self.acceleration_slider = Slider(min=400, max=600, default=500, text='Acceleration', dynamic=True, position=(-0.65, -0.35), scale=0.7)
        self.acceleration_slider.label.color = color.black
        self.acceleration_slider.knob.text_entity.color = color.black

        self.max_speed_slider = Slider(min=0, max=200, default=100, text='Max Speed', dynamic=True, position=(-0.65, -0.40), scale=0.7)
        self.max_speed_slider.label.color = color.black
        self.max_speed_slider.knob.text_entity.color = color.black

        self.fov_slider = Slider(min=60, max=130, default=90, text='FOV', dynamic=True, position=(-0.65, -0.45), scale=0.7)
        self.fov_slider.label.color = color.black
        self.fov_slider.knob.text_entity.color = color.black

    def update(self):
        # Keyboard slider controls
        if held_keys['t']: self.sensitivity_slider.value += 100 * time.dt
        if held_keys['g']: self.sensitivity_slider.value -= 100 * time.dt
        
        if held_keys['y']: self.acceleration_slider.value += 50 * time.dt
        if held_keys['h']: self.acceleration_slider.value -= 50 * time.dt
        
        if held_keys['u']: self.max_speed_slider.value += 150 * time.dt
        if held_keys['j']: self.max_speed_slider.value -= 150 * time.dt

        if held_keys['i']: self.fov_slider.value += 30 * time.dt
        if held_keys['k']: self.fov_slider.value -= 30 * time.dt

        camera.fov = self.fov_slider.value

        # Mouse direction tracking
        self.cursor_pos.x += mouse.velocity[0]
        self.cursor_pos.y += mouse.velocity[1]
        
        distance = self.cursor_pos.length()
        
        if distance > self.max_radius:
            self.cursor_pos = self.cursor_pos.normalized() * self.max_radius
            distance = self.max_radius

        if distance > self.deadzone:
            self.direction_arrow.position = self.cursor_pos
            angle = math.degrees(math.atan2(self.cursor_pos.y, self.cursor_pos.x))
            self.direction_arrow.rotation_z = 90 - angle
            self.direction_arrow.color = color.cyan
        else:
            self.direction_arrow.color = color.clear

    def get_sensitivity(self):
        return self.sensitivity_slider.value
    
    def get_acceleration(self):
        return self.acceleration_slider.value
    
    def get_max_speed(self):
        return self.max_speed_slider.value
