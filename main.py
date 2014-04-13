# The main file, with all the stuff. Yeah.

# External imports
import curses

# Our imports
from game import Game
from constants import Constants
from title import TitleScreen

def main(stdscr):
    """Initialises the Game object and basically gets out of the way"""
    # Make sure the screen is big enough for our amazing game
    (ywidth, xwidth) = stdscr.getmaxyx()
    if (ywidth < Constants.YRES or xwidth < Constants.XRES):
        stdscr.addstr("The terminal should be at least {} by {}".format(Constants.XRES, Constants.YRES))
        stdscr.getch()
        return -1

    # Set-up the colours we'll be using'
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_BLACK)
    Constants.initColours()

    # Make the window..
    win = curses.newwin(Constants.YRES, Constants.XRES)
    win.bkgd(' ', curses.color_pair(0))

    # Start the game, with the title screen.
    title = TitleScreen(win)
    title.execute()

if __name__ == '__main__':
    """Handles all the nasty stuff to do with curses set-up + tear-down"""
    curses.wrapper(main)
