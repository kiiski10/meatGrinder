import time, random, pygame
import utilities

TARGET_LOOPS_PER_SEC = 130

WINDOW_SIZE = [1700, 600]
# FULLSCREEN = True
FULLSCREEN = False
TILE_SIZE = 48

if FULLSCREEN:
    displaySurf = pygame.display.set_mode((0, 0), pygame.NOFRAME)
else:
    displaySurf = pygame.display.set_mode(WINDOW_SIZE)

pygame.display.init()

from character import Fighter
from equipment import *
from factory import Factory
from grinder import Grinder
from team import Team

team_settings = [
    {
        "name": "orange",
        "color": (255, 87, 20),
        "spawn_points": ["24x0","24x9"],
        "enemy_name": "blue"
    },
    {
        "name": "blue",
        "color": (25, 175, 255),
        "spawn_points": ["0x4"],
        "enemy_name": "orange"
    },
]

teams = {}
for team in team_settings:
    teams[team["name"]] = Team(
        grinder=None,
        name=team["name"],
        color=team["color"],
        spawn_points=team["spawn_points"],
        enemy_name=team["enemy_name"]
    )

# Set fallback targets for teams
teams["orange"].fallback_target = teams["blue"].spawn_points[0]
teams["blue"].fallback_target = teams["orange"].spawn_points[0]

def init_game():
    clock = pygame.time.Clock()
    meatGrinder = Grinder(teams, TILE_SIZE)
    factory = Factory(teams["orange"], meatGrinder)
    frame_counter = 0
    game_loop_counter = 0
    game_loop_min_delay = 0.014 # 0.014 = max 60 loops per sec
    steps_per_sec_timer = time.time()
    return(
        clock, meatGrinder, factory,
        frame_counter, game_loop_counter,
        game_loop_min_delay, steps_per_sec_timer,
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
    meatGrinder.fighterSprites[team].add(new_fighter)


def handleEvents(mouse_handler):
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
            if event.unicode.upper() == "Q" or event.scancode == 41: # 41 = ESC
                return False
            elif event.unicode.upper() == "D":
                meatGrinder.debug_layer_enabled = not(meatGrinder.debug_layer_enabled)
            elif event.unicode.upper() == "R":
                return("RESET")   # Reset game state

        elif event.type == 1024: # Mouse motion
            mouse_handler.pos = event.pos

        elif event.type == 1025: # Mouse button down
            if event.button == 1:
                mouse_handler.pos_down = event.pos
                mouse_handler.pos_up = ()

        elif event.type == 1026: # Mouse button up
            if event.button == 3:
                mouse_handler.pos_down = None
                mouse_handler.pos_up = None
            else:
                mouse_handler.pos_up = event.pos

    return True


def randomEquipments(n): # TODO: move this to Grinder
    equipmentAvailable = [Sword(), Shield(), Shirt(), Pants(), Hair(), Shoes()]
    selectedEquipment = [Skin(), Fist()]
    while len(selectedEquipment) < n:
        e = random.choice(equipmentAvailable)
        if e not in selectedEquipment:
            selectedEquipment.append(e)
    return selectedEquipment


def text_surf(text, font):
    return(
        font.render(
            text,
            True, # Antialiasing
            (40, 10, 240),
            (220, 230, 220),
        )
    )


# @utilities.time_this
def game_step(mouse_handler):
    displaySurf.fill((120, 120, 120))

    meatGrinder.step()
    if meatGrinder.step_count - factory.advanced_on_grinder_step > factory.grinder_steps_between_steps:
        factory.step(meatGrinder.step_count)
        factory.render()
    meatGrinder.render()
    factory_surf_x_pos = meatGrinder.surface.get_width() + 10

    displaySurf.blit(meatGrinder.surface, (0, 0))
    if meatGrinder.debug_layer_enabled:
        displaySurf.blit(meatGrinder.debugLayer, (0, 0))

    # Mouse debug
    start_pos = None
    end_pos = None
    path_to_mouse = []

    if mouse_handler.pos_down:
        start_pos = mouse_handler.pos_down

    if mouse_handler.pos_up and mouse_handler.pos_down:
        end_pos = mouse_handler.pos_up
        start_tile_pos = utilities.screenPosToTilePos(TILE_SIZE, start_pos)
        goal_tile_pos = utilities.screenPosToTilePos(TILE_SIZE, end_pos)
        path_to_mouse = utilities.find_path(meatGrinder.tile_map, start_tile_pos, goal_tile_pos)

    if not end_pos:
        end_pos = mouse_handler.pos

    if start_pos:
        pygame.draw.line(
            displaySurf,
            [242, 132, 45],
            start_pos,
            end_pos,
            5,
        )

    # draw path debug lines
    start_pos = None
    if path_to_mouse:
        for t in path_to_mouse:
            end_pos = utilities.tilePosToScreenPos(TILE_SIZE, t)
            if start_pos:
                pygame.draw.line(
                    displaySurf,
                    [42, 232, 45],
                    start_pos,
                    end_pos,
                    5,
                )
            start_pos = end_pos

    # draw tile info
    if mouse_handler.pos:
        tile_pos = utilities.screenPosToTilePos(TILE_SIZE, mouse_handler.pos)
        tile_id = utilities.tilePosId(tile_pos)
        mouse_hover_tile_node = None
        try:
            mouse_hover_tile_node = meatGrinder.tile_map[tile_id]
        except:
            pass

        if mouse_hover_tile_node:
            hover_info_text = "{} {}".format(tile_id, len(mouse_hover_tile_node.cached_fighters))

            displaySurf.blit(
                text_surf(hover_info_text, small_font),
                (mouse_hover_tile_node.rect.x, mouse_hover_tile_node.rect.y),
            )

            pygame.draw.rect(
                displaySurf,
                (240, 20, 100),
                mouse_hover_tile_node.rect,
                1,
            )

    displaySurf.blit(factory.surface, (factory_surf_x_pos, 0))
    pygame.display.flip()


(
    clock, meatGrinder, factory,
    frame_counter, game_loop_counter,
    game_loop_min_delay, steps_per_sec_timer
) = init_game()


small_font = pygame.font.Font('freesansbold.ttf', 12)
mouse_handler = utilities.MouseHandler()

while True:
    event_handler_status = handleEvents(mouse_handler)
    if not event_handler_status:
        break
    if event_handler_status == "RESET":
        (
            clock, meatGrinder, factory,
            frame_counter, game_loop_counter,
            game_loop_min_delay, steps_per_sec_timer
        ) = init_game()
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

        if random.randint(0, 100) < 5: # % chance to spawn new fighter on each frame
            speed = random.randint(10, 30) / 10.00
            # x_pos = 220
            x_pos = random.randint(20, 400)
            addFighter("blue", [24, x_pos], speed, randomEquipments(4))

        game_step(mouse_handler)

    clock.tick(TARGET_LOOPS_PER_SEC)


pygame.quit()
print("QUIT BYE")

