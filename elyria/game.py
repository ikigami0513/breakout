import os
import glm
import random
from glfw.GLFW import *
from enum import StrEnum
from typing import Optional
from elyria import base_dir
from elyria.sprite_renderer import SpriteRenderer
from elyria.resource_manager import ResourceManager
from elyria.game_object import GameObject
from elyria.ball_object import BallObject
from elyria.collision import check_ball_collision, Direction, check_collision
from elyria.particle import ParticleGenerator
from elyria.post_processor import PostProcessor
from elyria.text_renderer import TextRenderer


class Game:
    def __init__(self, width: int, height: int):
        self.keys = [False for _ in range(1024)]
        self.keys_processed = [False for _ in range(1024)]
        self.width = width
        self.height = height

        self.renderer: Optional[SpriteRenderer] = None
        self.player: Optional[GameObject] = None
        self.ball: Optional[BallObject] = None
        self.particles: Optional[ParticleGenerator] = None
        self.effects: Optional[PostProcessor] = None
        self.text: Optional[TextRenderer] = None

    def init(self) -> None:
        # initialize game state (load all shaders/textures/levels)
        
        # load shaders
        ResourceManager.load_shader("sprite", os.path.join(base_dir, "shaders", "sprite.vs"), os.path.join(base_dir, "shaders", "sprite.fs"))
        ResourceManager.load_shader("particle", os.path.join(base_dir, "shaders", "particle.vs"), os.path.join(base_dir, "shaders", "particle.fs"))
        ResourceManager.load_shader("postprocessing", os.path.join(base_dir, "shaders", "post_processing.vs"), os.path.join(base_dir, "shaders", "post_processing.fs"))

        # configure shaders
        projection = glm.ortho(0.0, float(self.width), float(self.height), 0.0, -1.0, 1.0)
        ResourceManager.get_shader("sprite").use()
        ResourceManager.get_shader("sprite").set_int("image", 0)
        ResourceManager.get_shader("sprite").set_mat4("projection", projection)
        ResourceManager.get_shader("particle").use()
        ResourceManager.get_shader("particle").set_int("sprite", 0)
        ResourceManager.get_shader("particle").set_mat4("projection", projection)

        # set render-specific controls
        self.renderer = SpriteRenderer(ResourceManager.get_shader("sprite"))
        self.effects = PostProcessor(ResourceManager.get_shader("postprocessing"), self.width, self.height)
        self.text = TextRenderer(self.width, self.height)
        self.text.load("fonts/ocraext.ttf", 24)

    def process_input(self, dt: float) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def render(self) -> None:
        pass
    