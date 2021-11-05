import pygame, math

pygame.font.init()
font = pygame.font.SysFont('Monotype', 12)

def distTo(fromPos, toPos):
	dist = math.sqrt((fromPos[0] - toPos[0]) ** 2 + (fromPos[1] - toPos[1]) ** 2)
	return(dist)

def angleTo(fromPos, toPos):
	dx = toPos[0] - fromPos[0]
	dy = toPos[1] - fromPos[1]
	rads = math.atan2(dy,dx)
	rads %= 2*math.pi
	degs = math.degrees(rads)
	return(degs)

def angleDistToPos(pos, angle, dist):
	movement = pygame.math.Vector2()
	movement.from_polar((dist, angle))
	movement.x = int(movement.x)
	movement.y = int(movement.y)
	x = movement.x + pos[0]
	y = movement.y + pos[1]
	return(x,y)

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
	return(compassDir)

def changeColor(image, replaceWith):
	toReplace = (255,0,0)
	pa = pygame.PixelArray(image)
	pa.replace(toReplace, replaceWith)
	return(pa.make_surface())

def tintImage(destImg, tintColor):
	tinted = destImg.copy()
	tinted.fill((0, 0, 0, 175), None, pygame.BLEND_RGBA_MULT)
	tinted.fill(tintColor[0:3] + (0,), None, pygame.BLEND_RGBA_ADD)
	return(tinted)

def screenPosToTilePos(tileSize, pos):
	x = int((pos[0] -1) / tileSize)
	y = int((pos[1] -1) / tileSize)
	# print("screen pos to tile {} -> ({}, {})".format(pos, x,y))
	return(x, y)

def tilePosToScreenPos(tileSize, pos):
	x = (pos[0]  * tileSize) + tileSize / 2
	y = (pos[1]  * tileSize) + tileSize / 2
	# print("tile pos to pixels {} -> {}x{}".format(pos, x,y))
	return(x, y)

def tilePosId(pos):
	return("{:.0f}x{:.0f}".format(pos[0], pos[1]))

def drawDebugLayer(grinder):
	# target line
	if grinder.target:
		pygame.draw.line(
			grinder.world.debugLayer,
			(20, 10, 40),
			(grinder.rect.center[0] + 24, grinder.rect.center[1] + 24),
			(grinder.target.center[0] + 24, grinder.target.center[1] + 24),
			1
		)

	# hit marker
	if grinder.lastHitArea:
		pygame.draw.rect(
			grinder.world.debugLayer,
			(200, 30, 30),
			grinder.lastHitArea,
			0
		)
		grinder.lastHitArea = None

	# health bar
	x = grinder.rect.x + grinder.rect.width * 0.5
	y = grinder.rect.y + grinder.rect.height * 1.5

	pygame.draw.line(
		grinder.world.debugLayer,
		(20, 130, 30),
		(x,y), (x + (grinder.health / 100) * grinder.rect.width, y),
		3
	)

	# state text
	textsurface = font.render(grinder.state, False, (0, 0, 0))
	x = grinder.rect.x + grinder.rect.width * 0.5
	y = grinder.rect.y + grinder.rect.height * 1.5
	grinder.world.debugLayer.blit(textsurface,(x,y))
