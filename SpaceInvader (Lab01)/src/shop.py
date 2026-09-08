# src/shop.py
import pygame
from src.config import (
    COLOR_WHITE, COLOR_GOLD, COLOR_YELLOW, COLOR_CYAN,
    COLOR_CARD_BG, COLOR_DARK_GRAY, COLOR_BLACK, COLOR_GREEN, COLOR_RED, COLOR_ORANGE, COLOR_PURPLE
)
from src.ui import Button, draw_text, draw_credit_token
from src.weapons import (
    WEAPON_SNIPER, WEAPON_MINIGUN, WEAPON_SPREAD, WEAPON_MISSILE, WEAPON_HOMING
)

WEAPON_COLORS = {
    WEAPON_SNIPER: COLOR_CYAN,
    WEAPON_MINIGUN: COLOR_YELLOW,
    WEAPON_SPREAD: COLOR_ORANGE,
    WEAPON_MISSILE: COLOR_RED,
    WEAPON_HOMING: COLOR_PURPLE
}

class Shop:
    """Tienda y Hangar Espacial de Mejoras de Armas con diseno tactico y responsive."""
    def __init__(self, screen_width, screen_height, font_title, font_btn, font_small):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font_title = font_title
        self.font_btn = font_btn
        self.font_small = font_small

        # Fuentes cacheadas para optimizacion extrema (0 instanciaciones por frame)
        self.font_card_title = pygame.font.Font('freesansbold.ttf', 14)
        self.font_card_lvl = pygame.font.Font('freesansbold.ttf', 12)
        self.font_card_desc = pygame.font.Font('freesansbold.ttf', 11)
        self.font_card_cost = pygame.font.Font('freesansbold.ttf', 13)

        # Niveles de mejora de cada arma (0 a 3)
        self.upgrades = {
            WEAPON_SNIPER: {"level": 0, "name": "CANON SNIPER", "desc": "+15% Dano | +1 Perforacion", "max": 3, "base_cost": 80},
            WEAPON_MINIGUN: {"level": 0, "name": "METRALLETA VULCAN", "desc": "+20% Cadencia de tiro", "max": 3, "base_cost": 70},
            WEAPON_SPREAD: {"level": 0, "name": "ESCOPETA FLAK", "desc": "+2 Perdigones por nivel", "max": 3, "base_cost": 75},
            WEAPON_MISSILE: {"level": 0, "name": "LANZAMISILES", "desc": "+1 Capacidad (max 5)", "max": 2, "base_cost": 100},
            WEAPON_HOMING: {"level": 0, "name": "MICRO-DRONES", "desc": "+25% Dano por impacto", "max": 3, "base_cost": 85},
        }

        # Boton para volver
        self.btn_back = Button(screen_width // 2 - 150, screen_height - 75, 300, 46, "VOLVER AL COMBATE (ESC)", font_btn)

        # Botones de compra por cada arma
        self.buy_buttons = {}
        self.init_cards_layout()

    def init_cards_layout(self):
        """Calcula de forma responsive la distribucion centrada de las 5 tarjetas."""
        weapons = [WEAPON_SNIPER, WEAPON_MINIGUN, WEAPON_SPREAD, WEAPON_MISSILE, WEAPON_HOMING]
        gap = 14
        available_w = self.screen_width - 80 - (4 * gap)
        card_w = min(220, available_w // 5)
        card_h = 320
        total_w = (5 * card_w) + (4 * gap)
        start_x = (self.screen_width - total_w) // 2
        card_y = 165

        for i, w_id in enumerate(weapons):
            cx = start_x + (i * (card_w + gap))
            btn = Button(cx + 16, card_y + card_h - 52, card_w - 32, 38, "MEJORAR", self.font_card_cost)
            self.buy_buttons[w_id] = (cx, card_y, card_w, card_h, btn)

    def get_cost(self, weapon_id):
        upg = self.upgrades[weapon_id]
        if upg["level"] >= upg["max"]:
            return "MAX"
        return int(upg["base_cost"] * (1.6 ** upg["level"]))

    def try_buy(self, weapon_id, player, weapon_sys):
        """Intenta comprar una mejora si el jugador tiene suficientes creditos."""
        cost = self.get_cost(weapon_id)
        if cost == "MAX":
            return False, "Nivel Maximo"

        if player.coins >= cost:
            player.coins -= cost
            self.upgrades[weapon_id]["level"] += 1
            lvl = self.upgrades[weapon_id]["level"]

            if weapon_id == WEAPON_MISSILE:
                weapon_sys.max_missile_ammo = 3 + lvl
                weapon_sys.missile_ammo = min(weapon_sys.max_missile_ammo, weapon_sys.missile_ammo + 1)
            return True, f"Mejora Nv.{lvl} adquirida"
        return False, "Creditos insuficientes"

    def draw(self, surface, player, mouse_pos):
        surface.fill((8, 10, 16))

        # Encabezado tactico
        draw_text(surface, "[ HANGAR ESPACIAL // ARMERIA DE FLOTA ]", self.font_title, COLOR_GOLD, (self.screen_width // 2, 50))
        draw_text(surface, "Sistemas de combate y mejoras permanentes de armamento", self.font_small, (160, 175, 200), (self.screen_width // 2, 88))
        
        # Saldo de Creditos (Pill central)
        bal_w, bal_h = 320, 36
        bal_x = self.screen_width // 2 - bal_w // 2
        bal_y = 112
        pygame.draw.rect(surface, (15, 20, 30), (bal_x, bal_y, bal_w, bal_h), border_radius=6)
        pygame.draw.rect(surface, (55, 68, 92), (bal_x, bal_y, bal_w, bal_h), width=1, border_radius=6)
        draw_credit_token(surface, bal_x + 22, bal_y + 18, radius=7)
        bal_t = self.font_btn.render(f"CREDITOS DISPONIBLES: {player.coins} CR", True, COLOR_GOLD)
        surface.blit(bal_t, (bal_x + 40, bal_y + 9))

        # Tarjetas de las 5 Armas
        weapons = [WEAPON_SNIPER, WEAPON_MINIGUN, WEAPON_SPREAD, WEAPON_MISSILE, WEAPON_HOMING]
        for idx, w_id in enumerate(weapons):
            cx, cy, cw, ch, btn = self.buy_buttons[w_id]
            upg = self.upgrades[w_id]
            w_color = WEAPON_COLORS.get(w_id, COLOR_CYAN)
            is_max = (upg["level"] >= upg["max"])
            
            rect = pygame.Rect(cx, cy, cw, ch)
            
            # Fondo y borde de tarjeta
            pygame.draw.rect(surface, (14, 18, 28), rect, border_radius=8)
            border_c = COLOR_GOLD if is_max else (50, 62, 85)
            pygame.draw.rect(surface, border_c, rect, width=1, border_radius=8)

            # Insignia de indice [ 1 ] a [ 5 ]
            num_rect = pygame.Rect(cx + 12, cy + 12, 24, 20)
            pygame.draw.rect(surface, (24, 30, 44), num_rect, border_radius=3)
            num_t = self.font_card_desc.render(f"{idx + 1}", True, w_color)
            surface.blit(num_t, (cx + 12 + (24 - num_t.get_width()) // 2, cy + 15))

            # Titulo del arma
            t_name = self.font_card_title.render(upg["name"], True, w_color)
            surface.blit(t_name, (cx + cw // 2 - t_name.get_width() // 2, cy + 42))

            # Pips de nivel [X][X][ ]
            lvl_str = f"NIVEL: {upg['level']} / {upg['max']}"
            t_lvl = self.font_card_lvl.render(lvl_str, True, COLOR_WHITE)
            surface.blit(t_lvl, (cx + cw // 2 - t_lvl.get_width() // 2, cy + 72))

            pip_w = 14
            pips_total_w = upg["max"] * pip_w + (upg["max"] - 1) * 6
            pip_start_x = cx + cw // 2 - pips_total_w // 2
            for pi in range(upg["max"]):
                px = pip_start_x + pi * (pip_w + 6)
                py = cy + 96
                if pi < upg["level"]:
                    pygame.draw.rect(surface, w_color, (px, py, pip_w, 6), border_radius=2)
                else:
                    pygame.draw.rect(surface, (30, 36, 50), (px, py, pip_w, 6), border_radius=2)
                    pygame.draw.rect(surface, (60, 70, 90), (px, py, pip_w, 6), width=1, border_radius=2)

            pygame.draw.line(surface, (28, 34, 48), (cx + 16, cy + 118), (cx + cw - 16, cy + 118), 1)

            # Descripcion de la mejora
            desc_lines = upg["desc"].split(" | ")
            dy = cy + 135
            for dl in desc_lines:
                t_desc = self.font_card_desc.render(dl, True, (165, 178, 198))
                surface.blit(t_desc, (cx + cw // 2 - t_desc.get_width() // 2, dy))
                dy += 20

            # Coste
            cost = self.get_cost(w_id)
            if cost != "MAX":
                cost_str = f"COSTE: {cost} CR"
                t_cost = self.font_card_cost.render(cost_str, True, COLOR_GOLD if player.coins >= cost else COLOR_RED)
            else:
                t_cost = self.font_card_cost.render("[ MAXIMO ]", True, COLOR_GREEN)
            surface.blit(t_cost, (cx + cw // 2 - t_cost.get_width() // 2, cy + 225))

            # Boton de Compra
            if cost != "MAX":
                can_afford = (player.coins >= cost)
                btn.text = "MEJORAR" if can_afford else "CREDITOS -"
                btn.check_hover(mouse_pos)
                btn.draw(surface)
            else:
                # Indicador completado
                max_rect = pygame.Rect(cx + 16, cy + ch - 52, cw - 32, 38)
                pygame.draw.rect(surface, (20, 35, 25), max_rect, border_radius=6)
                pygame.draw.rect(surface, COLOR_GREEN, max_rect, width=1, border_radius=6)
                mt = self.font_card_lvl.render("COMPLETADO", True, COLOR_GREEN)
                surface.blit(mt, (cx + cw // 2 - mt.get_width() // 2, cy + ch - 42))

        # Boton Volver
        self.btn_back.check_hover(mouse_pos)
        self.btn_back.draw(surface)
