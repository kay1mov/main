from engine.collision import Collision
from ursina import *
from consts import GROUND_LEVEL
from core.models import Player, Ground, Explosion, Cube, Wind, Rules



class Game:

    def __init__(self):

        self.index = 0
        self.cmd_opened = False
        self.entered_text = ""

        self.entered_text_label = Text(origin=(-.5, .5))
        self.entered_text_label.size = 10


        self.world = {
            "ground": None,
            "objects": []
        }

        self.available_objects = [
            {
                "name": "Block",
                "object": Cube,
                "rules": Rules(explosive=True, gravitational=True, collidable=True, moveable=True)
            },
            {
                "name": "TNT",
                "object": Explosion,
                "rules": Rules(explosive=False, gravitational=False, collidable=False, moveable=False)
            }
        ]

        self.wind = Wind()
        self.wind.wind_speed = 0

        self.collide_master = Collision([])

        self.ground = Ground()
        self.ground.position = Vec3(0, 0, 0)
        self.ground.scale = 256

        self.world["ground"] = self.ground

        self.player = Player()
        self.player.position = (0, 2, 0)
        self.player.gravity = 1

        camera.fov = 110

        self.dl = DirectionalLight(y=2, z=3, shadows=True)
        self.al = AmbientLight(color=color.rgba(100, 100, 100, 100))
        self.sky = Sky()

        self.demo_wind()


    #wind
    def demo_wind(self):

        self.wind_speed_start = 0
        self.wind_speed_stop = 1000
        self.wind_speed_step = 50
        self._iw = 0


    #gravity
    def demo_gravity(self):

        for o in self.world["objects"]:
            destroy(o)
            self.world["objects"].remove(o)

        start_x, start_y, start_z = 2, 50, 2
        for _ in range(10):

            c = Cube()
            p = Vec3(start_x + (_ * 2), start_y + (_ * 2), start_z)
            self.add_object(c, p)

        self.add_object(Cube(), Vec3(0, 10_000, 0))

    def build_structure(self):
        block = 1

        for x in range(-2, 3):
            for z in range(-2, 3):
                c = Cube()
                p = Vec3(x * block, 0, z * block)
                self.add_object(c, p)

        for y in range(1, 7):
            for x in range(-1, 2):
                for z in range(-1, 2):
                    if abs(x) == 1 or abs(z) == 1:
                        c = Cube()
                        p = Vec3(x * block + 5, y * block, z * block)
                        self.add_object(c, p)

        for x in range(-1, 2):
            for z in range(-1, 2):
                c = Cube()
                p = Vec3(x * block + 5, 7 * block, z * block)
                self.add_object(c, p)

        for y in range(1, 4):
            for side in (-3, -1):
                c = Cube()
                p = Vec3(side, y, -5)
                self.add_object(c, p)

        for x in range(-3, 0):
            c = Cube()
            p = Vec3(x, 4, -5)
            self.add_object(c, p)

        for i in range(6):
            c = Cube()
            p = Vec3(i, 2, 3)
            self.add_object(c, p)

            if i % 2 == 0:
                for y in range(1, 3):
                    c2 = Cube()
                    p2 = Vec3(i, 2 - y, 3)
                    self.add_object(c2, p2)

    def add_object(self, obj, pos, rules: Rules = None):
        obj.position = pos
        if rules is not None:
            obj.rules = rules


        try:
            if obj.rules.collidable:
                self.collide_master.collider(obj)
        except AttributeError:
            try:
                if obj.default_rules.collider:
                    self.collide_master.collider(obj)
                else:
                    pass
            except:
                pass

        self.world["objects"].append(obj)


    def input(self, key):
        if key == "left mouse down":
            if mouse.hovered_entity:
                entity = mouse.hovered_entity

                if isinstance(entity, Explosion) and not entity.exploded:
                    entity.exploded = True
                    entity.left_time = entity.explosion_delay

                else:
                    if hasattr(entity, "affectable") and entity.affectable:
                        try:
                            self.world["objects"].remove(entity)
                        except ValueError:
                            pass
                        destroy(entity)

        elif key == "right mouse down":

            hit_info = raycast(camera.world_position, camera.forward, distance=999)

            print(f"HIT INFO: {hit_info}")

            p = mouse.world_point
            print(f"Mouse world point: {p}")

            try:

                if p.y < GROUND_LEVEL: p.y = GROUND_LEVEL

            except AttributeError:
                print("Attribute error on checking Y of mouse world point")
                return

            if hit_info.hit and hit_info.entity.rules.collidable and not isinstance(hit_info.entity, Ground):
                p = hit_info.entity.position + hit_info.normal
                print(f"new P = {p}")

            try:

                o = self.available_objects[self.index]["object"]()
                print(f"Object: {o}")
                self.add_object(o, p, self.available_objects[self.index]["rules"])

            except IndexError:

                pass

        if key in [str(e) for e in range(0, 9)]:
            self.index = int(key)
            try:
                obj_name = self.available_objects[self.index]["name"]
                print(f"Выбран объект: {obj_name}")
            except IndexError:
                return

        if key == "=":
            self.player.speed += 1
        elif key == "-":
            self.player.speed -=1

        if key == "f":
            try:
                if self._iw >= self.wind_speed_stop / self.wind_speed_step:
                    self._iw = 0

                self.wind.wind_speed = self.wind_speed_step * self._iw
                self._iw += 1
            except:
                self.demo_wind()

        if key == "g":

            self.demo_gravity()

        if key == "c":

            for o in self.world["objects"]:
                destroy(o)
                self.world["objects"].remove(o)

        if key == "o":
            self.build_structure()
    def update(self):

        self.entered_text_label = self.entered_text
        self.collide_master.apply_colliding()

        if self.wind:
            self.wind.world = self.world
            self.wind.update()

        if self.ground:
            self.ground.world = self.world


        for obj in self.world["objects"]:
            if obj.died:
                self.world["objects"].remove(obj)
                destroy(obj)
            else:
                obj.world = self.world
                obj.update(time.dt)

                try:
                    if obj.position.x > self.ground.scale / 2:

                        if obj.velocity.x == 0:
                            obj.position.x = self.ground.scale_x_getter() / 2
                        elif obj.velocity.x > 0:
                            obj.velocity.x *= -1

                    elif obj.position.x < -self.ground.scale_x_getter() / 2:

                        if obj.velocity.x == 0:
                            obj.position.x = -self.ground.scale_x_getter() / 2

                        elif obj.velocity.x < 0:
                            obj.velocity.x = abs(obj.velocity.x)

                    if obj.position.z > self.ground.scale_z_getter() / 2:

                        if obj.velocity.z == 0:
                            obj.position.z = self.ground.scale_z_getter() / 2
                        elif obj.velocity.z > 0:
                            obj.velocity.z *= -1

                    elif obj.position.z < -self.ground.scale_z_getter() / 2:

                        if obj.velocity.z == 0:
                            obj.position.z = -self.ground.scale_z_getter() / 2

                        elif obj.velocity.z < 0:
                            obj.velocity.z = abs(obj.velocity.z)
                except AttributeError:
                    pass


        if self.player.position.y <= -50:
            self.player.position = Vec3(0, 1, 0)



