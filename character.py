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
        pygame.sprite.Sprite.__init__(self)
        self.image = fighterTiles.get_tile_image(
            4, 0, 0
        ).copy()  # set naked body sprite as base image
        self.world = world
        self.rect = self.image.get_rect()
        self.rect.center = (spawnPos,)
        self.enemyDetectionAreaSize = 10
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
        self.lastHitArea = pygame.Rect((0, 0), (0, 0))
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
                "S": [],
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
            for frame in range(
                animation.ANIM_MAPPING["directions"][d],
                4 + animation.ANIM_MAPPING["directions"][d],
            ):
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

    def __str__(self):
        tile_pos = utilities.screenPosToTilePos(48, self.rect.center)
        tile_pos_id = utilities.tilePosId(tile_pos)
        return("Fighter{} Team:'{}'".format(
            tile_pos_id,
            self.team["name"],
        ))


    def findTarget(self):
        colliders = self.world.fighter_detector.detect(
            self.world.fighterSprites[self.team["enemy_name"]],
            self.rect,
            self.enemyDetectionAreaSize,
        )

        self.timeStamps[CharacterStates.search] = self.frame
        if len(colliders) > 0:
            return(colliders[0].rect)
        else:
            return pygame.Rect(
                self.world.fighterInputs[self.team["primaryTarget"]], (20, 20)
            )

    def move(self):
        compass_dir = utilities.dirAsCompassDir(self.dir)
        self.image = self.anim["MOVE"][compass_dir][self.animFrame]
        self.rect.center = utilities.angleDistToPos(
            self.rect.center,
            self.dir,
            self.speed,
        )

    def takeHit(self, hit, angle):
        armor = self.equipment.get("armor", None)
        damage = hit["baseDamage"] * hit["level"]

        if armor:
            damage *= armor.damageMultiplier

        self.spill_blood(damage, angle)

        self.health -= damage
        if self.health <= 0:
            self.die()

    def spill_blood(self, force, angle):
        bloodAmount = int(force / 6)
        if bloodAmount < 1:
            bloodAmount = 1

        for d in range(bloodAmount):
            self.world.addBloodDrop(
                pos=self.rect.center,
                dir=angle + random.randint(-10, 10),
                damage=force + random.randint(7, 10),
                color=(
                    (255 - random.randint(0, 55)) - force,
                    force,
                    force
                ),
            )

    def die(self):
        skeletonColors = [(155, 155, 105), (55, 55, 55)]
        i = 0
        for sColor in skeletonColors:
            i += 1
            bones = utilities.tintImage(self.image, sColor)
            self.world.bloodNcorpseLayer.blit(
                bones, (self.rect.center[0] - i, self.rect.center[1] - i)
            )
        self.world.fighters.remove(self)
        self.world.fighterSprites[self.team["name"]].remove(self)
        self.state = CharacterStates.dead

    def hit(self, distance):
        hit = False
        weapon = self.equipment.get("weapon", None)
        self.timeStamps["hit"] = self.frame

        # 1. define hit area
        self.lastHitArea = pygame.Rect((100, 100), (distance, distance))
        self.lastHitArea.center = utilities.angleDistToPos(
            self.rect.center, self.dir, distance
        )

        # 2. find players in the area
        enemiesInArea = [] # TODO: Use Detector
        for p in self.world.fighterSprites[self.team["enemy_name"]]:
            if self.lastHitArea.colliderect(p.rect) and p.state != "DEAD":
                enemiesInArea.append(p)

        # 3. deal damage to players
        if weapon:
            for e in enemiesInArea:
                e.takeHit(weapon.hit, self.dir)
                hit = True
        return hit

    def step(self, frame):
        self.frame = frame
        weapon = self.equipment.get("weapon", None)

        # change animation frame on every other step
        self.advAnim = not self.advAnim
        if self.advAnim:
            self.animFrame += 1
            if self.animFrame >= len(
                self.anim["MOVE"][utilities.dirAsCompassDir(self.dir)]
            ):
                self.animFrame -= len(
                    self.anim["MOVE"][utilities.dirAsCompassDir(self.dir)]
                )

        if self.frame - self.timeStamps[CharacterStates.search] > self.searchInterval:
            self.state = CharacterStates.search

        if self.state == CharacterStates.search:
            self.target = self.findTarget()
            self.dir = utilities.angleTo(self.rect.center, self.target.center)
            self.state = CharacterStates.move

        if not self.target:
            target = self.world.fighterInputs[self.team["primaryTarget"]]
            self.target = pygame.Rect(target, (3, 3))

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
