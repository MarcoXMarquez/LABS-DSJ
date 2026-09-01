# src/config.py
import pygame

# --- CONFIGURACIÓN DE PANTALLA (Se ajusta a tu monitor al iniciar) ---
FPS = 60
GAME_TITLE = "Space Invaders: Rogue Legacy"

# --- COLORES (RGB) ---
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_GREEN = (0, 255, 0)
COLOR_RED = (255, 60, 60)
COLOR_BLUE = (80, 160, 255)
COLOR_YELLOW = (255, 220, 0)
COLOR_PURPLE = (180, 70, 240)
COLOR_ORANGE = (255, 140, 0)
COLOR_CYAN = (0, 230, 230)
COLOR_GOLD = (255, 215, 0)
COLOR_DARK_GRAY = (25, 25, 30)
COLOR_CARD_BG = (35, 40, 55)

# --- ESTADOS DEL JUEGO ---
STATE_MENU = "MENU"
STATE_PLAYING = "PLAYING"
STATE_PAUSED = "PAUSED"
STATE_GAME_OVER = "GAME_OVER"
STATE_VICTORY = "VICTORY"

# --- BALANCE DEL JUGADOR ---
PLAYER_SPEED = 7
PLAYER_MAX_HP = 100
PLAYER_START_LIVES = 3
PLAYER_INVULNERABLE_TIME = 1200  # ms de inmunidad al recibir daño

# --- BALANCE DE DISPAROS BASE ---
BULLET_SPEED = 12
FIRE_RATE_DELAY = 180  # ms entre disparos

# --- BALANCE DE DROPS Y HABILIDADES ---
DROP_CHANCE = 0.40      # 40% de probabilidad de soltar burbuja
DROP_SPEED = 2.5        # Velocidad de flotación de la burbuja hacia abajo
MAX_POWER_LEVEL = 3     # Nivel máximo por poder

# Identificadores de habilidades
POWER_FIRE = "FIRE"
POWER_ICE = "ICE"
POWER_SPREAD = "SPREAD"
POWER_EXPLOSIVE = "EXPLOSIVE"
POWER_SHIELD = "SHIELD"
POWER_SPEED_BOOST = "SPEED"