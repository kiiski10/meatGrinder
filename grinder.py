import pygame, random, time
import utilities


class Grinder:
    def __init__(self, teams, debug=False):
        print("grinder init")
        self.debug = debug
        self.last_step_time = time.time()
        self.surface = pygame.Surface((1200, 480))
        self.debugLayer = pygame.Surface(self.surface.get_rect().size)
        self.debugLayer.set_colorkey((255, 0, 255))
        self.debugLayer.fill((255, 0, 255))
        self.bloodNcorpseLayer = pygame.Surface(self.surface.get_rect().size)
        self.bloodNcorpseLayer.fill((255, 255, 255))  # TODO: draw the fight arena here
        self.bloodNcorpseLayer.set_colorkey((255, 0, 255))
        self.bloodDropLayer = pygame.Surface(self.surface.get_rect().size)
        self.bloodDropLayer.set_colorkey((0, 0, 0))
        self.fighter_detector = utilities.Detector()
        self.fighters = []
        self.fighterSprites = {
            "orange": pygame.sprite.Group(),
            "blue": pygame.sprite.Group(),
        }
        self.teams = teams
        self.bloodDrops = []
        self.step_count = 0
        self.fighterInputs = {
            "0x0": [1160, 0],
            "0x9": [1160, 430],
            "2x2": [10, 200],
            "2x2": [10, 200],
        }

    def step(self):
        self.step_count += 1
        self.last_step_time = time.time()

        for f in self.fighters:
            f.step(self.step_count)

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

    def listEnemies(self, team_name):
        """
        List enemy fighters for a given team.
        """
        return [x for x in self.fighters if x.team["name"] != team_name]

    def render(self):
        self.drawBlood()
        utilities.drawDebugLayer(self)
        for name, team in self.fighterSprites.items():
            team.draw(self.surface)
