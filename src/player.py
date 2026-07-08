from ursina import *
import src.settings as cfg
import random

class LaserProjectile(Entity):
    def __init__(self, position, velocity):
        super().__init__(
            model='cube',
            color=cfg.WEAPON_LASER_COLOR,
            scale=(0.1, 0.1, 4.0),
            position=position
        )
        self.velocity = velocity
        self.look_at(self.position + self.velocity)
        destroy(self, delay=cfg.WEAPON_LASER_LIFESPAN)

    def update(self):
        self.position += self.velocity * time.dt

class PlayerController(Entity):
    def __init__(self, ui_manager):
        super().__init__(model='sphere', color=color.red, scale=cfg.PLAYER_SCALE, collider='sphere')
        self.ui = ui_manager
        
        # Laser guns
        gun_scale = (0.1, 0.6, 0.1)
        gun_color = color.dark_gray
        self.gun_left = Entity(parent=self, model=Cylinder(16), color=gun_color, scale=gun_scale, position=(-0.6, 0, 0.2), rotation=(90, 0, 0))
        self.gun_right = Entity(parent=self, model=Cylinder(16), color=gun_color, scale=gun_scale, position=(0.6, 0, 0.2), rotation=(90, 0, 0))
        self.gun_bottom = Entity(parent=self, model=Cylinder(16), color=gun_color, scale=gun_scale, position=(0, -0.6, 0.2), rotation=(90, 0, 0))
        
        self.third_person = False
        self.third_person_zoom = cfg.THIRD_PERSON_ZOOM_DEFAULT
        self.freecam_yaw = 0.0
        self.freecam_pitch = 0.0
        
        self.camera_gimbal = Entity(parent=self)
        camera.parent = self.camera_gimbal
        camera.position = cfg.PLAYER_START_POS
        camera.rotation = cfg.PLAYER_START_ROT
        
        self.velocity = Vec3(0, 0, 0)
        self.roll_velocity = 0.0
        self.angular_vel_yaw = 0.0
        self.angular_vel_pitch = 0.0
        self.drag = cfg.PLAYER_DRAG
        self.coupled_mode = True
        self.current_accel_magnitude = 0.0

        # Boost system
        self.boost_fuel = cfg.BOOST_FUEL_MAX
        self.is_boosting = False
        self.dead = False
        
        # Weapons
        self.fire_cooldown = 0.0

    def input(self, key):
        if getattr(self, 'dead', False): return
        if key == 'c':
            self.coupled_mode = not self.coupled_mode
        if key == 'v':
            self.third_person = not self.third_person
            if self.third_person:
                camera.position = (0, 3, -self.third_person_zoom)
                camera.rotation = (10, 0, 0)
                self.ui.set_hud_visible(False)
            else:
                camera.position = (0, 0, 0)
                camera.rotation = (0, 0, 0)
                self.ui.set_hud_visible(True)
                
        if self.third_person:
            if key == 'scroll up':
                self.third_person_zoom = max(cfg.THIRD_PERSON_ZOOM_MIN, self.third_person_zoom - cfg.THIRD_PERSON_ZOOM_SPEED)
                camera.position = (0, 3, -self.third_person_zoom)
            elif key == 'scroll down':
                self.third_person_zoom = min(cfg.THIRD_PERSON_ZOOM_MAX, self.third_person_zoom + cfg.THIRD_PERSON_ZOOM_SPEED)
                camera.position = (0, 3, -self.third_person_zoom)

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

        turn_acceleration = cfg.TURN_ACCELERATION
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
            self.boost_fuel -= cfg.BOOST_DRAIN_RATE * time.dt
            if self.boost_fuel < 0: self.boost_fuel = 0
            
            current_accel *= cfg.BOOST_ACCEL_MULT
            current_roll_accel *= cfg.BOOST_ROLL_ACCEL_MULT
            current_max_speed += cfg.BOOST_SPEED_BONUS
            current_max_roll_speed *= cfg.BOOST_MAX_ROLL_SPEED_MULT
        else:
            self.is_boosting = False
            self.boost_fuel += cfg.BOOST_RECHARGE_RATE * time.dt
            if self.boost_fuel > cfg.BOOST_FUEL_MAX: self.boost_fuel = cfg.BOOST_FUEL_MAX

        # Freecam logic
        if held_keys['middle mouse']:
            self.freecam_yaw += mouse.velocity[0] * current_sens * cfg.FREECAM_SENSITIVITY_MULT
            self.freecam_pitch -= mouse.velocity[1] * current_sens * cfg.FREECAM_SENSITIVITY_MULT
            self.freecam_pitch = clamp(self.freecam_pitch, -cfg.FREECAM_PITCH_LIMIT, cfg.FREECAM_PITCH_LIMIT)
            
            if not self.third_person:
                self.freecam_yaw = clamp(self.freecam_yaw, -cfg.FREECAM_YAW_LIMIT, cfg.FREECAM_YAW_LIMIT)
            
            self.camera_gimbal.rotation = (self.freecam_pitch, self.freecam_yaw, 0)
        else:
            if self.freecam_yaw != 0 or self.freecam_pitch != 0:
                self.freecam_yaw = lerp(self.freecam_yaw, 0, cfg.FREECAM_RETURN_SPEED * time.dt)
                self.freecam_pitch = lerp(self.freecam_pitch, 0, cfg.FREECAM_RETURN_SPEED * time.dt)
                
                if abs(self.freecam_yaw) < 0.1 and abs(self.freecam_pitch) < 0.1:
                    self.freecam_yaw = 0
                    self.freecam_pitch = 0
                    
                self.camera_gimbal.rotation = (self.freecam_pitch, self.freecam_yaw, 0)

        target_fov = self.ui.fov_slider.value
        if held_keys['right mouse']:
            target_fov = cfg.WEAPON_ZOOM_FOV
        camera.fov = lerp(camera.fov, target_fov, cfg.WEAPON_ZOOM_SPEED * time.dt)

        if self.fire_cooldown > 0:
            self.fire_cooldown -= time.dt

        if held_keys['left mouse'] and mouse.locked and self.fire_cooldown <= 0:
            self.fire_cooldown = cfg.WEAPON_FIRE_RATE
            self.fire_lasers()

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
            if impact_speed >= cfg.DEATH_IMPACT_SPEED and not getattr(self, 'dead', False):
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
        self.camera_gimbal.rotation = (0, 0, 0)
        camera.position = (0, 8, -30)
        camera.rotation = (15, 0, 0)
        self.ui.set_hud_visible(False)
        
        # Create explosion entity
        self.explosion = Entity(model='sphere', color=color.orange, scale=1, position=self.position)
        self.explosion.animate_scale(cfg.DEATH_EXPLOSION_SCALE, duration=cfg.DEATH_EXPLOSION_DURATION, curve=curve.out_expo)
        self.explosion.animate_color(color.rgba(255, 100, 0, 0), duration=cfg.DEATH_FADE_DURATION)
        destroy(self.explosion, delay=cfg.DEATH_FADE_DURATION)
        
        # Hide player model
        self.visible = False
        
        # Schedule respawn
        invoke(self.respawn, delay=cfg.DEATH_RESPAWN_DELAY)

    def respawn(self):
        self.dead = False
        self.position = Vec3(0, 0, 0)
        self.velocity = Vec3(0, 0, 0)
        self.rotation = Vec3(0, 0, 0)
        self.roll_velocity = 0
        self.angular_vel_yaw = 0
        self.angular_vel_pitch = 0
        self.boost_fuel = cfg.BOOST_FUEL_MAX
        
        self.visible = True
        
        self.third_person = False
        self.camera_gimbal.rotation = (0, 0, 0)
        camera.position = (0, 0, 0)
        camera.rotation = (0, 0, 0)
        self.ui.set_hud_visible(True)

    def fire_lasers(self):
        guns = [self.gun_left, self.gun_right, self.gun_bottom]
        for gun in guns:
            spawn_pos = gun.world_position + self.forward * 0.3
            
            spread_x = random.uniform(-cfg.WEAPON_LASER_SPREAD, cfg.WEAPON_LASER_SPREAD)
            spread_y = random.uniform(-cfg.WEAPON_LASER_SPREAD, cfg.WEAPON_LASER_SPREAD)
            spread_z = random.uniform(-cfg.WEAPON_LASER_SPREAD, cfg.WEAPON_LASER_SPREAD)
            spread_vec = Vec3(spread_x, spread_y, spread_z)
            
            fire_dir = (self.forward + spread_vec).normalized()
            proj_vel = self.velocity + fire_dir * cfg.WEAPON_LASER_SPEED
            
            LaserProjectile(position=spawn_pos, velocity=proj_vel)
