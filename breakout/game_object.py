import glm
from breakout.texture2d import Texture2D
from breakout.sprite_renderer import SpriteRenderer
from typing import Optional

# Container object for holding all state relevant for a single
# game object entity. Each object in the game likely needs the
# minimal of state as described within GameObject.
class GameObject:
    def __init__(
        self,
        position: glm.vec2 = glm.vec2(0.0, 0.0),
        rotation: float = 0.0,
        size: glm.vec2 = glm.vec2(1.0, 1.0),
        sprite: Optional[Texture2D] = None,
        color: glm.vec3 = glm.vec3(1.0),
        velocity: glm.vec2 = glm.vec2(0.0, 0.0),
        is_solid: bool = False,
        destroyed: bool = False
    ):
        self.position = position
        self.rotation = rotation
        self.size = size
        self.sprite = sprite
        self.color = color
        self.velocity = velocity
        self.is_solid = is_solid
        self.destroyed = destroyed

    def draw(self, renderer: SpriteRenderer) -> None:
        renderer.draw_sprite(
            self.sprite,
            self.position,
            self.size,
            self.rotation,
            self.color
        )

