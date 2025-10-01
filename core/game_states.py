"""
Sistema de estados del juego.
Maneja los diferentes estados: menú, juego, transición de niveles, etc.
"""
from enum import Enum
from typing import Optional
import pygame
import math
import random
from utils.math import Vector2D
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, COLORS


class GameState(Enum):
    """Estados posibles del juego."""
    MENU = "menu"
    MODE_SELECT = "mode_select"
    LEVEL_SELECT = "level_select"
    LEADERBOARD = "leaderboard"
    CHARACTER_SELECT = "character_select"
    PLAYING = "playing"
    LEVEL_COMPLETE = "level_complete"
    SHOP = "shop"
    GAME_OVER = "game_over"
    VICTORY = "victory"


class Button:
    """Botón simple para la interfaz."""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str, font: pygame.font.Font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.is_hovered = False
        # Customizable colors
        self.color = COLORS['button']
        self.hover_color = COLORS['button_hover']
        self.text_color = COLORS['button_text']
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Maneja eventos del botón. Retorna True si fue clickeado."""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                return True
        return False
    
    def draw(self, screen: pygame.Surface):
        """Dibuja el botón."""
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, COLORS['white'], self.rect, 2)
        
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


class InputField:
    """Campo de entrada de texto."""
    
    def __init__(self, x: int, y: int, width: int, height: int, font: pygame.font.Font, placeholder: str = ""):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.text = ""
        self.placeholder = placeholder
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0
        
    def handle_event(self, event: pygame.event.Event):
        """Maneja eventos del campo de texto."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode.isprintable() and len(self.text) < 15:
                self.text += event.unicode
    
    def update(self, dt: float):
        """Actualiza el cursor parpadeante."""
        self.cursor_timer += dt
        if self.cursor_timer >= 0.5:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
    
    def draw(self, screen: pygame.Surface):
        """Dibuja el campo de texto."""
        color = COLORS['button_hover'] if self.active else COLORS['button']
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, COLORS['white'], self.rect, 2)
        
        display_text = self.text if self.text else self.placeholder
        text_color = COLORS['white'] if self.text else COLORS['gray']
        text_surface = self.font.render(display_text, True, text_color)
        
        text_x = self.rect.x + 10
        text_y = self.rect.centery - text_surface.get_height() // 2
        screen.blit(text_surface, (text_x, text_y))
        
        # Cursor parpadeante
        if self.active and self.cursor_visible and self.text:
            cursor_x = text_x + text_surface.get_width() + 2
            cursor_y = self.rect.y + 5
            pygame.draw.line(screen, COLORS['white'], 
                           (cursor_x, cursor_y), 
                           (cursor_x, cursor_y + self.rect.height - 10), 2)


class Star:
    """Estrella para el fondo espacial."""
    
    def __init__(self, base_color=None):
        self.pos = Vector2D(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))
        self.speed = random.uniform(10, 50)
        self.brightness = random.randint(100, 255)
        self.size = random.randint(1, 3)
        self.base_color = base_color if base_color else (255, 255, 255)
        self.color = self._calculate_color()
    
    def _calculate_color(self):
        """Calcula el color de la estrella basado en el brillo y color base."""
        factor = self.brightness / 255.0
        return (
            int(self.base_color[0] * factor),
            int(self.base_color[1] * factor),
            int(self.base_color[2] * factor)
        )
    
    def update(self, dt: float):
        """Actualiza la posición de la estrella."""
        self.pos.y += self.speed * dt
        if self.pos.y > SCREEN_HEIGHT:
            self.pos.y = -self.size
            self.pos.x = random.randint(0, SCREEN_WIDTH)
    
    def draw(self, screen: pygame.Surface):
        """Dibuja la estrella."""
        pygame.draw.circle(screen, self.color, self.pos.to_int_tuple(), self.size)


class SpaceBackground:
    """Fondo espacial con estrellas en movimiento y ambientes planetarios."""
    
    def __init__(self, num_stars: int = 100, bg_color=None, star_color=None):
        self.stars = [Star(star_color) for _ in range(num_stars)]
        self.bg_color = bg_color if bg_color else COLORS['space_bg']
        self.current_level = 1
        self.planetary_effects = []
        self.atmosphere_particles = []
        
    def update(self, dt: float):
        """Actualiza todas las estrellas y efectos planetarios."""
        for star in self.stars:
            star.update(dt)
        
        # Actualizar efectos atmosféricos
        for particle in self.atmosphere_particles[:]:
            particle['pos'].x += particle['vel'].x * dt
            particle['pos'].y += particle['vel'].y * dt
            particle['life'] -= dt
            
            # Remover partículas que han expirado
            if particle['life'] <= 0:
                self.atmosphere_particles.remove(particle)
    
    def draw(self, screen: pygame.Surface):
        """Dibuja el fondo espacial con ambiente planetario."""
        self._draw_planetary_background(screen)
        
        # Dibujar estrellas
        for star in self.stars:
            star.draw(screen)
        
        # Dibujar efectos atmosféricos
        self._draw_atmospheric_effects(screen)
            
    def set_theme(self, bg_color, star_color):
        """Cambia el tema del fondo."""
        self.bg_color = bg_color
        for star in self.stars:
            star.color = star_color
    
    def set_planetary_level(self, level: int):
        """Configura el ambiente planetario según el nivel."""
        self.current_level = level
        self._generate_planetary_effects()
    
    def _draw_planetary_background(self, screen: pygame.Surface):
        """Dibuja el fondo planetario según el nivel actual."""
        from config.settings import STELLAR_BODIES
        
        if 1 <= self.current_level <= len(STELLAR_BODIES):
            stellar_body = STELLAR_BODIES[self.current_level - 1]
            theme = stellar_body.get("theme", "space")
            bg_color = stellar_body.get("bg_color", self.bg_color)
            
            # Aplicar color de fondo base primero
            adjusted_bg = (
                max(5, bg_color[0] // 3),  # Oscurecer para el espacio
                max(5, bg_color[1] // 3),
                max(5, bg_color[2] // 3)
            )
            screen.fill(adjusted_bg)
            
            if theme == "hot":  # Planetas calientes como Venus, Mercurio
                self._draw_hot_planet_bg(screen, bg_color)
            elif theme == "cold":  # Planetas fríos como Neptuno, Plutón
                self._draw_cold_planet_bg(screen, bg_color)
            elif theme == "desert":  # Planetas desérticos como Marte
                self._draw_desert_planet_bg(screen, bg_color)
            elif theme == "gas":  # Gigantes gaseosos como Júpiter, Saturno
                self._draw_gas_planet_bg(screen, bg_color)
            elif theme == "stellar":  # Estrellas como Betelgeuse, Sirio
                self._draw_stellar_bg(screen, bg_color)
        else:
            screen.fill(self.bg_color)
    
    def _draw_hot_planet_bg(self, screen: pygame.Surface, base_color: tuple):
        """Dibuja fondo de planeta caliente con efectos de calor."""
        # Gradiente de calor
        for y in range(0, SCREEN_HEIGHT, 4):
            intensity = 1.0 - (y / SCREEN_HEIGHT) * 0.3
            color = (
                min(255, int(base_color[0] * intensity)),
                min(255, int(base_color[1] * intensity)),
                min(255, int(base_color[2] * intensity))
            )
            pygame.draw.rect(screen, color, (0, y, SCREEN_WIDTH, 4))
        
        # Efectos de calor (ondas)
        import math
        time = pygame.time.get_ticks() * 0.001
        for i in range(5):
            wave_y = SCREEN_HEIGHT * 0.2 + i * 60 + math.sin(time + i) * 20
            heat_color = (255, 100 + i * 20, 0, 50)
            if wave_y > 0 and wave_y < SCREEN_HEIGHT:
                # Simular onda de calor con líneas onduladas
                for x in range(0, SCREEN_WIDTH, 8):
                    wave_offset = math.sin(time * 2 + x * 0.01) * 10
                    start_y = int(wave_y + wave_offset)
                    end_y = int(wave_y + wave_offset + 3)
                    if 0 <= start_y < SCREEN_HEIGHT and 0 <= end_y < SCREEN_HEIGHT:
                        pygame.draw.line(screen, heat_color[:3], (x, start_y), (x, end_y), 2)
    
    def _draw_cold_planet_bg(self, screen: pygame.Surface, base_color: tuple):
        """Dibuja fondo de planeta frío con efectos de hielo."""
        # Gradiente frío
        for y in range(0, SCREEN_HEIGHT, 3):
            intensity = 0.6 + (y / SCREEN_HEIGHT) * 0.4
            color = (
                min(255, int(base_color[0] * intensity)),
                min(255, int(base_color[1] * intensity)),
                min(255, int(base_color[2] * intensity))
            )
            pygame.draw.rect(screen, color, (0, y, SCREEN_WIDTH, 3))
        
        # Cristales de hielo flotantes
        time = pygame.time.get_ticks() * 0.0005
        for i in range(15):
            crystal_x = (i * 80 + time * 30) % (SCREEN_WIDTH + 50)
            crystal_y = (i * 40 + time * 20) % SCREEN_HEIGHT
            size = 3 + (i % 3)
            ice_color = (200, 230, 255)
            pygame.draw.polygon(screen, ice_color, [
                (crystal_x, crystal_y - size),
                (crystal_x - size, crystal_y + size),
                (crystal_x + size, crystal_y + size)
            ])
    
    def _draw_desert_planet_bg(self, screen: pygame.Surface, base_color: tuple):
        """Dibuja fondo de planeta desértico con tormentas de arena."""
        screen.fill(base_color)
        
        # Tormenta de arena
        time = pygame.time.get_ticks() * 0.001
        import math
        for i in range(20):
            sand_x = (i * 40 + time * 50) % (SCREEN_WIDTH + 100)
            sand_y = (i * 30 + time * 25) % SCREEN_HEIGHT
            opacity = int(100 + 50 * math.sin(time + i))
            sand_color = (180, 140, 100, opacity)
            size = 2 + (i % 4)
            pygame.draw.circle(screen, sand_color[:3], (int(sand_x), int(sand_y)), size)
    
    def _draw_gas_planet_bg(self, screen: pygame.Surface, base_color: tuple):
        """Dibuja fondo de gigante gaseoso con bandas atmosféricas."""
        # Bandas horizontales de gas
        num_bands = 8
        for band in range(num_bands):
            band_height = SCREEN_HEIGHT // num_bands
            y_start = band * band_height
            
            # Alternar colores para crear bandas
            band_intensity = 0.7 + (band % 2) * 0.3
            band_color = (
                min(255, int(base_color[0] * band_intensity)),
                min(255, int(base_color[1] * band_intensity)),
                min(255, int(base_color[2] * band_intensity))
            )
            pygame.draw.rect(screen, band_color, (0, y_start, SCREEN_WIDTH, band_height))
        
        # Tormenta atmosférica (Gran Mancha Roja estilo Júpiter)
        time = pygame.time.get_ticks() * 0.0003
        storm_x = SCREEN_WIDTH * 0.7
        storm_y = SCREEN_HEIGHT * 0.4
        storm_radius = 60 + math.sin(time) * 10
        storm_color = (min(255, base_color[0] + 50), max(0, base_color[1] - 30), max(0, base_color[2] - 30))
        pygame.draw.circle(screen, storm_color, (int(storm_x), int(storm_y)), int(storm_radius))
        pygame.draw.circle(screen, base_color, (int(storm_x), int(storm_y)), int(storm_radius - 15))
    
    def _draw_stellar_bg(self, screen: pygame.Surface, base_color: tuple):
        """Dibuja fondo estelar con efectos de estrella."""
        # Brillo estelar pulsante
        import math
        time = pygame.time.get_ticks() * 0.002
        intensity = 0.5 + 0.5 * math.sin(time)
        
        stellar_color = (
            min(255, int(base_color[0] * intensity)),
            min(255, int(base_color[1] * intensity)),
            min(255, int(base_color[2] * intensity))
        )
        screen.fill(stellar_color)
        
        # Llamaradas estelares
        for i in range(8):
            flare_angle = (i * math.pi / 4) + time * 0.1
            flare_length = 100 + 50 * math.sin(time * 2 + i)
            start_x = SCREEN_WIDTH // 2
            start_y = SCREEN_HEIGHT // 2
            end_x = start_x + math.cos(flare_angle) * flare_length
            end_y = start_y + math.sin(flare_angle) * flare_length
            
            flare_color = (255, min(255, base_color[1] + 100), 0)
            pygame.draw.line(screen, flare_color, (start_x, start_y), (int(end_x), int(end_y)), 3)
    
    def _draw_atmospheric_effects(self, screen: pygame.Surface):
        """Dibuja efectos atmosféricos como partículas flotantes."""
        for particle in self.atmosphere_particles:
            alpha = int(255 * (particle['life'] / particle['max_life']))
            color = (*particle['color'], alpha) if alpha < 255 else particle['color']
            size = max(1, int(particle['size'] * (particle['life'] / particle['max_life'])))
            pygame.draw.circle(screen, color[:3], 
                             (int(particle['pos'].x), int(particle['pos'].y)), size)
    
    def _generate_planetary_effects(self):
        """Genera efectos atmosféricos según el planeta actual."""
        self.atmosphere_particles.clear()
        
        from config.settings import STELLAR_BODIES
        if 1 <= self.current_level <= len(STELLAR_BODIES):
            stellar_body = STELLAR_BODIES[self.current_level - 1]
            theme = stellar_body.get("theme", "space")
            
            # Generar partículas atmosféricas según el tema
            if theme in ["hot", "stellar"]:
                # Partículas de fuego/plasma
                for _ in range(10):
                    self.atmosphere_particles.append({
                        'pos': Vector2D(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)),
                        'vel': Vector2D(random.uniform(-20, 20), random.uniform(-30, -10)),
                        'color': (255, random.randint(100, 200), 0),
                        'size': random.randint(2, 5),
                        'life': random.uniform(2.0, 4.0),
                        'max_life': 3.0
                    })
            elif theme == "cold":
                # Cristales de hielo flotantes
                for _ in range(8):
                    self.atmosphere_particles.append({
                        'pos': Vector2D(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)),
                        'vel': Vector2D(random.uniform(-10, 10), random.uniform(10, 30)),
                        'color': (150, 200, 255),
                        'size': random.randint(1, 3),
                        'life': random.uniform(3.0, 6.0),
                        'max_life': 4.0
                    })