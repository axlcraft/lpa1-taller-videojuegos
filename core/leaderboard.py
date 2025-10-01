"""
Sistema de puntuaciones altas (Leaderboard).
Gestiona el guardado y visualización de las mejores puntuaciones.
"""
import json
import os
from typing import List, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from config.settings import COLORS, SCREEN_WIDTH, SCREEN_HEIGHT


@dataclass
class ScoreEntry:
    """Entrada de puntuación en el leaderboard."""
    player_name: str
    character_name: str
    character_type: str
    score: int
    level_reached: int
    date: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la entrada a diccionario."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScoreEntry':
        """Crea una entrada desde un diccionario."""
        return cls(**data)


class Leaderboard:
    """Gestor del sistema de puntuaciones altas."""
    
    def __init__(self, max_entries: int = 10):
        """
        Inicializa el leaderboard.
        
        Args:
            max_entries: Número máximo de entradas a mantener
        """
        self.max_entries = max_entries
        self.scores_file = "scores.json"
        self.scores: List[ScoreEntry] = []
        self.load_scores()
        
    def load_scores(self) -> None:
        """Carga las puntuaciones desde el archivo."""
        try:
            if os.path.exists(self.scores_file):
                with open(self.scores_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.scores = [ScoreEntry.from_dict(entry) for entry in data]
            else:
                self.scores = []
        except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
            print(f"Error cargando puntuaciones: {e}")
            self.scores = []
            
    def save_scores(self) -> None:
        """Guarda las puntuaciones al archivo."""
        try:
            with open(self.scores_file, 'w', encoding='utf-8') as f:
                data = [score.to_dict() for score in self.scores]
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando puntuaciones: {e}")
            
    def add_score(self, player_name: str, character_name: str, character_type: str, 
                  score: int, level_reached: int) -> bool:
        """
        Añade una nueva puntuación.
        
        Args:
            player_name: Nombre del jugador
            character_name: Nombre del personaje
            character_type: Tipo de personaje
            score: Puntuación obtenida
            level_reached: Nivel máximo alcanzado
            
        Returns:
            True si la puntuación fue añadida al top 10
        """
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        new_entry = ScoreEntry(
            player_name=player_name,
            character_name=character_name,
            character_type=character_type,
            score=score,
            level_reached=level_reached,
            date=date_str
        )
        
        # Añadir y ordenar por puntuación (descendente)
        self.scores.append(new_entry)
        self.scores.sort(key=lambda x: x.score, reverse=True)
        
        # Mantener solo las mejores puntuaciones
        is_top_score = len(self.scores) <= self.max_entries or new_entry in self.scores[:self.max_entries]
        self.scores = self.scores[:self.max_entries]
        
        self.save_scores()
        return is_top_score
        
    def get_top_scores(self, count: int = None) -> List[ScoreEntry]:
        """
        Obtiene las mejores puntuaciones.
        
        Args:
            count: Número de puntuaciones a retornar (None para todas)
            
        Returns:
            Lista de puntuaciones ordenadas
        """
        if count is None:
            return self.scores.copy()
        return self.scores[:count]
        
    def is_high_score(self, score: int) -> bool:
        """
        Verifica si una puntuación clasifica para el top 10.
        
        Args:
            score: Puntuación a verificar
            
        Returns:
            True si es una puntuación alta
        """
        if len(self.scores) < self.max_entries:
            return True
        return score > self.scores[-1].score
        
    def get_player_best(self, player_name: str) -> ScoreEntry:
        """
        Obtiene la mejor puntuación de un jugador específico.
        
        Args:
            player_name: Nombre del jugador
            
        Returns:
            Mejor entrada del jugador o None
        """
        player_scores = [s for s in self.scores if s.player_name == player_name]
        return player_scores[0] if player_scores else None


class LeaderboardScreen:
    """Pantalla de visualización del leaderboard."""
    
    def __init__(self, font, big_font, leaderboard: Leaderboard):
        """
        Inicializa la pantalla.
        
        Args:
            font: Fuente normal
            big_font: Fuente grande
            leaderboard: Sistema de puntuaciones
        """
        self.font = font
        self.big_font = big_font
        self.leaderboard = leaderboard
        
    def render(self, screen) -> None:
        """
        Renderiza la pantalla de puntuaciones.
        
        Args:
            screen: Superficie de pygame
        """
        import pygame
        
        # Título
        title_text = self.big_font.render("TABLA DE PUNTUACIONES", True, COLORS['white'])
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 60))
        screen.blit(title_text, title_rect)
        
        # Subtítulo
        subtitle_text = self.font.render("Los mejores pilotos de la galaxia", True, COLORS['gray'])
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH//2, 100))
        screen.blit(subtitle_text, subtitle_rect)
        
        # Encabezados de tabla
        headers_y = 140
        col_widths = [50, 200, 150, 100, 80, 120]  # Ancho de columnas
        col_x_positions = []
        current_x = 50
        
        for width in col_widths:
            col_x_positions.append(current_x)
            current_x += width
            
        headers = ["#", "JUGADOR", "NAVE", "PUNTOS", "NIVEL", "FECHA"]
        
        for i, header in enumerate(headers):
            header_text = self.font.render(header, True, COLORS['yellow'])
            screen.blit(header_text, (col_x_positions[i], headers_y))
            
        # Línea separadora
        pygame.draw.line(screen, COLORS['gray'], 
                        (50, headers_y + 25), (SCREEN_WIDTH - 50, headers_y + 25), 2)
        
        # Puntuaciones
        scores = self.leaderboard.get_top_scores(10)
        start_y = headers_y + 40
        
        if not scores:
            # Mensaje si no hay puntuaciones
            no_scores_text = self.font.render("No hay puntuaciones registradas", True, COLORS['gray'])
            no_scores_rect = no_scores_text.get_rect(center=(SCREEN_WIDTH//2, start_y + 100))
            screen.blit(no_scores_text, no_scores_rect)
        else:
            for i, score in enumerate(scores):
                y_pos = start_y + i * 30
                
                # Color alternado para filas
                row_color = COLORS['white'] if i % 2 == 0 else COLORS['light_gray']
                
                # Color especial para el primer lugar
                if i == 0:
                    row_color = COLORS['yellow']
                elif i == 1:
                    row_color = COLORS['light_gray']
                elif i == 2:
                    row_color = (205, 127, 50)  # Bronce
                    
                # Datos de la fila
                row_data = [
                    f"{i + 1}°",
                    score.player_name[:15],  # Limitar longitud
                    score.character_name[:12],
                    f"{score.score:,}",
                    f"{score.level_reached}",
                    score.date.split()[0]  # Solo la fecha, sin hora
                ]
                
                for j, data in enumerate(row_data):
                    text = self.font.render(data, True, row_color)
                    screen.blit(text, (col_x_positions[j], y_pos))
                    
        # Instrucciones
        instructions = [
            "ESC - Volver al menú principal",
            "R - Actualizar puntuaciones"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_text = self.font.render(instruction, True, COLORS['gray'])
            inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 60 + i * 25))
            screen.blit(inst_text, inst_rect)
            
    def handle_input(self, key: int) -> str:
        """
        Maneja la entrada del teclado.
        
        Args:
            key: Código de tecla presionada
            
        Returns:
            Acción a realizar ('menu', 'refresh', '')
        """
        import pygame
        
        if key == pygame.K_ESCAPE:
            return 'menu'
        elif key == pygame.K_r:
            self.leaderboard.load_scores()  # Recargar puntuaciones
            return 'refresh'
        return ''