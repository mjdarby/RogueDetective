# The game screen logic, including level creation and whatnot

# External imports
import curses

# Python imports
import random, platform

# Our imports
from constants import Constants
from enums import Direction, InputActions, Status
from entity import Player, Police
from tiles import Decoration, Tile
from town import Town
from plan import Plan

class Game:
    """The game logic itself. The loop and input handling are here."""
    def __init__(self, screen):
        """Create the screen, player, assets."""
        # Some technical items, first
        self.screen = screen
        self.gameScreen = curses.newpad(Constants.SCREENHEIGHT, Constants.SCREENWIDTH)
        self.running = True

        # Collections of various objects
        self.player = Player(self)
        self.walls = dict()
        self.doors = dict()
        self.decorations = dict()
        self.fences = dict()
        self.npcs = []
        self.police = []
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
            (y, x) = (random.randint(1, Constants.MAPHEIGHT - 1), random.randint(1, Constants.MAPWIDTH - 1))
            self.decorations[(y, x)] = Decoration()

        # Create tiles for visibility and FoV
        self.tiles = dict()
        for x in range(Constants.MAPWIDTH):
            for y in range(Constants.MAPHEIGHT):
                self.tiles[(y,x)] = Tile()

        # Town creation
        self.town = Town(self, 5, 5, 3, 3)
        
        # Setup the murder..
        self.murderSetup()

        # Put together the NPC schedules
        self.generatePlans()

    def initialiseWalls(self):
        """Builds the correct wall graphics"""
        # This is one of the ugliest things I've ever written.
        # Don't judge me!
        for (y, x) in self.walls:
            wall = self.walls[(y, x)]
            if wall.character.isdigit():
                continue
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
        return (entityY >= cameraY and entityY <= cameraY + Constants.GAMEHEIGHT 
                and entityX >= cameraX and entityX <= entityX + Constants.GAMEWIDTH)

    def draw(self):
        """ Draw it all, but only the stuff that would be on the screen"""
        # Wipe out the screen.
        self.screen.erase()
        self.gameScreen.erase()

        # Sort out the camera
        cameraX = max(0, self.player.x - Constants.GAMEWIDTH // 2)
        cameraX = min(cameraX, Constants.MAPWIDTH - Constants.GAMEWIDTH)
        cameraY = max(0, self.player.y - Constants.GAMEHEIGHT // 2)
        cameraY = min(cameraY, Constants.MAPHEIGHT - Constants.GAMEHEIGHT)
        alwaysSeeWalls = False

        # Draw the floors, walls, etc.
        # Floors first, then we'll override them
        for x in range(0, Constants.MAPWIDTH):
            for y in range(0, Constants.MAPHEIGHT):
                if not self.isInCamera(cameraY, cameraX, y, x):
                    continue

                if self.tiles[(y, x)].visible or not Constants.FOV_ENABLED:
                    self.gameScreen.addstr(
                        y, 
                        x, 
                        '.', 
                        Constants.COLOUR_GREEN)

                    if (y, x) in self.decorations:
                        decoration = self.decorations[(y, x)]
                        self.gameScreen.addstr(y, 
                                               x, 
                                               decoration.character, 
                                               decoration.colour)

                    # Fences
                    if (y, x) in self.fences:
                        fence = self.fences[(y, x)]
                        self.gameScreen.addstr(y, 
                                               x, 
                                               fence.character, 
                                               fence.colour)

                    # Doors
                    if (y, x) in self.doors:
                        door = self.doors[(y, x)]
                        self.gameScreen.addstr(y, 
                                               x, 
                                               door.character, 
                                               door.colour)

                if (self.tiles[(y,x)].seen
                    and (alwaysSeeWalls or self.tiles[(y,x)].visible)
                    or not Constants.FOV_ENABLED):
                    if (y, x) in self.walls:
                        wall = self.walls[(y,x)]
                        self.gameScreen.addstr(y, 
                                               x, 
                                               wall.character, 
                                               wall.colour)

        # Draw the entities like players, NPCs
        for npc in self.npcs:
            npcPos = (npc.y, npc.x)
            if npcPos in self.tiles:
                tile = self.tiles[npcPos]
                if tile.visible or not Constants.FOV_ENABLED:
                    self.gameScreen.addstr(npc.y, 
                                           npc.x, 
                                           npc.character, 
                                           npc.colour)

        for police in self.police:
            policePos = (police.y, police.x)
            if policePos in self.tiles:
                tile = self.tiles[policePos]
                if tile.visible or not Constants.FOV_ENABLED:
                    self.gameScreen.addstr(police.y, 
                                           police.x, 
                                           police.character, 
                                           police.colour)

        player = self.player
        self.gameScreen.addstr(player.y, player.x,
                               player.character, player.colour)

        # Status line printing
        self.screen.addstr(0, 0, self.statusLine)
        self.statusLine = ""

        # Debug and bottom status stuff
        self.screen.addstr(Constants.GAMEHEIGHT +1, 0, self.bottomLine)

        if self.npcs:
            npc = self.npcs[0]
            if npc.path:
                path = npc.path[0]
                self.screen.addstr(Constants.GAMEHEIGHT+2, 1, str(path))

        self.screen.noutrefresh()

        self.gameScreen.noutrefresh(cameraY, cameraX, 1, 1, Constants.GAMEHEIGHT, Constants.GAMEWIDTH)

        self.moveCursorToPlayer()

        # Blit the screen
        curses.doupdate()

    def moveCursorToPlayer(self):
        """Moves the cursor to the player. Duh."""
        # Make sure the cursor follows the players y/x co-ord
        # when he's near the minimum values of each
        cursorX = min(Constants.GAMEWIDTH // 2 + 1, self.player.x + 1)
        cursorY = min(Constants.GAMEHEIGHT // 2 + 1, self.player.y + 1)

        # Make sure the cursor follows the players y/x co-ord +
        # the max camera range when he's near the maximum values
        # of each
        maxCameraX = Constants.MAPWIDTH - Constants.GAMEWIDTH // 2 - 1
        maxCameraY = Constants.MAPHEIGHT - Constants.GAMEHEIGHT // 2  - 1
        if self.player.x > maxCameraX:
            offset = (self.player.x - maxCameraX) + Constants.GAMEWIDTH // 2
            cursorX = offset
        if self.player.y > maxCameraY:
            offset = self.player.y - maxCameraY + Constants.GAMEHEIGHT // 2 + 1
            cursorY = offset
        self.screen.move(cursorY, cursorX)

    def getKey(self):
        """Utility funciton that waits until a valid input has been entered."""
        gotKey = False
        while not gotKey:
            try:
                key = Constants.KEYMAP[self.screen.getch()]
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
            direction = Constants.KEYMAP[direction]
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
        
    def openDoor(self):
        self.printStatus("Which direction?")
        direction = self.screen.getch()
        playerPos = [self.player.y, self.player.x]
        actionTaken = True
        try:
            direction = Constants.KEYMAP[direction]
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
            elif key == InputActions.OPEN_DOOR:
                actionTaken = self.openDoor()
            elif key == InputActions.KICK_DOOR:
                actionTaken = self.kickDoor()
            elif key == InputActions.WAIT:
                actionTaken = True # Do nothing.

    def murderSetup(self):
        """Picks the victim and murderer, and kills the victim"""
        victimIdx = random.randint(0, len(self.npcs) - 1)
        killerIdx = None
        while True:
            killerIdx = random.randint(0, len(self.npcs) - 1)
            if killerIdx is not victimIdx:
                break
        self.npcs[victimIdx].die()
        self.npcs[killerIdx].killer = True

        # Spawn some cops around the dead guy
        victim = self.npcs[victimIdx]
        house = victim.square.house
        for _ in range(0, random.randint(4, 5)):
            y = random.randint(house.absoluteY + 1, 
                               house.absoluteY + house.height - 1)
            x = random.randint(house.absoluteX + 1, 
                               house.absoluteX + house.width - 1)
            police = Police(self, y, x)
            self.police.append(police)

        # Put the player outside the dead guy's house
        self.player.y = house.absoluteY + house.frontDoorPos[0] + 1
        self.player.x = house.absoluteX + house.frontDoorPos[1]

        # Put an office next to him
        police = Police(self, self.player.y, self.player.x + 1)
        self.police.append(police)

        self.printStatus("\"It's a messy one today, boss.\"")

    def generatePlans(self):
        """Generate the initial Plans for all NPCs"""
        # It should be pretty consistent. Like, if an NPC is visiting 
        # another NPC's house, the vistee shouldn't make a plan to go out.
        for npc in self.npcs:
            if npc.alive:
                for x in range(5):
                    randomSquareIndex = None
                    while True:
                        # Don't visit the dead guy, that's morbid
                        randomSquareIndex = random.randint(0, len(self.squares) - 1)
                        if self.squares[randomSquareIndex].npc.alive:
                            break
                    visitNeighbour = Plan.VisitNeighbour(npc, randomSquareIndex)
                    randomHour = random.randint(0, 8) + 8
                    npc.plan.addPlanEntry(randomHour, 0, visitNeighbour)

    def logic(self):
        """Run all the assorted logic for all entities and advance the clock"""
        if self.turnsToNextMinute <= 0:
            self.minute += 1
            if self.minute == 60:
                self.minute = 0
                self.hour += 1
                if self.hour == 24:
                    self.hour = 0
            self.turnsToNextMinute = Constants.TURNS_BETWEEN_MINUTES
        else:
            self.turnsToNextMinute -= 1

        for npc in self.npcs:
            npc.update()
        for police in self.police:
            police.update()
        for door in self.doors:
            self.doors[door].update()
        self.player.generateFov()

        # Update the bottom line
        self.bottomLine = "(" + str(self.player.x) + ", " + str(self.player.y) + ")"
        time = str(self.hour).zfill(2) + ":" + str(self.minute).zfill(2)
        self.bottomLine += " " + time
