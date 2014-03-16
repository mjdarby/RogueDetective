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

    MAPWIDTH = 200
    MAPHEIGHT = 200
    SCREENWIDTH = 200
    SCREENHEIGHT = 201 # because of really dumb cursor bugs

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
        self.gameScreen = curses.newpad(Game.SCREENHEIGHT, Game.SCREENWIDTH)
        self.running = True
        self.player = Player(self)
        self.walls = dict()
        self.doors = dict()
        self.decorations = dict()
        self.fences = dict()
        self.npcs = []
        self.statusLine = ""

        # Random decoration
        for _ in range(1000):
            (y, x) = (random.randint(1, Game.MAPHEIGHT - 1), random.randint(1, Game.MAPWIDTH - 1))
            self.decorations[(y, x)] = Decoration()

        # Test town:
        town = Town(self, 0, 0, 9, 8)

        # NPC test
        self.npcs.append(NPC(self, 20, 20))

        # Testing house generation:
        # house = House(self)
        # house.generateLayout()
        # house.createHouse(1, 4)

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
        cameraY = max(0, self.player.y - Game.GAMEHEIGHT // 2)

        # Draw the floors, walls, etc.
        # Floors first, then we'll override them
        for x in range(0, Game.MAPWIDTH):
            for y in range(0, Game.MAPHEIGHT):
                if self.isInCamera(cameraY, cameraX, y, x):
                    self.gameScreen.addstr(y, x, '.', curses.color_pair(3))

        # Decor
        for (y, x) in self.decorations:
            decoration = self.decorations[(y, x)]
            if self.isInCamera(cameraY, cameraX, y, x):
                self.gameScreen.addstr(y, x, decoration.character, decoration.colour)

        # Fences
        for (y, x) in self.fences:
            fence = self.fences[(y, x)]
            if self.isInCamera(cameraY, cameraX, y, x):
                self.gameScreen.addstr(y, x, fence.character, fence.colour)
                            
        # Walls
        for (y, x) in self.walls:   
            wall = self.walls[(y, x)]
            if self.isInCamera(cameraY, cameraX, y, x):
                self.gameScreen.addstr(y, x, wall.character, curses.color_pair(0))

        # Doors
        for (y, x) in self.doors:
            door = self.doors[(y, x)]
            if self.isInCamera(cameraY, cameraX, y, x):
                self.gameScreen.addstr(y, x, door.character, curses.color_pair(1))

        # Draw the entities like players, NPCs
        for npc in self.npcs:
            self.gameScreen.addstr(npc.y, npc.x, npc.character, npc.colour)

        player = self.player
        self.gameScreen.addstr(player.y, player.x,
                               player.character, curses.color_pair(1))

        # Status line printing
        self.screen.addstr(0, 0, self.statusLine)
        self.statusLine = ""

        # Debug and bottom status stuff
        self.screen.addstr(Game.GAMEHEIGHT+1, 1, str(player.x) + " " + str(player.y))
        self.screen.noutrefresh()

        self.gameScreen.noutrefresh(cameraY, cameraX, 1, 1, Game.GAMEHEIGHT, Game.GAMEWIDTH)
        #self.gameScreen.refresh(player.y, player.x, 1, 1, Game.GAMEHEIGHT, Game.GAMEWIDTH)

        cursorX = min(Game.GAMEWIDTH // 2 + 1, player.x + 1)
        cursorY = min(Game.GAMEHEIGHT // 2 + 1, player.y + 1)
        self.screen.move(cursorY, cursorX)

        # Blit the screen
        curses.doupdate()

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
#        self.screen.move(self.player.y, self.player.x)

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
                            self.printStatus("")
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

class Town(object):
    """A grid with random edges removed, houses placed on the grid"""

    GRID_SIZE = 20
    ROAD_WIDTH = 3
    ROAD_HEIGHT = 2

    class Square(object):
        def __init__(self, game, y, x, heightIdx, widthIdx):
            self.y = y
            self.x = x
            self.game = game
            self.heightIdx = heightIdx
            self.widthIdx = widthIdx

        def generateHouse(self):
            house = House(self.game)
            house.generateLayout(Town.GRID_SIZE, Town.GRID_SIZE)
            house.createHouse(self.y, self.x)

    def __init__(self, game, y, x, height, width):
        self.y = y
        self.x = x
        self.game = game
        # In grid squares, not in tiles
        self.height = height
        self.width = width
        self.squares = dict()
        self.roads = dict()

        self.generateGrid()
        self.createRoads()

    def createRoads(self):
        """Actually make the roads"""
        for (y1, x1) in self.roads:
            self.game.decorations[(self.y+y1), (self.x+x1)] = self.roads[y1, x1]

    def generateRoads(self, heightIdx, widthIdx):
        """Create roads for given grid square"""
        baseY = heightIdx * (Town.GRID_SIZE + Town.ROAD_HEIGHT)
        baseX = widthIdx * (Town.GRID_SIZE + Town.ROAD_WIDTH)
        road = Decoration()
        road.character = '#'
        road.colour = curses.color_pair(4)
        for roadX in range(Town.GRID_SIZE + Town.ROAD_WIDTH - 1):
            for width in range(Town.ROAD_WIDTH):
                self.roads[(baseY + roadX, baseX + Town.GRID_SIZE + width)] = road
        for roadX in range(Town.GRID_SIZE + Town.ROAD_HEIGHT):
            for width in range(Town.ROAD_HEIGHT):
                self.roads[(baseY + Town.GRID_SIZE + width, baseX + roadX)] = road


    def generateGrid(self):
        """Generate the grids + roads + houses"""
        for y in range(self.height):
            squareY = y * (Town.GRID_SIZE + Town.ROAD_HEIGHT) + self.y
            for x in range(self.width):
                squareX = x * (Town.GRID_SIZE + Town.ROAD_WIDTH) + self.x
                # Make a square
                self.squares[(y, x)] = Town.Square(self.game, squareY, squareX, y, x)
                # For now, put a house in the square
                self.squares[(y,x)].generateHouse()
                self.generateRoads(y, x)

class House(object):
    """Houses are procedurally generated constructs in which NPCs live."""
    MINIMUM_WIDTH = 15
    MINIMUM_HEIGHT = 9

    MINIMUM_ROOM_DIMENSION = 4

    class Room(object):
        """Representation of a room in the house"""
        def __init__(self, y, x, height, width):
            self.y = y
            self.x = x
            self.height = height
            self.width = width
            self.walls = dict()
            self.generateWalls()

        def generateWalls(self):
            for x in range(self.width + 1): # +1 to include the corners
                self.walls[(0, x)] = Wall()
                self.walls[(self.height, x)] = Wall()
            for y in range(self.height):
                self.walls[(y, 0)] = Wall()
                self.walls[(y, self.width)] = Wall()

    def __init__(self, game):
        self.width = 0
        self.height = 0
        self.rooms = []
        self.walls = dict()
        self.decorations = dict()
        self.doors = dict()
        self.game = game

    def generateLayout(self, maxHeight, maxWidth):
        # Create the outer walls
        self.generateWalls(maxHeight, maxWidth)

        # Create rooms
        self.generateRooms()

        # Create doors
        self.generateDoors()

    def generateWalls(self, maxHeight, maxWidth):
        """Create the outer walls of the house"""
        self.width = random.randint(House.MINIMUM_WIDTH, maxWidth) - 1
        self.height = random.randint(House.MINIMUM_WIDTH, maxHeight) - 1
        for x in range(self.width): # +1 to include the corners
            self.walls[(0, x)] = Wall()
            self.walls[(self.height, x)] = Wall()
            # Might as well do the floors too, while we're here
            for y in range(self.height):
                decoration = Decoration()
                decoration.character = '.'
                decoration.colour = curses.color_pair(0)
                self.decorations[(y, x)] = decoration
        for y in range(self.height):
            self.walls[(y, 0)] = Wall()
            self.walls[(y, self.width)] = Wall()
        # For now, pick a random wall on the bottom and put the door in it
        self.doorX = random.randint(1,self.width-1)
        del self.walls[(self.height, self.doorX)]

    def generateFirstPartition(self):
        # Make the initial rooms via the first partition
        widthwisePartition = bool(random.getrandbits(1))
        cut = random.randint(House.MINIMUM_ROOM_DIMENSION, 
                            (self.height if widthwisePartition else self.width) - House.MINIMUM_ROOM_DIMENSION)
        if widthwisePartition:
            room = House.Room(0, 0, cut, self.width)
            self.rooms.append(room)
            room = House.Room(cut, 0, self.height - cut, self.width)
            self.rooms.append(room)
            doorPos = random.randint(0, self.width - 1)
            self.doors[(cut, doorPos)] = Door(self.game, cut, doorPos)
        else:
            room = House.Room(0, 0, self.height, cut)
            self.rooms.append(room)
            room = House.Room(0, cut, self.height, self.width - cut)
            self.rooms.append(room)
            doorPos = random.randint(1, self.height - 1)
            self.doors[(doorPos, cut)] = Door(self.game, doorPos, cut)

    def generateRooms(self):
        """Create the rooms by repeated partitioning"""
        # How many partitions should we make, excluding the first?
        numPartitions = random.randint(2, 3)
        self.generateFirstPartition()

        for _ in range(numPartitions):
            # Get a random room, which we'll partition just like the first room
            attempts = 10
            randomRoomIndex = random.randint(0, len(self.rooms) - 1)
            baseRoom = self.rooms[randomRoomIndex]
            widthwisePartition = bool(random.getrandbits(1))

            # Make sure the room will be able to split. If not, pick a new room up to 10 times.
            while baseRoom.height < (2 * House.MINIMUM_ROOM_DIMENSION) or baseRoom.width < (2 * House.MINIMUM_ROOM_DIMENSION):
                # If we really can't make it work with the rooms we have, start fresh.
                if attempts < 0:
                    attempts = 10
                    del self.rooms[:]
                    self.doors.clear()
                    self.generateFirstPartition()

                randomRoomIndex = random.randint(0, len(self.rooms) - 1)
                baseRoom = self.rooms[randomRoomIndex]
                widthwisePartition = bool(random.getrandbits(1))
                attempts -= 1

            cut = random.randint(House.MINIMUM_ROOM_DIMENSION, 
                                 (baseRoom.height if widthwisePartition else baseRoom.width) - House.MINIMUM_ROOM_DIMENSION)

            # Create the two rooms annd put a door in connecting the two new rooms
            if widthwisePartition:
                room = House.Room(baseRoom.y, baseRoom.x, cut, baseRoom.width)
                self.rooms.append(room)
                room = House.Room(baseRoom.y + cut, baseRoom.x, baseRoom.height - cut, baseRoom.width)
                self.rooms.append(room)
                doorPos = random.randint(baseRoom.x+1, baseRoom.x + baseRoom.width - 1)
                self.doors[(baseRoom.y + cut, doorPos)] = Door(self.game, baseRoom.y + cut, doorPos)
            else:
                room = House.Room(baseRoom.y, baseRoom.x, baseRoom.height, cut)
                self.rooms.append(room)
                room = House.Room(baseRoom.y, baseRoom.x + cut, baseRoom.height, baseRoom.width  - cut)
                self.rooms.append(room)
                doorPos = random.randint(baseRoom.y+1, baseRoom.y + baseRoom.height - 1)
                self.doors[(doorPos, baseRoom.x + cut)] = Door(self.game, doorPos, baseRoom.x + cut)

            # Remove the original room, because it's now two rooms.
            self.rooms.remove(baseRoom)

    def generateFrontDoor(self):
        """Create the front door"""
        pass

    def generateDoors(self):
        """Make the doors for the house"""
        self.generateFrontDoor()

    def createHouse(self, y, x):
        """Actually builds the house, regardless of if it fits or not"""
        # Build the walls..
        for (y1, x1) in self.walls:
            self.game.walls[(y+y1), (x+x1)] = Wall()

        # Floors..
        for (y1, x1) in self.decorations:
            self.game.decorations[(y+y1), (x+x1)] = self.decorations[y1, x1]

        # Inner walls..
        for room in self.rooms:
            (yRoom, xRoom) = (room.y, room.x)
            for (y1, x1) in room.walls:
                self.game.walls[(y + yRoom + y1), (x + xRoom + x1)] = Wall()

        # Doors..
        for (y1, x1) in self.doors:
            # If it rests at an intersection of three walls, move the door.
            # This is the ugliest line in history. Along with the other condition.
            if ((y + y1-1, x + x1) in self.game.walls and (y + y1+1, x + x1) in self.game.walls) and ((y + y1, x + x1+1) in self.game.walls or (y + y1, x + x1-1) in self.game.walls):
                y1 -= 1
            elif ((y + y1, x + x1-1) in self.game.walls and (y + y1, x + x1+1) in self.game.walls) and  ((y + y1+1, x + x1) in self.game.walls or (y + y1-1, x + x1) in self.game.walls):
                x1 -= 1
            # Remove any walls that happen to be hanging around where they shouldn't be
            try:
                wall = self.game.walls[(y + y1, x + x1)]
                del self.game.walls[(y + y1, x + x1)]
            except:
                # No door!
                pass
            self.game.doors[(y1 + y, x1 + x)] = Door(self.game, y1 + y, x1 + x)

    def area(self):
        """Returns the total area required to place house."""
        return self.width * self.height

#### PLAYER

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

        for npc in self.game.npcs:
            if (npc.y, npc.x) == (candidateY, candidateX):
                return True

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
        if (self.x < 0):
            self.x = 0
            moved = False
        elif (self.x >= Game.MAPWIDTH):
            self.x = Game.MAPWIDTH - 1
            moved = False

        if (self.y < 0):
            self.y = 0
            moved = False
        elif (self.y >= Game.MAPHEIGHT):
            self.y = Game.MAPHEIGHT - 1
            moved = False

        return moved

##### NPCS

class NPC(object):
    """Super class for all NPCs"""
    def __init__(self, game, y, x):
        """Initialise the player object"""
        self.x = x
        self.y = y
        self.character = '@'
        self.game = game
        self.colour = curses.color_pair(5)

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
