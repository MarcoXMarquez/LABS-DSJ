# src/shop.py
import pygame
from src.config import (
    COLOR_WHITE, COLOR_GOLD, COLOR_YELLOW, COLOR_CYAN,
    COLOR_CARD_BG, COLOR_DARK_GRAY, COLOR_BLACK, COLOR_GREEN, COLOR_RED
)
from src.ui import Button, draw_text
from src.weapons import (
    WEAPON_SNIPER, WEAPON_MINIGUN, WEAPON_SPREAD, WEAPON_MISSILE, WEAPON_HOMING
)

class Shop:
    """Tienda y Hangar Espacial de Mejoras de Armas."""
    def __init__(self, screen_width, screen_height, font_title, font_btn, font_small):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font_title = font_title
        self.font_btn = font_btn
        self.font_small = font_small

        # Niveles de mejora de cada arma (0 a 3)
        self.upgrades = {
            WEAPON_SNIPER: {"level": 0, "name": "Cañón Sniper", "desc": "+30% Daño por nivel", "max": 3, "base_cost": 80},
            WEAPON_MINIGUN: {"level": 0, "name": "Metralleta Vulcan", "desc": "+25% Cadencia de tiro", "max": 3, "base_cost": 70},
            WEAPON_SPREAD: {"level": 0, "name": "Escopeta Flak", "desc": "+2 Perdigones adicionales", "max": 3, "base_cost": 75},
            WEAPON_MISSILE: {"level": 0, "name": "Lanzamisiles", "desc": "+1 Capacidad máxima (hasta 5 misiles)", "max": 2, "base_cost": 100},
            WEAPON_HOMING: {"level": 0, "name": "Drones Teledirigidos", "desc": "+40% Velocidad de rastreo", "max": 3, "base_cost": 85},
        }

        # Botón para volver
        self.btn_back = Button(screen_width // 2 - 140, screen_height - 90, 280, 50, "VOLVER A LA BATALLA (ESC)", font_btn)

        # Botones de compra por cada arma
        self.buy_buttons = {}
        self.init_cards_layout()

    def init_cards_layout(self):
        """Calcula la posición de las 5 tarjetas de armas en la pantalla."""
        card_w, card_h = 240, 310
        gap = 25
        total_w = (5 * card_w) + (4 * gap)
        start_x = (self.screen_width - total_w) // 2
        card_y = 170

        weapons = [WEAPON_SNIPER, WEAPON_MINIGUN, WEAPON_SPREAD, WEAPON_MISSILE, WEAPON_HOMING]
        for i, w_id in enumerate(weapons):
            cx = start_x + (i * (card_w + gap))
            btn = Button(cx + 20, card_y + card_h - 60, card_w - 40, 42, "MEJORAR", self.font_small)
            self.buy_buttons[w_id] = (cx, card_y, card_w, card_h, btn)

    def get_cost(self, weapon_id):
        upg = self.upgrades[weapon_id]
        if upg["level"] >= upg["max"]:
            return "MAX"
        return int(upg["base_cost"] * (1.6 ** upg["level"]))

    def try_buy(self, weapon_id, player, weapon_sys):
        """Intenta comprar una mejora si el jugador tiene suficientes monedas."""
        cost = self.get_cost(weapon_id)
        if cost == "MAX":
            return False, "Nivel Máximo"

        if player.coins >= cost:
            player.coins -= cost
            self.upgrades[weapon_id]["level"] += 1
            lvl = self.upgrades[weapon_id]["level"]

            # Aplicar efecto permanente en el sistema de armas
            if weapon_id == WEAPON_MISSILE:
                weapon_sys.max_missile_ammo = 3 + lvl
                weapon_sys.missile_ammo = min(weapon_sys.max_missile_ammo, weapon_sys.missile_ammo + 1)
            return True, f"¡Mejora Lv.{lvl} adquirida!"
        return False, "Monedas insuficientes"

    def draw(self, surface, player, mouse_pos):
        surface.fill(COLOR_BLACK)

        # Encabezado
        draw_text(surface, "🛸 HANGAR ESPACIAL & TIENDA DE ARMAS 🛸", self.font_title, COLOR_GOLD, (self.screen_width // 2, 60))
        draw_text(surface, "Gasta tus créditos espaciales para mejorar permanentemente tu arsenal", self.font_small, COLOR_CYAN, (self.screen_width // 2, 105))
        
        # Saldo de Monedas
        coin_txt = self.font_btn.render(f"🪙 CRÉDITOS DISPONIBLES: {player.coins}", True, COLOR_YELLOW)
        surface.blit(coin_txt, (self.screen_width // 2 - coin_txt.get_width() // 2, 130))

        # Tarjetas de las 5 Armas
        for w_id, (cx, cy, cw, ch, btn) in self.buy_buttons.items():
            upg = self.upgrades[w_id]
            rect = pygame.Rect(cx, cy, cw, ch)
            
            # Fondo de tarjeta
            pygame.draw.rect(surface, COLOR_CARD_BG, rect, border_radius=12)
            border_c = COLOR_GOLD if upg["level"] == upg["max"] else COLOR_CYAN
            pygame.draw.rect(surface, border_c, rect, width=2, border_radius=12)

            # Título del arma
            t_name = self.font_small.render(upg["name"], True, COLOR_GOLD)
            surface.blit(t_name, (cx + cw//2 - t_name.get_width()//2, cy + 18))

            # Nivel actual
            lvl_str = f"NIVEL: {upg['level']} / {upg['max']}"
            t_lvl = pygame.font.SysFont("Arial", 13, bold=True).render(lvl_str, True, COLOR_WHITE)
            surface.blit(t_lvl, (cx + cw//2 - t_lvl.get_width()//2, cy + 50))

            # Descripción de la mejora
            desc_lines = upg["desc"].split(" (")
            dy = cy + 90
            for dl in desc_lines:
                t_desc = pygame.font.SysFont("Arial", 12).render(dl.replace(")", ""), True, (200, 200, 220))
                surface.blit(t_desc, (cx + cw//2 - t_desc.get_width()//2, dy))
                dy += 20

            # Coste
            cost = self.get_cost(w_id)
            cost_str = f"Precio: {cost} 🪙" if cost != "MAX" else "¡COMPLETADO!"
            cost_c = COLOR_YELLOW if cost != "MAX" else COLOR_GREEN
            t_cost = pygame.font.SysFont("Arial", 14, bold=True).render(cost_str, True, cost_c)
            surface.blit(t_cost, (cx + cw//2 - t_cost.get_width()//2, cy + 185))

            # Botón de Compra
            if cost != "MAX":
                btn.text = "MEJORAR"
                btn.check_hover(mouse_pos)
                btn.draw(surface)

        # Botón Volver
        self.btn_back.check_hover(mouse_pos)
        self.btn_back.draw(surface)
