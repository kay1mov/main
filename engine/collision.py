from ursina import *
from engine.physics import Phys
from consts import *

class Collision:

    def __init__(self, colliders: list):

        self.colliders = colliders

    def collider(self, obj):

        self.colliders.append(obj)

    def do_not_fall_in_to_block(self, obj):
        i = obj.intersects()

        if not i.hit:
            return

        for e in i.entities:
            try:
                if obj.position.y >= e.position.y + e.scale_y / 2:
                    if (
                            abs(e.position.x - obj.position.x) <= (e.scale_x + obj.scale_x) / 2 and
                            abs(e.position.z - obj.position.z) <= (e.scale_z + obj.scale_z) / 2
                    ):
                        try:
                            energy = Phys.get_object_energy(obj)
                            e.apply_force(force=energy, direction=Vec3(0, -1, 0), impulse=abs(obj.velocity.y))
                        except AttributeError:
                            pass

                        obj.velocity.y = 0
                        obj.position.y = max(GROUND_LEVEL, e.position.y + e.scale_y / 2 + obj.scale_y / 2 + 0.001)
                        obj.on_ground = True
                        break
            except AttributeError:
                continue

    def apply_colliding(self):
        for o in self.colliders:
            i = o.intersects()
            if not i.hit:
                continue

            e = i.entity
            if e.rules.collidable:

                offset_value = (o.scale_y + e.scale_y) / 4 - i.distance

                if offset_value > 0:
                    offset_value = min(offset_value, 0.1)
                    adt = i.normal * offset_value
                    o.position += adt

                    if hasattr(o, "apply_force") and o.rules.moveable:


                        energy = Phys.get_object_energy(o)

                        abs_vel = Phys.get_distance_by_velocity(o.velocity)
                        if abs_vel == 0: abs_vel = 1

                        direction = (e.world_position - o.world_position).normalized()
                        try:
                            e.apply_force(force=energy, direction=direction, impulse=1 / abs_vel)
                        except AttributeError:
                            pass



            self.do_not_fall_in_to_block(o)