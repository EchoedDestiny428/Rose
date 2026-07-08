from ursina import *
import random

class SpaceDust(Entity):
    def __init__(self, num_particles=600, radius=200):
        super().__init__()
        self.radius = radius
        self.particles = []
        for _ in range(num_particles):
            p = Entity(
                model='sphere',
                color=color.rgba(200, 220, 255, 180),
                scale=random.uniform(0.02, 0.08),
                position=self.get_random_pos(Vec3(0,0,0)),
                unlit=True, # Make it visible regardless of lighting
                parent=self
            )
            self.particles.append(p)

    def get_random_pos(self, center):
        return center + Vec3(
            random.uniform(-self.radius, self.radius),
            random.uniform(-self.radius, self.radius),
            random.uniform(-self.radius, self.radius)
        )

    def update(self):
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

    box = Entity(
        model='cube',
        name='front_object',
        color=color.azure,
        scale=(5.0, 5.0, 5.0),
        position=(0.0, 0.0, 30.0),
        rotation=(25, 45, 0)
    )

    dust = SpaceDust()
    return dust, box, lumina
