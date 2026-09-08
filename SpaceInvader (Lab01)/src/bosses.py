# src/bosses.py
import pygame
import math
import random
import os
from src.config import (
    COLOR_RED, COLOR_YELLOW, COLOR_GOLD, COLOR_CYAN,
    COLOR_WHITE, COLOR_PURPLE, COLOR_CARD_BG, COLOR_GREEN
)
from src.enemies import EnemyBullet, HealerDrone, DamageBanner, Enemy, ENEMY_SCOUT

BOSS_SPRITES = {}
BOSS_MASKS = {}

def load_boss_sprites():
    global BOSS_SPRITES, BOSS_MASKS
    if BOSS_SPRITES:
        return
    files = {
        "MINI": 'assets/images/boss_mini.png',
        "FINAL_P1": 'assets/images/boss_final_p1.png',
        "FINAL_P2": 'assets/images/boss_final_p2.png'
    }
    for key, path in files.items():
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                BOSS_SPRITES[key] = img
                BOSS_MASKS[key] = pygame.mask.from_surface(img)
            except Exception:
                pass


class MiniBoss:
    """Jefe Intermedio (Nivel 6) con Vínculo de Resurrección con sus Minions."""
    def __init__(self, screen_width, screen_height):
        load_boss_sprites()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.width = 160
        self.height = 95
        self.x = screen_width // 2 - self.width // 2
        self.y = -130
        self.target_y = 110
        
        self.max_hp = 600
        self.hp = self.max_hp
        self.vx = 3.2
        self.is_alive = True
        self.name = "CRUCERO DE ASALTO (MINI-BOSS)"
        
        self.last_shot = pygame.time.get_ticks()
        self.has_summoned_minions = False
        self.hit_flash = 0
        self.coin_reward = 250

    def take_damage(self, amount, wave_enemies):
        self.hp -= amount
        self.hit_flash = pygame.time.get_ticks() + 60
        if self.hp <= 0:
            alive_minions = [e for e in wave_enemies if e.is_alive]
            if len(alive_minions) > 0:
                self.hp = int(self.max_hp * 0.40)
                return "regenerated"
            else:
                self.hp = 0
                self.is_alive = False
                return "killed"
        return False

    def update(self, player_pos, enemy_bullets, wave_mgr):
        now = pygame.time.get_ticks()
        
        if self.y < self.target_y:
            self.y += 2
            return

        self.x += self.vx
        if self.x <= 40 or self.x >= self.screen_width - self.width - 40:
            self.vx *= -1

        if not self.has_summoned_minions and self.hp <= (self.max_hp * 0.5):
            self.has_summoned_minions = True
            for i in range(4):
                scout = Enemy(ENEMY_SCOUT, self.screen_width, self.screen_height)
                scout.param_type = "ORBIT"
                scout.param_angle = (i / 4.0) * 6.28
                scout.param_radius = 115
                scout.x = self.x + (i * 35)
                scout.y = self.y + self.height + 20
                wave_mgr.enemies.append(scout)

        px, py = player_pos
        cx = self.x + self.width // 2
        cy = self.y + self.height

        if now - self.last_shot >= 1300:
            self.last_shot = now
            base_ang = math.atan2(py - cy, px - cx)
            for offset in [-0.25, 0, 0.25]:
                ang = base_ang + offset
                enemy_bullets.append(EnemyBullet(cx, cy, math.cos(ang) * 6, math.sin(ang) * 6, damage=22))

    def draw(self, surface, font):
        now = pygame.time.get_ticks()
        rect = pygame.Rect(int(self.x), int(self.y), self.width, self.height)
        
        spr = BOSS_SPRITES.get("MINI")
        mask = BOSS_MASKS.get("MINI")
        if spr and mask:
            if now < self.hit_flash:
                flash_surf = mask.to_surface(setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))
                surface.blit(flash_surf, (self.x, self.y))
            else:
                surface.blit(spr, (self.x, self.y))
        else:
            body_c = COLOR_WHITE if now < self.hit_flash else (160, 40, 60)
            pygame.draw.rect(surface, body_c, rect, border_radius=12)
            pygame.draw.rect(surface, COLOR_GOLD, rect, width=2, border_radius=12)

        # Barra de Vida Superior Táctica
        bar_w = 440
        bar_h = 12
        bar_x = self.screen_width // 2 - bar_w // 2
        bar_y = 80
        
        panel_bg = pygame.Surface((bar_w + 30, 36), pygame.SRCALPHA)
        panel_bg.fill((10, 14, 22, 210))
        surface.blit(panel_bg, (bar_x - 15, bar_y - 20))
        pygame.draw.rect(surface, (45, 55, 75), (bar_x - 15, bar_y - 20, bar_w + 30, 36), width=1, border_radius=4)

        pygame.draw.rect(surface, (20, 24, 34), (bar_x, bar_y, bar_w, bar_h), border_radius=3)
        fill_w = int(bar_w * max(0, self.hp / self.max_hp))
        if fill_w > 0:
            pygame.draw.rect(surface, COLOR_RED, (bar_x, bar_y, fill_w, bar_h), border_radius=3)
        pygame.draw.rect(surface, COLOR_GOLD, (bar_x, bar_y, bar_w, bar_h), width=1, border_radius=3)
        
        name_t = font.render(f"// AMENAZA: CRUCERO DE ASALTO //  HP: {int(self.hp)} / {self.max_hp}", True, COLOR_GOLD)
        surface.blit(name_t, (self.screen_width // 2 - name_t.get_width() // 2, bar_y - 17))


class FinalBoss:
    """Jefe Final de 2 Fases con Drones Sanadores y Estandartes de Daño (+20% c/u)."""
    def __init__(self, screen_width, screen_height):
        load_boss_sprites()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.width = 260
        self.height = 130
        self.x = screen_width // 2 - self.width // 2
        self.y = -170
        self.target_y = 90
        
        self.phase = 1
        self.max_hp_p1 = 1000
        self.max_hp_p2 = 1200
        self.hp = self.max_hp_p1
        self.max_hp = self.max_hp_p1
        self.is_alive = True
        
        self.vx = 3.6  # antes 2.6 — más dinámico en Fase 1
        self.last_shot = pygame.time.get_ticks()
        self.spiral_angle = 0
        self.hit_flash = 0
        self.coin_reward = 600
        
        self.has_spawned_drones = False
        self.has_spawned_banners = False

    def init_phase_1(self, wave_mgr):
        if not self.has_spawned_drones:
            self.has_spawned_drones = True
            for i in range(5):
                ang = (i / 5.0) * 6.28
                dron = HealerDrone(self.x + self.width // 2, self.y, self, angle_offset=ang)
                wave_mgr.healer_drones.append(dron)

    def check_phase_2_banners(self, wave_mgr):
        if self.phase == 2 and not self.has_spawned_banners and self.hp <= (self.max_hp_p2 * 0.5):
            self.has_spawned_banners = True
            spacing = self.screen_width // 6
            for i in range(1, 6):
                bx = i * spacing - 18
                by = 150
                wave_mgr.damage_banners.append(DamageBanner(bx, by))

    def take_damage(self, amount):
        self.hp -= amount
        self.hit_flash = pygame.time.get_ticks() + 60
        
        if self.phase == 1 and self.hp <= 0:
            self.phase = 2
            self.max_hp = self.max_hp_p2
            self.hp = self.max_hp_p2
            self.vx = 4.6
            return "phase2_transition"

        elif self.phase == 2 and self.hp <= 0:
            self.hp = 0
            self.is_alive = False
            return "final_victory"
        return False

    def update(self, player_pos, enemy_bullets, wave_mgr):
        now = pygame.time.get_ticks()

        if self.y < self.target_y:
            self.y += 1.5
            return

        self.x += self.vx
        if self.x <= 30 or self.x >= self.screen_width - self.width - 30:
            self.vx *= -1

        self.check_phase_2_banners(wave_mgr)

        px, py = player_pos
        cx = self.x + self.width // 2
        cy = self.y + self.height

        active_banners_count = len([b for b in wave_mgr.damage_banners if b.is_alive])
        damage_multiplier = 1.0 + (active_banners_count * 0.20)

        if self.phase == 1:
            if now - self.last_shot >= 1100:
                self.last_shot = now
                base_dmg = int(18 * damage_multiplier)
                enemy_bullets.append(EnemyBullet(self.x + 20, cy, 0, 7, damage=base_dmg))
                enemy_bullets.append(EnemyBullet(self.x + self.width - 20, cy, 0, 7, damage=base_dmg))
                
                base_ang = math.atan2(py - cy, px - cx)
                for off in [-0.25, 0, 0.25]:
                    ang = base_ang + off
                    enemy_bullets.append(EnemyBullet(cx, cy, math.cos(ang) * 5.5, math.sin(ang) * 5.5, damage=base_dmg))

        elif self.phase == 2:
            if now - self.last_shot >= 380:
                self.last_shot = now
                self.spiral_angle += 28
                rad = math.radians(self.spiral_angle)
                base_dmg = int(22 * damage_multiplier)
                enemy_bullets.append(EnemyBullet(cx, cy, math.cos(rad) * 6.5, math.sin(rad) * 6.5, damage=base_dmg))
                enemy_bullets.append(EnemyBullet(cx, cy, -math.cos(rad) * 6.5, -math.sin(rad) * 6.5, damage=base_dmg))

    def draw(self, surface, font):
        now = pygame.time.get_ticks()
        rect = pygame.Rect(int(self.x), int(self.y), self.width, self.height)
        
        key = "FINAL_P1" if self.phase == 1 else "FINAL_P2"
        spr = BOSS_SPRITES.get(key)
        mask = BOSS_MASKS.get(key)
        
        if spr and mask:
            if now < self.hit_flash:
                flash_surf = mask.to_surface(setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))
                surface.blit(flash_surf, (self.x, self.y))
            else:
                surface.blit(spr, (self.x, self.y))
        else:
            body_color = COLOR_WHITE if now < self.hit_flash else ((75, 20, 95) if self.phase == 1 else (195, 20, 20))
            pygame.draw.rect(surface, body_color, rect, border_radius=16)
            pygame.draw.rect(surface, COLOR_GOLD, rect, width=3, border_radius=16)

        # Barra de Vida Superior Táctica
        bar_w = 540
        bar_h = 14
        bar_x = self.screen_width // 2 - bar_w // 2
        bar_y = 80
        
        panel_bg = pygame.Surface((bar_w + 30, 38), pygame.SRCALPHA)
        panel_bg.fill((10, 14, 22, 215))
        surface.blit(panel_bg, (bar_x - 15, bar_y - 20))
        pygame.draw.rect(surface, (55, 68, 92), (bar_x - 15, bar_y - 20, bar_w + 30, 38), width=1, border_radius=4)

        pygame.draw.rect(surface, (20, 24, 34), (bar_x, bar_y, bar_w, bar_h), border_radius=3)
        fill_w = int(bar_w * max(0, self.hp / self.max_hp))
        bar_color = COLOR_PURPLE if self.phase == 1 else COLOR_RED
        if fill_w > 0:
            pygame.draw.rect(surface, bar_color, (bar_x, bar_y, fill_w, bar_h), border_radius=3)
        pygame.draw.rect(surface, COLOR_GOLD, (bar_x, bar_y, bar_w, bar_h), width=1, border_radius=3)

        title = f"// AMENAZA NIVEL OMEGA: DREADNOUGHT [FASE {self.phase}] //  HP: {int(self.hp)} / {self.max_hp}"
        name_t = font.render(title, True, COLOR_GOLD)
        surface.blit(name_t, (self.screen_width // 2 - name_t.get_width() // 2, bar_y - 17))