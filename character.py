import random, pygame
import utilities
import animation
from equipment import *

pygame.font.init()
font = pygame.font.SysFont('Monotype', 12)

class Fighter(pygame.sprite.Sprite):
	def __init__(
			self, speed=1, world=None, selectedEquipment=[], team=None, spawnNr=0
		):

		pygame.sprite.Sprite.__init__(self)
		self.image = fighterTiles.get_tile_image(4, 0, 0).copy() # set naked body sprite as base image
		self.world = world
		self.rect = self.image.get_rect()
		self.rect.center = team["fighterInputs"][spawnNr],
		# self.rect.x += random.randint(-48, 48)
		# self.rect.y = random.randint(-48, 48)
		self.enemyDetectionAreaSize = 350
		self.dir = 45
		self.speed = speed + random.randint(10, 30) / 10
		self.state = "IDLE" # IDLE, SEARCH, MOVE, INFIGHT, STUNNED, DEAD
		self.searchInterval = random.randint(10, 15)
		self.team = team
		self.health = 200
		self.target = None
		self.frame = 0
		self.animFrame = 0
		self.lastHitArea = pygame.Rect((0,0), (0,0))
		self.equipment = {}

		for e in selectedEquipment:
			if e.category == "armor":
				self.equipment["armor"] = e

			elif e.category == "weapon":
				self.equipment["weapon"] = e

			else:
				if not e.category in self.equipment:
					self.equipment[e.category] = [e]
				else:
					self.equipment[e.category].append(e)

		self.anim = {
			"MOVE": {
				"E": [],
				"W": [],
				"N": [],
				"S": []
			}
		}

		self.timeStamps = {
			"hit": 0,
			"stun": 0,
			"move": 0,
			"search": 0,
		}

		# generate anim frames
		for d in animation.ANIM_MAPPING["directions"]:
			frames = []
			fn = 0
			for frame in range(animation.ANIM_MAPPING["directions"][d], 4 + animation.ANIM_MAPPING["directions"][d]):
				newFrame = fighterTiles.get_tile_image(frame, 0, 0).copy()
				for c in self.equipment:
					if c == "clothing":
						for i in self.equipment[c]:
							newFrame.blit(i.anim[d][fn], [0, 0])
					if c == "weapon":
						newFrame.blit(self.equipment[c].anim[d][fn], [0, 0])
					if c == "armor":
						newFrame.blit(self.equipment[c].anim[d][fn], [0, 0])
				newFrame = utilities.changeColor(newFrame, self.team["color"])
				frames.append(newFrame)
				fn += 1

			self.anim["MOVE"][d] = frames



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
		enemyRects = []
		for e in self.world.enemiesOf[self.team["name"]]:
			enemyRects.append(e.rect)

		dr = self.getDetectionRect()
		index = dr.collidelist(enemyRects)

		if index != -1:
			return(enemyRects[index])
		else:
			return(pygame.Rect(self.team["primaryTarget"], (20, 20)))


	def move(self):
		# change animation frame
		self.animFrame += 1
		if self.animFrame >= len(self.anim[self.state][utilities.dirAsCompassDir(self.dir)]):
			self.animFrame -= len(self.anim[self.state][utilities.dirAsCompassDir(self.dir)])
		self.image = self.anim["MOVE"][utilities.dirAsCompassDir(self.dir)][self.animFrame]
		self.rect.center = utilities.angleDistToPos(self.rect.center, self.dir, 1.1 * self.speed)


	def takeHit(self, hit, angle):
		damage = (hit["baseDamage"] * hit["level"]) * self.equipment["armor"].damageMultiplier
		self.health -= damage
		# print("{} got hit. damage: {}/{}".format(self.team["name"], damage, hit["baseDamage"]))
		bloodAmount = int(damage / 6)
		if bloodAmount < 1:
			bloodAmount = 1

		for d in range(bloodAmount):
			self.world.addBloodDrop(
				self.centerPoint(),
				angle + random.randint(-10,10),
				damage + random.randint(7,10),
				((255 - random.randint(0, 55)) - damage , damage, damage)
			)
		if self.health <= 0:
			self.world.dead.append(self)
			skeletonColors = [(155,155,105),(55,55,55)]
			i = 0
			for sColor in skeletonColors:
				i += 1
				tintColor = sColor
				bones = utilities.tintImage(self.image, sColor)
				self.world.bloodNcorpseLayer.blit(
					bones,
					(
						self.rect.center[0] - i,
						self.rect.center[1] - i
					)
				)
			self.world.fighters.remove(self)
			self.state = "DEAD"


	def hit(self, distance):
		self.timeStamps["hit"] = self.frame

		# 1. define hit area
		self.lastHitArea = pygame.Rect((100,100), (distance, distance))

		self.lastHitArea.center = utilities.angleDistToPos(
			self.centerPoint(),
			self.dir,
			distance
		)

		# 2. find players in the area
		enemiesInArea = []

		for p in self.world.enemiesOf[self.team["name"]]:
			if self.lastHitArea.colliderect(p.rect) and p.state != "DEAD":
				enemiesInArea.append(p)

		# 3. deal damage to players
		for e in enemiesInArea:
			e.takeHit(self.equipment["weapon"].hit, self.dir)

		if len(enemiesInArea) > 0:
			return(True)
		else:
			return(False)


	def step(self, frame):
		self.frame = frame
		if self.frame - self.timeStamps["search"] > self.searchInterval:
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

		if self.state == "SEARCH":
			self.target = self.findTarget()
			self.dir = utilities.angleTo(self.rect.center, self.target.center)
			self.state = "MOVE"

		if not self.target:
			self.target = pygame.Rect(self.team["primaryTarget"], (3,3))

		dist = utilities.distTo(self.rect.center, self.target.center)
		angle = utilities.angleTo(self.rect.center, self.target.center)

		if self.state == "IDLE":
			self.state = "SEARCH"

		elif self.state == "MOVE":

			if dist < self.equipment["weapon"].reach * 3:
				oldSpeed = self.speed
				self.speed *= 0.5
				self.move()
				self.speed = oldSpeed
			else:
				self.move()

		elif self.state == "INFIGHT":
			if self.frame - self.timeStamps["hit"] > self.equipment["weapon"].weight:
				success = False
				if dist < self.equipment["weapon"].reach:
					success = self.hit(dist)
				if not success:
					self.state = "MOVE"
					self.timeStamps["move"] = self.frame
					self.dir = angle - 180
					if angle < 0:
						angle += 360

		elif self.state == "DEAD":
			pass # Cant do much else while dead

		if dist < self.equipment["weapon"].reach:
			self.state = "INFIGHT"
