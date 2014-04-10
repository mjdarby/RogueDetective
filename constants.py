# All the constants, super sweet. Collected in ultra cool class form!

from enums import InputActions

# TODO: Put the colours in here, it's getting silly having to import curses
# everywhere

class Constants:
    """All the constants used by the game that need to be shared across
    modules"""

    # The window resolution
    XRES = 80
    YRES = 24

    # The offset of the game screen itself
    # Status messages appear on the first line,
    # so we currently offset by 1 y-line
    TOPLEFT = (1, 0)

    # Game width/height: The size of the visible map at any one time
    GAMEWIDTH = 78
    GAMEHEIGHT = 21

    # Map width/height: The complete size of the map
    # NB. Must be greater than or equal to the game width/height
    # May remove this restriction later on, but right now breaking it
    # messed with the cursor logic.
    MAPWIDTH = 78
    MAPHEIGHT = 75

    # Screen width/height: Size of the curses pad. +1 height because
    # of a crazy off-the-screen cursor bug
    SCREENWIDTH = MAPWIDTH
    SCREENHEIGHT = MAPHEIGHT + 1

    # Other constants (debugging, etc)
    PATHFINDING_DEBUG = False
    DOOR_CLOSE_TIME = 10
    TURNS_BETWEEN_MINUTES = 3
    FRONT_DOORS_LOCKED = False
    FOV_ENABLED = False
    NPC_ON_NPC_COLLISIONS = False

    # Map of keyboard key to action
    KEYMAP = dict()
    KEYMAP[ord('h')] = InputActions.MOVE_LEFT
    KEYMAP[ord('j')] = InputActions.MOVE_DOWN
    KEYMAP[ord('k')] = InputActions.MOVE_UP
    KEYMAP[ord('l')] = InputActions.MOVE_RIGHT

    KEYMAP[ord('4')] = InputActions.MOVE_LEFT
    KEYMAP[ord('2')] = InputActions.MOVE_DOWN
    KEYMAP[ord('8')] = InputActions.MOVE_UP
    KEYMAP[ord('6')] = InputActions.MOVE_RIGHT

    KEYMAP[ord('o')] = InputActions.OPEN_DOOR
    KEYMAP[ord('p')] = InputActions.KICK_DOOR
    KEYMAP[ord('K')] = InputActions.KICK_DOOR
    KEYMAP[ord('q')] = InputActions.QUIT

    KEYMAP[ord('.')] = InputActions.WAIT

