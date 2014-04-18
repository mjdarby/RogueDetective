# Our entities, the NPCs and Player.

# Our imports
from enums import Direction, Gender

from plan import Plan

from constants import Constants

from behaviours import DefaultBehaviour, Dead

class Entity(object):
    """The base entity object, for players and NPCs"""
    def __init__(self, game):
        self.x = 0
        self.y = 15
        self.character = '@'
        self.game = game

    def checkObstruction(self, direction = None, steps = 1):
        """Returns true if moving in the given direction isn't allowed"""
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

        for police in self.game.police:
            if (police.y, police.x) == (candidateY, candidateX):
                return True

        if (self.game.player.y, self.game.player.x) == (candidateY, candidateX):
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
        """Actually move the entity"""
        if direction == Direction.UP:
            self.y -= steps
        elif direction == Direction.DOWN:
            self.y += steps
        elif direction == Direction.LEFT:
            self.x -= steps
        elif direction == Direction.RIGHT:
            self.x += steps

    def attemptMove(self, direction):
        """Move the entity one unit in the specified direction, if allowed"""
        moved = True

        # Don't move if bumping in to a wall, door, fence..
        if not self.checkObstruction(direction, 1):
            self.move(direction)
        else:
            moved = False

        # If it was a fence, let them try and jump it if there's nothing left
        # Only players should be able to do this though.
        if self.checkForFence(direction, 1) and not moved and type(self) is Player:
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

        # Bounce them back if they've walked off the terminal!
        if (self.x < 0):
            self.x = 0
            moved = False
        elif (self.x >= Constants.MAPWIDTH):
            self.x = Constants.MAPWIDTH - 1
            moved = False

        if (self.y < 0):
            self.y = 0
            moved = False
        elif (self.y >= Constants.MAPHEIGHT):
            self.y = Constants.MAPHEIGHT - 1
            moved = False

        return moved

#### PLAYER

class Player(Entity):
    """The player object, containing data such as HP etc."""
    def __init__(self, game):
        """Initialise the player object"""
        super(Player, self).__init__(game)
        self.colour = Constants.COLOUR_RED

    def generateFov(self):
        """Reveals grid squares if they've never been seen before,
        shows the contents of squares if within FoV"""
        # Reset the current FoV
        for tile in self.game.tiles:
            tile = self.game.tiles[tile]
            tile.visible = False

        # Start the shadowcast for each octact
        octants = 8 # This is constant naming gone mad.
        for octant in range(octants):
            self.shadowcast(self.y, self.x, 1, Constants.GAMEWIDTH, 1.0, 0.0, octant)

    def shadowcast(self, oY, oX, startRow, rows, startSlope, endSlope, octant):
        """Calculates the FOV for one octant of the shadowcasting algorithm"""
        # Set up the transformation values for the octant
        dX = dY = 0
        rowY = rowX = offsetY = offsetX = 1
        xSlope = True
        if octant == 0 or octant == 5:
            dY = 1
            dX = -1
            rowX = 0
            offsetY = 0
        elif octant == 1 or octant == 4:
            dY = 1
            dX = 1
            rowX = 0
            offsetY = 0
        elif octant == 2 or octant == 7:
            dY = 1
            dX = 1
            offsetX = 0
            rowY = 0
            xSlope = False
        elif octant == 3 or octant == 6:
            dY = -1
            dX = 1
            offsetX = 0
            rowY = 0
            xSlope = False

        if octant == 5 or octant == 4:
            dY = -dY
        elif octant == 6 or octant == 7:
            dX = -dX

        # Iterate across each row and column
        for row in range(startRow, rows):
            if startSlope <= endSlope:
                break
            blocked = False
            lastRightSlope = 0
            for column in range(row+1):
                # Here, we do the hard bit: Finding the right
                # tile that we're considering, deciding if it's
                # in the current scan's FoV, starting child
                # scans and adjusting the start slope.

                if startSlope <= endSlope:
                    break

                # Find the target tile.
                targetY = oY
                targetX = oX
                offset = row - column
                targetY -= dY * rowY * row - dY * offsetY * offset
                targetX += dX * offsetX * offset - dX * rowX * row

                # Determine if it's inside the cone we're considering.
                leftSlope  = ((targetX + (0.5 * dX)) - oX) / \
                             ((targetY + (0.5 * dY)) - oY)
                rightSlope = ((targetX - (0.5 * dX)) - oX) / \
                             ((targetY - (0.5 * dY)) - oY)
                if not xSlope:
                    leftSlope  = 1 / leftSlope
                    rightSlope = 1 / rightSlope

                leftSlope = abs(leftSlope)
                rightSlope = abs(rightSlope)

                if startSlope < rightSlope:
                    continue
                if endSlope > leftSlope:
                    break

                # Light up the tile if we got this far.
                if (targetY, targetX) in self.game.tiles:
                    tile = self.game.tiles[(targetY, targetX)]
                    tile.visible = True
                    tile.seen = True

                    doorClosed = (targetY, targetX) in self.game.doors and \
                                 self.game.doors[(targetY, targetX)].closed

                    if (targetY, targetX) in self.game.walls or doorClosed:
                        # Start child scan if not previously blocked
                        if not blocked:
                            self.shadowcast(self.y, self.x, row+1, \
                                            Constants.GAMEWIDTH - row, \
                                            startSlope, leftSlope, octant)
                        lastRightSlope = rightSlope
                        blocked = True
                    elif blocked: # If we were blocked, but aren't now..
                        # We could be clever and work out the slope and stuff.. But
                        # why bother when we already have it from the last loop?
                        startSlope = lastRightSlope
                        blocked = False
            if blocked: # If the last block in the row scan was a blocker, we stop.
                break

##### NPCS
class NPC(Entity):
    """Super class for all NPCs"""
    def __init__(self, game, y, x):
        """Initialise the player object"""
        super(NPC, self).__init__(game)
        self.y = y
        self.x = x
        self.colour = Constants.COLOUR_WHITE
        self.path = []
        self.square = None
        self.plan = Plan(self)
        self.currentBehaviour = DefaultBehaviour(self)
        self.alive = True
        self.killer = False

        # Fluffy, plot stuff
        self.name = "Dave"
        self.gender = Gender.MALE
        self.description = "very Davelike"

        # Emotions and states
        # TODO: Something with this?
        self.scared = False
        self.answeringDoor = False

    def die(self):
        self.alive = False
        self.character = '%'
        self.currentBehaviour = Dead(self)

    def isAtHome(self):
        # If we need to know that the NPC is at home, regardless of their
        # plan
        if self.square:
            isInX = (self.x > self.square.houseXOffset and
                     self.x < self.square.houseXOffset + self.square.house.width)
            isInY = (self.y > self.square.houseYOffset and
                     self.y < self.square.houseYOffset + self.square.house.height)
            return isInX and isInY

    def update(self):
        """If the NPC is alive, carry out their Plan and Behavaiour"""
        if self.alive:
            # Move randomly, or sometimes actually pick a place to go and go there!
            # If we have a plan and we're not otherwise occupied (to do), execute it
            self.plan.checkForAndExecutePlanEntry()

            # Once we've decided on a plan (or have no plan), the NPC should first
            # go to anywhere they're planning on being before performing their 
            # status action.

            if self.path and self.alive:
                (nextY, nextX) = self.path[0]
                # The algorithm will have avoided walls and fences,
                # so the only obstructions will be the player, doors and NPCs
                blockedByEntity = False
                blockedByDoor = False
                # Check for player..
                if (self.game.player.y, self.game.player.x) == (nextY, nextX):
                    blockedByEntity = True
                # Check for NPC..
                if Constants.NPC_ON_NPC_COLLISIONS:
                    for npc in self.game.npcs:
                        if npc is not self:
                            if (npc.y, npc.x) == (nextY, nextX):
                                blockedByEntity = True
                # Check for Door..
                if (nextY, nextX) in self.game.doors:
                    door = self.game.doors[(nextY, nextX)]
                    if door.closed:
                        blockedByDoor = True
                        door.npcOpen()
                if (not blockedByEntity) and (not blockedByDoor):
                    (self.y, self.x) = (nextY, nextX)
                    self.path.pop(0)
            else:
                if Constants.PATHFINDING_DEBUG:
                    randnum = random.randint(1, 30)
                    if randnum == 25:
                        targetX = targetY = 0
                        while True:
                            targetX = random.randint(1, Constants.MAPWIDTH)
                            targetY = random.randint(1, Constants.MAPHEIGHT)
                            if (targetY, targetX) not in self.game.walls:
                                break
                        self.path = self.findPath(targetY, targetX)
                self.currentBehaviour.execute()

    def findPath(self, targetY, targetX):
        """A big ol' ripoff of the A* algorithm"""
        def sld(y1, x1, y2, x2):
            """Using Euclidean distance as the heuristic"""
            return ((y1-y2) ** 2) + ((x1-x2) ** 2)

        def manhattan(y1, x1, y2, x2):
            """Using Manhattan distance as the heuristic"""
            return (abs(y1 - y2) + abs(x1 - x2))

        def nextCurrent(openSet):
            bestNode = (1,1)
            bestScore = None
            nodeSet = { node: f_score[node] for node in openSet}
            bestNode = min(nodeSet, key=nodeSet.get)
            return bestNode

        def spaceObstructed(y, x, game):
            wallObstruction = (y, x) in game.walls

            # This line WILL cause pathfinding failures if the character is
            # currently inside a fenced area or is attempting to pathfind into
            # one.
            fenceObstruction = (y, x) in game.fences
            #fenceObstruction = False
            return wallObstruction or fenceObstruction

        def returnNeighbours(node, game):
            # Return a list of nodes that aren't walls basically
            neighbours = []
            for nX in [-1, 1]:
                if not spaceObstructed(node[0], node[1] + nX, game):
                    neighbours.append((node[0], node[1] + nX))
                if not spaceObstructed(node[0] + nX, node[1], game):
                    neighbours.append((node[0] + nX, node[1]))
            return neighbours

        def reconstructPath(current):
            if current in came_from:
                rest = reconstructPath(came_from[current])
                rest.append(current)
                return rest
            else:
                return [current,]

        x = self.x
        y = self.y
        goal = (targetY, targetX)
        closedSet = []
        openSet = [(y,x)]
        came_from = {}

        g_score = {}
        f_score = {}
        g_score[(y,x)] = 0
        adjustment = Constants.PATHFINDING_HEURISTIC_ADJUSTMENT
        heuristicScore = manhattan(y, x, targetY, targetX) * adjustment
        f_score[(y,x)] = g_score[(y,x)] + heuristicScore

        count = 100000

        while openSet and count > 0:
            count -= 1
            current = nextCurrent(openSet)
            if current == (targetY, targetX):
                return reconstructPath(current)

            openSet.remove(current)
            closedSet.append(current)
            for neighbour in returnNeighbours(current, self.game):
                if neighbour in closedSet:
                    continue
                tentative_g_score = g_score[current] + 1
                nG_score = -1
                try:
                    nG_score = g_score[neighbour]
                except:
                    pass
                if (neighbour not in openSet or 
                    tentative_g_score < nG_score):
                    came_from[neighbour] = current
                    g_score[neighbour] = tentative_g_score
                    f_score[neighbour] = g_score[neighbour] + sld(neighbour[0], neighbour[1], goal[0], goal[1])
                    if neighbour not in openSet:
                        openSet.append(neighbour)
        return False

    def getDescription(self):
        "Returns the description, modifying it for special cases"
        description = self.description
        if not self.alive:
            description += ". " + ("He" if self.gender == Gender.MALE
                                  else "She") + "'s seen better days."
        return description


class Police(NPC):
    def __init__(self, game, y, x):
        super(Police, self).__init__(game, y, x)
        self.colour = Constants.COLOUR_BLUE
