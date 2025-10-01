"""
Enemigos del juego.
Contiene la clase Enemigo con IA básica y comportamiento de combate.
"""
from typing import TYPE_CHECKING
from entities.base import Figura
from utils.math import Vector2D
from config.settings import ENEMY_RADIUS, COLORS

if TYPE_CHECKING:
    from entities.player import Jugador


class Enemigo(Figura):
    """Enemigo con IA básica que persigue al jugador."""

    def __init__(self, x: float, y: float, tipo: str = "terrestre"):
        """
        Inicializa un enemigo.
        
        Args:
            x: Posición X inicial
            y: Posición Y inicial
            tipo: Tipo de enemigo ("terrestre" o "volador")
        """
        super().__init__(x, y, ENEMY_RADIUS, COLORS['enemy'])
        self.tipo = tipo
        self.hp = 60 if tipo == "terrestre" else 45
        self.attack = 12 if tipo == "terrestre" else 10
        self.defense = 3 if tipo == "terrestre" else 1
        self.speed = 80.0 if tipo == "terrestre" else 110.0
        self._invulnerable_timer = 0.0

    def update(self, dt: float, player: "Jugador") -> None:
        """
        Actualiza el comportamiento del enemigo (IA simple).
        
        Args:
            dt: Tiempo transcurrido desde la última actualización
            player: Referencia al jugador para perseguirlo
        """
        # IA simple: perseguir al jugador si está vivo
        if self.hp <= 0:
            return
        
        dir_to_player = Vector2D(player.pos.x - self.pos.x, player.pos.y - self.pos.y)
        step = dir_to_player.normalized()
        self.pos = Vector2D(
            self.pos.x + step.x * self.speed * dt,
            self.pos.y + step.y * self.speed * dt
        )
        self._invulnerable_timer = max(0.0, self._invulnerable_timer - dt)

    def receive_damage(self, amount: int) -> int:
        """
        Recibe daño aplicando defensa e invulnerabilidad temporal.
        
        Args:
            amount: Cantidad de daño recibido
            
        Returns:
            Daño final aplicado
        """
        if self._invulnerable_timer > 0:
            return 0
        dmg = max(0, amount - self.defense)
        self.hp -= dmg
        self._invulnerable_timer = 0.15
        return dmg