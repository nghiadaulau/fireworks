import pygame
import random
import sys
import math

pygame.init()

WIDTH, HEIGHT = 800, 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
COLORS = [RED, GREEN, BLUE, YELLOW]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fireworks Game")

clock = pygame.time.Clock()

names = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
name_index = 0

class Firework:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = random.choice(COLORS)
        self.radius = random.randint(2, 5)
        self.velocity = random.uniform(-5, -2)
        self.sparks = []
        self.exploded = False

    def update(self):
        if not self.exploded:
            self.y += self.velocity
            if self.y <= HEIGHT / 2:
                self.explode()

    def explode(self):
        global name_index
        self.exploded = True
        for _ in range(100):  # Increase the number of sparks
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            vx = speed * math.cos(angle)
            vy = speed * math.sin(angle)
            self.sparks.append(Spark(self.x, self.y, vx, vy, self.color))
        self.name = names[name_index]
        name_index = (name_index + 1) % len(names)

    def draw(self, surface):
        if not self.exploded:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        else:
            for spark in self.sparks:
                spark.update()
                spark.draw(surface)
            if self.sparks:
                font = pygame.font.Font(None, 36)
                text = font.render(self.name, True, self.color)  # Use the firework color for the name
                text_rect = text.get_rect(center=(self.x, self.y - 20))
                surface.blit(text, text_rect)

class Spark:
    def __init__(self, x, y, vx, vy, color):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = random.randint(20, 40)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1  # Simulate gravity
        self.lifetime -= 1

    def draw(self, surface):
        if self.lifetime > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), 2)

fireworks = []
frame_count = 0
running = True
while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    frame_count += 1
    if frame_count % 60 == 0:
        for _ in range(random.randint(1, 3)):
            x = random.randint(100, WIDTH - 100)
            fireworks.append(Firework(x, HEIGHT))

    for firework in fireworks[:]:
        firework.update()
        firework.draw(screen)
        if firework.exploded and all(spark.lifetime <= 0 for spark in firework.sparks):
            fireworks.remove(firework)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
