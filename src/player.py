from ursina import *
import src.settings as cfg
import random
import math

class LaserProjectile(Entity):
    def __init__(self, position, velocity, owner=None):
        super().__init__(
            model='cube',
            color=cfg.WEAPON_LASER_COLOR,
            scale=(0.1, 0.1, 4.0),
            position=position
        )
        self.velocity = velocity
        self.owner = owner
        self.look_at(self.position + self.velocity)
        destroy(self, delay=cfg.WEAPON_LASER_LIFESPAN)

    def update(self):
        dist = self.velocity.length() * time.dt
        hit_info = raycast(self.position, self.velocity.normalized(), distance=dist, ignore=(self, self.owner))
        if hit_info.hit:
            if hasattr(hit_info.entity, 'take_damage'):
                hit_info.entity.take_damage(25.0)
            destroy(self)
            return
            
        self.position += self.velocity * time.dt

class BaseShip(Entity):
    def __init__(self, color_choice=color.red, **kwargs):
        super().__init__(model='sphere', color=color_choice, scale=cfg.PLAYER_SCALE, collider='sphere', **kwargs)
        
        # Laser guns
        gun_scale = (0.1, 0.6, 0.1)
        gun_color = color.dark_gray
        self.gun_left = Entity(parent=self, model=Cylinder(16), color=gun_color, scale=gun_scale, position=(-0.6, 0, 0.2), rotation=(90, 0, 0))
        self.gun_right = Entity(parent=self, model=Cylinder(16), color=gun_color, scale=gun_scale, position=(0.6, 0, 0.2), rotation=(90, 0, 0))
        self.gun_bottom = Entity(parent=self, model=Cylinder(16), color=gun_color, scale=gun_scale, position=(0, -0.6, 0.2), rotation=(90, 0, 0))
        
        self.velocity = Vec3(0, 0, 0)
        self.dead = False
        self.max_health = 1000.0
        self.health = self.max_health

    def take_damage(self, amount):
        if self.dead: return
        self.health -= amount
        if self.health <= 0:
            self.die()
            
    def die(self):
        self.dead = True
        self.velocity = Vec3(0,0,0)
        
        # Create explosion entity
        self.explosion = Entity(model='sphere', color=color.orange, scale=1, position=self.position)
        self.explosion.animate_scale(cfg.DEATH_EXPLOSION_SCALE, duration=cfg.DEATH_EXPLOSION_DURATION, curve=curve.out_expo)
        self.explosion.animate_color(color.rgba(255, 100, 0, 0), duration=cfg.DEATH_FADE_DURATION)
        destroy(self.explosion, delay=cfg.DEATH_FADE_DURATION)
        
        # Hide player model
        self.visible = False
        self.gun_left.visible = False
        self.gun_right.visible = False
        self.gun_bottom.visible = False
        
        # Schedule respawn
        invoke(self.respawn, delay=cfg.DEATH_RESPAWN_DELAY)

    def respawn(self):
        self.dead = False
        self.health = self.max_health
        self.position = Vec3(0, 0, 0)
        self.velocity = Vec3(0, 0, 0)
        self.rotation = Vec3(0, 0, 0)
        self.visible = True
        self.gun_left.visible = True
        self.gun_right.visible = True
        self.gun_bottom.visible = True

    def fire_lasers(self):
        if self.dead: return []
        guns = [self.gun_left, self.gun_right, self.gun_bottom]
        laser_data = []
        for gun in guns:
            spawn_pos = gun.world_position + self.forward * 0.3
            
            spread_x = random.uniform(-cfg.WEAPON_LASER_SPREAD, cfg.WEAPON_LASER_SPREAD)
            spread_y = random.uniform(-cfg.WEAPON_LASER_SPREAD, cfg.WEAPON_LASER_SPREAD)
            spread_z = random.uniform(-cfg.WEAPON_LASER_SPREAD, cfg.WEAPON_LASER_SPREAD)
            spread_vec = Vec3(spread_x, spread_y, spread_z)
            
            fire_dir = (self.forward + spread_vec).normalized()
            proj_vel = self.velocity + fire_dir * cfg.WEAPON_LASER_SPEED
            
            LaserProjectile(position=spawn_pos, velocity=proj_vel, owner=self)
            laser_data.append((spawn_pos, proj_vel))
        return laser_data


class LocalPlayer(BaseShip):
    def __init__(self, ui_manager, **kwargs):
        super().__init__(color_choice=color.red, **kwargs)
        self.ui = ui_manager
        
        self.visible = False
        self.gun_left.visible = False
        self.gun_right.visible = False
        self.gun_bottom.visible = False
        
        self.third_person = False
        self.third_person_zoom = cfg.THIRD_PERSON_ZOOM_DEFAULT
        self.freecam_yaw = 0.0
        self.freecam_pitch = 0.0
        
        self.camera_gimbal = Entity(parent=self)
        camera.parent = self.camera_gimbal
        camera.position = cfg.PLAYER_START_POS
        camera.rotation = cfg.PLAYER_START_ROT
        
        self.roll_velocity = 0.0
        self.angular_vel_yaw = 0.0
        self.angular_vel_pitch = 0.0
        self.drag = cfg.PLAYER_DRAG
        self.coupled_mode = True
        self.current_accel_magnitude = 0.0

        # Boost system
        self.boost_fuel = cfg.BOOST_FUEL_MAX
        self.is_boosting = False
        
        # Weapons
        self.fire_cooldown = 0.0
        self.obstacles = []
        self.hard_target = None
        
        self.position = self.get_safe_spawn()

    def get_safe_spawn(self):
        import os
        import random as rnd
        r = rnd.Random(os.urandom(8))
        for _ in range(50):
            pos = Vec3(r.uniform(-100, 100), r.uniform(-100, 100), r.uniform(-100, 100))
            safe = True
            for obs in self.obstacles:
                if not obs.enabled or getattr(obs, 'dead', False): continue
                if distance(pos, obs.position) < 30.0: # At least 30 meters away
                    safe = False
                    break
            if safe:
                return pos
        return Vec3(0, 0, 0)

    def input(self, key):
        if self.dead: return
        
        if key == 't':
            best_dot = -1.0
            best_cube = None
            for cube in self.obstacles:
                if not cube.enabled or getattr(cube, 'dead', False): continue
                dist = distance(self.world_position, cube.world_position)
                if dist <= cfg.RADAR_RANGE:
                    v = cube.world_position - camera.world_position
                    v_norm = v.normalized()
                    fwd_dot = v_norm.dot(camera.forward)
                    if fwd_dot > 0 and fwd_dot > best_dot:
                        best_dot = fwd_dot
                        best_cube = cube
            
            if best_cube:
                self.hard_target = best_cube
                self.ui.set_hard_target(best_cube)

        if key == 'c':
            self.coupled_mode = not self.coupled_mode
        if key == 'v':
            self.third_person = not self.third_person
            if self.third_person:
                camera.position = (0, 3, -self.third_person_zoom)
                camera.rotation = (10, 0, 0)
                self.ui.set_hud_visible(False)
                self.visible = True
                self.gun_left.visible = True
                self.gun_right.visible = True
                self.gun_bottom.visible = True
            else:
                camera.position = (0, 0, 0)
                camera.rotation = (0, 0, 0)
                self.ui.set_hud_visible(True)
                self.visible = False
                self.gun_left.visible = False
                self.gun_right.visible = False
                self.gun_bottom.visible = False
                
        if self.third_person:
            if key == 'scroll up':
                self.third_person_zoom = max(cfg.THIRD_PERSON_ZOOM_MIN, self.third_person_zoom - cfg.THIRD_PERSON_ZOOM_SPEED)
                camera.position = (0, 3, -self.third_person_zoom)
            elif key == 'scroll down':
                self.third_person_zoom = min(cfg.THIRD_PERSON_ZOOM_MAX, self.third_person_zoom + cfg.THIRD_PERSON_ZOOM_SPEED)
                camera.position = (0, 3, -self.third_person_zoom)

    def die(self):
        super().die()
        # Switch to 3rd person view for death
        self.third_person = True
        self.camera_gimbal.rotation = (0, 0, 0)
        camera.position = (0, 8, -30)
        camera.rotation = (15, 0, 0)
        self.ui.set_hud_visible(False)

    def respawn(self):
        super().respawn()
        self.position = self.get_safe_spawn()
        self.roll_velocity = 0
        self.angular_vel_yaw = 0
        self.angular_vel_pitch = 0
        self.boost_fuel = cfg.BOOST_FUEL_MAX
        
        self.third_person = False
        self.camera_gimbal.rotation = (0, 0, 0)
        camera.position = (0, 0, 0)
        camera.rotation = (0, 0, 0)
        self.ui.set_hud_visible(True)

    def fire_lasers(self):
        laser_data = super().fire_lasers()
        if hasattr(self, 'network_manager'):
            for pos, vel in laser_data:
                self.network_manager.fire_laser(pos, vel)

    def update(self):
        if held_keys['escape']:
            import os
            os._exit(0)
        
        if self.dead: return

        joy_x = self.ui.cursor_pos.x
        joy_y = self.ui.cursor_pos.y

        if abs(joy_x) < self.ui.deadzone: joy_x = 0
        if abs(joy_y) < self.ui.deadzone: joy_y = 0

        current_sens = self.ui.get_sensitivity()
        curve = self.ui.get_sensitivity_curve()
        current_accel = self.ui.get_acceleration()
        current_max_speed = self.ui.get_max_speed()
        current_roll_accel = self.ui.get_roll_acceleration()
        current_max_roll_speed = self.ui.get_max_roll_speed()

        # Boost logic
        if held_keys['left shift'] and self.boost_fuel > 0:
            self.is_boosting = True
            self.boost_fuel -= cfg.BOOST_DRAIN_RATE * time.dt
            if self.boost_fuel < 0: self.boost_fuel = 0
            current_sens *= cfg.BOOST_TURN_MULT
        else:
            self.is_boosting = False
            self.boost_fuel += cfg.BOOST_RECHARGE_RATE * time.dt
            if self.boost_fuel > cfg.BOOST_FUEL_MAX: self.boost_fuel = cfg.BOOST_FUEL_MAX
            
        norm_x = clamp(joy_x / self.ui.max_radius, -1, 1)
        norm_y = clamp(joy_y / self.ui.max_radius, -1, 1)
        
        curved_norm_x = math.copysign(abs(norm_x) ** curve, norm_x)
        curved_norm_y = math.copysign(abs(norm_y) ** curve, norm_y)
        
        scaled_joy_x = curved_norm_x * 0.5
        scaled_joy_y = curved_norm_y * 0.5

        target_yaw_vel = scaled_joy_x * current_sens
        target_pitch_vel = -scaled_joy_y * current_sens

        turn_acceleration = cfg.TURN_ACCELERATION
        self.angular_vel_yaw = lerp(self.angular_vel_yaw, target_yaw_vel, turn_acceleration * time.dt)
        self.angular_vel_pitch = lerp(self.angular_vel_pitch, target_pitch_vel, turn_acceleration * time.dt)

        delta_yaw = self.angular_vel_yaw * time.dt
        delta_pitch = self.angular_vel_pitch * time.dt

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
            
            if impact_speed > 5.0 and not self.dead:
                damage = impact_speed * 5.0
                self.take_damage(damage)
                if hasattr(hit_info.entity, 'take_damage'):
                    hit_info.entity.take_damage(damage)
                    
            self.position -= self.velocity * time.dt
            if hit_info.normal.length() > 0:
                self.velocity = self.velocity - 2 * self.velocity.dot(hit_info.normal) * hit_info.normal
            else:
                self.velocity = -self.velocity
            self.velocity *= 0.5

    def intersects(self):
        dist = self.velocity.length() * time.dt
        if dist > 0:
            return raycast(self.position, self.velocity.normalized(), distance=dist, ignore=(self,))
        return raycast(self.position, self.forward, distance=0.1, ignore=(self,))


class RemotePlayer(BaseShip):
    def __init__(self, **kwargs):
        super().__init__(color_choice=color.blue, **kwargs)
        self.target_position = self.position
        self.target_rotation = self.rotation

    def take_damage(self, amount):
        pass # Remote players only die when the server/their client says so!

    def die(self):
        pass

    def respawn(self):
        pass

    def update(self):
        if self.dead: return
        self.position = self.target_position
        self.rotation = self.target_rotation
