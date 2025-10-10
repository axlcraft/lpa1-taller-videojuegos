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
        
        # Sistema de armas mejorado
        from core.weapon_system import WeaponFactory, WeaponType
        self.current_weapon = WeaponFactory.create_weapon(WeaponType.BASIC)
        
        # Sistema de efectos activos
        self.active_effects = {}
        self.shield = 0
        self.max_shield = 200
        
        # Estadísticas para efectos
        self.base_move_speed = self.move_speed
        self.base_shoot_cooldown = self.shoot_cooldown
        self.base_attack = self.attack

    def update_timers(self, dt: float) -> None:
        """
        Actualiza los temporizadores del jugador.
        
        Args:
            dt: Tiempo transcurrido desde la última actualización
        """
        self._shoot_timer = max(0.0, self._shoot_timer - dt)
        self._inv_timer = max(0.0, self._inv_timer - dt)
        self._super_shot_timer = max(0.0, self._super_shot_timer - dt)
        
        # Actualizar arma
        self.current_weapon.update(dt)
        
        # Actualizar efectos activos
        self._update_active_effects(dt)
        
    def _update_active_effects(self, dt: float) -> None:
        """Actualiza los efectos activos del jugador."""
        expired_effects = []
        
        for effect_type, effect_data in self.active_effects.items():
            effect_data['duration'] -= dt
            if effect_data['duration'] <= 0:
                expired_effects.append(effect_type)
                
        # Remover efectos expirados y revertir sus efectos
        for effect_type in expired_effects:
            self._remove_effect(effect_type)
            
    def _remove_effect(self, effect_type: str) -> None:
        """Remueve un efecto específico."""
        if effect_type in self.active_effects:
            del self.active_effects[effect_type]
            
        # Recalcular estadísticas
        self._recalculate_stats()
        
    def _recalculate_stats(self) -> None:
        """Recalcula las estadísticas basándose en los efectos activos."""
        # Resetear a valores base
        self.move_speed = self.base_move_speed
        self.shoot_cooldown = self.base_shoot_cooldown
        self.attack = self.base_attack
        
        # Aplicar efectos activos
        for effect_type, effect_data in self.active_effects.items():
            value = effect_data['value']
            
            if effect_type == "speed":
                self.move_speed = self.base_move_speed * (1 + value / 100)
            elif effect_type == "rapid_fire":
                self.shoot_cooldown = self.base_shoot_cooldown * (1 - value / 100)
            elif effect_type == "damage":
                self.attack = int(self.base_attack * (1 + value / 100))

    def can_shoot(self) -> bool:
        """Verifica si el jugador puede disparar."""
        return self.current_weapon.can_shoot()

    def shoot(self, target_pos: Vector2D) -> List[Proyectil]:
        """
        Dispara proyectiles hacia la posición objetivo.
        
        Args:
            target_pos: Posición objetivo del disparo
            
        Returns:
            Lista de proyectiles creados
        """
        if not self.can_shoot():
            return []
            
        # Calcular dirección
        dir_vec = Vector2D(target_pos.x - self.pos.x, target_pos.y - self.pos.y)
        direction = dir_vec.normalized()
        
        # Disparar con el arma actual
        projectiles = self.current_weapon.shoot(self.pos, direction, "player")
        
        # Aplicar efectos especiales
        modified_projectiles = []
        for projectile in projectiles:
            # Aplicar bonificación de daño
            projectile.damage = int(projectile.damage * (self.attack / self.base_attack))
            
            # Aplicar efectos de multi-shot
            if "multi_shot" in self.active_effects:
                multi_projectiles = self._create_multi_shot(projectile, direction)
                modified_projectiles.extend(multi_projectiles)
            else:
                modified_projectiles.append(projectile)
                
            # Aplicar efectos especiales
            for effect_type in self.active_effects:
                if effect_type == "penetrating":
                    projectile.special_effect = "penetrating"
                elif effect_type == "explosive":
                    projectile.special_effect = "explosive"
                    
        return modified_projectiles
        
    def _create_multi_shot(self, base_projectile: Proyectil, direction: Vector2D) -> List[Proyectil]:
        """Crea proyectiles múltiples basados en el efecto multi-shot."""
        import math
        projectiles = [base_projectile]
        
        # Crear proyectiles adicionales con ángulos ligeramente diferentes
        angle_spread = math.pi / 12  # 15 grados
        for i in [-1, 1]:  # Izquierda y derecha
            angle = math.atan2(direction.y, direction.x) + (i * angle_spread)
            new_direction = Vector2D(math.cos(angle), math.sin(angle))
            
            extra_projectile = Proyectil(
                base_projectile.pos.x, base_projectile.pos.y,
                new_direction.x * (base_projectile.vel_x**2 + base_projectile.vel_y**2)**0.5,
                new_direction.y * (base_projectile.vel_x**2 + base_projectile.vel_y**2)**0.5,
                int(base_projectile.damage * 0.8), base_projectile.owner_type,
                base_projectile.color
            )
            projectiles.append(extra_projectile)
            
        return projectiles
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
        Recibe daño aplicando defensa, escudo e invulnerabilidad.
        
        Args:
            amount: Cantidad de daño recibido
            
        Returns:
            Daño final aplicado a la salud
        """
        if self._inv_timer > 0:
            return 0
            
        damage_after_defense = max(0, amount - self.defense)
        
        # Aplicar daño al escudo primero
        if self.shield > 0:
            shield_damage = min(self.shield, damage_after_defense)
            self.shield -= shield_damage
            damage_after_defense -= shield_damage
            
        # Aplicar daño restante a la salud
        self.hp -= damage_after_defense
        self._inv_timer = self.invulnerable_time
        
        return damage_after_defense

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
        
    def change_weapon(self, weapon_type: str) -> None:
        """
        Cambia el arma actual del jugador.
        
        Args:
            weapon_type: Tipo de arma a equipar
        """
        from core.weapon_system import WeaponFactory
        self.current_weapon = WeaponFactory.create_weapon(weapon_type)
        
    def add_effect(self, effect_type: str, duration: float, value: int, name: str) -> None:
        """
        Añade un efecto temporal al jugador.
        
        Args:
            effect_type: Tipo de efecto
            duration: Duración del efecto
            value: Valor del efecto
            name: Nombre del efecto
        """
        self.active_effects[effect_type] = {
            'duration': duration,
            'value': value,
            'name': name
        }
        self._recalculate_stats()
        
    def has_effect(self, effect_type: str) -> bool:
        """
        Verifica si el jugador tiene un efecto activo.
        
        Args:
            effect_type: Tipo de efecto a verificar
            
        Returns:
            True si tiene el efecto activo
        """
        return effect_type in self.active_effects
        
    def get_effect_time_remaining(self, effect_type: str) -> float:
        """
        Obtiene el tiempo restante de un efecto.
        
        Args:
            effect_type: Tipo de efecto
            
        Returns:
            Tiempo restante en segundos, 0 si no tiene el efecto
        """
        if effect_type in self.active_effects:
            return self.active_effects[effect_type]['duration']
        return 0.0