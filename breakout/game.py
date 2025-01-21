import glm
from glfw.GLFW import *
from enum import StrEnum
from typing import Optional
from breakout.sprite_renderer import SpriteRenderer
from breakout.resource_manager import ResourceManager
from breakout.game_object import GameObject
from breakout.game_level import GameLevel
from breakout.ball_object import BallObject
from breakout.collision import check_ball_collision, Direction
from breakout.particle import ParticleGenerator
from breakout.post_processor import PostProcessor

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
        self.particles: Optional[ParticleGenerator] = None
        self.effects: Optional[PostProcessor] = None
        
        self.shake_time = 0.0

    def init(self) -> None:
        # initialize game state (load all shaders/textures/levels)
        
        # load shaders
        ResourceManager.load_shader("sprite", "breakout/shaders/sprite.vs", "breakout/shaders/sprite.fs")
        ResourceManager.load_shader("particle", "breakout/shaders/particle.vs", "breakout/shaders/particle.fs")
        ResourceManager.load_shader("postprocessing", "breakout/shaders/post_processing.vs", "breakout/shaders/post_processing.fs")

        # configure shaders
        projection = glm.ortho(0.0, float(self.width), float(self.height), 0.0, -1.0, 1.0)
        ResourceManager.get_shader("sprite").use()
        ResourceManager.get_shader("sprite").set_int("image", 0)
        ResourceManager.get_shader("sprite").set_mat4("projection", projection)
        ResourceManager.get_shader("particle").use()
        ResourceManager.get_shader("particle").set_int("sprite", 0)
        ResourceManager.get_shader("particle").set_mat4("projection", projection)

        # load textures
        ResourceManager.load_texture("textures/background.jpg", False, "background")
        ResourceManager.load_texture("textures/awesomeface.png", True, "face")
        ResourceManager.load_texture("textures/block.png", False, "block")
        ResourceManager.load_texture("textures/block_solid.png", False, "block_solid")
        ResourceManager.load_texture("textures/paddle.png", True, "paddle")
        ResourceManager.load_texture("textures/particle.png", True, "particle")

        # set render-specific controls
        self.renderer = SpriteRenderer(ResourceManager.get_shader("sprite"))
        self.particles = ParticleGenerator(
            ResourceManager.get_shader("particle"),
            ResourceManager.get_texture("particle"),
            500
        )
        self.effects = PostProcessor(ResourceManager.get_shader("postprocessing"), self.width, self.height)

        # load levels
        self.levels.append(GameLevel("levels/1.lvl", self.width, self.height / 2))
        self.levels.append(GameLevel("levels/2.lvl", self.width, self.height / 2))
        self.levels.append(GameLevel("levels/3.lvl", self.width, self.height / 2))
        self.levels.append(GameLevel("levels/4.lvl", self.width, self.height / 2))
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

        # update particles
        self.particles.update(dt, self.ball, 2, glm.vec2(self.ball.radius / 2.0))

        # reduce shake time
        if self.shake_time > 0.0:
            self.shake_time -= dt
            if self.shake_time <= 0.0:
                self.effects.shake = False

        # check loss condition
        if self.ball.position.y >= self.height:  # did ball reach bottom edge ?
            self.reset_level()
            self.reset_player()

    def render(self):
        # begin rendering to postprocessing framebuffer
        self.effects.begin_render()

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

        # draw particles
        self.particles.draw()

        # draw ball
        self.ball.draw(self.renderer)

        # end rendering to postprocessing framebuffer
        self.effects.end_render()

        # render postprocessing quad
        self.effects.render(glfwGetTime())
    
    def do_collisions(self):
        for box in self.levels[self.level].bricks:
            if not box.destroyed:
                collision = check_ball_collision(self.ball, box)
                if collision.is_collided:
                    # destroy block if not solid
                    if not box.is_solid:
                        box.destroyed = True
                    else:  # if block is solid, enable shake effect
                        self.shake_time = 0.05
                        self.effects.shake = True

                    # collision resolution
                    direction = collision.direction
                    diff_vector = collision.difference
                    if direction == Direction.LEFT or direction == Direction.RIGHT:  # horizontal collision
                        self.ball.velocity.x = -self.ball.velocity.x  # reverse horizontal velocity

                        # relocate
                        penetration = self.ball.radius - abs(diff_vector.x)
                        if direction == Direction.LEFT:
                            self.ball.position.x += penetration  # move ball to right
                        else:
                            self.ball.position.x -= penetration  # move ball to left
                    else:  # vertical collision
                        self.ball.velocity.y = -self.ball.velocity.y  # reverse vertical velocity

                        # relocate
                        penetration = self.ball.radius - abs(diff_vector.y)
                        if direction == Direction.UP:
                            self.ball.position.y -= penetration  # move ball back up
                        else:
                            self.ball.position.y += penetration  # move ball back down

        # check collisions for player pad (unless stuck)
        result = check_ball_collision(self.ball, self.player)
        if not self.ball.stuck and result.is_collided:
            # check where it hit the board, and change velocity based on where it hit the board
            center_board = self.player.position.x + self.player.size.x / 2.0
            distance = (self.player.position.x + self.ball.radius) - center_board
            percentage = distance / (self.player.size.x / 2.0)

            # then move accordingly
            strength = 2.0
            old_velocity = self.ball.velocity
            self.ball.velocity.x = INITIAL_BALL_VELOCITY.x * percentage * strength
            self.ball.velocity.y = -1.0 * abs(self.ball.velocity.y)
            self.ball.velocity = glm.normalize(self.ball.velocity) * glm.length(old_velocity)

    # reset
    def reset_level(self) -> None:
        self.levels[self.level].load(f"levels/{self.level + 1}.lvl", self.width, self.height / 2)

    def reset_player(self) -> None:
        # reset player stats
        self.player.size = PLAYER_SIZE
        self.player.position = glm.vec2(
            self.width / 2.0 - PLAYER_SIZE.x / 2.0,
            self.height - PLAYER_SIZE.y
        )

        # reset ball stats
        self.ball.reset(
            self.player.position + glm.vec2(PLAYER_SIZE.x / 2.0 - BALL_RADIUS, -(BALL_RADIUS * 2.0)),
            INITIAL_BALL_VELOCITY
        )        
