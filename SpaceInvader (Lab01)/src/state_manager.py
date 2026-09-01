# src/state_manager.py
import pygame
from src.config import (
    GAME_TITLE, STATE_MENU, STATE_PLAYING, STATE_PAUSED,
    COLOR_BLACK, COLOR_WHITE, COLOR_GOLD, COLOR_CYAN
)
from src.ui import Button, draw_text, draw_pause_overlay


class DisplayManager:
    """Inicia nativamente en pantalla completa usando la resolución exacta del monitor."""

    def __init__(self):
        # Iniciar modo pantalla completa nativa sin deformaciones
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.DOUBLEBUF)
        pygame.display.set_caption(GAME_TITLE)

        # Dimensiones reales del monitor
        self.width, self.height = self.screen.get_size()

    def get_screen(self):
        return self.screen


class GameStateManager:
    """Gestiona los estados y centra los menús según el tamaño real de pantalla."""

    def __init__(self, screen_width, screen_height, font_title, font_btn):
        self.current_state = STATE_MENU
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font_title = font_title
        self.font_btn = font_btn

        # Botones del Menú Principal centrados
        btn_w, btn_h = 280, 55
        cx = screen_width // 2 - btn_w // 2
        cy = screen_height // 2

        self.btn_start = Button(cx, cy - 20, btn_w, btn_h, "INICIAR MISIÓN", font_btn)
        self.btn_exit = Button(cx, cy + 60, btn_w, btn_h, "SALIR (ESC)", font_btn)

        # Botones de Pausa centrados
        self.btn_resume = Button(cx, cy - 40, btn_w, btn_h, "CONTINUAR", font_btn)
        self.btn_restart = Button(cx, cy + 30, btn_w, btn_h, "REINICIAR", font_btn)
        self.btn_pause_menu = Button(cx, cy + 100, btn_w, btn_h, "MENÚ PRINCIPAL", font_btn)

    def set_state(self, new_state):
        self.current_state = new_state

    def draw_main_menu(self, surface, mouse_pos):
        surface.fill(COLOR_BLACK)

        cy = self.screen_height // 2
        draw_text(surface, "SPACE INVADERS", self.font_title, COLOR_GOLD, (self.screen_width // 2, cy - 180))
        draw_text(surface, "— ROGUE LEGACY —", self.font_btn, COLOR_CYAN, (self.screen_width // 2, cy - 120))
        draw_text(surface, "WASD / Flechas para moverte en 4 direcciones | Espacio para disparar | ESC para Pausa",
                  pygame.font.SysFont("Arial", 16), COLOR_WHITE, (self.screen_width // 2, cy - 75))

        for btn in [self.btn_start, self.btn_exit]:
            btn.check_hover(mouse_pos)
            btn.draw(surface)

    def draw_pause_menu(self, surface, mouse_pos):
        draw_pause_overlay(surface, self.screen_width, self.screen_height, self.font_title, self.font_btn)
        for btn in [self.btn_resume, self.btn_restart, self.btn_pause_menu]:
            btn.check_hover(mouse_pos)
            btn.draw(surface)