from machine import Machine
from equipment import *

class ProductionLine:
	def __init__(self):
		print("production line init")

		self.stats = {
			"step": 0
		}

		self.line = {
			"9x0": {
				"machine": Machine(Sword()),
				"direction": "N",
				"fighters": []
			},
		}


	def hasRoom(self, pos, inPixelFormat=False):
		if inPixelFormat:
			pos = utilities.screenPosToTilePos(48, pos)

		posString = "{:.0f}x{:.0f}".format(pos[0], pos[1])
		if posString in self.line:
			if len(self.line[posString]["fighters"]) < 4:
				#print("part of line has room", posString)
				return(True)
		# 	else:
		# 		print("part of line is full")
		# else:
		# 	print("part of line not found", posString)

		return(False)


	def step(self):
		self.stats["step"] += 1
		self.render()


	def render(self):
		print("line render")
		for p in self.line:
			print(" part:", p)
