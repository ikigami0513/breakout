import glm
from breakout.game_object import GameObject
from breakout.texture2d import Texture2D
from typing import Optional

class BallObject(GameObject):
    def __init__(
        self,
        position: glm.vec2,
        radius: float = 12.5,
        velocity: glm.vec2 = glm.vec2(0.0, 0.0),
        sprite: Optional[Texture2D] = None,
        stuck: bool = True
    ):
        super().__init__(
            position=position, 
            sprite=sprite, 
            velocity=velocity,
            size=glm.vec2(radius * 2.0, radius * 2.0)
        )
        self.radius = radius
        self.stuck = stuck

    def move(self, dt: float, window_width: int) -> glm.vec2:
        # if not stuck to player board
        if not self.stuck:
            # move ball
            self.position += self.velocity * dt

            # check if outside window bounds; if so, reverse velocity and restore at correct position
            if self.position.x <= 0.0:
                self.velocity.x = -self.velocity.x
                self.position.x = 0.0
            elif self.position.x + self.size.x >= window_width:
                self.velocity.x = -self.velocity.x
                self.position.x = window_width - self.size.x
            
            if self.position.y <= 0.0:
                self.velocity.y = -self.velocity.y
                self.position.y = 0.0
            
        return self.position

    def reset(self, position: glm.vec2, velocity: glm.vec2) -> None:
        self.position = position
        self.velocity = velocity
        self.stuck = True
