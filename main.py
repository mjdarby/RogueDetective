# The main file, with all the stuff. Yeah.

# External imports
import curses

# Our imports
from game import Game

def main(stdscr):
    """Initialises the Game object and basically gets out of the way"""
    (ywidth, xwidth) = stdscr.getmaxyx()
    if (ywidth < Game.YRES or xwidth < Game.XRES):
        stdscr.addstr("The terminal should be at least {} by {}".format(Game.XRES, Game.YRES))
        stdscr.getch()
        return -1
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_BLACK)
    win = curses.newwin(Game.YRES, Game.XRES)
    win.bkgd(' ', curses.color_pair(0))
    game = Game(win)
    game.mainLoop()

if __name__ == '__main__':
    """Handles all the nasty stuff to do with curses set-up + tear-down"""
    curses.wrapper(main)
