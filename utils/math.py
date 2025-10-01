"""
Utilidades matemáticas para el juego.
Contiene la clase Vector2D para operaciones vectoriales.
"""
from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Tuple


@dataclass
class Vector2D:
    """Clase para representar vectores 2D con operaciones matemáticas básicas."""
    x: float
    y: float

    def __add__(self, other: "Vector2D") -> "Vector2D":
        """Suma dos vectores."""
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vector2D") -> "Vector2D":
        """Resta dos vectores."""
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Vector2D":
        """Multiplica el vector por un escalar."""
        return Vector2D(self.x * scalar, self.y * scalar)

    def magnitude(self) -> float:
        """Calcula la magnitud (longitud) del vector."""
        return math.hypot(self.x, self.y)

    def normalized(self) -> "Vector2D":
        """Devuelve un vector normalizado (unitario)."""
        mag = self.magnitude()
        if mag == 0:
            return Vector2D(0, 0)
        return Vector2D(self.x / mag, self.y / mag)

    def to_int_tuple(self) -> Tuple[int, int]:
        """Convierte el vector a una tupla de enteros."""
        return int(self.x), int(self.y)