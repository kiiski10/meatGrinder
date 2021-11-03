import pygame, random
import utilities
import os
from pytmx import load_pygame

APP_PATH = os.path.dirname(os.path.realpath(__file__)) + os.sep


class Factory:
	def __init__(self, team):
		print("factory init")
		self.tileMap = load_pygame(os.path.join(APP_PATH, "tiles", "factory", "factory.tmx"))
		self.surface = pygame.Surface((500, 500))
		self.staticBackground = pygame.Surface(self.surface.get_rect().size)
		#self.staticBackground.set_colorkey((255, 0, 255))
		self.lineSurface = pygame.Surface(self.surface.get_rect().size)
		#self.lineSurface.set_colorkey((255, 0, 255))
		self.machineSurface = pygame.Surface(self.surface.get_rect().size)
		#self.machineSurface.set_colorkey((255, 0, 255))
		self.fighterSurface = pygame.Surface(self.surface.get_rect().size)
		#self.fighterSurface.set_colorkey((255, 0, 255))
		self.fighters = []


	def getTilesBylayer(self, layerName):
		tileCoords = []
		for x, y, gid, in self.tileMap.get_layer_by_name(layerName):
			if gid:
				tileCoords.append((x + 1, y + 1))
		return tileCoords


	def render(self):
		self.staticBackground.fill((255, 200 ,255))

		for layer in self.tileMap.visible_layers:
			for x, y, gid, in layer:
				tile = self.tileMap.get_tile_image_by_gid(gid)
				if tile:
					self.staticBackground.blit(
						tile,
						(
							x * self.tileMap.tilewidth,
							y * self.tileMap.tileheight
						)
					)

		pygame.Surface.blit(
			self.surface,
			self.staticBackground,
			[0, 0]
		)
