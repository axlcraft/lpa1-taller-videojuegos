"""
Proyectiles del juego.
Contiene la clase Proyectil para manejar proyectiles disparados por el jugador.
"""
from typing import Optional
from entities.base import Figura
from utils.math import Vector2D
from config.settings import PROJECTILE_RADIUS, COLORS


class Proyectil(Figura):
    """Proyectil disparado por el jugador."""

    def __init__(self, x: float, y: float, direction: Vector2D, speed: float = 400.0, damage: int = 10):
        """
        Inicializa un proyectil.
        
        Args:
            x: Posición X inicial
            y: Posición Y inicial
            direction: Vector de dirección del movimiento
            speed: Velocidad del proyectil en píxeles por segundo
            damage: Daño que causa el proyectil
        """
        super().__init__(x, y, PROJECTILE_RADIUS, COLORS['projectile'])
        self.direction = direction.normalized()
        self.speed = speed
        self.damage = damage
        self.lifetime = 2.5  # segundos

    def update(self, dt: float) -> None:
        """
        Actualiza la posición del proyectil.
        
        Args:
            dt: Tiempo transcurrido desde la última actualización
        """
        self.pos = Vector2D(
            self.pos.x + self.direction.x * self.speed * dt,
            self.pos.y + self.direction.y * self.speed * dt
        )
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.activo = False