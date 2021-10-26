import random, pygame
import utilities
from equipment import *

pygame.font.init()
font = pygame.font.SysFont('Monotype', 12)

class Fighter(pygame.sprite.Sprite):
	def __init__(
			self, speed=1, world=None, selectedEquipment=[],
			primaryTarget=None, team=None, spawnNr=0
		):

		print("fighter init")

		pygame.sprite.Sprite.__init__(self)
		self.image = fighterTiles.get_tile_image(0, 0, 0).copy() # set naked body sprite as base image
		self.world = world
		self.rect = self.image.get_rect()
		self.rect.center = team["fighterInputs"][spawnNr],
		self.rect.x += random.randint(-20, 20)
		self.rect.y = random.randint(0, 450)
		self.enemyDetectionAreaSize = 350
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
		self.bloodDrops = []

		self.timeStamps = {
			"spawn": 0,
			"hit": 0,
			"stun": 0,
			"move": 0,
			"search": 0,
		}

		self.equipment = {
			"weapon": Fist(),
			"armor": Skin(),
		}

		for e in selectedEquipment:
			print("EQUIP:", e.category, e.name)
			if e.category == "armor":
				self.equipment["armor"] = e

			elif e.category == "weapon":
				self.equipment["weapon"] = e

			self.image.blit(e.image, [0, 0])


		colorToReplace = (255,0,0)
		pa = pygame.PixelArray(self.image)
		pa.replace(colorToReplace, self.team["color"])


	def centerPoint(self):
		return [
			int(self.rect.center[0] + self.rect.width / 2),
			int(self.rect.center[1] + self.rect.height / 2)
		]

	def getDetectionRect(self):
		w = self.enemyDetectionAreaSize
		h = self.enemyDetectionAreaSize
		r = pygame.Rect((0, 0), [w, h])
		self.centerPoint()
		r.center = self.centerPoint()
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


	def move(self, angle):
		self.dir = angle

		# change animation frame
		self.animFrame += 1
		if self.animFrame >= len(self.anim):
			self.animFrame = 0
		self.image = self.anim[self.animFrame]
		self.rect.center = utilities.angleDistToPos(self.rect.center, angle, 1.1 * self.speed)

	def addBloodDrop(self):
		self.bloodDrops.append(
			{
				"spawnOnFrame": self.frame,
				"speed": 5,
				"pos": self.centerPoint()
			}
		)


	def takeHit(self, hit):
		damage = (hit["baseDamage"] * hit["level"]) * self.equipment["armor"].damageMultiplier
		self.health -= damage
		self.addBloodDrop()
		if self.health <= 0:
			self.world.dead.append(self)
			self.world.fighters.remove(self)
			self.state = "DEAD"


	def hit(self, angle, distance):
		self.timeStamps["hit"] = self.frame

		# 1. define hit area
		reach = self.equipment["weapon"].reach
		#print("HIT:", self.equipment["weapon"])
		self.lastHitArea = pygame.Rect((0,0), (reach,reach))
		center = self.centerPoint()

		self.lastHitArea.center = utilities.angleDistToPos(
			center,
			angle,
			reach
		)

		# 2. find players in the area
		enemiesInArea = []
		for p in list(filter(lambda x: x.team != self.team, self.world.fighters)):
			if self.lastHitArea.colliderect(p.rect):
				enemiesInArea.append(p)

		# 3. deal damage to players
		for e in enemiesInArea:
			e.takeHit(self.equipment["weapon"].hit)

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

		for b in self.bloodDrops:
			bloodSize = 10
			drop = pygame.Rect((0,0), (bloodSize, bloodSize))
			lifeTime = self.frame - b["spawnOnFrame"]
			x = b["pos"][0]
			y = b["pos"][1]

			drop.center = [
				x + lifeTime,
				y + lifeTime
			]

			print(lifeTime)
			if lifeTime > 100:
				targetLayer = self.world.bloodNcorpseLayer
				color = (100,50,0)
				self.bloodDrops.remove(b)
			else:
				targetLayer = self.world.bloodDropLayer
				color = (200,100,0)

			pygame.draw.rect(
				targetLayer,
				color,
				drop,
				0
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
			self.timeStamps["search"] = self.frame

		if self.state == "SEARCH":
			self.target = self.findTarget()

		dist = utilities.distTo(self.rect.center, self.target.center)
		angle = utilities.angleTo(self.rect.center, self.target.center)

		if self.state == "MOVE":
			self.move(angle)

		if self.state == "INFIGHT":
			if self.frame - self.timeStamps["hit"] > self.equipment["weapon"].weight:
				success = False
				if dist < self.equipment["weapon"].reach:
					success = self.hit(angle, dist)
				if not success:
					self.state = "MOVE"
					self.timeStamps["move"] = self.frame

		if dist < self.equipment["weapon"].reach:
			self.state = "INFIGHT"
			self.timeStamps["infight"] = self.frame

		elif self.frame - self.timeStamps["move"] > 10:
			self.state = "MOVE"
			self.timeStamps["move"] = self.frame

		elif self.state == "DEAD":
			pass # Cant do much else while dead
