import numpy as np
from OpenGL.GL import *
from pygame import mixer
from PIL import Image
from breakout.texture2d import Texture2D
from breakout.shader import Shader
from typing import Optional

class ResourceManager:
    # resource storage
    shaders: dict[str, Shader] = {}
    textures: dict[str, Texture2D] = {}
    audios: dict[str, mixer.Sound] = {}

    # loads (and generates) a shader program from file loading 
    # vertex, fragment (and geometry) shader's source code.
    # If gShaderFile is not nullptr, it also loads a 
    # geometry shader
    @staticmethod
    def load_shader(name: str, v_shader_file: str, f_shader_file: str, g_shader_file: Optional[str] = None) -> Shader:
        ResourceManager.shaders[name] = ResourceManager.load_shader_from_file(v_shader_file, f_shader_file, g_shader_file)
        return ResourceManager.shaders[name]

    # retrieves a stored shader
    @staticmethod
    def get_shader(name: str) -> Optional[Shader]:
        return ResourceManager.shaders.get(name)

    # loads (and generates) a texture from file
    @staticmethod
    def load_texture(file: str, alpha: bool, name: str) -> Texture2D:
        ResourceManager.textures[name] = ResourceManager.load_texture_from_file(file, alpha)
        return ResourceManager.textures[name]

    # retrieves a stored texture
    @staticmethod
    def get_texture(name: str) -> Optional[Texture2D]:
        return ResourceManager.textures.get(name)
    
    # loads an audio from file
    def load_music(file: str, name: str) -> mixer.Sound:
        ResourceManager.audios[name] = mixer.Sound(file)
        return ResourceManager.audios[name]
    
    # play a stored music
    @staticmethod
    def play_music(name: str) -> None:
        audio = ResourceManager.audios.get(name)
        if audio:
            audio.play()

    # properly de-allocates all loaded resources
    @staticmethod
    def clear() -> None:
        # properly delete all shaders
        for shader in ResourceManager.shaders.values():
            glDeleteProgram(shader.id)

        # properly delete all textures
        for texture in ResourceManager.textures.values():
            texture_id = np.array([texture.id], dtype=np.uint32)
            glDeleteTextures(1, texture_id)

    # loads and generates a shader from file
    @staticmethod
    def load_shader_from_file(v_shader_file: str, f_shader_file: str, g_shader_file: Optional[str] = None) -> Shader:
        shader = Shader(v_shader_file, f_shader_file, g_shader_file)
        return shader

    # loads a single texture from file
    @staticmethod
    def load_texture_from_file(file: str, alpha: bool) -> Texture2D:
        # create texture object
        texture = Texture2D()
        if alpha:
            texture.internal_format = GL_RGBA
            texture.image_format = GL_RGBA
        else:
            texture.internal_format = GL_RGB
            texture.image_format = GL_RGB

        # load image
        try:
            image = Image.open(file)
            if alpha:
                image = image.convert("RGBA")
            else:
                image = image.convert("RGB")
            image_data = np.array(image, dtype=np.uint8)
        except Exception as e:
            print(f"ERROR::TEXTURE: Failed to load texture file {file}\n{e}")
            return None
        
        # now generate texture
        texture.width = image.width
        texture.height = image.height
        texture.generate(image_data)

        return texture
    