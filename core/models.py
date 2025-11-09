from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from engine.physics import Phys
from consts import *
from core.sounds import Sounds


class Cube(Entity):
    def __init__(self):
        super().__init__()
        self.ignore = False

        self.model = "cube"
        self.weight = 10
        self.collider = "box"
        self.affectable = True
        self.velocity = Vec3(0, 0, 0)
        self.on_ground = True
        self.world = {}
        self.died = False

    def apply_force(self, force, direction, impulse):
        acceleration = direction * (force / self.weight)
        self.velocity += acceleration * impulse
        print(f"Применена сила: {force:.2f}, направление: {direction}, импульс: {impulse:.4f}")

    def affect_to_others(self):
        if "objects" not in self.world:
            return


        origin = self.world_position + (self.up*.5)

        direction = self.position + self.velocity

        distance_traveling = Phys.get_distance_by_velocity(self.velocity)

        hit_info = raycast(origin, direction=direction, ignore=(self,), distance=distance_traveling, debug=False)

        for ent in hit_info.hits:

            if hasattr(ent, "affectable"):

                energy = Phys.get_object_energy(self)
                ent.apply_force(energy, self.velocity, time.dt)


    def update(self):
        self.velocity = Phys.calculate_falling(self.velocity, time.dt)
        self.velocity.x *= FRICTION
        self.velocity.z *= FRICTION

        if self.on_ground:
            self.velocity.y = 0

        self.position += self.velocity * time.dt

        if self.position.y <= GROUND_LEVEL:
            self.position.y = GROUND_LEVEL
            self.on_ground = True
        else:
            self.on_ground = False

        #self.affect_to_others()


class Explosion(Entity):
    def __init__(self):
        super().__init__()

        self.ignore = False

        self.model = "sphere"
        self.collider = "box"
        self.color = color.red
        self.power = 5000
        self.affectable = False
        self.exploded = False
        self.explosion_delay = 3
        self.left_time = self.explosion_delay
        self.min_size = Vec3(1, 1, 1)
        self.max_size = Phys.explosion_radius(self.power)
        self.affected_entities = set()
        self.world = {}
        self.died = False

    def update(self):
        if self.died:
            return

        if self.exploded and self.left_time <= 0:
            Sounds.ExplosionSound()

            expansion_rate = (self.max_size - self.min_size) / EXPLOSION_SPEED
            new_scale = self.scale + expansion_rate * time.dt

            if new_scale.x > self.max_size.x:
                self.scale = self.max_size
            else:
                self.scale = new_scale

            if "objects" in self.world:
                hits = Phys.get_range_units(self.world, self.scale_x, self.position)

                for hit in hits:
                    if hit in self.affected_entities or hit == self:
                        continue

                    if hasattr(hit, "affectable") and hit.affectable:
                        if hasattr(hit, "exploded") and not hit.exploded:
                            hit.exploded = True
                            hit.left_time = 0

                        if hasattr(hit, "weight") and hasattr(hit, "apply_force"):
                            r = Phys.calculate_force(
                                power=self.power,
                                hit=hit,
                                own=self,
                                dt=time.dt
                            )

                            hit.apply_force(r["force"], r["direction"], r["impulse"])
                            self.affected_entities.add(hit)
                            print(
                                f"Взрыв! Объект на {hit.position}, расстояние={r['distance']:.2f}, сила={r['force']:.2f}")

        elif self.exploded and self.left_time > 0:
            self.left_time -= time.dt
            self.color = color.rgb(255, int(128 + 127 * abs(sin(self.left_time * 10))), 0)

        if self.exploded and self.scale_x >= self.max_size.x:
            self.alpha = max(0, self.alpha - time.dt * 2)
            if self.alpha <= 0:
                self.died = True


class Ground(Entity):
    def __init__(self):
        super().__init__()
        self.model = "plane"
        self.texture = "grass"
        self.scale = (64, 1, 64)
        self.position = Vec3(0, 0, 0)
        self.affectable = False
        self.texture_scale = (4, 4)
        self.collider = "box"
        self.color = color.green


class Player(FirstPersonController):
    def __init__(self):
        super().__init__()
        self.speed = 10
        self.collider = 'box'