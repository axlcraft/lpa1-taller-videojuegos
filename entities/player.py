"""
Jugador del juego.
Contiene la clase Jugador con todas las mecánicas del personaje principal.
"""
import math
from typing import List, Optional
from entities.base import Figura
from entities.projectile import Proyectil
from world.objects import Objeto
from utils.math import Vector2D
from config.settings import PLAYER_RADIUS, COLORS


class Jugador(Figura):
    """Clase del jugador principal con sistema de niveles, inventario y combate."""

    def __init__(self, x: float, y: float, name: str = "Hero", character_data: Optional[dict] = None):
        """
        Inicializa el jugador.
        
        Args:
            x: Posición X inicial
            y: Posición Y inicial
            name: Nombre del jugador
            character_data: Datos del personaje seleccionado
        """
        # Configurar color y estadísticas según el personaje
        if character_data:
            color = character_data.get('color', COLORS['player'])
            stats = character_data.get('stats')
        else:
            color = COLORS['player']
            stats = None
            
        super().__init__(x, y, PLAYER_RADIUS, color)
        self.name = name
        self.character_type = character_data.get('ship_type', 'fighter') if character_data else 'fighter'
        
        # Aplicar estadísticas del personaje
        if stats:
            self.hp = stats.hp
            self.attack = stats.attack
            self.defense = stats.defense
            self.move_speed = stats.move_speed
            self.shoot_cooldown = stats.shoot_cooldown
            self.special_ability = stats.special_ability
        else:
            # Valores por defecto
            self.hp = 120
            self.attack = 18
            self.defense = 6
            self.move_speed = 180.0
            self.shoot_cooldown = 0.35
            self.special_ability = "Ninguna"
            
        self.max_hp = self.hp  # Para referencia
        self.level = 1
        self.xp = 0
        self.xp_to_next = 100
        self.inventory: List[Objeto] = []
        self.gold = 0
        self._shoot_timer = 0.0
        self.invulnerable_time = 0.6
        self._inv_timer = 0.0
        
        # Sistema de super disparo
        self.super_shot_charges = 0  # Se recarga matando enemigos
        self.max_super_charges = 4   # Necesita 4 kills para recargar
        self.super_shot_cooldown = 2.0  # Cooldown del super disparo
        self._super_shot_timer = 0.0

    def update_timers(self, dt: float) -> None:
        """
        Actualiza los temporizadores del jugador.
        
        Args:
            dt: Tiempo transcurrido desde la última actualización
        """
        self._shoot_timer = max(0.0, self._shoot_timer - dt)
        self._inv_timer = max(0.0, self._inv_timer - dt)
        self._super_shot_timer = max(0.0, self._super_shot_timer - dt)

    def can_shoot(self) -> bool:
        """Verifica si el jugador puede disparar."""
        return self._shoot_timer <= 0.0

    def shoot(self, target_pos: Vector2D) -> Optional[Proyectil]:
        """
        Dispara un proyectil hacia la posición objetivo.
        
        Args:
            target_pos: Posición objetivo del disparo
            
        Returns:
            Proyectil creado o None si no puede disparar
        """
        if not self.can_shoot():
            return None
        dir_vec = Vector2D(target_pos.x - self.pos.x, target_pos.y - self.pos.y)
        proj = Proyectil(self.pos.x, self.pos.y, dir_vec, speed=480.0, damage=self.attack // 1)
        self._shoot_timer = self.shoot_cooldown
        return proj
        
    def can_super_shoot(self) -> bool:
        """Verifica si puede usar el super disparo."""
        return self.super_shot_charges >= self.max_super_charges and self._super_shot_timer <= 0.0
        
    def super_shoot(self, target_pos: Vector2D) -> List[Proyectil]:
        """
        Dispara el super disparo (múltiples proyectiles).
        
        Args:
            target_pos: Posición objetivo del disparo
            
        Returns:
            Lista de proyectiles del super disparo
        """
        if not self.can_super_shoot():
            return []
            
        projectiles = []
        center_dir = Vector2D(target_pos.x - self.pos.x, target_pos.y - self.pos.y).normalized()
        
        # Crear 5 proyectiles en abanico
        angles = [-0.4, -0.2, 0.0, 0.2, 0.4]  # Radianes
        for angle in angles:
            # Rotar el vector dirección
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            new_dir = Vector2D(
                center_dir.x * cos_a - center_dir.y * sin_a,
                center_dir.x * sin_a + center_dir.y * cos_a
            )
            
            # Crear proyectil más poderoso
            proj = Proyectil(self.pos.x, self.pos.y, new_dir, speed=600.0, damage=self.attack * 2)
            projectiles.append(proj)
            
        # Consumir cargas y activar cooldown
        self.super_shot_charges = 0
        self._super_shot_timer = self.super_shot_cooldown
        return projectiles
        
    def add_kill(self) -> bool:
        """
        Añade una muerte al contador para el super disparo.
        
        Returns:
            True si el super disparo está listo
        """
        self.super_shot_charges = min(self.max_super_charges, self.super_shot_charges + 1)
        return self.super_shot_charges >= self.max_super_charges

    def receive_damage(self, amount: int) -> int:
        """
        Recibe daño aplicando defensa e invulnerabilidad.
        
        Args:
            amount: Cantidad de daño recibido
            
        Returns:
            Daño final aplicado
        """
        if self._inv_timer > 0:
            return 0
        damage_final = max(0, amount - self.defense)
        self.hp -= damage_final
        self._inv_timer = self.invulnerable_time
        return damage_final

    def gain_xp(self, amount: int) -> bool:
        """
        Gana experiencia y verifica si sube de nivel.
        
        Args:
            amount: Cantidad de XP ganada
            
        Returns:
            True si subió de nivel, False en caso contrario
        """
        self.xp += amount
        leveled = False
        while self.xp >= self.xp_to_next:
            self.xp -= self.xp_to_next
            self.level += 1
            self.hp += 20
            self.attack += 4
            self.defense += 2
            self.xp_to_next = int(self.xp_to_next * 1.4)
            leveled = True
        return leveled