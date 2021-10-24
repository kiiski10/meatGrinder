import random, pygame
import utilities
from equipment import Sword, Fist, Shield, Skin

pygame.font.init()
font = pygame.font.SysFont('Monotype', 12)

SPRITE_ROW_MAPPING = {
	"body": 0,
	"sword": 1,
	"shield": 2,
	"shirt": 3,
	"pants": 4,
	"hair": 5,
}

equipmentAvailable = {
	"sword": Sword(),
	"shield": Shield(),
	"fist": Fist(),
	"skin": Skin(),
}

class Fighter(pygame.sprite.Sprite):
	def __init__(
			self, speed=1, world=None, selectedEquipment=[],
			primaryTarget=None, weapon=None, armor=None, team=None,
			fighterTiles=None, spawnNr=0
		):

		print("fighter init")
		print("equipment", selectedEquipment)

		self.weapon = weapon
		self.armor = armor

		images = {}
		for e in selectedEquipment:
			if e == "shield":
				self.armor = equipmentAvailable["shield"]

			elif e == "sword":
				self.weapon = equipmentAvailable["sword"]

			images[e] = fighterTiles.get_tile_image(0, SPRITE_ROW_MAPPING[e], 0)

		if not self.weapon:
			self.weapon = equipmentAvailable["fist"]

		if not self.armor:
			self.armor = equipmentAvailable["skin"]

		if images == None:
			self.images = {}
		else:
			self.images = images

		for r in SPRITE_ROW_MAPPING:
			if r not in self.images:
				self.images[r] = None

		pygame.sprite.Sprite.__init__(self)
		self.image = fighterTiles.get_tile_image(0, SPRITE_ROW_MAPPING["body"], 0).copy()
		self.world = world
		self.rect = self.image.get_rect()
		self.rect.center = team["fighterInputs"][spawnNr],
		self.rect.x += random.randint(-20, 20)
		self.rect.y = random.randint(0, 450)
		self.enemyDetectionAreaSize = 450
		self.dir = 45
		self.speed = speed
		self.state = "IDLE" # IDLE, SEARCH, MOVE, INFIGHT, STUNNED, DEAD
		self.team = team
		self.health = 100
		self.target = None
		self.frame = 0
		self.animFrame = 0
		self.anim = [self.image]
		self.lastHitArea = pygame.Rect((0,0), (0,0))

		for e in images:
			if images[e]:
				self.image.blit(images[e], [0, 0])

		self.timeStamps = {
			"spawn": 0,
			"hit": 0,
			"stun": 0,
			"move": 0,
			"search": 0,
		}

		colorToReplace = (255,0,0)
		pa = pygame.PixelArray(self.image)
		pa.replace(colorToReplace, self.team["color"])


	def getDetectionRect(self):
		w = self.enemyDetectionAreaSize
		h = self.enemyDetectionAreaSize
		r = pygame.Rect([0, 0], [w, h])
		r.center = [
			self.rect.x + self.rect.width,
			self.rect.y + self.rect.width
		]
		return(r)


	def findTarget(self):
		self.timeStamps["search"] = self.frame
		enemies = list(filter(lambda x: x.team != self.team, self.world.fighters))
		enemyRects = []
		for e in enemies:
			enemyRects.append(e.rect)

		dr = self.getDetectionRect()
		index = dr.collidelist(enemyRects)

		if index != -1:
			return(enemyRects[index])
		else:
			return(pygame.Rect(self.team["primaryTarget"], (20, 20)))

		print("NO RETURN")


	def move(self, angle):
		self.dir = angle

		# change animation frame
		self.animFrame += 1
		if self.animFrame >= len(self.anim):
			self.animFrame = 0
		self.image = self.anim[self.animFrame]

		movement = pygame.math.Vector2()
		movement.from_polar((1 * self.speed, angle))
		movement.x = int(movement.x) + random.randint(-3, 3)
		movement.y = int(movement.y) + random.randint(-3, 3)
		self.rect.x += movement.x
		self.rect.y += movement.y


	def takeHit(self, hit):
		damage = (hit["baseDamage"] * hit["level"]) * self.armor.damageMultiplier
		self.health -= damage
		if self.health <= 0:
			self.world.dead.append(self)
			self.world.fighters.remove(self)


	def hit(self, angle, distance):
		self.timeStamps["hit"] = self.frame

		# 1. define hit area
		reach = self.weapon.reach
		hitArea = pygame.Rect((0,0), (reach,reach))
		hitArea.center = utilities.angleDistToPos(self.rect.center, angle, self.weapon.reach)
		self.lastHitArea = hitArea

		# 2. find players in the area
		enemiesInArea = []
		for p in list(filter(lambda x: x.team != self.team, self.world.fighters)):
			if hitArea.colliderect(p.rect):
				enemiesInArea.append(p)

		# 3. deal damage to players
		for e in enemiesInArea:
			e.takeHit(self.weapon.hit)

		if len(enemiesInArea) > 0:
			return(True)


	def step(self, frame):
		self.frame = frame

		if self.frame - self.timeStamps["search"] > 15 * (random.randint(1, 10)):
			self.state = "SEARCH"

		debug = True
		if debug and self.target: # target line
			pygame.draw.line(
				self.world.debugLayer,
				(20, 10, 40),
				(self.rect.center[0] + 24, self.rect.center[1] + 24),
				(self.target.center[0] + 24, self.target.center[1] + 24),
				1
		)

		debug = True
		if debug: # hit marker
			if self.lastHitArea:
				pygame.draw.rect(
					self.world.debugLayer,
					(200, 30, 30),
					self.lastHitArea,
					0
				)
				self.lastHitArea = None

		debug = True
		if debug: # health bar
			x = self.rect.x + self.rect.width * 0.5
			y = self.rect.y + self.rect.height * 1.5

			pygame.draw.line(
				self.world.debugLayer,
				(20, 130, 30),
				(x,y), (x + (self.health / 100) * self.rect.width, y),
				3
		)

		debug = True
		if debug: # state
			textsurface = font.render(self.state, False, (0, 0, 0))
			x = self.rect.x + self.rect.width * 0.5
			y = self.rect.y + self.rect.height * 1.5
			self.world.debugLayer.blit(textsurface,(x,y))


		if self.state == "IDLE":
			self.state = "SEARCH"


		if self.state == "SEARCH":
			self.target = self.findTarget()
			self.state= "MOVE"


		dist = utilities.distTo(self.rect.center, self.target)
		angle = utilities.angleTo(self.rect.center, self.target)
		print(angle)

		if self.state == "MOVE":
			self.move(angle)


		if self.state == "INFIGHT":
			if self.frame - self.timeStamps["hit"] > self.weapon.weight:
				success = False
				if dist < self.weapon.reach:
					success = self.hit(angle, dist)
				if not success:
					self.state = "IDLE"

		if dist < self.weapon.reach:
			self.state = "INFIGHT"
