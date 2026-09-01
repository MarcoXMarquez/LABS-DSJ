# src/ui.py
import pygame
from src.config import (
    COLOR_WHITE, COLOR_GREEN, COLOR_RED, COLOR_BLUE,
    COLOR_YELLOW, COLOR_CARD_BG, COLOR_GOLD,
    COLOR_CYAN, COLOR_BLACK
)


class Button:
    """Botón interactivo con hover y clics."""

    def __init__(self, x, y, width, height, text, font, base_color=COLOR_CARD_BG, hover_color=COLOR_BLUE,
                 text_color=COLOR_WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.base_color = base_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False

    def update_position(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered

    def is_clicked(self, mouse_pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(mouse_pos)
        return False

    def draw(self, surface):
        current_color = self.hover_color if self.is_hovered else self.base_color
        pygame.draw.rect(surface, current_color, self.rect, border_radius=10)
        border_color = COLOR_CYAN if self.is_hovered else COLOR_WHITE
        pygame.draw.rect(surface, border_color, self.rect, width=2, border_radius=10)

        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)


def draw_text(surface, text, font, color, center_pos, shadow=True):
    """Dibuja texto con sombra para máxima legibilidad."""
    if shadow:
        shadow_surf = font.render(text, True, (15, 15, 20))
        shadow_rect = shadow_surf.get_rect(center=(center_pos[0] + 2, center_pos[1] + 2))
        surface.blit(shadow_surf, shadow_rect)

    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(center=center_pos)
    surface.blit(text_surf, text_rect)
    return text_rect


def draw_pause_overlay(surface, screen_width, screen_height, font_title, font_sub):
    """Capa translúcida de pausa adaptada al tamaño total del monitor."""
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 190))
    surface.blit(overlay, (0, 0))

    draw_text(surface, "JUEGO PAUSADO", font_title, COLOR_GOLD, (screen_width // 2, screen_height // 2 - 160))
    draw_text(surface, "Presiona ESC o P para reanudar", font_sub, COLOR_WHITE,
              (screen_width // 2, screen_height // 2 - 100))


def draw_hud(surface, player, score, screen_width, font_hud, font_small):
    """HUD adaptado a la resolución nativa."""
    # 1. Barra de Vida (HP)
    bar_x, bar_y = 30, 25
    bar_width, bar_height = 240, 24
    pygame.draw.rect(surface, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height), border_radius=6)

    hp_percent = max(0, player.hp / player.max_hp)
    fill_width = int(bar_width * hp_percent)
    hp_color = COLOR_GREEN if hp_percent > 0.5 else (COLOR_YELLOW if hp_percent > 0.25 else COLOR_RED)

    if fill_width > 0:
        pygame.draw.rect(surface, hp_color, (bar_x, bar_y, fill_width, bar_height), border_radius=6)
    pygame.draw.rect(surface, COLOR_WHITE, (bar_x, bar_y, bar_width, bar_height), width=2, border_radius=6)

    hp_text = font_small.render(f"HP: {int(player.hp)} / {player.max_hp}", True, COLOR_WHITE)
    surface.blit(hp_text, (bar_x + 8, bar_y + 4))

    # 2. Vidas
    lives_text = font_small.render(f"Vidas: {player.lives}", True, COLOR_CYAN)
    surface.blit(lives_text, (bar_x, bar_y + 32))

    # 3. Puntaje en la esquina superior derecha
    score_surf = font_hud.render(f"Puntos: {score}", True, COLOR_GOLD)
    surface.blit(score_surf, (screen_width - score_surf.get_width() - 30, 25))

    # 4. Badges de Habilidades y su Nivel
    badge_x = 30
    badge_y = 90
    for power_id, level in player.powers.items():
        if level > 0:
            badge_rect = pygame.Rect(badge_x, badge_y, 130, 28)
            pygame.draw.rect(surface, COLOR_CARD_BG, badge_rect, border_radius=6)
            pygame.draw.rect(surface, COLOR_GOLD if level == 3 else COLOR_CYAN, badge_rect, width=1, border_radius=6)

            p_text = font_small.render(f"{power_id} Lv.{level}", True, COLOR_WHITE)
            surface.blit(p_text, (badge_x + 10, badge_y + 5))
            badge_x += 140