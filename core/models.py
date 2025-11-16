from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from engine.physics import Phys
from engine.system import IO
from core.config import *
from consts import *
from core.materials import *
import uuid


class Rules:


    def __init__(self, explosive: bool = None, gravitational: bool = None, collidable: bool = None, moveable: bool = None):

        self.explosive = explosive
        self.gravitational = gravitational
        self.collidable = collidable
        self.moveable = moveable

    def __repr__(self):
        return f"Can be exploded: {self.explosive} | Can be gravitied: {self.gravitational} | Can collide: {self.collidable}"


class Cube(Entity):
    def __init__(self, material = Stone, rules: Rules = None):
        super().__init__()
        self.default_rules = Rules(True, True, True, True)
        self.ignore = True

        self.rules = rules
        if self.rules is None: self.rules = self.default_rules

        self.material_type = material
        self.texture = "white_cube"
        self.model = "cube"
        self.collider = "box"
        self.affectable = True
        self.velocity = Vec3(0, 0, 0)
        self.on_ground = True
        self.world = {}
        self.died = False
        self.moving = False
        self.object_id = uuid.uuid1()


        self.weight = (self.scale_x_getter() + self.scale_y_getter() + self.scale_z_getter()) * self.material_type.density


    def apply_force(self, force, direction, impulse):
        acceleration = direction * (force / self.weight)
        self.velocity += acceleration * impulse



    def update(self, dt):
        self.velocity = Phys.calculate_falling(self.velocity, dt)
        self.velocity.x *= FRICTION
        self.velocity.z *= FRICTION

        if self.on_ground:
            self.velocity.y = 0

        self.position += self.velocity * dt

        if self.position.y <= GROUND_LEVEL:
            self.position.y = GROUND_LEVEL
            self.on_ground = True
        else:
            self.on_ground = False

        if distance(Vec3(0, 0, 0), self.velocity) > COLLISION_THRESHOLD:
            self.moving = True
        else:
            self.moving = False


class Explosion(Entity):
    def __init__(self, rules: Rules = None):
        super().__init__()

        self.default_rules = Rules(True, False, True, False)

        self.rules = rules
        if self.rules is None: self.rules = self.default_rules

        self.ignore = True
        self.object_id = uuid.uuid1()

        self.model = "sphere"
        self.collider = "box"
        self.color = color.red
        self.power = 1000
        self.affectable = False
        self.exploded = False
        self.explosion_delay = 1
        self.left_time = self.explosion_delay
        self.min_size = Vec3(1, 1, 1)
        self.max_size = Phys.explosion_radius(self.power)
        self.affected_entities = set()
        self.world = {}
        self.died = False

        self.fixed_position = None

    def update(self, dt):



        if self.died:
            return

        if self.exploded and self.fixed_position is None:
            self.fixed_position = Vec3(self.position.x, self.position.y, self.position.z)

        if self.fixed_position is not None:
            self.position = self.fixed_position

        if self.exploded and self.left_time <= 0:

            expansion_rate = (self.max_size - self.min_size) / EXPLOSION_SPEED
            new_scale = self.scale + expansion_rate * dt

            if new_scale.x > self.max_size.x:
                self.scale = self.max_size
            else:
                self.scale = new_scale

            if "objects" in self.world:
                hits = Phys.get_range_units(self.world, self.scale_x, self.position)

                for hit in hits:
                    print(f'==========={hit}===========')
                    print(f"{hit in self.affected_entities}")
                    print(f"{hit == self}")
                    print(f"{isinstance(hit, Explosion)}")
                    if hit in self.affected_entities or hit == self or isinstance(hit, Explosion):
                        print(f"{hit} is skipping...")
                        continue

                    print(f"explosive: {hit.rules.explosive} and moveable: {hit.rules.moveable}")
                    if hit.rules.explosive and hit.rules.moveable:

                        print(f"hasattr exploded: {hasattr(hit, 'exploded')}")

                        if hasattr(hit, "exploded") and not hit.exploded:
                            hit.explosion_delay = 0.1
                            hit.exploded = True

                        print(f"has weight: {hasattr(hit, 'weight')} and has apply force: {hasattr(hit, 'apply_force')}")
                        if hasattr(hit, "weight") and hasattr(hit, "apply_force"):
                            r = Phys.calculate_force(
                                power=self.power,
                                hit=hit,
                                own=self,
                                dt=dt
                            )

                            hit.apply_force(r["force"], r["direction"], r["impulse"])
                            self.affected_entities.add(hit)
                            print(
                                f"Взрыв! Объект на {hit.position}, расстояние={r['distance']:.2f}, сила={r['force']:.2f}")

        elif self.exploded and self.left_time > 0:
            self.left_time -= dt
            self.color = color.rgb(255, int(128 + 127 * abs(sin(self.left_time * 10))), 0)

        if self.exploded and self.scale_x >= self.max_size.x:
            self.alpha = max(0, self.alpha - dt * 2)
            if self.alpha <= 0:
                self.died = True

class Ground(Entity):
    def __init__(self, rules: Rules = Rules(True, True,  True)):
        super().__init__()

        self.rules = rules
        self.model = "plane"
        self.texture = "grass"
        self.scale = (64, 1, 64)
        self.position = Vec3(0, 0, 0)
        self.affectable = False
        self.texture_scale = (4, 4)
        self.collider = "box"
        self.color = color.green
        self.world = {}

    def update(self):

        for obj in self.world["objects"]:
            if obj.position.y < GROUND_LEVEL:
                try:
                    obj.velocity.y = 0
                except AttributeError:
                    pass
                obj.position.y = GROUND_LEVEL


class Player(FirstPersonController):
    def __init__(self):
        super().__init__()
        self.speed = 10




class Wind:

    def __init__(self, wind_speed: float = 1.00, direction: Vec3 = Vec3(-1, 0, 0)):

        self.air_density = AIR_DENSITY
        self.wind_speed = wind_speed
        self.direction = direction
        self.world = {}

    def update(self):

        if self.world == {}:
            return

        for obj in self.world["objects"]:


            if hasattr(obj, "affectable") and hasattr(obj, "weight"):
                f = 0.5 * self.air_density * (self.wind_speed ** 2) * (obj.scale.x * obj.scale.y)
                acceleration = self.direction.normalized() * (f / obj.weight)
                obj.velocity += acceleration * time.dt


DYNAMIC_OBJECTS = [
    Cube, Explosion
]