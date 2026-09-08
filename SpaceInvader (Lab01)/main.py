# main.py
import pygame
import sys
import math
import random
from src.config import (
    FPS, STATE_MENU, STATE_PLAYING, STATE_PAUSED, STATE_SHOP,
    STATE_GAME_OVER, STATE_VICTORY,
    COLOR_BLACK, COLOR_WHITE, COLOR_GREEN, COLOR_RED, COLOR_GOLD, COLOR_CYAN, COLOR_YELLOW
)
from src.state_manager import DisplayManager, GameStateManager
from src.ui import draw_hud, draw_weapon_hud_bottom_right, draw_powerup_modal, draw_life_lost_alert, draw_summary_screen
from src.player import Player
from src.weapons import (
    WeaponSystem, MissileAmmoDrop,
    WEAPON_SNIPER, WEAPON_MINIGUN, WEAPON_SPREAD, WEAPON_MISSILE, WEAPON_HOMING
)
from src.drops import (
    DropManager, POWER_FIRE, POWER_ICE, POWER_SHIELD, POWER_ELECTRO,
    POWER_SPEED, POWER_HEALTH, POWER_FUEL, POWER_VOID, POWER_CONFIG
)
from src.enemies import (
    WaveManager, ENEMY_SCOUT, ENEMY_SHOUTER, ENEMY_TANK, ENEMY_KAMIKAZE
)
from src.bosses import MiniBoss, FinalBoss
from src.effects import Starfield, ParticleManager, FloatingTextManager, ScreenShake

def main():
    pygame.init()
    pygame.mixer.init()
    clock = pygame.time.Clock()

    # 1. Pantalla Completa Nativa
    display_mgr = DisplayManager()
    screen = display_mgr.get_screen()
    sw, sh = display_mgr.width, display_mgr.height

    # 2. Fuentes
    font_huge = pygame.font.Font('freesansbold.ttf', 38)
    font_title = pygame.font.Font('freesansbold.ttf', 44)
    font_large = pygame.font.Font('freesansbold.ttf', 20)
    font_hud = pygame.font.Font('freesansbold.ttf', 18)
    font_small = pygame.font.Font('freesansbold.ttf', 14)
    font_sub = pygame.font.Font('freesansbold.ttf', 22)
    font_btn = pygame.font.Font('freesansbold.ttf', 18)

    # 3. Sonidos
    try:
        laser_sound = pygame.mixer.Sound('laser.wav')
        explosion_sound = pygame.mixer.Sound('explosion.wav')
        pygame.mixer.music.load('background.wav')
        pygame.mixer.music.set_volume(0.35)
        pygame.mixer.music.play(-1)
    except Exception:
        laser_sound = None
        explosion_sound = None

    # 4. Efectos Visuales
    starfield = Starfield(sw, sh)
    particle_mgr = ParticleManager()
    text_mgr = FloatingTextManager()
    screen_shake = ScreenShake()

    # 5. Administrador de Estados
    state_mgr = GameStateManager(sw, sh, font_title, font_btn, font_sub, font_small)

    # Variables de Partida
    player = None
    weapon_sys = None
    drop_mgr = None
    wave_mgr = None
    mini_boss = None
    final_boss = None
    stats = {}
    level_transition_timer = 0
    previous_state = STATE_MENU
    power_modal_data = {"type": None, "level": 1, "synergies": [], "until": 0}

    # Botones dinámicos de pantalla de resumen
    summary_btn_retry = None
    summary_btn_menu = None

    def reset_game():
        nonlocal player, weapon_sys, drop_mgr, wave_mgr, mini_boss, final_boss, stats, level_transition_timer, power_modal_data
        player = Player(sw, sh)
        weapon_sys = WeaponSystem()
        drop_mgr = DropManager()
        wave_mgr = WaveManager(sw, sh)
        mini_boss = None
        final_boss = None
        level_transition_timer = 0
        power_modal_data = {"type": None, "level": 1, "synergies": [], "until": 0}
        stats = {
            'time_sec': 0,
            'start_ticks': pygame.time.get_ticks(),
            'kills': 0,
            'score': 0,
            'sector': 1
        }
        wave_mgr.start_level(1)

    reset_game()
    running = True

    while running:
        clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()
        now = pygame.time.get_ticks()

        # Actualizar estrellas y partículas globales
        starfield.update()
        particle_mgr.update()
        text_mgr.update()

        if state_mgr.current_state == STATE_PLAYING and not player.is_dying:
            stats['time_sec'] = (now - stats['start_ticks']) // 1000
            stats['sector'] = wave_mgr.current_level

        # --- GESTIÓN DE EVENTOS ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                # ESC: Pausar / Salir de Tienda / Salir del Juego
                if event.key == pygame.K_ESCAPE:
                    if state_mgr.current_state == STATE_PLAYING:
                        state_mgr.set_state(STATE_PAUSED)
                    elif state_mgr.current_state == STATE_PAUSED:
                        state_mgr.set_state(STATE_PLAYING)
                    elif state_mgr.current_state == STATE_SHOP:
                        state_mgr.set_state(previous_state)
                    elif state_mgr.current_state in (STATE_GAME_OVER, STATE_VICTORY):
                        state_mgr.set_state(STATE_MENU)
                    elif state_mgr.current_state == STATE_MENU:
                        running = False

                elif event.key == pygame.K_p and state_mgr.current_state in (STATE_PLAYING, STATE_PAUSED):
                    state_mgr.set_state(STATE_PLAYING if state_mgr.current_state == STATE_PAUSED else STATE_PAUSED)

                # Tecla 'T': Abrir Tienda
                elif event.key == pygame.K_t:
                    if state_mgr.current_state in (STATE_PLAYING, STATE_PAUSED, STATE_MENU):
                        previous_state = state_mgr.current_state
                        state_mgr.set_state(STATE_SHOP)

                # Reintentar con R en pantallas de fin de juego
                elif event.key == pygame.K_r and state_mgr.current_state in (STATE_GAME_OVER, STATE_VICTORY):
                    reset_game()
                    state_mgr.set_state(STATE_PLAYING)

                # Cambio de Armas con 1, 2, 3, 4, 5
                if state_mgr.current_state == STATE_PLAYING:
                    if event.key == pygame.K_1: weapon_sys.switch_weapon(WEAPON_SNIPER)
                    elif event.key == pygame.K_2: weapon_sys.switch_weapon(WEAPON_MINIGUN)
                    elif event.key == pygame.K_3: weapon_sys.switch_weapon(WEAPON_SPREAD)
                    elif event.key == pygame.K_4: weapon_sys.switch_weapon(WEAPON_MISSILE)
                    elif event.key == pygame.K_5: weapon_sys.switch_weapon(WEAPON_HOMING)
                    
                    # Habilidad Especial con 'F' (Consume Fuel)
                    elif event.key == pygame.K_f:
                        fuel_cost = 35 if player.powers[POWER_FUEL] >= 2 else 45
                        if player.fuel >= fuel_cost:
                            player.fuel -= fuel_cost
                            weapon_sys.use_special_skill(player, wave_mgr.enemies)
                            screen_shake.add_trauma(0.35)
                            if laser_sound: laser_sound.play()

                    # Dash con Shift
                    elif event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                        keys = pygame.key.get_pressed()
                        dx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
                        dy = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])
                        if player.trigger_dash(dx, dy):
                            particle_mgr.spawn_sparks(player.x + player.width // 2, player.y + player.height // 2, COLOR_CYAN, 12)
                            screen_shake.add_trauma(0.2)

            # --- EVENTOS EN MENÚ PRINCIPAL ---
            if state_mgr.current_state == STATE_MENU:
                if state_mgr.btn_start.is_clicked(mouse_pos, event):
                    reset_game()
                    state_mgr.set_state(STATE_PLAYING)
                if state_mgr.btn_shop_menu.is_clicked(mouse_pos, event):
                    previous_state = STATE_MENU
                    state_mgr.set_state(STATE_SHOP)
                if state_mgr.btn_exit.is_clicked(mouse_pos, event):
                    running = False

            # --- EVENTOS EN MENÚ DE PAUSA ---
            elif state_mgr.current_state == STATE_PAUSED:
                if state_mgr.btn_resume.is_clicked(mouse_pos, event):
                    state_mgr.set_state(STATE_PLAYING)
                if state_mgr.btn_pause_shop.is_clicked(mouse_pos, event):
                    previous_state = STATE_PAUSED
                    state_mgr.set_state(STATE_SHOP)
                if state_mgr.btn_restart.is_clicked(mouse_pos, event):
                    reset_game()
                    state_mgr.set_state(STATE_PLAYING)
                if state_mgr.btn_pause_menu.is_clicked(mouse_pos, event):
                    state_mgr.set_state(STATE_MENU)

            # --- EVENTOS EN TIENDA / HANGAR ---
            elif state_mgr.current_state == STATE_SHOP:
                if state_mgr.shop.btn_back.is_clicked(mouse_pos, event):
                    state_mgr.set_state(previous_state)
                for w_id, (_, _, _, _, btn) in state_mgr.shop.buy_buttons.items():
                    if btn.is_clicked(mouse_pos, event):
                        success, msg = state_mgr.shop.try_buy(w_id, player, weapon_sys)
                        if success:
                            text_mgr.add_text(sw // 2, sh - 140, msg, COLOR_GREEN)
                        else:
                            text_mgr.add_text(sw // 2, sh - 140, msg, COLOR_RED)

            # --- EVENTOS EN PANTALLA DE RESUMEN ---
            elif state_mgr.current_state in (STATE_GAME_OVER, STATE_VICTORY):
                if summary_btn_retry and summary_btn_retry.is_hovered and event.type == pygame.MOUSEBUTTONDOWN:
                    reset_game()
                    state_mgr.set_state(STATE_PLAYING)
                elif summary_btn_menu and summary_btn_menu.is_hovered and event.type == pygame.MOUSEBUTTONDOWN:
                    state_mgr.set_state(STATE_MENU)

        # --- LÓGICA DURANTE EL JUEGO ACTIVO ---
        if state_mgr.current_state == STATE_PLAYING:
            player.update(particle_mgr)

            # Si el jugador murió en la secuencia de explosión
            if not player.is_alive and not player.is_dying:
                screen_shake.add_trauma(0.9)
                state_mgr.set_state(STATE_GAME_OVER)

            # Si el modal de poder está pausando la acción, omitir updates de enemigos/balas
            is_power_frozen = (now < power_modal_data["until"])

            if not is_power_frozen and player.is_alive and not player.is_dying:
                keys = pygame.key.get_pressed()
                mouse_buttons = pygame.mouse.get_pressed()

                # 1. Movimiento del Jugador
                dx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
                dy = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])
                player.move(dx, dy)

                # 2. Disparo con Espacio o Clic Izquierdo
                if keys[pygame.K_SPACE] or mouse_buttons[0]:
                    shot_fired = weapon_sys.shoot(player, wave_mgr.enemies, state_mgr.shop)
                    if shot_fired and laser_sound:
                        laser_sound.play()

                # 3. Disparo Especial con Clic Derecho
                if mouse_buttons[2]:
                    fuel_cost = 35 if player.powers[POWER_FUEL] >= 2 else 45
                    if player.fuel >= fuel_cost:
                        player.fuel -= fuel_cost
                        weapon_sys.use_special_skill(player, wave_mgr.enemies)
                        screen_shake.add_trauma(0.35)
                        if laser_sound: laser_sound.play()

                # 4. Actualizar Proyectiles y Entidades
                all_target_enemies = list(wave_mgr.enemies)
                if mini_boss and mini_boss.is_alive: all_target_enemies.append(mini_boss)
                if final_boss and final_boss.is_alive: all_target_enemies.append(final_boss)

                weapon_sys.update(all_target_enemies, particle_mgr, player)
                
                # Recoger burbujas con Banner Modal y Freeze Cinemático
                for drop in drop_mgr.drops:
                    if not drop.is_collected and drop.check_collision(player):
                        new_lvl, leveled_up, new_syns = player.collect_power(drop.power_type)
                        power_modal_data = {
                            "type": drop.power_type,
                            "level": new_lvl,
                            "synergies": new_syns,
                            "until": now + 1200
                        }
                        particle_mgr.spawn_sparks(player.x + player.width // 2, player.y, COLOR_GOLD, 20)
                        screen_shake.add_trauma(0.25)

                drop_mgr.update(player, sh)
                wave_mgr.update((player.x + player.width // 2, player.y + player.height // 2))

                # Recogida de cápsulas físicas de misiles
                for drop in weapon_sys.ammo_drops:
                    if not drop.is_collected and math.hypot(player.x + player.width // 2 - drop.x, player.y + player.height // 2 - drop.y) < 36:
                        drop.is_collected = True
                        weapon_sys.missile_ammo = min(weapon_sys.max_missile_ammo, weapon_sys.missile_ammo + 1)
                        text_mgr.add_text(player.x, player.y - 25, "+1 MISIL", COLOR_RED)
                        particle_mgr.spawn_sparks(drop.x, drop.y, COLOR_RED, 8)

                # 5. Flujo de Niveles y Jefes
                if not wave_mgr.wave_in_progress and len(wave_mgr.enemies) == 0:
                    if wave_mgr.current_level == 6 and not mini_boss:
                        mini_boss = MiniBoss(sw, sh)
                        text_mgr.add_text(sw // 2 - 160, 200, "// ALERTA: CRUCERO DE ASALTO //", COLOR_RED)
                        screen_shake.add_trauma(0.6)

                    elif wave_mgr.current_level == 6 and mini_boss and not mini_boss.is_alive:
                        if level_transition_timer == 0:
                            level_transition_timer = now + 2500
                            text_mgr.add_text(sw // 2 - 140, 250, "[ CRUCERO DE ASALTO DESTRUIDO ]", COLOR_GOLD)
                        elif now > level_transition_timer:
                            level_transition_timer = 0
                            wave_mgr.start_level(7)

                    elif wave_mgr.current_level == 12 and not final_boss:
                        final_boss = FinalBoss(sw, sh)
                        final_boss.init_phase_1(wave_mgr)
                        text_mgr.add_text(sw // 2 - 170, 200, "// AMENAZA OMEGA: NAVE NODRIZA //", COLOR_RED)
                        screen_shake.add_trauma(0.8)

                    elif wave_mgr.current_level == 12 and final_boss and not final_boss.is_alive:
                        state_mgr.set_state(STATE_VICTORY)

                    elif wave_mgr.current_level not in (6, 12):
                        if level_transition_timer == 0:
                            level_transition_timer = now + 2000
                            text_mgr.add_text(sw // 2 - 110, 250, f"¡SECTOR {wave_mgr.current_level} LIMPIADO!", COLOR_GREEN)
                        elif now > level_transition_timer:
                            level_transition_timer = 0
                            wave_mgr.start_level(wave_mgr.current_level + 1)

                # 6. Actualización de Jefes
                if mini_boss and mini_boss.is_alive:
                    mini_boss.update((player.x + player.width // 2, player.y), wave_mgr.enemy_bullets, wave_mgr)
                if final_boss and final_boss.is_alive:
                    final_boss.update((player.x + player.width // 2, player.y), wave_mgr.enemy_bullets, wave_mgr)

                # 7. COLISIONES
                # A) Proyectiles vs Enemigos Comunes
                for bullet in weapon_sys.bullets:
                    if not bullet.is_alive: continue
                    for enemy in wave_mgr.enemies:
                        if not enemy.is_alive: continue
                        if math.hypot(enemy.x + enemy.width // 2 - bullet.x, enemy.y + enemy.height // 2 - bullet.y) < (bullet.radius + enemy.width // 2):
                            bullet.pierce -= 1
                            if bullet.pierce <= 0: bullet.is_alive = False

                            particle_mgr.spawn_sparks(bullet.x, bullet.y, COLOR_YELLOW, 6)

                            # Elementales
                            if bullet.is_fire:
                                f_lvl = player.powers.get(POWER_FIRE, 1)
                                enemy.apply_burn(1200 + (f_lvl * 600))
                            if bullet.is_ice:
                                i_lvl = player.powers.get(POWER_ICE, 1)
                                dur = 1000 if i_lvl <= 1 else (1500 if i_lvl == 2 else 2000)
                                enemy.apply_freeze(dur, is_full_freeze=(i_lvl >= 3))

                            # Sinergia Choque Térmico
                            if "CHOQUE TERMICO" in player.synergies and enemy.freeze_until > now and bullet.is_fire:
                                enemy.take_damage(bullet.damage * 2.0)
                                particle_mgr.spawn_explosion(enemy.x + enemy.width // 2, enemy.y + enemy.height // 2)
                            else:
                                enemy.take_damage(bullet.damage)

                            if not enemy.is_alive:
                                stats['kills'] += 1
                                stats['score'] += 250 if enemy.is_captain else 100
                                
                                coins_earned = enemy.coin_reward
                                player.add_coins(coins_earned)
                                text_mgr.add_text(enemy.x, enemy.y, f"+{coins_earned} CR", COLOR_YELLOW)
                                
                                particle_mgr.spawn_explosion(enemy.x + enemy.width // 2, enemy.y + enemy.height // 2, is_large=enemy.is_captain)
                                if explosion_sound: explosion_sound.play()

                                drop_chance = 0.40 if enemy.is_captain else (0.25 if enemy.elemental_power else 0.12)
                                if random.random() < drop_chance:
                                    drop_mgr.try_spawn_drop(enemy.x, enemy.y, force=True)

                                if bullet.weapon_type == WEAPON_MISSILE:
                                    weapon_sys.ammo_drops.append(MissileAmmoDrop(enemy.x, enemy.y))
                                    screen_shake.add_trauma(0.3)
                            break

                # B) Proyectiles vs Mini-Boss
                if mini_boss and mini_boss.is_alive:
                    for bullet in weapon_sys.bullets:
                        if not bullet.is_alive: continue
                        if math.hypot(mini_boss.x + mini_boss.width // 2 - bullet.x, mini_boss.y + mini_boss.height // 2 - bullet.y) < (bullet.radius + mini_boss.width // 2):
                            bullet.pierce -= 1
                            if bullet.pierce <= 0: bullet.is_alive = False
                            particle_mgr.spawn_sparks(bullet.x, bullet.y, COLOR_WHITE, 8)
                            
                            res = mini_boss.take_damage(bullet.damage, wave_mgr.enemies)
                            if res == "regenerated":
                                text_mgr.add_text(mini_boss.x + 20, mini_boss.y - 30, "¡EL JEFE SE HA REGENERADO POR SUS MINIONS!", COLOR_RED)
                                screen_shake.add_trauma(0.5)
                            elif res == "killed":
                                stats['kills'] += 1
                                stats['score'] += 1500
                                player.add_coins(mini_boss.coin_reward)
                                text_mgr.add_text(mini_boss.x + 40, mini_boss.y, f"+{mini_boss.coin_reward} CR", COLOR_GOLD)
                                drop_mgr.try_spawn_drop(mini_boss.x + mini_boss.width // 2, mini_boss.y + mini_boss.height // 2, force=True)
                                particle_mgr.spawn_explosion(mini_boss.x + mini_boss.width // 2, mini_boss.y + mini_boss.height // 2, is_large=True)
                                screen_shake.add_trauma(0.7)
                                if explosion_sound: explosion_sound.play()

                # C) Proyectiles vs Drones y Estandartes
                for bullet in weapon_sys.bullets:
                    if not bullet.is_alive: continue
                    for dron in wave_mgr.healer_drones:
                        if dron.is_alive and math.hypot(dron.x + dron.width // 2 - bullet.x, dron.y + dron.height // 2 - bullet.y) < (bullet.radius + 18):
                            bullet.is_alive = False
                            if dron.take_damage(bullet.damage):
                                particle_mgr.spawn_explosion(dron.x, dron.y)
                                player.add_coins(40)
                                if random.random() < 0.15: drop_mgr.try_spawn_drop(dron.x, dron.y, force=True)

                    for banner in wave_mgr.damage_banners:
                        if banner.is_alive and math.hypot(banner.x + banner.width // 2 - bullet.x, banner.y + banner.height // 2 - bullet.y) < (bullet.radius + 20):
                            bullet.is_alive = False
                            if banner.take_damage(bullet.damage):
                                particle_mgr.spawn_explosion(banner.x, banner.y)
                                player.add_coins(50)
                                if random.random() < 0.15: drop_mgr.try_spawn_drop(banner.x, banner.y, force=True)

                # D) Proyectiles vs Boss Final
                if final_boss and final_boss.is_alive:
                    for bullet in weapon_sys.bullets:
                        if not bullet.is_alive: continue
                        if math.hypot(final_boss.x + final_boss.width // 2 - bullet.x, final_boss.y + final_boss.height // 2 - bullet.y) < (bullet.radius + final_boss.width // 2):
                            bullet.pierce -= 1
                            if bullet.pierce <= 0: bullet.is_alive = False
                            particle_mgr.spawn_sparks(bullet.x, bullet.y, COLOR_GOLD, 8)
                            
                            res = final_boss.take_damage(bullet.damage)
                            if res == "phase2_transition":
                                text_mgr.add_text(sw // 2 - 170, 220, "// FASE 2: NUCLEO EN ENRAGE //", COLOR_RED)
                                particle_mgr.spawn_explosion(final_boss.x + final_boss.width // 2, final_boss.y + final_boss.height // 2, is_large=True)
                                screen_shake.add_trauma(0.8)
                            elif res == "final_victory":
                                stats['kills'] += 1
                                stats['score'] += 5000
                                player.add_coins(final_boss.coin_reward)
                                particle_mgr.spawn_explosion(final_boss.x + final_boss.width // 2, final_boss.y + final_boss.height // 2, is_large=True)
                                screen_shake.add_trauma(1.0)
                                if explosion_sound: explosion_sound.play()
                                state_mgr.set_state(STATE_VICTORY)

                # E) Proyectiles Enemigos vs Jugador
                for b in wave_mgr.enemy_bullets:
                    if not b.is_alive: continue
                    dist_to_p = math.hypot(player.x + player.width // 2 - b.x, player.y + player.height // 2 - b.y)
                    if dist_to_p < (b.radius + 20):
                        b.is_alive = False
                        screen_shake.add_trauma(0.35)
                        dmg_res = player.take_damage(b.damage)
                        if dmg_res == "shield_explosion":
                            for other_b in wave_mgr.enemy_bullets: other_b.is_alive = False
                            particle_mgr.spawn_explosion(player.x + player.width // 2, player.y + player.height // 2)

                # F) Choque Físico Jugador vs Naves Invasoras y Jefes
                if not player.is_invulnerable:
                    p_cx = player.x + player.width // 2
                    p_cy = player.y + player.height // 2
                    for enemy in wave_mgr.enemies:
                        if enemy.is_alive:
                            e_cx = enemy.x + enemy.width // 2
                            e_cy = enemy.y + enemy.height // 2
                            if math.hypot(p_cx - e_cx, p_cy - e_cy) < (player.width // 2 + enemy.width // 2 - 8):
                                crash_dmg = 35 if (enemy.is_captain or enemy.enemy_type == ENEMY_KAMIKAZE) else 25
                                player.take_damage(crash_dmg)
                                text_mgr.add_text(player.x, player.y - 20, "¡CHOQUE!", COLOR_RED)
                                screen_shake.add_trauma(0.55)
                                particle_mgr.spawn_explosion(e_cx, e_cy, count=16)
                                if enemy.enemy_type == ENEMY_KAMIKAZE:
                                    enemy.is_alive = False
                                break

                    # Choque con Mini-Boss o Final Boss
                    if mini_boss and mini_boss.is_alive:
                        mb_cx = mini_boss.x + mini_boss.width // 2
                        mb_cy = mini_boss.y + mini_boss.height // 2
                        if math.hypot(p_cx - mb_cx, p_cy - mb_cy) < (player.width // 2 + mini_boss.width // 3):
                            player.take_damage(40)
                            text_mgr.add_text(player.x, player.y - 20, "¡IMPACTO PESADO!", COLOR_RED)
                            screen_shake.add_trauma(0.65)
                            particle_mgr.spawn_explosion(p_cx, p_cy, count=20)

                    if final_boss and final_boss.is_alive:
                        fb_cx = final_boss.x + final_boss.width // 2
                        fb_cy = final_boss.y + final_boss.height // 2
                        if math.hypot(p_cx - fb_cx, p_cy - fb_cy) < (player.width // 2 + final_boss.width // 3):
                            player.take_damage(50)
                            text_mgr.add_text(player.x, player.y - 20, "¡COLISIÓN TITÁNICA!", COLOR_RED)
                            screen_shake.add_trauma(0.8)
                            particle_mgr.spawn_explosion(p_cx, p_cy, count=24)

        # --- DIBUJADO DE PANTALLAS ---
        render_surf = screen
        render_surf.fill(COLOR_BLACK)
        starfield.draw(render_surf)

        if state_mgr.current_state == STATE_MENU:
            state_mgr.draw_main_menu(render_surf, mouse_pos)

        elif state_mgr.current_state == STATE_SHOP:
            state_mgr.draw_shop_menu(render_surf, player, mouse_pos)

        elif state_mgr.current_state in (STATE_PLAYING, STATE_PAUSED):
            drop_mgr.draw(render_surf)
            wave_mgr.draw(render_surf)
            if mini_boss and mini_boss.is_alive: mini_boss.draw(render_surf, font_small)
            if final_boss and final_boss.is_alive: final_boss.draw(render_surf, font_small)
            weapon_sys.draw(render_surf)
            player.draw(render_surf)
            particle_mgr.draw(render_surf)
            text_mgr.draw(render_surf, font_small)
            
            # HUD Superior
            draw_hud(render_surf, player, weapon_sys, stats['score'], wave_mgr.current_level, sw, font_large, font_small)
            
            # HUD Tactico de Armas Abajo a la Derecha
            draw_weapon_hud_bottom_right(render_surf, player, weapon_sys, state_mgr.shop, sw, sh, font_large, font_small)

            # Alerta de Perdida de Vida (-1 VIDA)
            if now < player.life_lost_alert_until:
                draw_life_lost_alert(render_surf, sw, sh, font_huge)

            # Modal Cinemático de Poderes con Freeze
            if now < power_modal_data["until"] and power_modal_data["type"]:
                draw_powerup_modal(
                    render_surf,
                    power_modal_data["type"],
                    power_modal_data["level"],
                    power_modal_data["synergies"],
                    sw, sh, font_huge, font_large, font_small
                )

            if state_mgr.current_state == STATE_PAUSED:
                state_mgr.draw_pause_menu(render_surf, mouse_pos)

        elif state_mgr.current_state in (STATE_GAME_OVER, STATE_VICTORY):
            is_vic = (state_mgr.current_state == STATE_VICTORY)
            summary_btn_retry, summary_btn_menu = draw_summary_screen(
                render_surf, player, stats, sw, sh, is_vic, mouse_pos, font_huge, font_large, font_small
            )

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()