"""
Sistema de selección y definición de personajes.
Contiene diferentes clases de pilotos espaciales con características únicas.
"""
from typing import Dict, Any, List
from dataclasses import dataclass
from config.settings import COLORS


@dataclass
class CharacterStats:
    """Estadísticas base de un personaje."""
    hp: int
    attack: int
    defense: int
    move_speed: float
    shoot_cooldown: float
    special_ability: str
    description: str


class CharacterType:
    """Tipos de personajes disponibles."""
    
    FIGHTER = "fighter"
    TANK = "tank"
    SNIPER = "sniper"
    SCOUT = "scout"


class CharacterManager:
    """Gestor de personajes y sus características."""
    
    def __init__(self):
        """Inicializa el gestor de personajes."""
        self.characters = self._create_characters()
        
    def _create_characters(self) -> Dict[str, Dict[str, Any]]:
        """Crea todos los personajes disponibles."""
        return {
            CharacterType.FIGHTER: {
                "name": "CAZA ESTELAR",
                "stats": CharacterStats(
                    hp=120,
                    attack=20,
                    defense=6,
                    move_speed=180.0,
                    shoot_cooldown=0.3,
                    special_ability="Disparo Rápido",
                    description="Equilibrado entre ataque y defensa"
                ),
                "color": COLORS['player'],
                "ship_type": "fighter"
            },
            CharacterType.TANK: {
                "name": "ACORAZADO",
                "stats": CharacterStats(
                    hp=180,
                    attack=15,
                    defense=12,
                    move_speed=120.0,
                    shoot_cooldown=0.5,
                    special_ability="Escudo Reforzado", 
                    description="Alta resistencia y defensa"
                ),
                "color": COLORS['green'],
                "ship_type": "tank"
            },
            CharacterType.SNIPER: {
                "name": "FRANCOTIRADOR",
                "stats": CharacterStats(
                    hp=90,
                    attack=35,
                    defense=3,
                    move_speed=160.0,
                    shoot_cooldown=0.7,
                    special_ability="Disparo Preciso",
                    description="Alto daño, baja resistencia"
                ),
                "color": COLORS['enemy'],
                "ship_type": "sniper"
            },
            CharacterType.SCOUT: {
                "name": "EXPLORADOR",
                "stats": CharacterStats(
                    hp=100,
                    attack=12,
                    defense=4,
                    move_speed=250.0,
                    shoot_cooldown=0.25,
                    special_ability="Velocidad Extrema",
                    description="Muy rápido y ágil"
                ),
                "color": COLORS['yellow'],
                "ship_type": "scout"
            }
        }
        
    def get_character(self, char_type: str) -> Dict[str, Any]:
        """
        Obtiene los datos de un personaje.
        
        Args:
            char_type: Tipo de personaje
            
        Returns:
            Diccionario con datos del personaje
        """
        return self.characters.get(char_type, self.characters[CharacterType.FIGHTER])
        
    def get_all_characters(self) -> Dict[str, Dict[str, Any]]:
        """Obtiene todos los personajes disponibles."""
        return self.characters
        
    def get_character_list(self) -> List[str]:
        """Obtiene lista de tipos de personajes."""
        return list(self.characters.keys())


class CharacterSelector:
    """Interfaz de selección de personajes."""
    
    def __init__(self, font, big_font):
        """
        Inicializa el selector.
        
        Args:
            font: Fuente normal
            big_font: Fuente grande
        """
        self.font = font
        self.big_font = big_font
        self.character_manager = CharacterManager()
        self.selected_index = 0
        self.character_types = self.character_manager.get_character_list()
        
    def handle_input(self, key: int, sound_manager=None) -> bool:
        """
        Maneja entrada del teclado.
        
        Args:
            key: Código de tecla presionada
            sound_manager: Gestor de sonidos (opcional)
            
        Returns:
            True si se seleccionó un personaje
        """
        import pygame
        
        if key == pygame.K_LEFT:
            self.selected_index = (self.selected_index - 1) % len(self.character_types)
            if sound_manager:
                sound_manager.play_sound('character_select', volume=0.5)
        elif key == pygame.K_RIGHT:
            self.selected_index = (self.selected_index + 1) % len(self.character_types)
            if sound_manager:
                sound_manager.play_sound('character_select', volume=0.5)
        elif key == pygame.K_RETURN or key == pygame.K_SPACE:
            if sound_manager:
                sound_manager.play_sound('character_select', volume=0.8)
            return True
            
        return False
        
    def get_selected_character(self) -> str:
        """Obtiene el tipo de personaje seleccionado."""
        return self.character_types[self.selected_index]
        
    def render(self, screen, screen_width: int, screen_height: int) -> None:
        """
        Renderiza la pantalla de selección.
        
        Args:
            screen: Superficie de pygame
            screen_width: Ancho de pantalla
            screen_height: Alto de pantalla
        """
        import pygame
        
        # Título
        title_text = self.big_font.render("SELECCIONA TU NAVE", True, COLORS['white'])
        title_rect = title_text.get_rect(center=(screen_width//2, 80))
        screen.blit(title_text, title_rect)
        
        # Instrucciones
        instruction_text = self.font.render("← → para navegar, ENTER para seleccionar", True, COLORS['gray'])
        instruction_rect = instruction_text.get_rect(center=(screen_width//2, 120))
        screen.blit(instruction_text, instruction_rect)
        
        # Mostrar personajes
        char_width = screen_width // 4
        start_x = char_width // 2
        
        for i, char_type in enumerate(self.character_types):
            character = self.character_manager.get_character(char_type)
            x_pos = start_x + i * char_width
            y_pos = screen_height // 2
            
            # Fondo de selección
            if i == self.selected_index:
                selection_rect = pygame.Rect(x_pos - 80, y_pos - 100, 160, 250)
                pygame.draw.rect(screen, COLORS['white'], selection_rect, 3)
                
            # Dibujar nave (representación simple)
            ship_color = character['color']
            self._draw_ship(screen, x_pos, y_pos - 40, character['ship_type'], ship_color)
            
            # Nombre del personaje
            name_text = self.font.render(character['name'], True, COLORS['white'])
            name_rect = name_text.get_rect(center=(x_pos, y_pos + 20))
            screen.blit(name_text, name_rect)
            
            # Estadísticas
            stats = character['stats']
            stat_y = y_pos + 50
            
            stat_lines = [
                f"HP: {stats.hp}",
                f"ATK: {stats.attack}",
                f"DEF: {stats.defense}",
                f"VEL: {int(stats.move_speed)}",
                stats.special_ability
            ]
            
            font_color = COLORS['yellow'] if i == self.selected_index else COLORS['gray']
            
            for j, line in enumerate(stat_lines):
                stat_text = self.font.render(line, True, font_color)
                stat_rect = stat_text.get_rect(center=(x_pos, stat_y + j * 20))
                screen.blit(stat_text, stat_rect)
                
        # Descripción del personaje seleccionado
        selected_char = self.character_manager.get_character(self.get_selected_character())
        desc_text = self.font.render(selected_char['stats'].description, True, COLORS['particle'])
        desc_rect = desc_text.get_rect(center=(screen_width//2, screen_height - 50))
        screen.blit(desc_text, desc_rect)
        
    def _draw_ship(self, screen, x: int, y: int, ship_type: str, color: tuple) -> None:
        """
        Dibuja una representación simple de la nave.
        
        Args:
            screen: Superficie de pygame
            x: Posición X
            y: Posición Y
            ship_type: Tipo de nave
            color: Color de la nave
        """
        import pygame
        
        if ship_type == "fighter":
            # Caza - forma triangular clásica
            points = [(x, y-20), (x-15, y+15), (x+15, y+15)]
            pygame.draw.polygon(screen, color, points)
            pygame.draw.polygon(screen, COLORS['white'], points, 2)
            
        elif ship_type == "tank":
            # Acorazado - forma rectangular robusta
            rect = pygame.Rect(x-20, y-15, 40, 30)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, COLORS['white'], rect, 2)
            # Cañones
            pygame.draw.rect(screen, color, (x-5, y-25, 10, 15))
            
        elif ship_type == "sniper":
            # Francotirador - forma alargada
            points = [(x, y-25), (x-8, y+20), (x+8, y+20)]
            pygame.draw.polygon(screen, color, points)
            pygame.draw.polygon(screen, COLORS['white'], points, 2)
            # Cañón largo
            pygame.draw.line(screen, COLORS['white'], (x, y-25), (x, y-35), 3)
            
        elif ship_type == "scout":
            # Explorador - forma de diamante
            points = [(x, y-15), (x-12, y), (x, y+15), (x+12, y)]
            pygame.draw.polygon(screen, color, points)
            pygame.draw.polygon(screen, COLORS['white'], points, 2)