from ursina import *

class PlayerController(Entity):
    def __init__(self, ui_manager):
        super().__init__()
        self.ui = ui_manager
        
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

    def input(self, key):
        if key == 'c':
            self.coupled_mode = not self.coupled_mode

    def update(self):
        if held_keys['escape']:
            application.quit()

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
        camera.rotate((delta_pitch, delta_yaw, delta_roll))

        acceleration = Vec3(0, 0, 0)
        # Scaled thrust (forward 100%, strafe 30%, reverse 30%)
        if held_keys['w']: acceleration += camera.forward * 1.0
        if held_keys['s']: acceleration += camera.back * 0.3
        if held_keys['d']: acceleration += camera.right * 0.3
        if held_keys['a']: acceleration += camera.left * 0.3
        if held_keys['space']: acceleration += camera.up * 0.3
        if held_keys['left control']: acceleration += camera.down * 0.3

        self.current_accel_magnitude = 0.0

        if acceleration.length() > 0:
            acceleration = acceleration.normalized() * current_accel
            self.current_accel_magnitude = current_accel
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

        camera.position += self.velocity * time.dt
