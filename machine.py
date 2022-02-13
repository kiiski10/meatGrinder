import os, time, pygame
from pytmx import load_pygame
import utilities
import animation

"""
	TODO:
	- make better location system for fighters in production lines
	- load & render sprites for machines properly
"""

APP_PATH = os.path.dirname(os.path.realpath(__file__)) + os.sep
machineTiles = load_pygame(os.path.join(APP_PATH, "tiles", "factory", "machines.tmx"))

class Machine(pygame.sprite.Sprite):
	def __init__(self, mountedOn):
		print("machine init")
		pygame.sprite.Sprite.__init__(self)
		self.image = machineTiles.get_tile_image(0, animation.ANIM_MAPPING["machine"]["gear"], 0)
		self.rect = self.image.get_rect()
		self.subject = None
		self.active = True
		self.state = "WAITING"
		self.mountedOn = mountedOn # factory lines section instance
		self.rect.center = utilities.tilePosToScreenPos(48, self.mountedOn.tilePos)
		self.lastInput = None
		self.level = 1
		self.processTime = 30
		self.processStarted = False

	def output(self):
		pos = self.mountedOn.tilePos
		for s in self.mountedOn.prodLine.neighboringSections(pos):
			if s.tilePos != self.lastInput:
				return(s)
		raise Exception("No output found for machine at {}".format(pos))

	def step(self):
		if self.active:
			if self.state == "WAITING":
				fighterQue = self.mountedOn.prodLine.fightersAt(
					self.mountedOn.tilePos
				)
				if len(fighterQue):
					self.subject = fighterQue[0]
					self.state = "PROCESSING"
					self.subject.state = "IN_MACHINE"
					self.processStarted = self.mountedOn.prodLine.stats["step"]
					self.lastInput = self.subject.prodLineLastSections[-2]

			elif self.state == "PROCESSING":
				if self.mountedOn.prodLine.stats["step"] - self.processStarted > self.processTime:
					self.processStarted = False
					self.state = "OUTPUT"

			elif self.state == "OUTPUT":
				outputQue = self.mountedOn.prodLine.fightersAt(
					self.output().tilePos
				)
				if len(outputQue) < 1:
					fighter = self.subject
					fighter.state = utilities.tilePosId(self.output().tilePos)
					fighter.rect.center = utilities.tilePosToScreenPos(48, self.output().tilePos)
					fighter.timeStamps["move"] = self.mountedOn.prodLine.stats["step"]
					fighter.prodLineLastSections.append(self.output().tilePos)

				subjects = self.mountedOn.prodLine.fightersAt(
					self.mountedOn.tilePos
				)
				if len(subjects) < 1:
				 	self.state = "WAITING"
