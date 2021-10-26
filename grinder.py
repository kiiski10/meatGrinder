import pygame

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

	def renderBlood(self):
		for b in self.bloodDrops:
			bloodSize = 10
			drop = pygame.Rect((0,0), (bloodSize, bloodSize))
			lifeTime = self.stats["step"] - b["spawnOnFrame"]
			x = b["pos"][0]
			y = b["pos"][1]

			drop.center = [
				x + lifeTime,
				y + lifeTime
			]

			if lifeTime > 100:
				targetLayer = self.bloodNcorpseLayer
				color = (100,50,0)
				self.bloodDrops.remove(b)
			else:
				targetLayer = self.bloodDropLayer
				color = (200,100,0)

			pygame.draw.rect(
				targetLayer,
				color,
				drop,
				0
			)

	def render(self, displaySurf):
		# render gore
		self.renderBlood()
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

		# render debug layer
		pygame.Surface.blit(
			displaySurf,
			self.debugLayer,
			[0, 0]
		)
		# renderFighters
		for f in self.fighters:
			pygame.Surface.blit(
				displaySurf,
				f.image,
				f.rect.center
			)
