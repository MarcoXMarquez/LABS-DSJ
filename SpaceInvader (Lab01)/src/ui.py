# src/ui.py
import pygame
import math
from src.config import (
    COLOR_WHITE, COLOR_GOLD, COLOR_RED, COLOR_CYAN,
    COLOR_CARD_BG, COLOR_CARD_BORDER, COLOR_GREEN,
    COLOR_YELLOW, COLOR_BLUE, COLOR_PURPLE, COLOR_BLACK,
    COLOR_ORANGE
)
from src.drops import (
    POWER_FIRE, POWER_ICE, POWER_SHIELD, POWER_ELECTRO,
    POWER_VOID, POWER_SPEED, POWER_HEALTH, POWER_FUEL, POWER_CONFIG
)
from src.weapons import (
    WEAPON_SNIPER, WEAPON_MINIGUN, WEAPON_SPREAD, WEAPON_MISSILE, WEAPON_HOMING
)

POWER_DESCRIPTIONS = {
    POWER_FIRE: {
        1: "Aplica quemadura DoT por 1.2s causando daño continuo.",
        2: "Aumenta la duración de la quemadura a 1.8s (+40% daño ígneo).",
        3: "¡INFIERNO TOTAL! Brasas ardientes por 2.5s y área de calor."
    },
    POWER_ICE: {
        1: "Aplica 50% de ralentización criogénica por 1.0s.",
        2: "Aumenta la ralentización al 65% y duración a 1.5s.",
        3: "¡CONGELACIÓN ABSOLUTA! Inmoviliza al invasor por 2.0s."
    },
    POWER_SHIELD: {
        1: "Genera 1 carga de Escudo de Plasma protector.",
        2: "Aumenta la capacidad a 2 cargas de escudo.",
        3: "¡PULSO DEFENSIVO! Al romperse el escudo, emite una onda que destruye balas."
    },
    POWER_ELECTRO: {
        1: "Cadencia de disparo aumentada un 20%.",
        2: "Cadencia aumentada un 40% y proyectiles con micro-chispas.",
        3: "¡SOBRECARGA ELÉCTRICA! Disparo continuo ultra-rápido (+65%)."
    },
    POWER_VOID: {
        1: "Atrae monedas y cápsulas a 140px de distancia.",
        2: "Aumenta el radio del campo gravitacional a 220px.",
        3: "¡AGUJERO NEGRO! Absorbe todas las monedas y munición a 320px."
    },
    POWER_SPEED: {
        1: "Velocidad de movimiento de la nave aumentada (+20%).",
        2: "Velocidad aumentada (+40%) y mayor agilidad.",
        3: "¡DASH TÁCTICO! Pulsa [SHIFT] para un impulso rápido con invulnerabilidad."
    },
    POWER_HEALTH: {
        1: "Salud máxima aumentada (+15 HP) y regeneración suave fuera de combate.",
        2: "Salud máxima aumentada (+30 HP).",
        3: "¡NÚCLEO TITÁNICO! +45 HP máximos y autorreparación."
    },
    POWER_FUEL: {
        1: "Capacidad de Combustible aumentada a 60 Fuel.",
        2: "Capacidad de Combustible aumentada a 100 Fuel.",
        3: "¡REACTOR SUPREMO! 120 Fuel y recarga pasiva acelerada para [F]."
    }
}

SYNERGY_DESCRIPTIONS = {
    "CHOQUE TERMICO": "El fuego detona a los enemigos congelados causando DAÑO DOBLE.",
    "PLASMA DE TORMENTA": "Las balas disparan ráfagas electrizadas y ardientes.",
    "CERO ABSOLUTO": "La armadura congela a los enemigos que se acerquen.",
    "ESCUDO SOBRECARGADO": "El escudo emite descargas eléctricas a enemigos cercanos.",
    "DASH DE FUEGO": "El Dash [SHIFT] deja una estela de fuego ardiente.",
    "AUTORREPARACION": "La nave se repara sola continuamente cuando no recibe daño."
}

def draw_text(surface, text, font, color, center_pos):
    """Renderiza texto centrado en una posición (x, y)."""
    surf = font.render(text, True, color)
    surface.blit(surf, (center_pos[0] - surf.get_width() // 2, center_pos[1] - surf.get_height() // 2))

def draw_pause_overlay(surface, screen_width, screen_height, font_title, font_sub):
    """Dibuja el overlay semitransparente del menú de pausa."""
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))
    draw_text(surface, "JUEGO EN PAUSA", font_title, COLOR_GOLD, (screen_width // 2, screen_height // 2 - 130))
    draw_text(surface, "Pulsa ESC o P para continuar", font_sub, COLOR_WHITE, (screen_width // 2, screen_height // 2 - 80))

class Button:
    """Botón interactivo con estados de hover y clic."""
    def __init__(self, x, y, width, height, text, font, base_color=COLOR_CARD_BG, hover_color=(45, 55, 75)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.base_color = base_color
        self.hover_color = hover_color
        self.is_hovered = False

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered

    def is_clicked(self, mouse_pos, event):
        return self.check_hover(mouse_pos) and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.base_color
        border_c = COLOR_GOLD if self.is_hovered else COLOR_CARD_BORDER
        
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, border_c, self.rect, width=2, border_radius=8)
        
        text_surf = self.font.render(self.text, True, COLOR_GOLD if self.is_hovered else COLOR_WHITE)
        surface.blit(text_surf, (
            self.rect.centerx - text_surf.get_width() // 2,
            self.rect.centery - text_surf.get_height() // 2
        ))


def draw_hud(surface, player, weapon_sys, score, wave_num, screen_width, font_large, font_small):
    """Dibuja el HUD superior compacto y elegante."""
    sw = screen_width
    
    # 1. Barra de Vida Superior Izquierda
    hp_w, hp_h = 200, 16
    pygame.draw.rect(surface, (25, 25, 30), (20, 20, hp_w, hp_h), border_radius=4)
    fill_hp = int(hp_w * max(0, player.hp / player.max_hp))
    if fill_hp > 0:
        pygame.draw.rect(surface, COLOR_GREEN if player.hp > player.max_hp * 0.35 else COLOR_RED, (20, 20, fill_hp, hp_h), border_radius=4)
    pygame.draw.rect(surface, COLOR_WHITE, (20, 20, hp_w, hp_h), width=1, border_radius=4)
    
    hp_t = font_small.render(f"HP: {int(player.hp)}/{player.max_hp}", True, COLOR_WHITE)
    surface.blit(hp_t, (230, 20))

    # 2. Vidas
    lives_t = font_small.render(f"VIDAS: {'❤️ ' * player.lives}", True, COLOR_RED)
    surface.blit(lives_t, (20, 44))

    # 3. Nivel y Puntuación (Centro)
    lvl_t = font_large.render(f"SECTOR {wave_num}", True, COLOR_GOLD)
    surface.blit(lvl_t, (sw // 2 - lvl_t.get_width() // 2, 14))
    
    score_t = font_small.render(f"PTS: {score}", True, COLOR_WHITE)
    surface.blit(score_t, (sw // 2 - score_t.get_width() // 2, 44))

    # 4. Monedas (Superior Derecha)
    coins_t = font_small.render(f"🪙 {player.coins} CRÉDITOS", True, COLOR_GOLD)
    surface.blit(coins_t, (sw - coins_t.get_width() - 25, 20))

    # 5. Indicadores de Poderes Activos
    px, py = 20, 75
    for p_type, lvl in player.powers.items():
        if lvl > 0:
            cfg = POWER_CONFIG[p_type]
            badge_rect = pygame.Rect(px, py, 75, 22)
            pygame.draw.rect(surface, (25, 28, 40), badge_rect, border_radius=4)
            pygame.draw.rect(surface, cfg["color"], badge_rect, width=1, border_radius=4)
            t = font_small.render(f"{cfg['symbol']} Lv.{lvl}", True, cfg["color"])
            surface.blit(t, (px + 4, py + 2))
            px += 82
            if px > 360:
                px = 20
                py += 26


def draw_weapon_hud_bottom_right(surface, player, weapon_sys, shop_ref, screen_width, screen_height, font_large, font_small):
    """Dibuja la tarjeta táctica ampliada del arma activa abajo a la derecha."""
    sw, sh = screen_width, screen_height
    card_w, card_h = 320, 115
    card_x = sw - card_w - 20
    card_y = sh - card_h - 18

    card_rect = pygame.Rect(card_x, card_y, card_w, card_h)
    bg_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
    bg_surf.fill((16, 20, 32, 225))
    surface.blit(bg_surf, (card_x, card_y))
    pygame.draw.rect(surface, COLOR_CYAN, card_rect, width=2, border_radius=8)

    w_info = {
        WEAPON_SNIPER: ("[1] SNIPER DE RIEL", COLOR_CYAN),
        WEAPON_MINIGUN: ("[2] METRALLETA GATLING", COLOR_YELLOW),
        WEAPON_SPREAD: ("[3] ESCOPETA EN ABANICO", COLOR_ORANGE),
        WEAPON_MISSILE: ("[4] LANZAMISILES PESADO", COLOR_RED),
        WEAPON_HOMING: ("[5] MICRO-DRONES RASTREO", COLOR_PURPLE)
    }
    w_name, w_color = w_info.get(weapon_sys.active_weapon, ("ARMA DESCONOCIDA", COLOR_WHITE))

    title_t = font_large.render(w_name, True, w_color)
    surface.blit(title_t, (card_x + 14, card_y + 10))

    upgrades = shop_ref.upgrades if shop_ref else {}
    lvl = upgrades.get(weapon_sys.active_weapon, {}).get("level", 0)
    lvl_t = font_small.render(f"✦ MEJORA HANGAR: NV. {lvl} / 3 ✦", True, COLOR_GOLD if lvl > 0 else (130, 130, 150))
    surface.blit(lvl_t, (card_x + 14, card_y + 36))

    if weapon_sys.active_weapon == WEAPON_MISSILE:
        missile_icons = "🚀 " * weapon_sys.missile_ammo + "⚪ " * (weapon_sys.max_missile_ammo - weapon_sys.missile_ammo)
        m_t = font_small.render(f"MISILES: {missile_icons}", True, COLOR_RED)
        surface.blit(m_t, (card_x + 14, card_y + 60))
    else:
        fuel_w = 160
        fuel_h = 10
        pygame.draw.rect(surface, (30, 30, 40), (card_x + 14, card_y + 65, fuel_w, fuel_h), border_radius=3)
        fill_f = int(fuel_w * max(0, player.fuel / player.max_fuel))
        if fill_f > 0:
            pygame.draw.rect(surface, COLOR_CYAN, (card_x + 14, card_y + 65, fill_f, fuel_h), border_radius=3)
        pygame.draw.rect(surface, COLOR_WHITE, (card_x + 14, card_y + 65, fuel_w, fuel_h), width=1, border_radius=3)
        f_t = font_small.render(f"FUEL: {int(player.fuel)} [F: ESPECIAL]", True, COLOR_CYAN)
        surface.blit(f_t, (card_x + fuel_w + 22, card_y + 62))

    hint_t = font_small.render("[1-5] Cambiar Arma  |  [T] Tienda", True, (160, 170, 190))
    surface.blit(hint_t, (card_x + 14, card_y + 88))


def draw_powerup_modal(surface, power_type, level, new_synergies, screen_width, screen_height, font_huge, font_large, font_small):
    """Banner central cinemático con pausa al recoger una burbuja de poder."""
    sw, sh = screen_width, screen_height
    
    overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, 0))

    cfg = POWER_CONFIG.get(power_type, {"name": power_type, "color": COLOR_CYAN, "symbol": "★"})
    box_w, box_h = 580, 240 if not new_synergies else 310
    box_x = sw // 2 - box_w // 2
    box_y = sh // 2 - box_h // 2

    modal_rect = pygame.Rect(box_x, box_y, box_w, box_h)
    pygame.draw.rect(surface, (18, 22, 34), modal_rect, border_radius=14)
    pygame.draw.rect(surface, cfg["color"], modal_rect, width=3, border_radius=14)

    title_str = f"{cfg['symbol']} ¡{cfg['name'].upper()} — NIVEL {level}! {cfg['symbol']}"
    title_t = font_huge.render(title_str, True, cfg["color"])
    surface.blit(title_t, (sw // 2 - title_t.get_width() // 2, box_y + 22))

    orbs_str = "PROGRESIÓN: " + ("● " * level) + ("○ " * (3 - level))
    orbs_t = font_small.render(orbs_str, True, COLOR_GOLD)
    surface.blit(orbs_t, (sw // 2 - orbs_t.get_width() // 2, box_y + 68))

    pygame.draw.line(surface, (60, 70, 95), (box_x + 30, box_y + 95), (box_x + box_w - 30, box_y + 95), 1)

    desc = POWER_DESCRIPTIONS.get(power_type, {}).get(level, "Poder aumentado.")
    desc_t = font_large.render(desc, True, COLOR_WHITE)
    surface.blit(desc_t, (sw // 2 - desc_t.get_width() // 2, box_y + 115))

    if new_synergies:
        syn_name = new_synergies[0]
        syn_desc = SYNERGY_DESCRIPTIONS.get(syn_name, "¡Efecto combinado legendario!")
        
        syn_box = pygame.Rect(box_x + 25, box_y + 160, box_w - 50, 70)
        pygame.draw.rect(surface, (40, 32, 10), syn_box, border_radius=8)
        pygame.draw.rect(surface, COLOR_GOLD, syn_box, width=2, border_radius=8)

        syn_title = font_small.render(f"✨ ¡NUEVA SINERGIA: {syn_name}! ✨", True, COLOR_GOLD)
        surface.blit(syn_title, (sw // 2 - syn_title.get_width() // 2, box_y + 168))
        
        syn_dt = font_small.render(syn_desc, True, (255, 230, 160))
        surface.blit(syn_dt, (sw // 2 - syn_dt.get_width() // 2, box_y + 195))

    resume_t = font_small.render("Continuando vuelo espacial...", True, (160, 170, 190))
    surface.blit(resume_t, (sw // 2 - resume_t.get_width() // 2, box_y + box_h - 28))


def draw_life_lost_alert(surface, screen_width, screen_height, font_huge):
    """Dibuja alerta central de -1 VIDA y viñeta roja."""
    sw, sh = screen_width, screen_height
    
    vignette = pygame.Surface((sw, sh), pygame.SRCALPHA)
    pygame.draw.rect(vignette, (220, 20, 20, 70), (0, 0, sw, sh), width=18)
    surface.blit(vignette, (0, 0))

    shadow = font_huge.render("-1 VIDA 💔", True, (10, 10, 10))
    surface.blit(shadow, (sw // 2 - shadow.get_width() // 2 + 3, sh // 2 - 40 + 3))
    
    txt = font_huge.render("-1 VIDA 💔", True, COLOR_RED)
    surface.blit(txt, (sw // 2 - txt.get_width() // 2, sh // 2 - 40))


def draw_summary_screen(surface, player, stats, screen_width, screen_height, is_victory, mouse_pos, font_huge, font_large, font_small):
    """Rediseño total de la pantalla de resumen estilo Hades sin solapamientos."""
    sw, sh = screen_width, screen_height

    bg_overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
    bg_overlay.fill((8, 10, 16, 245))
    surface.blit(bg_overlay, (0, 0))

    title_text = "🏆 ¡VICTORIA CÓSMICA!" if is_victory else "☠️ NAVE DESTRUIDA"
    title_color = COLOR_GOLD if is_victory else COLOR_RED
    t_surf = font_huge.render(title_text, True, title_color)
    surface.blit(t_surf, (sw // 2 - t_surf.get_width() // 2, 40))

    sub_t = font_small.render(f"REPORTE DE BATALLA — SECTOR {stats.get('sector', 1)} / 12 ALCANZADO", True, (180, 190, 210))
    surface.blit(sub_t, (sw // 2 - sub_t.get_width() // 2, 95))

    card_w = (sw - 120) // 2
    card_h = 240
    top_y = 135

    # TARJETA IZQUIERDA: RENDIMIENTO
    left_rect = pygame.Rect(45, top_y, card_w, card_h)
    pygame.draw.rect(surface, (18, 22, 32), left_rect, border_radius=10)
    pygame.draw.rect(surface, COLOR_CARD_BORDER, left_rect, width=2, border_radius=10)

    lt_title = font_large.render("ESTADÍSTICAS DE COMBATE", True, COLOR_CYAN)
    surface.blit(lt_title, (left_rect.x + 20, left_rect.y + 16))

    mins = stats.get('time_sec', 0) // 60
    secs = stats.get('time_sec', 0) % 60
    time_str = f"{mins:02d}:{secs:02d}"

    stat_rows = [
        ("⏱️ Tiempo de Vuelo:", time_str),
        ("👾 Invasores Abatidos:", f"{stats.get('kills', 0)}"),
        ("🪙 Créditos Obtenidos:", f"{player.coins} 🪙"),
        ("⭐ Puntuación Total:", f"{stats.get('score', 0)} PTS")
    ]
    sy = left_rect.y + 58
    for label, val in stat_rows:
        lbl_t = font_small.render(label, True, (170, 180, 200))
        val_t = font_small.render(val, True, COLOR_WHITE)
        surface.blit(lbl_t, (left_rect.x + 24, sy))
        surface.blit(val_t, (left_rect.x + card_w - val_t.get_width() - 24, sy))
        sy += 38

    # TARJETA DERECHA: BUILD FINAL DE PODERES
    right_rect = pygame.Rect(sw - card_w - 45, top_y, card_w, card_h)
    pygame.draw.rect(surface, (18, 22, 32), right_rect, border_radius=10)
    pygame.draw.rect(surface, COLOR_CARD_BORDER, right_rect, width=2, border_radius=10)

    rt_title = font_large.render("BUILD FINAL DE PODERES", True, COLOR_GOLD)
    surface.blit(rt_title, (right_rect.x + 20, right_rect.y + 16))

    gx, gy = right_rect.x + 20, right_rect.y + 58
    col_w = (card_w - 50) // 2
    row_h = 38
    idx = 0
    for p_type in [POWER_FIRE, POWER_ICE, POWER_SHIELD, POWER_ELECTRO, POWER_VOID, POWER_SPEED, POWER_HEALTH, POWER_FUEL]:
        lvl = player.powers.get(p_type, 0)
        cfg = POWER_CONFIG[p_type]
        
        slot_x = gx + (idx % 2) * col_w
        slot_y = gy + (idx // 2) * row_h
        
        badge_rect = pygame.Rect(slot_x, slot_y, col_w - 12, 30)
        pygame.draw.rect(surface, (28, 32, 46), badge_rect, border_radius=6)
        border_c = cfg["color"] if lvl > 0 else (50, 55, 70)
        pygame.draw.rect(surface, border_c, badge_rect, width=1, border_radius=6)
        
        p_txt = font_small.render(f"{cfg['symbol']} {cfg['name']} Lv.{lvl}", True, cfg["color"] if lvl > 0 else (110, 115, 130))
        surface.blit(p_txt, (slot_x + 8, slot_y + 6))
        idx += 1

    # TARJETA INFERIOR: SINERGIAS ACTIVAS
    bot_w = sw - 90
    bot_h = 100
    bot_y = top_y + card_h + 18
    bot_rect = pygame.Rect(45, bot_y, bot_w, bot_h)
    pygame.draw.rect(surface, (18, 22, 32), bot_rect, border_radius=10)
    pygame.draw.rect(surface, COLOR_GOLD if player.synergies else COLOR_CARD_BORDER, bot_rect, width=2, border_radius=10)

    syn_header = font_small.render("✨ SINERGIAS LEGENDARIAS ACTIVADAS:", True, COLOR_GOLD)
    surface.blit(syn_header, (bot_rect.x + 20, bot_rect.y + 12))

    if player.synergies:
        syn_x = bot_rect.x + 20
        syn_y = bot_rect.y + 40
        for syn in player.synergies:
            badge = pygame.Rect(syn_x, syn_y, 220, 32)
            pygame.draw.rect(surface, (45, 38, 15), badge, border_radius=6)
            pygame.draw.rect(surface, COLOR_GOLD, badge, width=1, border_radius=6)
            t = font_small.render(f"★ {syn}", True, COLOR_GOLD)
            surface.blit(t, (syn_x + 10, syn_y + 7))
            syn_x += 235
    else:
        no_syn = font_small.render("Ninguna sinergia desbloqueada en esta incursión.", True, (130, 140, 160))
        surface.blit(no_syn, (bot_rect.x + 20, bot_rect.y + 45))

    # BOTONES INFERIORES
    btn_w, btn_h = 240, 48
    btn_retry = Button(sw // 2 - btn_w - 20, bot_y + bot_h + 20, btn_w, btn_h, "REINTENTAR RUN (R)", font_small)
    btn_menu = Button(sw // 2 + 20, bot_y + bot_h + 20, btn_w, btn_h, "VOLVER AL MENÚ (ESC)", font_small)

    btn_retry.check_hover(mouse_pos)
    btn_menu.check_hover(mouse_pos)

    btn_retry.draw(surface)
    btn_menu.draw(surface)

    return btn_retry, btn_menu

# Alias para compatibilidad
draw_run_summary = draw_summary_screen