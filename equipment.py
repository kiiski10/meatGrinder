class Sword:
	def __init__(self, level=1):
		print("sword init")
		self.category = "weapon"
		self.type = "slash"
		self.reach = 35
		self.baseDamage = 10
		self.level = level
		self.weight = 15
		self.condition = 100

		self.hit = {
			"type": self.type,
			"baseDamage": self.baseDamage,
			"level": self.level,
			"weight": self.weight
		}


class Fist:
	def __init__(self):
		print("fist init")
		self.category = "weapon"
		self.type = "melee"
		self.reach = 10
		self.baseDamage = 2
		self.level = 1
		self.weight = 4

		self.hit = {
			"type": self.type,
			"baseDamage": self.baseDamage,
			"level": self.level,
			"weight": self.weight
		}


class Skin:
	def __init__(self):
		print("skin init")
		self.category = "armor"
		self.level = 1
		self.damageMultiplier = 1
		self.condition = 100
		self.weaknesses = [] # [{"type": "blunt", "multiplier": 0.5}, {...}]


class Shield:
	def __init__(self, level=1):
		print("armor init")
		self.category = "armor"
		self.level = level
		self.damageMultiplier = 0.8
		self.condition = 100
		self.weaknesses = [] # [{"type": "blunt", "multiplier": 0.5}, {...}]
