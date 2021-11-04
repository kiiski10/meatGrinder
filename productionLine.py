from machine import Machine
import utilities
from equipment import *

class Section:
	def __init__(self, pos):
		self.tilePos = pos
		self.machine = None
		self.direction = "W"
		self.fighters = []
		self.connections = []

class ProductionLine:
	def __init__(self, factory, inGate):
		print("production line init")

		self.inGate = inGate
		self.factory = factory

		self.stats = {
			"step": 0
		}

		self.line = {
			utilities.tilePosId(self.inGate): Section(self.inGate),
		}


	def hasRoom(self, pos):
		posString = utilities.tilePosId(pos)

		if posString in self.line:
			if len(self.line[posString].fighters) < 2:
				print("part of line has room", posString)
				return(True)
			else:
				print("part of line is full")
		else:
			print("part of line not found", posString)

		return(False)


	def step(self):
		self.stats["step"] += 1
