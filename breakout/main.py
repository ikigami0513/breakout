import sys
import os

# We dynamically add Elyria to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from game import Breakout
from elyria import main


if __name__ == "__main__":
    breakout = Breakout()
    main(breakout)
