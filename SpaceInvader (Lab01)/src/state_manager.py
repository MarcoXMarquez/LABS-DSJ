# src/state_manager.py
import pygame
from src.config import (
    GAME_TITLE, STATE_MENU, STATE_PLAYING, STATE_PAUSED,
    STATE_SHOP, STATE_GAME_OVER, STATE_VICTORY,
    COLOR_BLACK, COLOR_WHITE, COLOR_GOLD, COLOR_CYAN
)
from src.ui import Button, draw_text, draw_pause_overlay, draw_run_summary
from src.shop import Shop


class DisplayManager:
    """Maneja la pantalla completa nativa sin deformaciones."""
    def __init__(self):
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.DOUBLEBUF)
        pygame.display.set_caption(GAME_TITLE)
        self.width, self.height = self.screen.get_size()

    def get_screen(self):
        return self.screen


class GameStateManager:
    """Gestiona los estados y dibuja los menús correspondientes."""
    def __init__(self, screen_width, screen_height, font_title, font_btn, font_sub, font_small):
        self.current_state = STATE_MENU
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.font_title = font_title
        self.font_btn = font_btn
        self.font_sub = font_sub
        self.font_small = font_small
        
        # Tienda
        self.shop = Shop(screen_width, screen_height, font_title, font_btn, font_small)
        
        # Botones del Menú Principal
        btn_w, btn_h = 280, 52
        cx = screen_width // 2 - btn_w // 2
        cy = screen_height // 2
        
        self.btn_start = Button(cx, cy - 40, btn_w, btn_h, "INICIAR MISIÓN", font_btn)
        self.btn_shop_menu = Button(cx, cy + 25, btn_w, btn_h, "TIENDA / HANGAR (T)", font_btn)
        self.btn_exit = Button(cx, cy + 90, btn_w, btn_h, "SALIR (ESC)", font_btn)

        # Botones de Pausa
        self.btn_resume = Button(cx, cy - 60, btn_w, btn_h, "CONTINUAR", font_btn)
        self.btn_pause_shop = Button(cx, cy + 5, btn_w, btn_h, "TIENDA DE ARMAS", font_btn)
        self.btn_restart = Button(cx, cy + 70, btn_w, btn_h, "REINICIAR", font_btn)
        self.btn_pause_menu = Button(cx, cy + 135, btn_w, btn_h, "MENÚ PRINCIPAL", font_btn)

        # Botones de Pantalla de Resumen (Victoria / Game Over)
        self.btn_play_again = Button(cx - 160, screen_height - 100, 260, 50, "JUGAR OTRA VEZ", font_btn)
        self.btn_summary_menu = Button(cx + 160, screen_height - 100, 260, 50, "MENÚ PRINCIPAL", font_btn)

    def set_state(self, new_state):
        self.current_state = new_state

    def draw_main_menu(self, surface, mouse_pos):
        surface.fill(COLOR_BLACK)
        cy = self.screen_height // 2
        draw_text(surface, "SPACE INVADERS", self.font_title, COLOR_GOLD, (self.screen_width // 2, cy - 180))
        draw_text(surface, "— ROGUE LEGACY —", self.font_btn, COLOR_CYAN, (self.screen_width // 2, cy - 120))
        draw_text(surface, "WASD / Flechas: Mover | Espacio: Disparo | 1-5: Armas | Shift: Dash | F: Especial | T: Tienda", 
                  self.font_small, COLOR_WHITE, (self.screen_width // 2, cy - 75))

        for btn in [self.btn_start, self.btn_shop_menu, self.btn_exit]:
            btn.check_hover(mouse_pos)
            btn.draw(surface)

    def draw_pause_menu(self, surface, mouse_pos):
        draw_pause_overlay(surface, self.screen_width, self.screen_height, self.font_title, self.font_btn)
        for btn in [self.btn_resume, self.btn_pause_shop, self.btn_restart, self.btn_pause_menu]:
            btn.check_hover(mouse_pos)
            btn.draw(surface)

    def draw_shop_menu(self, surface, player, mouse_pos):
        self.shop.draw(surface, player, mouse_pos)

    def draw_summary_screen(self, surface, player, stats, mouse_pos, is_victory=True):
        draw_run_summary(surface, player, stats, self.screen_width, self.screen_height,
                         self.font_title, self.font_sub, self.font_small, is_victory)
        for btn in [self.btn_play_again, self.btn_summary_menu]:
            btn.check_hover(mouse_pos)
            btn.draw(surface)