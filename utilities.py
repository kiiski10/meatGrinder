import pygame, math

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
