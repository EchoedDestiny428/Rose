from ursina import *
import math
import src.settings as cfg

class TargetMarker(Entity):
    def __init__(self, target_entity, player=None, **kwargs):
        super().__init__(parent=camera.ui, **kwargs)
        self.target = target_entity
        self.player = player
        
        t = 0.0005
        l = 0.01
        
        self.lock_anim_scale = 1.0
        
        self.soft_parent = Entity(parent=self)
        c = cfg.UI_COLOR_RED
        self.s_t = Entity(parent=self.soft_parent, model='quad', scale=(t, l), position=(0, l), color=c)
        self.s_b = Entity(parent=self.soft_parent, model='quad', scale=(t, l), position=(0, -l), color=c)
        self.s_r = Entity(parent=self.soft_parent, model='quad', scale=(l, t), position=(l, 0), color=c)
        self.s_l = Entity(parent=self.soft_parent, model='quad', scale=(l, t), position=(-l, 0), color=c)
        
        self.hard_parent = Entity(parent=self)
        self.hl_vt = Entity(parent=self.hard_parent, model='quad', color=c)
        self.hl_vb = Entity(parent=self.hard_parent, model='quad', color=c)
        self.hl_t = Entity(parent=self.hard_parent, model='quad', color=c)
        self.hl_b = Entity(parent=self.hard_parent, model='quad', color=c)
        self.hr_vt = Entity(parent=self.hard_parent, model='quad', color=c)
        self.hr_vb = Entity(parent=self.hard_parent, model='quad', color=c)
        self.hr_t = Entity(parent=self.hard_parent, model='quad', color=c)
        self.hr_b = Entity(parent=self.hard_parent, model='quad', color=c)
        
        self.pip_parent = Entity(parent=self)
        self.pip_o = Text(text='o', parent=self.pip_parent, origin=(0, 0), color=c, scale=0.8)
        self.pip_l = Entity(parent=self.pip_parent, model='quad', color=c, scale=(0.001, 0.015))
        self.pip_r = Entity(parent=self.pip_parent, model='quad', color=c, scale=(0.001, 0.015))
        
        self._is_hard_locked = False
        
    @property
    def is_hard_locked(self):
        return self._is_hard_locked
        
    @is_hard_locked.setter
    def is_hard_locked(self, value):
        if value and not self._is_hard_locked:
            self.lock_anim_scale = 2.0
            self.animate('lock_anim_scale', 1.0, duration=0.4, curve=curve.out_back)
        self._is_hard_locked = value
        
    def update(self):
        if not self.target or not self.target.enabled:
            self.soft_parent.enabled = False
            self.hard_parent.enabled = False
            self.pip_parent.enabled = False
            return
            
        dist = distance(self.target.world_position, camera.world_position)
        if dist > cfg.RADAR_RANGE:
            self.soft_parent.enabled = False
            self.hard_parent.enabled = False
            self.pip_parent.enabled = False
            return
            
        v = self.target.world_position - camera.world_position
        v_norm = v.normalized()
        fwd_dot = v_norm.dot(camera.forward)
        if fwd_dot <= 0:
            self.soft_parent.enabled = False
            self.hard_parent.enabled = False
            self.pip_parent.enabled = False
            return
            
        right_dot = v_norm.dot(camera.right)
        up_dot = v_norm.dot(camera.up)
        
        tan_half_fov = math.tan(math.radians(camera.fov / 2))
        c_factor = 0.5 * window.aspect_ratio / tan_half_fov
        self.position = Vec2(
            (right_dot / fwd_dot) * c_factor,
            (up_dot / fwd_dot) * c_factor
        )
        
        size = 5.0 / dist
        size = max(size, cfg.TARGET_MIN_SIZE)
        
        size = size * self.lock_anim_scale
        
        t = 0.001
        self.s_t.y = size
        self.s_b.y = -size
        self.s_r.x = size
        self.s_l.x = -size
        
        h = size * 2.0
        w = size * 0.5
        corner_h = size * 0.5
        offset = size * 1.5
        
        self.hl_vt.scale = (t, corner_h)
        self.hl_vt.position = (-offset, h/2 - corner_h/2)
        self.hl_t.scale = (w, t)
        self.hl_t.position = (-offset + w/2, h/2)
        
        self.hl_vb.scale = (t, corner_h)
        self.hl_vb.position = (-offset, -h/2 + corner_h/2)
        self.hl_b.scale = (w, t)
        self.hl_b.position = (-offset + w/2, -h/2)
        
        self.hr_vt.scale = (t, corner_h)
        self.hr_vt.position = (offset, h/2 - corner_h/2)
        self.hr_t.scale = (w, t)
        self.hr_t.position = (offset - w/2, h/2)
        
        self.hr_vb.scale = (t, corner_h)
        self.hr_vb.position = (offset, -h/2 + corner_h/2)
        self.hr_b.scale = (w, t)
        self.hr_b.position = (offset - w/2, -h/2)
        
        self.soft_parent.enabled = not self.is_hard_locked
        self.hard_parent.enabled = self.is_hard_locked

        if self.player and self.is_hard_locked:
            R = self.target.world_position - camera.world_position
            V_p = self.player.velocity
            S = cfg.WEAPON_LASER_SPEED
            
            A = R.length_squared()
            B = -2 * R.dot(V_p)
            C_math = V_p.length_squared() - S**2
            
            D = B**2 - 4*A*C_math
            if D >= 0 and A > 0.001:
                u = (-B + math.sqrt(D)) / (2*A)
                if u > 0:
                    t_aim = 1 / u
                    V_b = R / t_aim
                    d = (V_b - V_p).normalized()
                    
                    pip_fwd_dot = d.dot(camera.forward)
                    if pip_fwd_dot > 0:
                        pip_right = d.dot(camera.right)
                        pip_up = d.dot(camera.up)
                        
                        pip_x = (pip_right / pip_fwd_dot) * c_factor
                        pip_y = (pip_up / pip_fwd_dot) * c_factor
                        
                        self.pip_parent.position = Vec2(pip_x - self.position.x, pip_y - self.position.y)
                        
                        if self.pip_parent.position.length_squared() > 0.000001:
                            angle = math.degrees(math.atan2(self.pip_parent.position.y, self.pip_parent.position.x))
                            self.pip_parent.rotation_z = -(angle - 90)
                        else:
                            self.pip_parent.rotation_z = 0
                            
                        self.pip_l.position = (-size, 0)
                        self.pip_r.position = (size, 0)
                        
                        pip_dist_from_center = Vec2(pip_x, pip_y).length()
                        if pip_dist_from_center < size * 1.2:
                            pip_c = cfg.UI_COLOR_GREEN
                        else:
                            pip_c = cfg.UI_COLOR_RED
                            
                        self.pip_o.color = pip_c
                        self.pip_l.color = pip_c
                        self.pip_r.color = pip_c
                        
                        self.pip_parent.enabled = True
                    else:
                        self.pip_parent.enabled = False
                else:
                    self.pip_parent.enabled = False
            else:
                self.pip_parent.enabled = False
        else:
            self.pip_parent.enabled = False

class UIManager(Entity):
    def __init__(self):
        super().__init__()
        
        self.deadzone = cfg.UI_DEADZONE
        self.cursor_pos = Vec2(0, 0)
        self.max_radius = cfg.UI_MAX_RADIUS
        mouse.locked = True

        # Colors
        self.amber = cfg.UI_COLOR_AMBER
        self.amber_faint = cfg.UI_COLOR_AMBER_FAINT
        self.cyan = cfg.UI_COLOR_CYAN

        self.center_crosshair = Text(
            text='-   .   -',
            origin=(0, 0),
            scale=1.1,
            color=self.amber,
            parent=camera.ui
        )

        self.direction_arrow = Text(
            text='^',
            color=self.cyan,
            scale=1.1,
            origin=(0, 0),
            parent=camera.ui
        )

        self.player = None
        self.target_markers = []

        self.speed_bar_bg = Entity(model='quad', color=self.amber_faint, scale=(0.008, 0.2), position=(-0.15, -0.1), origin=(0, -0.5), parent=camera.ui, z=1)
        self.speed_bar = Entity(model='quad', color=self.cyan, scale=(0.008, 0.001), position=(-0.15, -0.1), origin=(0, -0.5), parent=camera.ui, z=0.5)
        self.speed_label = Text(text='0\nm/s', position=(-0.15, -0.15), origin=(0, 0), color=self.amber, scale=0.6, parent=camera.ui)

        self.boost_bar_bg = Entity(model='quad', color=self.amber_faint, scale=(0.008, 0.2), position=(0.15, -0.1), origin=(0, -0.5), parent=camera.ui, z=1)
        self.boost_bar = Entity(model='quad', color=self.cyan, scale=(0.008, 0.001), position=(0.15, -0.1), origin=(0, -0.5), parent=camera.ui, z=0.5)
        self.boost_label = Text(text='100%\nAB', position=(0.15, -0.15), origin=(0, 0), color=self.amber, scale=0.6, parent=camera.ui)

        self.hud_text = Text(text='', position=(0.15, -0.25), origin=(0, 0), color=self.amber, scale=0.7, parent=camera.ui)

        self.prograde_marker = Text(text='[o]', color=self.cyan, scale=0.8, origin=(0,0), parent=camera.ui)
        self.prograde_marker.enabled = False

        self.retrograde_marker = Text(text='[x]', color=self.amber, scale=0.8, origin=(0,0), parent=camera.ui)
        self.retrograde_marker.enabled = False

        self.slider_bg = Entity(
            model='quad',
            color=color.rgba(255, 255, 255, 180),
            scale=(0.7, 0.42),
            position=(-0.55, -0.27),
            parent=camera.ui,
            z=1
        )

        self.sensitivity_slider = Slider(min=cfg.SLIDER_SENSITIVITY[0], max=cfg.SLIDER_SENSITIVITY[1], default=cfg.SLIDER_SENSITIVITY[2], text='Sensitivity', dynamic=True, position=(-0.65, -0.10), scale=0.7)
        self.sensitivity_slider.label.color = color.black
        self.sensitivity_slider.knob.text_entity.color = color.black

        self.acceleration_slider = Slider(min=cfg.SLIDER_ACCELERATION[0], max=cfg.SLIDER_ACCELERATION[1], default=cfg.SLIDER_ACCELERATION[2], text='Acceleration', dynamic=True, position=(-0.65, -0.16), scale=0.7)
        self.acceleration_slider.label.color = color.black
        self.acceleration_slider.knob.text_entity.color = color.black

        self.max_speed_slider = Slider(min=cfg.SLIDER_MAX_SPEED[0], max=cfg.SLIDER_MAX_SPEED[1], default=cfg.SLIDER_MAX_SPEED[2], text='Max Speed', dynamic=True, position=(-0.65, -0.22), scale=0.7)
        self.max_speed_slider.label.color = color.black
        self.max_speed_slider.knob.text_entity.color = color.black

        self.fov_slider = Slider(min=cfg.SLIDER_FOV[0], max=cfg.SLIDER_FOV[1], default=cfg.SLIDER_FOV[2], text='FOV', dynamic=True, position=(-0.65, -0.28), scale=0.7)
        self.fov_slider.label.color = color.black
        self.fov_slider.knob.text_entity.color = color.black

        self.roll_slider = Slider(min=cfg.SLIDER_ROLL_ACCEL[0], max=cfg.SLIDER_ROLL_ACCEL[1], default=cfg.SLIDER_ROLL_ACCEL[2], text='Roll Accel', dynamic=True, position=(-0.65, -0.34), scale=0.7)
        self.roll_slider.label.color = color.black
        self.roll_slider.knob.text_entity.color = color.black

        self.roll_speed_slider = Slider(min=cfg.SLIDER_MAX_ROLL_SPEED[0], max=cfg.SLIDER_MAX_ROLL_SPEED[1], default=cfg.SLIDER_MAX_ROLL_SPEED[2], text='Max Roll', dynamic=True, position=(-0.65, -0.40), scale=0.7)
        self.roll_speed_slider.label.color = color.black
        self.roll_speed_slider.knob.text_entity.color = color.black

        self.sliders_ui = [
            self.slider_bg,
            self.sensitivity_slider,
            self.acceleration_slider,
            self.max_speed_slider,
            self.fov_slider,
            self.roll_slider,
            self.roll_speed_slider
        ]
        self.sliders_visible = True
        self.toggle_sliders() # Start hidden for clean HUD

    def input(self, key):
        if key == 'm':
            self.toggle_sliders()

    def toggle_sliders(self):
        self.sliders_visible = not self.sliders_visible
        for el in self.sliders_ui:
            el.enabled = self.sliders_visible
        mouse.locked = not self.sliders_visible
        mouse.visible = self.sliders_visible

    def add_target_marker(self, entity):
        marker = TargetMarker(entity, player=self.player)
        self.target_markers.append(marker)

    def set_hard_target(self, target_entity):
        for marker in self.target_markers:
            marker.is_hard_locked = (marker.target == target_entity)

    def set_hud_visible(self, visible):
        hud_elements = [
            self.center_crosshair, self.direction_arrow,
            self.speed_bar_bg, self.speed_bar, self.speed_label,
            self.boost_bar_bg, self.boost_bar, self.boost_label,
            self.hud_text, self.prograde_marker, self.retrograde_marker
        ]
        for el in hud_elements:
            el.enabled = visible

    def update(self):
        if held_keys['t']: self.sensitivity_slider.value += 100 * time.dt
        if held_keys['g']: self.sensitivity_slider.value -= 100 * time.dt
        
        if held_keys['y']: self.acceleration_slider.value += 50 * time.dt
        if held_keys['h']: self.acceleration_slider.value -= 50 * time.dt
        
        if held_keys['u']: self.max_speed_slider.value += 150 * time.dt
        if held_keys['j']: self.max_speed_slider.value -= 150 * time.dt

        if held_keys['i']: self.fov_slider.value += 30 * time.dt
        if held_keys['k']: self.fov_slider.value -= 30 * time.dt
        
        if held_keys['o']: self.roll_slider.value += 50 * time.dt
        if held_keys['l']: self.roll_slider.value -= 50 * time.dt

        if not held_keys['middle mouse']:
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
            self.direction_arrow.color = self.amber
        else:
            self.direction_arrow.color = color.clear

        if self.player:
            if getattr(self.player, 'third_person', False):
                return
            speed = self.player.velocity.length()
            accel = self.player.current_accel_magnitude
            max_spd = self.max_speed_slider.value
            max_accel = self.acceleration_slider.max

            speed_ratio = clamp(speed / max_spd, 0, 1) if max_spd > 0 else 0
            self.speed_bar.scale_y = max(0.001, 0.2 * speed_ratio)
            
            boost_ratio = clamp(self.player.boost_fuel / 100.0, 0, 1)
            self.boost_bar.scale_y = max(0.001, 0.2 * boost_ratio)

            self.speed_label.text = f"{int(speed)}\nm/s"
            self.boost_label.text = f"{int(self.player.boost_fuel)}%\nAB"

            cpl_str = "ON" if self.player.coupled_mode else "OFF"
            self.hud_text.text = f"CPL: {cpl_str}"

            if speed > 1.0:
                v_norm = self.player.velocity.normalized()
                fwd_dot = v_norm.dot(camera.forward)
                right_dot = v_norm.dot(camera.right)
                up_dot = v_norm.dot(camera.up)
                
                tan_half_fov = math.tan(math.radians(camera.fov / 2))
                c = 0.5 * window.aspect_ratio / tan_half_fov
                
                if fwd_dot > 0:
                    self.prograde_marker.x = (right_dot / fwd_dot) * c
                    self.prograde_marker.y = (up_dot / fwd_dot) * c
                    self.prograde_marker.enabled = True
                else:
                    self.prograde_marker.enabled = False

                inv_v_norm = -v_norm
                inv_fwd_dot = inv_v_norm.dot(camera.forward)
                inv_right_dot = inv_v_norm.dot(camera.right)
                inv_up_dot = inv_v_norm.dot(camera.up)
                
                if inv_fwd_dot > 0:
                    self.retrograde_marker.x = (inv_right_dot / inv_fwd_dot) * c
                    self.retrograde_marker.y = (inv_up_dot / inv_fwd_dot) * c
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

    def get_roll_acceleration(self):
        return self.roll_slider.value

    def get_max_roll_speed(self):
        return self.roll_speed_slider.value
