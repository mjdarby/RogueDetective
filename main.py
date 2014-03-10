import curses;
import time;

class Direction:
    """An enum for the possible movement directions"""
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

class Game:
    """The game logic itself. The loop and input handling are here."""
    def __init__(self, screen):
        """Create the screen, player, assets."""
        self.screen = screen
        self.running = True
        self.player = Player()

    def mainLoop(self):
        """Run the game while a flag is set."""
        while (self.running):
            self.logic()
            self.draw()
            self.handleInput()

    def draw(self):
        """ Draw it all, filling in the blanks as necessary """
        self.screen.erase()
        player = self.player
        self.screen.addstr(player.y, player.x,
                           player.character, curses.color_pair(1))
        self.screen.move(player.y, player.x)
        self.screen.refresh()

    def handleInput(self):
        """ Wait for the player to press a key, then handle
            input appropriately."""
        character = self.screen.getch()
        if character == ord('q'):
            self.running = False
        elif character == ord('h'):
            self.player.move(Direction.LEFT)
        elif character == ord('j'):
            self.player.move(Direction.DOWN)
        elif character == ord('k'):
            self.player.move(Direction.UP)
        elif character == ord('l'):
            self.player.move(Direction.RIGHT)

    def logic(self):
        pass

class Grid(object):
    """The game grid itself."""
    def __init__(self, xDimension, yDimension):
        """Initialises the game grid to X by Y tiles."""
        self.xDimension = xDimension
        self.yDimension = yDimension

class Player(object):
    """The player object, containing data such as HP etc."""
    def __init__(self):
        """Initialise the player object"""
        self.x = 20
        self.y = 30
        self.character = '@'
        self.colour = curses.COLOR_WHITE

    def move(self, direction):
        """Move the player one unit in the specified direction"""
        if direction == Direction.UP:
            self.y -= 1
        elif direction == Direction.DOWN:
            self.y += 1
        elif direction == Direction.LEFT:
            self.x -= 1
        elif direction == Direction.RIGHT:
            self.x += 1

def main(stdscr):
    """Initialises the Game object and basically gets out of the way"""
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    stdscr.bkgd(' ', curses.color_pair(0))
    game = Game(stdscr)
    game.mainLoop()

if __name__ == '__main__':
    """Handles all the nasty stuff to do with curses set-up + tear-down"""
    curses.wrapper(main)
