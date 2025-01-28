from breakout.game import Game
from breakout.core import main

SCREEN_WIDTH: int = 800
SCREEN_HEIGHT: int = 600

if __name__ == "__main__":
    Breakout = Game(SCREEN_WIDTH, SCREEN_HEIGHT)
    main(Breakout)
