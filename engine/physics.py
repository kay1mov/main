
import math
from consts import *
from ursina import Entity, Vec3


class Phys:

    def __init__(self):
        pass

    @staticmethod
    def explosion_radius(energy: float = 1, k: float = 5) -> Vec3:
        """
        Радиус взрыва пропорционален кубическому корню от энергии
        R = k * E^(1/3)
        :param energy: Энергия взрыва (мощность)
        :param k: Коэффициент подстройки под игровой баланс
        :return: Vec3 с радиусом взрыва
        """

        radius = k * math.copysign(abs(energy) ** (1 / 3), energy)
        return Vec3(radius, radius, radius)

    @staticmethod
    def calculate_force(power: float, hit: Entity, own: Entity, dt: float) -> dict:
        """
        Сила зависит от энергии, расстояния до центра и массы объекта

        F = P / D²

        P = Энергия
        D = Расстояние от центра до объекта
        F = Сила применяемая к объекту

        :param power: Энергия
        :param hit: Жертва
        :param own: Бомба
        :param dt: Дельта-тайм
        :return: dict с направлением, силой и импульсом
        """

        direction = (hit.world_position - own.world_position)
#        radius = max(hit.scale.x, hit.scale.y, hit.scale.z) * 0.5
        distance = max(direction.length(), 0.500)
        direction = direction.normalized()


        force = power / (distance ** 2)

        impulse = force * dt * 0.5

        return {
            "direction": direction,
            "force": force,
            "impulse": impulse,
            "distance": distance
        }

    @staticmethod
    def calculate_falling(velocity: Vec3, dt: float) -> Vec3:

        """
        Ускорение = текущее ускорение + гравитация * дельта тайм
        :param velocity: Vec3(float, float, float)
        :param dt: float
        :return: Vec3(float, float, float)
        """

        velocity.y += GRAVITY * dt

        return velocity

    @staticmethod
    def get_range_units(world, radius, center):

        """
        :param world: dict
        :param radius: float
        :param center: Vec3(float, float, float)
        :return: List[Objects]
        """

        au = []
        for cube in world["objects"]:
            if cube is None or cube.is_empty():
                continue

            dist = math.dist(cube.position, center)
            if dist <= radius:
                au.append(cube)
        return au

    @staticmethod
    def get_object_energy(obj):
        """
        Энергия объекта равен ее абсолютной скорости * на массу
        :param obj:
        :return: float
        """

        x, y, z = obj.velocity
        w = obj.weight

        e = w * (abs(x) + abs(y) + abs(z))

        return e

    @staticmethod
    def get_distance_by_velocity(velocity: Vec3):
        """
        :param velocity: Vector3
        :return: float
        """

        return abs(velocity.x)+abs(velocity.y)+abs(velocity.z)