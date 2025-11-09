
from ursina import *

from consts import GROUND_LEVEL
from core.models import Player, Ground, Explosion, Cube
from engine.system import ThreadMaster


class Game:

    def __init__(self):
        self.tdm = ThreadMaster()
        self.index = 0

        self.world = {
            "ground": None,
            "objects": []
        }

        self.available_objects = [
            {
                "name": "Block",
                "object": Cube
            },
            {
                "name": "TNT",
                "object": Explosion
            }
        ]

        self.ground = Ground()
        self.ground.position = (0, 0, 0)
        self.ground.scale = 256

        self.world["ground"] = self.ground

        self.player = Player()
        self.player.position = (0, 2, 0)
        self.player.gravity = 0.5

        camera.fov = 110

        self.dl = DirectionalLight(y=2, z=3, shadows=True)
        self.al = AmbientLight(color=color.rgba(100, 100, 100, 100))
        self.sky = Sky()

        self.create_demo_scene()


    def create_demo_scene(self):

        for _ in range(128):

            cube = Cube()
            pos = Vec3(random.randint(-32, 32), random.randint(1, 1000), random.randint(-32, 32))

            self.add_object(cube, pos)




    def add_object(self, obj, pos):
        obj.position = pos
        self.world["objects"].append(obj)

    def input(self, key):
        if key == "left mouse down":
            if mouse.hovered_entity:
                entity = mouse.hovered_entity
                if isinstance(entity, Explosion) and not entity.exploded:
                    entity.exploded = True
                    entity.left_time = entity.explosion_delay

        elif key == "right mouse down":
            try:
                p = mouse.world_point
                if p.y < GROUND_LEVEL:
                    p.y = GROUND_LEVEL
                self.add_object(self.available_objects[self.index]["object"](), p)
            except:
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

    def update(self):
        for obj in self.world["objects"]:
            if obj.died:
                self.world["objects"].remove(obj)
                destroy(obj)
            else:
                obj.world = self.world
                obj.update()

                if obj.position.x > self.ground.scale // 2:

                    if obj.velocity.x == 0:
                        obj.position.x = self.ground.scale // 2
                    elif obj.velocity.x > 0:
                        obj.velocity.x *= -1

                elif obj.position.x < -self.ground.scale // 2:

                    if obj.velocity.x == 0:
                        obj.position.x = -self.ground.scale // 2

                    elif obj.velocity.x < 0:
                        obj.velocity.x = abs(obj.velocity.x)

                if obj.position.z > self.ground.scale // 2:

                    if obj.velocity.z == 0:
                        obj.position.z = self.ground.scale // 2
                    elif obj.velocity.z > 0:
                        obj.velocity.z *= -1

                elif obj.position.z < -self.ground.scale // 2:

                    if obj.velocity.z == 0:
                        obj.position.z = -self.ground.scale // 2

                    elif obj.velocity.z < 0:
                        obj.velocity.z = abs(obj.velocity.z)





#            print(obj.position)


def input(key):
    game.input(key)


def update():
    game.update()


urs = Ursina()
game = Game()
urs.run()