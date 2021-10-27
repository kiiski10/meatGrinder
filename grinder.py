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
		self.debug = False
		#self.debug = True
		self.teamsFilteredOn = 0
		self.enemiesOf = {}
		for t in self.teams:
			self.enemiesOf[t] = []
		self.stats = {
			"step": 0
		}

	def step(self):
		self.stats["step"] += 1

		if self.stats["step"] - self.teamsFilteredOn > 10:
			self.teamsFilteredOn = self.stats["step"]

			for t in self.teams:
				self.enemiesOf[t] = []

			for t in self.teams:
				self.enemiesOf[t] = self.listEnemies(t)

		for f in self.fighters:
			f.step(self.stats["step"])


	def addBloodDrop(self, pos, dir, damage, color):
		if len(self.bloodDrops) > 500:
			draw = not random.randint(0, 2)
		else:
			draw = True

		if draw:
			self.bloodDrops.append(
				{
					"spiltOnFrame": self.stats["step"],
					"damage": damage,
					"dir": dir,
					"speed": 7,
					"pos": pos,
					"color": color
				}
			)


	def drawBlood(self):
		self.bloodDropLayer.fill((0,0,0))

		for b in self.bloodDrops:
			lifeTime = self.stats["step"] - b["spiltOnFrame"]
			x = b["pos"][0]
			y = b["pos"][1]
			x, y = utilities.angleDistToPos(b["pos"], b["dir"], lifeTime * b["speed"])

			if lifeTime > b["damage"] * 0.5:
				bloodSize = 5
				targetLayer = self.bloodNcorpseLayer
				color = b["color"]
				self.bloodDrops.remove(b)
			else:
				bloodSize = 3
				targetLayer = self.bloodDropLayer
				color = b["color"]

			drop = pygame.Rect((0,0), (bloodSize, bloodSize))
			drop.center = [x, y]

			pygame.draw.rect(
				targetLayer,
				color,
				drop,
				0
			)

		pygame.Surface.blit(
			self.displaySurf,
			self.bloodNcorpseLayer,
			[0, 0]
		)
		pygame.Surface.blit(
			self.displaySurf,
			self.bloodDropLayer,
			[0, 0]
		)

	def listEnemies(self, team):
		return(list(filter(lambda x: x.team["name"] != team, self.fighters)))

	def render(self, displaySurf):
		self.drawBlood()

		# renderFighters
		for f in self.fighters:
			pygame.Surface.blit(
				displaySurf,
				f.image,
				f.rect.center
			)

		# render debug layer
		if self.debug:
			pygame.Surface.blit(
				displaySurf,
				self.debugLayer,
				[0, 0]
			)
