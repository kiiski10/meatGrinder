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
		print(self.image)
		self.subject = None
		self.active = True
		self.state = "WAITING"
		self.mountedOn = mountedOn # factory lines section instance
		self.rect.center = utilities.tilePosToScreenPos(48, self.mountedOn.tilePos)
		print(self.rect.center)
		self.lastInput = None
		self.level = 1
		self.processTime = 3
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
					self.state = "PROCESSING"
					self.processStarted = time.time()
					self.subject = fighterQue[0]
					self.subject.state = "IN_MACHINE"
					self.lastInput = self.subject.prodLineLastSections[-2]
					print("""
	last sects: {}
	last input: {}
	mount point:{}
	output:     {}
						""".format(
							self.subject.prodLineLastSections,
							self.lastInput,
							self.mountedOn.tilePos,
							self.output().tilePos
						)
					)
					time.sleep(1)

			elif self.state == "PROCESSING":
				if time.time() - self.processStarted > self.processTime:
					self.processStarted = False
					self.state = "OUTPUT"

			elif self.state == "OUTPUT":
				outputQue = self.mountedOn.prodLine.fightersAt(
					self.output().tilePos
				)
				if len(outputQue) < 1:
					self.subject.state = "IDLE"
					if not self.mountedOn.prodLine.fightersAt(
						self.mountedOn.tilePos
					):
						self.state = "WAITING"
						print("move fighter to {}".format(self.output().tilePos))
						self.subject.prodLineLastSections.append(self.output().tilePos)
						self.subject.rect.center = utilities.tilePosToScreenPos(48, self.output().tilePos)
				else:
					print("{} fighters blocking: at {}: {}".format(self.mountedOn.tilePos, self.output().tilePos, len(outputQue)))
					print("blocker #1: {} state:{}".format(utilities.screenPosToTilePos(48, outputQue[0].rect.center), outputQue[0].state))
