# NPC Behaviour classes!

# Python imports
import random

# Our imports
from enums import Direction

class Behaviour(object):
    """The base class for NPC behaviours. Behaviours control NPC behaviour
    when they're not pathfinding."""
    def __init__(self, npc):
        super(Behaviour, self).__init__()
        self.npc = npc

    def execute(self):
        """The actual behaviour logic, override me"""
        return True

class DefaultBehaviour(Behaviour):
    """If there's no other behaviour, move randomly"""
    def __init__(self, npc):
        super(DefaultBehaviour, self).__init__(npc)
    
    def execute(self):
        """Move randomly!"""
        self.npc.attemptMove(random.randint(1,5))

class Dead(Behaviour):
    """Do nothing. Seriously, what do you expect a corpse to do?"""
    def __init__(self, npc):
        super(Dead, self).__init__(npc)

    def execute(self):
        self.npc.character = '%'
        return True

class VisitingHouse(Behaviour):
    """Behaviour when visiting a neighbour's house (or indeed, staying in)"""
    def __init__(self, npc, house):
        super(VisitingHouse, self).__init__(npc)
        self.house = house

    def execute(self):
        """Move randomly, but don't leave the house"""
        # Occasionally decide to move to a new room, otherwise just
        # womble about randomly without leaving.
        moveRoom = random.randint(0, 25) == 24
        npc = self.npc
        house = self.house
        if moveRoom:
            room = random.choice(house.rooms)
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
