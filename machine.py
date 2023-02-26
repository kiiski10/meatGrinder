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
    def __init__(self, parent_section):
        print("machine init")
        pygame.sprite.Sprite.__init__(self)
        self.image = machineTiles.get_tile_image(
            0, animation.ANIM_MAPPING["machine"]["gear"], 0
        )
        self.rect = self.image.get_rect()
        self.parent_section = parent_section
        self.rect.center = utilities.tilePosToScreenPos(48, self.parent_section.tilePos)
        self.active = True
        self.level = 1
        self.processTime = 3
        self.process_start_time = 0
        self.objects_in_process = []

    def process_in_progress(self):
        if self.process_start_time == 0:
            return False
        else:
            return time.time() - self.process_start_time < self.processTime
