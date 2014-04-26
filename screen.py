# Screen helper functions

import textwrap
from constants import Constants

def printDialogueChoices(screen, player, choices, npcName = None):
    choices = zip(range(0, len(choices)), choices)
    choices = [str(idx+1) + ") " + choice for (idx, choice) in choices]
    text = ("\n".join(choices)).splitlines()
    if npcName:
        header = "Talking to " + npcName
        text.insert(0, '-' * Constants.DESC_BOX_WIDTH)
        text.insert(0, header)
    printBox(screen, text, False)
    moveCursorToPlayer(screen, player)

def moveCursorToPlayer(screen, player):
    """Moves the cursor to the player. Duh."""
    # Make sure the cursor follows the players y/x co-ord
    # when he's near the minimum values of each
    cursorX = min(Constants.GAMEWIDTH // 2 + 1, player.x + 1)
    cursorY = min(Constants.GAMEHEIGHT // 2 + 1, player.y + 1)

    # Make sure the cursor follows the players y/x co-ord +
    # the max camera range when he's near the maximum values
    # of each
    maxCameraX = Constants.MAPWIDTH - Constants.GAMEWIDTH // 2 - 1
    maxCameraY = Constants.MAPHEIGHT - Constants.GAMEHEIGHT // 2  - 1
    if player.x > maxCameraX:
        offset = player.x - maxCameraX + Constants.GAMEWIDTH // 2
        cursorX = offset
    if player.y > maxCameraY:
        offset = player.y - maxCameraY + Constants.GAMEHEIGHT // 2 + 1
        cursorY = offset
    screen.move(cursorY, cursorX)

def moveCursorToEntity(screen, player, entity):
    """Moves the cursor to an entity"""
    # It's easier to move the cursor to the player, and then move
    # it to the NPC relative to the player.
    moveCursorToPlayer(screen, player)
    (y, x) = screen.getyx()
    y += entity.y - player.y
    x += entity.x - player.x
    # It may transpire that we're somehow trying to do
    # this for an offscreen dude. Block it for now.
    try:
        screen.move(y, x)
    except:
        pass

def printBox(screen, paragraphs, anyKeyPrompt=False):
    """Prints a box on the screen. Caller is responsible for clearing screen afterwards."""
    # Prepare the text!
    wrappedText = []
    for paragraph in paragraphs:
        wrappedText += textwrap.wrap(paragraph, Constants.DESC_BOX_WIDTH)
    # Print the top border
    topBottomBorder = "+" + (Constants.DESC_BOX_WIDTH * "-") + "+"
    screen.addstr(0, 0, topBottomBorder)
    lineNo = 1
    # Print the actual text
    for line in wrappedText:
        printedLine = "|" + line.ljust(Constants.DESC_BOX_WIDTH) + "|"
        screen.addstr(lineNo, 0, printedLine)
        lineNo += 1
    if anyKeyPrompt:
        screen.addstr(lineNo, 0,
                           "|" +
                           "<Press any key to continue>".ljust(Constants.DESC_BOX_WIDTH) +
                           "|")
        lineNo += 1
    # Bottom border
    screen.addstr(lineNo, 0, topBottomBorder)
