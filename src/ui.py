from ursina import *
import math

class UIManager(Entity):
    def __init__(self):
        super().__init__()
        
        self.deadzone = 0.005
        self.cursor_pos = Vec2(0, 0)
        self.max_radius = 0.1
        mouse.locked = True

        self.center_crosshair = Text(
            text='+',
            origin=(0, 0),
            scale=2,
            color=color.cyan,
            parent=camera.ui
        )

        self.direction_arrow = Text(
            text='^',
            color=color.cyan,
            scale=1.5,
            origin=(0, 0),
            parent=camera.ui
        )

        self.player = None

        self.speed_bar_bg = Entity(model='quad', color=color.rgba(255, 255, 255, 50), scale=(0.01, 0.3), position=(-0.10, -0.15), origin=(0, -0.5), parent=camera.ui, z=1)
        self.speed_bar = Entity(model='quad', color=color.cyan, scale=(0.01, 0.001), position=(-0.10, -0.15), origin=(0, -0.5), parent=camera.ui, z=0.5)

        self.accel_bar_bg = Entity(model='quad', color=color.rgba(255, 255, 255, 50), scale=(0.008, 0.15), position=(-0.08, -0.15), origin=(0, -0.5), parent=camera.ui, z=1)
        self.accel_bar = Entity(model='quad', color=color.orange, scale=(0.008, 0.001), position=(-0.08, -0.15), origin=(0, -0.5), parent=camera.ui, z=0.5)

        self.hud_text = Text(text='', position=(0.10, 0.0), color=color.cyan, scale=0.8, parent=camera.ui)

        self.prograde_marker = Text(text='[o]', color=color.green, scale=1.0, origin=(0,0), parent=camera.ui)
        self.prograde_marker.enabled = False

        self.retrograde_marker = Text(text='[x]', color=color.red, scale=1.0, origin=(0,0), parent=camera.ui)
        self.retrograde_marker.enabled = False

        self.slider_bg = Entity(
            model='quad',
            color=color.rgba(255, 255, 255, 180),
            scale=(0.7, 0.25),
            position=(-0.55, -0.375),
            parent=camera.ui,
            z=1
        )

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
        if held_keys['t']: self.sensitivity_slider.value += 100 * time.dt
        if held_keys['g']: self.sensitivity_slider.value -= 100 * time.dt
        
        if held_keys['y']: self.acceleration_slider.value += 50 * time.dt
        if held_keys['h']: self.acceleration_slider.value -= 50 * time.dt
        
        if held_keys['u']: self.max_speed_slider.value += 150 * time.dt
        if held_keys['j']: self.max_speed_slider.value -= 150 * time.dt

        if held_keys['i']: self.fov_slider.value += 30 * time.dt
        if held_keys['k']: self.fov_slider.value -= 30 * time.dt

        camera.fov = self.fov_slider.value

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

        if self.player:
            speed = self.player.velocity.length()
            accel = self.player.current_accel_magnitude
            max_spd = self.max_speed_slider.value
            max_accel = self.acceleration_slider.max

            speed_ratio = clamp(speed / max_spd, 0, 1) if max_spd > 0 else 0
            self.speed_bar.scale_y = max(0.001, 0.3 * speed_ratio)
            
            accel_ratio = clamp(accel / max_accel, 0, 1) if max_accel > 0 else 0
            self.accel_bar.scale_y = max(0.001, 0.15 * accel_ratio)

            g_force = accel / 9.8
            cpl_str = "ON" if self.player.coupled_mode else "OFF"
            self.hud_text.text = f"VEL: {int(speed)} m/s\nACC: {g_force:.1f} G\nCPL: {cpl_str}"

            if speed > 1.0:
                v_norm = self.player.velocity.normalized()
                fwd_dot = v_norm.dot(camera.forward)
                right_dot = v_norm.dot(camera.right)
                up_dot = v_norm.dot(camera.up)
                
                fov_factor = camera.fov / 90.0
                
                if fwd_dot > 0:
                    self.prograde_marker.x = (right_dot / fwd_dot) * 0.5 / fov_factor
                    self.prograde_marker.y = (up_dot / fwd_dot) * 0.5 / fov_factor
                    self.prograde_marker.enabled = True
                else:
                    self.prograde_marker.enabled = False

                inv_v_norm = -v_norm
                inv_fwd_dot = inv_v_norm.dot(camera.forward)
                inv_right_dot = inv_v_norm.dot(camera.right)
                inv_up_dot = inv_v_norm.dot(camera.up)
                
                if inv_fwd_dot > 0:
                    self.retrograde_marker.x = (inv_right_dot / inv_fwd_dot) * 0.5 / fov_factor
                    self.retrograde_marker.y = (inv_up_dot / inv_fwd_dot) * 0.5 / fov_factor
                    self.retrograde_marker.enabled = True
                else:
                    self.retrograde_marker.enabled = False
            else:
                self.prograde_marker.enabled = False
                self.retrograde_marker.enabled = False

    def get_sensitivity(self):
        return self.sensitivity_slider.value
    
    def get_acceleration(self):
        return self.acceleration_slider.value
    
    def get_max_speed(self):
        return self.max_speed_slider.value
