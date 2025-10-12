"""
Proyectiles del juego.
Contiene la clase Proyectil para manejar proyectiles disparados por jugadores y enemigos.
"""
import math
import random
import pygame
from typing import Optional, Tuple, List
from entities.base import Figura
from utils.math import Vector2D
from config.settings import PROJECTILE_RADIUS, COLORS


class Particula:
    """Partícula para efectos visuales."""
    
    def __init__(self, x: float, y: float, vel_x: float, vel_y: float, 
                 color: Tuple[int, int, int], lifetime: float, size: float = 2.0):
        self.x = x
        self.y = y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        
    def update(self, dt: float):
        """Actualiza la partícula."""
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        self.lifetime -= dt
        # Reducir velocidad gradualmente
        self.vel_x *= 0.98
        self.vel_y *= 0.98
        
    def draw(self, screen: pygame.Surface):
        """Dibuja la partícula."""
        if self.lifetime > 0:
            # Calcular alpha basado en el tiempo de vida restante
            alpha_ratio = self.lifetime / self.max_lifetime
            alpha = int(255 * alpha_ratio)
            current_size = int(self.size * alpha_ratio)
            
            if current_size > 0 and alpha > 0:
                # Crear superficie con alpha
                surf = pygame.Surface((current_size * 2, current_size * 2), pygame.SRCALPHA)
                color_with_alpha = (*self.color, alpha)
                pygame.draw.circle(surf, color_with_alpha, (current_size, current_size), current_size)
                screen.blit(surf, (self.x - current_size, self.y - current_size))
                
    def is_alive(self) -> bool:
        """Verifica si la partícula sigue viva."""
        return self.lifetime > 0


class Proyectil(Figura):
    """Proyectil disparado por jugadores o enemigos."""

    def __init__(self, x: float, y: float, direction_or_vel_x, vel_y=None, 
                 speed: float = None, damage: int = 10, owner_type: str = "player", 
                 color: Optional[Tuple[int, int, int]] = None):
        """
        Inicializa un proyectil.
        
        Args:
            x: Posición X inicial
            y: Posición Y inicial
            direction_or_vel_x: Vector de dirección (Vector2D) o velocidad X
            vel_y: Velocidad Y del proyectil (si direction_or_vel_x es float)
            speed: Magnitud de la velocidad (si direction_or_vel_x es Vector2D)
            damage: Daño que causa el proyectil
            owner_type: Tipo de dueño ("player" o "enemy")
            color: Color del proyectil
        """
        projectile_color = color if color else COLORS['projectile']
        super().__init__(x, y, PROJECTILE_RADIUS, projectile_color)
        if vel_y is not None:
            # Forma antigua: vel_x, vel_y
            self.vel_x = direction_or_vel_x
            self.vel_y = vel_y
        elif speed is not None and hasattr(direction_or_vel_x, 'x') and hasattr(direction_or_vel_x, 'y'):
            # Forma nueva: dirección y velocidad
            self.vel_x = direction_or_vel_x.x * speed
            self.vel_y = direction_or_vel_x.y * speed
        else:
            raise ValueError("Proyectil requiere vel_x/vel_y o direction+speed")
        self.damage = int(damage)
        self.owner_type = owner_type
        self.lifetime = 3.0  # segundos
        self.special_effect = None  # Para efectos especiales como láser, plasma, etc.
        
        # Efectos visuales mejorados
        self.trail_points: List[Tuple[float, float]] = []  # Puntos del trail
        self.max_trail_length = 8
        self.particles: List[Particula] = []
        self.glow_intensity = 0.0
        self.sparkle_timer = 0.0
        
        # Configuración de efectos según el tipo de proyectil
        if owner_type == "player":
            self.core_color = (0, 255, 255)  # Cyan brillante
            self.trail_color = (0, 150, 255)  # Azul brillante
            self.particle_color = (255, 255, 255)  # Blanco
            self.glow_color = (0, 200, 255)
        else:  # enemy
            self.core_color = (255, 50, 50)  # Rojo brillante
            self.trail_color = (255, 100, 0)  # Naranja
            self.particle_color = (255, 200, 0)  # Amarillo
            self.glow_color = (255, 100, 100)

    def update(self, dt: float) -> None:
        """
        Actualiza la posición del proyectil.
        
        Args:
            dt: Tiempo transcurrido desde la última actualización
        """
        # Guardar posición anterior para el trail
        self.trail_points.append((self.pos.x, self.pos.y))
        if len(self.trail_points) > self.max_trail_length:
            self.trail_points.pop(0)
        
        # Actualizar posición
        self.pos = Vector2D(
            self.pos.x + self.vel_x * dt,
            self.pos.y + self.vel_y * dt
        )
        
        # Actualizar efectos visuales
        self.glow_intensity = 0.5 + 0.5 * abs(math.sin(pygame.time.get_ticks() * 0.01))
        self.sparkle_timer += dt
        
        # Generar partículas de estela
        if len(self.trail_points) > 1:
            # Crear partículas en la estela
            if self.sparkle_timer > 0.05:  # Cada 50ms
                self.sparkle_timer = 0.0
                # Partícula en la posición actual con velocidad perpendicular
                perp_x = -self.vel_y * 0.1
                perp_y = self.vel_x * 0.1
                
                for i in range(2):  # 2 partículas por frame
                    offset_x = (random.random() - 0.5) * 10
                    offset_y = (random.random() - 0.5) * 10
                    part_vel_x = perp_x * (random.random() - 0.5) + offset_x
                    part_vel_y = perp_y * (random.random() - 0.5) + offset_y
                    
                    particle = Particula(
                        self.pos.x + offset_x,
                        self.pos.y + offset_y,
                        part_vel_x,
                        part_vel_y,
                        self.particle_color,
                        0.3 + random.random() * 0.2,  # 0.3-0.5s lifetime
                        1.0 + random.random() * 2.0   # 1-3 pixels
                    )
                    self.particles.append(particle)
        
        # Actualizar partículas
        for particle in self.particles[:]:
            particle.update(dt)
            if not particle.is_alive():
                self.particles.remove(particle)
        
        # Limitar número de partículas para performance
        if len(self.particles) > 20:
            self.particles = self.particles[-20:]
        
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.activo = False
            
    def can_damage_player(self) -> bool:
        """Verifica si el proyectil puede dañar al jugador."""
        return self.owner_type == "enemy"
        
    def can_damage_enemy(self) -> bool:
        """Verifica si el proyectil puede dañar a enemigos."""
        return self.owner_type == "player"
        
    def draw(self, screen: pygame.Surface):
        """Dibuja el proyectil con efectos visuales mejorados."""
        if not self.activo:
            return
            
        # Dibujar partículas primero (fondo)
        for particle in self.particles:
            particle.draw(screen)
        
        # Dibujar trail/estela
        if len(self.trail_points) > 1:
            for i in range(len(self.trail_points) - 1):
                # Calcular alpha basado en la posición en el trail
                alpha_ratio = (i + 1) / len(self.trail_points)
                alpha = int(100 * alpha_ratio)
                
                if alpha > 10:
                    # Crear superficie para el segmento del trail
                    trail_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
                    trail_color = (*self.trail_color, alpha)
                    
                    # Dibujar línea del trail
                    start_pos = (10, 10)
                    end_pos = (int(self.trail_points[i+1][0] - self.trail_points[i][0] + 10),
                              int(self.trail_points[i+1][1] - self.trail_points[i][1] + 10))
                    
                    if abs(end_pos[0] - start_pos[0]) < 15 and abs(end_pos[1] - start_pos[1]) < 15:
                        pygame.draw.line(trail_surf, trail_color, start_pos, end_pos, 
                                       max(1, int(3 * alpha_ratio)))
                        screen.blit(trail_surf, (self.trail_points[i][0] - 10, self.trail_points[i][1] - 10))
        
        # Dibujar glow/halo externo
        glow_radius = int(self.radio * 3 * self.glow_intensity)
        if glow_radius > 0:
            glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            glow_alpha = int(50 * self.glow_intensity)
            
            # Dibujar múltiples círculos para efecto de glow
            for r in range(glow_radius, 0, -2):
                alpha = int(glow_alpha * (1 - r / glow_radius))
                if alpha > 0:
                    glow_color = (*self.glow_color, alpha)
                    pygame.draw.circle(glow_surf, glow_color, 
                                     (glow_radius, glow_radius), r)
            
            screen.blit(glow_surf, (self.pos.x - glow_radius, self.pos.y - glow_radius))
        
        # Dibujar núcleo brillante del proyectil
        # Anillo exterior
        pygame.draw.circle(screen, self.color, 
                          (int(self.pos.x), int(self.pos.y)), 
                          int(self.radio + 1))
        
        # Núcleo central brillante
        core_intensity = int(255 * self.glow_intensity)
        core_color = (min(255, self.core_color[0] + core_intensity // 2),
                     min(255, self.core_color[1] + core_intensity // 2),  
                     min(255, self.core_color[2] + core_intensity // 2))
        
        pygame.draw.circle(screen, core_color,
                          (int(self.pos.x), int(self.pos.y)), 
                          int(self.radio))
        
        # Punto central ultra-brillante
        pygame.draw.circle(screen, (255, 255, 255),
                          (int(self.pos.x), int(self.pos.y)), 
                          max(1, int(self.radio * 0.3)))
        
        # Sparkles/destellos ocasionales
        time = pygame.time.get_ticks() * 0.001
        if math.sin(time * 10) > 0.8:  # Destello ocasional
            for i in range(4):
                angle = i * math.pi / 2 + time * 2
                sparkle_x = self.pos.x + math.cos(angle) * (self.radio + 3)
                sparkle_y = self.pos.y + math.sin(angle) * (self.radio + 3)
                pygame.draw.circle(screen, (255, 255, 255),
                                 (int(sparkle_x), int(sparkle_y)), 1)