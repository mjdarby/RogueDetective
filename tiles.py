# Tiles, tiles, tiles! Doors, walls.. If it's not a player but it's
# on the map, it goes here.

# Our imports
from constants import Constants

class Tile(object):
    """Represents a tile in vision.
    Once seen, a tile will show what is currently on it via the game draw method.
    Once a tile goes out of view, everything that isn't a wall disappears during draw."""
    def __init__(self):
        self.visible = False
        self.seen = False
        if not Constants.FOV_ENABLED:
            self.seen = True

class Decoration(object):
    """Just a decorative tile."""
    def __init__(self):
        self.character = '?'
        self.colour = Constants.COLOUR_GREEN

class Fence(object):
    """Fences are walls that can be jumped over."""
    def __init__(self):
        self.character = '#'
        self.colour = Constants.COLOUR_WHITE

class Door(object):
    """Players can open or close these!"""
    def __init__(self, game, y, x):
        self.y = y
        self.x = x
        self.character = '+'
        self.closed = True
        self.locked = False
        self.colour = Constants.COLOUR_RED
        self.game = game
        self.timer = -1

    def update(self):
        if self.timer == 0:
            # Close the door if it's open.
            if not self.closed:
                self.open() # This function could be named better

        if self.timer >= 0:
            self.timer -= 1

    def npcOpen(self): # NPCs share all their house keys, okay?
        self.open()

    def playerOpen(self):
        """Open the door such that it doesn't blend with the walls
        Don't let them open it if it's locked"""

        # To prevent the player from being locked in a house, we let him exit
        # if he's inside it. We know he's inside if he's above the door.
        playerInside = (self.game.player.y + 1, self.game.player.x) == (self.y, self.x)
        if not playerInside and self.locked:
            self.game.printStatus("The door is locked.")
            return
        # Reset status line
        self.game.printStatus("")
        self.open()

    def open(self):
        self.closed = not self.closed
        self.character = '+' if self.closed else '-'
        if not self.closed:
            self.timer = self.game.DOOR_CLOSE_TIME
            try:
                self.game.walls[(self.y, self.x-1)] # Ridiculous test for wall on the left
                self.character = '|'
            except:
                pass

class Wall(object):
    """Wall objects, which the player cannot walk through"""
    def __init__(self):
        """Initialise the player object"""
        self.x = 21
        self.y = 20
        self.character = '|'
        self.colour = Constants.COLOUR_WHITE
