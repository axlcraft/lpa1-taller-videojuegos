"""
Configuración y constantes del juego.
Centraliza todos los valores configurables para facilitar su modificación.
"""

# Configuración de pantalla
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
FPS = 60

# Tamaños de entidades (radios)
PLAYER_RADIUS = 16
ENEMY_RADIUS = 14
PROJECTILE_RADIUS = 4
TRAP_RADIUS = 12
TREASURE_RADIUS = 10

# Sistema de experiencia
XP_PER_KILL = 40
XP_PER_TREASURE_VALUE = 0.1  # XP gain = value * this factor

# Sistema de niveles
MAX_LEVELS = 18  # Número máximo de niveles (extendido de 10 a 18)

# Victoria por puntaje
VICTORY_SCORE_THRESHOLD = 5000  # Puntaje necesario para ganar
ENEMIES_PER_LEVEL = [6, 8, 10, 12, 15, 18, 20, 22, 25, 30,   # Niveles 1-10 (originales)
                    35, 40, 45, 50, 60, 70, 85, 100]         # Niveles 11-18 (nuevos)
TREASURES_PER_LEVEL = [5, 6, 7, 8, 10, 12, 14, 16, 18, 20,   # Niveles 1-10 (originales) 
                      22, 25, 28, 32, 36, 40, 45, 50]        # Niveles 11-18 (nuevos)
TRAPS_PER_LEVEL = [4, 5, 6, 7, 8, 10, 12, 14, 16, 18,       # Niveles 1-10 (originales)
                  22, 26, 30, 35, 40, 45, 50, 60]           # Niveles 11-18 (nuevos)

# Cuerpos estelares y temas por nivel (extendido a 18 niveles)
STELLAR_BODIES = [
    # Niveles 1-10 (originales - Sistema Solar)
    {"name": "Mercurio", "theme": "hot", "bg_color": (160, 100, 60), "accent": (220, 140, 80)},
    {"name": "Venus", "theme": "hot", "bg_color": (180, 120, 40), "accent": (240, 180, 80)},
    {"name": "Marte", "theme": "desert", "bg_color": (160, 80, 40), "accent": (220, 120, 60)},
    {"name": "Júpiter", "theme": "gas", "bg_color": (120, 100, 160), "accent": (180, 140, 220)},
    {"name": "Saturno", "theme": "gas", "bg_color": (180, 160, 100), "accent": (240, 220, 140)},
    {"name": "Neptuno", "theme": "cold", "bg_color": (60, 120, 180), "accent": (100, 160, 240)},
    {"name": "Plutón", "theme": "cold", "bg_color": (80, 80, 120), "accent": (120, 120, 180)},
    {"name": "Betelgeuse", "theme": "stellar", "bg_color": (180, 60, 60), "accent": (240, 100, 100)},
    {"name": "Sirio", "theme": "stellar", "bg_color": (60, 100, 180), "accent": (100, 140, 240)},
    {"name": "Vega", "theme": "stellar", "bg_color": (160, 160, 180), "accent": (220, 220, 240)},
    
    # Niveles 11-18 (nuevos - Sistemas estelares avanzados)
    {"name": "Rigel", "theme": "supergiant", "bg_color": (100, 150, 255), "accent": (150, 200, 255)},
    {"name": "Antares", "theme": "supergiant", "bg_color": (255, 80, 80), "accent": (255, 120, 120)},
    {"name": "Aldebaran", "theme": "giant", "bg_color": (255, 140, 80), "accent": (255, 180, 120)},
    {"name": "Polaris", "theme": "cepheid", "bg_color": (200, 200, 255), "accent": (230, 230, 255)},
    {"name": "Capella", "theme": "multiple", "bg_color": (255, 255, 150), "accent": (255, 255, 200)},
    {"name": "Agujero Negro X1", "theme": "blackhole", "bg_color": (10, 5, 20), "accent": (50, 20, 80)},
    {"name": "Sagitario A*", "theme": "galactic_center", "bg_color": (80, 20, 100), "accent": (120, 60, 150)},
    {"name": "Núcleo Galáctico", "theme": "final_boss", "bg_color": (5, 0, 10), "accent": (100, 50, 200)}
]

# Colores RGB - Tema espacial
COLORS = {
    # Fondo espacial
    'space_bg': (5, 5, 15),
    'stars': (200, 200, 255),
    'nebula': (30, 20, 60),
    
    # UI
    'hud_background': (10, 10, 30),
    'menu_bg': (15, 15, 40),
    'button': (40, 60, 120),
    'button_hover': (60, 80, 140),
    'button_text': (255, 255, 255),
    
    # Entidades
    'player': (50, 130, 240),
    'enemy': (230, 70, 70),
    'projectile': (255, 220, 0),
    'treasure': (255, 215, 0),
    'trap': (150, 30, 30),
    'trap_range': (120, 30, 30),
    'equipment': (100, 200, 150),
    
    # Texto
    'white': (255, 255, 255),
    'yellow': (255, 255, 0),
    'cyan': (0, 255, 255),
    'gray': (200, 200, 200),
    'light_gray': (180, 180, 180),
    'green': (0, 255, 0),
    'health_green': (0, 200, 0),
    'health_bg': (80, 80, 80),
    'black': (0, 0, 0),
    
    # Efectos espaciales
    'particle': (100, 150, 255),
    'explosion': (255, 100, 50)
}