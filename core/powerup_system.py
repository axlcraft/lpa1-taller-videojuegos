"""
Sistema mejorado de power-ups y mejoras para el juego.
Incluye diferentes tipos de mejoras con efectos únicos.
"""
import random
from typing import List, Dict, Any
from entities.base import Figura
from utils.math import Vector2D
from config.settings import COLORS


class PowerUpType:
    """Tipos de power-ups disponibles."""
    HEALTH = "health"
    SHIELD = "shield"
    DAMAGE = "damage"
    SPEED = "speed"
    RAPID_FIRE = "rapid_fire"
    MULTI_SHOT = "multi_shot"
    PENETRATING = "penetrating"
    EXPLOSIVE = "explosive"
    MAGNETIC = "magnetic"
    REGENERATION = "regeneration"


class PowerUp(Figura):
    """Power-up que mejora las habilidades del jugador."""
    
    def __init__(self, x: float, y: float, power_type: str):
        """
        Inicializa un power-up.
        
        Args:
            x: Posición X inicial
            y: Posición Y inicial
            power_type: Tipo de power-up
        """
        color = self._get_color_for_type(power_type)
        super().__init__(x, y, 15, color)
        self.power_type = power_type
        self.name = self._get_name_for_type(power_type)
        self.description = self._get_description_for_type(power_type)
        self.duration = self._get_duration_for_type(power_type)
        self.value = self._get_value_for_type(power_type)
        self.animation_timer = 0.0
        
    def _get_color_for_type(self, power_type: str) -> tuple:
        """Obtiene el color según el tipo de power-up."""
        colors = {
            PowerUpType.HEALTH: (0, 255, 0),      # Verde
            PowerUpType.SHIELD: (0, 150, 255),    # Azul claro
            PowerUpType.DAMAGE: (255, 0, 0),      # Rojo
            PowerUpType.SPEED: (255, 255, 0),     # Amarillo
            PowerUpType.RAPID_FIRE: (255, 150, 0), # Naranja
            PowerUpType.MULTI_SHOT: (255, 0, 255), # Magenta
            PowerUpType.PENETRATING: (150, 255, 150), # Verde claro
            PowerUpType.EXPLOSIVE: (255, 100, 0),  # Rojo-naranja
            PowerUpType.MAGNETIC: (0, 255, 255),   # Cian
            PowerUpType.REGENERATION: (100, 255, 100) # Verde suave
        }
        return colors.get(power_type, (255, 255, 255))
        
    def _get_name_for_type(self, power_type: str) -> str:
        """Obtiene el nombre según el tipo de power-up."""
        names = {
            PowerUpType.HEALTH: "Botiquín Médico",
            PowerUpType.SHIELD: "Escudo Energético",
            PowerUpType.DAMAGE: "Amplificador de Daño",
            PowerUpType.SPEED: "Propulsores",
            PowerUpType.RAPID_FIRE: "Carga Rápida",
            PowerUpType.MULTI_SHOT: "Cañones Múltiples",
            PowerUpType.PENETRATING: "Munición Perforante",
            PowerUpType.EXPLOSIVE: "Carga Explosiva",
            PowerUpType.MAGNETIC: "Campo Magnético",
            PowerUpType.REGENERATION: "Nanobots Médicos"
        }
        return names.get(power_type, "Power-Up")
        
    def _get_description_for_type(self, power_type: str) -> str:
        """Obtiene la descripción según el tipo de power-up."""
        descriptions = {
            PowerUpType.HEALTH: "Restaura 50 puntos de salud",
            PowerUpType.SHIELD: "Otorga escudo temporal que absorbe daño",
            PowerUpType.DAMAGE: "Aumenta el daño de los proyectiles en 50%",
            PowerUpType.SPEED: "Aumenta la velocidad de movimiento en 30%",
            PowerUpType.RAPID_FIRE: "Reduce el tiempo de recarga de armas en 40%",
            PowerUpType.MULTI_SHOT: "Los disparos se dividen en 3 proyectiles",
            PowerUpType.PENETRATING: "Los proyectiles atraviesan enemigos",
            PowerUpType.EXPLOSIVE: "Los proyectiles explotan al impactar",
            PowerUpType.MAGNETIC: "Atrae objetos cercanos automáticamente",
            PowerUpType.REGENERATION: "Regenera 2 HP por segundo"
        }
        return descriptions.get(power_type, "Mejora desconocida")
        
    def _get_duration_for_type(self, power_type: str) -> float:
        """Obtiene la duración según el tipo de power-up."""
        durations = {
            PowerUpType.HEALTH: 0.0,           # Instantáneo
            PowerUpType.SHIELD: 15.0,          # 15 segundos
            PowerUpType.DAMAGE: 20.0,          # 20 segundos
            PowerUpType.SPEED: 15.0,           # 15 segundos
            PowerUpType.RAPID_FIRE: 25.0,      # 25 segundos
            PowerUpType.MULTI_SHOT: 18.0,      # 18 segundos
            PowerUpType.PENETRATING: 22.0,     # 22 segundos
            PowerUpType.EXPLOSIVE: 16.0,       # 16 segundos
            PowerUpType.MAGNETIC: 30.0,        # 30 segundos
            PowerUpType.REGENERATION: 20.0     # 20 segundos
        }
        return durations.get(power_type, 10.0)
        
    def _get_value_for_type(self, power_type: str) -> int:
        """Obtiene el valor según el tipo de power-up."""
        values = {
            PowerUpType.HEALTH: 50,            # Cantidad de HP
            PowerUpType.SHIELD: 100,           # Cantidad de escudo
            PowerUpType.DAMAGE: 50,            # Porcentaje de aumento
            PowerUpType.SPEED: 30,             # Porcentaje de aumento
            PowerUpType.RAPID_FIRE: 40,        # Porcentaje de reducción
            PowerUpType.MULTI_SHOT: 3,         # Número de proyectiles
            PowerUpType.PENETRATING: 1,        # Niveles de penetración
            PowerUpType.EXPLOSIVE: 25,         # Radio de explosión
            PowerUpType.MAGNETIC: 80,          # Radio magnético
            PowerUpType.REGENERATION: 2        # HP por segundo
        }
        return values.get(power_type, 1)
        
    def update(self, dt: float) -> None:
        """Actualiza el power-up (animación)."""
        self.animation_timer += dt * 3.0
        # Animación de flotación
        import math
        self.pos.y += math.sin(self.animation_timer) * 0.5
        
    def apply_effect(self, player) -> None:
        """
        Aplica el efecto del power-up al jugador.
        
        Args:
            player: Jugador que recoge el power-up
        """
        if self.power_type == PowerUpType.HEALTH:
            player.hp = min(player.max_hp, player.hp + self.value)
        elif self.power_type == PowerUpType.SHIELD:
            if not hasattr(player, 'shield'):
                player.shield = 0
            player.shield += self.value
        else:
            # Para efectos temporales, añadirlos a la lista de efectos activos
            if not hasattr(player, 'active_effects'):
                player.active_effects = {}
            player.active_effects[self.power_type] = {
                'duration': self.duration,
                'value': self.value,
                'name': self.name
            }


class PowerUpManager:
    """Gestor de power-ups."""
    
    def __init__(self):
        """Inicializa el gestor de power-ups."""
        self.power_ups: List[PowerUp] = []
        self.spawn_timer = 0.0
        self.spawn_interval = 8.0  # Cada 8 segundos
        
    def update(self, dt: float, scene_bounds: tuple) -> None:
        """
        Actualiza todos los power-ups.
        
        Args:
            dt: Tiempo transcurrido
            scene_bounds: Límites de la escena (min_x, min_y, max_x, max_y)
        """
        # Actualizar power-ups existentes
        for power_up in self.power_ups[:]:
            power_up.update(dt)
            
        # Generar nuevos power-ups
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0.0
            self._spawn_power_up(scene_bounds)
            
    def _spawn_power_up(self, scene_bounds: tuple) -> None:
        """Genera un nuevo power-up en una posición aleatoria."""
        min_x, min_y, max_x, max_y = scene_bounds
        
        # Posición aleatoria dentro de los límites
        x = random.uniform(min_x + 50, max_x - 50)
        y = random.uniform(min_y + 50, max_y - 50)
        
        # Tipo aleatorio con pesos
        power_types = [
            (PowerUpType.HEALTH, 20),      # Más común
            (PowerUpType.DAMAGE, 15),
            (PowerUpType.SPEED, 15),
            (PowerUpType.RAPID_FIRE, 12),
            (PowerUpType.SHIELD, 10),
            (PowerUpType.MULTI_SHOT, 8),
            (PowerUpType.PENETRATING, 6),
            (PowerUpType.EXPLOSIVE, 6),
            (PowerUpType.MAGNETIC, 4),
            (PowerUpType.REGENERATION, 4)  # Más raro
        ]
        
        # Selección ponderada
        total_weight = sum(weight for _, weight in power_types)
        random_value = random.randint(1, total_weight)
        
        current_weight = 0
        selected_type = PowerUpType.HEALTH
        
        for power_type, weight in power_types:
            current_weight += weight
            if random_value <= current_weight:
                selected_type = power_type
                break
                
        power_up = PowerUp(x, y, selected_type)
        self.power_ups.append(power_up)
        
    def check_collisions(self, player) -> List[PowerUp]:
        """
        Verifica colisiones con el jugador.
        
        Args:
            player: Jugador a verificar
            
        Returns:
            Lista de power-ups recogidos
        """
        collected = []
        
        for power_up in self.power_ups[:]:
            distance = ((player.pos.x - power_up.pos.x) ** 2 + 
                       (player.pos.y - power_up.pos.y) ** 2) ** 0.5
            
            if distance < (player.radio + power_up.radio):
                collected.append(power_up)
                self.power_ups.remove(power_up)
                
        return collected
        
    def remove_power_up(self, power_up: PowerUp) -> None:
        """Elimina un power-up específico."""
        if power_up in self.power_ups:
            self.power_ups.remove(power_up)