"""
Boss Enemy Module - Super enemies with laser attacks and weak points.

This module implements boss enemies that appear every 2 levels with:
- Laser beam attacks
- Multiple weak points that must be targeted
- Higher health and defense
- Advanced movement patterns
"""

import math
import random
from typing import List, Optional
from utils.math import Vector2D
from .enemy import Enemigo
from .projectile import Proyectil


class WeakPoint:
    """Represents a weak point on the boss enemy."""
    
    def __init__(self, offset_x: float, offset_y: float, radius: float = 15):
        """
        Initialize weak point.
        
        Args:
            offset_x: X offset from boss center
            offset_y: Y offset from boss center
            radius: Collision radius for weak point
        """
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.radius = radius
        self.is_destroyed = False
        self.hit_points = 3  # Requires 3 hits to destroy
        
    def get_position(self, boss_pos: Vector2D) -> Vector2D:
        """Get absolute position of weak point based on boss position."""
        return Vector2D(boss_pos.x + self.offset_x, boss_pos.y + self.offset_y)
    
    def collides_with_projectile(self, boss_pos: Vector2D, projectile) -> bool:
        """Check if projectile hits this weak point."""
        if self.is_destroyed:
            return False
        
        weak_pos = self.get_position(boss_pos)
        distance = math.sqrt((weak_pos.x - projectile.pos.x)**2 + (weak_pos.y - projectile.pos.y)**2)
        return distance < (self.radius + projectile.radio)
    
    def take_damage(self) -> bool:
        """Apply damage to weak point. Returns True if destroyed."""
        if not self.is_destroyed:
            self.hit_points -= 1
            if self.hit_points <= 0:
                self.is_destroyed = True
                return True
        return False


class BossEnemy(Enemigo):
    """Boss enemy with laser attacks and weak points."""
    
    def __init__(self, x: float, y: float, level: int):
        """
        Initialize boss enemy.
        
        Args:
            x: Initial X position
            y: Initial Y position
            level: Current game level (affects boss strength)
        """
        # Initialize as regular enemy first
        super().__init__(x, y, "boss")
        
        # Override with boss-specific stats that scale with level (escalado agresivo)
        if level <= 10:
            # Escalado normal para niveles 1-10
            hp_bonus = level * 20
            attack_bonus = level * 5
            defense_bonus = level * 2
            speed_bonus = level * 3
        else:
            # Escalado más agresivo para niveles 11-18
            base_hp = 80 + (10 * 20)  # HP at level 10
            base_attack = 25 + (10 * 5)  # Attack at level 10
            base_defense = 8 + (10 * 2)  # Defense at level 10
            base_speed = 30 + (10 * 3)  # Speed at level 10
            
            extra_levels = level - 10
            hp_bonus = (10 * 20) + (extra_levels * 40)  # Double scaling for HP
            attack_bonus = (10 * 5) + (extra_levels * 12)  # 2.4x scaling for attack
            defense_bonus = (10 * 2) + (extra_levels * 5)  # 2.5x scaling for defense
            speed_bonus = (10 * 3) + (extra_levels * 6)  # 2x scaling for speed
            
        self.hp = 80 + hp_bonus
        self.attack = 25 + attack_bonus
        self.defense = 8 + defense_bonus
        self.speed = 30 + speed_bonus
        
        self.level = level
        self.size = 60  # Larger than regular enemies
        self.radius = 30
        
        # Movement pattern
        self.movement_timer = 0
        self.movement_phase = 0
        self.center_x = x
        self.center_y = y
        
        # Laser attack system
        self.laser_cooldown = 0
        self.laser_charge_time = 2.0  # 2 seconds to charge laser
        self.laser_charging = False
        self.laser_charge_timer = 0
        self.last_laser_target = Vector2D(0, 0)
        
        # Weak points - positioned around the boss
        self.weak_points = [
            WeakPoint(-25, -25),  # Top-left
            WeakPoint(25, -25),   # Top-right
            WeakPoint(-25, 25),   # Bottom-left
            WeakPoint(25, 25),    # Bottom-right
        ]
        
        # Boss state
        self.is_defeated = False
        
    def update(self, dt: float, player_pos: Vector2D) -> List[Proyectil]:
        """
        Update boss behavior and return any projectiles created.
        
        Args:
            dt: Delta time in seconds
            player_pos: Player position for targeting
            
        Returns:
            List of projectiles created this frame
        """
        projectiles = []
        
        if self.is_defeated:
            return projectiles
            
        # Update movement pattern
        self._update_movement(dt)
        
        # Update laser system
        projectiles.extend(self._update_laser_system(dt, player_pos))
        
        return projectiles
    
    def _update_movement(self, dt: float):
        """Update boss movement pattern."""
        self.movement_timer += dt
        
        # Circular movement pattern
        angle = self.movement_timer * 0.5  # Slow rotation
        radius = 80
        
        target_x = self.center_x + math.cos(angle) * radius
        target_y = self.center_y + math.sin(angle) * radius
        
        # Move towards target position
        dx = target_x - self.pos.x
        dy = target_y - self.pos.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 5:
            move_speed = self.speed * 0.5  # Slower movement for boss
            self.pos.x += (dx / distance) * move_speed * dt
            self.pos.y += (dy / distance) * move_speed * dt
    
    def _update_laser_system(self, dt: float, player_pos: Vector2D) -> List[Proyectil]:
        """Update laser attack system."""
        projectiles = []
        
        # Update cooldowns
        if self.laser_cooldown > 0:
            self.laser_cooldown -= dt
        
        if self.laser_charging:
            self.laser_charge_timer += dt
            if self.laser_charge_timer >= self.laser_charge_time:
                # Fire laser
                projectiles.extend(self._fire_laser())
                self.laser_charging = False
                self.laser_charge_timer = 0
                self.laser_cooldown = 4.0  # 4 second cooldown between lasers
        
        # Start laser charge if ready
        elif self.laser_cooldown <= 0:
            self._start_laser_charge(player_pos)
        
        return projectiles
    
    def _start_laser_charge(self, player_pos: Vector2D):
        """Start charging a laser attack."""
        self.laser_charging = True
        self.laser_charge_timer = 0
        self.last_laser_target = Vector2D(player_pos.x, player_pos.y)
    
    def _fire_laser(self) -> List[Proyectil]:
        """Fire laser beam attack."""
        projectiles = []
        
        # Create multiple projectiles in a line towards target
        direction = Vector2D(
            self.last_laser_target.x - self.pos.x,
            self.last_laser_target.y - self.pos.y
        ).normalized()
        
        # Create laser beam as multiple fast projectiles
        for i in range(8):  # 8 projectiles for beam effect
            offset = i * 40  # Space projectiles along beam
            proj_pos = Vector2D(
                self.pos.x + direction.x * offset,
                self.pos.y + direction.y * offset
            )
            
            laser_speed = 400.0
            laser_projectile = Proyectil(
                proj_pos.x,
                proj_pos.y,
                direction.x * laser_speed,
                direction.y * laser_speed,
                damage=int(self.attack), owner_type="enemy",
                color=(255, 0, 0)
            )
            laser_projectile.is_laser = True  # Mark as laser for visual effects
            projectiles.append(laser_projectile)
        
        return projectiles
    
    def check_weak_point_hits(self, projectiles: List) -> List:
        """
        Check projectile hits against weak points.
        
        Args:
            projectiles: List of player projectiles
            
        Returns:
            List of projectiles that didn't hit weak points
        """
        remaining_projectiles = []
        
        for projectile in projectiles:
            hit_weak_point = False
            
            for weak_point in self.weak_points:
                if weak_point.collides_with_projectile(self.pos, projectile):
                    if weak_point.take_damage():
                        print(f"¡Punto débil destruido! Quedan {self._remaining_weak_points()} puntos.")
                    hit_weak_point = True
                    break
            
            if not hit_weak_point:
                remaining_projectiles.append(projectile)
        
        # Check if all weak points are destroyed
        if self._remaining_weak_points() == 0:
            self._defeat_boss()
        
        return remaining_projectiles
    
    def _remaining_weak_points(self) -> int:
        """Count remaining weak points."""
        return sum(1 for wp in self.weak_points if not wp.is_destroyed)
    
    def _defeat_boss(self):
        """Handle boss defeat."""
        self.is_defeated = True
        self.hp = 0
        print("¡Boss derrotado! Todos los puntos débiles han sido destruidos.")
    
    def collides_with(self, other) -> bool:
        """Check collision with boss body (not weak points)."""
        if self.is_defeated:
            return False
        
        distance = math.sqrt((self.pos.x - other.pos.x)**2 + (self.pos.y - other.pos.y)**2)
        return distance < (self.radius + getattr(other, 'radio', 15))
    
    def is_charging_laser(self) -> bool:
        """Check if boss is currently charging a laser."""
        return self.laser_charging
    
    def get_laser_charge_progress(self) -> float:
        """Get laser charge progress (0.0 to 1.0)."""
        if not self.laser_charging:
            return 0.0
        return min(self.laser_charge_timer / self.laser_charge_time, 1.0)
    
    def get_weak_points_positions(self) -> List[tuple]:
        """Get positions of all weak points for rendering."""
        positions = []
        for wp in self.weak_points:
            if not wp.is_destroyed:
                pos = wp.get_position(self.pos)
                positions.append((pos.x, pos.y, wp.radius, wp.hit_points))
        return positions