import glm
import numpy as np
import random
from OpenGL.GL import *
from breakout.shader import Shader
from breakout.texture2d import Texture2D
from breakout.game_object import GameObject


# Represents a single particle and its state
class Particle:
    def __init__(
        self,
        position: glm.vec2 = glm.vec2(0.0),
        velocity: glm.vec2 = glm.vec2(0.0),
        color: glm.vec4 = glm.vec4(1.0),
        life: float = 0.0
    ):
        self.position = position
        self.velocity = velocity
        self.color = color
        self.life = life


# ParticleGenerator acts as a container for rendering a large number of
# particles by repeatedly spawing and updating particles and killing
# them after a given amount of time.
class ParticleGenerator:
    def __init__(self, shader: Shader, texture: Texture2D, amount: int):
        self.shader = shader
        self.texture = texture
        self.amount = amount

        self.particles: list[Particle] = []

        # stores the index of the last particle used
        # (for quick access to next dead particle)
        self.last_used_particle = 0

        # initializes buffer and vertex attributes

        # set up mesh and attribute properties
        particle_quad = np.array([
            0.0, 1.0, 0.0, 1.0,
            1.0, 0.0, 1.0, 0.0,
            0.0, 0.0, 0.0, 0.0,

            0.0, 1.0, 0.0, 1.0,
            1.0, 1.0, 1.0, 1.0,
            1.0, 0.0, 1.0, 0.0
        ], dtype=np.float32)
        self.vao = glGenVertexArrays(1)
        vbo = glGenBuffers(1)
        glBindVertexArray(self.vao)

        # fill mesh buffer
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, particle_quad.nbytes, particle_quad, GL_STATIC_DRAW)

        # set mesh attributes
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 4, GL_FLOAT, GL_FALSE, 4 * glm.sizeof(glm.float32), ctypes.c_void_p(0))
        glBindVertexArray(0)

        # create self.amount default particle instances
        for i in range(self.amount):
            self.particles.append(Particle())

    # update all particles
    def update(self, dt: float, go: GameObject, new_particles: int, offset: glm.vec2 = glm.vec2(0.0, 0.0)) -> None:
        # add new particles
        for i in range(new_particles):
            unused_particle = self.first_unused_particle()
            self.respawn_particle(self.particles[unused_particle], go, offset)

        # update all particles
        for p in self.particles:
            p.life -= dt  # reduce life
            if p.life > 0.0:
                # particle is alive, thus update
                p.position -= p.velocity * dt
                p.color.w -= dt * 2.5

    # render all particles
    def draw(self) -> None:
        # use additive blending to give it a 'glow' effect
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        self.shader.use()

        for particle in self.particles:
            if particle.life > 0.0:
                self.shader.set_vec2("offset", particle.position)
                self.shader.set_vec4("color", particle.color)
                self.texture.bind()
                glBindVertexArray(self.vao)
                glDrawArrays(GL_TRIANGLES, 0, 6)
                glBindVertexArray(0)

        # don't forget to reset to default blending mode
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # returns the first Particle index that's currently unused e.g. 
    # Life <= 0.0f or 0 if no particle is currently inactive
    def first_unused_particle(self) -> int:
        # first search from last used particle, this will usually return almost instantly
        for i in range(self.last_used_particle, self.amount):
            if self.particles[i].life <= 0.0:
                self.last_used_particle = i
                return i
            
        # otherwise, do a linear search
        for i in range(self.last_used_particle):
            if self.particles[i].life <= 0.0:
                self.last_used_particle = i
                return i
            
        # all particles are taken, override the first one (note that if it
        # repeatedly hits this case, more particles should be reserved)
        self.last_used_particle = 0
        return 0

    def respawn_particle(self, particle: Particle, go: GameObject, offset: glm.vec2 = glm.vec2(0.0, 0.0)) -> None:
        rnd = (random.randint(0, 99) - 50) / 10.0
        r_color = 0.5 + (random.randint(0, 99) / 100.0)
        particle.position = go.position + rnd + offset
        particle.color = glm.vec4(r_color, r_color, r_color, 1.0)
        particle.life = 1.0
        particle.velocity = go.velocity * 0.1
