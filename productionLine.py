import pygame
from machine import Machine
import utilities
from equipment import *


class Section:
	def __init__(self, pos):
		#self.image = img
		self.tilePos = pos
		self.machine = None
		self.connections = []


class ProductionLine:
	def __init__(self, factory, inGate):
		print("production line init")
		self.fighters = []
		self.inGate = inGate
		self.factory = factory
		self.debugLayer = pygame.Surface(self.factory.surface.get_rect().size)
		self.debugLayer.set_colorkey((255, 0, 255))
		self.debugLayer.fill((255, 0, 255))
		self.stats = {
			"step": 0
		}

		self.line = {
			utilities.tilePosId(self.inGate): Section(self.inGate),
		}

		for s in self.factory.getTilesByLayer("prodLine"):
			newSection = Section(s)
			self.line[utilities.tilePosId(s)] = newSection

		# add connections
		for section in self.line:
			pos = self.line[section].tilePos
			#print("section in", pos)
			for n in self.neighboringSections(pos):
				posString = utilities.tilePosId(n.tilePos)

				pygame.draw.line(
					self.debugLayer,
					[242, 132, 45],
					utilities.tilePosToScreenPos(48, pos),
					utilities.tilePosToScreenPos(48, n.tilePos),
					5
				)


	def neighboringSections(self, pos):
		neighbors = []
		posString = utilities.tilePosId(pos)
		if posString in self.line:
			for x, y in [[-1, 0], [1, 0], [0, -1], [0, 1]]:
				testKey = utilities.tilePosId((pos[0] + x, pos[1] + y))
				if testKey in self.line:
					n = self.line[testKey]
					neighbors.append(n)

		#print("  is connected to", len(neighbors))
		return(neighbors)


	def addFighter(self, newFighter):
		print("add fighter to factory tile", utilities.screenPosToTilePos(48, newFighter.rect.center))
		self.fighters.append(newFighter)


	def fightersAt(self, pos):
		posString = utilities.tilePosId(pos)
		occupiers = []
		for f in self.fighters:
			if utilities.screenPosToTilePos(48, f.rect.center) == pos:
				occupiers.append(f)
		return(len(occupiers))


	def moveFighters(self):
		for fighter in self.fighters:
			if fighter.state != "INMACHINE":
				pass #print(fighter)

		return([])

	def lineAdvance(self):
		self.moveFighters()


	def step(self):
		self.stats["step"] += 1
		self.lineAdvance()
