# Plans and plan accessories (PlanEntries)

# Our imports
from enums import Status

class Plan(object):
    """Describes an NPC's schedule throughout the game day"""
    class PlanEntry(object):
        """Individual entry in the NPC plan, superclass for
        other entries. Override action function to provide actual
        logic"""
        def __init__(self, npc):
            super(Plan.PlanEntry, self).__init__()
            self.npc = npc
            self.shouldReschedule = False
            self.rescheduleTime = (0, 0) # In (hours, minutes) from the
                                         # time of rescheduling
        def action(self):
            return True

    class VisitNeighbour(PlanEntry):
        """Triggers a path-finding event to the specified square index"""
        def __init__(self, npc, square):
            super(Plan.VisitNeighbour, self).__init__(npc)
            self.square = npc.game.squares[square]

        def action(self):
            house = self.square.house
            # This takes them to just inside the door.
            targetY = self.square.y + self.square.houseYOffset + house.frontDoorPos[0] - 1
            targetX = self.square.x + self.square.houseXOffset + house.frontDoorPos[1]
            self.npc.path = self.npc.findPath(targetY, targetX)
            self.npc.status = Status.VISITING_HOUSE
            self.npc.currentlyVisitingHouse = self.square.house

            # TODO: Some sort of 'don't leave the house' flag, I guess
            return True

    def __init__(self, npc):
        super(Plan, self).__init__()
        self.npc = npc
        self.planEntries = dict() # (hour, minute) -> PlanEntry

    def addPlanEntry(self, hour, minute, plan):
        """Abstraction for adding PlanEntries to the plan"""
        self.planEntries[(hour, minute)] = plan

    def checkForAndExecutePlanEntry(self):
        """Also removes the PlanEntry from the dict to avoid repeating it"""
        hour = self.npc.game.hour
        minute = self.npc.game.minute
        if (hour, minute) in self.planEntries:
            planEntry = self.planEntries[(hour, minute)]
            actionSuccessful = planEntry.action()
            if (not actionSuccessful) and planEntry.shouldReschedule:
                # Should write helper functions for adding times,
                # but for now..
                (newHour, newMinute) = (hour + planEntry.rescheduleTime[0],
                                        minute + planEntry.rescheduleTime[1])
                while newMinute >= 60:
                    newHour += 1
                    newMinute -= 60
                while newHour >= 24:
                    newHour -= 24
                self.planEntries[(newHour, newMinute)] = planEntry
            elif actionSuccessful:
                del self.planEntries[(hour, minute)]


