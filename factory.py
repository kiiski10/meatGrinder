import pygame, random
import utilities

class Factory:
	def __init__(self, team):
		print("grinder init")
		self.surface = pygame.Surface((500, 500))
		self.staticBackground = pygame.Surface(self.surface.get_rect().size)
		self.staticBackground.fill((255, 0 ,255)) # TODO: draw the factory background here
		self.staticBackground.set_colorkey((255, 12, 255))
		self.lineSurface = pygame.Surface(self.surface.get_rect().size)
		self.lineSurface.set_colorkey((255, 0, 255))
		self.machineSurface = pygame.Surface(self.surface.get_rect().size)
		self.machineSurface.set_colorkey((255, 0, 255))
		self.fighterSurface = pygame.Surface(self.surface.get_rect().size)
		self.fighterSurface.set_colorkey((255, 0, 255))
		self.fighters = []


	def render(self):
		# background

		pygame.Surface.blit(
			self.surface,
			self.staticBackground,
			[900, 0]
		)
