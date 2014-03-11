import curses;
import time, platform;

class Direction:
    """An enum for the possible movement directions"""
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

class Game:
    """The game logic itself. The loop and input handling are here."""

    XRES = 80
    YRES = 24

    TOPLEFT = (1, 1)
    GAMEWIDTH = 78
    GAMEHEIGHT = 21

    def __init__(self, screen):
        """Create the screen, player, assets."""
        self.screen = screen
        self.running = True
        self.player = Player(self)
        self.walls = dict()

        # Debug: Make walls
        self.walls[(20, 21)] = Wall()
        self.walls[(20, 22)] = Wall()
        self.walls[(20, 23)] = Wall()
        self.walls[(20, 24)] = Wall()

        self.walls[(19, 20)] = Wall()
        self.walls[(18, 20)] = Wall()
        self.walls[(17, 20)] = Wall()
        self.walls[(16, 20)] = Wall()

        self.walls[(16, 21)] = Wall()
        self.walls[(16, 22)] = Wall()
        self.walls[(16, 23)] = Wall()
        self.walls[(16, 24)] = Wall()

        self.walls[(16, 24)] = Wall()
        self.walls[(17, 24)] = Wall()
        self.walls[(18, 24)] = Wall()
        self.walls[(19, 24)] = Wall()

        self.walls[(20, 20)] = Wall()

        self.walls[(18, 22)] = Wall()
        self.walls[(19, 22)] = Wall()
        self.walls[(17, 22)] = Wall()
        self.walls[(18, 21)] = Wall()
        self.walls[(18, 23)] = Wall()

    def initialiseWalls(self):
        """Builds the correct wall graphics"""
        # This is one of the ugliest things I've ever written.
        # Don't judge me!
        for (y, x) in self.walls:
            wall = self.walls[(y, x)]
            wallUp = wallDown = wallLeft = wallRight = False
            try:
                self.walls[(y-1, x)]
                wallUp = True
            except Exception as e:
                pass
            try:
                self.walls[(y+1, x)]
                wallDown = True
            except Exception as e:
                pass
            try:
                self.walls[(y, x-1)]
                wallLeft = True
            except Exception as e:
                pass
            try:
                self.walls[(y, x+1)]
                wallRight = True
            except Exception as e:
                pass

            system = platform.system()

            UpDown = '|'
            LeftRight = '-'
            UpLeft = '-'
            UpRight = '-'
            DownLeft = '-'
            DownRight = '-'
            DownLeftRight = '-'
            UpLeftRight = '-'
            LeftUpDown = '|'
            RightUpDown = '|'
            UpDownLeftRight = '|'

            if (system == 'Windows'):
                LeftRight = chr(0xC4)
                UpDown = chr(0xB3)
                UpLeft = chr(0xD9)
                UpRight = chr(0xC0)
                DownLeft = chr(0xBF)
                DownRight = chr(0xDA)
                DownLeftRight = chr(0xC2)
                UpLeftRight = chr(0xC1)
                LeftUpDown = chr(0xB4)
                RightUpDown = chr(0xC3)
                UpDownLeftRight = chr(0xC5)


            if (wallLeft or wallRight):
                wall.character = LeftRight
            else:
                wall.character = UpDown

            # Yeah.. This just happened.
            if (wallUp and wallLeft):
                wall.character = UpLeft
            if (wallUp and wallRight):
                wall.character = UpRight
            if (wallDown and wallLeft):
                wall.character = DownLeft
            if (wallDown and wallRight):
                wall.character = DownRight
            if (wallDown and wallLeft and wallRight):
                wall.character = DownLeftRight
            if (wallUp and wallLeft and wallRight):
                wall.character = UpLeftRight
            if (wallLeft and wallUp and wallDown):
                wall.character = LeftUpDown
            if (wallRight and wallUp and wallDown):
                wall.character = RightUpDown
            if (wallRight and wallUp and wallDown and wallLeft):
                wall.character = UpDownLeftRight

    def mainLoop(self):
        """Run the game while a flag is set."""
        # Initialise walls to correct characters
        self.initialiseWalls()

        # Start the main loop
        while (self.running):
            self.logic()
            self.draw()
            self.handleInput()

    def draw(self):
        """ Draw it all, filling in the blanks as necessary """
        # Wipe out the screen.
        self.screen.erase()

        # Draw the floors, walls, etc.
        # Floors first, then we'll override them
        for x in range(Game.TOPLEFT[0], Game.GAMEWIDTH + 1):
            for y in range(Game.TOPLEFT[1], Game.GAMEHEIGHT + 1):
                self.screen.addstr(y, x, '.', curses.color_pair(0))
                try:
                    wall = self.walls[(y, x)]
                    self.screen.addstr(y, x, wall.character, curses.color_pair(0))
                except Exception as e:
                    pass

        # Walls

        # Draw the entities like players, NPCs
        player = self.player
        self.screen.addstr(player.y, player.x,
                           player.character, curses.color_pair(1))

        # Put the cursor on the player
        self.screen.move(player.y, player.x)
        self.screen.refresh()

        # Debug stuff
        self.screen.addstr(0, 0, str(player.x) + " " + str(player.y))

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

class Wall(object):
    """Wall objects, which the player cannot walk through"""
    def __init__(self):
        """Initialise the player object"""
        self.x = 21
        self.y = 20
        self.character = '|'
        self.colour = curses.COLOR_WHITE

class Player(object):
    """The player object, containing data such as HP etc."""
    def __init__(self, game):
        """Initialise the player object"""
        self.x = 20
        self.y = 20
        self.character = '@'
        self.game = game
        self.colour = curses.COLOR_WHITE

    def move(self, direction, steps=1):
        """Move the player one unit in the specified direction"""
        oldX = self.x
        oldY = self.y
        if direction == Direction.UP:
            self.y -= steps
        elif direction == Direction.DOWN:
            self.y += steps
        elif direction == Direction.LEFT:
            self.x -= steps
        elif direction == Direction.RIGHT:
            self.x += steps

        # Don't let them walk through walls.
        try:
            wall = self.game.walls[(self.y, self.x)]
            self.x = oldX
            self.y = oldY
        except Exception as e:
            # No wall.
            pass

        # Bounce them back if they've walked off the terminal!
        if (self.x < Game.TOPLEFT[0]):
            self.x = Game.TOPLEFT[0]
        elif (self.x >= Game.TOPLEFT[0] + Game.GAMEWIDTH):
            self.x = Game.GAMEWIDTH

        if (self.y < Game.TOPLEFT[1]):
            self.y = Game.TOPLEFT[1]
        elif (self.y >= Game.TOPLEFT[1] + Game.GAMEHEIGHT):
            self.y = Game.GAMEHEIGHT

def main(stdscr):
    """Initialises the Game object and basically gets out of the way"""
    (ywidth, xwidth) = stdscr.getmaxyx()
    if (ywidth < Game.YRES or xwidth < Game.XRES):
        stdscr.addstr("The terminal should be at least {} by {}".format(Game.XRES, Game.YRES))
        stdscr.getch()
        return -1
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    win = curses.newwin(Game.YRES, Game.XRES)
    win.bkgd(' ', curses.color_pair(0))
    game = Game(win)
    game.mainLoop()

if __name__ == '__main__':
    """Handles all the nasty stuff to do with curses set-up + tear-down"""
    curses.wrapper(main)
