"""
Efectos visuales del juego.
Contiene efectos de daño, explosiones, y gráficos de naves espaciales.
"""
import pygame
import math
import random
from typing import List, Tuple
from utils.math import Vector2D
from config.settings import COLORS


class DamageEffect:
    """Efecto visual cuando el jugador recibe daño."""
    
    def __init__(self):
        self.active = False
        self.timer = 0.0
        self.duration = 0.3
        self.shake_intensity = 0
        self.flash_alpha = 0
    
    def trigger(self, intensity: int = 5):
        """Activa el efecto de daño."""
        self.active = True
        self.timer = 0.0
        self.shake_intensity = intensity
        self.flash_alpha = 150
    
    def update(self, dt: float):
        """Actualiza el efecto de daño."""
        if not self.active:
            return
        
        self.timer += dt
        if self.timer >= self.duration:
            self.active = False
            self.shake_intensity = 0
            self.flash_alpha = 0
        else:
            # Reducir intensidad gradualmente
            progress = self.timer / self.duration
            self.shake_intensity = int(5 * (1 - progress))
            self.flash_alpha = int(150 * (1 - progress))
    
    def get_screen_shake(self) -> Tuple[int, int]:
        """Obtiene el desplazamiento de pantalla para el efecto de shake."""
        if not self.active:
            return (0, 0)
        
        shake_x = random.randint(-self.shake_intensity, self.shake_intensity)
        shake_y = random.randint(-self.shake_intensity, self.shake_intensity)
        return (shake_x, shake_y)
    
    def draw_flash(self, screen: pygame.Surface):
        """Dibuja el flash rojo de daño."""
        if not self.active or self.flash_alpha <= 0:
            return
        
        flash_surface = pygame.Surface(screen.get_size())
        flash_surface.set_alpha(self.flash_alpha)
        flash_surface.fill((255, 0, 0))
        screen.blit(flash_surface, (0, 0))


class Spaceship:
    """Representación gráfica de una nave espacial."""
    
    @staticmethod
    def draw_player_ship(screen: pygame.Surface, pos: Vector2D, radius: int, color: Tuple[int, int, int]):
        """Dibuja la nave del jugador con diseño futurista intergaláctico."""
        x, y = int(pos.x), int(pos.y)
        
        # Colores futuristas
        hull_color = (100, 150, 255)      # Azul metálico
        accent_color = (200, 220, 255)    # Azul claro
        energy_color = (0, 255, 200)     # Verde energía
        engine_color = (255, 100, 0)     # Naranja motores
        
        # Cuerpo principal (forma aerodinámica)
        # Fuselaje principal
        main_body = [
            (x, y - radius * 1.2),           # Punta frontal
            (x - radius * 0.3, y - radius * 0.6),  # Lateral superior izq
            (x - radius * 0.8, y),           # Lateral medio izq
            (x - radius * 0.4, y + radius * 0.8),  # Lateral trasero izq
            (x, y + radius * 0.4),           # Centro trasero
            (x + radius * 0.4, y + radius * 0.8),  # Lateral trasero der
            (x + radius * 0.8, y),           # Lateral medio der
            (x + radius * 0.3, y - radius * 0.6),  # Lateral superior der
        ]
        pygame.draw.polygon(screen, hull_color, main_body)
        
        # Alas laterales futuristas
        left_wing = [
            (x - radius * 0.4, y - radius * 0.2),
            (x - radius * 1.1, y + radius * 0.1),
            (x - radius * 0.9, y + radius * 0.4),
            (x - radius * 0.3, y + radius * 0.2)
        ]
        right_wing = [
            (x + radius * 0.4, y - radius * 0.2),
            (x + radius * 1.1, y + radius * 0.1),
            (x + radius * 0.9, y + radius * 0.4),
            (x + radius * 0.3, y + radius * 0.2)
        ]
        pygame.draw.polygon(screen, color, left_wing)
        pygame.draw.polygon(screen, color, right_wing)
        
        # Cabina cristalina (forma diamante)
        cockpit_points = [
            (x, y - radius * 0.8),
            (x - radius * 0.2, y - radius * 0.2),
            (x, y + radius * 0.1),
            (x + radius * 0.2, y - radius * 0.2)
        ]
        pygame.draw.polygon(screen, accent_color, cockpit_points)
        
        # Motores futuristas (círculos con anillos)
        engine_left_x = x - radius * 0.4
        engine_right_x = x + radius * 0.4
        engine_y = y + radius * 0.6
        
        # Motores principales
        pygame.draw.circle(screen, engine_color, (engine_left_x, engine_y), radius // 4)
        pygame.draw.circle(screen, engine_color, (engine_right_x, engine_y), radius // 4)
        
        # Anillos de energía alrededor de motores
        pygame.draw.circle(screen, energy_color, (engine_left_x, engine_y), radius // 3, 2)
        pygame.draw.circle(screen, energy_color, (engine_right_x, engine_y), radius // 3, 2)
        
        # Líneas de energía en el casco
        energy_lines = [
            [(x - radius * 0.1, y - radius * 0.9), (x - radius * 0.1, y + radius * 0.2)],
            [(x + radius * 0.1, y - radius * 0.9), (x + radius * 0.1, y + radius * 0.2)],
            [(x - radius * 0.6, y - radius * 0.3), (x - radius * 0.2, y - radius * 0.1)],
            [(x + radius * 0.6, y - radius * 0.3), (x + radius * 0.2, y - radius * 0.1)]
        ]
        
        for line in energy_lines:
            pygame.draw.line(screen, energy_color, line[0], line[1], 2)
        
        # Detalles adicionales (sensores)
        pygame.draw.circle(screen, (255, 255, 100), (x - radius * 0.6, y - radius * 0.1), 3)
        pygame.draw.circle(screen, (255, 255, 100), (x + radius * 0.6, y - radius * 0.1), 3)
        
        # Contorno general
        pygame.draw.polygon(screen, accent_color, main_body, 2)

    @staticmethod
    def draw_ship_upgrades(screen: pygame.Surface, pos: Vector2D, radius: int, player):
        """
        Dibuja efectos visuales de las mejoras activas en la nave del jugador.
        
        Args:
            screen: Superficie donde dibujar
            pos: Posición de la nave
            radius: Radio de la nave
            player: Objeto jugador con estadísticas
        """
        x, y = int(pos.x), int(pos.y)
        time = pygame.time.get_ticks() * 0.001
        
        # Verificar si existen mejoras visuales
        visual_upgrades = getattr(player, 'visual_upgrades', set())
        
        # Escudo de energía (mejorado con compras de defensa)
        defense_upgrades = 'defense' in visual_upgrades
        base_defense_check = hasattr(player, 'defense') and player.defense > 5
        
        if defense_upgrades or base_defense_check:
            # Intensidad basada en defensa actual y mejoras
            base_intensity = min(1.0, (player.defense - 5) / 10.0) if base_defense_check else 0.5
            upgrade_bonus = 0.8 if defense_upgrades else 0  # Bonus por compra de Blindaje Titanio
            shield_intensity = min(1.0, base_intensity + upgrade_bonus)
            shield_pulse = 0.3 + 0.7 * math.sin(time * 2) * shield_intensity
            
            # Anillos de escudo hexagonales mejorados
            num_rings = 3 if defense_upgrades else 2  # Más anillos con mejoras
            for ring in range(num_rings):
                shield_radius = radius + 10 + ring * 8 + int(shield_pulse * 6)
                shield_alpha = int(120 * shield_pulse * (1 - ring * 0.2))
                
                if shield_alpha > 0:
                    # Hexágono del escudo
                    shield_points = []
                    for i in range(6):
                        angle = i * math.pi / 3 + time * 0.5
                        px = x + math.cos(angle) * shield_radius
                        py = y + math.sin(angle) * shield_radius
                        shield_points.append((px, py))
                    
                    if len(shield_points) >= 3:
                        shield_surf = pygame.Surface((shield_radius * 2 + 20, shield_radius * 2 + 20), pygame.SRCALPHA)
                        adjusted_points = [(px - (x - shield_radius - 10), py - (y - shield_radius - 10)) for px, py in shield_points]
                        # Color mejorado para blindaje titanio
                        shield_color = (0, 255, 200) if defense_upgrades else (0, 200, 255)
                        line_width = 4 if defense_upgrades else 3
                        pygame.draw.polygon(shield_surf, (*shield_color, shield_alpha), adjusted_points, line_width)
                        screen.blit(shield_surf, (x - shield_radius - 10, y - shield_radius - 10))
        
        # Mejoras de armas (mejorado con compras de ataque)
        attack_upgrades = 'attack' in visual_upgrades
        base_attack_check = hasattr(player, 'attack') and player.attack > 15
        
        if attack_upgrades or base_attack_check:
            # Intensidad basada en ataque actual y mejoras
            base_intensity = min(1.0, (player.attack - 15) / 20.0) if base_attack_check else 0.5
            upgrade_bonus = 1.0 if attack_upgrades else 0  # Bonus por Cañones de Plasma
            weapon_intensity = min(1.0, base_intensity + upgrade_bonus)
            weapon_glow = 0.5 + 0.5 * math.sin(time * 6) * weapon_intensity
            
            # Cañones de plasma mejorados
            if attack_upgrades:
                weapon_color = (255, int(100 + 155 * weapon_glow), 255)  # Color plasma
            else:
                weapon_color = (255, int(150 * weapon_glow), 0)  # Color normal
            
            # Puntos de armas en las alas (más si hay mejoras)
            if attack_upgrades:
                weapon_points = [
                    (x - radius * 0.9, y - radius * 0.1),  # Izquierda superior
                    (x + radius * 0.9, y - radius * 0.1),  # Derecha superior
                    (x - radius * 0.7, y + radius * 0.3),  # Izquierda inferior
                    (x + radius * 0.7, y + radius * 0.3),  # Derecha inferior
                ]
            else:
                weapon_points = [
                    (x - radius * 0.8, y + radius * 0.2),  # Izquierda
                    (x + radius * 0.8, y + radius * 0.2),  # Derecha
                ]
            
            for wp_x, wp_y in weapon_points:
                # Núcleo del arma mejorado
                core_size = 6 if attack_upgrades else 4
                pygame.draw.circle(screen, weapon_color, (int(wp_x), int(wp_y)), core_size)
                
                # Anillos de energía mejorados
                max_rings = [8, 12, 16] if attack_upgrades else [6, 8, 10]
                for ring_radius in max_rings:
                    ring_alpha = int(150 * weapon_glow * (1 - (ring_radius - max_rings[0]) / (max_rings[-1] - max_rings[0])))
                    if ring_alpha > 0:
                        ring_surf = pygame.Surface((ring_radius * 2, ring_radius * 2), pygame.SRCALPHA)
                        pygame.draw.circle(ring_surf, (*weapon_color, ring_alpha), (ring_radius, ring_radius), ring_radius, 3)
                        screen.blit(ring_surf, (int(wp_x - ring_radius), int(wp_y - ring_radius)))
                
                # Chispas de energía mejoradas
                num_sparks = 8 if attack_upgrades else 4
                for i in range(num_sparks):
                    spark_angle = time * 4 + i * (2 * math.pi / num_sparks)
                    spark_dist = 15 + math.sin(time * 8) * 4
                    sx = wp_x + math.cos(spark_angle) * spark_dist
                    sy = wp_y + math.sin(spark_angle) * spark_dist
                    spark_color = (255, 0, 255) if attack_upgrades else (255, 255, 0)
                    pygame.draw.circle(screen, spark_color, (int(sx), int(sy)), 2)
        
        # Motor mejorado (con Motores Warp)
        speed_upgrades = 'speed' in visual_upgrades
        base_speed_check = hasattr(player, 'move_speed') and player.move_speed > 200.0
        
        if speed_upgrades or base_speed_check:
            # Intensidad basada en velocidad actual y mejoras
            base_intensity = min(1.0, (player.move_speed - 200.0) / 100.0) if base_speed_check else 0.5
            upgrade_bonus = 1.0 if speed_upgrades else 0  # Bonus por Motores Warp
            speed_intensity = min(1.0, base_intensity + upgrade_bonus)
            engine_pulse = 0.6 + 0.4 * math.sin(time * 10) * speed_intensity
            
            # Motores traseros warp
            if speed_upgrades:
                engine_points = [
                    (x - radius * 0.5, y + radius * 0.7),  # Motor izquierdo principal
                    (x + radius * 0.5, y + radius * 0.7),  # Motor derecho principal
                    (x - radius * 0.2, y + radius * 0.8),  # Motor central izquierdo
                    (x + radius * 0.2, y + radius * 0.8),  # Motor central derecho
                    (x, y + radius * 0.9),                 # Motor central
                ]
            else:
                engine_points = [
                    (x - radius * 0.4, y + radius * 0.6),  # Motor izquierdo
                    (x + radius * 0.4, y + radius * 0.6),  # Motor derecho
                ]
            
            for ex, ey in engine_points:
                # Llama del motor warp
                if speed_upgrades:
                    flame_color = (0, 200, 255)  # Color azul warp
                    warp_glow = (255, 255, 255)  # Brillo blanco warp
                else:
                    flame_color = (255, int(100 + 155 * engine_pulse), 0)  # Color normal
                
                # Núcleo de la llama mejorado
                flame_size = int(8 + engine_pulse * 6) if speed_upgrades else int(6 + engine_pulse * 4)
                pygame.draw.circle(screen, flame_color, (int(ex), int(ey)), flame_size)
                
                if speed_upgrades:
                    # Núcleo brillante warp
                    pygame.draw.circle(screen, warp_glow, (int(ex), int(ey)), flame_size // 2)
                
                # Estela de plasma mejorada
                num_trails = 8 if speed_upgrades else 5
                for i in range(num_trails):
                    trail_y = ey + radius * 0.3 + i * 10
                    trail_alpha = int(255 * engine_pulse * (1 - i * 0.1))
                    trail_width = flame_size - i
                    
                    if trail_alpha > 0 and trail_width > 0:
                        trail_surf = pygame.Surface((trail_width * 2, 6), pygame.SRCALPHA)
                        trail_surf.fill((*flame_color, trail_alpha))
                        screen.blit(trail_surf, (int(ex - trail_width), int(trail_y)))
        
        # Reactor Cuántico (mejoras de HP)
        max_health_upgrades = 'max_health' in visual_upgrades
        if max_health_upgrades or (hasattr(player, 'max_hp') and player.max_hp > 120):
            health_intensity = min(1.0, (player.max_hp - 120) / 160.0) if hasattr(player, 'max_hp') else 0.5
            upgrade_bonus = 1.0 if max_health_upgrades else 0
            final_intensity = min(1.0, health_intensity + upgrade_bonus * 0.8)
            health_pulse = 0.4 + 0.6 * math.sin(time * 2) * final_intensity
            
            # Aura cuántica del reactor
            aura_radius = radius + 20 + int(health_pulse * 10)
            aura_alpha = int(80 * health_pulse)
            
            if aura_alpha > 0:
                # Ondas cuánticas concéntricas
                for wave in range(3):
                    wave_radius = aura_radius - wave * 8
                    wave_alpha = aura_alpha * (1 - wave * 0.3)
                    if wave_alpha > 0:
                        aura_surf = pygame.Surface((wave_radius * 2, wave_radius * 2), pygame.SRCALPHA)
                        if max_health_upgrades:
                            # Color cuántico azul-blanco
                            pygame.draw.circle(aura_surf, (100, 200, 255, int(wave_alpha)), 
                                             (wave_radius, wave_radius), wave_radius, 3)
                        else:
                            # Color verde salud
                            pygame.draw.circle(aura_surf, (0, 255, 100, int(wave_alpha)), 
                                             (wave_radius, wave_radius), wave_radius, 2)
                        screen.blit(aura_surf, (x - wave_radius, y - wave_radius))
        
        # Escudo Deflector (mejoras de invulnerabilidad)
        invulnerability_upgrades = 'invulnerability' in visual_upgrades
        if invulnerability_upgrades:
            deflector_pulse = 0.7 + 0.3 * math.sin(time * 4)
            
            # Campo deflector octogonal
            deflector_radius = radius + 25 + int(deflector_pulse * 8)
            deflector_alpha = int(100 * deflector_pulse)
            
            if deflector_alpha > 0:
                # Puntos del octógono
                deflector_points = []
                for i in range(8):
                    angle = i * math.pi / 4 + time * 0.3
                    px = x + math.cos(angle) * deflector_radius
                    py = y + math.sin(angle) * deflector_radius
                    deflector_points.append((px, py))
                
                # Dibujar campo deflector
                deflector_surf = pygame.Surface((deflector_radius * 2 + 20, deflector_radius * 2 + 20), pygame.SRCALPHA)
                adjusted_points = [(px - (x - deflector_radius - 10), py - (y - deflector_radius - 10)) 
                                 for px, py in deflector_points]
                
                # Líneas de energía doradas
                pygame.draw.polygon(deflector_surf, (255, 215, 0, deflector_alpha), adjusted_points, 4)
                screen.blit(deflector_surf, (x - deflector_radius - 10, y - deflector_radius - 10))
                
                # Partículas de energía en los vértices
                for px, py in deflector_points[::2]:  # Solo cada segundo vértice
                    particle_glow = 0.5 + 0.5 * math.sin(time * 6)
                    pygame.draw.circle(screen, (255, 255, 0), (int(px), int(py)), 
                                     int(3 + particle_glow * 2))
            
            if aura_alpha > 0:
                aura_surf = pygame.Surface((aura_radius * 2, aura_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(aura_surf, (0, 255, 100, aura_alpha), (aura_radius, aura_radius), aura_radius)
                screen.blit(aura_surf, (x - aura_radius, y - aura_radius))
                
                # Partículas curativas flotantes
                for i in range(3):
                    particle_angle = time * 0.8 + i * 2 * math.pi / 3
                    px = x + math.cos(particle_angle) * (radius + 20)
                    py = y + math.sin(particle_angle) * (radius + 20) 
                    pygame.draw.circle(screen, (100, 255, 150), (int(px), int(py)), 2)
    
    @staticmethod
    def draw_enemy_ship(screen: pygame.Surface, pos: Vector2D, radius: int, ship_type: str):
        """Dibuja la nave enemiga con diseño futurista alienígena."""
        x, y = int(pos.x), int(pos.y)
        
        # Colores alienígenas
        alien_hull = (120, 80, 150)      # Púrpura alienígena
        alien_accent = (180, 100, 200)   # Rosa alienígena
        hostile_energy = (255, 50, 50)   # Rojo hostil
        
        # Definir tipos y sus efectos visuales
        if ship_type == "volador":
            # Nave enemiga voladora - Diseño orgánico alienígena
            
            # Cuerpo principal (forma orgánica)
            core_points = [
                (x, y - radius * 1.1),        # Punta frontal
                (x - radius * 0.7, y - radius * 0.4),  # Lateral izq superior
                (x - radius * 0.9, y + radius * 0.2),  # Lateral izq medio
                (x - radius * 0.5, y + radius * 0.8),  # Lateral izq trasero
                (x, y + radius * 0.6),        # Centro trasero
                (x + radius * 0.5, y + radius * 0.8),  # Lateral der trasero
                (x + radius * 0.9, y + radius * 0.2),  # Lateral der medio
                (x + radius * 0.7, y - radius * 0.4),  # Lateral der superior
            ]
            pygame.draw.polygon(screen, alien_hull, core_points)
            
            # Tentáculos/extensiones laterales
            tentacle_left = [
                (x - radius * 0.6, y - radius * 0.2),
                (x - radius * 1.2, y - radius * 0.1),
                (x - radius * 1.1, y + radius * 0.3),
                (x - radius * 0.7, y + radius * 0.1)
            ]
            tentacle_right = [
                (x + radius * 0.6, y - radius * 0.2),
                (x + radius * 1.2, y - radius * 0.1),
                (x + radius * 1.1, y + radius * 0.3),
                (x + radius * 0.7, y + radius * 0.1)
            ]
            pygame.draw.polygon(screen, alien_accent, tentacle_left)
            pygame.draw.polygon(screen, alien_accent, tentacle_right)
            
            # Núcleo de energía (pulsante)
            pulse_size = radius // 3 + int(3 * math.sin(pygame.time.get_ticks() * 0.01))
            pygame.draw.circle(screen, hostile_energy, (x, y), pulse_size)
            
            # Ojos alienígenas
            pygame.draw.circle(screen, (255, 255, 0), (x - radius//4, y - radius//3), radius//8)
            pygame.draw.circle(screen, (255, 255, 0), (x + radius//4, y - radius//3), radius//8)
            
            pygame.draw.polygon(screen, hostile_energy, core_points, 2)
            
        elif ship_type == "elite":
            # Nave enemiga ELITE - Diseño avanzado con cristales
            elite_crystal = (100, 255, 200)    # Cyan cristalino
            elite_energy = (255, 100, 255)     # Magenta energético
            
            # Cuerpo principal cristalino
            body_points = [
                (x, y - radius * 1.2),        # Punta afilada
                (x - radius * 0.5, y - radius * 0.8),
                (x - radius * 0.9, y - radius * 0.2),
                (x - radius * 0.7, y + radius * 0.4),
                (x - radius * 0.3, y + radius * 0.9),
                (x, y + radius * 0.7),
                (x + radius * 0.3, y + radius * 0.9),
                (x + radius * 0.7, y + radius * 0.4),
                (x + radius * 0.9, y - radius * 0.2),
                (x + radius * 0.5, y - radius * 0.8),
            ]
            pygame.draw.polygon(screen, elite_crystal, body_points)
            
            # Cristales de energía laterales
            for side in [-1, 1]:
                crystal_points = [
                    (x + side * radius * 0.8, y - radius * 0.3),
                    (x + side * radius * 1.3, y - radius * 0.1),
                    (x + side * radius * 1.2, y + radius * 0.3),
                    (x + side * radius * 0.7, y + radius * 0.1)
                ]
                pygame.draw.polygon(screen, elite_energy, crystal_points)
            
            # Núcleo de energía triple
            time_offset = pygame.time.get_ticks() * 0.008
            for i in range(3):
                pulse_size = radius // 4 + int(2 * math.sin(time_offset + i * math.pi / 3))
                color_intensity = 150 + int(105 * abs(math.sin(time_offset + i * math.pi / 3)))
                core_color = (color_intensity, 100, 255)
                pygame.draw.circle(screen, core_color, (x + (i-1) * radius//4, y), pulse_size)
            
            pygame.draw.polygon(screen, elite_energy, body_points, 3)
            
        elif ship_type == "berserker":
            # Nave enemiga BERSERKER - Diseño agresivo con llamas
            berserker_flame = (255, 80, 0)     # Naranja llameante
            berserker_core = (255, 200, 0)     # Amarillo ardiente
            
            # Cuerpo afilado y agresivo
            body_points = [
                (x, y - radius * 1.3),        # Punta ultra-afilada
                (x - radius * 0.3, y - radius * 0.9),
                (x - radius * 0.6, y - radius * 0.4),
                (x - radius * 1.0, y + radius * 0.1),
                (x - radius * 0.4, y + radius * 0.8),
                (x, y + radius * 0.5),
                (x + radius * 0.4, y + radius * 0.8),
                (x + radius * 1.0, y + radius * 0.1),
                (x + radius * 0.6, y - radius * 0.4),
                (x + radius * 0.3, y - radius * 0.9),
            ]
            pygame.draw.polygon(screen, berserker_flame, body_points)
            
            # Alas de fuego
            for side in [-1, 1]:
                flame_points = [
                    (x + side * radius * 0.5, y - radius * 0.2),
                    (x + side * radius * 1.4, y),
                    (x + side * radius * 1.1, y + radius * 0.5),
                    (x + side * radius * 0.7, y + radius * 0.2)
                ]
                pygame.draw.polygon(screen, berserker_core, flame_points)
            
            # Efectos de llamas (partículas)
            time_val = pygame.time.get_ticks() * 0.01
            for i in range(6):
                flame_x = x + math.cos(time_val + i) * radius * 0.3
                flame_y = y + math.sin(time_val + i) * radius * 0.3 + radius * 0.7
                flame_size = int(3 + 2 * abs(math.sin(time_val * 2 + i)))
                pygame.draw.circle(screen, berserker_core, (int(flame_x), int(flame_y)), flame_size)
            
            # Núcleo ardiente
            pygame.draw.circle(screen, (255, 255, 255), (x, y), radius//3)
            pygame.draw.circle(screen, berserker_core, (x, y), radius//4)
            
            pygame.draw.polygon(screen, (255, 255, 0), body_points, 2)
            
        elif ship_type == "guardian":
            # Nave enemiga GUARDIAN - Diseño defensivo masivo
            guardian_armor = (80, 120, 160)    # Azul metálico
            guardian_shield = (150, 200, 255)  # Azul escudo
            
            # Cuerpo masivo y blindado
            body_points = [
                (x, y - radius * 0.8),        # Punta roma
                (x - radius * 0.8, y - radius * 0.6),
                (x - radius * 1.1, y - radius * 0.1),
                (x - radius * 1.0, y + radius * 0.4),
                (x - radius * 0.6, y + radius * 0.9),
                (x, y + radius * 0.8),
                (x + radius * 0.6, y + radius * 0.9),
                (x + radius * 1.0, y + radius * 0.4),
                (x + radius * 1.1, y - radius * 0.1),
                (x + radius * 0.8, y - radius * 0.6),
            ]
            pygame.draw.polygon(screen, guardian_armor, body_points)
            
            # Escudo energético rotatorio
            time_val = pygame.time.get_ticks() * 0.005
            for i in range(8):
                angle = time_val + i * math.pi / 4
                shield_x = x + math.cos(angle) * radius * 1.3
                shield_y = y + math.sin(angle) * radius * 1.3
                shield_size = 4 + int(2 * abs(math.sin(time_val * 3 + i)))
                pygame.draw.circle(screen, guardian_shield, (int(shield_x), int(shield_y)), shield_size)
            
            # Torretas defensivas
            for angle_offset in [0, math.pi/2, math.pi, 3*math.pi/2]:
                turret_x = x + math.cos(angle_offset) * radius * 0.6
                turret_y = y + math.sin(angle_offset) * radius * 0.6
                pygame.draw.circle(screen, (200, 200, 200), (int(turret_x), int(turret_y)), radius//6)
                pygame.draw.circle(screen, hostile_energy, (int(turret_x), int(turret_y)), radius//8)
            
            # Núcleo blindado
            pygame.draw.circle(screen, guardian_shield, (x, y), radius//2)
            pygame.draw.circle(screen, guardian_armor, (x, y), radius//3)
            
            pygame.draw.polygon(screen, guardian_shield, body_points, 3)
            
        elif ship_type == "artillero":
            # Nave enemiga artillero - Diseño de artillería pesada
            
            # Cuerpo principal (forma de caza estelar hostil)
            body_points = [
                (x, y - radius * 0.9),        # Punta frontal
                (x - radius * 0.4, y - radius * 0.6),  # Hombro izq
                (x - radius * 0.8, y - radius * 0.1),  # Ala izq
                (x - radius * 0.6, y + radius * 0.7),  # Motor izq
                (x - radius * 0.2, y + radius * 0.5),  # Centro trasero izq
                (x, y + radius * 0.3),        # Centro trasero
                (x + radius * 0.2, y + radius * 0.5),  # Centro trasero der
                (x + radius * 0.6, y + radius * 0.7),  # Motor der
                (x + radius * 0.8, y - radius * 0.1),  # Ala der
                (x + radius * 0.4, y - radius * 0.6),  # Hombro der
            ]
            pygame.draw.polygon(screen, alien_hull, body_points)
            
            # Cañones laterales
            cannon_left = pygame.Rect(x - radius * 0.8 - 3, y - radius * 0.1 - 6, 6, 12)
            cannon_right = pygame.Rect(x + radius * 0.8 - 3, y - radius * 0.1 - 6, 6, 12)
            pygame.draw.rect(screen, hostile_energy, cannon_left)
            pygame.draw.rect(screen, hostile_energy, cannon_right)
            
            # Motores traseros
            pygame.draw.circle(screen, (255, 150, 0), (x - radius//3, y + radius//2), radius//6)
            pygame.draw.circle(screen, (255, 150, 0), (x + radius//3, y + radius//2), radius//6)
            
            # Cabina de mando (angular)
            cockpit_points = [
                (x, y - radius * 0.6),
                (x - radius * 0.2, y - radius * 0.2),
                (x, y),
                (x + radius * 0.2, y - radius * 0.2)
            ]
            pygame.draw.polygon(screen, (150, 150, 200), cockpit_points)
            
            # Detalles hostiles
            pygame.draw.line(screen, hostile_energy, (x - radius//2, y - radius//4), (x + radius//2, y - radius//4), 2)
            
            pygame.draw.polygon(screen, hostile_energy, body_points, 2)
            
        else:  # terrestre (default)
            # Nave enemiga terrestre - Diseño básico
            
            # Cuerpo principal (forma de caza estelar hostil)
            body_points = [
                (x, y - radius * 0.9),        # Punta frontal
                (x - radius * 0.4, y - radius * 0.6),  # Hombro izq
                (x - radius * 0.8, y - radius * 0.1),  # Ala izq
                (x - radius * 0.6, y + radius * 0.7),  # Motor izq
                (x - radius * 0.2, y + radius * 0.5),  # Centro trasero izq
                (x, y + radius * 0.3),        # Centro trasero
                (x + radius * 0.2, y + radius * 0.5),  # Centro trasero der
                (x + radius * 0.6, y + radius * 0.7),  # Motor der
                (x + radius * 0.8, y - radius * 0.1),  # Ala der
                (x + radius * 0.4, y - radius * 0.6),  # Hombro der
            ]
            pygame.draw.polygon(screen, alien_hull, body_points)
            
            # Motores traseros
            pygame.draw.circle(screen, (255, 150, 0), (x - radius//3, y + radius//2), radius//6)
            pygame.draw.circle(screen, (255, 150, 0), (x + radius//3, y + radius//2), radius//6)
            
            # Cabina de mando (angular)
            cockpit_points = [
                (x, y - radius * 0.6),
                (x - radius * 0.2, y - radius * 0.2),
                (x, y),
                (x + radius * 0.2, y - radius * 0.2)
            ]
            pygame.draw.polygon(screen, (150, 150, 200), cockpit_points)
            
            pygame.draw.polygon(screen, hostile_energy, body_points, 2)


class Explosion:
    """Efecto de explosión cuando se destruye una nave."""
    
    def __init__(self, pos: Vector2D, size: int = 20):
        self.pos = pos
        self.size = size
        self.timer = 0.0
        self.duration = 0.5
        self.particles = []
        
        # Crear partículas
        for _ in range(size):
            particle = {
                'pos': Vector2D(pos.x, pos.y),
                'vel': Vector2D(
                    random.uniform(-100, 100),
                    random.uniform(-100, 100)
                ),
                'color': random.choice([COLORS['explosion'], COLORS['yellow'], COLORS['white']]),
                'size': random.randint(2, 6),
                'life': random.uniform(0.3, 0.7)
            }
            self.particles.append(particle)
    
    def update(self, dt: float) -> bool:
        """Actualiza la explosión. Retorna False cuando termine."""
        self.timer += dt
        
        for particle in self.particles[:]:
            particle['pos'].x += particle['vel'].x * dt
            particle['pos'].y += particle['vel'].y * dt
            particle['life'] -= dt
            particle['size'] = max(1, particle['size'] - dt * 10)
            
            if particle['life'] <= 0:
                self.particles.remove(particle)
        
        return len(self.particles) > 0
    
    def draw(self, screen: pygame.Surface):
        """Dibuja la explosión."""
        for particle in self.particles:
            if particle['life'] > 0:
                pygame.draw.circle(
                    screen, 
                    particle['color'], 
                    particle['pos'].to_int_tuple(), 
                    int(particle['size'])
                )


class EngineTrail:
    """Efecto de estela de motor para las naves."""
    
    def __init__(self, ship_pos: Vector2D, ship_radius: int):
        self.particles = []
        self.last_pos = Vector2D(ship_pos.x, ship_pos.y)
        self.ship_radius = ship_radius
    
    def update(self, dt: float, ship_pos: Vector2D, moving: bool):
        """Actualiza las partículas de la estela."""
        # Agregar nuevas partículas si la nave se está moviendo
        if moving and random.random() < 0.7:
            # Posición de los motores
            left_engine = Vector2D(ship_pos.x - self.ship_radius//3, ship_pos.y + self.ship_radius//2)
            right_engine = Vector2D(ship_pos.x + self.ship_radius//3, ship_pos.y + self.ship_radius//2)
            
            for engine_pos in [left_engine, right_engine]:
                particle = {
                    'pos': Vector2D(engine_pos.x, engine_pos.y),
                    'vel': Vector2D(
                        random.uniform(-20, 20),
                        random.uniform(50, 100)
                    ),
                    'life': random.uniform(0.2, 0.4),
                    'size': random.randint(2, 4),
                    'color': random.choice([COLORS['particle'], COLORS['white']])
                }
                self.particles.append(particle)
        
        # Actualizar partículas existentes
        for particle in self.particles[:]:
            particle['pos'].x += particle['vel'].x * dt
            particle['pos'].y += particle['vel'].y * dt
            particle['life'] -= dt
            particle['size'] = max(1, particle['size'] - dt * 8)
            
            if particle['life'] <= 0:
                self.particles.remove(particle)
        
        self.last_pos = Vector2D(ship_pos.x, ship_pos.y)
    
    def draw(self, screen: pygame.Surface):
        """Dibuja las partículas de la estela."""
        for particle in self.particles:
            if particle['life'] > 0:
                alpha = int(255 * (particle['life'] / 0.4))
                color = (*particle['color'][:3], alpha)
                
                # Crear superficie temporal para alpha blending
                temp_surface = pygame.Surface((particle['size']*2, particle['size']*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surface, color, (particle['size'], particle['size']), int(particle['size']))
                screen.blit(temp_surface, (particle['pos'].x - particle['size'], particle['pos'].y - particle['size']))


def draw_explosive_trap(screen: pygame.Surface, pos: Vector2D, radius: int, armed: bool = True):
    """Dibuja una trampa explosiva con forma realista."""
    center = (int(pos.x), int(pos.y))
    
    if armed:
        # Base de la bomba (cilindro)
        base_color = (60, 60, 60)  # Gris oscuro
        pygame.draw.ellipse(screen, base_color, 
                          (center[0] - radius, center[1] - radius//2, 
                           radius * 2, radius))
        
        # Cuerpo principal
        body_color = (40, 40, 40)  # Negro metálico
        pygame.draw.circle(screen, body_color, center, radius - 2)
        
        # Detalles metálicos
        detail_color = (80, 80, 80)
        pygame.draw.circle(screen, detail_color, center, radius - 4, 2)
        
        # Luz de activación (roja parpadeante)
        import time
        if int(time.time() * 3) % 2:  # Parpadeo cada 0.33 segundos
            light_color = (255, 50, 50)
            pygame.draw.circle(screen, light_color, 
                             (center[0] - radius//3, center[1] - radius//3), 3)
        
        # Cables/alambres
        wire_color = (150, 50, 50)  # Rojo oscuro
        pygame.draw.line(screen, wire_color, 
                        (center[0] - radius//2, center[1]), 
                        (center[0] + radius//2, center[1]), 2)
        
        # Fusible/detonador
        fuse_color = (200, 150, 100)
        pygame.draw.circle(screen, fuse_color, 
                          (center[0], center[1] - radius//2), 2)
    else:
        # Trampa desactivada/explotada
        debris_color = (100, 80, 60)
        for i in range(5):
            offset_x = random.randint(-radius, radius)
            offset_y = random.randint(-radius, radius)
            pygame.draw.circle(screen, debris_color, 
                             (center[0] + offset_x, center[1] + offset_y), 2)


def get_stellar_background_color(level: int) -> Tuple[int, int, int]:
    """Obtiene el color de fondo basado en el cuerpo estelar del nivel."""
    from config.settings import STELLAR_BODIES
    if 1 <= level <= len(STELLAR_BODIES):
        return STELLAR_BODIES[level - 1]["bg_color"]
    return (5, 5, 15)  # Color por defecto


def get_stellar_accent_color(level: int) -> Tuple[int, int, int]:
    """Obtiene el color de acento basado en el cuerpo estelar del nivel."""
    from config.settings import STELLAR_BODIES
    if 1 <= level <= len(STELLAR_BODIES):
        return STELLAR_BODIES[level - 1]["accent"]
    return (200, 200, 255)  # Color por defecto


def get_stellar_name(level: int) -> str:
    """Obtiene el nombre del cuerpo estelar del nivel."""
    from config.settings import STELLAR_BODIES
    if 1 <= level <= len(STELLAR_BODIES):
        return STELLAR_BODIES[level - 1]["name"]
    return "Espacio Profundo"


def draw_intergalactic_eye_boss(screen: pygame.Surface, center: Tuple[int, int], 
                               size: int, time: float, weak_points: List = None) -> None:
    """
    Dibuja un jefe con forma de ojo intergaláctico con tentáculos espaciales.
    
    Args:
        screen: Superficie donde dibujar
        center: Centro del jefe (x, y)
        size: Tamaño del jefe
        time: Tiempo actual para animaciones
        weak_points: Lista de puntos débiles del jefe
    """
    x, y = center
    
    # Colores del ojo intergaláctico
    eye_base = (25, 15, 35)       # Base púrpura oscura
    eye_outer = (60, 30, 80)      # Iris exterior
    eye_inner = (120, 60, 150)    # Iris intermedio
    pupil_color = (200, 50, 50)   # Pupila roja brillante
    tentacle_color = (40, 20, 60) # Tentáculos púrpura
    energy_color = (255, 100, 200) # Energía rosa
    
    # Animación de pulsado
    pulse = 1.0 + 0.2 * math.sin(time * 3.0)
    current_size = int(size * pulse)
    
    # Dibujar tentáculos espaciales (8 tentáculos)
    num_tentacles = 8
    for i in range(num_tentacles):
        angle = (i * 2 * math.pi / num_tentacles) + time * 0.5
        
        # Crear tentáculo ondulante
        tentacle_length = current_size * 1.8
        segments = 12
        
        for segment in range(segments):
            t = segment / segments
            
            # Posición base del segmento
            base_x = x + math.cos(angle) * tentacle_length * t
            base_y = y + math.sin(angle) * tentacle_length * t
            
            # Ondulación del tentáculo
            wave_offset = math.sin(time * 2.0 + t * 4.0 + i * 0.5) * 15
            seg_x = base_x + math.cos(angle + math.pi/2) * wave_offset
            seg_y = base_y + math.sin(angle + math.pi/2) * wave_offset
            
            # Grosor que disminuye hacia la punta
            thickness = max(1, int((1 - t) * 8))
            
            # Color que se desvanece
            alpha = int(255 * (1 - t * 0.7))
            color = (*tentacle_color, alpha) if alpha < 255 else tentacle_color
            
            pygame.draw.circle(screen, tentacle_color, (int(seg_x), int(seg_y)), thickness)
            
            # Puntos de energía en los tentáculos
            if segment % 3 == 0 and random.random() < 0.3:
                energy_size = random.randint(1, 3)
                pygame.draw.circle(screen, energy_color, (int(seg_x), int(seg_y)), energy_size)
    
    # Dibujar el ojo principal
    # Base del ojo (más grande)
    pygame.draw.circle(screen, eye_base, (x, y), current_size + 10)
    pygame.draw.circle(screen, eye_outer, (x, y), current_size)
    
    # Iris con efecto de profundidad
    iris_size = int(current_size * 0.7)
    pygame.draw.circle(screen, eye_inner, (x, y), iris_size)
    
    # Agregar textura al iris
    for i in range(8):
        angle = i * math.pi / 4
        inner_x = x + math.cos(angle) * iris_size * 0.3
        inner_y = y + math.sin(angle) * iris_size * 0.3
        outer_x = x + math.cos(angle) * iris_size * 0.8
        outer_y = y + math.sin(angle) * iris_size * 0.8
        pygame.draw.line(screen, eye_outer, (inner_x, inner_y), (outer_x, outer_y), 2)
    
    # Pupila que sigue al jugador (animación)
    pupil_offset = 8
    pupil_x = x + math.cos(time * 0.8) * pupil_offset
    pupil_y = y + math.sin(time * 0.8) * pupil_offset
    pupil_size = int(current_size * 0.3)
    
    pygame.draw.circle(screen, pupil_color, (int(pupil_x), int(pupil_y)), pupil_size)
    
    # Brillo en la pupila
    highlight_x = pupil_x - pupil_size * 0.3
    highlight_y = pupil_y - pupil_size * 0.3
    pygame.draw.circle(screen, (255, 150, 150), (int(highlight_x), int(highlight_y)), 
                      max(1, pupil_size // 4))
    
    # Dibujar puntos débiles si están definidos
    if weak_points:
        for i, weak_point in enumerate(weak_points):
            if not weak_point.is_destroyed:
                weak_pos = weak_point.get_position(Vector2D(x, y))
                
                # Punto débil como un nodo de energía
                weak_color = (255, 255, 100)  # Amarillo brillante
                weak_size = int(weak_point.radius * (1.0 + 0.3 * math.sin(time * 4.0 + i)))
                
                pygame.draw.circle(screen, weak_color, 
                                 (int(weak_pos.x), int(weak_pos.y)), weak_size)
                pygame.draw.circle(screen, (255, 200, 0), 
                                 (int(weak_pos.x), int(weak_pos.y)), weak_size // 2)
    
    # Efectos de energía aleatoria alrededor del ojo
    for _ in range(5):
        if random.random() < 0.4:
            spark_angle = random.random() * 2 * math.pi
            spark_distance = current_size + random.randint(10, 30)
            spark_x = x + math.cos(spark_angle) * spark_distance
            spark_y = y + math.sin(spark_angle) * spark_distance
            spark_size = random.randint(1, 4)
            pygame.draw.circle(screen, energy_color, (int(spark_x), int(spark_y)), spark_size)


def draw_meteorite(screen: pygame.Surface, center: Tuple[int, int], size: int, 
                  rotation: float) -> None:
    """
    Dibuja un meteorito espacial con detalles realistas.
    
    Args:
        screen: Superficie donde dibujar
        center: Centro del meteorito (x, y)
        size: Tamaño del meteorito (1=pequeño, 2=mediano, 3=grande)
        rotation: Ángulo de rotación actual
    """
    x, y = center
    
    # Colores del meteorito
    rock_colors = [
        (60, 40, 30),   # Marrón oscuro
        (80, 50, 35),   # Marrón medio
        (45, 35, 25),   # Marrón muy oscuro
        (70, 45, 30),   # Marrón rojizo
    ]
    
    highlight_color = (120, 80, 60)  # Resaltes
    crater_color = (30, 20, 15)      # Cráteres
    
    # Tamaños según el tipo
    if size == 1:  # Pequeño
        base_radius = 15
        detail_density = 3
    elif size == 2:  # Mediano
        base_radius = 25
        detail_density = 5
    else:  # Grande
        base_radius = 35
        detail_density = 8
    
    # Cuerpo principal del meteorito (irregular)
    import math
    points = []
    num_points = 8 + size * 2
    
    for i in range(num_points):
        angle = (i * 2 * math.pi / num_points) + rotation
        # Variación en el radio para forma irregular
        radius_variation = random.uniform(0.7, 1.3)
        radius = base_radius * radius_variation
        
        point_x = x + math.cos(angle) * radius
        point_y = y + math.sin(angle) * radius
        points.append((point_x, point_y))
    
    # Dibujar el cuerpo principal
    main_color = random.choice(rock_colors)
    pygame.draw.polygon(screen, main_color, points)
    
    # Agregar textura con círculos más pequeños
    for i in range(detail_density):
        detail_angle = rotation + i * 2.5
        detail_distance = random.uniform(0.3, 0.8) * base_radius
        detail_x = x + math.cos(detail_angle) * detail_distance
        detail_y = y + math.sin(detail_angle) * detail_distance
        detail_radius = random.randint(2, base_radius // 4)
        detail_color = random.choice(rock_colors)
        
        pygame.draw.circle(screen, detail_color, (int(detail_x), int(detail_y)), detail_radius)
    
    # Cráteres (círculos más oscuros)
    num_craters = size + 1
    for i in range(num_craters):
        crater_angle = rotation + i * 3.2 + 1.5
        crater_distance = random.uniform(0.2, 0.6) * base_radius
        crater_x = x + math.cos(crater_angle) * crater_distance
        crater_y = y + math.sin(crater_angle) * crater_distance
        crater_radius = random.randint(1, base_radius // 6)
        
        pygame.draw.circle(screen, crater_color, (int(crater_x), int(crater_y)), crater_radius)
    
    # Resaltes de luz (simulando iluminación espacial)
    highlight_angle = rotation + 0.5
    highlight_distance = base_radius * 0.4
    highlight_x = x + math.cos(highlight_angle) * highlight_distance
    highlight_y = y + math.sin(highlight_angle) * highlight_distance
    highlight_radius = max(1, base_radius // 8)
    
    pygame.draw.circle(screen, highlight_color, (int(highlight_x), int(highlight_y)), highlight_radius)
    
    # Partículas de polvo espacial alrededor (efecto de velocidad)
    for i in range(2 + size):
        if random.random() < 0.6:
            dust_angle = rotation + i * 1.8 + random.uniform(-0.5, 0.5)
            dust_distance = base_radius + random.randint(5, 15)
            dust_x = x + math.cos(dust_angle) * dust_distance
            dust_y = y + math.sin(dust_angle) * dust_distance
            dust_size = random.randint(1, 2)
            dust_color = (100, 80, 60)
            
            pygame.draw.circle(screen, dust_color, (int(dust_x), int(dust_y)), dust_size)


def draw_power_up(screen: pygame.Surface, center: Tuple[int, int], power_type: str, 
                 glow_intensity: float) -> None:
    """
    Dibuja un power-up espacial con efectos de brillo azul.
    
    Args:
        screen: Superficie donde dibujar
        center: Centro del power-up (x, y)
        power_type: Tipo de power-up (shield, speed, weapon, repair)
        glow_intensity: Intensidad del brillo (0.0 a 1.0)
    """
    x, y = center
    
    # Colores base azules para ventajas
    base_blue = (0, 100, 255)
    light_blue = (100, 200, 255)
    bright_blue = (200, 230, 255)
    
    # Calcular colores con intensidad de brillo
    glow_color = (
        int(base_blue[0] + (bright_blue[0] - base_blue[0]) * glow_intensity),
        int(base_blue[1] + (bright_blue[1] - base_blue[1]) * glow_intensity),
        int(base_blue[2] + (bright_blue[2] - base_blue[2]) * glow_intensity)
    )
    
    # Efecto de brillo exterior
    for i in range(3):
        glow_radius = 20 + i * 5 + int(glow_intensity * 8)
        glow_alpha = int(30 - i * 8)
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*glow_color, glow_alpha), (glow_radius, glow_radius), glow_radius)
        screen.blit(glow_surf, (x - glow_radius, y - glow_radius))
    
    # Cuerpo principal del power-up
    if power_type == "shield":
        # Escudo de energía - Hexágono
        points = []
        for i in range(6):
            angle = i * math.pi / 3
            px = x + math.cos(angle) * 12
            py = y + math.sin(angle) * 12
            points.append((px, py))
        pygame.draw.polygon(screen, glow_color, points)
        pygame.draw.polygon(screen, bright_blue, points, 2)
        
        # Centro brillante
        pygame.draw.circle(screen, bright_blue, (x, y), 6)
        
    elif power_type == "speed":
        # Impulso de velocidad - Flechas hacia adelante
        arrow_points = [
            (x, y - 10),    # Punta
            (x - 8, y + 5), # Base izq
            (x - 3, y + 5), # Muesca izq
            (x - 3, y + 10), # Base centro izq
            (x + 3, y + 10), # Base centro der
            (x + 3, y + 5),  # Muesca der
            (x + 8, y + 5)   # Base der
        ]
        pygame.draw.polygon(screen, glow_color, arrow_points)
        pygame.draw.polygon(screen, bright_blue, arrow_points, 2)
        
        # Estelas de velocidad
        for i in range(3):
            trail_y = y + 15 + i * 4
            trail_alpha = int(100 - i * 25)
            if trail_alpha > 0:
                pygame.draw.line(screen, (*light_blue, trail_alpha), 
                               (x - 6, trail_y), (x + 6, trail_y), 2)
    
    elif power_type == "weapon":
        # Mejora de armas - Cristal de energía
        crystal_points = [
            (x, y - 12),     # Punta superior
            (x - 6, y - 4),  # Lateral sup izq
            (x - 8, y + 4),  # Lateral inf izq  
            (x - 3, y + 10), # Base izq
            (x + 3, y + 10), # Base der
            (x + 8, y + 4),  # Lateral inf der
            (x + 6, y - 4)   # Lateral sup der
        ]
        pygame.draw.polygon(screen, glow_color, crystal_points)
        pygame.draw.polygon(screen, bright_blue, crystal_points, 2)
        
        # Líneas de energía internas
        pygame.draw.line(screen, bright_blue, (x - 4, y - 2), (x + 4, y + 8), 2)
        pygame.draw.line(screen, bright_blue, (x + 4, y - 2), (x - 4, y + 8), 2)
        
    elif power_type == "repair":
        # Reparación - Cruz médica futurista
        # Barra horizontal
        pygame.draw.rect(screen, glow_color, (x - 10, y - 3, 20, 6))
        # Barra vertical  
        pygame.draw.rect(screen, glow_color, (x - 3, y - 10, 6, 20))
        
        # Contornos brillantes
        pygame.draw.rect(screen, bright_blue, (x - 10, y - 3, 20, 6), 2)
        pygame.draw.rect(screen, bright_blue, (x - 3, y - 10, 6, 20), 2)
        
        # Centro brillante
        pygame.draw.circle(screen, bright_blue, (x, y), 4)
    
    # Partículas de energía alrededor
    import random
    for i in range(int(3 + glow_intensity * 5)):
        if random.random() < 0.7:
            particle_angle = random.random() * 2 * math.pi
            particle_distance = 18 + random.randint(0, 12)
            particle_x = x + math.cos(particle_angle) * particle_distance
            particle_y = y + math.sin(particle_angle) * particle_distance
            particle_size = random.randint(1, 3)
            pygame.draw.circle(screen, light_blue, (int(particle_x), int(particle_y)), particle_size)


def draw_space_hazard(screen: pygame.Surface, center: Tuple[int, int], hazard_type: str,
                     glow_intensity: float) -> None:
    """
    Dibuja un peligro espacial con efectos de brillo rojo.
    
    Args:
        screen: Superficie donde dibujar
        center: Centro del peligro (x, y)
        hazard_type: Tipo de peligro (shield_drain, speed_reduction, weapon_malfunction, radiation)
        glow_intensity: Intensidad del brillo (0.0 a 1.0)
    """
    x, y = center
    
    # Colores base rojos para desventajas
    base_red = (255, 50, 0)
    dark_red = (150, 20, 0)
    bright_red = (255, 150, 100)
    
    # Calcular colores con intensidad de brillo
    glow_color = (
        int(base_red[0] + (bright_red[0] - base_red[0]) * glow_intensity * 0.3),
        int(base_red[1] + (bright_red[1] - base_red[1]) * glow_intensity),
        int(base_red[2] + (bright_red[2] - base_red[2]) * glow_intensity)
    )
    
    # Efecto de brillo exterior ominoso
    for i in range(4):
        glow_radius = 18 + i * 4 + int(glow_intensity * 6)
        glow_alpha = int(40 - i * 8)
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*glow_color, glow_alpha), (glow_radius, glow_radius), glow_radius)
        screen.blit(glow_surf, (x - glow_radius, y - glow_radius))
    
    # Cuerpo principal del peligro
    if hazard_type == "shield_drain":
        # Drenaje de escudo - Rayos hacia adentro
        pygame.draw.circle(screen, dark_red, (x, y), 10)
        pygame.draw.circle(screen, glow_color, (x, y), 10, 2)
        
        # Rayos de drenaje
        for i in range(8):
            angle = i * math.pi / 4
            inner_x = x + math.cos(angle) * 12
            inner_y = y + math.sin(angle) * 12
            outer_x = x + math.cos(angle) * 20
            outer_y = y + math.sin(angle) * 20
            pygame.draw.line(screen, glow_color, (inner_x, inner_y), (outer_x, outer_y), 2)
    
    elif hazard_type == "speed_reduction":
        # Reducción de velocidad - Espiral hacia adentro
        pygame.draw.circle(screen, dark_red, (x, y), 12)
        pygame.draw.circle(screen, glow_color, (x, y), 12, 2)
        
        # Espiral
        time = pygame.time.get_ticks() * 0.01
        for i in range(20):
            angle = i * 0.5 + time
            radius = 10 - i * 0.4
            if radius > 2:
                spiral_x = x + math.cos(angle) * radius
                spiral_y = y + math.sin(angle) * radius
                pygame.draw.circle(screen, bright_red, (int(spiral_x), int(spiral_y)), 2)
    
    elif hazard_type == "weapon_malfunction":
        # Mal funcionamiento de armas - X de interferencia
        # X principal
        pygame.draw.line(screen, glow_color, (x - 10, y - 10), (x + 10, y + 10), 4)
        pygame.draw.line(screen, glow_color, (x + 10, y - 10), (x - 10, y + 10), 4)
        
        # Marco cuadrado
        pygame.draw.rect(screen, dark_red, (x - 8, y - 8, 16, 16))
        pygame.draw.rect(screen, glow_color, (x - 8, y - 8, 16, 16), 2)
        
        # Chispas de interferencia
        for i in range(4):
            spark_angle = i * math.pi / 2 + glow_intensity * math.pi
            spark_x = x + math.cos(spark_angle) * 15
            spark_y = y + math.sin(spark_angle) * 15
            pygame.draw.circle(screen, bright_red, (int(spark_x), int(spark_y)), 2)
    
    elif hazard_type == "radiation":
        # Radiación - Símbolo de radiación
        pygame.draw.circle(screen, dark_red, (x, y), 8)
        pygame.draw.circle(screen, glow_color, (x, y), 8, 2)
        
        # Símbolo de radiación (3 sectores)
        for i in range(3):
            angle = i * 2 * math.pi / 3
            # Sector exterior
            end_x = x + math.cos(angle) * 12
            end_y = y + math.sin(angle) * 12
            pygame.draw.line(screen, glow_color, (x, y), (end_x, end_y), 3)
            
            # Punto final del sector
            pygame.draw.circle(screen, bright_red, (int(end_x), int(end_y)), 3)
    
    # Partículas de peligro alrededor
    for i in range(int(2 + glow_intensity * 4)):
        if random.random() < 0.6:
            particle_angle = random.random() * 2 * math.pi
            particle_distance = 20 + random.randint(0, 10)
            particle_x = x + math.cos(particle_angle) * particle_distance
            particle_y = y + math.sin(particle_angle) * particle_distance
            particle_size = random.randint(1, 2)
            particle_color = (255, random.randint(0, 100), 0)
            pygame.draw.circle(screen, particle_color, (int(particle_x), int(particle_y)), particle_size)


class ExplosionEffect:
    """Efecto visual de explosión mejorado."""
    
    def __init__(self, x: float, y: float, max_radius: float, duration: float = 1.0):
        self.x = x
        self.y = y
        self.max_radius = max_radius
        self.duration = duration
        self.timer = 0.0
        self.particles = []
        self.shockwave_particles = []
        
        # Generar partículas de explosión
        num_particles = int(max_radius * 0.8)  # Más partículas para explosiones grandes
        for i in range(num_particles):
            angle = random.random() * 2 * math.pi
            speed = random.uniform(50, max_radius * 2)
            particle_x = x
            particle_y = y
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            
            # Diferentes tipos de partículas
            if i < num_particles * 0.6:  # 60% partículas de fuego
                color = (255, random.randint(100, 255), random.randint(0, 50))
                lifetime = random.uniform(0.5, 0.8)
                size = random.uniform(2, 5)
            elif i < num_particles * 0.8:  # 20% partículas de humo
                gray = random.randint(60, 120)
                color = (gray, gray, gray)
                lifetime = random.uniform(0.8, 1.2)
                size = random.uniform(3, 7)
            else:  # 20% chispas brillantes
                color = (255, 255, random.randint(200, 255))
                lifetime = random.uniform(0.3, 0.6)
                size = random.uniform(1, 3)
            
            particle = {
                'x': particle_x,
                'y': particle_y,
                'vel_x': vel_x,
                'vel_y': vel_y,
                'color': color,
                'lifetime': lifetime,
                'max_lifetime': lifetime,
                'size': size,
                'type': 'fire' if i < num_particles * 0.6 else ('smoke' if i < num_particles * 0.8 else 'spark')
            }
            self.particles.append(particle)
        
        # Generar partículas de onda expansiva
        num_shockwave = int(max_radius * 0.2)
        for i in range(num_shockwave):
            angle = (i / num_shockwave) * 2 * math.pi
            particle = {
                'angle': angle,
                'radius': 0.0,
                'max_radius': max_radius * 1.5,
                'speed': max_radius * 4,
                'alpha': 255,
                'color': (255, 200, 0)
            }
            self.shockwave_particles.append(particle)
    
    def update(self, dt: float):
        """Actualiza el efecto de explosión."""
        self.timer += dt
        
        # Actualizar partículas principales
        for particle in self.particles[:]:
            particle['x'] += particle['vel_x'] * dt
            particle['y'] += particle['vel_y'] * dt
            particle['lifetime'] -= dt
            
            # Aplicar fricción y gravedad
            particle['vel_x'] *= 0.98
            particle['vel_y'] *= 0.98
            if particle['type'] == 'smoke':
                particle['vel_y'] -= 20 * dt  # El humo sube
            
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)
        
        # Actualizar partículas de onda expansiva
        for particle in self.shockwave_particles[:]:
            particle['radius'] += particle['speed'] * dt
            particle['alpha'] = int(255 * (1 - particle['radius'] / particle['max_radius']))
            
            if particle['radius'] >= particle['max_radius'] or particle['alpha'] <= 0:
                self.shockwave_particles.remove(particle)
    
    def draw(self, screen: pygame.Surface):
        """Dibuja el efecto de explosión."""
        if not self.is_alive():
            return
        
        # Dibujar onda expansiva (círculos concéntricos)
        progress = self.timer / self.duration
        current_radius = self.max_radius * progress
        
        # Múltiples ondas expansivas
        for wave in range(3):
            wave_radius = current_radius - wave * 10
            if wave_radius > 0:
                alpha = int(100 * (1 - progress) * (1 - wave * 0.3))
                if alpha > 0:
                    # Crear superficie con alpha para la onda
                    wave_surf = pygame.Surface((wave_radius * 2 + 20, wave_radius * 2 + 20), pygame.SRCALPHA)
                    wave_color = (255, 150 - wave * 40, 0, alpha)
                    pygame.draw.circle(wave_surf, wave_color, (int(wave_radius + 10), int(wave_radius + 10)), int(wave_radius), 3)
                    screen.blit(wave_surf, (self.x - wave_radius - 10, self.y - wave_radius - 10))
        
        # Dibujar partículas de onda expansiva
        for particle in self.shockwave_particles:
            if particle['alpha'] > 0:
                pos_x = self.x + math.cos(particle['angle']) * particle['radius']
                pos_y = self.y + math.sin(particle['angle']) * particle['radius']
                
                surf = pygame.Surface((6, 6), pygame.SRCALPHA)
                color_with_alpha = (*particle['color'], particle['alpha'])
                pygame.draw.circle(surf, color_with_alpha, (3, 3), 3)
                screen.blit(surf, (pos_x - 3, pos_y - 3))
        
        # Dibujar partículas principales
        for particle in self.particles:
            if particle['lifetime'] > 0:
                alpha_ratio = particle['lifetime'] / particle['max_lifetime']
                alpha = int(255 * alpha_ratio)
                current_size = int(particle['size'] * alpha_ratio)
                
                if alpha > 0 and current_size > 0:
                    surf = pygame.Surface((current_size * 2, current_size * 2), pygame.SRCALPHA)
                    
                    # Color con alpha
                    if particle['type'] == 'fire':
                        color = (*particle['color'], alpha)
                    elif particle['type'] == 'smoke':
                        # El humo se vuelve más transparente
                        smoke_alpha = int(alpha * 0.6)
                        color = (*particle['color'], smoke_alpha)
                    else:  # spark
                        color = (*particle['color'], alpha)
                    
                    pygame.draw.circle(surf, color, (current_size, current_size), current_size)
                    screen.blit(surf, (particle['x'] - current_size, particle['y'] - current_size))
        
        # Flash central (durante los primeros momentos)
        if progress < 0.2:
            flash_intensity = (0.2 - progress) / 0.2
            flash_radius = int(self.max_radius * 0.3 * flash_intensity)
            if flash_radius > 0:
                flash_surf = pygame.Surface((flash_radius * 2, flash_radius * 2), pygame.SRCALPHA)
                flash_alpha = int(200 * flash_intensity)
                pygame.draw.circle(flash_surf, (255, 255, 255, flash_alpha), 
                                 (flash_radius, flash_radius), flash_radius)
                screen.blit(flash_surf, (self.x - flash_radius, self.y - flash_radius))
    
    def is_alive(self) -> bool:
        """Verifica si el efecto sigue activo."""
        return self.timer < self.duration or len(self.particles) > 0 or len(self.shockwave_particles) > 0


class ExplosionManager:
    """Gestor de efectos de explosión."""
    
    def __init__(self):
        self.explosions: List[ExplosionEffect] = []
    
    def add_explosion(self, x: float, y: float, radius: float, duration: float = 1.0):
        """Agrega una nueva explosión."""
        explosion = ExplosionEffect(x, y, radius, duration)
        self.explosions.append(explosion)
    
    def update(self, dt: float):
        """Actualiza todas las explosiones."""
        for explosion in self.explosions[:]:
            explosion.update(dt)
            if not explosion.is_alive():
                self.explosions.remove(explosion)
    
    def draw(self, screen: pygame.Surface):
        """Dibuja todas las explosiones."""
        for explosion in self.explosions:
            explosion.draw(screen)
    
    def clear(self):
        """Limpia todas las explosiones."""
        self.explosions.clear()