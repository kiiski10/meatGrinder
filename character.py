import random, pygame
import utilities
import animation
from equipment import *

class CharacterStates:
	"""
		Possible states for game characters
	"""

	idle = "IDLE"
	move = "MOVE"
	fight = "INFIGHT"
	search = "SEARCH"
	stun = "STUN"
	dead = "DEAD"


	
class Fighter(pygame.sprite.Sprite):
	def __init__(
			self, speed=1, world=None, selectedEquipment=[], team=None, spawnPos=[100, 200]
		):

		self.debug = True
		pygame.sprite.Sprite.__init__(self)
		self.image = fighterTiles.get_tile_image(4, 0, 0).copy() # set naked body sprite as base image
		self.world = world
		self.rect = self.image.get_rect()
		self.rect.center = spawnPos,
		# self.rect.x += random.randint(-48, 48)
		# self.rect.y = random.randint(-48, 48)
		self.enemyDetectionAreaSize = 400
		self.dir = 45
		self.speed = speed + random.randint(10, 30) / 10
		self.state = CharacterStates.idle
		self.searchInterval = random.randint(10, 15)
		self.team = team
		self.health = 100
		self.target = None
		self.frame = 0
		self.animFrame = 0
		self.advAnim = True
		self.lastHitArea = pygame.Rect((0,0), (0,0))
		self.equipment = {}
		self.moved_in_step = 0

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
			CharacterStates.stun: 0,
			CharacterStates.move: 0,
			CharacterStates.search: 0,
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
		self.timeStamps[CharacterStates.search] = self.frame
		enemyRects = []
		for e in self.world.enemiesOf[self.team["name"]]:
			enemyRects.append(e.rect)

		dr = self.getDetectionRect()
		index = dr.collidelist(enemyRects)

		if index != -1:
			return(enemyRects[index])
		else:
			return(pygame.Rect(self.world.fighterInputs[self.team["primaryTarget"]], (20, 20)))


	def move(self):
		self.image = self.anim["MOVE"][utilities.dirAsCompassDir(self.dir)][self.animFrame]
		self.rect.center = utilities.angleDistToPos(self.rect.center, self.dir, 1.1 * self.speed)


	def takeHit(self, hit, angle):
		armor = self.equipment.get("armor", None)
		damage = hit["baseDamage"] * hit["level"]
		
		if armor:
			damage *= armor.damageMultiplier

		self.health -= damage
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
			self.state = CharacterStates.dead


	def hit(self, distance):
		hit = False
		weapon = self.equipment.get("weapon", None)
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
		if weapon:
			for e in enemiesInArea:
				e.takeHit(weapon.hit, self.dir)
				hit = True
		return(hit)


	def step(self, frame):
		self.frame = frame
		weapon = self.equipment.get("weapon", None)

		# change animation frame on every other step
		self.advAnim = not self.advAnim
		if self.advAnim:
			self.animFrame += 1
			if self.animFrame >= len(self.anim["MOVE"][utilities.dirAsCompassDir(self.dir)]):
				self.animFrame -= len(self.anim["MOVE"][utilities.dirAsCompassDir(self.dir)])

		if self.debug:
			utilities.drawDebugLayer(self)

		if self.frame - self.timeStamps[CharacterStates.search] > self.searchInterval:
			self.state = CharacterStates.search

		if self.state == CharacterStates.search:
			self.target = self.findTarget()
			self.dir = utilities.angleTo(self.rect.center, self.target.center)
			self.state = CharacterStates.move

		if not self.target:
			target = self.world.fighterInputs[self.team["primaryTarget"]]
			self.target = pygame.Rect(target, (3,3))

		dist = utilities.distTo(self.rect.center, self.target.center)
		angle = utilities.angleTo(self.rect.center, self.target.center)

		if self.state == CharacterStates.idle:
			self.state = CharacterStates.search

		elif self.state == CharacterStates.move:
			self.move()

		elif self.state == CharacterStates.fight:
			if weapon and self.frame - self.timeStamps["hit"] > weapon.weight:
				success = False
				if dist < weapon.reach:
					success = self.hit(dist)
				if not success:
					self.state = CharacterStates.move
					self.timeStamps[CharacterStates.move] = self.frame
					self.dir = angle - 180
					if angle < 0:
						angle += 360

		if weapon and dist < weapon.reach:
			self.state = CharacterStates.fight
