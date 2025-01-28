import glm
import random
from glfw.GLFW import *
from enum import StrEnum
from typing import Optional
from breakout.sprite_renderer import SpriteRenderer
from breakout.resource_manager import ResourceManager
from breakout.game_object import GameObject
from breakout.game_level import GameLevel
from breakout.ball_object import BallObject
from breakout.collision import check_ball_collision, Direction, check_collision
from breakout.particle import ParticleGenerator
from breakout.post_processor import PostProcessor
from breakout.power_up import PowerUp
from breakout.text_renderer import TextRenderer

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
        self.state = GameState.GAME_MENU
        self.keys = [False for _ in range(1024)]
        self.keys_processed = [False for _ in range(1024)]
        self.keys_processed = [False for _ in range(1024)]
        self.width = width
        self.height = height

        self.renderer: Optional[SpriteRenderer] = None

        self.levels: list[GameLevel] = []
        self.level: int = 0

        self.lives = 3

        self.player: Optional[GameObject] = None
        self.ball: Optional[BallObject] = None
        self.particles: Optional[ParticleGenerator] = None
        self.effects: Optional[PostProcessor] = None
        self.powerups: list[PowerUp] = []
        self.text: Optional[TextRenderer] = None

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
        ResourceManager.load_texture("textures/powerup_speed.png", True, "powerup_speed")
        ResourceManager.load_texture("textures/powerup_sticky.png", True, "powerup_sticky")
        ResourceManager.load_texture("textures/powerup_increase.png", True, "powerup_increase")
        ResourceManager.load_texture("textures/powerup_confuse.png", True, "powerup_confuse")
        ResourceManager.load_texture("textures/powerup_chaos.png", True, "powerup_chaos")
        ResourceManager.load_texture("textures/powerup_passthrough.png", True, "powerup_passthrough")

        # set render-specific controls
        self.renderer = SpriteRenderer(ResourceManager.get_shader("sprite"))
        self.particles = ParticleGenerator(
            ResourceManager.get_shader("particle"),
            ResourceManager.get_texture("particle"),
            500
        )
        self.effects = PostProcessor(ResourceManager.get_shader("postprocessing"), self.width, self.height)
        self.text = TextRenderer(self.width, self.height)
        self.text.load("fonts/ocraext.ttf", 24)

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
            texture=ResourceManager.get_texture("paddle")
        )

        ball_pos = player_pos + glm.vec2(
            PLAYER_SIZE.x / 2.0 - BALL_RADIUS, -BALL_RADIUS * 2.0
        )
        self.ball = BallObject(ball_pos, BALL_RADIUS, INITIAL_BALL_VELOCITY, ResourceManager.get_texture("face"))

        # audio
        ResourceManager.load_music("audio/breakout.mp3", "game_music")
        ResourceManager.load_music("audio/bleep.mp3", "bleep1")  # the sound for when the ball hit a non-solid block. 
        ResourceManager.load_music("audio/solid.wav", "solid")  # the sound for when the ball hit a solid block. 
        ResourceManager.load_music("audio/powerup.wav", "powerup")  # the sound for when we the player paddle collided with a powerup block. 
        ResourceManager.load_music("audio/bleep.wav", "bleep2")  # the sound for when we the ball bounces of the player paddle.

        ResourceManager.play_music("game_music")

    def process_input(self, dt: float):
        if self.state == GameState.GAME_MENU:
            if self.keys[GLFW_KEY_ENTER] and not self.keys_processed[GLFW_KEY_ENTER]:
                self.state = GameState.GAME_ACTIVE
                self.keys_processed[GLFW_KEY_ENTER] = True
            if self.keys[GLFW_KEY_W] and not self.keys_processed[GLFW_KEY_W]:
                self.level = (self.level + 1) % 4
                self.keys_processed[GLFW_KEY_W] = True
            if self.keys[GLFW_KEY_S] and not self.keys_processed[GLFW_KEY_S]:
                if self.level > 0:
                    self.level -= 1
                else:
                    self.level = 3
                self.keys_processed[GLFW_KEY_S] = True

        if self.state == GameState.GAME_WIN:
            if self.keys[GLFW_KEY_ENTER]:
                self.keys_processed[GLFW_KEY_ENTER] = True
                self.effects.chaos = False
                self.state = GameState.GAME_MENU

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

        # update powerups
        self.update_power_ups(dt)

        # reduce shake time
        if self.shake_time > 0.0:
            self.shake_time -= dt
            if self.shake_time <= 0.0:
                self.effects.shake = False

        # check loss condition
        if self.ball.position.y >= self.height:  # did ball reach bottom edge ?
            self.lives -= 1
            # did the player lose all hist lives ? : game over
            if self.lives == 0:
                self.reset_level()
                self.state = GameState.GAME_MENU
            self.reset_player()

        # check win condition
        if self.state == GameState.GAME_ACTIVE and self.levels[self.level].is_completed():
            self.reset_level()
            self.reset_player()
            self.effects.chaos = True
            self.state = GameState.GAME_WIN

    def render(self):
        if (
            self.state == GameState.GAME_ACTIVE or 
            self.state == GameState.GAME_MENU or
            self.state == GameState.GAME_WIN
        ):
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

            # draw powerups
            for powerup in self.powerups:
                if not powerup.destroyed:
                    powerup.draw(self.renderer)

            # draw particles
            self.particles.draw()

            # draw ball
            self.ball.draw(self.renderer)

            # end rendering to postprocessing framebuffer
            self.effects.end_render()

            # render postprocessing quad
            self.effects.render(glfwGetTime())

            # render text (don't include postprocessing)
            self.text.render_text(f"Lives: {self.lives}", 5.0, 5.0, 1.0)

        if self.state == GameState.GAME_MENU:
            self.text.render_text("Press ENTER to start", 250.0, self.height / 2.0, 1.0)
            self.text.render_text("Press W or S to select level", 245.0, self.height / 2.0 + 20.0, 0.75)

        if self.state == GameState.GAME_WIN:
            self.text.render_text("You WON!!!", 320.0, self.height / 2.0 - 20.0, 1.0, glm.vec3(0.0, 1.0, 0.0))
            self.text.render_text("Press ENTER to retry or ESC to quit", 130.0, self.height / 2.0, 1.0, glm.vec3(1.0, 1.0, 0.0))

    def do_collisions(self):
        for box in self.levels[self.level].bricks:
            if not box.destroyed:
                collision = check_ball_collision(self.ball, box)
                if collision.is_collided:
                    # destroy block if not solid
                    if not box.is_solid:
                        box.destroyed = True
                        self.spawn_power_ups(box)
                        ResourceManager.play_music("bleep1")
                    else:  # if block is solid, enable shake effect
                        self.shake_time = 0.05
                        self.effects.shake = True
                        ResourceManager.play_music("solid")

                    # collision resolution
                    direction = collision.direction
                    diff_vector = collision.difference
                    if not (self.ball.pass_through and not box.is_solid):
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

        # also check collisions on PowerUps and if so, activate them
        for powerup in self.powerups:
            if not powerup.destroyed:
                # first check if powerup passed bottom edge, if so: keep as inactive and destroy
                if powerup.position.y >= self.height:
                    powerup.destroyed = True

                if check_collision(self.player, powerup):
                    # collided with player, now activate powerup
                    self.activate_power_up(powerup)
                    powerup.destroyed = True
                    powerup.activated = True
                    ResourceManager.play_music("powerup")

        # and finally check collisions for player pad (unless stuck)
        result = check_ball_collision(self.ball, self.player)
        if not self.ball.stuck and result.is_collided and result.direction == Direction.UP:
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

            # if Sticky powerup is activated, also stick ball to paddle once new velocity vectors were calculated
            self.ball.stuck = self.ball.sticky

            ResourceManager.play_music("bleep2")

    # reset
    def reset_level(self) -> None:
        self.levels[self.level].load(f"levels/{self.level + 1}.lvl", self.width, self.height / 2)
        self.lives = 3

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

    def should_spawn(self, chance: int) -> bool:
        rdn = random.randint(0, chance - 1)
        return rdn == 0

    # powerups
    def spawn_power_ups(self, block: GameObject) -> None:
        if self.should_spawn(75):  # 1 in 75 chance
            self.powerups.append(PowerUp(
                type="speed",
                color=glm.vec3(0.5, 0.5, 1.0),
                duration=5,
                position=block.position,
                texture=ResourceManager.get_texture("powerup_speed")
            ))
        if self.should_spawn(75):
            self.powerups.append(PowerUp(
                type="sticky",
                color=glm.vec3(1.0, 0.5, 1.0),
                duration=20.0,
                position=block.position,
                texture=ResourceManager.get_texture("powerup_sticky")
            ))
        if self.should_spawn(75):
            self.powerups.append(PowerUp(
                type="pass-through",
                color=glm.vec3(0.5, 1.0, 0/5),
                duration=10.0,
                position=block.position,
                texture=ResourceManager.get_texture("powerup_passthrough")
            ))
        if self.should_spawn(75):
            self.powerups.append(PowerUp(
                type="pad-size-increase",
                color=glm.vec3(1.0, 0.3, 0.3),
                duration=0.0,
                position=block.position,
                texture=ResourceManager.get_texture("powerup_increase")
            ))
        # Negative powerups should spawn more often
        if self.should_spawn(15):
            self.powerups.append(PowerUp(
                type="confuse",
                color=glm.vec3(1.0, 0.3, 0.3),
                duration=15.0,
                position=block.position,
                texture=ResourceManager.get_texture("powerup_confuse")
            ))
        if self.should_spawn(15):
            self.powerups.append(PowerUp(
                type="chaos",
                color=glm.vec3(0.9, 0.25, 0.25),
                duration=15.0,
                position=block.position,
                texture=ResourceManager.get_texture("powerup_chaos")
            ))

    def update_power_ups(self, dt: float) -> None:
        for powerup in self.powerups:
            powerup.position += powerup.velocity * dt
            if powerup.activated:
                powerup.duration -= dt

                if powerup.duration <= 0.0:
                    # remove powerup from list (will later be removed)
                    powerup.activated = False

                    # deactive effects
                    if (
                        powerup.type == "sticky" and 
                        not self.is_other_powerup_active("sticky")
                    ):
                        self.ball.sticky = False
                        self.player.color = glm.vec3(1.0)
                    elif (
                        powerup.type == "speed" and
                        not self.is_other_powerup_active("speed")
                    ):
                        self.ball.velocity /= 1.2  
                    elif (
                        powerup.type == "pass-through" and
                        not self.is_other_powerup_active("path-through")
                    ):
                        self.ball.pass_through = False
                        self.ball.color = glm.vec3(1.0)
                    elif (
                        powerup.type == "confuse" and
                        not self.is_other_powerup_active("confuse")
                    ):
                        self.effects.confuse = False
                    elif (
                        powerup.type == "chaos" and
                        not self.is_other_powerup_active("chaos")
                    ):
                        self.effects.chaos = False

        # Remove all PowerUps from vector that are destroyed AND !activated (thus either off the map or finished)
        self.powerups = [
            powerup for powerup in self.powerups
            if not (powerup.destroyed and not powerup.activated)
        ]

    def activate_power_up(self, powerup: PowerUp) -> None:
        if powerup.type == "speed":
            self.ball.velocity *= 1.2
        elif powerup.type == "sticky":
            self.ball.sticky = True
            self.player.color = glm.vec3(1.0, 0.5, 1.0)
        elif powerup.type == "pass-through":
            self.ball.pass_through = True
            self.ball.color = glm.vec3(1.0, 0.5, 0.5)
        elif powerup.type == "pad-size-increase":
            self.player.size.x += 50
        elif powerup.type == "confuse":
            if not self.effects.chaos:
                # only activate if chaos wasn't already active
                self.effects.confuse = True
        elif powerup.type == "chaos":
            if not self.effects.confuse:
                self.effects.chaos = True

    def is_other_powerup_active(self, type: str) -> bool:
        # check if another PowerUp of the same type is still active
        # in which case we don't disable its effect (yet)
        for powerup in self.powerups:
            if powerup.activated and powerup.type == type:
                return True 
        return False
