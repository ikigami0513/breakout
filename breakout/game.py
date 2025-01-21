import glm
from glfw.GLFW import *
from enum import StrEnum
from typing import Optional, Tuple
from breakout.sprite_renderer import SpriteRenderer
from breakout.resource_manager import ResourceManager
from breakout.game_object import GameObject
from breakout.game_level import GameLevel
from breakout.ball_object import BallObject

# Initial size of the player paddle
PLAYER_SIZE = glm.vec2(100.0, 20.0)

# Initial velocity of the player paddle
PLAYER_VELOCITY = 500.0

# Initial velocity of the ball
INITIAL_BALL_VELOCITY = glm.vec2(100.0, -350.0)

# Radius of the ball object
BALL_RADIUS = 12.5

# represents the current state of the game
class GameState(StrEnum):
    GAME_ACTIVE = "GAME_ACTIVE"
    GAME_MENU = "GAME_MENU"
    GAME_WIN = "GAME_WIN"

# represents the four possible (collision) directions
class Direction(StrEnum):
    UP = "UP"
    RIGHT = "RIGHT"
    DOWN = "DOWN"
    LEFT = "LEFT"

# Defines a Collision type that represents collision data
# bool: collision ?
# Direction: what direction ?
# glm.vec2: difference vector center - closest point
Collision = Tuple[bool, Direction, glm.vec2]

class Game:
    def __init__(self, width: int, height: int):
        self.state = GameState.GAME_ACTIVE
        self.keys = [False for _ in range(1024)]
        self.width = width
        self.height = height

        self.renderer: Optional[SpriteRenderer] = None

        self.levels: list[GameLevel] = []
        self.level: int = 0

        self.player: Optional[GameObject] = None
        self.ball: Optional[BallObject] = None

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
        ResourceManager.load_texture("textures/background.jpg", False, "background")
        ResourceManager.load_texture("textures/awesomeface.png", True, "face")
        ResourceManager.load_texture("textures/block.png", False, "block")
        ResourceManager.load_texture("textures/block_solid.png", False, "block_solid")
        ResourceManager.load_texture("textures/paddle.png", True, "paddle")

        # load levels
        self.levels.append(GameLevel("levels/one.lvl", self.width, self.height / 2))
        self.levels.append(GameLevel("levels/two.lvl", self.width, self.height / 2))
        self.levels.append(GameLevel("levels/three.lvl", self.width, self.height / 2))
        self.levels.append(GameLevel("levels/four.lvl", self.width, self.height / 2))
        self.level = 0

        player_pos = glm.vec2(
            self.width / 2.0 - PLAYER_SIZE.x / 2.0,
            self.height - PLAYER_SIZE.y
        )
        self.player = GameObject(
            position=player_pos,
            size=PLAYER_SIZE,
            sprite=ResourceManager.get_texture("paddle")
        )

        ball_pos = player_pos + glm.vec2(
            PLAYER_SIZE.x / 2.0 - BALL_RADIUS, -BALL_RADIUS * 2.0
        )
        self.ball = BallObject(ball_pos, BALL_RADIUS, INITIAL_BALL_VELOCITY, ResourceManager.get_texture("face"))

    def process_input(self, dt: float):
        if self.state == GameState.GAME_ACTIVE:
            velocity = PLAYER_VELOCITY * dt

            if self.keys[GLFW_KEY_A]:
                if self.player.position.x >= 0.0:
                    self.player.position.x -= velocity
                    if self.ball.stuck:
                        self.ball.position.x -= velocity

            if self.keys[GLFW_KEY_D]:
                if self.player.position.x <= self.width - self.player.size.x:
                    self.player.position.x += velocity
                    if self.ball.stuck:
                        self.ball.position.x += velocity

            if self.keys[GLFW_KEY_SPACE]:
                self.ball.stuck = False


    def update(self, dt: float):
        # update objects
        self.ball.move(dt, self.width)

        # check for collisions
        self.do_collisions()

    def render(self):
        # draw background
        self.renderer.draw_sprite(
            ResourceManager.get_texture("background"),
            glm.vec2(0.0, 0.0),
            glm.vec2(self.width, self.height),
            0.0
        )

        # draw level
        self.levels[self.level].draw(self.renderer)

        # draw player
        self.player.draw(self.renderer)

        # draw ball
        self.ball.draw(self.renderer)
    
    def do_collisions(self):
        for box in self.levels[self.level].bricks:
            if not box.destroyed:
                if self.ball.check_collision(box):
                    if not box.is_solid:
                        box.destroyed = True
