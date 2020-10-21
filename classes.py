import pygame
from pygame.locals import *
import random as r
import math
import itertools

# Barrier
rx = 250
ry = 275
rw = 300
rh = 10

# GLOBALS
LIFESPAN = 225

def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

class DNA():
    def __init__(self, genes):
        if genes:
            self.genes = genes
        else:
            self.genes = []
            for i in range(LIFESPAN):
                self.genes.append(pygame.math.Vector2(r.uniform(-1, 1), r.uniform(-1,1)))

    def crossover(self, partner):
        newgenes = []
        # Select random gene
        gene = math.floor(r.randint(0, len(self.genes)))

        for i in range(len(self.genes)):
            if i > gene:
                newgenes.append(self.genes[i])
            else:
                newgenes.append(partner.genes[i])

        return DNA(newgenes)
    
    def mutation(self):
        for i in range(len(self.genes)):
            # if random number less than 0.01, new gene is then random vector
            rand = r.random()
            if rand < 0.01:
                self.genes[i] = pygame.math.Vector2(r.uniform(-1, 1), r.uniform(-1, 1))
    

class Population():
    def __init__(self, win):
        self.win = win
        self.rockets = []
        self.popsize = 25
        self.matingpool = []
        i = 0
        while i < self.popsize:
            self.rockets.append(Rocket(self.win, False))
            i += 1

    def selection(self):
        newRockets = []
        for i in range(len(self.rockets)):
            # Picks random dna
            parentA = r.choice(self.matingpool)
            parentB = r.choice(self.matingpool)
            parentA_dna = parentA.dna
            parentB_dna = parentB.dna
            parentA_id = parentA.id
            parentB_id = parentB.id
            #print(f"Mating: {parentA_id} AND {parentB_id}")
            # Creates child by using crossover function
            child = parentA_dna.crossover(parentB_dna)
            child.mutation()
            # Creates new rocket with child dna
            newRockets.append(Rocket(self.win, child))

        # This instance of rockets are the new rockets
        self.rockets = newRockets

    def evaluate(self):
        maxfit = 0
        # Iterate through all rockets and calcultes their fitness
        i = 0
        while i < self.popsize:
            # Calculates fitness
            self.rockets[i].calcFitness()
            # If current fitness is greater than max, then make max equal to current
            if self.rockets[i].fitness > maxfit:
                maxfit = self.rockets[i].fitness
            i += 1
        #print(maxfit)
        # Normalises fitnesses
        i = 0
        while i < self.popsize:
            self.rockets[i].fitness /= maxfit
            print(f"Normalized Fitness: {self.rockets[i].fitness}")
            i += 1

        self.matingpool = []
        # Take rockets fitness make in to scale of 1 to 100
        # A rocket with high fitness will highly likely will be in the mating pool
        i = 0
        while i < self.popsize:
            n = self.rockets[i].fitness * 100
            j = 0
            while j < n:
                self.matingpool.append(self.rockets[i])
                j += 1
            i += 1

    def run(self, frame_count):
        for i in range(self.popsize):
            self.rockets[i].move(frame_count)
            self.rockets[i].draw()

class Rocket(pygame.sprite.Sprite):
    id_iter = itertools.count()
    def __init__(self, win, dna):
        super(Rocket, self).__init__()
        self.id = next(Rocket.id_iter)

        self.original_image = pygame.Surface((32, 32))
        pygame.draw.aalines(self.original_image, (255, 255, 255), True, [(16, 0), (0, 31), (31, 31)])
        self.image = self.original_image  # This will reference our rotated copy.
        self.rect  = self.image.get_rect()
        self.win = win
        self.WIN_WIDTH, self.WIN_HEIGHT = win.get_size()

        self.position = pygame.math.Vector2(self.WIN_WIDTH/2, self.WIN_HEIGHT-50)
        self.velocity = pygame.math.Vector2()
        self.accel = pygame.math.Vector2()
        self.collision = False
        self.completed = False
        self.fitness = 0

        if dna:
            self.dna = dna
        else:
            self.dna = DNA(False)
    def applyForce(self, force):
        self.accel += force

    def calcFitness(self):
        target_pos = pygame.math.Vector2(400, 75)
        distance = math.hypot(target_pos.x-self.position.x, target_pos.y-self.position.y)
        self.fitness = translate(distance, 0, self.WIN_WIDTH, self.WIN_WIDTH, 0)
        if self.completed:
            self.fitness *= 15
        if self.collision:
            self.fitness /= 10


    def move(self, frame_count):
        # Rocket has hit left or right of window
        if self.position.x > self.WIN_WIDTH or self.position.x < 0:
            self.collision = True

        # Rocket has hit top or bottom of window
        if self.position.y > self.WIN_HEIGHT or self.position.y < 0:
            self.collision = True

        # Rocket hit the barrier
        crash_conditions = (
            self.position.x > rx and
            self.position.x < rx + rw and
            self.position.y > ry and
            self.position.y < ry + rh
        )
        if crash_conditions:
            self.collision = True
        # Create a vector pointing at the target position.
        target_pos = pygame.math.Vector2(400, 75)
        # Create a vector pointing from the image towards the target position.
        relative_target_pos = target_pos - self.position

        distance = math.hypot(target_pos.x-self.position.x, target_pos.y-self.position.y)
        if distance <= 25:
            self.completed = True

        # Calculate the angle between the y_axis and the vector pointing from the image towards the target position.
        y_axis = pygame.math.Vector2(0, -1)
        self.angle  = -y_axis.angle_to(relative_target_pos)  # Subtracting because pygame rotates counter-clockwise.
        
        # Create the rotated copy.
        self.image = pygame.transform.rotate(self.original_image, self.angle).convert()  # Angle is absolute value!
        

        # Make sure your rect represent the actual Surface.
        self.rect = self.image.get_rect()
        # Since the dimension probably changed you should move its center back to where it was.
        self.rect.center = self.position.x, self.position.y

        # applies the random vectors defined in dna to consecutive frames of rocket
        self.applyForce(self.dna.genes[frame_count])

        # if rocket has not got to goal and not crashed then update physics engine
        if not self.completed and not self.collision:
            self.velocity += self.accel
            self.position += self.velocity
            self.accel *= 0
            #self.vel.limit(4)

    def draw(self):
        self.win.blit(self.image, self.rect)



