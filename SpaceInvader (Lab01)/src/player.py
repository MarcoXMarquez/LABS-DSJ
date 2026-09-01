# src/player.py
import pygame
import math
import os
import random
from src.config import (
    PLAYER_SPEED, PLAYER_MAX_HP, PLAYER_START_LIVES,
    PLAYER_INVULNERABLE_TIME,
    COLOR_CYAN, COLOR_WHITE, COLOR_BLUE, COLOR_GOLD, COLOR_ORANGE, COLOR_YELLOW, COLOR_RED
)
from src.drops import (
    POWER_FIRE, POWER_ICE, POWER_SHIELD, POWER_ELECTRO,
    POWER_VOID, POWER_SPEED, POWER_HEALTH, POWER_FUEL, ALL_POWERS
)


class Player:
    """Jugador con 4 direcciones, sistema de evolución 2 en 2, Dash, Fuel, Sinergias y Animación de Muerte."""

    def __init__(self, screen_width, screen_height, image_path='player.png'):
        if os.path.exists('assets/images/player.png'):
            self.image = pygame.image.load('assets/images/player.png').convert_alpha()
        elif os.path.exists(image_path):
            self.image = pygame.image.load(image_path).convert_alpha()
        else:
            self.image = pygame.Surface((64, 64), pygame.SRCALPHA)
            pygame.draw.polygon(self.image, COLOR_CYAN, [(32, 4), (60, 60), (4, 60)])

        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.mask = pygame.mask.from_surface(self.image)

        self.screen_width = screen_width
        self.screen_height = screen_height

        self.x = screen_width // 2 - self.width // 2
        self.y = screen_height - self.height - 40
        self.base_speed = PLAYER_SPEED
        self.speed = self.base_speed

        # Salud y Vidas
        self.max_hp = PLAYER_MAX_HP
        self.hp = self.max_hp
        self.lives = PLAYER_START_LIVES
        self.is_alive = True
        
        # Animación de Muerte en Cadena
        self.is_dying = False
        self.death_timer = 0
        self.death_duration = 75 # frames (~1.25s)

        # Inmunidad
        self.is_invulnerable = False
        self.invulnerable_timer = 0
        self.last_damage_time = 0

        # Sistema de Progresión
        self.power_orbs = {p: 0 for p in ALL_POWERS}
        self.powers = {p: 0 for p in ALL_POWERS}
        self.synergies = []

        # Combustible
        self.max_fuel = 60
        self.fuel = self.max_fuel

        # Dash
        self.is_dashing = False
        self.dash_timer = 0
        self.dash_cooldown = 0
        self.dash_dir = [0, 0]

        # Escudo
        self.shield_charges = 0
        self.max_shield = 0

        # Monedas
        self.coins = 0

        # Alerta de pérdida de vida
        self.life_lost_alert_until = 0

    def add_coins(self, amount):
        self.coins += amount

    def collect_power(self, power_type):
        self.power_orbs[power_type] += 1
        cnt = self.power_orbs[power_type]

        old_lvl = self.powers[power_type]
        new_lvl = old_lvl

        if cnt == 1 and old_lvl < 1: new_lvl = 1
        elif cnt == 2 and old_lvl < 2: new_lvl = 2
        elif cnt == 4 and old_lvl < 3: new_lvl = 3

        self.powers[power_type] = new_lvl

        if power_type == POWER_SPEED:
            self.speed = self.base_speed + (new_lvl * 1.6)

        elif power_type == POWER_HEALTH:
            self.max_hp = PLAYER_MAX_HP + (new_lvl * 15)
            self.hp = min(self.max_hp, self.hp + 15)

        elif power_type == POWER_FUEL:
            fuel_caps = {1: 60, 2: 100, 3: 120}
            self.max_fuel = fuel_caps.get(new_lvl, 60)

        elif power_type == POWER_SHIELD:
            self.max_shield = new_lvl
            self.shield_charges = self.max_shield

        new_synergies = self.check_synergies()
        return new_lvl, (new_lvl > old_lvl), new_synergies

    def check_synergies(self):
        new_unlocked = []
        p = self.powers

        def try_add(name):
            if name not in self.synergies:
                self.synergies.append(name)
                new_unlocked.append(name)

        if p[POWER_FIRE] >= 2 and p[POWER_ICE] >= 2: try_add("CHOQUE TERMICO")
        if p[POWER_ELECTRO] >= 2 and p[POWER_FIRE] >= 2: try_add("PLASMA DE TORMENTA")
        if p[POWER_ICE] >= 3 and p[POWER_SHIELD] >= 2: try_add("CERO ABSOLUTO")
        if p[POWER_SHIELD] >= 3 and p[POWER_ELECTRO] >= 2: try_add("ESCUDO SOBRECARGADO")
        if p[POWER_SPEED] >= 3 and p[POWER_FIRE] >= 2: try_add("DASH DE FUEGO")
        if p[POWER_HEALTH] >= 3 and p[POWER_FUEL] >= 2: try_add("AUTORREPARACION")

        return new_unlocked

    def take_damage(self, amount):
        now = pygame.time.get_ticks()
        if self.is_invulnerable or not self.is_alive or self.is_dying:
            return False

        if self.shield_charges > 0:
            self.shield_charges -= 1
            self.is_invulnerable = True
            self.invulnerable_timer = now + 800
            if self.shield_charges == 0 and self.powers[POWER_SHIELD] == 3:
                return "shield_explosion"
            return "shield_absorbed"

        self.hp -= amount
        self.last_damage_time = now
        self.is_invulnerable = True
        self.invulnerable_timer = now + PLAYER_INVULNERABLE_TIME

        if self.hp <= 0:
            self.lives -= 1
            self.life_lost_alert_until = now + 1800
            
            if self.lives > 0:
                self.hp = self.max_hp
                self.is_invulnerable = True
                self.invulnerable_timer = now + 2500
                return "life_lost"
            else:
                self.hp = 0
                self.is_dying = True
                self.death_timer = self.death_duration
                return "dying"

        return "hit"

    def move(self, dx, dy):
        if self.is_dying or not self.is_alive:
            return

        if self.is_dashing:
            self.x += self.dash_dir[0] * 16
            self.y += self.dash_dir[1] * 16
        else:
            self.x += dx * self.speed
            self.y += dy * self.speed

        self.x = max(0, min(self.screen_width - self.width, self.x))
        self.y = max(0, min(self.screen_height - self.height, self.y))

    def trigger_dash(self, dx, dy):
        now = pygame.time.get_ticks()
        if self.powers[POWER_SPEED] >= 3 and now > self.dash_cooldown and (dx != 0 or dy != 0):
            self.is_dashing = True
            self.dash_timer = now + 160
            self.dash_cooldown = now + 750
            self.is_invulnerable = True
            self.invulnerable_timer = now + 250

            mag = math.hypot(dx, dy)
            self.dash_dir = [dx / mag, dy / mag] if mag > 0 else [0, -1]
            return True
        return False

    def update(self, particle_mgr=None):
        now = pygame.time.get_ticks()

        # Secuencia de explosión al morir
        if self.is_dying:
            self.death_timer -= 1
            if particle_mgr and self.death_timer % 8 == 0:
                ox = random.randint(-20, 20)
                oy = random.randint(-20, 20)
                particle_mgr.spawn_explosion(self.x + self.width // 2 + ox, self.y + self.height // 2 + oy, count=18, is_large=True)
            if self.death_timer <= 0:
                self.is_alive = False
                self.is_dying = False
            return

        if self.is_dashing and now > self.dash_timer:
            self.is_dashing = False

        if self.is_invulnerable and now > self.invulnerable_timer:
            self.is_invulnerable = False

        if self.fuel < self.max_fuel:
            self.fuel = min(self.max_fuel, self.fuel + 0.05)

        if "AUTORREPARACION" in self.synergies and now - self.last_damage_time >= 4000:
            if self.hp < self.max_hp:
                self.hp = min(self.max_hp, self.hp + 0.04)

    def draw(self, surface):
        now = pygame.time.get_ticks()

        # Si está en secuencia de muerte, parpadear en fuego
        if self.is_dying:
            if self.death_timer % 4 < 2:
                flash_surf = self.mask.to_surface(setcolor=(255, 60, 20, 255), unsetcolor=(0, 0, 0, 0))
                surface.blit(flash_surf, (self.x, self.y))
            return

        if not self.is_alive:
            return

        # Parpadeo fuerte de invulnerabilidad
        if self.is_invulnerable:
            if (now // 60) % 2 == 0:
                flash_surf = self.mask.to_surface(setcolor=(255, 255, 255, 220), unsetcolor=(0, 0, 0, 0))
                surface.blit(flash_surf, (self.x, self.y))
                return

        surface.blit(self.image, (self.x, self.y))

        # Cúpula de Escudo
        if self.shield_charges > 0:
            center = (int(self.x + self.width // 2), int(self.y + self.height // 2))
            r = int(self.width * 0.72 + math.sin(now * 0.01) * 3)
            pygame.draw.circle(surface, COLOR_CYAN, center, r, width=2)
            pygame.draw.circle(surface, COLOR_BLUE, center, r + 2, width=1)