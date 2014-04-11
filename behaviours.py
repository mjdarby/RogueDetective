# NPC Behaviour functions, grouped together in a handle module!

# Python imports
import random

# Our imports
from enums import Status, Direction

def VisitingHouse(npc):
    """Move randomly, but don't leave the house"""
    # Occasionally decide to move to a new room, otherwise just
    # womble about randomly without leaving.
    moveRoom = random.randint(0, 25) == 24
    house = npc.currentlyVisitingHouse
    if moveRoom:
        randomRoomIdx = random.randint(0, len(house.rooms) - 1)
        room = house.rooms[randomRoomIdx]
        randomX = random.randint(1, room.width - 1)
        randomY = random.randint(1, room.height - 1)
        npc.path = npc.findPath(house.absoluteY + room.y + randomY,
                                house.absoluteX + room.x + randomX)
    else:
        randomDirection = random.randint(1,5)
        while True:
            if randomDirection is not Direction.DOWN:
                break
            else:
                absoluteFrontDoorPos = (house.absoluteY + house.frontDoorPos[0],
                                        house.absoluteX + house.frontDoorPos[1])
                if (npc.y + 1, npc.x) == absoluteFrontDoorPos:
                    randomDirection = random.randint(1,5)
                else:
                    break
        npc.attemptMove(randomDirection)

functions = {}
functions[Status.VISITING_HOUSE] = VisitingHouse
