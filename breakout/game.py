from enum import StrEnum

class GameState(StrEnum):
    GAME_ACTIVE = "GAME_ACTIVE"
    GAME_MENU = "GAME_MENU"
    GAME_WIN = "GAME_WIN"

class Game:
    state: GameState
    keys: list[bool]
    width: int
    height: int

    def __init__(self):
        pass

    def init(self) -> None:
        # initialize game state (load all shaders/textures/levels)
        pass

    def process_input(dt: float):
        pass

    def update(dt: float):
        pass

    def render():
        pass
    