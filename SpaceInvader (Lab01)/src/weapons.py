# src/weapons.py
import pygame
import math
import random
from src.config import (
    COLOR_CYAN, COLOR_YELLOW, COLOR_RED, COLOR_ORANGE, COLOR_PURPLE,
    COLOR_WHITE, COLOR_GREEN, COLOR_BLUE,
    POWER_FIRE, POWER_ICE
)

WEAPON_SNIPER = "SNIPER"
WEAPON_MINIGUN = "MINIGUN"
WEAPON_SPREAD = "SPREAD"
WEAPON_MISSILE = "MISSILE"
WEAPON_HOMING = "HOMING"

class Bullet:
    """Clase universal de proyectiles del jugador."""
    def __init__(self, x, y, vx, vy, damage, weapon_type, max_distance=None, pierce=1, aoe_radius=0, is_special=False):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.damage = damage
        self.weapon_type = weapon_type
        self.max_distance = max_distance
        self.distance_traveled = 0
        self.pierce = pierce
        self.aoe_radius = aoe_radius
        self.is_special = is_special
        self.is_alive = True
        
        self.is_fire = False
        self.is_ice = False
        self.is_electro = False

        self.radius = 4
        if weapon_type == WEAPON_SNIPER:
            self.radius = 6 if is_special else 3
        elif weapon_type == WEAPON_MISSILE:
            self.radius = 8
        elif weapon_type == WEAPON_SPREAD:
            self.radius = 5

    def update(self, enemies=None, particle_mgr=None):
        if self.weapon_type == WEAPON_HOMING and enemies:
            target = None
            min_dist = 99999
            for e in enemies:
                if e.is_alive:
                    dist = math.hypot(e.x - self.x, e.y - self.y)
                    if dist < min_dist:
                        min_dist = dist
                        target = e
            
            if target:
                angle = math.atan2((target.y + target.height // 2) - self.y, (target.x + target.width // 2) - self.x)
                speed = 9.5
                self.vx = math.cos(angle) * speed
                self.vy = math.sin(angle) * speed

        if self.weapon_type == WEAPON_MISSILE and particle_mgr and random.random() < 0.4:
            particle_mgr.spawn_smoke_trail(self.x, self.y + 6)

        self.x += self.vx
        self.y += self.vy
        dist_step = math.hypot(self.vx, self.vy)
        self.distance_traveled += dist_step

        if self.max_distance and self.distance_traveled >= self.max_distance:
            self.is_alive = False

        if self.y < -50 or self.y > 2000 or self.x < -50 or self.x > 3000:
            self.is_alive = False

    def draw(self, surface):
        pos = (int(self.x), int(self.y))
        
        if self.weapon_type == WEAPON_SNIPER:
            color = COLOR_CYAN if not self.is_special else COLOR_WHITE
            pygame.draw.line(surface, color, (self.x, self.y), (self.x - self.vx * 2, self.y - self.vy * 2), 4)
            
        elif self.weapon_type == WEAPON_MINIGUN:
            pygame.draw.circle(surface, COLOR_YELLOW, pos, self.radius)
            
        elif self.weapon_type == WEAPON_SPREAD:
            pygame.draw.circle(surface, COLOR_ORANGE, pos, self.radius)
            
        elif self.weapon_type == WEAPON_MISSILE:
            pygame.draw.circle(surface, COLOR_RED, pos, self.radius)
            pygame.draw.circle(surface, COLOR_YELLOW, (int(self.x), int(self.y + 6)), 4)
            
        elif self.weapon_type == WEAPON_HOMING:
            pygame.draw.circle(surface, COLOR_PURPLE, pos, self.radius)
            pygame.draw.circle(surface, COLOR_CYAN, pos, 2)


class MissileAmmoDrop:
    """Cápsula de munición física de misil que flota en el espacio."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 16
        self.height = 16
        self.vy = 1.6
        self.is_collected = False

    def update(self, player=None):
        self.y += self.vy
        if player and player.powers.get("VOID", 0) > 0:
            px = player.x + player.width // 2
            py = player.y + player.height // 2
            dist = math.hypot(px - self.x, py - self.y)
            if dist < 220:
                ang = math.atan2(py - self.y, px - self.x)
                self.x += math.cos(ang) * 5
                self.y += math.sin(ang) * 5

    def draw(self, surface):
        rect = pygame.Rect(int(self.x), int(self.y), self.width, self.height)
        pygame.draw.rect(surface, COLOR_RED, rect, border_radius=4)
        pygame.draw.rect(surface, COLOR_WHITE, rect, width=1, border_radius=4)
        font = pygame.font.SysFont("Arial", 11, bold=True)
        t = font.render("M", True, COLOR_WHITE)
        surface.blit(t, (self.x + 3, self.y + 1))


class WeaponSystem:
    """Controlador de armas y mejoras balanceadas del Hangar/Tienda."""
    def __init__(self):
        self.bullets = []
        self.ammo_drops = []
        self.active_weapon = WEAPON_MINIGUN
        self.last_shot_time = 0
        
        self.missile_ammo = 3
        self.max_missile_ammo = 3

    def switch_weapon(self, weapon_type):
        self.active_weapon = weapon_type

    def shoot(self, player, enemies=None, shop_ref=None):
        now = pygame.time.get_ticks()
        px = player.x + player.width // 2
        py = player.y

        shop_levels = shop_ref.upgrades if shop_ref else {}
        sniper_lvl = shop_levels.get(WEAPON_SNIPER, {}).get("level", 0)
        minigun_lvl = shop_levels.get(WEAPON_MINIGUN, {}).get("level", 0)
        spread_lvl = shop_levels.get(WEAPON_SPREAD, {}).get("level", 0)
        homing_lvl = shop_levels.get(WEAPON_HOMING, {}).get("level", 0)

        # 1. SNIPER: 16 base, bonus +15%/nivel hangar (antes +25%)
        if self.active_weapon == WEAPON_SNIPER:
            cooldown = max(380, 520 - (sniper_lvl * 40))
            if now - self.last_shot_time >= cooldown:
                self.last_shot_time = now
                dmg = int(16 * (1.0 + sniper_lvl * 0.15))
                b = Bullet(px, py - 10, 0, -22, damage=dmg, weapon_type=WEAPON_SNIPER, pierce=2 + sniper_lvl)
                self.apply_elements(b, player)
                self.bullets.append(b)
                return True

        # 2. METRALLETA: 6 base (antes 4), cooldown mín 35ms (antes 45ms)
        elif self.active_weapon == WEAPON_MINIGUN:
            cooldown = max(35, 80 - (minigun_lvl * 15))
            if now - self.last_shot_time >= cooldown:
                self.last_shot_time = now
                vx = random.uniform(-0.5, 0.5)
                dmg = int(6 * (1.0 + minigun_lvl * 0.20))
                b = Bullet(px, py - 5, vx, -15, damage=dmg, weapon_type=WEAPON_MINIGUN, max_distance=480)
                self.apply_elements(b, player)
                self.bullets.append(b)
                return True

        # 3. ESCOPETA: 4 por perdigón (sin cambio)
        elif self.active_weapon == WEAPON_SPREAD:
            if now - self.last_shot_time >= 310:
                self.last_shot_time = now
                base_angles = [-20, -10, 0, 10, 20]
                if spread_lvl >= 1: base_angles.extend([-30, 30])
                if spread_lvl >= 2: base_angles.extend([-40, 40])
                for ang in base_angles:
                    rad = math.radians(ang - 90)
                    b = Bullet(px, py - 5, math.cos(rad) * 14, math.sin(rad) * 14, damage=4, weapon_type=WEAPON_SPREAD, max_distance=320)
                    self.apply_elements(b, player)
                    self.bullets.append(b)
                return True

        # 4. LANZAMISILES: 18 directo (antes 15) + AoE
        elif self.active_weapon == WEAPON_MISSILE:
            if self.missile_ammo > 0 and now - self.last_shot_time >= 480:
                self.last_shot_time = now
                self.missile_ammo -= 1
                b = Bullet(px, py - 10, 0, -10, damage=18, weapon_type=WEAPON_MISSILE, aoe_radius=75)
                self.apply_elements(b, player)
                self.bullets.append(b)
                return True

        # 5. HOMING: 5 base (antes 3)
        elif self.active_weapon == WEAPON_HOMING:
            if now - self.last_shot_time >= 150:
                self.last_shot_time = now
                vx = random.choice([-2.5, 2.5])
                dmg = int(5 * (1.0 + homing_lvl * 0.25))
                b = Bullet(px, py - 5, vx, -9, damage=dmg, weapon_type=WEAPON_HOMING)
                self.apply_elements(b, player)
                self.bullets.append(b)
                return True

        return False

    def use_special_skill(self, player, enemies=None):
        px = player.x + player.width // 2
        py = player.y

        if self.active_weapon == WEAPON_SNIPER:
            b = Bullet(px, py - 20, 0, -28, damage=110, weapon_type=WEAPON_SNIPER, pierce=99, is_special=True)
            self.apply_elements(b, player)
            self.bullets.append(b)
            return True

        elif self.active_weapon == WEAPON_SPREAD:
            for ang in range(0, 360, 24):
                rad = math.radians(ang)
                b = Bullet(px, py, math.cos(rad) * 12, math.sin(rad) * 12, damage=14, weapon_type=WEAPON_SPREAD, max_distance=360, is_special=True)
                self.apply_elements(b, player)
                self.bullets.append(b)
            return True

        elif self.active_weapon == WEAPON_HOMING:
            for _ in range(12):
                ang = random.uniform(0, 360)
                rad = math.radians(ang)
                b = Bullet(px, py, math.cos(rad) * 8, math.sin(rad) * 8, damage=8, weapon_type=WEAPON_HOMING, is_special=True)
                self.apply_elements(b, player)
                self.bullets.append(b)
            return True
        return False

    def apply_elements(self, bullet, player):
        if player.powers.get(POWER_FIRE, 0) > 0: bullet.is_fire = True
        if player.powers.get(POWER_ICE, 0) > 0: bullet.is_ice = True

    def update(self, enemies=None, particle_mgr=None, player=None):
        for b in self.bullets:
            b.update(enemies, particle_mgr)
        self.bullets = [b for b in self.bullets if b.is_alive]

        for drop in self.ammo_drops:
            drop.update(player)
        self.ammo_drops = [d for d in self.ammo_drops if not d.is_collected and d.y < 1200]

    def draw(self, surface):
        for b in self.bullets:
            b.draw(surface)
        for d in self.ammo_drops:
            d.draw(surface)