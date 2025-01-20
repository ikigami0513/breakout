from OpenGL.GL import *
from breakout.shader import Shader
from breakout.texture2d import Texture2D
import glm
import numpy as np

class SpriteRenderer:
    def __init__(self, shader: Shader) -> None:
        self.shader = shader
        self.quad_vao = None
        self.init_render_data()

    def draw_sprite(
        self,
        texture: Texture2D,
        position: glm.vec2,
        size: glm.vec2 = glm.vec2(10.0, 10.0),
        rotate: float = 0.0,
        color: glm.vec3 = glm.vec3(1.0)
    ) -> None:
        # prepare transformations
        self.shader.use()

        model = glm.mat4(1.0)
        model = glm.translate(model, glm.vec3(position, 0.0))

        model = glm.translate(model, glm.vec3(0.5 * size.x, 0.5 * size.y, 0.0))
        model = glm.rotate(model, glm.radians(rotate), glm.vec3(0.0, 0.0, 1.0))
        model = glm.translate(model, glm.vec3(-0.5 * size.x, -0.5 * size.y, 0.0))

        model = glm.scale(model, glm.vec3(size, 1.0))

        self.shader.set_mat4("model", model)
        self.shader.set_vec3("spriteColor", color)

        glActiveTexture(GL_TEXTURE0)
        texture.bind()

        glBindVertexArray(self.quad_vao)
        glDrawArrays(GL_TRIANGLES, 0, 6)
        glBindVertexArray(0)

    def init_render_data(self) -> None:
        vertices = np.array([
            # pos    # tex
            0.0, 1.0, 0.0, 1.0,
            1.0, 0.0, 1.0, 0.0,
            0.0, 0.0, 0.0, 0.0,
            
            0.0, 1.0, 0.0, 1.0,
            1.0, 1.0, 1.0, 1.0,
            1.0, 0.0, 1.0, 0.0
        ], dtype=np.float32)

        self.quad_vao = glGenVertexArrays(1)
        vbo = glGenBuffers(1)

        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        glBindVertexArray(self.quad_vao)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 4, GL_FLOAT, GL_FALSE, 4 * vertices.itemsize, None)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)
