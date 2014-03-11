import curses;
import time, platform, random;

class Direction:
    """An enum for the possible movement directions"""
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

class InputActions:
    """Enum for input actions"""
    MOVE_UP = 1
    MOVE_LEFT = 2
    MOVE_RIGHT = 3
    MOVE_DOWN = 4
    OPEN_DOOR = 5
    QUIT = 6

class Game:
    """The game logic itself. The loop and input handling are here."""

    XRES = 80
    YRES = 24

    TOPLEFT = (1, 1)
    GAMEWIDTH = 78
    GAMEHEIGHT = 21

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
    KEYMAP[ord('q')] = InputActions.QUIT

    def __init__(self, screen):
        """Create the screen, player, assets."""
        self.screen = screen
        self.running = True
        self.player = Player(self)
        self.walls = dict()
        self.doors = dict()
        self.decorations = dict()
        self.fences = dict()
        self.statusLine = ""

        # Debug: Make walls
        #self.walls[(20, 21)] = Wall()
        self.walls[(20, 22)] = Wall()
        self.walls[(20, 23)] = Wall()
        self.walls[(20, 24)] = Wall()

#        self.walls[(19, 20)] = Wall()
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

        self.fences[(15, 20)] = Fence()
        self.fences[(14, 20)] = Fence()
        self.fences[(13, 20)] = Fence()
        self.fences[(12, 20)] = Fence()
        self.fences[(11, 20)] = Fence()

        self.fences[(11, 21)] = Fence()
        self.fences[(11, 22)] = Fence()
        self.fences[(11, 23)] = Fence()
        self.fences[(11, 24)] = Fence()

        self.fences[(15, 24)] = Fence()
        self.fences[(14, 24)] = Fence()
        self.fences[(13, 24)] = Fence()
        self.fences[(12, 24)] = Fence()
        self.fences[(11, 24)] = Fence()

        self.doors[(20, 21)] = Door(self, 20, 21)
        self.doors[(19, 20)] = Door(self, 19, 20)

        # Random decoration
        for _ in range(50):
            (y, x) = (random.randint(1, Game.GAMEHEIGHT), random.randint(1, Game.GAMEWIDTH))
            self.decorations[(y, x)] = Decoration()

    def initialiseWalls(self):
        """Builds the correct wall graphics"""
        # This is one of the ugliest things I've ever written.
        # Don't judge me!
        for (y, x) in self.walls:
            wall = self.walls[(y, x)]
            wallUp = wallDown = wallLeft = wallRight = False
            # Check for walls via worst method possible
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
            # Check for doors using the same awful method
            try:
                self.doors[(y-1, x)]
                wallUp = True
            except Exception as e:
                pass
            try:
                self.doors[(y+1, x)]
                wallDown = True
            except Exception as e:
                pass
            try:
                self.doors[(y, x-1)]
                wallLeft = True
            except Exception as e:
                pass
            try:
                self.doors[(y, x+1)]
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

            # Terrible attempt at getting nice walls in Linux
            # UpDown = '|'
            # LeftRight = '-'
            # UpLeft = chr(0x6a)
            # UpRight = chr(0x6d)
            # DownLeft = chr(0x06b)
            # DownRight = chr(0x6c)
            # DownLeftRight = chr(0x77)
            # UpLeftRight = chr(0x76)
            # LeftUpDown = chr(0x75)
            # RightUpDown = chr(0x74)
            # UpDownLeftRight = chr(0x6e)
            # Smells bad, huh.

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

        # Decor
        for (y, x) in self.decorations:
            decoration = self.decorations[(y, x)]
            self.screen.addstr(y, x, decoration.character, decoration.colour)

        # Fences
        for (y, x) in self.fences:
            fence = self.fences[(y, x)]
            self.screen.addstr(y, x, fence.character, fence.colour)

        # Walls
        for (y, x) in self.walls:
            wall = self.walls[(y, x)]
            self.screen.addstr(y, x, wall.character, curses.color_pair(0))

        # Doors
        for (y, x) in self.doors:
            door = self.doors[(y, x)]
            self.screen.addstr(y, x, door.character, curses.color_pair(1))

        # Draw the entities like players, NPCs
        player = self.player
        self.screen.addstr(player.y, player.x,
                           player.character, curses.color_pair(1))

        # Status line printing
        self.screen.addstr(0, 0, self.statusLine)
        self.statusLine = ""

        # Debug stuff
        self.screen.addstr(Game.GAMEHEIGHT+1, 1, str(player.x) + " " + str(player.y))

        # Put the cursor on the player
        self.screen.move(player.y, player.x)
        self.screen.refresh()

    def getKey(self):
        gotKey = False
        while not gotKey:
            try:
                key = Game.KEYMAP[self.screen.getch()]
                return key
            except:
                pass

    def getYesNo(self):
        gotYesNo = False
        key = None
        while not gotYesNo:
            key = self.screen.getch()
            if key is ord('y') or key is ord('n'):
                gotYesNo = True
        return key is ord('y')

    def printStatus(self, status):
        """Prints the status line, sets it too so it doesn't get wiped until next frame"""
        self.statusLine = status
        self.screen.addstr(0, 0, " " * 50)
        self.screen.addstr(0, 0, status)
        self.screen.move(self.player.y, self.player.x)

    def handleInput(self):
        """ Wait for the player to press a key, then handle
            input appropriately."""
        actionTaken = False
        while not actionTaken:
            # Update the status line
            key = self.getKey()
            actionTaken = True
            # Quit?
            if key == InputActions.QUIT:
                self.running = False
            # Move?
            elif key == InputActions.MOVE_LEFT:
                actionTaken = self.player.attemptMove(Direction.LEFT)
            elif key == InputActions.MOVE_DOWN:
                actionTaken = self.player.attemptMove(Direction.DOWN)
            elif key == InputActions.MOVE_UP:
                actionTaken = self.player.attemptMove(Direction.UP)
            elif key == InputActions.MOVE_RIGHT:
                actionTaken = self.player.attemptMove(Direction.RIGHT)
            # Open doors?
            elif key == InputActions.OPEN_DOOR:
                self.printStatus("Which direction?")
                direction = self.screen.getch()
                playerPos = [self.player.y, self.player.x]
                try:
                    direction = Game.KEYMAP[direction]
                    if direction == InputActions.MOVE_LEFT:
                        playerPos[1] -= 1
                    elif direction == InputActions.MOVE_DOWN:
                        playerPos[0] += 1
                    elif direction == InputActions.MOVE_UP:
                        playerPos[0] -= 1
                    elif direction == InputActions.MOVE_RIGHT:
                        playerPos[1] += 1

                    if playerPos != [self.player.y, self.player.x]:
                        try:
                            door = self.doors[tuple(playerPos)]
                            door.open()
                        except:
                            self.printStatus("No door there!")
                            actionTaken = False
                    else:
                        self.printStatus("Nevermind.")
                        actionTaken = False
                except:
                    self.printStatus("Nevermind.")
                    actionTaken = False

    def logic(self):
        pass

class Grid(object):
    """The game grid itself."""
    def __init__(self, xDimension, yDimension):
        """Initialises the game grid to X by Y tiles."""
        self.xDimension = xDimension
        self.yDimension = yDimension

class Decoration(object):
    """Just a decorative tile."""
    def __init__(self):
        self.character = '?'
        self.colour = curses.color_pair(3)

class Fence(object):
    """Fences are walls that can be jumped over."""
    def __init__(self):
        self.character = '#'
        self.colour = curses.color_pair(0)

class Door(object):
    """Players can open or close these!"""
    def __init__(self, game, y, x):
        self.y = y
        self.x = x
        self.character = '+'
        self.closed = True
        self.colour = curses.COLOR_RED
        self.game = game

    def open(self):
        """Open the door such that it doesn't blend with the walls"""
        self.closed = not self.closed
        self.character = '+' if self.closed else '-'
        if not self.closed:
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

    def checkObstruction(self, direction = None, steps = 1):
        # Don't let them walk through walls or closed doors
        (candidateY, candidateX) = (self.y, self.x)
        if direction == Direction.UP:
            candidateY -= steps
        elif direction == Direction.DOWN:
            candidateY += steps
        elif direction == Direction.LEFT:
            candidateX -= steps
        elif direction == Direction.RIGHT:
            candidateX += steps

        try:
            wall = self.game.walls[(candidateY, candidateX)]
            return True
        except Exception as e:
            # No wall.
            pass

        try:
            door = self.game.doors[(candidateY, candidateX)]
            if door.closed:
                return True
        except Exception as e:
            # No door.
            pass

        try:
            fence = self.game.fences[(candidateY, candidateX)]
            return True
        except:
            pass

        return False

    def checkForFence(self, direction = None, steps = 1):
        """Check for fence in direction specified, at distance steps"""
        # Don't let them walk through walls or closed doors
        (candidateY, candidateX) = (self.y, self.x)
        if direction == Direction.UP:
            candidateY -= steps
        elif direction == Direction.DOWN:
            candidateY += steps
        elif direction == Direction.LEFT:
            candidateX -= steps
        elif direction == Direction.RIGHT:
            candidateX += steps

        try:
            fence = self.game.fences[(candidateY, candidateX)]
            return True
        except:
            pass

        return False

    def move(self, direction, steps=1):
        if direction == Direction.UP:
            self.y -= steps
        elif direction == Direction.DOWN:
            self.y += steps
        elif direction == Direction.LEFT:
            self.x -= steps
        elif direction == Direction.RIGHT:
            self.x += steps

    def attemptMove(self, direction):
        """Move the player one unit in the specified direction"""
        moved = True

        # Don't move if bumping in to a wall, door, fence..
        if not self.checkObstruction(direction, 1):
            self.move(direction)
        else:
            moved = False

        # If it was a fence, let them try and jump it if there's nothing left
        if self.checkForFence(direction, 1) and not moved:
            moreFences = self.checkObstruction(direction, 2)
            if not moreFences:
                self.game.printStatus("Jump fence?")
                jumpFence = self.game.getYesNo()
                if jumpFence:
                    # Put them on the other side of the fence.
                    self.move(direction, 2)
                    moved = True
                else:
                    moved = False
            else:
                moved = False
            self.game.printStatus("")

        # TODO: Or indeed, NPCs

        # Bounce them back if they've walked off the terminal!
        if (self.x < Game.TOPLEFT[0]):
            self.x = Game.TOPLEFT[0]
            moved = False
        elif (self.x >= Game.TOPLEFT[0] + Game.GAMEWIDTH):
            self.x = Game.GAMEWIDTH
            moved = False

        if (self.y < Game.TOPLEFT[1]):
            self.y = Game.TOPLEFT[1]
            moved = False
        elif (self.y >= Game.TOPLEFT[1] + Game.GAMEHEIGHT):
            self.y = Game.GAMEHEIGHT
            moved = False

        return moved

def main(stdscr):
    """Initialises the Game object and basically gets out of the way"""
    (ywidth, xwidth) = stdscr.getmaxyx()
    if (ywidth < Game.YRES or xwidth < Game.XRES):
        stdscr.addstr("The terminal should be at least {} by {}".format(Game.XRES, Game.YRES))
        stdscr.getch()
        return -1
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    win = curses.newwin(Game.YRES, Game.XRES)
    win.bkgd(' ', curses.color_pair(0))
    game = Game(win)
    game.mainLoop()

if __name__ == '__main__':
    """Handles all the nasty stuff to do with curses set-up + tear-down"""
    curses.wrapper(main)
