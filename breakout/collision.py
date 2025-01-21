import glm
from enum import Enum
from typing import Tuple
from breakout.game_object import GameObject
from breakout.ball_object import BallObject


# represents the four possible (collision) directions
class Direction(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3


# Defines a Collision type that represents collision data
# bool: collision ?
# Direction: what direction ?
# glm.vec2: difference vector center - closest point
# Collision = Tuple[bool, Direction, glm.vec2]

class Collision:
    def __init__(self, is_collided: bool, direction: Direction, difference: glm.vec2):
        self.is_collided = is_collided
        self.direction = direction
        self.difference = difference


def vector_direction(target: glm.vec2) -> Direction:
    compass = [
        glm.vec2( 0.0,  1.0),  # up
        glm.vec2( 1.0,  0.0),  # right
        glm.vec2( 0.0, -1.0),  # down
        glm.vec2(-1.0,  0.0)   # left
    ]

    fmax = 0.0
    best_match = -1
    for i in range(4):
        dot_product = glm.dot(glm.normalize(target), compass[i])
        if dot_product > fmax:
            fmax = dot_product
            best_match = i

    if best_match == -1:
        return Direction.UP

    return Direction(best_match)


def check_ball_collision(one: BallObject, two: GameObject) -> Collision:
    # get center point circle first
    center = glm.vec2(one.position + one.radius)

    # calculate AABB info (center, half-extents)
    aabb_half_extents = glm.vec2(two.size.x / 2.0, two.size.y / 2.0)
    aabb_center = glm.vec2(
        two.position.x + aabb_half_extents.x,
        two.position.y + aabb_half_extents.y
    )

    # get difference vector between both centers
    difference = center - aabb_center
    clamped = glm.clamp(difference, -aabb_half_extents, aabb_half_extents)

    # add clamped value to AABB_center and we get the value
    # of box closest to circle
    closest = aabb_center + clamped

    # retrieve vector between center circle and closest
    # point AABB and check if length <= radius
    difference = closest - center

    if glm.length(difference) < one.radius:
        # not <= since in that case a collision also occurs when object 
        # one exactly touches object two, which they are at the end of 
        # each collision resolution stage.
        return Collision(True, vector_direction(difference), difference)
    else:
        return Collision(False, Direction.UP, glm.vec2(0.0, 0.0))


# AABB - AABB collision
def check_collision(one: GameObject, two: GameObject) -> bool:
    collisionX = (
        one.position.x + one.size.x >= two.position.x and 
        two.position.x + two.size.x >= one.position.x
    )
    collisionY = (
        two.position.y + one.size.y >= two.position.y and
        two.position.y + two.size.y >= one.position.y
    )
    return collisionX and collisionY