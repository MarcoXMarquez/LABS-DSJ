# main.py
import pygame
import sys
from src.config import (
    FPS, STATE_MENU, STATE_PLAYING, STATE_PAUSED,
    COLOR_BLACK, COLOR_WHITE, COLOR_GREEN
)
from src.state_manager import DisplayManager, GameStateManager
from src.ui import draw_text

def main():
    pygame.init()
    pygame.mixer.init()
    clock = pygame.time.Clock()

    # 1. Configuración de Pantalla Completa Nativa
    display_mgr = DisplayManager()
    screen = display_mgr.get_screen()
    screen_width, screen_height = display_mgr.width, display_mgr.height

    # 2. Fuentes
    font_title = pygame.font.Font('freesansbold.ttf', 56)
    font_btn = pygame.font.Font('freesansbold.ttf', 22)
    font_hud = pygame.font.Font('freesansbold.ttf', 24)
    font_small = pygame.font.Font('freesansbold.ttf', 18)

    # 3. Administrador de Estados
    state_mgr = GameStateManager(screen_width, screen_height, font_title, font_btn)

    running = True
    while running:
        clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                # En el menú, ESC sale del juego. Durante el juego, ESC pausa/reanuda.
                if event.key == pygame.K_ESCAPE:
                    if state_mgr.current_state == STATE_PLAYING:
                        state_mgr.set_state(STATE_PAUSED)
                    elif state_mgr.current_state == STATE_PAUSED:
                        state_mgr.set_state(STATE_PLAYING)
                    elif state_mgr.current_state == STATE_MENU:
                        running = False

                elif event.key == pygame.K_p and state_mgr.current_state in (STATE_PLAYING, STATE_PAUSED):
                    state_mgr.set_state(STATE_PLAYING if state_mgr.current_state == STATE_PAUSED else STATE_PAUSED)

            # Eventos de Menú Principal
            if state_mgr.current_state == STATE_MENU:
                if state_mgr.btn_start.is_clicked(mouse_pos, event):
                    state_mgr.set_state(STATE_PLAYING)
                if state_mgr.btn_exit.is_clicked(mouse_pos, event):
                    running = False

            # Eventos de Menú de Pausa
            elif state_mgr.current_state == STATE_PAUSED:
                if state_mgr.btn_resume.is_clicked(mouse_pos, event):
                    state_mgr.set_state(STATE_PLAYING)
                if state_mgr.btn_restart.is_clicked(mouse_pos, event):
                    state_mgr.set_state(STATE_PLAYING)
                if state_mgr.btn_pause_menu.is_clicked(mouse_pos, event):
                    state_mgr.set_state(STATE_MENU)

        # Dibujado según estado
        if state_mgr.current_state == STATE_MENU:
            state_mgr.draw_main_menu(screen, mouse_pos)

        elif state_mgr.current_state == STATE_PLAYING:
            screen.fill(COLOR_BLACK)
            draw_text(screen, "¡MODO DE JUEGO NATIVO A PANTALLA COMPLETA!", font_title, COLOR_GREEN, (screen_width // 2, screen_height // 2 - 40))
            draw_text(screen, "Presiona ESC o P para pausar", font_btn, COLOR_WHITE, (screen_width // 2, screen_height // 2 + 30))

        elif state_mgr.current_state == STATE_PAUSED:
            state_mgr.draw_pause_menu(screen, mouse_pos)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()