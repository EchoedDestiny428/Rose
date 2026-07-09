from ursina import *
import random
import math
import src.settings as cfg

class Starfield(Entity):
    def __init__(self, num_stars=cfg.STARFIELD_NUM_STARS, radius=cfg.STARFIELD_RADIUS):
        super().__init__()
        verts = []
        colors = []
        for _ in range(num_stars):
            theta = random.uniform(0, 2 * math.pi)
            phi = math.acos(random.uniform(-1, 1))
            x = radius * math.sin(phi) * math.cos(theta)
            y = radius * math.sin(phi) * math.sin(theta)
            z = radius * math.cos(phi)
            verts.append(Vec3(x, y, z))
            
            c = random.choice([
                color.white, 
                color.rgb(200, 220, 255),
                color.rgb(255, 230, 200)
            ])
            colors.append(c)
            
        self.model = Mesh(vertices=verts, colors=colors, mode='point', thickness=3)
        self.unlit = True
        self.alpha = 0.4

    def update(self):
        self.position = camera.world_position

class SpaceDust(Entity):
    def __init__(self, num_particles=cfg.SPACEDUST_NUM_PARTICLES, radius=cfg.SPACEDUST_RADIUS):
        super().__init__()
        self.radius = radius
        self.particles = []
        for _ in range(num_particles):
            p = Entity(
                model='cube', 
                color=color.white, 
                scale=random.uniform(0.1, 0.4), 
                position=self.get_random_pos(Vec3(0,0,0)),
                unlit=True,
                parent=self
            )
            p.alpha = 0.5
            self.particles.append(p)

    def get_random_pos(self, center):
        return center + Vec3(
            random.uniform(-self.radius, self.radius),
            random.uniform(-self.radius, self.radius),
            random.uniform(-self.radius, self.radius)
        )

    def update(self):
        cam_pos = camera.world_position
        for p in self.particles:
            if p.world_x - cam_pos.x > self.radius: p.x -= self.radius * 2
            elif p.world_x - cam_pos.x < -self.radius: p.x += self.radius * 2
            
            if p.world_y - cam_pos.y > self.radius: p.y -= self.radius * 2
            elif p.world_y - cam_pos.y < -self.radius: p.y += self.radius * 2
            
            if p.world_z - cam_pos.z > self.radius: p.z -= self.radius * 2
            elif p.world_z - cam_pos.z < -self.radius: p.z += self.radius * 2

class Obstacle(Entity):
    def __init__(self, player):
        super().__init__(
            model='cube',
            collider='box',
            color=color.white
        )
        self.transparent = True
        self.player = player
        self.max_health = 3000.0
        self.respawn()

    @property
    def hp(self):
        actual_ratio = self.health / self.max_health
        display_ratio = (actual_ratio - 0.2) / 0.8
        return max(0.0, display_ratio)

    def respawn(self):
        if hasattr(self, 'player') and self.player and hasattr(self.player, 'ui'):
            if self.player.ui.hard_target == self:
                self.player.ui.set_hard_target(None)
        
        self.health = self.max_health
        self.color = color.white
        self.alpha = 1.0
        self.scale = (random.uniform(12, 32), random.uniform(12, 32), random.uniform(12, 32))
        self.rotation = Vec3(random.uniform(0, 360), random.uniform(0, 360), random.uniform(0, 360))
        
        player_pos = self.player.world_position if self.player else Vec3(0,0,0)
        dist = random.uniform(cfg.OBSTACLE_SPAWN_MIN_DIST, cfg.OBSTACLE_SPAWN_MAX_DIST)
        dir_vec = Vec3(random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)).normalized()
        self.position = player_pos + dir_vec * dist

    def take_damage(self, amount):
        self.health -= amount
        hp_ratio = self.health / self.max_health
        if hp_ratio <= 0.2:
            self.respawn()
        else:
            self.alpha = hp_ratio

def setup_environment(player=None):
    window.color = color.black
    mouse.visible = False
    
    lumina = DirectionalLight()
    lumina.look_at(Vec3(1, -1, 1))

    cubes = []
    for _ in range(cfg.CUBE_COUNT):
        c = Obstacle(player)
        cubes.append(c)

    stars = Starfield()
    dust = SpaceDust()
    return stars, dust, lumina, cubes
