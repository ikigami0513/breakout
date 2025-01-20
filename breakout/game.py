import glm
from enum import StrEnum
from typing import Optional
from breakout.sprite_renderer import SpriteRenderer
from breakout.resource_manager import ResourceManager

class GameState(StrEnum):
    GAME_ACTIVE = "GAME_ACTIVE"
    GAME_MENU = "GAME_MENU"
    GAME_WIN = "GAME_WIN"

class Game:
    def __init__(self, width: int, height: int):
        self.state = GameState.GAME_ACTIVE
        self.keys = [False for _ in range(1024)]
        self.width = width
        self.height = height

        self.renderer: Optional[SpriteRenderer] = None

    def init(self) -> None:
        # initialize game state (load all shaders/textures/levels)
        
        # load shaders
        ResourceManager.load_shader("sprite", "breakout/shaders/sprite.vs", "breakout/shaders/sprite.fs")

        # configure shaders
        projection = glm.ortho(0.0, float(self.width), float(self.height), 0.0, -1.0, 1.0)
        shader = ResourceManager.get_shader("sprite")
        shader.use()
        shader.set_int("image", 0)
        shader.set_mat4("projection", projection)

        # set render-specific controls
        self.renderer = SpriteRenderer(shader)

        # load textures
        ResourceManager.load_texture("textures/awesomeface.png", True, "face")

    def process_input(self, dt: float):
        pass

    def update(self, dt: float):
        pass

    def render(self):
        self.renderer.draw_sprite(
            ResourceManager.get_texture("face"),
            glm.vec2(200.0, 200.0),
            glm.vec2(300.0, 400.0),
            45.0,
            glm.vec3(0.0, 1.0, 0.0)
        )
    