import pygame, math

def angleDistToPos(pos, angle, dist):
	x = pos[0] + (math.cos(angle) * dist)
	y = pos[1] - (math.sin(angle) * dist)
	return(x, y)

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
