import math, time
import pygame

pygame.font.init()
font = pygame.font.SysFont("Monotype", 12)


def distTo(fromPos, toPos):
    dist = math.sqrt((fromPos[0] - toPos[0]) ** 2 + (fromPos[1] - toPos[1]) ** 2)
    return dist


def angleTo(fromPos, toPos):
    dx = toPos[0] - fromPos[0]
    dy = toPos[1] - fromPos[1]
    rads = math.atan2(dy, dx)
    rads %= 2 * math.pi
    degs = math.degrees(rads)
    return degs


def angleDistToPos(pos, angle, dist):
    movement = pygame.math.Vector2()
    movement.from_polar((dist, angle))
    movement.x = int(movement.x)
    movement.y = int(movement.y)
    x = movement.x + pos[0]
    y = movement.y + pos[1]
    return (x, y)


def dirAsCompassDir(degrees):
    degrees = int(degrees)
    if degrees >= 225 and degrees <= 315:
        compassDir = "N"
    elif degrees >= 45 and degrees <= 135:
        compassDir = "S"
    elif degrees >= 135 and degrees <= 225:
        compassDir = "W"
    elif degrees >= 315 or degrees <= 45:
        compassDir = "E"
    return compassDir


def changeColor(image, replaceWith):
    toReplace = (255, 0, 0)
    pa = pygame.PixelArray(image)
    pa.replace(toReplace, replaceWith)
    return pa.make_surface()


def tintImage(destImg, tintColor):
    tinted = destImg.copy()
    tinted.fill((0, 0, 0, 175), None, pygame.BLEND_RGBA_MULT)
    tinted.fill(tintColor[0:3] + (0,), None, pygame.BLEND_RGBA_ADD)
    return tinted


def screenPosToTilePos(tileSize, pos):
    x = int((pos[0] - 1) / tileSize)
    y = int((pos[1] - 1) / tileSize)
    # print("screen pos to tile {} -> ({}, {})".format(pos, x,y))
    return (x, y)


def tilePosToScreenPos(tileSize, pos):
    x = (pos[0] * tileSize) + tileSize / 2
    y = (pos[1] * tileSize) + tileSize / 2
    # print("tile pos to pixels {} -> {}x{}".format(pos, x,y))
    return (x, y)


def tilePosId(pos):
    return "{:.0f}x{:.0f}".format(pos[0], pos[1])


def drawDebugLayer(grinder):
    # Clear canvas
    grinder.debugLayer.fill((255, 0, 255))

    for fighter in grinder.fighters:
        # target line
        if fighter.target:
            pygame.draw.line(
                fighter.world.debugLayer,
                (20, 10, 40),
                (fighter.rect.center[0], fighter.rect.center[1]),
                (fighter.target.center[0], fighter.target.center[1]),
                1,
            )

        # hit marker
        if fighter.lastHitArea:
            pygame.draw.rect(
                fighter.world.debugLayer, (200, 30, 30), fighter.lastHitArea, 0
            )
            fighter.lastHitArea = None

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
        textsurface = font.render(fighter.state, False, (0, 0, 0))
        x, y = fighter.rect.bottomleft
        fighter.world.debugLayer.blit(textsurface, (x, y))


def time_this(func):
    def wrapper_func(*args, **kwargs):
        start_time = time.time()
        func(*args, **kwargs)
        print("{module: >10}.{name} {run_time: >25}ms".format(
            module=func.__module__,
            name=func.__name__,
            run_time=round((time.time() - start_time) * 1000, 6),     # ms
        ))
    return wrapper_func


class Detector:
    def __init__(self):
        self.detection_area = pygame.Rect(
            0, # left
            0, # top
            0, # width
            0, # heigh
        )
        self.detection_sprite = pygame.sprite.Sprite()
        self.detection_sprite.rect = self.detection_area

    def detect(self, haystack, target_area, area_scale):
        """"
        Match detection_sprite to target_area and scale up depending on the fighter skill.
        Returns list of objects in haystack that collide with the detection_area
        """
        self.detection_area.x = target_area.x * area_scale
        self.detection_area.y = target_area.y * area_scale
        self.detection_area.w = target_area.w * area_scale
        self.detection_area.h = target_area.h * area_scale
        self.detection_area.center = target_area.center

        self.detection_sprite.rect.update(self.detection_area)

        collider_dict = pygame.sprite.groupcollide(
                [self.detection_sprite],
                haystack,
                False,
                False
            )
        collider_list = collider_dict.get(self.detection_sprite, [])
        return(collider_list)