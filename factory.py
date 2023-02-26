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
        self.stats = {"step": 0}
        self.grinder = grinder
        self.tileMap = load_pygame(
            os.path.join(APP_PATH, "tiles", "factory", "factory.tmx")
        )
        self.surface = pygame.Surface((480, 480))
        _surfsize = self.surface.get_rect().size
        self.arrowSurface = pygame.Surface(_surfsize)
        self.lineSurface = pygame.Surface(_surfsize)
        self.machineSurface = pygame.Surface(_surfsize)
        self.fighterSurface = pygame.Surface(_surfsize)
        self.arrowSurface.fill((255, 255, 255))
        self.lineSurface.fill((255, 255, 255))
        self.machineSurface.fill((255, 255, 255))
        self.fighterSurface.fill((255, 255, 255))
        self.arrowSurface.set_colorkey((255, 0, 255))
        self.lineSurface.set_colorkey((255, 0, 255))
        self.machineSurface.set_colorkey((255, 0, 255))
        self.fighterSurface.set_colorkey((255, 0, 255))
        self.inGate = self.getTilesByLayer("fighterIn")[0]
        self.prodLine = ProductionLine(self, self.inGate)

    def getTilesByLayer(self, layerName):
        tileCoords = []
        for (
            x,
            y,
            gid,
        ) in self.tileMap.get_layer_by_name(layerName):
            if gid:
                tileCoords.append((x, y))
        return tileCoords

    def step(self):
        self.stats["step"] += 1
        self.prodLine.step()

        # let fighters in the factory
        pos = self.inGate
        in_gate_section = self.prodLine.line[utilities.tilePosId(pos)]
        if len(in_gate_section.fighters_here) == 0:
            newFighter = Fighter(
                world=self.grinder,
                team=self.team,
                spawnPos=[0, 0],
                speed=2,
                selectedEquipment=[],
            )

            newFighter.rect.center = utilities.tilePosToScreenPos(48, pos)
            self.prodLine.addFighter(newFighter)

    def drawLayerByName(self, layerName, targetSurface):
        for (
            x,
            y,
            gid,
        ) in self.tileMap.get_layer_by_name(layerName):
            if gid:
                tile = self.tileMap.get_tile_image_by_gid(gid)
                if tile:
                    targetSurface.blit(
                        tile, (x * self.tileMap.tilewidth, y * self.tileMap.tileheight)
                    )

        pygame.Surface.blit(self.surface, targetSurface, [0, 0])

    def drawMachines(self, targetSurface):
        machines = [
            x[1].machine
            for x in self.prodLine.line.items()
            if x[1].machine
        ]
        for m in machines:
            x = m.parent_section.tilePos[0]
            y = m.parent_section.tilePos[1]
            targetSurface.blit(
                m.image, (x * self.tileMap.tilewidth, y * self.tileMap.tileheight)
            )

    def render(self):
        self.surface.fill((255, 255, 255))
        self.drawLayerByName("prodLine", self.surface)
        self.drawLayerByName("fighterIn", self.surface)
        self.drawLayerByName("fighterOut", self.surface)
        self.drawLayerByName("arrows", self.surface)
        self.fighterSurface.fill((255, 0, 255))
        self.fighterSprites.draw(self.surface)
        self.drawMachines(self.surface)

        pygame.Surface.blit(self.surface, self.fighterSurface, [0, 0])
