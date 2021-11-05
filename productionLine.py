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
		self.fighters = []


class ProductionLine:
	def __init__(self, factory, inGate):
		print("production line init")

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
			# TODO: check neighbouring tiles and add connections
			for x, y in [[-1, 0], [1, 0], [0, -1], [0, 1]]:
				xx = s[0] + x
				yy = s[1] + y
				if self.hasRoom([xx, yy]):
					newSection.connections.append([xx, yy])
					pygame.draw.line(
						self.debugLayer,
						[42, 132, 245],
						utilities.tilePosToScreenPos(48, s),
						utilities.tilePosToScreenPos(48, [xx, yy]),
						5
					)
					#print("add connection {}-> {}x{}".format(s, xx, yy))

			if newSection.connections:
				print("connections", s, "->", newSection.connections)
			self.line[utilities.tilePosId(s)] = newSection


	def hasRoom(self, pos):
		posString = utilities.tilePosId(pos)

		if posString in self.line:
			if len(self.line[posString].fighters) < 2:
				#print("part of line has room", posString)
				return(True)
		# 	else:
		# 		print("part of line is full")
		# else:
		# 	print("part of line not found", posString)

		return(False)


	def step(self):
		self.stats["step"] += 1
