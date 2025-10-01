"""
Sistema de texto flotante para feedback visual.
Muestra mensajes temporales cuando se recogen objetos.
"""
import pygame
from typing import List, Tuple
from utils.math import Vector2D
from config.settings import COLORS, SCREEN_WIDTH, SCREEN_HEIGHT


class FloatingText:
    """Texto que aparece y se desvanece gradualmente."""
    
    def __init__(self, x: float, y: float, text: str, color: Tuple[int, int, int], 
                 font: pygame.font.Font, duration: float = 2.0):
        """
        Inicializa el texto flotante.
        
        Args:
            x: Posición X inicial
            y: Posición Y inicial
            text: Texto a mostrar
            color: Color del texto
            font: Fuente a usar
            duration: Duración en segundos
        """
        self.pos = Vector2D(x, y)
        self.text = text
        self.color = color
        self.font = font
        self.duration = duration
        self.elapsed = 0.0
        self.velocity = Vector2D(0, -30)  # Movimiento hacia arriba
        self.fade_start = duration * 0.6  # Empezar a desvanecer al 60%
        
    def update(self, dt: float) -> bool:
        """
        Actualiza el texto flotante.
        
        Args:
            dt: Tiempo transcurrido
            
        Returns:
            False si el texto debe ser eliminado
        """
        self.elapsed += dt
        self.pos = Vector2D(
            self.pos.x + self.velocity.x * dt,
            self.pos.y + self.velocity.y * dt
        )
        
        # Desacelerar el movimiento
        self.velocity = Vector2D(
            self.velocity.x * 0.98,
            self.velocity.y * 0.95
        )
        
        return self.elapsed < self.duration
        
    def render(self, screen: pygame.Surface) -> None:
        """
        Renderiza el texto flotante.
        
        Args:
            screen: Superficie donde dibujar
        """
        # Calcular alpha para fade out
        if self.elapsed > self.fade_start:
            fade_progress = (self.elapsed - self.fade_start) / (self.duration - self.fade_start)
            alpha = int(255 * (1.0 - fade_progress))
        else:
            alpha = 255
            
        alpha = max(0, min(255, alpha))
        
        # Crear superficie con alpha
        text_surface = self.font.render(self.text, True, self.color)
        
        if alpha < 255:
            # Crear superficie temporal para alpha blending
            temp_surface = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
            temp_surface.fill((*self.color, alpha))
            temp_surface.blit(text_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            text_surface = temp_surface
            
        # Centrar texto en la posición
        text_rect = text_surface.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        
        # Asegurar que el texto esté dentro de la pantalla
        text_rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        
        screen.blit(text_surface, text_rect)


class FloatingTextManager:
    """Gestor de todos los textos flotantes."""
    
    def __init__(self, font: pygame.font.Font):
        """
        Inicializa el gestor.
        
        Args:
            font: Fuente por defecto
        """
        self.font = font
        self.texts: List[FloatingText] = []
        
    def add_text(self, x: float, y: float, text: str, text_type: str = "default") -> None:
        """
        Añade un nuevo texto flotante.
        
        Args:
            x: Posición X
            y: Posición Y
            text: Texto a mostrar
            text_type: Tipo de texto para determinar color y estilo
        """
        color = self._get_color_for_type(text_type)
        duration = self._get_duration_for_type(text_type)
        
        floating_text = FloatingText(x, y, text, color, self.font, duration)
        self.texts.append(floating_text)
        
    def _get_color_for_type(self, text_type: str) -> Tuple[int, int, int]:
        """
        Obtiene el color según el tipo de texto.
        
        Args:
            text_type: Tipo de texto
            
        Returns:
            Color RGB
        """
        color_map = {
            "treasure": COLORS['yellow'],
            "gold": COLORS['gold'] if 'gold' in COLORS else (255, 215, 0),
            "item": COLORS['particle'],
            "equipment": COLORS['green'],
            "damage": COLORS['enemy'],
            "heal": COLORS['green'],
            "xp": COLORS['purple'] if 'purple' in COLORS else (128, 0, 128),
            "default": COLORS['white']
        }
        
        return color_map.get(text_type, COLORS['white'])
        
    def _get_duration_for_type(self, text_type: str) -> float:
        """
        Obtiene la duración según el tipo de texto.
        
        Args:
            text_type: Tipo de texto
            
        Returns:
            Duración en segundos
        """
        duration_map = {
            "treasure": 2.5,
            "gold": 2.0,
            "item": 3.0,
            "equipment": 3.5,
            "damage": 1.5,
            "heal": 2.0,
            "xp": 2.0,
            "default": 2.0
        }
        
        return duration_map.get(text_type, 2.0)
        
    def update(self, dt: float) -> None:
        """
        Actualiza todos los textos flotantes.
        
        Args:
            dt: Tiempo transcurrido
        """
        # Actualizar y filtrar textos que aún están activos
        self.texts = [text for text in self.texts if text.update(dt)]
        
    def render(self, screen: pygame.Surface) -> None:
        """
        Renderiza todos los textos flotantes.
        
        Args:
            screen: Superficie donde dibujar
        """
        for text in self.texts:
            text.render(screen)
            
    def clear(self) -> None:
        """Limpia todos los textos flotantes."""
        self.texts.clear()


def create_treasure_text(value: int) -> str:
    """
    Crea texto para tesoro recogido.
    
    Args:
        value: Valor del tesoro
        
    Returns:
        Texto descriptivo
    """
    if value < 50:
        return f"Fragmento de cristal (+{value} oro)"
    elif value < 100:
        return f"Gema menor (+{value} oro)"
    elif value < 200:
        return f"Reliquia antigua (+{value} oro)"
    else:
        return f"Tesoro legendario (+{value} oro)"


def create_item_text(item_name: str) -> str:
    """
    Crea texto para objeto recogido.
    
    Args:
        item_name: Nombre del objeto
        
    Returns:
        Texto descriptivo
    """
    item_descriptions = {
        "ArmamentoDefensa": "Equipo militar encontrado",
        "Tesoro": "Artefacto valioso",
        "TrampaExplosiva": "Dispositivo peligroso",
        "default": "Objeto desconocido"
    }
    
    return item_descriptions.get(item_name, item_descriptions["default"])