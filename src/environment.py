from ursina import *
import random
import math

class Starfield(Entity):
    def __init__(self, num_stars=5000, radius=5000):
        super().__init__()
        # Distant background stars (Skybox equivalent)
        verts = []
        colors = []
        for _ in range(num_stars):
            # Random point on a sphere
            theta = random.uniform(0, 2 * math.pi)
            phi = math.acos(random.uniform(-1, 1))
            x = radius * math.sin(phi) * math.cos(theta)
            y = radius * math.sin(phi) * math.sin(theta)
            z = radius * math.cos(phi)
            verts.append(Vec3(x, y, z))
            
            # Pure colors, we will use the entity's .alpha to make them transparent
            c = random.choice([
                color.white, 
                color.rgb(200, 220, 255),  # Blueish
                color.rgb(255, 230, 200)   # Orangeish
            ])
            colors.append(c)
            
        self.model = Mesh(vertices=verts, colors=colors, mode='point', thickness=3)
        self.unlit = True
        self.alpha = 0.4  # 40% opacity for the distant stars

    def update(self):
        # Anchor to camera so stars are infinitely far away (no parallax)
        self.position = camera.position

class SpaceDust(Entity):
    def __init__(self, num_particles=300, radius=80):
        super().__init__()
        # Local space dust to show movement speed (velocity reference)
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
            p.alpha = 0.5  # 50% opacity for dust
            self.particles.append(p)

    def get_random_pos(self, center):
        return center + Vec3(
            random.uniform(-self.radius, self.radius),
            random.uniform(-self.radius, self.radius),
            random.uniform(-self.radius, self.radius)
        )

    def update(self):
        # A small loop is fine for 200 particles
        cam_pos = camera.position
        for p in self.particles:
            if p.x - cam_pos.x > self.radius: p.x -= self.radius * 2
            elif p.x - cam_pos.x < -self.radius: p.x += self.radius * 2
            
            if p.y - cam_pos.y > self.radius: p.y -= self.radius * 2
            elif p.y - cam_pos.y < -self.radius: p.y += self.radius * 2
            
            if p.z - cam_pos.z > self.radius: p.z -= self.radius * 2
            elif p.z - cam_pos.z < -self.radius: p.z += self.radius * 2


def setup_environment():
    window.color = color.black
    mouse.visible = False
    
    lumina = DirectionalLight()
    lumina.look_at(Vec3(1, -1, 1))

    # Random reference cubes
    cubes = []
    for _ in range(3):
        c = Entity(
            model='cube',
            color=color.azure,
            scale=(random.uniform(3, 8), random.uniform(3, 8), random.uniform(3, 8)),
            position=Vec3(
                random.uniform(-40, 40),
                random.uniform(-40, 40),
                random.uniform(20, 80)
            ),
            rotation=Vec3(random.uniform(0, 360), random.uniform(0, 360), random.uniform(0, 360))
        )
        cubes.append(c)

    stars = Starfield()
    dust = SpaceDust()
    return stars, dust, lumina, cubes
