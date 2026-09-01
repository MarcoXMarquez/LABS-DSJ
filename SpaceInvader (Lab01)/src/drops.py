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
    POWER_FIRE:    {"color": COLOR_ORANGE,     "label": "FUEGO",    "sym": "🔥", "name": "FUEGO",     "symbol": "🔥"},
    POWER_ICE:     {"color": COLOR_BLUE,        "label": "HIELO",    "sym": "❄️",  "name": "HIELO",     "symbol": "❄️"},
    POWER_SHIELD:  {"color": COLOR_CYAN,        "label": "ESCUDO",   "sym": "🛡️",  "name": "ESCUDO",    "symbol": "🛡️"},
    POWER_ELECTRO: {"color": COLOR_YELLOW,      "label": "ELECTRO",  "sym": "⚡",  "name": "ELECTRO",   "symbol": "⚡"},
    POWER_VOID:    {"color": COLOR_PURPLE,      "label": "VACIO",    "sym": "🌀",  "name": "VACÍO",     "symbol": "🌀"},
    POWER_SPEED:   {"color": COLOR_GOLD,        "label": "VELOCIDAD","sym": "💨",  "name": "VELOCIDAD", "symbol": "💨"},
    POWER_HEALTH:  {"color": COLOR_GREEN,       "label": "VIDA",     "sym": "💚",  "name": "VIDA",      "symbol": "💚"},
    POWER_FUEL:    {"color": (230, 50, 180),    "label": "FUEL",     "sym": "⚗️",  "name": "FUEL",      "symbol": "⚗️"},
}


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
        """Dibuja la burbuja brillante con su icono interior."""
        pos = (int(self.x), int(self.y))
        color = self.config["color"]

        # Halo exterior translúcido
        pygame.draw.circle(surface, color, pos, self.radius, width=2)
        # Núcleo brillante interior
        pygame.draw.circle(surface, (color[0] // 2, color[1] // 2, color[2] // 2), pos, self.radius - 3)

        # Letra/Símbolo identificador
        font = pygame.font.SysFont("Arial", 12, bold=True)
        t = font.render(self.config["sym"], True, COLOR_WHITE)
        t_rect = t.get_rect(center=pos)
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