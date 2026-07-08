from ursina import *

class PlayerController(Entity):
    def __init__(self, ui_manager):
        super().__init__(model='sphere', color=color.red, scale=1.0, collider='sphere')
        self.ui = ui_manager
        
        # Laser guns
        gun_scale = (0.1, 0.6, 0.1)
        gun_color = color.dark_gray
        self.gun_left = Entity(parent=self, model=Cylinder(16), color=gun_color, scale=gun_scale, position=(-0.6, 0, 0.2), rotation=(90, 0, 0))
        self.gun_right = Entity(parent=self, model=Cylinder(16), color=gun_color, scale=gun_scale, position=(0.6, 0, 0.2), rotation=(90, 0, 0))
        self.gun_bottom = Entity(parent=self, model=Cylinder(16), color=gun_color, scale=gun_scale, position=(0, -0.6, 0.2), rotation=(90, 0, 0))
        
        self.third_person = False
        camera.parent = self
        camera.position = (0, 0, 0)
        camera.rotation = (0, 0, 0)
        
        self.velocity = Vec3(0, 0, 0)
        self.roll_velocity = 0.0
        self.angular_vel_yaw = 0.0
        self.angular_vel_pitch = 0.0
        self.drag = 2.0
        self.coupled_mode = True
        self.current_accel_magnitude = 0.0

        # Boost system
        self.boost_fuel = 100.0
        self.is_boosting = False
        self.dead = False

    def input(self, key):
        if getattr(self, 'dead', False): return
        if key == 'c':
            self.coupled_mode = not self.coupled_mode
        if key == 'v':
            self.third_person = not self.third_person
            if self.third_person:
                camera.position = (0, 3, -15)
                camera.rotation = (10, 0, 0)
                self.ui.set_hud_visible(False)
            else:
                camera.position = (0, 0, 0)
                camera.rotation = (0, 0, 0)
                self.ui.set_hud_visible(True)

    def update(self):
        if held_keys['escape']:
            application.quit()
        
        if getattr(self, 'dead', False):
            return

        joy_x = self.ui.cursor_pos.x
        joy_y = self.ui.cursor_pos.y

        if abs(joy_x) < self.ui.deadzone: joy_x = 0
        if abs(joy_y) < self.ui.deadzone: joy_y = 0

        current_sens = self.ui.get_sensitivity()
        
        scale_factor = 0.5 / self.ui.max_radius
        scaled_joy_x = joy_x * scale_factor
        scaled_joy_y = joy_y * scale_factor

        target_yaw_vel = scaled_joy_x * current_sens
        target_pitch_vel = -scaled_joy_y * current_sens

        turn_acceleration = 5.0
        self.angular_vel_yaw = lerp(self.angular_vel_yaw, target_yaw_vel, turn_acceleration * time.dt)
        self.angular_vel_pitch = lerp(self.angular_vel_pitch, target_pitch_vel, turn_acceleration * time.dt)

        delta_yaw = self.angular_vel_yaw * time.dt
        delta_pitch = self.angular_vel_pitch * time.dt

        current_accel = self.ui.get_acceleration()
        current_max_speed = self.ui.get_max_speed()
        current_roll_accel = self.ui.get_roll_acceleration()
        current_max_roll_speed = self.ui.get_max_roll_speed()

        # Boost logic
        if held_keys['left shift'] and self.boost_fuel > 0:
            self.is_boosting = True
            self.boost_fuel -= 30.0 * time.dt
            if self.boost_fuel < 0: self.boost_fuel = 0
            
            current_accel *= 2.0
            current_roll_accel *= 2.0
            current_max_speed += 100.0
            current_max_roll_speed *= 1.5
        else:
            self.is_boosting = False
            self.boost_fuel += 15.0 * time.dt
            if self.boost_fuel > 100.0: self.boost_fuel = 100.0

        roll_acceleration = current_roll_accel
        roll_input = 0
        if held_keys['q']: roll_input -= 1
        if held_keys['e']: roll_input += 1

        if roll_input != 0:
            self.roll_velocity += roll_input * roll_acceleration * time.dt
        else:
            braking_roll_accel = roll_acceleration * 0.5
            if self.roll_velocity > 0:
                self.roll_velocity = max(0, self.roll_velocity - braking_roll_accel * time.dt)
            elif self.roll_velocity < 0:
                self.roll_velocity = min(0, self.roll_velocity + braking_roll_accel * time.dt)

        max_roll_speed = current_max_roll_speed
        self.roll_velocity = clamp(self.roll_velocity, -max_roll_speed, max_roll_speed)

        delta_roll = self.roll_velocity * time.dt
        self.rotate((delta_pitch, delta_yaw, delta_roll))

        acceleration = Vec3(0, 0, 0)
        # Scaled thrust (forward 100%, strafe 30%, reverse 30%)
        if held_keys['w']: acceleration += self.forward * 1.0
        if held_keys['s']: acceleration += self.back * 0.3
        if held_keys['d']: acceleration += self.right * 0.3
        if held_keys['a']: acceleration += self.left * 0.3
        if held_keys['space']: acceleration += self.up * 0.3
        if held_keys['left control']: acceleration += self.down * 0.3

        self.current_accel_magnitude = 0.0

        if acceleration.length() > 0:
            accel_mag = min(acceleration.length(), 1.0)
            acceleration = acceleration.normalized() * (current_accel * accel_mag)
            self.current_accel_magnitude = current_accel * accel_mag
            self.velocity += acceleration * time.dt

        if self.coupled_mode:
            if acceleration.length() == 0:
                vel_mag = self.velocity.length()
                if vel_mag > 0:
                    braking_accel = current_accel * 0.5
                    drop = braking_accel * time.dt
                    if vel_mag <= drop:
                        self.current_accel_magnitude = vel_mag / time.dt
                        self.velocity = Vec3(0, 0, 0)
                    else:
                        self.current_accel_magnitude = braking_accel
                        self.velocity -= self.velocity.normalized() * drop

        if self.velocity.length() > current_max_speed:
            self.velocity = self.velocity.normalized() * current_max_speed

        self.position += self.velocity * time.dt
        
        hit_info = self.intersects()
        if hit_info.hit:
            impact_speed = self.velocity.length()
            if impact_speed >= 20.0 and not getattr(self, 'dead', False):
                self.die()
            else:
                self.position -= self.velocity * time.dt  # Revert to prevent clipping
                if hit_info.normal.length() > 0:
                    self.velocity = self.velocity - 2 * self.velocity.dot(hit_info.normal) * hit_info.normal
                else:
                    self.velocity = -self.velocity
            self.velocity *= 0.5

    def die(self):
        self.dead = True
        self.velocity = Vec3(0,0,0)
        
        # Switch to 3rd person view for death
        self.third_person = True
        camera.position = (0, 8, -30)
        camera.rotation = (15, 0, 0)
        self.ui.set_hud_visible(False)
        
        # Create explosion entity
        self.explosion = Entity(model='sphere', color=color.orange, scale=1, position=self.position)
        self.explosion.animate_scale(20, duration=0.5, curve=curve.out_expo)
        self.explosion.animate_color(color.rgba(255, 100, 0, 0), duration=1.0)
        destroy(self.explosion, delay=1.0)
        
        # Hide player model
        self.visible = False
        
        # Schedule respawn
        invoke(self.respawn, delay=2.0)

    def respawn(self):
        self.dead = False
        self.position = Vec3(0, 0, 0)
        self.velocity = Vec3(0, 0, 0)
        self.rotation = Vec3(0, 0, 0)
        self.roll_velocity = 0
        self.angular_vel_yaw = 0
        self.angular_vel_pitch = 0
        self.boost_fuel = 100.0
        
        self.visible = True
        
        self.third_person = False
        camera.position = (0, 0, 0)
        camera.rotation = (0, 0, 0)
        self.ui.set_hud_visible(True)
