import pygame, random, time
import utilities


class GrinderMapTileNode:
    def __init__(self, grinder, x, y):
        self.grinder = grinder
        self.cached_fighters = []
        self.x = x
        self.y = y
        self.occupancy = "EMPTY"
        self.tile_size = self.grinder.tile_size
        self.rect = pygame.Rect(0, 0, self.tile_size, self.tile_size)
        self.rect.bottomright = [
            x * self.tile_size,
            y * self.tile_size
        ]

    def __str__(self):
        return("GrinderMapTileNode@{}x{}".format(self.x, self.y))

    def fighters(self):
        fighters_on_tile = [
            f for f in self.grinder.fighters
                if self.rect.collidepoint(f.rect.center)
        ]
        return(fighters_on_tile)


class Grinder:
    def __init__(self, teams, tile_size):
        print("grinder init")
        pygame.font.init()
        self.last_step_time = time.time()
        self.surface = pygame.Surface((1200, 480))
        self.debug_layer_enabled = False
        self.debugLayer = pygame.Surface(self.surface.get_rect().size)
        self.debugLayer.set_colorkey((255, 0, 255))
        self.debugLayer.fill((255, 0, 255))
        self.bloodNcorpseLayer = pygame.Surface(self.surface.get_rect().size)
        self.bloodNcorpseLayer.fill((255, 255, 255))  # TODO: draw the fight arena here
        self.bloodNcorpseLayer.set_colorkey((255, 0, 255))
        self.bloodDropLayer = pygame.Surface(self.surface.get_rect().size)
        self.bloodDropLayer.set_colorkey((0, 0, 0))
        self.font = pygame.font.SysFont("Monotype", 12)
        self.fighter_detector = utilities.Detector()
        self.fighters = []
        self.teams = teams
        self.bloodDrops = []
        self.step_count = 0
        self.tile_size = tile_size

        self.fighterSprites = {
            "orange": pygame.sprite.Group(),
            "blue": pygame.sprite.Group(),
        }

        x, y = self.surface.get_rect().size
        map_width = int(x / self.tile_size)
        map_height = int(y / self.tile_size)

        self.tile_map = {}
        for y in range(1, map_height +1):   # Generate path map with EMPTY nodes
            self.tile_map.update({"{}x{}".format(x, y): GrinderMapTileNode(self, x, y) for x in range(1, map_width +1)})

        self.tile_render_order = sorted(self.tile_map, key=lambda x: x.split("x")[1])

        self.fighterInputs = {
            "0x0": "25x1",   #  factory out: grinder in
            "0x9": "25x10",
            "5x5": "1x5",
        }

        self.path_finding_costs = {
            "EMPTY": 0,
            "FIGHTER": 20,
            "BLOCK": 100,
        }

    def step(self):
        self.step_count += 1
        self.last_step_time = time.time()

        # Detect player positions and construct 'open map' for path finding
        for location_str, tile_node in self.tile_map.items():
            tile_node.cached_fighters = tile_node.fighters()

        open_map = {
            location_str: tile_node
                for location_str, tile_node in self.tile_map.items()
                    if not tile_node.cached_fighters
        }
        tiles_list = [1 if y.cached_fighters else 0 for x, y in self.tile_map.items()]
        world = [tiles_list[x:x+25] for x in range(0, len(tiles_list), 25)]

        for location_str, tile_node in self.tile_map.items():
            for f in tile_node.cached_fighters:
                f.step(self.step_count, world)


    def addBloodDrop(self, pos=None, dir=None, damage=None, color=None):
        if None in [pos, dir, damage, color]:
            raise Exception("Can't add blood!")

        if len(self.bloodDrops) > 1000:  # limit drawing of blood
            draw = random.randint(0, 9) < 4  # 40% chance to draw if over 1000 drops
        else:
            draw = True

        if draw:
            self.bloodDrops.append(
                {
                    "spiltOnFrame": self.step_count,
                    "damage": damage,
                    "dir": dir,
                    "speed": 7,
                    "pos": pos,
                    "color": color,
                }
            )

    def drawBlood(self):
        self.bloodDropLayer.fill((0, 0, 0))

        for b in self.bloodDrops:
            lifeTime = self.step_count - b["spiltOnFrame"]
            x = b["pos"][0]
            y = b["pos"][1]
            x, y = utilities.angleDistToPos(b["pos"], b["dir"], lifeTime * b["speed"])

            if lifeTime > b["damage"] * 0.5:
                bloodSize = 5
                targetLayer = self.bloodNcorpseLayer
                color = b["color"]
                self.bloodDrops.remove(b)
            else:
                bloodSize = 3
                targetLayer = self.bloodDropLayer
                color = b["color"]

                hilight = pygame.Rect((0, 0), (bloodSize, bloodSize))
                hilight.center = [x - 1, y - 1]

                pygame.draw.rect(targetLayer, (250, 150, 150), hilight, 2)

            drop = pygame.Rect((0, 0), (bloodSize, bloodSize))
            drop.center = [x, y]

            pygame.draw.rect(targetLayer, color, drop, 0)

        pygame.Surface.blit(self.surface, self.bloodNcorpseLayer, [0, 0])
        pygame.Surface.blit(self.surface, self.bloodDropLayer, [0, 0])

    def drawDebugLayer(self):
        # Clear canvas
        self.debugLayer.fill((255, 0, 255))

        # Draw path to target
        for fighter in self.fighters:
            if fighter.path:
                last_point = fighter.rect.center
                for point in fighter.path:
                    x, y = utilities.tilePosToScreenPos(self.tile_size, point)
                    pygame.draw.line(
                        fighter.world.debugLayer,
                        (220, 20, 50),
                        last_point,
                        (x, y),
                        1
                    )
                    last_point = (x, y)

        # Draw AStar debug lines from mouse
        # TODO

        for fighter in self.fighters:
            # target line
            if fighter.target:
                pygame.draw.line(
                    fighter.world.debugLayer,
                    (20, 10, 40),
                    (fighter.rect.center[0], fighter.rect.center[1]),
                    (fighter.target.rect.center[0], fighter.target.rect.center[1]),
                    1,
                )

            # health bar
            x, y = fighter.rect.bottomleft
            pygame.draw.line(
                fighter.world.debugLayer,
                (20, 130, 30),
                (x, y),
                (x + (fighter.health / 100) * fighter.rect.width, y),
                3,
            )

            # state text
            textsurface = self.font.render(fighter.state, False, (0, 0, 0))
            x, y = fighter.rect.bottomleft
            fighter.world.debugLayer.blit(textsurface, (x, y))

    def listEnemies(self, team_name):
        """
        List enemy fighters for a given team.
        """
        return [x for x in self.fighters if x.team["name"] != team_name]

    def render(self):
        self.drawBlood()
        self.drawDebugLayer()

        # # Draw fighters by team and sprite group
        # for name, team in self.fighterSprites.items():
        #     team.draw(self.surface)

        # Draw fighters individually in layers (propably slower)
        for location_str in self.tile_render_order:
            tile = self.tile_map[location_str]
            for f in tile.cached_fighters:
                pygame.Surface.blit(
                    self.surface,
                    f.image,
                    [
                        f.rect.x,
                        f.rect.y
                    ],
                )

