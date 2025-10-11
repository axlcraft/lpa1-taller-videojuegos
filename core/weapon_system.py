"""
Sistema avanzado de armas para el juego.
Incluye diferentes tipos de armas con efectos únicos.
"""
import math
import random
from typing import List, Tuple, Optional
from entities.projectile import Proyectil
from utils.math import Vector2D
from config.settings import COLORS


class WeaponType:
    """Tipos de armas disponibles."""
    BASIC = "basic"
    RAPID_FIRE = "rapid_fire"
    SHOTGUN = "shotgun"
    LASER = "laser"
    PLASMA = "plasma"
    MISSILE = "missile"


class Weapon:
    """Clase base para armas."""
    
    def __init__(self, weapon_type: str, name: str, damage: int, 
                 cooldown: float, projectile_speed: float, 
                 projectile_color: Tuple[int, int, int],
                 special_effect: Optional[str] = None):
        """
        Inicializa un arma.
        
        Args:
            weapon_type: Tipo de arma
            name: Nombre del arma
            damage: Daño base
            cooldown: Tiempo de recarga
            projectile_speed: Velocidad del proyectil
            projectile_color: Color del proyectil
            special_effect: Efecto especial del arma
        """
        self.weapon_type = weapon_type
        self.name = name
        self.damage = damage
        self.cooldown = cooldown
        self.projectile_speed = projectile_speed
        self.projectile_color = projectile_color
        self.special_effect = special_effect
        self.current_cooldown = 0.0
        
    def update(self, dt: float) -> None:
        """Actualiza el cooldown del arma."""
        self.current_cooldown = max(0.0, self.current_cooldown - dt)
        
    def can_shoot(self) -> bool:
        """Verifica si el arma puede disparar."""
        return self.current_cooldown <= 0.0
        
    def shoot(self, pos: Vector2D, direction: Vector2D, owner_type: str = "player") -> List[Proyectil]:
        """
        Dispara el arma.
        
        Args:
            pos: Posición de disparo
            direction: Dirección de disparo
            owner_type: Tipo de dueño ("player" o "enemy")
            
        Returns:
            Lista de proyectiles creados
        """
        if not self.can_shoot():
            return []
            
        self.current_cooldown = self.cooldown
        projectiles = []
        
        if self.weapon_type == WeaponType.BASIC:
            projectiles = self._shoot_basic(pos, direction, owner_type)
        elif self.weapon_type == WeaponType.RAPID_FIRE:
            projectiles = self._shoot_rapid_fire(pos, direction, owner_type)
        elif self.weapon_type == WeaponType.SHOTGUN:
            projectiles = self._shoot_shotgun(pos, direction, owner_type)
        elif self.weapon_type == WeaponType.LASER:
            projectiles = self._shoot_laser(pos, direction, owner_type)
        elif self.weapon_type == WeaponType.PLASMA:
            projectiles = self._shoot_plasma(pos, direction, owner_type)
        elif self.weapon_type == WeaponType.MISSILE:
            projectiles = self._shoot_missile(pos, direction, owner_type)
            
        return projectiles
        
    def _shoot_basic(self, pos: Vector2D, direction: Vector2D, owner_type: str) -> List[Proyectil]:
        """Disparo básico: un proyectil simple."""
        projectile = Proyectil(
            pos.x, pos.y,
            direction.x * self.projectile_speed,
            direction.y * self.projectile_speed,
            damage=int(self.damage), owner_type=owner_type, color=self.projectile_color
        )
        return [projectile]
        
    def _shoot_rapid_fire(self, pos: Vector2D, direction: Vector2D, owner_type: str) -> List[Proyectil]:
        """Disparo rápido: proyectil con velocidad aumentada."""
        speed_mult = 1.5
        projectile = Proyectil(
            pos.x, pos.y,
            direction.x * self.projectile_speed * speed_mult,
            direction.y * self.projectile_speed * speed_mult,
            damage=int(self.damage), owner_type=owner_type, color=self.projectile_color
        )
        return [projectile]
        
    def _shoot_shotgun(self, pos: Vector2D, direction: Vector2D, owner_type: str) -> List[Proyectil]:
        """Escopeta: múltiples proyectiles en un cono."""
        projectiles = []
        num_pellets = 5
        spread_angle = math.pi / 6  # 30 grados de dispersión
        
        for i in range(num_pellets):
            # Calcular ángulo de cada perdigón
            angle_offset = (i - num_pellets // 2) * (spread_angle / num_pellets)
            base_angle = math.atan2(direction.y, direction.x)
            final_angle = base_angle + angle_offset
            
            # Crear proyectil con dirección ajustada
            pellet_dir = Vector2D(math.cos(final_angle), math.sin(final_angle))
            damage_reduced = int(self.damage * 0.7)  # Daño reducido por perdigón
            
            projectile = Proyectil(
                pos.x, pos.y,
                pellet_dir.x * self.projectile_speed * 0.9,
                pellet_dir.y * self.projectile_speed * 0.9,
                damage=int(damage_reduced), owner_type=owner_type, color=self.projectile_color
            )
            projectiles.append(projectile)
            
        return projectiles
        
    def _shoot_laser(self, pos: Vector2D, direction: Vector2D, owner_type: str) -> List[Proyectil]:
        """Láser: proyectil muy rápido y preciso."""
        speed_mult = 3.0
        projectile = Proyectil(
            pos.x, pos.y,
            direction.x * self.projectile_speed * speed_mult,
            direction.y * self.projectile_speed * speed_mult,
            damage=int(self.damage), owner_type=owner_type, color=self.projectile_color
        )
        # Marcar como láser para efectos especiales
        projectile.special_effect = "laser"
        return [projectile]
        
    def _shoot_plasma(self, pos: Vector2D, direction: Vector2D, owner_type: str) -> List[Proyectil]:
        """Plasma: proyectil que causa daño en área."""
        projectile = Proyectil(
            pos.x, pos.y,
            direction.x * self.projectile_speed,
            direction.y * self.projectile_speed,
            damage=int(self.damage), owner_type=owner_type, color=self.projectile_color
        )
        # Marcar como plasma para efectos especiales
        projectile.special_effect = "plasma"
        projectile.radio *= 1.5  # Radio aumentado
        return [projectile]
        
    def _shoot_missile(self, pos: Vector2D, direction: Vector2D, owner_type: str) -> List[Proyectil]:
        """Misil: proyectil explosivo."""
        projectile = Proyectil(
            pos.x, pos.y,
            direction.x * self.projectile_speed * 0.8,
            direction.y * self.projectile_speed * 0.8,
            damage=int(self.damage * 1.5), owner_type=owner_type, color=self.projectile_color
        )
        # Marcar como misil para efectos especiales
        projectile.special_effect = "explosive"
        return [projectile]


class WeaponFactory:
    """Fábrica de armas."""
    
    @staticmethod
    def create_weapon(weapon_type: str) -> Weapon:
        """
        Crea un arma del tipo especificado.
        
        Args:
            weapon_type: Tipo de arma a crear
            
        Returns:
            Instancia del arma
        """
        weapons = {
            WeaponType.BASIC: Weapon(
                WeaponType.BASIC, "Cañón Básico", 25, 0.3, 400.0, 
                COLORS['projectile']
            ),
            WeaponType.RAPID_FIRE: Weapon(
                WeaponType.RAPID_FIRE, "Ametralladora", 18, 0.15, 450.0,
                (255, 255, 100), "rapid"
            ),
            WeaponType.SHOTGUN: Weapon(
                WeaponType.SHOTGUN, "Escopeta Plasma", 20, 0.8, 350.0,
                (255, 150, 0), "spread"
            ),
            WeaponType.LASER: Weapon(
                WeaponType.LASER, "Láser de Combate", 35, 0.4, 600.0,
                (0, 255, 255), "precision"
            ),
            WeaponType.PLASMA: Weapon(
                WeaponType.PLASMA, "Cañón de Plasma", 40, 0.6, 300.0,
                (255, 0, 255), "area"
            ),
            WeaponType.MISSILE: Weapon(
                WeaponType.MISSILE, "Lanzamisiles", 60, 1.2, 250.0,
                (255, 100, 0), "explosive"
            )
        }
        
        return weapons.get(weapon_type, weapons[WeaponType.BASIC])


class WeaponUpgrade:
    """Mejora de arma."""
    
    def __init__(self, name: str, description: str, weapon_type: str, 
                 damage_bonus: int = 0, cooldown_reduction: float = 0.0,
                 speed_bonus: float = 0.0):
        """
        Inicializa una mejora de arma.
        
        Args:
            name: Nombre de la mejora
            description: Descripción de la mejora
            weapon_type: Tipo de arma que mejora
            damage_bonus: Bonificación de daño
            cooldown_reduction: Reducción de tiempo de recarga
            speed_bonus: Bonificación de velocidad
        """
        self.name = name
        self.description = description
        self.weapon_type = weapon_type
        self.damage_bonus = damage_bonus
        self.cooldown_reduction = cooldown_reduction
        self.speed_bonus = speed_bonus