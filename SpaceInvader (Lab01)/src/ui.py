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
        1: "Aplica quemadura DoT por 1.2s causando dano continuo.",
        2: "Aumenta la duracion a 1.8s (+40% dano igneo).",
        3: "INFIERNO TOTAL: Brasas ardientes por 2.5s y calor extremo."
    },
    POWER_ICE: {
        1: "Aplica 50% de ralentizacion criogenica por 1.0s.",
        2: "Aumenta la ralentizacion al 65% y duracion a 1.5s.",
        3: "CONGELACION ABSOLUTA: Inmoviliza al invasor por 2.0s."
    },
    POWER_SHIELD: {
        1: "Genera 1 carga de Escudo de Plasma protector.",
        2: "Aumenta la capacidad a 2 cargas de escudo.",
        3: "PULSO DEFENSIVO: Al romperse, emite onda que destruye balas."
    },
    POWER_ELECTRO: {
        1: "Cadencia de disparo aumentada un 20%.",
        2: "Cadencia aumentada un 40% y proyectiles con micro-chispas.",
        3: "SOBRECARGA ELECTRICA: Disparo continuo ultra-rapido (+65%)."
    },
    POWER_VOID: {
        1: "Atrae creditos y capsulas a 140px de distancia.",
        2: "Aumenta el radio del campo gravitacional a 220px.",
        3: "AGUJERO NEGRO: Absorbe todos los creditos y municion a 320px."
    },
    POWER_SPEED: {
        1: "Velocidad de movimiento de la nave aumentada (+20%).",
        2: "Velocidad aumentada (+40%) y mayor agilidad de combate.",
        3: "DASH TACTICO: Pulsa [SHIFT] para impulso rapido con inmunidad."
    },
    POWER_HEALTH: {
        1: "Salud maxima aumentada (+15 HP) y reparacion suave.",
        2: "Salud maxima aumentada (+30 HP).",
        3: "NUCLEO TITANICO: +45 HP maximos y autorreparacion."
    },
    POWER_FUEL: {
        1: "Capacidad de Reactor aumentada a 60 Fuel.",
        2: "Capacidad de Reactor aumentada a 100 Fuel.",
        3: "REACTOR SUPREMO: 120 Fuel y recarga pasiva acelerada para [F]."
    }
}

SYNERGY_DESCRIPTIONS = {
    "CHOQUE TERMICO": "El fuego detona a los invasores congelados causando DANO DOBLE.",
    "PLASMA DE TORMENTA": "Las balas disparan rafagas electrizadas y ardientes.",
    "CERO ABSOLUTO": "La armadura congela a los enemigos que se acerquen.",
    "ESCUDO SOBRECARGADO": "El escudo emite descargas electricas a enemigos cercanos.",
    "DASH DE FUEGO": "El Dash [SHIFT] deja una estela de fuego ardiente.",
    "AUTORREPARACION": "La nave se repara sola continuamente fuera de combate."
}

# --- AYUDAS VISUALES PROCEDURALES (CERO EMOJIS, 100% VECTORIALES) ---

def draw_ship_life_icon(surface, cx, cy, size=10, is_active=True):
    """Dibuja una silueta vectorial de caza estelar para representar vidas."""
    pts = [
        (cx, cy - size),
        (cx - int(size * 0.75), cy + size),
        (cx, cy + int(size * 0.4)),
        (cx + int(size * 0.75), cy + size)
    ]
    if is_active:
        pygame.draw.polygon(surface, COLOR_CYAN, pts)
        pygame.draw.polygon(surface, COLOR_WHITE, pts, width=1)
        pygame.draw.circle(surface, COLOR_GOLD, (cx, cy + int(size * 0.2)), 2)
    else:
        pygame.draw.polygon(surface, (45, 52, 68), pts, width=1)


def draw_missile_pip(surface, cx, cy, w=7, h=16, is_active=True):
    """Dibuja un icono estilizado de misil tactico."""
    top_y = cy - h // 2
    bot_y = cy + h // 2
    body_w = w - 2
    
    if is_active:
        nose_pts = [(cx, top_y), (cx - w // 2, top_y + 4), (cx + w // 2, top_y + 4)]
        pygame.draw.polygon(surface, COLOR_WHITE, nose_pts)
        body_rect = pygame.Rect(cx - body_w // 2, top_y + 4, body_w, h - 8)
        pygame.draw.rect(surface, COLOR_RED, body_rect)
        pygame.draw.polygon(surface, COLOR_GOLD, [(cx - w // 2, bot_y), (cx - w // 2 - 2, bot_y), (cx - body_w // 2, bot_y - 4)])
        pygame.draw.polygon(surface, COLOR_GOLD, [(cx + w // 2, bot_y), (cx + w // 2 + 2, bot_y), (cx + body_w // 2, bot_y - 4)])
    else:
        rect = pygame.Rect(cx - w // 2, top_y, w, h)
        pygame.draw.rect(surface, (50, 56, 70), rect, width=1, border_radius=2)


def draw_credit_token(surface, cx, cy, radius=6):
    """Dibuja una insignia hexagonal o circular de credito espacial."""
    pygame.draw.circle(surface, COLOR_GOLD, (cx, cy), radius)
    pygame.draw.circle(surface, (140, 110, 10), (cx, cy), radius - 2)
    pygame.draw.circle(surface, COLOR_GOLD, (cx, cy), 2)


def draw_text(surface, text, font, color, center_pos):
    """Renderiza texto centrado en una posicion (x, y) con sombra sutil."""
    shadow = font.render(text, True, (8, 10, 15))
    surface.blit(shadow, (center_pos[0] - shadow.get_width() // 2 + 1, center_pos[1] - shadow.get_height() // 2 + 1))
    surf = font.render(text, True, color)
    surface.blit(surf, (center_pos[0] - surf.get_width() // 2, center_pos[1] - surf.get_height() // 2))


def draw_pause_overlay(surface, screen_width, screen_height, font_title, font_sub):
    """Dibuja el overlay semitransparente del menu de pausa."""
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill((5, 8, 14, 210))
    surface.blit(overlay, (0, 0))
    
    box_w, box_h = 440, 220
    bx = screen_width // 2 - box_w // 2
    by = screen_height // 2 - box_h // 2 - 30
    rect = pygame.Rect(bx, by, box_w, box_h)
    pygame.draw.rect(surface, (16, 20, 32), rect, border_radius=10)
    pygame.draw.rect(surface, COLOR_CYAN, rect, width=2, border_radius=10)
    
    draw_text(surface, "[ SISTEMA EN PAUSA ]", font_title, COLOR_GOLD, (screen_width // 2, by + 42))
    draw_text(surface, "Pulsa ESC o P para reanudar combate", font_sub, COLOR_WHITE, (screen_width // 2, by + 88))


class Button:
    """Boton interactivo con estados de hover, borde brillante y clic."""
    def __init__(self, x, y, width, height, text, font, base_color=(20, 26, 38), hover_color=(36, 46, 68)):
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
        border_c = COLOR_GOLD if self.is_hovered else (55, 68, 92)
        
        pygame.draw.rect(surface, color, self.rect, border_radius=6)
        pygame.draw.rect(surface, border_c, self.rect, width=2 if self.is_hovered else 1, border_radius=6)
        
        text_c = COLOR_GOLD if self.is_hovered else COLOR_WHITE
        text_surf = self.font.render(self.text, True, text_c)
        surface.blit(text_surf, (
            self.rect.centerx - text_surf.get_width() // 2,
            self.rect.centery - text_surf.get_height() // 2
        ))


# --- HUD PRINCIPAL DE COMBATE ---

def draw_hud(surface, player, weapon_sys, score, wave_num, screen_width, font_large, font_small):
    """Dibuja el HUD superior con diseno limpio y proporciones equilibradas."""
    sw = screen_width
    
    # 1. MODULO SUPERIOR IZQUIERDO: SALUD Y VIDAS
    hud_bg = pygame.Surface((310, 68), pygame.SRCALPHA)
    hud_bg.fill((12, 16, 24, 210))
    surface.blit(hud_bg, (14, 12))
    pygame.draw.rect(surface, (45, 55, 75), (14, 12, 310, 68), width=1, border_radius=6)

    bar_w, bar_h = 160, 12
    bar_x, bar_y = 24, 22
    pygame.draw.rect(surface, (20, 24, 32), (bar_x, bar_y, bar_w, bar_h), border_radius=3)
    fill_hp = int(bar_w * max(0, player.hp / player.max_hp))
    if fill_hp > 0:
        hp_color = COLOR_GREEN if player.hp > player.max_hp * 0.4 else (COLOR_YELLOW if player.hp > player.max_hp * 0.2 else COLOR_RED)
        pygame.draw.rect(surface, hp_color, (bar_x, bar_y, fill_hp, bar_h), border_radius=3)
    pygame.draw.rect(surface, (80, 95, 120), (bar_x, bar_y, bar_w, bar_h), width=1, border_radius=3)

    hp_t = font_small.render(f"HP: {int(player.hp)}/{player.max_hp}", True, COLOR_WHITE)
    surface.blit(hp_t, (bar_x + bar_w + 12, bar_y - 1))

    if player.shield_charges > 0:
        shield_txt = font_small.render(f"ESCUDO: {player.shield_charges}", True, COLOR_CYAN)
        surface.blit(shield_txt, (bar_x + bar_w + 12, bar_y + 14))

    lives_label = font_small.render("VIDAS:", True, (170, 185, 205))
    surface.blit(lives_label, (24, 46))
    for i in range(max(3, player.lives)):
        draw_ship_life_icon(surface, 85 + (i * 22), 52, size=7, is_active=(i < player.lives))

    # 2. MODULO SUPERIOR CENTRAL: SECTOR Y PUNTUACION
    center_w = 240
    cx = sw // 2 - center_w // 2
    center_bg = pygame.Surface((center_w, 60), pygame.SRCALPHA)
    center_bg.fill((12, 16, 24, 210))
    surface.blit(center_bg, (cx, 12))
    pygame.draw.rect(surface, (45, 55, 75), (cx, 12, center_w, 60), width=1, border_radius=6)

    sector_t = font_small.render(f"[ SECTOR {wave_num:02d} ]", True, COLOR_GOLD)
    surface.blit(sector_t, (sw // 2 - sector_t.get_width() // 2, 18))
    
    score_str = f"SCORE: {score:06d}"
    score_t = font_large.render(score_str, True, COLOR_WHITE)
    surface.blit(score_t, (sw // 2 - score_t.get_width() // 2, 38))

    # 3. MODULO SUPERIOR DERECHO: CREDITOS
    coin_w = 175
    coin_x = sw - coin_w - 14
    coin_bg = pygame.Surface((coin_w, 40), pygame.SRCALPHA)
    coin_bg.fill((12, 16, 24, 210))
    surface.blit(coin_bg, (coin_x, 12))
    pygame.draw.rect(surface, (55, 68, 92), (coin_x, 12, coin_w, 40), width=1, border_radius=6)

    draw_credit_token(surface, coin_x + 20, 32, radius=6)
    coins_t = font_large.render(f"{player.coins} CR", True, COLOR_GOLD)
    surface.blit(coins_t, (coin_x + 36, 22))

    # 4. CINTA DE PODERES ACTIVOS (Bajo la barra de salud)
    px, py = 14, 86
    for p_type, lvl in player.powers.items():
        if lvl > 0:
            cfg = POWER_CONFIG[p_type]
            badge_rect = pygame.Rect(px, py, 68, 22)
            pygame.draw.rect(surface, (14, 18, 28), badge_rect, border_radius=4)
            pygame.draw.rect(surface, cfg["color"], badge_rect, width=1, border_radius=4)
            
            p_sym = cfg.get("sym", p_type[:3])
            lvl_str = "I" if lvl == 1 else ("II" if lvl == 2 else "III")
            t = font_small.render(f"{p_sym} {lvl_str}", True, cfg["color"])
            surface.blit(t, (px + (68 - t.get_width()) // 2, py + 4))
            px += 74
            if px > 340:
                px = 14
                py += 26


# --- HUD TACTICO DE ARMAS (ABAJO A LA DERECHA) ---

def draw_weapon_hud_bottom_right(surface, player, weapon_sys, shop_ref, screen_width, screen_height, font_large, font_small):
    """Dibuja la tarjeta tactica del arma activa abajo a la derecha."""
    sw, sh = screen_width, screen_height
    card_w, card_h = 320, 118
    card_x = sw - card_w - 16
    card_y = sh - card_h - 16

    card_rect = pygame.Rect(card_x, card_y, card_w, card_h)
    bg_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
    bg_surf.fill((12, 16, 26, 230))
    surface.blit(bg_surf, (card_x, card_y))
    pygame.draw.rect(surface, (50, 65, 90), card_rect, width=1, border_radius=8)

    w_info = {
        WEAPON_SNIPER: ("SNIPER DE RIEL", COLOR_CYAN, "1"),
        WEAPON_MINIGUN: ("METRALLETA GATLING", COLOR_YELLOW, "2"),
        WEAPON_SPREAD: ("ESCOPETA FLAK", COLOR_ORANGE, "3"),
        WEAPON_MISSILE: ("LANZAMISILES", COLOR_RED, "4"),
        WEAPON_HOMING: ("MICRO-DRONES", COLOR_PURPLE, "5")
    }
    w_name, w_color, w_key = w_info.get(weapon_sys.active_weapon, ("ARMA", COLOR_WHITE, "1"))

    # Selector superior de armas [1] [2] [3] [4] [5]
    sel_x = card_x + 14
    for wid, (_, col, key) in w_info.items():
        is_active = (weapon_sys.active_weapon == wid)
        box_w = 26
        rect = pygame.Rect(sel_x, card_y + 10, box_w, 18)
        if is_active:
            pygame.draw.rect(surface, col, rect, border_radius=3)
            kt = font_small.render(key, True, COLOR_BLACK)
        else:
            pygame.draw.rect(surface, (24, 30, 44), rect, border_radius=3)
            pygame.draw.rect(surface, (60, 72, 95), rect, width=1, border_radius=3)
            kt = font_small.render(key, True, (150, 165, 185))
        surface.blit(kt, (sel_x + (box_w - kt.get_width()) // 2, card_y + 11))
        sel_x += 32

    # Nombre del arma activa
    title_t = font_large.render(w_name, True, w_color)
    surface.blit(title_t, (card_x + 14, card_y + 34))

    # Nivel de mejora en hangar
    upgrades = shop_ref.upgrades if shop_ref else {}
    lvl = upgrades.get(weapon_sys.active_weapon, {}).get("level", 0)
    pips = "".join(["[X]" if i < lvl else "[ ]" for i in range(3)])
    lvl_t = font_small.render(f"MEJORA: {pips} NV.{lvl}", True, COLOR_GOLD if lvl > 0 else (130, 140, 160))
    surface.blit(lvl_t, (card_x + card_w - lvl_t.get_width() - 14, card_y + 38))

    # Municion o Combustible
    if weapon_sys.active_weapon == WEAPON_MISSILE:
        m_label = font_small.render("MUNICION:", True, (180, 195, 215))
        surface.blit(m_label, (card_x + 14, card_y + 64))
        for mi in range(weapon_sys.max_missile_ammo):
            draw_missile_pip(surface, card_x + 95 + (mi * 18), card_y + 70, is_active=(mi < weapon_sys.missile_ammo))
    else:
        fuel_w = 150
        fuel_h = 10
        fuel_y = card_y + 66
        pygame.draw.rect(surface, (25, 30, 42), (card_x + 14, fuel_y, fuel_w, fuel_h), border_radius=2)
        fill_f = int(fuel_w * max(0, player.fuel / player.max_fuel))
        if fill_f > 0:
            pygame.draw.rect(surface, COLOR_CYAN, (card_x + 14, fuel_y, fill_f, fuel_h), border_radius=2)
        pygame.draw.rect(surface, (70, 85, 110), (card_x + 14, fuel_y, fuel_w, fuel_h), width=1, border_radius=2)
        
        f_pct = int((player.fuel / player.max_fuel) * 100)
        f_t = font_small.render(f"REACTOR: {f_pct}% [F: ESPECIAL]", True, COLOR_CYAN)
        surface.blit(f_t, (card_x + fuel_w + 22, card_y + 63))

    # Atajos inferiores
    hint_t = font_small.render("[1-5] Armas  |  [F] Especial  |  [T] Hangar", True, (135, 150, 175))
    surface.blit(hint_t, (card_x + 14, card_y + 92))


# --- MODAL CINEMATICO DE ADQUISICION DE PODER ---

def draw_powerup_modal(surface, power_type, level, new_synergies, screen_width, screen_height, font_huge, font_large, font_small):
    """Banner central de adquisicion de modulo espacial con pausa cinematica."""
    sw, sh = screen_width, screen_height
    
    overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 185))
    surface.blit(overlay, (0, 0))

    cfg = POWER_CONFIG.get(power_type, {"name": power_type, "color": COLOR_CYAN, "sym": "MOD"})
    box_w = 540
    box_h = 230 if not new_synergies else 295
    box_x = sw // 2 - box_w // 2
    box_y = sh // 2 - box_h // 2

    modal_rect = pygame.Rect(box_x, box_y, box_w, box_h)
    pygame.draw.rect(surface, (14, 18, 28), modal_rect, border_radius=10)
    pygame.draw.rect(surface, cfg["color"], modal_rect, width=2, border_radius=10)

    # Encabezado tactico
    tag_t = font_small.render("// MODULO DE MEJORA DETECTADO //", True, (160, 175, 200))
    surface.blit(tag_t, (sw // 2 - tag_t.get_width() // 2, box_y + 16))

    title_str = f"MODULO: {cfg['name'].upper()} [NIVEL {level}]"
    title_t = font_large.render(title_str, True, cfg["color"])
    surface.blit(title_t, (sw // 2 - title_t.get_width() // 2, box_y + 38))

    # Segmentos de nivel [NV 1] [NV 2] [NV 3]
    seg_w = 90
    seg_total_w = 3 * seg_w + 2 * 10
    seg_start_x = sw // 2 - seg_total_w // 2
    for i in range(1, 4):
        bx = seg_start_x + (i - 1) * (seg_w + 10)
        by = box_y + 72
        seg_rect = pygame.Rect(bx, by, seg_w, 20)
        if i < level:
            pygame.draw.rect(surface, (35, 45, 60), seg_rect, border_radius=3)
            st = font_small.render(f"NV. {i} OK", True, (160, 175, 195))
        elif i == level:
            pygame.draw.rect(surface, cfg["color"], seg_rect, border_radius=3)
            st = font_small.render(f"NV. {i} ACTIVO", True, COLOR_BLACK)
        else:
            pygame.draw.rect(surface, (20, 24, 34), seg_rect, border_radius=3)
            pygame.draw.rect(surface, (50, 60, 80), seg_rect, width=1, border_radius=3)
            st = font_small.render(f"NV. {i}", True, (100, 110, 130))
        surface.blit(st, (bx + (seg_w - st.get_width()) // 2, by + 3))

    # Linea divisoria
    pygame.draw.line(surface, (45, 55, 75), (box_x + 30, box_y + 106), (box_x + box_w - 30, box_y + 106), 1)

    # Descripcion
    desc = POWER_DESCRIPTIONS.get(power_type, {}).get(level, "Rendimiento aumentado.")
    desc_t = font_small.render(desc, True, COLOR_WHITE)
    surface.blit(desc_t, (sw // 2 - desc_t.get_width() // 2, box_y + 124))

    # Sinergia
    if new_synergies:
        syn_name = new_synergies[0]
        syn_desc = SYNERGY_DESCRIPTIONS.get(syn_name, "Efecto combinado legendario activado.")
        
        syn_box = pygame.Rect(box_x + 24, box_y + 155, box_w - 48, 62)
        pygame.draw.rect(surface, (32, 28, 12), syn_box, border_radius=6)
        pygame.draw.rect(surface, COLOR_GOLD, syn_box, width=1, border_radius=6)

        syn_title = font_small.render(f"// NUEVA SINERGIA: {syn_name} //", True, COLOR_GOLD)
        surface.blit(syn_title, (sw // 2 - syn_title.get_width() // 2, box_y + 163))
        
        syn_dt = font_small.render(syn_desc, True, (240, 225, 180))
        surface.blit(syn_dt, (sw // 2 - syn_dt.get_width() // 2, box_y + 188))

    resume_t = font_small.render("Reanudando combate espacial...", True, (130, 145, 170))
    surface.blit(resume_t, (sw // 2 - resume_t.get_width() // 2, box_y + box_h - 24))


# --- ALERTA DE PERDIDA DE VIDA ---

def draw_life_lost_alert(surface, screen_width, screen_height, font_huge):
    """Dibuja alerta central de perdida de vida e impacto critico sin emojis."""
    sw, sh = screen_width, screen_height
    
    # Vineta perimetral roja
    vignette = pygame.Surface((sw, sh), pygame.SRCALPHA)
    pygame.draw.rect(vignette, (200, 20, 20, 65), (0, 0, sw, sh), width=18)
    surface.blit(vignette, (0, 0))

    # Cuadro de alerta central
    bw, bh = 380, 85
    bx = sw // 2 - bw // 2
    by = sh // 2 - bh // 2
    alert_rect = pygame.Rect(bx, by, bw, bh)
    pygame.draw.rect(surface, (18, 12, 14), alert_rect, border_radius=8)
    pygame.draw.rect(surface, COLOR_RED, alert_rect, width=2, border_radius=8)

    draw_text(surface, "-1 VIDA PERDIDA", font_huge, COLOR_RED, (sw // 2, by + 30))
    
    font_sub = pygame.font.Font('freesansbold.ttf', 13)
    draw_text(surface, "INMUNIDAD TEMPORAL ACTIVADA", font_sub, (200, 215, 235), (sw // 2, by + 60))


# --- PANTALLA DE RESUMEN FINAL ---

def draw_summary_screen(surface, player, stats, screen_width, screen_height, is_victory, mouse_pos, font_huge, font_large, font_small):
    """Pantalla de reporte de mision final con diseno balanceado y limpio."""
    sw, sh = screen_width, screen_height

    bg_overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
    bg_overlay.fill((6, 8, 14, 245))
    surface.blit(bg_overlay, (0, 0))

    title_text = "[ VICTORIA COSMICA - MISION COMPLETADA ]" if is_victory else "[ TRANSMISION FINAL - NAVE DESTRUIDA ]"
    title_color = COLOR_GOLD if is_victory else COLOR_RED
    t_surf = font_huge.render(title_text, True, title_color)
    surface.blit(t_surf, (sw // 2 - t_surf.get_width() // 2, 36))

    sub_t = font_small.render(f"REGISTRO TACTICO // SECTOR FINAL ALCANZADO: {stats.get('sector', 1)} / 12", True, (160, 175, 200))
    surface.blit(sub_t, (sw // 2 - sub_t.get_width() // 2, 85))

    card_w = min(540, (sw - 100) // 2)
    card_h = 240
    top_y = 120

    # TARJETA IZQUIERDA: ESTADISTICAS DE COMBATE
    left_rect = pygame.Rect(sw // 2 - card_w - 15, top_y, card_w, card_h)
    pygame.draw.rect(surface, (14, 18, 28), left_rect, border_radius=8)
    pygame.draw.rect(surface, (45, 56, 78), left_rect, width=1, border_radius=8)

    lt_title = font_large.render("ESTADISTICAS DE COMBATE", True, COLOR_CYAN)
    surface.blit(lt_title, (left_rect.x + 22, left_rect.y + 18))

    mins = stats.get('time_sec', 0) // 60
    secs = stats.get('time_sec', 0) % 60
    time_str = f"{mins:02d}:{secs:02d}"

    stat_rows = [
        ("Tiempo de Incursion:", time_str),
        ("Invasores Abatidos:", f"{stats.get('kills', 0)}"),
        ("Creditos Obtenidos:", f"{player.coins} CR"),
        ("Puntuacion Final:", f"{stats.get('score', 0)} PTS")
    ]
    sy = left_rect.y + 60
    for label, val in stat_rows:
        lbl_t = font_small.render(label, True, (165, 180, 200))
        val_t = font_small.render(val, True, COLOR_WHITE)
        surface.blit(lbl_t, (left_rect.x + 24, sy))
        surface.blit(val_t, (left_rect.x + card_w - val_t.get_width() - 24, sy))
        pygame.draw.line(surface, (28, 34, 48), (left_rect.x + 24, sy + 28), (left_rect.x + card_w - 24, sy + 28), 1)
        sy += 40

    # TARJETA DERECHA: MODULOS Y ARSENAL FINAL
    right_rect = pygame.Rect(sw // 2 + 15, top_y, card_w, card_h)
    pygame.draw.rect(surface, (14, 18, 28), right_rect, border_radius=8)
    pygame.draw.rect(surface, (45, 56, 78), right_rect, width=1, border_radius=8)

    rt_title = font_large.render("MODULOS ADQUIRIDOS", True, COLOR_GOLD)
    surface.blit(rt_title, (right_rect.x + 22, right_rect.y + 18))

    gx, gy = right_rect.x + 22, right_rect.y + 58
    col_w = (card_w - 44) // 2
    row_h = 38
    idx = 0
    for p_type in [POWER_FIRE, POWER_ICE, POWER_SHIELD, POWER_ELECTRO, POWER_VOID, POWER_SPEED, POWER_HEALTH, POWER_FUEL]:
        lvl = player.powers.get(p_type, 0)
        cfg = POWER_CONFIG[p_type]
        
        slot_x = gx + (idx % 2) * col_w
        slot_y = gy + (idx // 2) * row_h
        
        badge_rect = pygame.Rect(slot_x, slot_y, col_w - 10, 30)
        pygame.draw.rect(surface, (20, 25, 36), badge_rect, border_radius=4)
        border_c = cfg["color"] if lvl > 0 else (40, 48, 62)
        pygame.draw.rect(surface, border_c, badge_rect, width=1, border_radius=4)
        
        p_tag = cfg.get("sym", p_type[:3])
        status_txt = f"NV.{lvl}" if lvl > 0 else "--"
        p_txt = font_small.render(f"[{p_tag}] {cfg['name']}", True, cfg["color"] if lvl > 0 else (110, 120, 135))
        st_txt = font_small.render(status_txt, True, COLOR_WHITE if lvl > 0 else (75, 85, 100))
        surface.blit(p_txt, (slot_x + 8, slot_y + 7))
        surface.blit(st_txt, (slot_x + col_w - 10 - st_txt.get_width() - 8, slot_y + 7))
        idx += 1

    # TARJETA INFERIOR: SINERGIAS ACTIVADAS
    bot_w = card_w * 2 + 30
    bot_h = 92
    bot_y = top_y + card_h + 16
    bot_rect = pygame.Rect(sw // 2 - bot_w // 2, bot_y, bot_w, bot_h)
    pygame.draw.rect(surface, (14, 18, 28), bot_rect, border_radius=8)
    pygame.draw.rect(surface, COLOR_GOLD if player.synergies else (45, 56, 78), bot_rect, width=1, border_radius=8)

    syn_header = font_small.render("// SINERGIAS TACTICAS COMBINADAS //", True, COLOR_GOLD if player.synergies else (140, 150, 170))
    surface.blit(syn_header, (bot_rect.x + 22, bot_rect.y + 14))

    if player.synergies:
        syn_x = bot_rect.x + 22
        syn_y = bot_rect.y + 42
        for syn in player.synergies:
            badge = pygame.Rect(syn_x, syn_y, 220, 28)
            pygame.draw.rect(surface, (36, 30, 12), badge, border_radius=4)
            pygame.draw.rect(surface, COLOR_GOLD, badge, width=1, border_radius=4)
            t = font_small.render(f"[+] {syn}", True, COLOR_GOLD)
            surface.blit(t, (syn_x + 10, syn_y + 6))
            syn_x += 232
    else:
        no_syn = font_small.render("Ninguna sinergia combinada en esta incursion.", True, (120, 130, 150))
        surface.blit(no_syn, (bot_rect.x + 22, bot_rect.y + 46))

    # BOTONES INFERIORES
    btn_w, btn_h = 240, 46
    btn_y = bot_y + bot_h + 20
    btn_retry = Button(sw // 2 - btn_w - 15, btn_y, btn_w, btn_h, "REINTENTAR RUN (R)", font_small)
    btn_menu = Button(sw // 2 + 15, btn_y, btn_w, btn_h, "MENU PRINCIPAL (ESC)", font_small)

    btn_retry.check_hover(mouse_pos)
    btn_menu.check_hover(mouse_pos)

    btn_retry.draw(surface)
    btn_menu.draw(surface)

    return btn_retry, btn_menu

# Alias para compatibilidad con llamadas existentes
draw_run_summary = draw_summary_screen
