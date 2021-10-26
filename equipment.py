import os
from pytmx import load_pygame


APP_PATH = os.path.dirname(os.path.realpath(__file__)) + os.sep
fighterTiles = load_pygame(os.path.join(APP_PATH, "tiles", "fighter.tmx"))

SPRITE_ROW_MAPPING = {
	"body": 0,
	"sword": 1,
	"shield": 2,
	"shirt": 3,
	"pants": 4,
	"hair": 5,
	"skin": 6,
	"fist": 7,
}

class Sword:
	def __init__(self, level=1):
		self.name = "sword"
		self.category = "weapon"
		self.type = "slash"
		self.reach = 50
		self.baseDamage = 30
		self.level = level
		self.weight = 80
		self.condition = 100
		self.image = fighterTiles.get_tile_image(0, SPRITE_ROW_MAPPING[self.name], 0)

		self.hit = {
			"type": self.type,
			"baseDamage": self.baseDamage,
			"level": self.level,
			"weight": self.weight
		}


class Fist:
	def __init__(self):
		self.name = "fist"
		self.category = "weapon"
		self.type = "melee"
		self.reach = 10
		self.baseDamage = 2
		self.level = 1
		self.weight = 30
		self.image = fighterTiles.get_tile_image(0, SPRITE_ROW_MAPPING[self.name], 0)

		self.hit = {
			"type": self.type,
			"baseDamage": self.baseDamage,
			"level": self.level,
			"weight": self.weight
		}


class Skin:
	def __init__(self):
		self.name = "skin"
		self.category = "armor"
		self.level = 1
		self.damageMultiplier = 1
		self.condition = 100
		self.weaknesses = [] # [{"type": "blunt", "multiplier": 0.5}, {...}]
		self.image = fighterTiles.get_tile_image(0, SPRITE_ROW_MAPPING[self.name], 0)


class Shield:
	def __init__(self, level=1):
		self.name = "shield"
		self.category = "armor"
		self.level = level
		self.damageMultiplier = 0.8
		self.condition = 100
		self.weaknesses = [] # [{"type": "blunt", "multiplier": 0.5}, {...}]
		self.image = fighterTiles.get_tile_image(0, SPRITE_ROW_MAPPING[self.name], 0)


class Shirt:
	def __init__(self, color=(255,0,255)):
		self.name = "shirt"
		self.category = "clothing"
		self.image = fighterTiles.get_tile_image(0, SPRITE_ROW_MAPPING[self.name], 0)


class Pants:
	def __init__(self, color=(255,0,255)):
		self.name = "pants"
		self.category = "clothing"
		self.image = fighterTiles.get_tile_image(0, SPRITE_ROW_MAPPING[self.name], 0)


class Hair:
	def __init__(self, color=(255,0,255)):
		self.name = "hair"
		self.category = "clothing"
		self.image = fighterTiles.get_tile_image(0, SPRITE_ROW_MAPPING[self.name], 0)
