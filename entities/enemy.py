"""
Enemigos del juego.
Contiene la clase Enemigo con IA básica y comportamiento de combate.
"""
import math
import random
from typing import TYPE_CHECKING, List
from entities.base import Figura
from entities.projectile import Proyectil
from utils.math import Vector2D
from config.settings import ENEMY_RADIUS, COLORS

if TYPE_CHECKING:
    from entities.player import Jugador


class Enemigo(Figura):
    """Enemigo con IA básica que persigue al jugador."""

    def __init__(self, x: float, y: float, tipo: str = "terrestre", level: int = 1):
        """
        Inicializa un enemigo.
        
        Args:
            x: Posición X inicial
            y: Posición Y inicial
            tipo: Tipo de enemigo ("terrestre", "volador", "artillero")
            level: Nivel del juego para escalado de dificultad
        """
        super().__init__(x, y, ENEMY_RADIUS, COLORS['enemy'])
        self.tipo = tipo
        self.level = level
        
        # Configurar estadísticas base según el tipo
        if tipo == "terrestre":
            base_hp = 60
            base_attack = 15
            base_defense = 3
            self.speed = 80.0
            base_contact_damage = 20
            self.can_shoot = False
        elif tipo == "volador":
            base_hp = 45
            base_attack = 12
            base_defense = 1
            self.speed = 110.0
            base_contact_damage = 15
            self.can_shoot = True
            self.shoot_range = 200.0
            self.shoot_cooldown = 1.5
        elif tipo == "artillero":
            base_hp = 80
            base_attack = 20
            base_defense = 5
            self.speed = 50.0
            base_contact_damage = 25
            self.can_shoot = True
            self.shoot_range = 300.0
            self.shoot_cooldown = 2.0
        elif tipo == "elite":  # Nuevo tipo para niveles 11+
            base_hp = 120
            base_attack = 30
            base_defense = 8
            self.speed = 90.0
            base_contact_damage = 35
            self.can_shoot = True
            self.shoot_range = 250.0
            self.shoot_cooldown = 1.0
        elif tipo == "berserker":  # Nuevo tipo para niveles 13+
            base_hp = 100
            base_attack = 40
            base_defense = 4
            self.speed = 140.0
            base_contact_damage = 50
            self.can_shoot = False
        elif tipo == "guardian":  # Nuevo tipo para niveles 15+
            base_hp = 180
            base_attack = 25
            base_defense = 15
            self.speed = 60.0
            base_contact_damage = 30
            self.can_shoot = True
            self.shoot_range = 400.0
            self.shoot_cooldown = 2.5
        else:
            # Tipo por defecto
            base_hp = 50
            base_attack = 10
            base_defense = 2
            self.speed = 70.0
            base_contact_damage = 12
            self.can_shoot = False
            
        # Aplicar escalado por nivel con dificultad progresiva más agresiva
        if level <= 10:
            # Escalado normal para niveles 1-10 (15% por nivel)
            level_multiplier = 1.0 + (level - 1) * 0.15
        else:
            # Escalado más agresivo para niveles 11-18 (25% por nivel + bonus base)
            base_multiplier = 1.0 + (10 - 1) * 0.15  # Multiplier at level 10
            extra_levels = level - 10
            level_multiplier = base_multiplier + (extra_levels * 0.25)
        
        self.hp = int(base_hp * level_multiplier)
        self.attack = int(base_attack * level_multiplier)
        self.defense = int(base_defense * level_multiplier)
        self.contact_damage = int(base_contact_damage * level_multiplier)
            
        self._invulnerable_timer = 0.0
        self._shoot_timer = 0.0
        self.last_shot_time = 0.0

    def update(self, dt: float, player: "Jugador") -> List[Proyectil]:
        """
        Actualiza el comportamiento del enemigo (IA simple).
        
        Args:
            dt: Tiempo transcurrido desde la última actualización
            player: Referencia al jugador para perseguirlo
            
        Returns:
            Lista de proyectiles creados por el enemigo
        """
        projectiles = []
        
        # Si está muerto, no hace nada
        if self.hp <= 0:
            return projectiles
        
        # Calcular dirección y distancia al jugador
        dir_to_player = Vector2D(player.pos.x - self.pos.x, player.pos.y - self.pos.y)
        distance_to_player = math.sqrt(dir_to_player.x**2 + dir_to_player.y**2)
        
        # Comportamiento según el tipo de enemigo
        if self.tipo == "terrestre":
            # Enemigo terrestre: solo persigue
            self._move_towards_player(dir_to_player, dt)
        elif self.tipo == "volador":
            # Enemigo volador: mantiene distancia y dispara
            if distance_to_player > self.shoot_range:
                self._move_towards_player(dir_to_player, dt)
            elif distance_to_player < self.shoot_range * 0.7:
                # Alejarse si está muy cerca
                self._move_away_from_player(dir_to_player, dt)
            # Disparar si está en rango
            if distance_to_player <= self.shoot_range:
                projectiles.extend(self._try_shoot(dir_to_player, dt))
        elif self.tipo == "artillero":
            # Enemigo artillero: se mantiene a distancia y dispara
            if distance_to_player > self.shoot_range * 1.2:
                self._move_towards_player(dir_to_player, dt)
            elif distance_to_player < self.shoot_range * 0.8:
                self._move_away_from_player(dir_to_player, dt)
            # Disparar si está en rango
            if distance_to_player <= self.shoot_range:
                projectiles.extend(self._try_shoot(dir_to_player, dt))
        
        # Actualizar timers
        self._invulnerable_timer = max(0.0, self._invulnerable_timer - dt)
        self._shoot_timer = max(0.0, self._shoot_timer - dt)
        
        return projectiles
        
    def _move_towards_player(self, dir_to_player: Vector2D, dt: float) -> None:
        """Mueve el enemigo hacia el jugador."""
        if dir_to_player.x != 0 or dir_to_player.y != 0:
            step = dir_to_player.normalized()
            self.pos = Vector2D(
                self.pos.x + step.x * self.speed * dt,
                self.pos.y + step.y * self.speed * dt
            )
            
    def _move_away_from_player(self, dir_to_player: Vector2D, dt: float) -> None:
        """Mueve el enemigo alejándose del jugador."""
        if dir_to_player.x != 0 or dir_to_player.y != 0:
            step = dir_to_player.normalized()
            self.pos = Vector2D(
                self.pos.x - step.x * self.speed * 0.5 * dt,
                self.pos.y - step.y * self.speed * 0.5 * dt
            )
            
    def _try_shoot(self, dir_to_player: Vector2D, dt: float) -> List[Proyectil]:
        """Intenta disparar al jugador."""
        projectiles = []
        
        if not self.can_shoot or self._shoot_timer > 0:
            return projectiles
            
        # Resetear timer de disparo
        self._shoot_timer = self.shoot_cooldown + random.uniform(-0.2, 0.2)
        
        # Crear proyectil
        direction = dir_to_player.normalized()
        projectile_speed = 300.0
        
        # Añadir un poco de imprecisión
        accuracy = 0.9 if self.tipo == "artillero" else 0.7
        angle_error = (1.0 - accuracy) * (random.random() - 0.5) * math.pi / 4
        
        cos_error = math.cos(angle_error)
        sin_error = math.sin(angle_error)
        
        # Rotar la dirección
        new_x = direction.x * cos_error - direction.y * sin_error
        new_y = direction.x * sin_error + direction.y * cos_error
        
        projectile = Proyectil(
            self.pos.x, self.pos.y,
            new_x * projectile_speed,
            new_y * projectile_speed,
            damage=int(self.attack), owner_type="enemy",
            color=(255, 100, 100)
        )
        
        projectiles.append(projectile)
        return projectiles

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
        
    def get_contact_damage(self) -> int:
        """
        Obtiene el daño que causa el enemigo por contacto.
        
        Returns:
            Daño por contacto
        """
        return self.contact_damage