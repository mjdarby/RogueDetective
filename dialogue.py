# This stores all the dialogue related stuff

import screen

class Dialogue(object):
  """Stores the dialogue tree for an individual NPC"""
  def __init__(self, npc):
    super(Dialogue, self).__init__()
    self.npc = npc
    self.game = npc.game
    self.root = None
    self.currentNode = None

  def setRootNode(self, node):
    self.root = node

  def resetCurrentNode(self):
    self.currentNode = self.root

  def beginConversation(self):
      self.resetCurrentNode()
      self.runNextNode()

  def runNextNode(self):
      if self.currentNode is None:
        return
      # Grab all the DialogueChoices that should be shown
      availableChoices = []

      for (choice, predicate, child) in self.currentNode.choices:
        if predicate is not None:
          if predicate():
            availableChoices.append((choice, child))
        else:
          availableChoices.append((choice, child))

      npcName = None
      if self.game.player.notebook.isNpcKnown(self.npc):
        npcName = self.npc.firstName + " " + self.npc.lastName

      choiceTexts = [choice.choiceText for (choice, child) in availableChoices]
      screen.printDialogueChoices(self.game.screen, self.game.player, 
                                  choiceTexts, npcName)
      choiceIdx = self.game.getDialogueChoice(len(choiceTexts)) - 1
      self.game.draw()
      (choice, nextNode) = availableChoices[choiceIdx]
      response = ""
      response += choice.response

      if choice.responseFunction is not None:
        response = choice.responseFunction(self.npc, response)
      self.game.printDescription(response, npcName)
      self.currentNode = nextNode
      self.runNextNode()

class DialogueNode(object):
  """A single node of the dialogue tree"""
  def __init__(self):
    super(DialogueNode, self).__init__()
    self.choices = []

  def addChoice(self, choice, choicePredicate=None, childNode=None):
    self.choices.append((choice, choicePredicate, childNode))

class DialogueChoice(object):
  """Stores the choice/function pair"""
  def __init__(self, choiceText, response, responseFunction=None):
    super(DialogueChoice, self).__init__()
    self.choiceText = choiceText
    self.response = response
    self.responseFunction = responseFunction

  def callResponseFunction(self, npcArgument, response):
    if responseFunction is not None:
      self.responseFunction(npcArgument, response)