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

# Add new bright colors with higher RGB values
BRIGHT_COLORS = [
    (255, 120, 120),  # Bright red
    (120, 255, 120),  # Bright green
    (120, 120, 255),  # Bright blue
    (255, 255, 120),  # Bright yellow
    (255, 120, 255),  # Bright pink
    (120, 255, 255),  # Bright cyan
    (255, 200, 120),  # Bright orange
]

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SRCALPHA)
pygame.display.set_caption("Fireworks Game")

clock = pygame.time.Clock()

names = ["Kai", "Kiera", "Anh Chung", "Vưnn"]
name_index = 0

class Firework:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = random.choice(BRIGHT_COLORS)
        self.radius = random.randint(4, 8)  # Larger initial radius
        self.velocity = random.uniform(-10, -6)  # Faster launch
        self.sparks = []
        self.name_sparks = []
        self.exploded = False
        self.explosion_radius = random.randint(20, 40)  # Control explosion size

    def update(self):
        if not self.exploded:
            self.y += self.velocity
            if self.y <= HEIGHT / 2:
                self.explode()

    def explode(self):
        global name_index
        self.exploded = True
        # Create more sparks for a denser explosion
        for _ in range(200):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 8)
            vx = speed * math.cos(angle)
            vy = speed * math.sin(angle)
            self.sparks.append(Spark(self.x, self.y, vx, vy, self.color))

        self.name = names[name_index]
        name_index = (name_index + 1) % len(names)

        # Store text rendering information for later use
        self.font = pygame.font.Font(None, 64)  # Even larger font size
        self.text_color = self.color
        self.text_pos = (self.x, self.y - 40)

    def draw(self, surface):
        if not self.exploded:
            for i in range(3):
                trail_pos = (int(self.x), int(self.y + i * 5))
                trail_radius = self.radius - i
                if trail_radius > 0:
                    pygame.draw.circle(surface, self.color, trail_pos, trail_radius)
        else:
            for spark in self.sparks:
                spark.update()
                spark.draw(surface)
            
            # Draw text with outline for better readability
            if hasattr(self, 'font'):
                # Draw outline (black border)
                for offset_x, offset_y in [(-2,0), (2,0), (0,-2), (0,2), (-2,-2), (-2,2), (2,-2), (2,2)]:
                    text_outline = self.font.render(self.name, True, (0, 0, 0))
                    outline_rect = text_outline.get_rect(center=(self.text_pos[0] + offset_x, self.text_pos[1] + offset_y))
                    surface.blit(text_outline, outline_rect)
                
                # Draw main text
                text_surface = self.font.render(self.name, True, self.text_color)
                text_rect = text_surface.get_rect(center=self.text_pos)
                surface.blit(text_surface, text_rect)

class Spark:
    def __init__(self, x, y, vx, vy, color):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = random.randint(40, 70)  # Longer lifetime
        self.original_lifetime = self.lifetime
        self.size = random.uniform(1.5, 3.0)  # Larger sparks

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1
        self.lifetime -= 1

    def draw(self, surface):
        if self.lifetime > 0:
            # Create a glowing effect
            alpha = int((self.lifetime / self.original_lifetime) * 255)
            radius = max(1, self.size * (self.lifetime / self.original_lifetime))
            
            # Draw multiple circles for glow effect
            for r in range(3):
                glow_radius = radius * (3-r)/2
                glow_alpha = alpha // (r+1)
                color = (*self.color[:3], glow_alpha)
                pygame.draw.circle(surface, color, (int(self.x), int(self.y)), int(glow_radius))

class NameSpark:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.lifetime = random.randint(30, 50)  # Longer lifetime
        self.original_lifetime = self.lifetime
        self.offset_x = random.uniform(-0.3, 0.3)
        self.offset_y = random.uniform(-0.3, 0.3)
        self.size = random.uniform(1.5, 2.5)  # Larger text sparks

    def update(self):
        self.x += self.offset_x
        self.y += self.offset_y
        self.lifetime -= 1

    def draw(self, surface):
        if self.lifetime > 0:
            alpha = int((self.lifetime / self.original_lifetime) * 255)
            # Create a glowing effect for text sparks
            for r in range(2):
                glow_alpha = alpha // (r+1)
                color = (*self.color[:3], glow_alpha)
                radius = self.size * (2-r)/2
                pygame.draw.circle(surface, color, (int(self.x), int(self.y)), int(radius))

fireworks = []
frame_count = 0
running = True
while running:
    # Create a semi-transparent black overlay for better trail effect
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 25))  # Reduced alpha for longer trails
    screen.blit(overlay, (0, 0))

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
