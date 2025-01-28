from OpenGL.GL import *


class Texture2D:
    def __init__(
        self,
        width: int = 0,
        height: int = 0,
        internal_format: int = GL_RGB,
        image_format: int = GL_RGB,
        wrap_s: int = GL_REPEAT,
        wrap_t: int = GL_REPEAT,
        filter_min: int = GL_LINEAR,
        filter_max: int = GL_LINEAR
    ):
        # holds the ID of the texture object, used for all texture operations to reference to this particular texture
        self.id = glGenTextures(1)

        # texture image dimensions
        self.width = width
        self.height = height

        # texture format
        self.internal_format = internal_format  # format of texture object
        self.image_format = image_format  # format of loaded image

        # texture configuration
        self.wrap_s = wrap_s  # wrapping mode on S axis
        self.wrap_t = wrap_t  # wrapping mode on T axis
        self.filter_min = filter_min  # filtering mode if texture pixels < screen pixels
        self.filter_max = filter_max  # filtering mode if texture pixels > screen pixels

    def generate(self, data):        
        # bind texture
        glBindTexture(GL_TEXTURE_2D, self.id)
        glTexImage2D(GL_TEXTURE_2D, 0, self.internal_format, self.width, self.height, 0, self.image_format, GL_UNSIGNED_BYTE, data)

        # set texture wrap and filter modes
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, self.wrap_s)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, self.wrap_t)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, self.filter_min)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, self.filter_max)

        # unbind texture
        glBindTexture(GL_TEXTURE_2D, 0)

    def bind(self):
        glBindTexture(GL_TEXTURE_2D, self.id)
