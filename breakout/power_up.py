import glm
from breakout.game_object import GameObject
from breakout.ball_object import BallObject
from breakout.texture2d import Texture2D


# The size of a PowerUp block
POWERUP_SIZE = glm.vec2(60.0, 20.0)

# Velocity a PowerUp block has when spawned
VELOCITY = glm.vec2(0.0, 150.0)


# PowerUp inherits its state and rendering functions from
# GameObject but also holds extra information to state its
# active duration and whether it is activated or not.
# The type op PowerUp is stored as a string
class PowerUp(GameObject):
    def __init__(self, type: str, color: glm.vec3, duration: float, position: glm.vec2, texture: Texture2D):
        super().__init__(
            position=position,
            size=POWERUP_SIZE,
            texture=texture,
            color=color,
            velocity=VELOCITY
        )
        self.type = type
        self.duration = duration
        self.activated = False
