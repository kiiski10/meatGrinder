import time, random, pygame

TARGET_FPS = 30
WINDOW_SIZE = [900, 500]
displaySurf = pygame.display.set_mode(WINDOW_SIZE, pygame.HWSURFACE | pygame.DOUBLEBUF)# | pygame.FULLSCREEN)
pygame.display.init()
from equipment import *
from grinder import Grinder
from character import Fighter

START_PLAYER_COUNT = 2000

fighterInputs =	{
	"A": [800, 200],
	"B": [20, 300]
}

teams = {
	"red": {
		"name": "red",
		"color": (170, 40, 40),
		"fighterInputs": [fighterInputs["A"]],
		"primaryTarget": fighterInputs["B"]
	},
	"blue": {
		"name": "blue",
		"color": (40, 40, 170),
		"fighterInputs": [fighterInputs["B"]],
		"primaryTarget": fighterInputs["A"]
	}
}

clock = pygame.time.Clock()
meatGrinder = Grinder(teams, fighterInputs, displaySurf)

def addFighter(team, spawn, speed, equipment):
	meatGrinder.fighters.append(Fighter(
		world=meatGrinder,
		team=teams[team],
		spawnNr=spawn,
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
	equipmentAvailable = [Sword(), Shield(), Shirt(), Pants(), Hair()]
	selectedEquipment = []
	while len(selectedEquipment) < n:
		e = random.choice(equipmentAvailable)
		if e not in selectedEquipment:
			selectedEquipment.append(e)

	return(selectedEquipment)

pygame.event.get()
running = True

c = 0
for i in range(START_PLAYER_COUNT):
	c += 1
	if c > 1:
		c = 0
		team = "red"
	else:
		team = "blue"
	speed = random.randint(20, 60) / 10
	addFighter(team, 0, speed, randomEquipments(3))

stepPerSecCounter = 0
stepPerSecTimer = time.time()
winTitleExtraText = "FPS:{}/{} BLOOD:{}".format(stepPerSecCounter, TARGET_FPS, len(meatGrinder.bloodDrops))

while running:
	stepPerSecCounter += 1
	running = handleEvents()
	displaySurf.fill((200, 200, 200))
	meatGrinder.debugLayer.fill((255,0,255))
	meatGrinder.step()
	meatGrinder.render(displaySurf)
	pygame.display.flip()

	spawnTime = not random.randint(0, 10)
	if spawnTime:
		speed = random.randint(20, 60) / 10
		addFighter(random.sample(list(teams), 1)[0], 0, speed, randomEquipments(3))

	if time.time() - stepPerSecTimer >= 1:
		winTitleExtraText = "FPS:{}/{} BLOOD:{}".format(stepPerSecCounter, TARGET_FPS, len(meatGrinder.bloodDrops))
		stepPerSecTimer = time.time()
		stepPerSecCounter = 0
	pygame.display.set_caption("MeatGrinder | Fighters: {} | {}".format(len(meatGrinder.fighters), winTitleExtraText))
	clock.tick(TARGET_FPS)

pygame.quit()
print("QUIT BYE")
