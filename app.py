import sys, pygame, random
from pygame.locals import *
from classes import Rocket, Population

pygame.init()
WIN_WIDTH = 800
WIN_HEIGHT = 600
size = WIN_WIDTH, WIN_HEIGHT
WIN = pygame.display.set_mode(size)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = pygame.Color("red")
GREEN = pygame.Color("green")
BLUE = pygame.Color("blue")
TARGET = pygame.math.Vector2(WIN_WIDTH/2, 75)
LIFESPAN = 225
FRAMECOUNT = 0

def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

# Barrier
rx = 250
ry = 275
rw = 300
rh = 10

rocket_pop = Population(WIN)
clock = pygame.time.Clock()

font = pygame.font.Font('freesansbold.ttf', 11) 
 
generation = 1
running = True
while running:
    clock.tick(50)
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Will change this once population is implemented fully.
                rocket_pop.rockets.append(Rocket(WIN, False))

    
    WIN.fill(BLACK)
    pygame.draw.rect(WIN,RED,(rx, ry, rw, rh,))
    pygame.draw.ellipse(WIN, WHITE, (int(WIN_WIDTH/2), 50, 20, 20))

    rocket_pop.run(FRAMECOUNT)

    FRAMECOUNT += 1
    if FRAMECOUNT == LIFESPAN:
        rocket_pop.evaluate()
        rocket_pop.selection()
        FRAMECOUNT = 0
        print(f"Generation: {generation}")
        generation += 1


    for rocket in rocket_pop.rockets:
        text = font.render(str(rocket.id), True, GREEN) 
        textRect = text.get_rect()  
        textRect.center = (rocket.position.x, rocket.position.y+10)
        WIN.blit(text, textRect) 
        if rocket.completed:
            pygame.draw.ellipse(WIN, RED, (int(WIN_WIDTH/2), 50, 20, 20))
    pygame.display.update()