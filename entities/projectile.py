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

    def __init__(self, x: float, y: float, vel_x: float, vel_y: float, 
                 damage: int = 10, owner_type: str = "player", 
                 color: Optional[Tuple[int, int, int]] = None):
        """
        Inicializa un proyectil.
        
        Args:
            x: Posición X inicial
            y: Posición Y inicial
            vel_x: Velocidad X del proyectil
            vel_y: Velocidad Y del proyectil
            damage: Daño que causa el proyectil
            owner_type: Tipo de dueño ("player" o "enemy")
            color: Color del proyectil
        """
        projectile_color = color if color else COLORS['projectile']
        super().__init__(x, y, PROJECTILE_RADIUS, projectile_color)
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.damage = damage
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