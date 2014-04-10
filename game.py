# The game screen logic, including level creation and whatnot

# External imports
import curses

# Python imports
import random, platform

# Our imports
from constants import Constants
from enums import Direction, InputActions, Status
from entity import Player
from tiles import Decoration, Tile
from town import Town
from plan import Plan

class Game:
    """The game logic itself. The loop and input handling are here."""

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

    def __init__(self, screen):
        """Create the screen, player, assets."""
        # Some technical items, first
        self.screen = screen
        self.gameScreen = curses.newpad(Game.SCREENHEIGHT, Game.SCREENWIDTH)
        self.running = True

        # Collections of various objects
        self.player = Player(self)
        self.walls = dict()
        self.doors = dict()
        self.decorations = dict()
        self.fences = dict()
        self.npcs = []
        self.squares = []

        # The current contents of the status line
        # TODO: Maybe rename this
        self.statusLine = ""

        # The bottom line contains the clock and other stuff
        self.bottomLine = ""

        # The current time and time-related variables
        self.hour = 7
        self.minute = 59
        self.turnsToNextMinute = 0

        ### The actual game creation logic
        # Random decoration
        for _ in range(500):
            (y, x) = (random.randint(1, Game.MAPHEIGHT - 1), random.randint(1, Game.MAPWIDTH - 1))
            self.decorations[(y, x)] = Decoration()

        # Create tiles for visibility and FoV
        self.tiles = dict()
        for x in range(Game.MAPWIDTH):
            for y in range(Game.MAPHEIGHT):
                self.tiles[(y,x)] = Tile()

        # Test town:
        self.town = Town(self, 5, 5, 3, 3)

        # Plan test!
        for npc in self.npcs:
            randomSquareIndex = random.randint(0, len(self.squares) - 1)
            visitNeighbour = Plan.VisitNeighbour(npc, randomSquareIndex)
            npc.plan.addPlanEntry(8, 0, visitNeighbour)

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

            # Yeah.. This just happened. Next time consider bitstates
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

    def isInCamera(self, cameraY, cameraX, entityY, entityX):
        """ Shouldn't be a class method. Determines if we should draw
        a character or not."""
        return entityY >= cameraY and entityY <= cameraY + Game.GAMEHEIGHT and entityX >= cameraX and entityX <= entityX + Game.GAMEWIDTH

    def draw(self):
        """ Draw it all, but only the stuff that would be on the screen"""
        # Wipe out the screen.
        self.screen.erase()
        self.gameScreen.erase()

        # Sort out the camera
        cameraX = max(0, self.player.x - Game.GAMEWIDTH // 2)
        cameraX = min(cameraX, Game.MAPWIDTH - Game.GAMEWIDTH)
        cameraY = max(0, self.player.y - Game.GAMEHEIGHT // 2)
        cameraY = min(cameraY, Game.MAPHEIGHT - Game.GAMEHEIGHT)
        alwaysSeeWalls = False

        # Draw the floors, walls, etc.
        # Floors first, then we'll override them
        for x in range(0, Game.MAPWIDTH):
            for y in range(0, Game.MAPHEIGHT):
                if not self.isInCamera(cameraY, cameraX, y, x):
                    continue

                if self.tiles[(y, x)].visible:
                    self.gameScreen.addstr(y, x, '.', Constants.COLOUR_GREEN)

                    if (y, x) in self.decorations:
                        decoration = self.decorations[(y, x)]
                        self.gameScreen.addstr(y, x, decoration.character, decoration.colour)

                    # Fences
                    if (y, x) in self.fences:
                        fence = self.fences[(y, x)]
                        self.gameScreen.addstr(y, x, fence.character, fence.colour)

                    # Doors
                    if (y, x) in self.doors:
                        door = self.doors[(y, x)]
                        self.gameScreen.addstr(y, x, door.character, door.colour)

                if (self.tiles[(y,x)].seen
                    and (alwaysSeeWalls or self.tiles[(y,x)].visible)):
                    if (y, x) in self.walls:
                        wall = self.walls[(y,x)]
                        self.gameScreen.addstr(y, x, wall.character, wall.colour)

        # Draw the entities like players, NPCs
        for npc in self.npcs:
            npcPos = (npc.y, npc.x)
            if npcPos in self.tiles:
                tile = self.tiles[npcPos]
                if tile.visible:
                    self.gameScreen.addstr(npc.y, npc.x, npc.character, npc.colour)

        player = self.player
        self.gameScreen.addstr(player.y, player.x,
                               player.character, player.colour)

        # Status line printing
        self.screen.addstr(0, 0, self.statusLine)
        self.statusLine = ""

        # Debug and bottom status stuff
        self.screen.addstr(Game.GAMEHEIGHT +1, 0, self.bottomLine)

        if self.npcs:
            npc = self.npcs[0]
            if npc.path:
                path = npc.path[0]
                self.screen.addstr(Game.GAMEHEIGHT+2, 1, str(path))

        self.screen.noutrefresh()

        self.gameScreen.noutrefresh(cameraY, cameraX, 1, 1, Game.GAMEHEIGHT, Game.GAMEWIDTH)

        self.moveCursorToPlayer()

        # Blit the screen
        curses.doupdate()

    def moveCursorToPlayer(self):
        """Moves the cursor to the player. Duh."""
        # Make sure the cursor follows the players y/x co-ord
        # when he's near the minimum values of each
        cursorX = min(Game.GAMEWIDTH // 2 + 1, self.player.x + 1)
        cursorY = min(Game.GAMEHEIGHT // 2 + 1, self.player.y + 1)

        # Make sure the cursor follows the players y/x co-ord +
        # the max camera range when he's near the maximum values
        # of each
        maxCameraX = Game.MAPWIDTH - Game.GAMEWIDTH // 2 - 1
        maxCameraY = Game.MAPHEIGHT - Game.GAMEHEIGHT // 2  - 1
        if self.player.x > maxCameraX:
            offset = (self.player.x - maxCameraX) + Game.GAMEWIDTH // 2
            cursorX = offset
        if self.player.y > maxCameraY:
            offset = self.player.y - maxCameraY + Game.GAMEHEIGHT // 2 + 1
            cursorY = offset
        self.screen.move(cursorY, cursorX)

    def getKey(self):
        """Utility funciton that waits until a valid input has been entered."""
        gotKey = False
        while not gotKey:
            try:
                key = Game.KEYMAP[self.screen.getch()]
                return key
            except:
                pass

    def getYesNo(self):
        """Utility function for getting 'yes/no' responses."""
        gotYesNo = False
        key = None
        while not gotYesNo:
            key = self.screen.getch()
            if key is ord('y') or key is ord('n'):
                gotYesNo = True
        return key is ord('y')

    def printStatus(self, status, wait=False):
        """Prints the status line. Also sets it so it doesn't get wiped until next frame"""
        self.statusLine = status
        self.screen.addstr(0, 0, " " * 50)
        self.screen.addstr(0, 0, status)
        self.moveCursorToPlayer()

    def kickDoor(self):
        """Prompts for direction and attempts to kick down the door there if present."""
        actionTaken = True
        self.printStatus("Which direction?")
        direction = self.screen.getch()
        success = random.randrange(100) > 80
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
                    if not door.closed:
                        self.printStatus("It's open, champ.")
                    elif success:
                        door.locked= False
                        door.playerOpen()
                        self.printStatus("The door slams open!")
                    else:
                        self.printStatus("The door holds fast.")
                except:
                    self.printStatus("No door there!")
                    actionTaken = False
            else:
                self.printStatus("Nevermind.")
                actionTaken = False
        except:
            self.printStatus("Nevermind.")
            actionTaken = False
        return actionTaken

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
                            door.playerOpen()
                        except:
                            self.printStatus("No door there!")
                            actionTaken = False
                    else:
                        self.printStatus("Nevermind.")
                        actionTaken = False
                except:
                    self.printStatus("Nevermind.")
                    actionTaken = False
            elif key == InputActions.KICK_DOOR:
                actionTaken = self.kickDoor()
            elif key == InputActions.WAIT:
                actionTaken = True # Do nothing.

    def logic(self):
        """Run all the assorted logic for all entities and advance the clock"""
        if self.turnsToNextMinute <= 0:
            self.minute += 1
            if self.minute == 60:
                self.minute = 0
                self.hour += 1
                if self.hour == 24:
                    self.hour = 0
            self.turnsToNextMinute = Game.TURNS_BETWEEN_MINUTES
        else:
            self.turnsToNextMinute -= 1

        for npc in self.npcs:
            npc.update()
        for door in self.doors:
            self.doors[door].update()
        self.player.generateFov()

        # Update the bottom line
        self.bottomLine = "(" + str(self.player.x) + ", " + str(self.player.y) + ")"
        time = str(self.hour).zfill(2) + ":" + str(self.minute).zfill(2)
        self.bottomLine += " " + time
