import pygame
import random
import sys
import math
import os
from urllib.request import urlretrieve

pygame.init()

# Create assets directory if it doesn't exist
if not os.path.exists('assets'):
    os.makedirs('assets')

# Font setup for Vietnamese support
def get_font():
    # Try to load font from assets folder first
    local_font = os.path.join('assets', 'NotoSans-Regular.ttf')

    if os.path.exists(local_font):
        return pygame.font.Font(local_font, 64)

    # If font doesn't exist, download it
    import urllib.request
    font_url = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Regular.ttf"

    try:
        print("Downloading font file for Vietnamese support...")
        urllib.request.urlretrieve(font_url, local_font)
        return pygame.font.Font(local_font, 64)
    except:
        print("Warning: Could not download Vietnamese font. Falling back to system font.")
        system_fonts = [
            "arial.ttf",
        ]

        for font_path in system_fonts:
            if os.path.exists(font_path):
                return pygame.font.Font(font_path, 64)

        return pygame.font.Font(None, 64)

VIETNAMESE_FONT = get_font()

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

# Countdown state
COUNTDOWN_DURATION = 10  # seconds
countdown_start_time = None
show_countdown = True
show_new_year = False
fireworks_started = False

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SRCALPHA)
pygame.display.set_caption("Fireworks Game")

clock = pygame.time.Clock()

names = ["Actiup", "Sếp Tuấn", "Anh Tài", "Anh Chung", "Anh Duy", "Anh Vương", "Thành", "Nghĩa"]
name_index = 0

# Add after creating assets directory, before SOUND_FILES
def download_sound(filename, url):
    sound_path = os.path.join('assets', filename)
    if not os.path.exists(sound_path):
        print(f"Downloading {filename}...")
        try:
            urlretrieve(url, sound_path)
        except Exception as e:
            print(f"Failed to download {filename}: {e}")
            return None
    return sound_path

SOUND_FILES = {
    'countdown': ('countdown.wav', 'https://assets.mixkit.co/active_storage/sfx/2568/2568.wav'),
    'happy_new_year': ('happy_new_year.mp3', None),
    'firework_sound': ('fireworks.mp3', None),
    'background_music': ('happynewyear.mp3', None)
}

sounds = {}
pygame.mixer.init()
for sound_name, (filename, url) in SOUND_FILES.items():
    sound_path = os.path.join('assets', filename)
    if os.path.exists(sound_path):
        try:
            sounds[sound_name] = pygame.mixer.Sound(sound_path)
            print(f"Loaded {sound_name} sound from local file")
        except:
            print(f"Warning: Could not load {sound_name} sound")
            sounds[sound_name] = None
    elif url:
        sound_path = download_sound(filename, url)
        if sound_path and os.path.exists(sound_path):
            sounds[sound_name] = pygame.mixer.Sound(sound_path)
        else:
            sounds[sound_name] = None
            print(f"Warning: Could not load {sound_name} sound")

for sound_name, sound in sounds.items():
    if sound:
        if sound_name == 'firework_sound':
            sound.set_volume(0.15)
        elif sound_name == 'background_music':
            sound.set_volume(0.6)
        else:
            sound.set_volume(0.5)

class Firework:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = random.choice(BRIGHT_COLORS)
        self.radius = random.randint(4, 8)
        self.velocity = random.uniform(-10, -6)
        self.sparks = []
        self.name_sparks = []
        self.exploded = False
        self.explosion_radius = random.randint(20, 40)  # Control explosion size
        if sounds['firework_sound']:
            sounds['firework_sound'].play()

    def update(self):
        if not self.exploded:
            self.y += self.velocity
            if self.y <= HEIGHT / 2:
                self.explode()

    def explode(self):
        global name_index
        self.exploded = True
        if sounds['firework_sound']:
            sounds['firework_sound'].play()
        for _ in range(200):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 8)
            vx = speed * math.cos(angle)
            vy = speed * math.sin(angle)
            self.sparks.append(Spark(self.x, self.y, vx, vy, self.color))

        self.name = names[name_index]
        name_index = (name_index + 1) % len(names)

        self.font = VIETNAMESE_FONT
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

            if hasattr(self, 'font'):
                for offset_x, offset_y in [(-3,0), (3,0), (0,-3), (0,3), (-3,-3), (-3,3), (3,-3), (3,3)]:
                    text_outline = self.font.render(self.name, True, (0, 0, 0))
                    outline_rect = text_outline.get_rect(center=(self.text_pos[0] + offset_x, self.text_pos[1] + offset_y))
                    surface.blit(text_outline, outline_rect)

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
            alpha = int((self.lifetime / self.original_lifetime) * 255)
            radius = max(1, self.size * (self.lifetime / self.original_lifetime))

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
            for r in range(2):
                glow_alpha = alpha // (r+1)
                color = (*self.color[:3], glow_alpha)
                radius = self.size * (2-r)/2
                pygame.draw.circle(surface, color, (int(self.x), int(self.y)), int(radius))

fireworks = []
frame_count = 0
running = True
clock = pygame.time.Clock()
countdown_start_time = pygame.time.get_ticks()
last_countdown_number = COUNTDOWN_DURATION + 1  # For countdown sound tracking

background_music_started = False

def draw_centered_text(text, y_position, color=WHITE, size=64):
    if size == 64:
        font = VIETNAMESE_FONT
    else:
        font = pygame.font.Font(os.path.join('assets', 'NotoSans-Regular.ttf'), size)
    
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(WIDTH/2, y_position))
    
    outline_color = BLACK
    for offset_x, offset_y in [(-2,0), (2,0), (0,-2), (0,2)]:
        outline_surface = font.render(text, True, outline_color)
        outline_rect = outline_surface.get_rect(center=(WIDTH/2 + offset_x, y_position + offset_y))
        screen.blit(outline_surface, outline_rect)
    
    screen.blit(text_surface, text_rect)

while running:
    current_time = pygame.time.get_ticks()
    
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 25))
    screen.blit(overlay, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if show_countdown:
        elapsed_time = (current_time - countdown_start_time) // 1000
        remaining_time = COUNTDOWN_DURATION - elapsed_time
        
        if remaining_time != last_countdown_number and remaining_time > 0:
            if sounds['countdown']:
                sounds['countdown'].play()
            last_countdown_number = remaining_time
        
        if remaining_time > 0:
            draw_centered_text(str(remaining_time), HEIGHT//2, WHITE, 120)
        else:
            show_countdown = False
            show_new_year = True
            new_year_start_time = current_time
            if sounds['happy_new_year']:
                sounds['happy_new_year'].play()

    elif show_new_year:
        if current_time - new_year_start_time < 2000:
            draw_centered_text("Happy New Year", HEIGHT//3, WHITE, 100)
            draw_centered_text("2025", HEIGHT//2, WHITE, 120)
        else:
            show_new_year = False
            fireworks_started = True
            if sounds['background_music'] and not background_music_started:
                sounds['background_music'].play(-1)
                background_music_started = True

    elif fireworks_started:
        frame_count += 1
        if frame_count % 120 == 0:
            for _ in range(random.randint(1, 2)):
                x = random.randint(100, WIDTH - 100)
                fireworks.append(Firework(x, HEIGHT))

        for firework in fireworks[:]:
            firework.update()
            firework.draw(screen)
            if firework.exploded and all(spark.lifetime <= 0 for spark in firework.sparks):
                fireworks.remove(firework)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
