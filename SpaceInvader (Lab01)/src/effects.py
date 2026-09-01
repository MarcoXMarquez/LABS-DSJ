# src/effects.py
import pygame
import random
import math
from src.config import (
    COLOR_WHITE, COLOR_GOLD, COLOR_YELLOW, COLOR_ORANGE,
    COLOR_RED, COLOR_CYAN, COLOR_BLUE
)

class Starfield:
    """Fondo de estrellas tenue en paralaje para no distraer la visión."""
    def __init__(self, screen_width, screen_height, num_stars=140):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.stars = []
        
        for _ in range(num_stars):
            x = random.randint(0, screen_width)
            y = random.randint(0, screen_height)
            layer = random.choice([1, 2, 3])
            
            if layer == 1:
                speed = 0.5
                size = 1
                color = (40, 42, 58)
            elif layer == 2:
                speed = 1.1
                size = 1
                color = (65, 70, 90)
            else:
                speed = 2.0
                size = 2
                color = (95, 100, 125)
                
            self.stars.append([x, y, speed, size, color])

    def update(self):
        for star in self.stars:
            star[1] += star[2]
            if star[1] > self.screen_height:
                star[1] = 0
                star[0] = random.randint(0, self.screen_width)

    def draw(self, surface):
        for star in self.stars:
            x, y, _, size, color = star
            pygame.draw.circle(surface, color, (int(x), int(y)), size)


class ShockwaveRing:
    """Onda expansiva circular translúcida para detonaciones y muerte de jefes."""
    def __init__(self, x, y, max_radius=90, speed=5.5, color=COLOR_CYAN, width=3):
        self.x = x
        self.y = y
        self.radius = 4
        self.max_radius = max_radius
        self.speed = speed
        self.color = color
        self.width = width
        self.is_alive = True

    def update(self):
        self.radius += self.speed
        if self.radius >= self.max_radius:
            self.is_alive = False

    def draw(self, surface):
        if self.is_alive:
            progress = max(0.0, 1.0 - (self.radius / self.max_radius))
            w = max(1, int(self.width * progress))
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.radius), width=w)


class Particle:
    """Partícula individual para explosiones, chispas y estelas."""
    def __init__(self, x, y, vx, vy, color, radius=3, lifetime=30, fade=True):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.radius = radius
        self.max_lifetime = lifetime
        self.lifetime = lifetime
        self.fade = fade
        self.is_alive = True

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.94
        self.vy *= 0.94
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.is_alive = False

    def draw(self, surface):
        if self.is_alive:
            progress = max(0, self.lifetime / self.max_lifetime)
            current_r = max(1, int(self.radius * progress))
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), current_r)


class ParticleManager:
    """Gestiona partículas y ondas expansivas."""
    def __init__(self):
        self.particles = []
        self.shockwaves = []

    def spawn_shockwave(self, x, y, max_radius=110, color=COLOR_CYAN):
        self.shockwaves.append(ShockwaveRing(x, y, max_radius=max_radius, color=color))

    def spawn_sparks(self, x, y, color=COLOR_YELLOW, count=8):
        for _ in range(count):
            ang = random.uniform(0, 6.28)
            spd = random.uniform(2, 6)
            vx = math.cos(ang) * spd
            vy = math.sin(ang) * spd
            p = Particle(x, y, vx, vy, color, radius=random.randint(2, 3), lifetime=random.randint(14, 22))
            self.particles.append(p)

    def spawn_explosion(self, x, y, count=22, is_large=False):
        colors = [COLOR_WHITE, COLOR_YELLOW, COLOR_ORANGE, COLOR_RED, (60, 60, 60)]
        num = count * 2 if is_large else count
        for _ in range(num):
            ang = random.uniform(0, 6.28)
            spd = random.uniform(1, 7 if is_large else 4.5)
            vx = math.cos(ang) * spd
            vy = math.sin(ang) * spd
            c = random.choice(colors)
            r = random.randint(3, 6) if is_large else random.randint(2, 4)
            life = random.randint(20, 40 if is_large else 26)
            self.particles.append(Particle(x, y, vx, vy, c, radius=r, lifetime=life))
        
        # Onda expansiva
        self.spawn_shockwave(x, y, max_radius=140 if is_large else 75, color=COLOR_ORANGE if is_large else COLOR_YELLOW)

    def spawn_smoke_trail(self, x, y):
        self.particles.append(Particle(x + random.uniform(-2, 2), y, random.uniform(-0.4, 0.4), random.uniform(1, 2), (120, 120, 130), radius=2, lifetime=16))

    def update(self):
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.is_alive]

        for sw in self.shockwaves:
            sw.update()
        self.shockwaves = [sw for sw in self.shockwaves if sw.is_alive]

    def draw(self, surface):
        for sw in self.shockwaves:
            sw.draw(surface)
        for p in self.particles:
            p.draw(surface)


class FloatingText:
    """Texto flotante animado para monedas y recompensas."""
    def __init__(self, x, y, text, color=COLOR_GOLD, lifetime=50):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.is_alive = True

    def update(self):
        self.y -= 0.9
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.is_alive = False

    def draw(self, surface, font):
        if self.is_alive:
            shadow = font.render(self.text, True, (10, 10, 10))
            surface.blit(shadow, (int(self.x) + 1, int(self.y) + 1))
            txt = font.render(self.text, True, self.color)
            surface.blit(txt, (int(self.x), int(self.y)))


class FloatingTextManager:
    """Gestiona los textos flotantes en pantalla."""
    def __init__(self):
        self.texts = []

    def add_text(self, x, y, text, color=COLOR_GOLD):
        self.texts.append(FloatingText(x, y, text, color))

    def update(self):
        for t in self.texts:
            t.update()
        self.texts = [t for t in self.texts if t.is_alive]

    def draw(self, surface, font):
        for t in self.texts:
            t.draw(surface, font)


class ScreenShake:
    """Sacudida de pantalla tras impactos o explosiones pesadas."""
    def __init__(self):
        self.trauma = 0.0

    def add_trauma(self, amount):
        self.trauma = min(1.0, self.trauma + amount)

    def get_offset(self):
        if self.trauma > 0:
            shake_amt = (self.trauma ** 2) * 12
            ox = random.uniform(-shake_amt, shake_amt)
            oy = random.uniform(-shake_amt, shake_amt)
            self.trauma = max(0.0, self.trauma - 0.04)
            return int(ox), int(oy)
        return 0, 0
