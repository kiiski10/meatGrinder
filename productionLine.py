import pygame, random, time
from machine import Machine
import utilities
from equipment import *
from character import Fighter


class Section:
	def __init__(self, pos, prodLine):
		self.prodLine = prodLine
		self.tilePos = pos
		self.machine = None
		self.neighbors = []


class ProductionLine:
	def __init__(self, factory, inGate):
		print("production line init")
		self.fighters = []
		self.inGate = inGate
		self.outGates = [(0,0), (0,9)]
		self.factory = factory
		self.debugLayer = pygame.Surface(self.factory.surface.get_rect().size)
		self.debugLayer.set_colorkey((255, 0, 255))
		self.debugLayer.fill((255, 0, 255))
		self.stats = {
			"step": 0
		}

		self.line = {
			utilities.tilePosId(self.inGate): Section(self.inGate, self),
		}

		for s in self.factory.getTilesByLayer("prodLine"):
			newSection = Section(s, self)
			self.line[utilities.tilePosId(s)] = newSection

		# add connections
		for section in self.line:
			pos = self.line[section].tilePos
			#print("section in", pos)
			for n in self.neighboringSections(pos):
				n.neighbors.append(self.line[section])
				self.line[section].neighbors.append(n)

				pygame.draw.line(
					self.debugLayer,
					[242, 132, 45],
					utilities.tilePosToScreenPos(48, pos),
					utilities.tilePosToScreenPos(48, n.tilePos),
					5
				)

		# add machines to random sections (not on the sides)
		for s in self.line:
			if self.line[s].tilePos[0] not in [0, 9] and self.line[s].tilePos[1] not in [0, 9]:
				if random.randint(0, 100) < 20:
					self.line[s].machine = Machine(self.line[s], equipment=random.choice([Sword(), Shield(), Pants(), Shirt()]))
					self.factory.machineSprites.add(self.line[s].machine)


	def availableDirections(self, fromPos):
		destSections = []
		if not fromPos in self.line:
			return(destSections)

		destSections += self.line[fromPos].neighbors
		#print("destinations from", fromPos, len(destSections))
		return(destSections)


	def neighboringSections(self, pos):
		neighbors = []
		posString = utilities.tilePosId(pos)
		if posString in self.line:
			for x, y in [[-1, 0], [1, 0], [0, -1], [0, 1]]:
				testKey = utilities.tilePosId((pos[0] + x, pos[1] + y))
				if testKey in self.line:
					n = self.line[testKey]
					neighbors.append(n)

		#print("  is connected to", len(neighbors))
		return(neighbors)


	def addFighter(self, newFighter):
		tilePos = utilities.screenPosToTilePos(48, newFighter.rect.center)
		newFighter.prodLineLastSections = [tilePos]
		posString = utilities.tilePosId(tilePos)
		newFighter.state = posString
		self.fighters.append(newFighter)


	def fightersAt(self, pos):
		posString = utilities.tilePosId(pos)
		occupiers = []
		for f in self.fighters:
			if utilities.screenPosToTilePos(48, f.rect.center) == pos:
				occupiers.append(f)
		return(occupiers)


	def lineAdvance(self):
		# move fighters
		fightersToGrinder = []
		for fighter in self.fighters:
			if fighter.state == "IN_MACHINE":
				continue

			if self.stats["step"] - fighter.timeStamps["move"] < 10 + random.randint(0, 10):
				continue

			if fighter.prodLineLastSections[-1] in self.outGates:
				fightersToGrinder.append(fighter)

			for sect in self.availableDirections(fighter.state):
				if not sect.tilePos in fighter.prodLineLastSections:
					if len(self.fightersAt(sect.tilePos)) == 0:
						fighter.state = utilities.tilePosId(sect.tilePos)
						fighter.rect.center = utilities.tilePosToScreenPos(48, sect.tilePos)
						fighter.timeStamps["move"] = self.stats["step"]
						fighter.prodLineLastSections.append(sect.tilePos)
						break

		for f in fightersToGrinder:
			x, y = utilities.tilePosToScreenPos(48, f.prodLineLastSections[-1])
			x = self.factory.grinder.surface.get_width() - 12
			y -= 24
			f.rect.center = [x, y]
			selectedEquipment=[Skin(), Fist()]
			
			for c in f.equipment:
				selectedEquipment.append(f.equipment[c])

			rebornFighter = Fighter(
				world=self.factory.grinder,
				team=self.factory.team,
				spawnPos=f.rect.center,
				speed=f.speed,
				selectedEquipment=selectedEquipment
			)

			#rebornFighter.equipment = f.equipment
			self.factory.grinder.fighters.append(rebornFighter)
			self.fighters.remove(f)
			fightersToGrinder.remove(f)
			f.kill()

		# step all machines
		for s in self.line:
			if self.line[s].machine:
				self.line[s].machine.step()


	def step(self):
		self.stats["step"] += 1
		self.lineAdvance()
