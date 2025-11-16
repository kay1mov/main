from ursina import Ursina, window
from engine.game import Game


def input(key):
    if game:
        game.input(key)


def update():
    if game:
        game.update()


urs = Ursina()

game = Game()

window.update = update
window.input = input
window.fullscreen = False

urs.run()
