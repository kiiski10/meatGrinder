import time, random, pygame
TARGET_FPS = 30
START_PLAYER_COUNT = 2

WINDOW_SIZE = [1700, 600]
#FULLSCREEN = True
FULLSCREEN = False
#DEBUG = True
DEBUG = False

if FULLSCREEN:
	displaySurf = pygame.display.set_mode((0, 0), pygame.NOFRAME)
else:
	displaySurf = pygame.display.set_mode(WINDOW_SIZE)

pygame.display.init()

from equipment import *
from grinder import Grinder
from factory import Factory
from character import Fighter

time.sleep(0)

fighterInputs =	{
	"A": [1180, 240],
	"B": [10, 240]
}

teams = {
	"orange": {
		"name": "orange",
		"color": (255, 87, 20),
		"fighterInputs": [fighterInputs["A"]],
		"primaryTarget": fighterInputs["B"]
	},
	"blue": {
		"name": "blue",
		"color": (25, 175, 255),
		"fighterInputs": [fighterInputs["B"]],
		"primaryTarget": fighterInputs["A"]
	}
}

clock = pygame.time.Clock()
meatGrinder = Grinder(teams, fighterInputs)
factory = Factory(teams["orange"], meatGrinder)


def addFighter(team, spawnPos, speed, equipment):
	meatGrinder.fighters.append(Fighter(
		world=meatGrinder,
		team=teams[team],
		spawnPos=spawnPos,
		speed=speed,
		selectedEquipment=equipment
	)
)


def handleEvents():
	events = pygame.event.get()
	for event in events:
		if event.type == 256:				# Window close
			return(False)
		elif event.type == 768:				# Key down
			key = {"unicode": event.unicode, "scancode": event.scancode}
			print("KEY PRESS: unicode: {0:5} scancode: {1}".format(key["unicode"], key["scancode"]))
			if event.unicode == "Q" or event.scancode == 41:
				return(False)
	return(True)


def randomEquipments(n):
	equipmentAvailable = [Sword(), Shield(), Shirt(), Pants(), Hair(), Shoes()]
	selectedEquipment = [Skin(), Fist()]
	while len(selectedEquipment) < n:
		e = random.choice(equipmentAvailable)
		if e not in selectedEquipment:
			selectedEquipment.append(e)

	return(selectedEquipment)


pygame.event.get()
running = True

stepPerSecCounter = 0
stepPerSecTimer = time.time()
winTitleExtraText = "FPS:{}/{} | BLOOD:{} | STEP:{}".format(stepPerSecCounter, TARGET_FPS, len(meatGrinder.bloodDrops), meatGrinder.stats["step"])

while running:
	stepPerSecCounter += 1
	running = handleEvents()
	displaySurf.fill((120, 120, 120))
	if DEBUG: meatGrinder.debugLayer.fill((255, 0, 255))
	meatGrinder.step()
	factory.step()
	meatGrinder.render()
	factory.render()

	surfaceYPos = (displaySurf.get_height() - meatGrinder.surface.get_height()) / 2
	surfaceXPos = meatGrinder.surface.get_width() + 10

	displaySurf.blit(meatGrinder.surface, (5, surfaceYPos))
	if DEBUG: displaySurf.blit(meatGrinder.debugLayer, (5, surfaceYPos))
	displaySurf.blit(factory.surface, (surfaceXPos, surfaceYPos))

	pygame.display.flip()

	## spawn enemy fighters
	spawnTime = not random.randint(0, 45)
	if spawnTime:
		speed = random.randint(10, 40) / 10
		addFighter("blue", [24, 250], speed, randomEquipments(4))

	if time.time() - stepPerSecTimer >= 1:
		winTitleExtraText = "FPS:{}/{} | BLOOD:{} | STEP:{}".format(stepPerSecCounter, TARGET_FPS, len(meatGrinder.bloodDrops), meatGrinder.stats["step"])
		stepPerSecTimer = time.time()
		stepPerSecCounter = 0
	pygame.display.set_caption("MeatGrinder | Fighters: {} | {}".format(len(meatGrinder.fighters), winTitleExtraText))
	clock.tick(TARGET_FPS)

pygame.quit()
print("QUIT BYE")
