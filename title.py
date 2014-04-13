# The title screen

# External imports
import curses

# Our imports
from game import Game
from constants import Constants

titleScreenGraphics = """
-------------------------------------------------------------------------------
|                                                                             |
|                                                                             |
|                                                                             |
|                                                                             |
|                              Rogue Detective                                |
|                                                                             |
|                         an adventure in suspicion                           |
|                                                                             |
|                                by Nifrith                                   |
|                                                                             |
|                                                                             |
|                                                                             |
|                                                                             |
|                           Press Any Key To Begin                            |
|                                                                             |
|                                                                             |
|                                                                             |
|                                                                             |
|                                                                             |
-------------------------------------------------------------------------------
"""

class TitleScreen:
    """The title screen representation"""
    def __init__(self, screen):
        """Just set up the text, really"""
        self.screen = screen

    def execute(self):
        self.screen.addstr(0, 0, titleScreenGraphics, Constants.COLOUR_WHITE)
        self.screen.noutrefresh()
        curses.doupdate()
        self.screen.getch()
        game = Game(self.screen)
        game.mainLoop()
