import pygame, random
import utilities

class Grinder:
	def __init__(self, teams, inputs, displaySurf):
		print("grinder init")
		self.displaySurf = displaySurf
		self.debugLayer = pygame.Surface(displaySurf.get_rect().size)
		self.debugLayer.set_colorkey((255, 0, 255))
		self.bloodNcorpseLayer = pygame.Surface(displaySurf.get_rect().size)
		self.bloodNcorpseLayer.set_colorkey((0, 0, 0))
		self.bloodDropLayer = pygame.Surface(displaySurf.get_rect().size)
		self.bloodDropLayer.set_colorkey((0, 0, 0))
		self.inputs = inputs # [{"name": "A", "pos": [x, y], "que": []}]
		self.fighters = []
		self.dead = []
		self.teams = teams
		self.bloodDrops = []

		self.stats = {
			"step": 0
		}

	def step(self):
		self.stats["step"] += 1

		for f in self.fighters:
			f.step(self.stats["step"])


	def addBloodDrop(self, pos, dir, damage):
		self.bloodDrops.append(
			{
				"spiltOnFrame": self.stats["step"],
				"damage": damage,
				"dir": dir,
				"speed": 7,
				"pos": pos
			}
		)


	def drawBlood(self):
		for b in self.bloodDrops:
			lifeTime = self.stats["step"] - b["spiltOnFrame"]
			x = b["pos"][0]
			y = b["pos"][1]
			x, y = utilities.angleDistToPos(b["pos"], b["dir"], lifeTime * b["speed"])

			if lifeTime > b["damage"] * 0.5:
				bloodSize = 7
				targetLayer = self.bloodNcorpseLayer
				color = (250,50,35)
				self.bloodDrops.remove(b)
			else:
				bloodSize = 3
				targetLayer = self.bloodDropLayer
				color = (250,100,70)

			drop = pygame.Rect((0,0), (bloodSize, bloodSize))
			drop.center = [x, y]

			pygame.draw.rect(
				targetLayer,
				color,
				drop,
				0
			)

	def render(self, displaySurf):
		# render gore
		self.drawBlood()
		pygame.Surface.blit(
			displaySurf,
			self.bloodNcorpseLayer,
			[0, 0]
		)
		pygame.Surface.blit(
			displaySurf,
			self.bloodDropLayer,
			[0, 0]
		)
		self.bloodDropLayer.fill((0,0,0))

		# renderFighters
		for f in self.fighters:
			pygame.Surface.blit(
				displaySurf,
				f.image,
				f.rect.center
			)

		# render debug layer
		pygame.Surface.blit(
			displaySurf,
			self.debugLayer,
			[0, 0]
		)
