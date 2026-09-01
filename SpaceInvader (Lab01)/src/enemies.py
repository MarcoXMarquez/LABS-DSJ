# src/enemies.py
import pygame
import math
import random
import os
from src.config import (
    COLOR_RED, COLOR_YELLOW, COLOR_ORANGE, COLOR_BLUE,
    COLOR_PURPLE, COLOR_GREEN, COLOR_WHITE, COLOR_CYAN, COLOR_GOLD
)
from src.drops import (
    POWER_FIRE, POWER_ICE, POWER_SHIELD, POWER_ELECTRO
)

ENEMY_SCOUT = "SCOUT"
ENEMY_SHOUTER = "SHOOTER"
ENEMY_TANK = "TANK"
ENEMY_KAMIKAZE = "KAMIKAZE"

SPRITES = {}
MASKS = {}

# Dimensiones ampliadas +30%
SIZES = {
    ENEMY_SCOUT: (62, 62),
    ENEMY_SHOUTER: (70, 70),
    ENEMY_TANK: (88, 88),
    ENEMY_KAMIKAZE: (62, 62),
    "CAPTAIN": (84, 84),
    "DRONE": (42, 42),
    "BANNER": (46, 62)
}

def load_enemy_sprites():
    global SPRITES, MASKS
    if SPRITES:
        return
    files = {
        ENEMY_SCOUT: 'assets/images/enemy_scout.png',
        ENEMY_SHOUTER: 'assets/images/enemy_shooter.png',
        ENEMY_TANK: 'assets/images/enemy_tank.png',
        ENEMY_KAMIKAZE: 'assets/images/enemy_kamikaze.png',
        "CAPTAIN": 'assets/images/enemy_captain.png',
        "DRONE": 'assets/images/drone_healer.png',
        "BANNER": 'assets/images/banner_damage.png'
    }
    for key, path in files.items():
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                target_size = SIZES.get(key, (60, 60))
                scaled_img = pygame.transform.smoothscale(img, target_size)
                SPRITES[key] = scaled_img
                MASKS[key] = pygame.mask.from_surface(scaled_img)
            except Exception:
                pass


class EnemyBullet:
    """Proyectil enemigo con soporte para balas teledirigidas curvas y formas diferenciadas."""
    def __init__(self, x, y, vx=0, vy=5.5, damage=15, is_fire=False, is_ice=False, is_captain=False, is_homing=False):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.damage = damage
        self.radius = 7 if is_captain else 5
        self.is_fire = is_fire
        self.is_ice = is_ice
        self.is_captain = is_captain
        self.is_homing = is_homing
        self.spawn_time = pygame.time.get_ticks()
        self.is_tracking = is_homing
        self.is_alive = True

    def update(self, player_pos=None):
        now = pygame.time.get_ticks()

        if self.is_tracking and player_pos:
            px, py = player_pos
            if (now - self.spawn_time > 1200) or (self.y > py - 20):
                self.is_tracking = False
            else:
                target_ang = math.atan2(py - self.y, px - self.x)
                current_ang = math.atan2(self.vy, self.vx)
                diff = (target_ang - current_ang + math.pi) % (2 * math.pi) - math.pi
                steer = max(-0.05, min(0.05, diff))
                new_ang = current_ang + steer
                speed = 5.2
                self.vx = math.cos(new_ang) * speed
                self.vy = math.sin(new_ang) * speed

        self.x += self.vx
        self.y += self.vy

        if self.y > 2000 or self.y < -100 or self.x < -100 or self.x > 3000:
            self.is_alive = False

    def draw(self, surface):
        pos = (int(self.x), int(self.y))
        
        if self.is_homing:
            glow_c = COLOR_ORANGE if self.is_tracking else (140, 140, 160)
            pygame.draw.circle(surface, glow_c, pos, self.radius + 2)
            pygame.draw.circle(surface, COLOR_YELLOW, pos, self.radius - 1)
            pygame.draw.circle(surface, COLOR_WHITE, pos, 2)

        elif self.is_fire:
            pygame.draw.circle(surface, COLOR_ORANGE, pos, self.radius + 2)
            pygame.draw.circle(surface, COLOR_YELLOW, pos, self.radius - 1)
            pygame.draw.polygon(surface, (255, 80, 0), [
                (self.x, self.y - self.radius - 4),
                (self.x - self.radius, self.y + 2),
                (self.x + self.radius, self.y + 2)
            ])

        elif self.is_ice:
            r = self.radius + 3
            pygame.draw.polygon(surface, COLOR_CYAN, [
                (self.x, self.y - r),
                (self.x + r, self.y),
                (self.x, self.y + r),
                (self.x - r, self.y)
            ])
            pygame.draw.polygon(surface, COLOR_WHITE, [
                (self.x, self.y - r + 2),
                (self.x + r - 2, self.y),
                (self.x, self.y + r - 2),
                (self.x - r + 2, self.y)
            ], width=1)

        elif self.is_captain:
            pygame.draw.circle(surface, COLOR_GOLD, pos, self.radius + 3)
            pygame.draw.circle(surface, COLOR_YELLOW, pos, self.radius + 1)
            pygame.draw.circle(surface, COLOR_WHITE, pos, self.radius - 1)

        else:
            pygame.draw.circle(surface, COLOR_RED, pos, self.radius)
            pygame.draw.circle(surface, COLOR_YELLOW, pos, 2)


class HealerDrone:
    """Dron sanador que orbita en 3D y cura al Boss Final en la Fase 1."""
    def __init__(self, x, y, boss_ref, angle_offset=0):
        load_enemy_sprites()
        self.x = x
        self.y = y
        self.boss_ref = boss_ref
        self.width = 42
        self.height = 42
        self.max_hp = 50
        self.hp = self.max_hp
        self.is_alive = True
        self.last_heal = pygame.time.get_ticks()
        self.angle = angle_offset
        self.hit_flash = 0

    def update(self):
        self.angle += 0.035
        if self.boss_ref and self.boss_ref.is_alive:
            cx = self.boss_ref.x + self.boss_ref.width // 2
            cy = self.boss_ref.y + self.boss_ref.height // 2
            self.x = cx + math.cos(self.angle) * 160
            self.y = cy + math.sin(self.angle) * 55

            now = pygame.time.get_ticks()
            if now - self.last_heal >= 2000:
                self.last_heal = now
                self.boss_ref.hp = min(self.boss_ref.max_hp, self.boss_ref.hp + 10)  # antes 15

    def take_damage(self, amount):
        self.hp -= amount
        self.hit_flash = pygame.time.get_ticks() + 60
        if self.hp <= 0:
            self.is_alive = False
            return True
        return False

    def draw(self, surface):
        now = pygame.time.get_ticks()
        rect = pygame.Rect(int(self.x), int(self.y), self.width, self.height)
        
        spr = SPRITES.get("DRONE")
        mask = MASKS.get("DRONE")
        if spr and mask:
            if now < self.hit_flash:
                flash_surf = mask.to_surface(setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))
                surface.blit(flash_surf, (self.x, self.y))
            else:
                surface.blit(spr, (self.x, self.y))
        else:
            color = COLOR_WHITE if now < self.hit_flash else COLOR_GREEN
            pygame.draw.rect(surface, color, rect, border_radius=8)
            pygame.draw.rect(surface, COLOR_WHITE, rect, width=1, border_radius=8)
        
        pulse = abs(math.sin(now * 0.008)) * 4
        pygame.draw.circle(surface, COLOR_GREEN, (int(self.x + self.width // 2), int(self.y + self.height // 2)), int(self.width * 0.6 + pulse), width=1)
        
        hp_w = int(self.width * max(0, self.hp / self.max_hp))
        pygame.draw.rect(surface, (40, 40, 40), (self.x, self.y - 6, self.width, 3))
        pygame.draw.rect(surface, COLOR_GREEN, (self.x, self.y - 6, hp_w, 3))


class DamageBanner:
    """Estandarte que aumenta el daño del Boss Final en +20% en la Fase 2."""
    def __init__(self, x, y):
        load_enemy_sprites()
        self.x = x
        self.y = y
        self.width = 46
        self.height = 62
        self.max_hp = 70
        self.hp = self.max_hp
        self.is_alive = True
        self.hit_flash = 0

    def take_damage(self, amount):
        self.hp -= amount
        self.hit_flash = pygame.time.get_ticks() + 60
        if self.hp <= 0:
            self.is_alive = False
            return True
        return False

    def draw(self, surface):
        now = pygame.time.get_ticks()
        rect = pygame.Rect(int(self.x), int(self.y), self.width, self.height)
        
        spr = SPRITES.get("BANNER")
        mask = MASKS.get("BANNER")
        if spr and mask:
            if now < self.hit_flash:
                flash_surf = mask.to_surface(setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))
                surface.blit(flash_surf, (self.x, self.y))
            else:
                surface.blit(spr, (self.x, self.y))
        else:
            color = COLOR_WHITE if now < self.hit_flash else (190, 20, 20)
            pygame.draw.rect(surface, color, rect, border_radius=6)
            pygame.draw.rect(surface, COLOR_GOLD, rect, width=2, border_radius=6)

        hp_w = int(self.width * max(0, self.hp / self.max_hp))
        pygame.draw.rect(surface, (40, 40, 40), (self.x, self.y - 6, self.width, 3))
        pygame.draw.rect(surface, COLOR_RED, (self.x, self.y - 6, hp_w, 3))


class Enemy:
    """Enemigo individual ampliado +30% con IA y confinamiento dentro de pantalla."""
    def __init__(self, enemy_type=ENEMY_SCOUT, screen_width=800, screen_height=600, is_captain=False, elemental_power=None):
        load_enemy_sprites()
        self.enemy_type = enemy_type
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.is_captain = is_captain
        self.elemental_power = elemental_power
        self.is_alive = True

        self.x = screen_width // 2
        self.y = -100

        self.param_type = "CRESCENT"
        self.param_index = 0
        self.param_total = 1
        self.param_radius = 120
        self.param_angle = 0.0
        self.param_side = 1.0
        self.param_row = 0

        # Dimensiones ampliadas +30%
        if enemy_type == ENEMY_SCOUT:
            self.width, self.height = 62, 62
            self.max_hp = 40          # antes 25 — ahora sobrevive 1-2 dashes antes de morir
            self.color = COLOR_YELLOW
            self.coin_reward = random.randint(6, 10)
        elif enemy_type == ENEMY_SHOUTER:
            self.width, self.height = 70, 70
            self.max_hp = 45
            self.color = COLOR_ORANGE
            self.coin_reward = random.randint(12, 18)
        elif enemy_type == ENEMY_TANK:
            self.width, self.height = 88, 88
            self.max_hp = 120
            self.color = (175, 40, 40)
            self.coin_reward = random.randint(25, 35)
        elif enemy_type == ENEMY_KAMIKAZE:
            self.width, self.height = 62, 62
            self.max_hp = 35
            self.color = COLOR_RED
            self.coin_reward = random.randint(10, 15)
        else:
            self.width, self.height = 62, 62
            self.max_hp = 30
            self.color = COLOR_YELLOW
            self.coin_reward = 8

        if self.is_captain:
            self.width = 84
            self.height = 84
            self.max_hp = int(self.max_hp * 2.5)
            self.color = COLOR_GOLD
            self.coin_reward = random.randint(45, 65)

        self.hp = self.max_hp
        self.shield_charges = 2 if self.elemental_power == POWER_SHIELD else 0
        self.last_shot_time = pygame.time.get_ticks() + random.randint(0, 1500)
        self.hit_flash_until = 0

        self.burn_until = 0
        self.freeze_until = 0
        self.slow_factor = 1.0

        self.evade_until = 0
        self.evade_vx = 0.0

        self.swoop_state = "IDLE"
        self.dive_vx = 0
        self.dive_vy = 0
        self.burn_until = 0
        self.freeze_until = 0
        self.slow_factor = 1.0
        # Cooldown para reaplicar efectos elementales (6 segundos)
        self.last_burn_applied = 0
        self.last_freeze_applied = 0
        self.last_burn_tick = 0   # Para separar los ticks de DoT
        self.last_swoop_time = pygame.time.get_ticks() + random.randint(3000, 8000)

    def apply_burn(self, duration_ms=1200):
        now = pygame.time.get_ticks()
        # Fuego: cooldown de reaplicación 4 segundos (antes 6s — más dinámico)
        if now - self.last_burn_applied < 4000:
            return
        self.last_burn_applied = now
        self.burn_until = now + duration_ms

    def apply_freeze(self, duration_ms=1000, is_full_freeze=False):
        now = pygame.time.get_ticks()
        # Solo se puede reaplicar cada 6 segundos
        if now - self.last_freeze_applied < 6000:
            return
        self.last_freeze_applied = now
        self.freeze_until = now + duration_ms
        self.slow_factor = 0.0 if is_full_freeze else 0.5

    def trigger_evade(self):
        if self.enemy_type == ENEMY_SCOUT and pygame.time.get_ticks() > self.evade_until:
            self.evade_until = pygame.time.get_ticks() + 260
            self.evade_vx = random.choice([-8.0, 8.0])

    def take_damage(self, amount):
        if self.shield_charges > 0:
            self.shield_charges -= 1
            self.hit_flash_until = pygame.time.get_ticks() + 60
            return False

        self.hp -= amount
        self.hit_flash_until = pygame.time.get_ticks() + 60
        
        if self.enemy_type == ENEMY_SCOUT:
            self.trigger_evade()

        if self.hp <= 0:
            self.is_alive = False
            return True
        return False

    def compute_geometric_target(self, t, cx, cy):
        idx = self.param_index
        tot = max(1, self.param_total)
        r = self.param_radius

        # Ancho contenido estrictamente dentro de la pantalla
        full_w = self.screen_width - 220

        raw_x = cx
        raw_y = cy

        if self.param_type == "CRESCENT":
            norm = (idx / (tot - 1)) if tot > 1 else 0.5
            span = (norm - 0.5) * full_w
            arc_y = (span ** 2) / 950
            wave = math.cos(t * 2.5 + norm * 3.14) * 16
            raw_x, raw_y = (cx + span, cy + arc_y + wave)

        elif self.param_type == "CHEVRON":
            spread = 1.0 + 0.22 * math.sin(t * 2.0)
            side = self.param_side
            row = self.param_row
            col = idx % 4
            off_x = side * (col * 95 * spread + 55)
            off_y = row * 52 + (col * 25) + math.sin(t * 3.0 + col) * 10
            if self.is_captain:
                raw_x, raw_y = (cx, cy - 30 + math.sin(t * 2.0) * 10)
            else:
                raw_x, raw_y = (cx + off_x, cy + off_y)

        elif self.param_type == "DIAMOND":
            pulse = 1.0 + 0.18 * math.sin(t * 2.2)
            ang = self.param_angle + (math.sin(t * 1.5) * 0.25)
            rx = (r * 2.0) * pulse
            ry = (r * 0.95) * pulse
            if self.is_captain:
                raw_x, raw_y = (cx, cy)
            else:
                raw_x, raw_y = (cx + math.cos(ang) * rx, cy + math.sin(ang) * ry)

        elif self.param_type == "ORBIT":
            if self.is_captain:
                raw_x, raw_y = (cx, cy + math.sin(t * 1.5) * 12)
            else:
                cur_ang = self.param_angle + (t * 1.6)
                rx = r * 2.0
                ry = r * 0.95
                raw_x, raw_y = (cx + math.cos(cur_ang) * rx, cy + math.sin(cur_ang) * ry)

        elif self.param_type == "LISSAJOUS":
            phase = self.param_angle + (t * 1.4)
            lx = math.sin(phase) * (full_w * 0.42)
            ly = math.sin(phase * 2.0) * (r * 0.75)
            if self.is_captain:
                raw_x, raw_y = (cx, cy - 30)
            else:
                raw_x, raw_y = (cx + lx, cy + ly)

        elif self.param_type == "HEXAGON":
            pulse = 1.0 + 0.14 * math.sin(t * 1.8)
            cur_ang = self.param_angle + (t * 0.6)
            if self.is_captain:
                raw_x, raw_y = (cx, cy)
            else:
                raw_x, raw_y = (cx + math.cos(cur_ang) * (r * 1.9 * pulse), cy + math.sin(cur_ang) * (r * 0.95 * pulse))

        elif self.param_type == "BUTTERFLY":
            side = self.param_side
            wing_flap = abs(math.cos(t * 2.5)) * (full_w * 0.34) + 40
            wing_y = math.sin(t * 3.5 + idx * 0.4) * 45
            if self.is_captain:
                raw_x, raw_y = (cx, cy - 20)
            else:
                raw_x, raw_y = (cx + side * (wing_flap + (idx % 5) * 48), cy + wing_y + (idx // 5) * 48)

        elif self.param_type == "TRIDENT":
            col = self.param_row
            off_y = (idx % 5) * 52
            spacing_col = full_w * 0.34
            shift = math.sin(t * 2.2) * 32 if col != 0 else -math.sin(t * 2.2) * 32
            raw_x, raw_y = (cx + col * spacing_col, cy + off_y + shift)

        elif self.param_type == "STAR":
            cur_ang = self.param_angle + (t * 0.9)
            pulse = r * (1.0 + 0.25 * math.sin(t * 3.0))
            if self.is_captain:
                raw_x, raw_y = (cx, cy)
            else:
                raw_x, raw_y = (cx + math.cos(cur_ang) * (pulse * 1.9), cy + math.sin(cur_ang) * (pulse * 0.95))

        elif self.param_type == "PHALANX":
            row = self.param_row
            advance = math.sin(t * 1.6) * 28
            spacing_x = (idx - tot / 2) * 92
            if row == 0:
                raw_x, raw_y = (cx + spacing_x, cy + 70 + advance)
            else:
                wiggle = math.sin(t * 3.0 + idx) * 20
                raw_x, raw_y = (cx + spacing_x + wiggle, cy - 10)

        elif self.param_type == "VORTEX":
            arm_ang = (self.param_row * (6.28 / 3)) + (t * 1.2)
            dist = 50 + (idx * 42) + math.sin(t * 2.0) * 15
            if self.is_captain:
                raw_x, raw_y = (cx, cy)
            else:
                raw_x, raw_y = (cx + math.cos(arm_ang) * (dist * 1.7), cy + math.sin(arm_ang) * (dist * 0.95))

        elif self.param_type == "IMPERIAL_V":
            side = self.param_side
            row = self.param_row
            col = idx % 5
            breath = 1.0 + 0.2 * math.sin(t * 2.0)
            off_x = side * (col * 90 * breath + 50)
            off_y = row * 52 + (col * 30) + math.sin(t * 2.5 + col) * 10
            if self.is_captain:
                raw_x, raw_y = (cx, cy - 35)
            else:
                raw_x, raw_y = (cx + off_x, cy + off_y)

        # Confinamiento estricto dentro de pantalla
        clamped_x = max(30, min(self.screen_width - self.width - 30, raw_x))
        clamped_y = max(60, min(self.screen_height - self.height - 70, raw_y))
        return clamped_x, clamped_y

    def update_geometric(self, t, cx, cy, player_pos, enemy_bullets):
        now = pygame.time.get_ticks()

        if now < self.freeze_until:
            if self.slow_factor == 0.0:
                return
        else:
            self.slow_factor = 1.0

        if now < self.burn_until:
            # DoT: 4 HP cada 500ms (antes 2 HP — ahora sí se nota el fuego)
            if now - self.last_burn_tick >= 500:
                self.last_burn_tick = now
                self.hp -= 4
                if self.hp <= 0:
                    self.is_alive = False
                    return

        px, py = player_pos
        target_x, target_y = self.compute_geometric_target(t, cx, cy)

        if now < self.evade_until:
            target_x += self.evade_vx

        speed_mult = self.slow_factor

        if self.enemy_type == ENEMY_KAMIKAZE:
            if self.swoop_state == "IDLE":
                self.x += (target_x - self.x) * (0.12 * speed_mult)
                self.y += (target_y - self.y) * (0.12 * speed_mult)

                if now - self.last_swoop_time > random.randint(3500, 6500):
                    self.last_swoop_time = now
                    self.swoop_state = "DIVING"
                    ang = math.atan2(py - self.y, px - self.x)
                    self.dive_vx = math.cos(ang) * (7.5 * speed_mult)
                    self.dive_vy = math.sin(ang) * (7.5 * speed_mult)

            elif self.swoop_state == "DIVING":
                self.x += self.dive_vx
                self.y += self.dive_vy
                if self.y > py + 40 or self.y > self.screen_height - 90:
                    self.swoop_state = "RETURNING"

            elif self.swoop_state == "RETURNING":
                ang = math.atan2(target_y - self.y, target_x - self.x)
                self.x += math.cos(ang) * (5.5 * speed_mult)
                self.y += math.sin(ang) * (5.5 * speed_mult)
                if math.hypot(target_x - self.x, target_y - self.y) < 20:
                    self.x = target_x
                    self.y = target_y
                    self.swoop_state = "IDLE"
                    self.last_swoop_time = now

        else:
            self.x += (target_x - self.x) * (0.14 * speed_mult)
            self.y += (target_y - self.y) * (0.14 * speed_mult)

            rate = int(1400 / speed_mult) if self.elemental_power == POWER_ELECTRO else (int(1700 / speed_mult) if self.is_captain else int(2300 / speed_mult))
            if now - self.last_shot_time >= rate:
                self.last_shot_time = now + random.randint(-150, 250)
                ang = math.atan2(py - (self.y + self.height), px - (self.x + self.width // 2))
                spd = 6.5 if self.elemental_power == POWER_ELECTRO else 5.2
                is_f = (self.elemental_power == POWER_FIRE)
                is_i = (self.elemental_power == POWER_ICE)
                em_cx = self.x + self.width // 2
                em_cy = self.y + self.height

                if self.is_captain:
                    # Daño por bala 15 (antes 22 — demasiado alto vs 100 HP del jugador)
                    enemy_bullets.append(EnemyBullet(em_cx - 16, em_cy, math.cos(ang - 0.14) * spd, math.sin(ang - 0.14) * spd, damage=15, is_fire=is_f, is_ice=is_i, is_captain=True))
                    enemy_bullets.append(EnemyBullet(em_cx + 16, em_cy, math.cos(ang + 0.14) * spd, math.sin(ang + 0.14) * spd, damage=15, is_fire=is_f, is_ice=is_i, is_captain=True))
                
                elif self.enemy_type == ENEMY_SHOUTER:
                    enemy_bullets.append(EnemyBullet(em_cx, em_cy, math.cos(ang) * 4.8, math.sin(ang) * 4.8, damage=16, is_fire=is_f, is_ice=is_i, is_homing=True))

                elif self.enemy_type == ENEMY_TANK:
                    enemy_bullets.append(EnemyBullet(em_cx, em_cy, math.cos(ang) * spd, math.sin(ang) * spd, damage=18, is_fire=is_f, is_ice=is_i))

                elif self.enemy_type == ENEMY_SCOUT:
                    enemy_bullets.append(EnemyBullet(em_cx, em_cy, 0, 6.2, damage=12, is_fire=is_f, is_ice=is_i))

    def draw(self, surface):
        now = pygame.time.get_ticks()
        center_pos = (int(self.x + self.width // 2), int(self.y + self.height // 2))

        key = "CAPTAIN" if self.is_captain else self.enemy_type
        spr = SPRITES.get(key)
        mask = MASKS.get(key)

        if spr and mask:
            if now < self.hit_flash_until:
                flash_surf = mask.to_surface(setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))
                surface.blit(flash_surf, (self.x, self.y))
            else:
                surface.blit(spr, (self.x, self.y))

            if now < self.freeze_until or self.slow_factor < 1.0:
                ice_mask = mask.to_surface(setcolor=(80, 220, 255, 175), unsetcolor=(0, 0, 0, 0))
                surface.blit(ice_mask, (self.x, self.y))
                pygame.draw.circle(surface, COLOR_CYAN, center_pos, int(self.width * 0.65), width=2)
                for off_x, off_y in [(-14, -14), (14, -14), (-14, 14), (14, 14)]:
                    pygame.draw.line(surface, COLOR_WHITE, (center_pos[0] + off_x, center_pos[1] + off_y - 5), (center_pos[0] + off_x, center_pos[1] + off_y + 5), 1)
                    pygame.draw.line(surface, COLOR_WHITE, (center_pos[0] + off_x - 5, center_pos[1] + off_y), (center_pos[0] + off_x + 5, center_pos[1] + off_y), 1)

            elif now < self.burn_until:
                alpha_f = int(160 + math.sin(now * 0.02) * 50)
                fire_mask = mask.to_surface(setcolor=(255, 110, 20, alpha_f), unsetcolor=(0, 0, 0, 0))
                surface.blit(fire_mask, (self.x, self.y))
                flame_h = int(8 + math.sin(now * 0.03) * 4)
                pygame.draw.polygon(surface, COLOR_ORANGE, [
                    (center_pos[0] - 10, self.y + 4),
                    (center_pos[0], self.y - flame_h),
                    (center_pos[0] + 10, self.y + 4)
                ])
                pygame.draw.polygon(surface, COLOR_YELLOW, [
                    (center_pos[0] - 5, self.y + 2),
                    (center_pos[0], self.y - flame_h + 3),
                    (center_pos[0] + 5, self.y + 2)
                ])

            if self.elemental_power == POWER_ELECTRO:
                if random.random() < 0.35:
                    rx = random.randint(-18, 18)
                    ry = random.randint(-18, 18)
                    pygame.draw.line(surface, COLOR_YELLOW, center_pos, (center_pos[0] + rx, center_pos[1] + ry), 2)
                    pygame.draw.circle(surface, COLOR_WHITE, (center_pos[0] + rx, center_pos[1] + ry), 2)

        else:
            draw_color = COLOR_WHITE if now < self.hit_flash_until else self.color
            if self.is_captain:
                radius = self.width // 2
                pygame.draw.circle(surface, COLOR_GOLD, center_pos, radius + 3, width=2)
                pygame.draw.circle(surface, draw_color, center_pos, radius)
            else:
                rect = pygame.Rect(int(self.x), int(self.y), self.width, self.height)
                pygame.draw.rect(surface, draw_color, rect, border_radius=8)

        if self.shield_charges > 0:
            shield_r = int(self.width * 0.72 + math.sin(now * 0.01) * 3)
            pygame.draw.circle(surface, COLOR_CYAN, center_pos, shield_r, width=2)
            pygame.draw.circle(surface, COLOR_BLUE, center_pos, shield_r + 2, width=1)


class WaveManager:
    """Gestiona los 12 niveles con conteo reducido un 20% y enemigos +30% más grandes."""
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.current_level = 1
        self.max_levels = 12
        
        self.enemies = []
        self.enemy_bullets = []
        self.healer_drones = []
        self.damage_banners = []
        self.wave_in_progress = False
        
        self.t = 0.0

    def start_level(self, level_num):
        self.current_level = level_num
        self.enemies.clear()
        self.healer_drones.clear()
        self.damage_banners.clear()
        self.wave_in_progress = True
        self.t = 0.0

        elements = [POWER_FIRE, POWER_ICE, POWER_SHIELD, POWER_ELECTRO]

        # --- NIVEL 1: CRESCENT (13 Invasores) ---
        if level_num == 1:
            total = 13
            for i in range(total):
                is_cap = (i == total // 2)
                etype = ENEMY_TANK if is_cap else (ENEMY_SHOUTER if i in (3, 9) else ENEMY_SCOUT)
                e = Enemy(etype, self.screen_width, self.screen_height, is_captain=is_cap)
                e.param_type = "CRESCENT"
                e.param_index = i
                e.param_total = total
                self.enemies.append(e)

        # --- NIVEL 2: CHEVRON (17 Invasores) ---
        elif level_num == 2:
            cap = Enemy(ENEMY_TANK, self.screen_width, self.screen_height, is_captain=True)
            cap.param_type = "CHEVRON"
            self.enemies.append(cap)
            for row in range(1, 3):
                for side in [-1, 1]:
                    for col in range(4):
                        etype = ENEMY_SHOUTER if row == 2 else ENEMY_SCOUT
                        e = Enemy(etype, self.screen_width, self.screen_height)
                        e.param_type = "CHEVRON"
                        e.param_row = row
                        e.param_side = side
                        e.param_index = col
                        self.enemies.append(e)

        # --- NIVEL 3: DIAMOND (16 Invasores) ---
        elif level_num == 3:
            cap = Enemy(ENEMY_TANK, self.screen_width, self.screen_height, is_captain=True, elemental_power=POWER_FIRE)
            cap.param_type = "DIAMOND"
            self.enemies.append(cap)
            total_ring = 15
            for i in range(total_ring):
                ang = (i / total_ring) * 6.28
                etype = ENEMY_SHOUTER if i % 3 == 0 else (ENEMY_TANK if i % 5 == 0 else ENEMY_SCOUT)
                e = Enemy(etype, self.screen_width, self.screen_height)
                e.param_type = "DIAMOND"
                e.param_angle = ang
                e.param_radius = 150 if i % 2 == 0 else 190
                self.enemies.append(e)

        # --- NIVEL 4: ORBIT (18 Satélites) ---
        elif level_num == 4:
            cap = Enemy(ENEMY_TANK, self.screen_width, self.screen_height, is_captain=True)
            cap.param_type = "ORBIT"
            self.enemies.append(cap)
            total_sat = 17
            for i in range(total_sat):
                ang = (i / total_sat) * 6.28
                etype = ENEMY_KAMIKAZE if i % 4 == 0 else (ENEMY_SHOUTER if i % 2 == 0 else ENEMY_SCOUT)
                e = Enemy(etype, self.screen_width, self.screen_height)
                e.param_type = "ORBIT"
                e.param_angle = ang
                e.param_radius = 145 if i % 2 == 0 else 195
                self.enemies.append(e)

        # --- NIVEL 5: LISSAJOUS (19 Invasores) ---
        elif level_num == 5:
            cap = Enemy(ENEMY_TANK, self.screen_width, self.screen_height, is_captain=True, elemental_power=POWER_ELECTRO)
            cap.param_type = "LISSAJOUS"
            self.enemies.append(cap)
            total_helix = 18
            for i in range(total_helix):
                ang = (i / total_helix) * 6.28
                etype = ENEMY_KAMIKAZE if i % 4 == 0 else (ENEMY_SHOUTER if i % 2 == 0 else ENEMY_SCOUT)
                e = Enemy(etype, self.screen_width, self.screen_height)
                e.param_type = "LISSAJOUS"
                e.param_angle = ang
                e.param_radius = 160
                self.enemies.append(e)

        # --- NIVEL 6: HEXAGON (18 Invasores Pre-MiniBoss con 2 Elementales) ---
        elif level_num == 6:
            cap = Enemy(ENEMY_TANK, self.screen_width, self.screen_height, is_captain=True, elemental_power=POWER_SHIELD)
            cap.param_type = "HEXAGON"
            self.enemies.append(cap)
            total_hex = 17
            for i in range(total_hex):
                ang = (i / total_hex) * 6.28
                elem = elements[i % 2] if i < 2 else None
                etype = ENEMY_TANK if i % 5 == 0 else (ENEMY_SHOUTER if i % 2 == 0 else ENEMY_KAMIKAZE)
                e = Enemy(etype, self.screen_width, self.screen_height, elemental_power=elem)
                e.param_type = "HEXAGON"
                e.param_angle = ang
                e.param_radius = 160 if i % 2 == 0 else 205
                self.enemies.append(e)

        # --- NIVEL 7: BUTTERFLY (19 Invasores) ---
        elif level_num == 7:
            cap = Enemy(ENEMY_TANK, self.screen_width, self.screen_height, is_captain=True, elemental_power=POWER_ICE)
            cap.param_type = "BUTTERFLY"
            self.enemies.append(cap)
            for side in [-1, 1]:
                for i in range(9):
                    etype = ENEMY_SHOUTER if i in (3, 6) else ENEMY_SCOUT
                    e = Enemy(etype, self.screen_width, self.screen_height)
                    e.param_type = "BUTTERFLY"
                    e.param_side = side
                    e.param_index = i
                    self.enemies.append(e)

        # --- NIVEL 8: TRIDENT (19 Invasores) ---
        elif level_num == 8:
            cap = Enemy(ENEMY_TANK, self.screen_width, self.screen_height, is_captain=True, elemental_power=POWER_FIRE)
            cap.param_type = "TRIDENT"
            cap.param_row = 0
            self.enemies.append(cap)
            for col in [-1, 0, 1]:
                for idx in range(6):
                    etype = ENEMY_SHOUTER if col == 0 else (ENEMY_TANK if idx in (0, 3) else ENEMY_KAMIKAZE)
                    e = Enemy(etype, self.screen_width, self.screen_height)
                    e.param_type = "TRIDENT"
                    e.param_row = col
                    e.param_index = idx
                    self.enemies.append(e)

        # --- NIVEL 9: STAR (20 Invasores) ---
        elif level_num == 9:
            cap = Enemy(ENEMY_TANK, self.screen_width, self.screen_height, is_captain=True, elemental_power=POWER_ELECTRO)
            cap.param_type = "STAR"
            self.enemies.append(cap)
            total_star = 19
            for i in range(total_star):
                ang = (i / total_star) * 6.28
                etype = ENEMY_KAMIKAZE if i % 3 == 0 else (ENEMY_SHOUTER if i % 2 == 0 else ENEMY_SCOUT)
                e = Enemy(etype, self.screen_width, self.screen_height)
                e.param_type = "STAR"
                e.param_angle = ang
                e.param_radius = 165 if i % 2 == 0 else 215
                self.enemies.append(e)

        # --- NIVEL 10: PHALANX (20 Invasores) ---
        elif level_num == 10:
            cap = Enemy(ENEMY_TANK, self.screen_width, self.screen_height, is_captain=True, elemental_power=POWER_SHIELD)
            cap.param_type = "PHALANX"
            cap.param_row = 1
            cap.param_index = 5
            self.enemies.append(cap)
            for i in range(9):
                e = Enemy(ENEMY_TANK, self.screen_width, self.screen_height)
                e.param_type = "PHALANX"
                e.param_row = 0
                e.param_index = i
                e.param_total = 9
                self.enemies.append(e)
            for i in range(10):
                e = Enemy(ENEMY_SHOUTER, self.screen_width, self.screen_height)
                e.param_type = "PHALANX"
                e.param_row = 1
                e.param_index = i
                e.param_total = 10
                self.enemies.append(e)

        # --- NIVEL 11: VORTEX (21 Invasores) ---
        elif level_num == 11:
            cap = Enemy(ENEMY_TANK, self.screen_width, self.screen_height, is_captain=True, elemental_power=POWER_FIRE)
            cap.param_type = "VORTEX"
            self.enemies.append(cap)
            for arm in range(3):
                for idx in range(7):
                    etype = ENEMY_KAMIKAZE if idx == 6 else (ENEMY_SHOUTER if idx % 2 == 0 else ENEMY_SCOUT)
                    e = Enemy(etype, self.screen_width, self.screen_height)
                    e.param_type = "VORTEX"
                    e.param_row = arm
                    e.param_index = idx
                    self.enemies.append(e)

        # --- NIVEL 12: IMPERIAL_V (23 Invasores Pre-Boss Final) ---
        elif level_num == 12:
            cap = Enemy(ENEMY_TANK, self.screen_width, self.screen_height, is_captain=True, elemental_power=POWER_SHIELD)
            cap.param_type = "IMPERIAL_V"
            self.enemies.append(cap)
            for row in range(2):
                for side in [-1, 1]:
                    for col in range(5):
                        etype = ENEMY_TANK if row == 0 and col == 0 else (ENEMY_SHOUTER if col % 2 == 0 else ENEMY_KAMIKAZE)
                        elem = elements[(col + row) % 2] if col == 1 else None
                        e = Enemy(etype, self.screen_width, self.screen_height, elemental_power=elem)
                        e.param_type = "IMPERIAL_V"
                        e.param_row = row
                        e.param_side = side
                        e.param_index = col
                        self.enemies.append(e)

    def update(self, player_pos):
        self.t += 0.022
        
        cx = self.screen_width // 2 + math.sin(self.t * 0.7) * 45
        cy = 150 + math.cos(self.t * 0.4) * 16

        for e in self.enemies:
            e.update_geometric(self.t, cx, cy, player_pos, self.enemy_bullets)
        self.enemies = [e for e in self.enemies if e.is_alive]

        for d in self.healer_drones:
            d.update()
        self.healer_drones = [d for d in self.healer_drones if d.is_alive]

        self.damage_banners = [b for b in self.damage_banners if b.is_alive]

        for b in self.enemy_bullets:
            b.update(player_pos)
        self.enemy_bullets = [b for b in self.enemy_bullets if b.is_alive]

        if len(self.enemies) == 0:
            self.wave_in_progress = False

    def draw(self, surface):
        for e in self.enemies:
            e.draw(surface)
        for d in self.healer_drones:
            d.draw(surface)
        for bn in self.damage_banners:
            bn.draw(surface)
        for b in self.enemy_bullets:
            b.draw(surface)