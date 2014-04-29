# Town stuff, including houses!

# Python imports
import random

# Our imports
from tiles import Wall, Door, Decoration, Fence
from constants import Constants
from entity import NPC

class Town(object):
    """A grid with random edges removed, houses placed on the grid"""

    GRID_SIZE = 20
    ROAD_WIDTH = 3
    ROAD_HEIGHT = 2

    class Square(object):
        """A plot of land owned by an NPC. Contains a house."""
        def __init__(self, game, y, x):
            self.y = y
            self.x = x
            self.game = game
            self.house = None
            self.houseYOffset = 0
            self.houseXOffset = 0
            self.npc = None

        def generateFences(self):
            # Generate the fences
            for y in range(Town.GRID_SIZE):
                if (y + self.y, self.x) not in self.game.walls:
                    self.game.fences[(y + self.y, self.x)] = Fence()
                if (y + self.y, self.x + Town.GRID_SIZE - 1) not in self.game.walls:
                    self.game.fences[(y + self.y, self.x + Town.GRID_SIZE - 1)] = Fence()
            for x in range(Town.GRID_SIZE):
                if (self.y, x + self.x) not in self.game.walls:
                    self.game.fences[(self.y, x + self.x)] = Fence()
                if (self.y + Town.GRID_SIZE - 1, x + self.x) not in self.game.walls \
                   and (self.y + Town.GRID_SIZE -1, x + self.x) not in self.game.doors:
                    self.game.fences[(self.y + Town.GRID_SIZE - 1, x + self.x)] = Fence()

        def generateHouse(self):
            """Actually builds the house and fences"""
            # Generate the building
            house = House(self.game)
            self.house = house
            self.house.number = len(self.game.villagers) + 1
            house.generateLayout(Town.GRID_SIZE, Town.GRID_SIZE)
            yOffset = Town.GRID_SIZE - house.height - 1
            xSpace = Town.GRID_SIZE - house.width - 1
            xOffset = random.randint(0, xSpace)
            house.createHouse(self.y + yOffset, self.x + xOffset)
            self.houseYOffset = yOffset
            self.houseXOffset = xOffset

            self.generateFences()

            # NPC owners! Woohoo! Spawn them inside the house, but not in a wall
            npcYOffset = 0
            npcXOffset = 0
            while (self.y + yOffset + npcYOffset, self.x + xOffset + npcXOffset) in self.game.walls:
                npcYOffset = random.randint(1, house.height - 2)
                npcXOffset = random.randint(1, house.width - 2)
            newNpc = NPC(self.game,
                         self.y + yOffset + npcYOffset,
                         self.x + xOffset + npcXOffset)
            newNpc.square = self
            self.npc = newNpc
            
            self.game.villagers.append(newNpc)
            self.game.npcs.append(newNpc)

        # Finally, add it to the list of squares
            self.game.squares.append(self)

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

    def createRoads(self):
        """Actually make the roads"""
        for (y1, x1) in self.roads:
            self.game.decorations[(self.y + y1), (self.x + x1)] = self.roads[y1, x1]

    def generateRoads(self):
        """Create roads for given grid square"""
        for y in range(self.height):
            for x in range(self.width):
                square = self.squares[(y,x)]
                # We'd like self.roads to be relative to the Town position, hence
                # the subtractions.
                baseY = square.y - self.y
                baseX = square.x - self.x
                road = Decoration()
                road.character = '#'
                road.colour = Constants.COLOUR_YELLOW
                for roadX in range(Town.GRID_SIZE + Town.ROAD_WIDTH - 1):
                    for width in range(Town.ROAD_WIDTH):
                        self.roads[(baseY + roadX, baseX + Town.GRID_SIZE + width)] = road
                for roadX in range(Town.GRID_SIZE + Town.ROAD_HEIGHT):
                    for width in range(Town.ROAD_HEIGHT):
                        self.roads[(baseY + Town.GRID_SIZE + width, baseX + roadX)] = road
        self.createRoads()

    def generateGrid(self):
        """Generate the grids + roads + houses"""
        for y in range(self.height):
            squareY = y * (Town.GRID_SIZE + Town.ROAD_HEIGHT) + self.y
            for x in range(self.width):
                squareX = x * (Town.GRID_SIZE + Town.ROAD_WIDTH) + self.x
                # Make a square
                self.squares[(y,x)] = Town.Square(self.game, squareY, squareX)
                # For now, put a house in the square
                self.squares[(y,x)].generateHouse()
        self.generateRoads()

class Building(object):
    """Buildings are procedurally generated constructs"""
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
        self.absoluteX = 0
        self.absoluteY = 0
        self.width = 0
        self.height = 0
        self.rooms = []
        self.walls = dict()
        self.decorations = dict()
        self.doors = dict()
        self.frontDoorPos = (0, 0)
        self.minNumberOfRooms = 1
        self.maxNumberOfRooms = 4
        self.game = game

    def generateLayout(self, maxHeight, maxWidth):
        # Create the outer walls
        self.generateWalls(maxHeight, maxWidth)

        # Create rooms
        self.generateRooms()

        # If the house isn't fully navigable, regenerate it until it is
        while not self.floodFill():
            del self.rooms[:]
            self.doors.clear()
            self.walls.clear()
            self.generateWalls(maxHeight, maxWidth)
            self.generateRooms()

        # Create doors
        self.generateDoors()

    def generateWalls(self, maxHeight, maxWidth):
        """Create the outer walls of the house"""
        self.width = random.randint(House.MINIMUM_WIDTH, maxWidth) - 1
        self.height = random.randint(House.MINIMUM_WIDTH, maxHeight) - 1
        for x in range(self.width):
            self.walls[(0, x)] = Wall()
            self.walls[(self.height, x)] = Wall()
            # Might as well do the floors too, while we're here
            for y in range(self.height):
                decoration = Decoration()
                decoration.character = '.'
                decoration.colour = Constants.COLOUR_WHITE
                self.decorations[(y, x)] = decoration
        for y in range(self.height):
            self.walls[(y, 0)] = Wall()
            self.walls[(y, self.width)] = Wall()

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

    def floodFill(self):
        """Returns true if every square of the house is reachable from the top-left space"""
        def _floodFill(y, x, visited):
            if x >= 0 and x < self.width and y >= 0 and y < self.height:
                if visited[(y,x)]:
                    return

                visited[(y,x)] = True
                _floodFill(y-1, x, visited)
                _floodFill(y, x-1, visited)
                _floodFill(y+1, x, visited)
                _floodFill(y, x+1, visited)

        visited = {}

        for y in range(self.height):
            for x in range(self.width):
                visited[(y,x)] = False
                if ((y, x) in self.walls) and ((y, x) not in self.doors):
                    visited[(y,x)] = True

        _floodFill(1, 1, visited)

        for y in range(self.height):
            for x in range(self.width):
                if not visited[(y,x)]:
                    return False

        return True

    def generateRooms(self):
        """Create the rooms by repeated partitioning"""
        # How many partitions should we make, excluding the first?
        numPartitions = random.randint(self.minNumberOfRooms, self.maxNumberOfRooms) - 1
        if numPartitions > 0:
            self.generateFirstPartition()
            numPartitions -= 1
        else:
            room = House.Room(0, 0, self.height, self.width)
            self.rooms.append(room)

        for _ in range(numPartitions):
            # Get a random room, which we'll partition just like the first room
            attempts = 10
            baseRoom = random.choice(self.rooms)
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

            # Create the two rooms and put a door in connecting the two new rooms
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
        # Now solidify the walls
        for room in self.rooms:
            (yRoom, xRoom) = (room.y, room.x)
            for (y1, x1) in room.walls:
                self.walls[(yRoom + y1), (xRoom + x1)] = Wall()

    def generateFrontDoor(self):
        """Create the front door"""
        # Actual door creation
        doorX = random.randint(1,self.width-1)
        if (self.height-1, doorX) in self.walls:
            doorX -= 1
        self.doors[(self.height, doorX)] = Door(self.game, self.height, doorX)
        self.doors[(self.height, doorX)].locked = Constants.FRONT_DOORS_LOCKED
        self.frontDoorPos = (self.height, doorX)

        # The house number sign
        sign = self.walls[(self.height, doorX - 1)]
        sign.character = str(self.number)
        sign.colour = Constants.COLOUR_GREEN

    def generateDoors(self):
        """Make the doors for the house"""
        self.generateFrontDoor()

    def createHouse(self, y, x):
        """Actually builds the house, regardless of if it fits or not"""
        self.absoluteX = x
        self.absoluteY = y
        # Build the walls..
        for (y1, x1) in self.walls:
            self.game.walls[(y+y1), (x+x1)] = self.walls[(y1, x1)]

        # Floors..
        for (y1, x1) in self.decorations:
            self.game.decorations[(y+y1), (x+x1)] = self.decorations[y1, x1]

        # Doors..
        for (y1, x1) in self.doors:
            # If it rests at an intersection of three walls, move the door.
            # This is the ugliest line in history. Along with the other condition.
            (oY, oX) = (y1, x1)
            if ((y + y1-1, x + x1) in self.game.walls and (y + y1+1, x + x1) in self.game.walls) and ((y + y1, x + x1+1) in self.game.walls or (y + y1, x + x1-1) in self.game.walls):
                y1 -= 1
            elif ((y + y1, x + x1-1) in self.game.walls and (y + y1, x + x1+1) in self.game.walls) and  ((y + y1+1, x + x1) in self.game.walls or (y + y1-1, x + x1) in self.game.walls):
                x1 -= 1
            # Remove any walls that happen to be hanging around where they shouldn't be
            try:
                wall = self.game.walls[(y + y1, x + x1)]
                del self.game.walls[(y + y1, x + x1)]
            except:
                # No wall!
                pass
            door = Door(self.game, y1 + y, x1 + x)
            door.locked = self.doors[(oY, oX)].locked
            self.game.doors[(y1 + y, x1 + x)] = door

    def area(self):
        """Returns the total area required to place house."""
        return self.width * self.height


class House(Building):
    """Houses are procedurally generated constructs in which NPCs live."""
    def __init__(self, game):
        super(House, self).__init__(game)


