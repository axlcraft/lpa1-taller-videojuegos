"""
Proyectiles del juego.
Contiene la clase Proyectil para manejar proyectiles disparados por jugadores y enemigos.
"""
import math
from typing import Optional, Tuple
from entities.base import Figura
from utils.math import Vector2D
from config.settings import PROJECTILE_RADIUS, COLORS


class Proyectil(Figura):
    """Proyectil disparado por jugadores o enemigos."""

    def __init__(self, x: float, y: float, direction_or_vel_x, vel_y=None, 
                 speed: float = None, damage: int = 10, owner_type: str = "player", 
                 color: Optional[Tuple[int, int, int]] = None):
        """
        Inicializa un proyectil.
        
        Args:
            x: Posición X inicial
            y: Posición Y inicial
            direction_or_vel_x: Vector de dirección (Vector2D) o velocidad X
            vel_y: Velocidad Y del proyectil (si direction_or_vel_x es float)
            speed: Magnitud de la velocidad (si direction_or_vel_x es Vector2D)
            damage: Daño que causa el proyectil
            owner_type: Tipo de dueño ("player" o "enemy")
            color: Color del proyectil
        """
        projectile_color = color if color else COLORS['projectile']
        super().__init__(x, y, PROJECTILE_RADIUS, projectile_color)
        if vel_y is not None:
            # Forma antigua: vel_x, vel_y
            self.vel_x = direction_or_vel_x
            self.vel_y = vel_y
        elif speed is not None and hasattr(direction_or_vel_x, 'x') and hasattr(direction_or_vel_x, 'y'):
            # Forma nueva: dirección y velocidad
            self.vel_x = direction_or_vel_x.x * speed
            self.vel_y = direction_or_vel_x.y * speed
        else:
            raise ValueError("Proyectil requiere vel_x/vel_y o direction+speed")
        self.damage = int(damage)
        self.owner_type = owner_type
        self.lifetime = 3.0  # segundos
        self.special_effect = None  # Para efectos especiales como láser, plasma, etc.

    def update(self, dt: float) -> None:
        """
        Actualiza la posición del proyectil.
        
        Args:
            dt: Tiempo transcurrido desde la última actualización
        """
        self.pos = Vector2D(
            self.pos.x + self.vel_x * dt,
            self.pos.y + self.vel_y * dt
        )
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.activo = False
            
    def can_damage_player(self) -> bool:
        """Verifica si el proyectil puede dañar al jugador."""
        return self.owner_type == "enemy"
        
    def can_damage_enemy(self) -> bool:
        """Verifica si el proyectil puede dañar a enemigos."""
        return self.owner_type == "player"