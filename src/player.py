from ursina import *

class PlayerController(Entity):
    def __init__(self, ui_manager):
        super().__init__()
        self.ui = ui_manager
        
        self.velocity = Vec3(0, 0, 0)
        self.roll_velocity = 0.0
        self.drag = 2.0
        self.coupled_mode = True

    def input(self, key):
        if key == 'c':
            self.coupled_mode = not self.coupled_mode
            print(f"Coupled Mode: {'ON' if self.coupled_mode else 'OFF'}")

    def update(self):
        if held_keys['escape']:
            application.quit()

        joy_x = self.ui.cursor_pos.x
        joy_y = self.ui.cursor_pos.y

        if abs(joy_x) < self.ui.deadzone: joy_x = 0
        if abs(joy_y) < self.ui.deadzone: joy_y = 0

        current_sens = self.ui.get_sensitivity()
        
        # Scale the virtual cursor so max_radius yields a 0.5 equivalent input
        scale_factor = 0.5 / self.ui.max_radius
        scaled_joy_x = joy_x * scale_factor
        scaled_joy_y = joy_y * scale_factor

        delta_yaw = scaled_joy_x * current_sens * time.dt
        delta_pitch = -scaled_joy_y * current_sens * time.dt

        current_accel = self.ui.get_acceleration()
        current_max_speed = self.ui.get_max_speed()

        roll_acceleration = current_accel * 5.0
        roll_input = 0
        if held_keys['q']: roll_input -= 1
        if held_keys['e']: roll_input += 1

        if roll_input != 0:
            self.roll_velocity += roll_input * roll_acceleration * time.dt
        else:
            self.roll_velocity = lerp(self.roll_velocity, 0, self.drag * 2 * time.dt)
            if abs(self.roll_velocity) < 0.1:
                self.roll_velocity = 0

        max_roll_speed = current_max_speed * 1.5
        self.roll_velocity = clamp(self.roll_velocity, -max_roll_speed, max_roll_speed)

        delta_roll = self.roll_velocity * time.dt
        camera.rotate((delta_pitch, delta_yaw, delta_roll))

        # Translation
        acceleration = Vec3(0, 0, 0)
        if held_keys['w']: acceleration += camera.forward
        if held_keys['s']: acceleration += camera.back
        if held_keys['d']: acceleration += camera.right
        if held_keys['a']: acceleration += camera.left
        if held_keys['space']: acceleration += camera.up
        if held_keys['left shift'] or held_keys['control']: acceleration += camera.down

        if acceleration.length() > 0:
            acceleration = acceleration.normalized() * current_accel * time.dt
            self.velocity += acceleration

        if self.coupled_mode:
            if acceleration.length() == 0:
                self.velocity = lerp(self.velocity, Vec3(0, 0, 0), self.drag * time.dt)
                if self.velocity.length() < 0.1:
                    self.velocity = Vec3(0, 0, 0)

        if self.velocity.length() > current_max_speed:
            self.velocity = self.velocity.normalized() * current_max_speed

        camera.position += self.velocity * time.dt
