# NPC Behaviour functions, grouped together in a handle module!

# Python imports
import random

# Our imports
from enums import Status, Direction

def VisitingHouse(npc):
    """Move randomly, but don't leave the house"""
    # TODO: Occasionally findPath to another room in the house
    randomDirection = random.randint(1,5)
    while True:
        if randomDirection is not Direction.DOWN:
            break
        else:
            house = npc.currentlyVisitingHouse
            absoluteFrontDoorPos = (house.absoluteY + house.frontDoorPos[0],
                                    house.absoluteX + house.frontDoorPos[1])
            if (npc.y + 1, npc.x) == absoluteFrontDoorPos:
                randomDirection = random.randint(1,5)
            else:
                break
    npc.attemptMove(randomDirection)

functions = {}
functions[Status.VISITING_HOUSE] = VisitingHouse
