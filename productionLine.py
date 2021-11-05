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

		for section in self.line:
			pos = self.line[section].tilePos
			posString = "{}x{}".format(pos[0], pos[1])

			# add connections
			for x, y in self.neighboringSections(pos):
				if self.isNextToLine([x, y]):
					print("  is connected to: {}x{}".format(x, y))
					self.line[posString].connections.append([x, y])

					pygame.draw.line(
						self.debugLayer,
						[42, 132, 245],
						utilities.tilePosToScreenPos(48, self.line[posString].tilePos),
						utilities.tilePosToScreenPos(48, [x, y]),
						5
					)


	def neighboringSections(self, pos):
		neighbors = []
		posString = utilities.tilePosId(pos)
		for x, y in [[-1, 0], [1, 0], [0, -1], [0, 1]]:
			xx = self.line[posString].tilePos[0] + x
			yy = self.line[posString].tilePos[1] + y
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
