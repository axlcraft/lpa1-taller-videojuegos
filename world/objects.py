"""
Objetos del mundo del juego.
Contiene todas las clases de objetos recolectables y del entorno.
"""
import math
import pygame
from typing import List, Tuple
from utils.math import Vector2D
from entities.base import Figura
from config.settings import TRAP_RADIUS, TREASURE_RADIUS


class Objeto:
    """Clase base para objetos recolectables (Trampa, Tesoro, Armamento)."""

    def __init__(self, x: float, y: float, name: str):
        """
        Inicializa un objeto.
        
        Args:
            x: Posición X del objeto
            y: Posición Y del objeto
            name: Nombre del objeto
        """
        self.pos = Vector2D(x, y)
        self.name = name


class TrampaExplosiva(Objeto):
    """Trampa explosiva que causa daño en área."""

    def __init__(self, x: float, y: float, alcance: float, dano: int):
        """
        Inicializa una trampa explosiva.
        
        Args:
            x: Posición X de la trampa
            y: Posición Y de la trampa
            alcance: Radio de explosión
            dano: Daño que causa la explosión
        """
        super().__init__(x, y, "TrampaExplosiva")
        self.alcance = alcance
        self.dano = dano
        self.radius = TRAP_RADIUS

    def detonar(self, entities: List[Figura]) -> List[Tuple[Figura, int]]:
        """
        Aplica daño a entidades dentro del alcance.
        
        Args:
            entities: Lista de entidades a verificar
            
        Returns:
            Lista de tuplas (entidad, daño) afectadas por la explosión
        """
        affected = []
        for e in entities:
            dist = (Vector2D(e.pos.x, e.pos.y) - Vector2D(self.pos.x, self.pos.y)).magnitude()
            if dist <= self.alcance + getattr(e, "radio", 0):
                affected.append((e, self.dano))
        return affected


class Tesoro(Objeto):
    """Tesoro recolectable que otorga oro y experiencia."""

    def __init__(self, x: float, y: float, valor: int):
        """
        Inicializa un tesoro.
        
        Args:
            x: Posición X del tesoro
            y: Posición Y del tesoro
            valor: Valor en oro del tesoro
        """
        super().__init__(x, y, "Tesoro")
        self.valor = valor
        self.radius = TREASURE_RADIUS


class ArmamentoDefensa(Objeto):
    """Equipo que mejora las estadísticas del jugador."""

    def __init__(self, x: float, y: float, bonus_atk: int, bonus_def: int, price: int):
        """
        Inicializa un equipamiento.
        
        Args:
            x: Posición X del equipo
            y: Posición Y del equipo
            bonus_atk: Bonus de ataque
            bonus_def: Bonus de defensa
            price: Precio del equipo
        """
        super().__init__(x, y, "Equipo")
        self.bonus_atk = bonus_atk
        self.bonus_def = bonus_def
        self.price = price
        self.radius = 12


class Meteorito(Objeto):
    """Meteorito espacial que causa daño al jugador por contacto."""

    def __init__(self, x: float, y: float, size: int = None):
        """
        Inicializa un meteorito.
        
        Args:
            x: Posición X del meteorito
            y: Posición Y del meteorito  
            size: Tamaño del meteorito (1=pequeño, 2=mediano, 3=grande)
        """
        super().__init__(x, y, "Meteorito")
        import random
        
        # Tamaño aleatorio si no se especifica
        self.size = size or random.randint(1, 3)
        
        # Propiedades según el tamaño
        if self.size == 1:  # Pequeño
            self.radius = 15
            self.damage = 15
            self.speed = 2.0
        elif self.size == 2:  # Mediano
            self.radius = 25
            self.damage = 25
            self.speed = 1.5
        else:  # Grande
            self.radius = 35
            self.damage = 35
            self.speed = 1.0
        
        # Velocidad y dirección aleatoria
        angle = random.random() * 2 * 3.14159
        self.velocity = Vector2D(
            self.speed * (random.random() - 0.5) * 2,
            self.speed * (random.random() - 0.5) * 2
        )
        
        # Rotación
        self.rotation = 0.0
        self.rotation_speed = random.uniform(-2.0, 2.0)
    
    def update(self, dt: float, screen_width: int, screen_height: int):
        """
        Actualiza la posición del meteorito.
        
        Args:
            dt: Delta time
            screen_width: Ancho de la pantalla
            screen_height: Alto de la pantalla
        """
        # Actualizar posición
        self.pos.x += self.velocity.x * dt * 60
        self.pos.y += self.velocity.y * dt * 60
        
        # Actualizar rotación
        self.rotation += self.rotation_speed * dt
        
        # Rebote en los bordes de la pantalla
        if self.pos.x - self.radius <= 0 or self.pos.x + self.radius >= screen_width:
            self.velocity.x *= -0.8  # Reduce velocidad en rebote
        if self.pos.y - self.radius <= 0 or self.pos.y + self.radius >= screen_height:
            self.velocity.y *= -0.8
        
        # Mantener dentro de los límites
        self.pos.x = max(self.radius, min(screen_width - self.radius, self.pos.x))
        self.pos.y = max(self.radius, min(screen_height - self.radius, self.pos.y))
    
    def collides_with(self, other_pos: Vector2D, other_radius: float) -> bool:
        """
        Verifica colisión con otra entidad.
        
        Args:
            other_pos: Posición de la otra entidad
            other_radius: Radio de la otra entidad
            
        Returns:
            True si hay colisión
        """
        distance_sq = (self.pos.x - other_pos.x)**2 + (self.pos.y - other_pos.y)**2
        min_distance = self.radius + other_radius
        return distance_sq <= min_distance**2


# ================================
# POWER-UPS ESPACIALES (VENTAJAS)
# ================================

class PowerUpEspacial(Objeto):
    """Clase base para power-ups espaciales con efectos brillantes."""
    
    def __init__(self, x: float, y: float, power_type: str, duration: float = 10.0):
        super().__init__(x, y, f"PowerUp_{power_type}")
        self.power_type = power_type
        self.duration = duration  # Duración del efecto en segundos
        self.radius = 15
        self.glow_intensity = 0.0  # Para el efecto de brillo
        self.collected = False
        
    def update(self, dt: float):
        """Actualiza el efecto de brillo."""
        import math
        self.glow_intensity = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() * 0.005)
    
    def collides_with(self, other_pos: Vector2D, other_radius: float) -> bool:
        """
        Verifica si este power-up colisiona con otro objeto.
        
        Args:
            other_pos: Posición del otro objeto
            other_radius: Radio del otro objeto
            
        Returns:
            True si hay colisión
        """
        distance_sq = (self.pos.x - other_pos.x)**2 + (self.pos.y - other_pos.y)**2
        min_distance = self.radius + other_radius
        return distance_sq <= min_distance**2


class EscudoEnergia(PowerUpEspacial):
    """Power-up que otorga escudo temporal al jugador."""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, "shield", 15.0)
        self.shield_points = 50  # Puntos de escudo que otorga
        
    def apply_effect(self, player):
        """Aplica el efecto de escudo al jugador."""
        player.shield_hp = getattr(player, 'shield_hp', 0) + self.shield_points
        player.max_shield = max(getattr(player, 'max_shield', 50), self.shield_points)
        return f"¡Escudo de energía activado! +{self.shield_points} puntos de escudo"


class ImpulsoVelocidad(PowerUpEspacial):
    """Power-up que aumenta la velocidad del jugador."""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, "speed", 12.0)
        self.speed_multiplier = 1.5
        
    def apply_effect(self, player):
        """Aplica el efecto de velocidad al jugador."""
        player.speed_boost = self.speed_multiplier
        player.speed_boost_timer = self.duration
        return f"¡Impulso de velocidad activado! Velocidad x{self.speed_multiplier}"


class MejoraArmas(PowerUpEspacial):
    """Power-up que mejora temporalmente las armas."""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, "weapon", 20.0)
        self.damage_bonus = 10
        
    def apply_effect(self, player):
        """Aplica el efecto de mejora de armas."""
        player.weapon_boost = self.damage_bonus
        player.weapon_boost_timer = self.duration
        return f"¡Armas mejoradas! +{self.damage_bonus} de daño"


class ReparacionNano(PowerUpEspacial):
    """Power-up que repara la nave del jugador."""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, "repair", 0.0)  # Efecto instantáneo
        self.repair_amount = 40
        
    def apply_effect(self, player):
        """Aplica el efecto de reparación."""
        old_hp = player.hp
        player.hp = min(player.max_hp, player.hp + self.repair_amount)
        healed = player.hp - old_hp
        return f"¡Nanobots de reparación! +{healed} HP restaurado"


# ================================
# PELIGROS ESPACIALES (DESVENTAJAS)  
# ================================

class PeligroEspacial(Objeto):
    """Clase base para peligros espaciales con efectos rojos."""
    
    def __init__(self, x: float, y: float, hazard_type: str, duration: float = 8.0):
        super().__init__(x, y, f"Hazard_{hazard_type}")
        self.hazard_type = hazard_type
        self.duration = duration
        self.radius = 15
        self.glow_intensity = 0.0
        self.triggered = False
        
    def update(self, dt: float):
        """Actualiza el efecto de brillo rojo."""
        import math
        self.glow_intensity = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() * 0.008)
    
    def collides_with(self, other_pos: Vector2D, other_radius: float) -> bool:
        """
        Verifica si este peligro colisiona con otro objeto.
        
        Args:
            other_pos: Posición del otro objeto
            other_radius: Radio del otro objeto
            
        Returns:
            True si hay colisión
        """
        distance_sq = (self.pos.x - other_pos.x)**2 + (self.pos.y - other_pos.y)**2
        min_distance = self.radius + other_radius
        return distance_sq <= min_distance**2


class DrenajeEscudo(PeligroEspacial):
    """Peligro que drena el escudo del jugador."""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, "shield_drain", 10.0)
        self.drain_amount = 30
        
    def apply_effect(self, player):
        """Aplica el efecto de drenaje de escudo."""
        shield_drained = min(getattr(player, 'shield_hp', 0), self.drain_amount)
        player.shield_hp = max(0, getattr(player, 'shield_hp', 0) - self.drain_amount)
        return f"¡Sistema de escudo comprometido! -{shield_drained} puntos de escudo"


class VirulenciaEspacial(PeligroEspacial):
    """Peligro que reduce la velocidad del jugador."""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, "speed_reduction", 15.0)
        self.speed_penalty = 0.6  # Reduce velocidad al 60%
        
    def apply_effect(self, player):
        """Aplica el efecto de reducción de velocidad."""
        player.speed_penalty = self.speed_penalty
        player.speed_penalty_timer = self.duration
        return "¡Contaminación espacial! Motores comprometidos"


class InterferenciaSistemas(PeligroEspacial):
    """Peligro que causa mal funcionamiento de armas."""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, "weapon_malfunction", 12.0)
        self.damage_penalty = 8
        
    def apply_effect(self, player):
        """Aplica el efecto de mal funcionamiento de armas."""
        player.weapon_malfunction = self.damage_penalty
        player.weapon_malfunction_timer = self.duration
        return f"¡Interferencia en sistemas de armas! -{self.damage_penalty} de daño"


class RadiacionCosmica(PeligroEspacial):
    """Peligro que causa daño continuo al jugador."""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, "radiation", 0.0)  # Efecto instantáneo
        self.damage_amount = 25
        
    def apply_effect(self, player):
        """Aplica daño por radiación."""
        old_hp = player.hp
        damage_dealt = player.receive_damage(self.damage_amount)
        return f"¡Radiación cósmica! -{damage_dealt} HP por exposición"