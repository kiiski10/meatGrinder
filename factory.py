import pygame, random, os
from pytmx import load_pygame
from productionLine import ProductionLine
from character import Fighter
import utilities

APP_PATH = os.path.dirname(os.path.realpath(__file__)) + os.sep


class Factory:
	def __init__(self, team, grinder):
		print("factory init")
		self.fighterSprites = pygame.sprite.Group()
		self.team = team
		self.stats = {
			"step": 0
		}
		self.grinder = grinder
		self.fighters = []
		self.tileMap = load_pygame(os.path.join(APP_PATH, "tiles", "factory", "factory.tmx"))
		self.surface = pygame.Surface((480, 480))
		_surfsize = self.surface.get_rect().size
		self.arrowSurface = pygame.Surface(_surfsize)
		self.lineSurface = pygame.Surface(_surfsize)
		self.machineSurface = pygame.Surface(_surfsize)
		self.fighterSurface = pygame.Surface(_surfsize)
		self.arrowSurface.set_colorkey((255, 0, 255))
		self.lineSurface.set_colorkey((255, 0, 255))
		self.machineSurface.set_colorkey((255, 0, 255))
		self.fighterSurface.set_colorkey((255, 0, 255))
		self.inGate = self.getTilesBylayer("fighterIn")[0]
		self.prodLine = ProductionLine(self, self.inGate)

	def getTilesBylayer(self, layerName):
		tileCoords = []
		for x, y, gid, in self.tileMap.get_layer_by_name(layerName):
			if gid:
				tileCoords.append((x, y))
		return tileCoords


	def step(self):
		self.stats["step"] += 1
		self.prodLine.step()

		if not random.randint(0, 20):
			pos = self.inGate
			if self.prodLine.hasRoom(pos):
				print("add fighter", pos)
				newFighter = Fighter(
					world=self.grinder,
					team=self.team,
					spawnNr=0,
					speed=2,
					selectedEquipment=[]
				)

				newFighter.rect.topleft = utilities.tilePosToScreenPos(48, pos)
				self.prodLine.line[utilities.tilePosId(pos)].fighters.append(newFighter)
				self.fighterSprites.add(newFighter)


	def drawLayerByName(self, layerName, targetSurface):
		for x, y, gid, in self.tileMap.get_layer_by_name(layerName):
			if gid:
				tile = self.tileMap.get_tile_image_by_gid(gid)
				if tile:
					targetSurface.blit(
						tile,
						(
							x * self.tileMap.tilewidth,
							y * self.tileMap.tileheight
						)
					)

		pygame.Surface.blit(
			self.surface,
			targetSurface,
			[0, 0]
		)

		targetSurface.fill((255, 0 ,255))


	def drawFighters(self):
		self.fighterSurface.fill((255, 0 ,255))

		# fighters on production lines
		self.fighterSprites.draw(self.fighterSurface)

		pygame.Surface.blit(
			self.surface,
			self.fighterSurface,
			[0, 0]
		)


	def render(self):
		self.drawLayerByName("lines", self.lineSurface)
		self.drawLayerByName("machines", self.machineSurface)
		self.drawLayerByName("arrows", self.arrowSurface)
		self.drawFighters()
