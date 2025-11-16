from ursina import rgb

class BaseMaterialModel:

    def __init__(self, density: float, jumping_threshold: float, name: str, colour: rgb):

        self.density = density
        self.jumping_threshold = jumping_threshold
        self.name = name
        self.colour = colour

    def __repr__(self):
        return f"Name: {self.name} \nJumping Threshold: {self.jumping_threshold}\nDensity: {self.density}\nColor: {self.colour}"