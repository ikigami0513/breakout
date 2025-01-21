import numpy as np
import glm
from breakout.game_object import GameObject
from breakout.sprite_renderer import SpriteRenderer
from breakout.resource_manager import ResourceManager

class GameLevel:
    def __init__(self, file: str, level_width: int, level_height: int):
        # level state
        self.bricks: list[GameObject] = []

        self.load(file, level_width, level_height)

    # loads level from file
    def load(self, file: str, level_width: int, level_height: int) -> None:
        # clear old data
        self.bricks.clear()

        # load from file
        tile_data = []
        try:
            with open(file, 'r') as f:
                for line in f:
                    row = list(map(int, line.split()))
                    tile_data.append(row)
        except FileNotFoundError:
            print(f"Error: file {file} not found.")
            return
            
        if tile_data:
            self.init(tile_data, level_width, level_height)

    # render level
    def draw(self, renderer: SpriteRenderer) -> None:
        for tile in self.bricks:
            if not tile.destroyed:
                tile.draw(renderer)

    def init(self, tile_data: list[list[int]], level_width: int, level_height: int) -> None:
        # calculate dimensions
        height = len(tile_data)
        width = len(tile_data[0]) if height > 0 else 0
        unit_width = level_width / width
        unit_height = level_height / height

        # initialize level tiles based on tile_data
        for y, row in enumerate(tile_data):
            for x, tile_code in enumerate(row):
                pos = glm.vec2(unit_width * x, unit_height * y)
                size = glm.vec2(unit_width, unit_height)

                if tile_code == 1:  # Solid block 
                    obj = GameObject(
                        position=pos,
                        size=size,
                        sprite=ResourceManager.get_texture("block_solid"),
                        color=glm.vec3(0.8, 0.8, 0.7),
                        is_solid=True
                    )
                    self.bricks.append(obj)
                elif tile_code > 1:  # Non-solid blocks with varying colors
                    color = glm.vec3(1.0, 1.0, 1.0)  # Default to white
                    if tile_code == 2:
                        color = glm.vec3(0.2, 0.6, 1.0)
                    elif tile_code == 3:
                        color = glm.vec3(0.0, 0.7, 0.0)
                    elif tile_code == 4:
                        color = glm.vec3(0.8, 0.8, 0.4)
                    elif tile_code == 5:
                        color = glm.vec3(1.0, 0.5, 0.0)

                    obj = GameObject(
                        position=pos,
                        size=size,
                        sprite=ResourceManager.get_texture("block"),
                        color=color,
                        is_solid=False
                    )
                    self.bricks.append(obj)

    def is_completed(self) -> bool:
        for tile in self.bricks:
            if not tile.is_solid and not tile.destroyed:
                return False
        return True