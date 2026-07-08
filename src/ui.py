from ursina import *
import math

class UIManager(Entity):
    def __init__(self):
        super().__init__()
        
        self.deadzone = 0.005

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
            scale=2.5,
            origin=(0, 0),
            parent=camera.ui
        )

        # Background Box
        self.slider_bg = Entity(
            model='quad',
            color=color.rgba(255, 255, 255, 180),
            scale=(0.7, 0.2),
            position=(-0.55, -0.4),
            parent=camera.ui,
            z=1
        )

        # Sliders
        self.sensitivity_slider = Slider(min=100, max=300, default=200, text='Sensitivity', dynamic=True, position=(-0.65, -0.35), scale=0.7)
        self.sensitivity_slider.label.color = color.black
        self.sensitivity_slider.knob.text_entity.color = color.black

        self.acceleration_slider = Slider(min=0, max=200, default=100, text='Acceleration', dynamic=True, position=(-0.65, -0.40), scale=0.7)
        self.acceleration_slider.label.color = color.black
        self.acceleration_slider.knob.text_entity.color = color.black

        self.max_speed_slider = Slider(min=400, max=600, default=500, text='Max Speed', dynamic=True, position=(-0.65, -0.45), scale=0.7)
        self.max_speed_slider.label.color = color.black
        self.max_speed_slider.knob.text_entity.color = color.black

    def update(self):
        # Keyboard slider controls
        if held_keys['t']: self.sensitivity_slider.value += 100 * time.dt
        if held_keys['g']: self.sensitivity_slider.value -= 100 * time.dt
        
        if held_keys['y']: self.acceleration_slider.value += 50 * time.dt
        if held_keys['h']: self.acceleration_slider.value -= 50 * time.dt
        
        if held_keys['u']: self.max_speed_slider.value += 150 * time.dt
        if held_keys['j']: self.max_speed_slider.value -= 150 * time.dt

        # Mouse direction tracking
        joy_x = mouse.position.x
        joy_y = mouse.position.y
        distance = math.sqrt(joy_x**2 + joy_y**2)
        
        if distance > self.deadzone:
            self.direction_arrow.position = (joy_x, joy_y)
            angle = math.degrees(math.atan2(joy_y, joy_x))
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
