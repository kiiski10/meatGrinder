import time, random, pygame
import utilities
TARGET_LOOPS_PER_SEC = 130

WINDOW_SIZE = [1700, 600]
# FULLSCREEN = True
FULLSCREEN = False
DEBUG = True
# DEBUG = False

if FULLSCREEN:
    displaySurf = pygame.display.set_mode((0, 0), pygame.NOFRAME)
else:
    displaySurf = pygame.display.set_mode(WINDOW_SIZE)

pygame.display.init()

from equipment import *
from grinder import Grinder
from factory import Factory
from character import Fighter

teams = {
    "orange": {
        "name": "orange",
        "color": (255, 87, 20),
        "fighterInputs": [
            "0x0",
            "0x9",
        ],
        "primaryTarget": "2x2",
    },
    "blue": {
        "name": "blue",
        "color": (25, 175, 255),
        "fighterInputs": [
            "2x2",
            "2x2",
        ],
        "primaryTarget": "0x0",
    },
}

clock = pygame.time.Clock()
meatGrinder = Grinder(teams, debug=DEBUG)
factory = Factory(teams["orange"], meatGrinder)
frame_counter = 0
game_loop_counter = 0
game_loop_min_delay = 0.014 # 0.014 = max 60 loops per sec
steps_per_sec_timer = time.time()

winTitleExtraText = "SPD:{}/{} | FPS:{} | BLOOD:{} | STEP:{}".format(
    game_loop_counter,
    TARGET_LOOPS_PER_SEC,
    frame_counter,
    len(meatGrinder.bloodDrops),
    meatGrinder.step_count,
)
pygame.display.set_caption(
    "MeatGrinder | {}".format(
        winTitleExtraText
    )
)


def addFighter(team, spawnPos, speed, equipment): # TODO: move this to Grinder
    new_fighter = Fighter(
            world=meatGrinder,
            team=teams[team],
            spawnPos=spawnPos,
            speed=speed,
            selectedEquipment=equipment,
    )
    meatGrinder.fighters.append(new_fighter)
    meatGrinder.fighterSprites.add(new_fighter)


def handleEvents():
    events = pygame.event.get()
    for event in events:
        if event.type == 256:  # Window close
            return False
        elif event.type == 768:  # Key down
            key = {"unicode": event.unicode, "scancode": event.scancode}
            print(
                "KEY PRESS: unicode: {0:5} scancode: {1}".format(
                    key["unicode"], key["scancode"]
                )
            )
            if event.unicode == "Q" or event.scancode == 41:
                return False
    return True


def randomEquipments(n): # TODO: move this to Grinder
    equipmentAvailable = [Sword(), Shield(), Shirt(), Pants(), Hair(), Shoes()]
    selectedEquipment = [Skin(), Fist()]
    while len(selectedEquipment) < n:
        e = random.choice(equipmentAvailable)
        if e not in selectedEquipment:
            selectedEquipment.append(e)
    return selectedEquipment

# @utilities.time_this
def game_step():
    displaySurf.fill((120, 120, 120))

    meatGrinder.step()
    if meatGrinder.step_count - factory.advanced_on_grinder_step > factory.grinder_steps_between_steps:
        factory.step(meatGrinder.step_count)
        factory.render()
    meatGrinder.render()

    surfaceYPos = (displaySurf.get_height() - meatGrinder.surface.get_height()) / 2
    surfaceXPos = meatGrinder.surface.get_width() + 10

    displaySurf.blit(meatGrinder.surface, (5, surfaceYPos))
    if DEBUG:
        displaySurf.blit(meatGrinder.debugLayer, (5, surfaceYPos))

    displaySurf.blit(factory.surface, (surfaceXPos, surfaceYPos))
    pygame.display.flip()


while handleEvents():
    game_loop_counter += 1

    # Update window title
    if time.time() - steps_per_sec_timer >= 1:
        winTitleExtraText = "SPD:{}/{} | FPS:{} | BLOOD:{} | STEP:{}".format(
            game_loop_counter,
            TARGET_LOOPS_PER_SEC,
            frame_counter,
            len(meatGrinder.bloodDrops),
            meatGrinder.step_count,
        )
        steps_per_sec_timer = time.time()
        game_loop_counter = 0
        frame_counter = 0
        pygame.display.set_caption(
            "MeatGrinder | Fighters: {} | {}".format(
                len(meatGrinder.fighters), winTitleExtraText
            )
        )

    if time.time() - meatGrinder.last_step_time > game_loop_min_delay:
        frame_counter += 1

        if random.randint(0, 100) < 10: # % chance to spawn new fighter on each round
            speed = random.randint(20, 30) / 10.00
            addFighter("blue", [24, 250], speed, randomEquipments(4))

        game_step()

    clock.tick(TARGET_LOOPS_PER_SEC)


pygame.quit()
print("QUIT BYE")

