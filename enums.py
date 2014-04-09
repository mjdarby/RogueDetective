# Our enums

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
    KICK_DOOR = 7
    WAIT = 8

class Status:
    """NPC statuses, help define what NPCs are doing when they are
    otherwise idle (ie. not performing a PlanEntry)"""
    IDLE = 0
    STAYING_HOME = 1
    VISITING_HOUSE = 2

