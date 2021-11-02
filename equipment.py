import os
from pytmx import load_pygame
import animation

APP_PATH = os.path.dirname(os.path.realpath(__file__)) + os.sep
fighterTiles = load_pygame(os.path.join(APP_PATH, "tiles", "fighter", "fighter.tmx"))


def loadFrames(name):
	anim = {
		"E": [],
		"W": [],
		"N": [],
		"S": []
	}

	x = 0
	for d in anim:
		for frame in range(0, 4):
			anim[d].append(fighterTiles.get_tile_image(x, animation.ANIM_MAPPING["equipment"][name], 0))
			x += 1
	return(anim)



class Sword:
	def __init__(self, level=1):
		self.name = "sword"
		self.category = "weapon"
		self.type = "slash"
		self.reach = 100
		self.baseDamage = 30
		self.level = level
		self.weight = 80
		self.condition = 100
		self.anim = loadFrames(self.name)

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
		self.reach = 30
		self.baseDamage = 5
		self.level = 1
		self.weight = 60
		self.anim = loadFrames(self.name)

		self.hit = {
			"type": self.type,
			"baseDamage": self.baseDamage,
			"level": self.level,
			"weight": self.weight
		}


class Skin:
	def __init__(self):
		self.name = "body"
		self.category = "armor"
		self.level = 1
		self.damageMultiplier = 1
		self.condition = 100
		self.weaknesses = [] # [{"type": "blunt", "multiplier": 0.5}, {...}]
		self.anim = loadFrames(self.name)


class Shield:
	def __init__(self, level=1):
		self.name = "shield"
		self.category = "armor"
		self.level = level
		self.damageMultiplier = 0.8
		self.condition = 100
		self.weaknesses = [] # [{"type": "blunt", "multiplier": 0.5}, {...}]
		self.anim = loadFrames(self.name)


class Shirt:
	def __init__(self):
		self.name = "shirt"
		self.category = "clothing"
		self.anim = loadFrames(self.name)


class Pants:
	def __init__(self):
		self.name = "pants"
		self.category = "clothing"
		self.anim = loadFrames(self.name)


class Hair:
	def __init__(self):
		self.name = "hair"
		self.category = "clothing"
		self.anim = loadFrames(self.name)


class Shoes:
	def __init__(self):
		self.name = "shoes"
		self.category = "clothing"
		self.anim = loadFrames(self.name)
