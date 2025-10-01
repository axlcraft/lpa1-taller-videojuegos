"""
Entidades base del juego.
Contiene la clase Figura que sirve como base para todos los elementos con posición y colisión.
"""
from typing import Tuple
from utils.math import Vector2D


class Figura:
    """Clase base para elementos con posición y radio (para colisiones)."""

    def __init__(self, x: float, y: float, radio: int, color: Tuple[int, int, int]):
        """
        Inicializa una figura.
        
        Args:
            x: Posición X inicial
            y: Posición Y inicial
            radio: Radio para colisiones
            color: Color RGB de la figura
        """
        self.pos = Vector2D(x, y)
        self.radio = radio
        self.color = color
        self.activo = True

    def distance_to(self, other: "Figura") -> float:
        """Calcula la distancia a otra figura."""
        return (self.pos - other.pos).magnitude()

    def collides_with(self, other: "Figura") -> bool:
        """Verifica si esta figura colisiona con otra."""
        return self.distance_to(other) <= (self.radio + other.radio)