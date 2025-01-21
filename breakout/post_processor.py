import glm
import numpy as np
from OpenGL.GL import *
from breakout.texture2d import Texture2D
from breakout.sprite_renderer import SpriteRenderer
from breakout.shader import Shader
from typing import Optional

class PostProcessor:
    def __init__(
        self,
        shader: Shader,
        width: int,
        height: int,
        texture: Optional[Texture2D] = None,
        confuse: bool = False,
        chaos: bool = False,
        shake: bool = False
    ):
        self.post_processing_shader = shader
        self.width = width
        self.height = height
        if texture is None:
            self.texture = Texture2D(width, height)
        else:
            self.texture = texture
        self.confuse = confuse
        self.chaos = chaos
        self.shake = shake

        # initialize renderbuffer / framebuffer object
        self.msfbo = glGenFramebuffers(1)
        self.fbo = glGenFramebuffers(1)
        self.rbo = glGenRenderbuffers(1)

        # initialize renderbuffer storage with a multisampled color buffer (don't need a depth/stencil buffer)
        glBindFramebuffer(GL_FRAMEBUFFER, self.msfbo)
        glBindRenderbuffer(GL_RENDERBUFFER, self.rbo)
        glRenderbufferStorageMultisample(GL_RENDERBUFFER, 4, GL_RGB, width, height)  # allocate storage for render buffer object
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_RENDERBUFFER, self.rbo)  # attach MS render buffer object to framebuffer
        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            print("ERROR::POSTPROCESSOR: Failed to initialize MSFBO")

        # also initialize the FBO/texture to blit multisampled color-buffer;
        # used for shader operations (for postprocessing effects)
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
        self.texture.generate(None)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.texture.id, 0)  # attach texture to framebuffer as its color attachment
        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            print("ERROR::POSTPROCESSOR: Failed to initialize FBO")
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        # initialize render data and uniforms
        self.init_render_data()
        self.post_processing_shader.use()
        self.post_processing_shader.set_int("scene", 0)

        offset = 1.0 / 300.0
        offsets = np.array([
                [-offset,  offset],  # top-left
                [ 0.0,     offset],  # top-center
                [ offset,  offset],  # top-right
                [-offset,  0.0   ],  # center-left
                [ 0.0,     0.0   ],  # center-center
                [ offset,  0.0   ],  # center-right
                [-offset, -offset],  # bottom-left
                [ 0.0,    -offset],  # bottom-center
                [ offset, -offset]   # bottom-right
        ], dtype=np.float32)
        glUniform2fv(glGetUniformLocation(self.post_processing_shader.id, "offsets"), len(offsets), offsets)
        
        edge_kernel = np.array([
            -1, -1, -1,
            -1,  8, -1,
            -1, -1, -1
        ], dtype=np.int32)
        glUniform1iv(glGetUniformLocation(self.post_processing_shader.id, "edge_kernel"), len(edge_kernel), edge_kernel)

        blur_kernel = np.array([
            1.0 / 16.0, 2.0 / 16.0, 1.0 / 16.0,
            2.0 / 16.0, 4.0 / 16.0, 2.0 / 16.0,
            1.0 / 16.0, 2.0 / 16.0, 1.0 / 16.0
        ], dtype=np.float32)
        glUniform1fv(glGetUniformLocation(self.post_processing_shader.id, "blur_kernel"), len(blur_kernel), blur_kernel)

    # prepares the postprocessor's framebuffer operations before rendering the game
    def begin_render(self) -> None:
        glBindFramebuffer(GL_FRAMEBUFFER, self.msfbo)
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

    # should be called after rendering the game, so it stores all the rendered data into a texture object
    def end_render(self) -> None:
        # now resolve multisampled color-buffer into intermediate fbo
        # to store to texture
        glBindFramebuffer(GL_READ_FRAMEBUFFER, self.msfbo)
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, self.fbo)
        glBlitFramebuffer(0, 0, self.width, self.height, 0, 0, self.width, self.height, GL_COLOR_BUFFER_BIT, GL_NEAREST)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)  # binds both READ and WRITE framebuffer to default framebuffer

    # renders the PostProcesor texture quad (as a screen-encompassing large sprite)
    def render(self, time: float) -> None:
        # set uniforms/options
        self.post_processing_shader.use()
        self.post_processing_shader.set_float("time", time)
        self.post_processing_shader.set_bool("confuse", self.confuse)
        self.post_processing_shader.set_bool("chaos", self.chaos)
        self.post_processing_shader.set_bool("shake", self.shake)

        # render textured quad
        glActiveTexture(GL_TEXTURE0)
        self.texture.bind()
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, 6)
        glBindVertexArray(0)

    # initialize quad for rendering postprocessing texture
    def init_render_data(self) -> None:
        # configure vao / vbo
        vertices = np.array([
            # pos       # tex
            -1.0, -1.0, 0.0, 0.0,
             1.0,  1.0, 1.0, 1.0,
            -1.0,  1.0, 0.0, 1.0,

            -1.0, -1.0, 0.0, 0.0,
             1.0, -1.0, 1.0, 0.0,
             1.0,  1.0, 1.0, 1.0
        ], dtype=np.float32)
        self.vao = glGenVertexArrays(1)
        vbo = glGenBuffers(1)

        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        glBindVertexArray(self.vao)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 4, GL_FLOAT, GL_FALSE, 4 * glm.sizeof(glm.float32), ctypes.c_void_p(0))
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)
