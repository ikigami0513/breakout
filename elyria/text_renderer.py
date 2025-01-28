import os
import glm
import freetype
import numpy as np
from OpenGL.GL import *
from elyria import base_dir
from elyria.resource_manager import ResourceManager
from elyria.texture2d import Texture2D
from elyria.shader import Shader


# Holds all state information relevant to a character as loaded using FreeType
class Character:
    def __init__(
        self,
        texture_id: int,
        size: glm.ivec2,
        bearing: glm.ivec2,
        advance: int
    ):
        # ID handle of the glyph texture
        self.texture_id = texture_id
        # size of glyph
        self.size = size
        # offset from baseline to left/top of glyph
        self.bearing = bearing
        # horizontal offset to advance to next glyph
        self.advance = advance


# A renderer class for rendering text displayed by a font loaded using the
# FreeType library. A single font is loaded, processed into a list of Character
# items for later rendering
class TextRenderer:
    def __init__(self, width: int, height: int):
        # holds a list of pre-compiled Characters
        self.characters: dict[str, Character] = {}
        # load and configure shader
        self.text_shader = ResourceManager.load_shader(
            "text",
            os.path.join(base_dir, "shaders", "text_2d.vs"),
            os.path.join(base_dir, "shaders", "text_2d.fs")
        )
        self.text_shader.use()
        projection = glm.ortho(0.0, float(width), float(height), 0.0)
        self.text_shader.set_mat4("projection", projection)
        self.text_shader.set_int("text", 0)

        # configure vao / vbo for texture quads
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, 6 * 6 * 4, None, GL_DYNAMIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 4, GL_FLOAT, GL_FALSE, 4 * 4, None)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    # pre-compiles a list of characters from the given font
    def load(self, font: str, font_size: int) -> None:
        # first clear the previously loaded Characters
        self.characters.clear()

        # load font as face
        face: freetype.Face = freetype.Face(font)

        # set size to load glyphs as
        face.set_pixel_sizes(font_size, font_size)

        # disable byte-alignment restriction
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

        # Then for the first 128 ASCII characters, pre-load / compile their characters and store them
        for c in range(128):
            # load character glyph
            if face.load_char(c, freetype.FT_LOAD_RENDER):
                print(f"ERROR::FREETYPE: Failed to load {c} Glyph")
                continue

            # generate texture
            texture = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture)
            glTexImage2D(
                GL_TEXTURE_2D,
                0,
                GL_RED,
                face.glyph.bitmap.width,
                face.glyph.bitmap.rows,
                0,
                GL_RED,
                GL_UNSIGNED_BYTE,
                face.glyph.bitmap.buffer
            )

            # set texture options
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

            # now store character for later use
            self.characters[chr(c)] = Character(
                texture_id=texture,
                size=glm.ivec2(face.glyph.bitmap.width, face.glyph.bitmap.rows),
                bearing=glm.ivec2(face.glyph.bitmap_left, face.glyph.bitmap_top),
                advance=face.glyph.advance.x
            )
        
        glBindTexture(GL_TEXTURE_2D, 0)

    # renders a string of text using the precompiled list of characters
    def render_text(self, text: str, x: float, y: float, scale: float, color: glm.vec3 = glm.vec3(1.0)):
        # activate corresponding render state
        self.text_shader.use()
        self.text_shader.set_vec3("text_color", color)
        glActiveTexture(GL_TEXTURE0)
        glBindVertexArray(self.vao)

        # iterate through all characters
        for c in text:
            ch = self.characters[c]

            xpos = x + ch.bearing.x * scale
            ypos = y + (self.characters['H'].bearing.y - ch.bearing.y) * scale

            w = ch.size.x * scale
            h = ch.size.y * scale

            # update VBO for each character
            vertices = np.array([
                [xpos,     ypos + h,   0.0, 1.0],
                [xpos + w, ypos,       1.0, 0.0],
                [xpos,     ypos,       0.0, 0.0],

                [xpos,     ypos + h,   0.0, 1.0],
                [xpos + w, ypos + h,   1.0, 1.0],
                [xpos + w, ypos,       1.0, 0.0]
            ], dtype=np.float32)

            # render glyph texture over quad
            glBindTexture(GL_TEXTURE_2D, ch.texture_id)

            # update content of vbo memory
            glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
            glBufferSubData(GL_ARRAY_BUFFER, 0, vertices.nbytes, vertices)
            glBindBuffer(GL_ARRAY_BUFFER, 0)

            # render quad
            glDrawArrays(GL_TRIANGLES, 0, 6)

            # now advance cursor for next glyph
            x += (ch.advance >> 6) * scale  # bitshift by 6 to get value in pixels (1/64th times 2^6 = 64)
        
        glBindVertexArray(0)
        glBindTexture(GL_TEXTURE_2D, 0)
        