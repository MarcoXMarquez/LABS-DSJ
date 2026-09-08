# src/drops.py
import pygame
import math
import random
from src.config import (
    COLOR_RED, COLOR_BLUE, COLOR_CYAN, COLOR_YELLOW, COLOR_PURPLE,
    COLOR_GOLD, COLOR_GREEN, COLOR_WHITE, COLOR_ORANGE,
    DROP_SPEED, DROP_CHANCE
)

# Constantes de los 8 Poderes
POWER_FIRE = "FIRE"
POWER_ICE = "ICE"
POWER_SHIELD = "SHIELD"
POWER_ELECTRO = "ELECTRO"
POWER_VOID = "VOID"
POWER_SPEED = "SPEED"
POWER_HEALTH = "HEALTH"
POWER_FUEL = "FUEL"

ALL_POWERS = [
    POWER_FIRE, POWER_ICE, POWER_SHIELD, POWER_ELECTRO,
    POWER_VOID, POWER_SPEED, POWER_HEALTH, POWER_FUEL
]

POWER_CONFIG = {
    POWER_FIRE:    {"color": COLOR_ORANGE,     "label": "FUEGO",     "sym": "FIR", "name": "FUEGO",     "symbol": "FIR"},
    POWER_ICE:     {"color": COLOR_BLUE,       "label": "HIELO",     "sym": "ICE", "name": "HIELO",     "symbol": "ICE"},
    POWER_SHIELD:  {"color": COLOR_CYAN,       "label": "ESCUDO",    "sym": "SHD", "name": "ESCUDO",    "symbol": "SHD"},
    POWER_ELECTRO: {"color": COLOR_YELLOW,     "label": "ELECTRO",   "sym": "ELC", "name": "ELECTRO",   "symbol": "ELC"},
    POWER_VOID:    {"color": COLOR_PURPLE,     "label": "VACIO",     "sym": "VOD", "name": "VACÍO",     "symbol": "VOD"},
    POWER_SPEED:   {"color": COLOR_GOLD,       "label": "VELOCIDAD", "sym": "SPD", "name": "VELOCIDAD", "symbol": "SPD"},
    POWER_HEALTH:  {"color": COLOR_GREEN,      "label": "VIDA",      "sym": "HP",  "name": "VIDA",      "symbol": "HP"},
    POWER_FUEL:    {"color": (230, 50, 180),   "label": "FUEL",      "sym": "FUL", "name": "REACTOR",   "symbol": "FUL"},
}

_DROP_FONT = None

def get_drop_font():
    global _DROP_FONT
    if _DROP_FONT is None:
        _DROP_FONT = pygame.font.Font('freesansbold.ttf', 11)
    return _DROP_FONT


class PowerDrop:
    """Burbuja flotante de poder que cae al espacio."""

    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.power_type = power_type
        self.config = POWER_CONFIG[power_type]
        self.radius = 18
        self.base_speed = DROP_SPEED
        self.birth_time = pygame.time.get_ticks()
        self.is_collected = False

    def update(self, player=None):
        """Movimiento con ondulación e imán de atracción si tienes VACIO."""
        now = pygame.time.get_ticks()
        # Ondulación suave horizontal
        wobble = math.sin((now - self.birth_time) * 0.005) * 0.8
        self.x += wobble
        self.y += self.base_speed

        # Sinergia de atracción (Poder de Vacío)
        if player and player.powers.get(POWER_VOID, 0) > 0:
            p_center_x = player.x + player.width // 2
            p_center_y = player.y + player.height // 2
            dist = math.hypot(p_center_x - self.x, p_center_y - self.y)
            magnet_range = 150 + (player.powers[POWER_VOID] * 70)

            if dist < magnet_range and dist > 5:
                angle = math.atan2(p_center_y - self.y, p_center_x - self.x)
                pull_speed = 4 + (player.powers[POWER_VOID] * 2)
                self.x += math.cos(angle) * pull_speed
                self.y += math.sin(angle) * pull_speed

    def check_collision(self, player):
        """Detecta si el jugador toca la burbuja."""
        p_center_x = player.x + player.width // 2
        p_center_y = player.y + player.height // 2
        dist = math.hypot(p_center_x - self.x, p_center_y - self.y)
        if dist < (self.radius + min(player.width, player.height) // 2):
            self.is_collected = True
            return True
        return False

    def draw(self, surface):
        """Dibuja la cápsula de energía con halo de pulso y código táctico nítido."""
        pos = (int(self.x), int(self.y))
        color = self.config["color"]
        now = pygame.time.get_ticks()

        # Pulso sutil en el halo exterior
        pulse = math.sin((now - self.birth_time) * 0.007) * 2
        outer_r = int(self.radius + pulse)

        # 1. Halo exterior
        pygame.draw.circle(surface, color, pos, max(outer_r, self.radius), width=2)
        # 2. Núcleo oscuro tecnológico
        dark_bg = (max(10, color[0] // 5), max(10, color[1] // 5), max(15, color[2] // 5))
        pygame.draw.circle(surface, dark_bg, pos, self.radius - 2)
        pygame.draw.circle(surface, color, pos, self.radius - 2, width=1)

        # 3. Código táctico nítido con sombra
        font = get_drop_font()
        tag = self.config["sym"]
        shadow = font.render(tag, True, (0, 0, 0))
        t = font.render(tag, True, COLOR_WHITE)
        s_rect = shadow.get_rect(center=(pos[0] + 1, pos[1] + 1))
        t_rect = t.get_rect(center=pos)
        surface.blit(shadow, s_rect)
        surface.blit(t, t_rect)


class DropManager:
    """Gestiona la aparición y recolección de todas las burbujas."""

    def __init__(self):
        self.drops = []

    def try_spawn_drop(self, x, y, force=False):
        """Genera una burbuja aleatoria con probabilidad balanceada."""
        if force or random.random() < DROP_CHANCE:
            power = random.choice(ALL_POWERS)
            drop = PowerDrop(x, y, power)
            self.drops.append(drop)
            return True
        return False

    def update(self, player, screen_height):
        """Actualiza y recoge las burbujas. La colisión real se maneja en main.py."""
        for drop in self.drops:
            drop.update(player)

        # Eliminar las que salieron de la pantalla
        self.drops = [d for d in self.drops if not d.is_collected and d.y < screen_height + 50]

    def draw(self, surface):
        for drop in self.drops:
            drop.draw(surface)