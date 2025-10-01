"""
Game Manager - Núcleo del juego.
Contiene la clase GameManager que maneja el bucle principal, eventos, y renderizado.
"""
import pygame
from typing import List, Optional
from entities.player import Jugador
from entities.projectile import Proyectil
from entities.enemy import Enemigo
from entities.boss_enemy import BossEnemy
from world.scene import Escenario
from world.objects import TrampaExplosiva, Tesoro, ArmamentoDefensa, Meteorito
from utils.math import Vector2D
from core.game_states import GameState, Button, InputField, SpaceBackground
from core.visual_effects import DamageEffect, Spaceship, Explosion, EngineTrail, get_stellar_name, draw_explosive_trap, draw_intergalactic_eye_boss, draw_meteorite, draw_power_up, draw_space_hazard
from core.shop import Shop
from core.sound_manager import SoundManager
from core.character_system import CharacterManager, CharacterSelector
from core.floating_text import FloatingTextManager, create_treasure_text, create_item_text
from core.leaderboard import Leaderboard, LeaderboardScreen
from config.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, PLAYER_RADIUS, ENEMY_RADIUS, 
    PROJECTILE_RADIUS, TRAP_RADIUS, TREASURE_RADIUS, XP_PER_KILL, 
    XP_PER_TREASURE_VALUE, COLORS, MAX_LEVELS, ENEMIES_PER_LEVEL,
    TREASURES_PER_LEVEL, TRAPS_PER_LEVEL
)


class GameManager:
    """Gestor principal del juego que maneja el bucle, eventos y renderizado."""

    def __init__(self):
        """Inicializa el gestor del juego."""
        pygame.init()
        pygame.display.set_caption("Odisea En El Espacio by AXL")
        
        # Sistema de pantalla con soporte para pantalla completa
        self.fullscreen = False
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("orbitron", 18)
        self.big_font = pygame.font.SysFont("orbitron", 32)
        self.title_font = pygame.font.SysFont("orbitron", 48)
        self.running = True

        # Estado del juego
        self.state = GameState.MENU
        self.current_level = 1
        self.player_name = ""
        
        # Elementos del menú
        self.space_background = SpaceBackground(150)
        self.start_button = Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 50, 200, 50, "INICIAR BATALLA", self.font)
        self.name_input = InputField(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 50, 300, 40, self.font, "Ingresa tu nombre de piloto...")
        self.leaderboard_button = Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 110, 200, 50, "PUNTUACIONES", self.font)
        self.continue_button = Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 170, 200, 50, "CONTINUAR", self.font)
        
        # Elementos del menú de modo
        self.story_mode_button = Button(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 50, 300, 60, "MODO HISTORIA", self.big_font)
        self.arcade_mode_button = Button(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 50, 300, 60, "MODO ARCADE", self.big_font)
        self.back_to_menu_button = Button(50, SCREEN_HEIGHT - 80, 150, 50, "VOLVER", self.font)
        
        # Elementos del selector de nivel (Arcade)
        self.level_buttons = []
        for i in range(MAX_LEVELS):
            level_num = i + 1
            row = i // 5
            col = i % 5
            x = SCREEN_WIDTH//2 - 200 + col * 80
            y = SCREEN_HEIGHT//2 - 100 + row * 80
            self.level_buttons.append(Button(x, y, 70, 70, f"{level_num}", self.font))
        
        # Variables de modo de juego
        self.game_mode = "story"  # "story" or "arcade"
        self.selected_level = 1
        
        # Efectos visuales
        self.damage_effect = DamageEffect()
        self.damage_effects: List[DamageEffect] = []  # Lista para efectos flotantes múltiples
        self.explosions: List[Explosion] = []
        self.player_engine_trail: Optional[EngineTrail] = None
        
        # Sistema de tienda
        self.shop = Shop(self.font, self.big_font)
        
        # Sistema de audio
        self.sound_manager = SoundManager()
        
        # Variables para controles de audio y pausa
        self.paused = False
        self.show_pause_menu = False
        
        # Botones del menú de pausa
        self.resume_button = Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 100, 200, 50, "REANUDAR", self.font)
        self.toggle_music_button = Button(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 30, 300, 40, "MÚSICA: ON", self.font) 
        self.toggle_sound_button = Button(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 20, 300, 40, "SONIDOS: ON", self.font)
        self.quit_to_menu_button = Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 80, 200, 50, "SALIR AL MENÚ", self.font)
        
        # Sistema de personajes y texto flotante
        self.character_manager = CharacterManager()
        self.character_selector = CharacterSelector(self.font, self.big_font)
        self.floating_text = FloatingTextManager(self.font)
        self.selected_character = None
        
        # Sistema de puntuaciones
        self.leaderboard = Leaderboard()
        self.leaderboard_screen = LeaderboardScreen(self.font, self.big_font, self.leaderboard)
        
        # Elementos del juego
        self.player: Optional[Jugador] = None
        self.scene: Optional[Escenario] = None
        self.projectiles: List[Proyectil] = []
        self.enemy_projectiles: List[Proyectil] = []
        self.score = 0
        self.death_cause = "unknown"  # Causa de muerte del jugador
        
        # Iniciar música del menú
        self.sound_manager.play_menu_music()

    def handle_input(self, dt: float) -> None:
        """
        Maneja la entrada del teclado para el movimiento del jugador.
        Solo funciona durante el estado de juego.
        
        Args:
            dt: Tiempo transcurrido desde la última actualización
        """
        if self.state != GameState.PLAYING or not self.player:
            return
            
        keys = pygame.key.get_pressed()
        move = Vector2D(0, 0)
        if keys[pygame.K_w]:
            move.y -= 1
        if keys[pygame.K_s]:
            move.y += 1
        if keys[pygame.K_a]:
            move.x -= 1
        if keys[pygame.K_d]:
            move.x += 1
        
        if move.x != 0 or move.y != 0:
            norm = move.normalized()
            self.player.pos = Vector2D(
                self.player.pos.x + norm.x * self.player.move_speed * dt,
                self.player.pos.y + norm.y * self.player.move_speed * dt
            )
            # Mantener al jugador dentro de la pantalla (dejando espacio para el HUD)
            self.player.pos.x = max(
                self.player.radio, 
                min(SCREEN_WIDTH - self.player.radio, self.player.pos.x)
            )
            self.player.pos.y = max(
                self.player.radio + 40,  # Evitar el HUD superior
                min(SCREEN_HEIGHT - self.player.radio - 30, self.player.pos.y)  # Evitar la barra de vida
            )

    def toggle_fullscreen(self) -> None:
        """Alterna entre modo ventana y pantalla completa."""
        self.fullscreen = not self.fullscreen
        
        if self.fullscreen:
            # Cambiar a pantalla completa con escalado
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            # Volver a modo ventana
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    def render_scaled_surface(self, surface: pygame.Surface, offset_x: int = 0, offset_y: int = 0) -> None:
        """
        Renderiza una superficie con escalado apropiado para pantalla completa.
        
        Args:
            surface: Superficie a renderizar
            offset_x: Desplazamiento X (para efectos como shake)
            offset_y: Desplazamiento Y (para efectos como shake)
        """
        if self.fullscreen:
            # Escalar la superficie del juego para llenar la pantalla
            screen_width, screen_height = self.screen.get_size()
            
            # Calcular el factor de escala manteniendo la proporción
            scale_x = screen_width / SCREEN_WIDTH
            scale_y = screen_height / SCREEN_HEIGHT
            scale = min(scale_x, scale_y)  # Usar el menor para mantener proporción
            
            # Calcular las dimensiones escaladas
            scaled_width = int(SCREEN_WIDTH * scale)
            scaled_height = int(SCREEN_HEIGHT * scale)
            
            # Escalar la superficie
            scaled_surface = pygame.transform.scale(surface, (scaled_width, scaled_height))
            
            # Centrar en la pantalla
            x_offset = (screen_width - scaled_width) // 2
            y_offset = (screen_height - scaled_height) // 2
            
            # Limpiar pantalla con color negro (letterboxing)
            self.screen.fill((0, 0, 0))
            
            # Dibujar superficie escalada centrada con offset
            self.screen.blit(scaled_surface, (x_offset + offset_x, y_offset + offset_y))
        else:
            # Modo ventana normal
            self.screen.blit(surface, (offset_x, offset_y))
    
    def toggle_pause(self) -> None:
        """Alterna el estado de pausa del juego."""
        if self.state == GameState.PLAYING:
            self.paused = not self.paused
            if self.paused:
                # Pausar música
                self.sound_manager.stop_ambient_music()
            else:
                # Reanudar música
                self.sound_manager.play_level_music()
    
    def handle_pause_events(self, event: pygame.event.Event) -> None:
        """Maneja los eventos del menú de pausa."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.toggle_pause()  # ESC para salir del menú de pausa
            return
        
        # Manejar botones del menú de pausa
        if self.resume_button.handle_event(event):
            self.toggle_pause()
        
        elif self.toggle_music_button.handle_event(event):
            # Toggle música
            self.sound_manager.music_enabled = not self.sound_manager.music_enabled
            if self.sound_manager.music_enabled:
                self.toggle_music_button.text = "MÚSICA: ON"
                if not self.paused:
                    self.sound_manager.play_level_music()
            else:
                self.toggle_music_button.text = "MÚSICA: OFF"
                self.sound_manager.stop_ambient_music()
        
        elif self.toggle_sound_button.handle_event(event):
            # Toggle efectos de sonido
            self.sound_manager.sound_enabled = not self.sound_manager.sound_enabled
            if self.sound_manager.sound_enabled:
                self.toggle_sound_button.text = "SONIDOS: ON"
            else:
                self.toggle_sound_button.text = "SONIDOS: OFF"
        
        elif self.quit_to_menu_button.handle_event(event):
            # Salir al menú principal
            self.paused = False
            self.state = GameState.MENU
            self.sound_manager.play_menu_music()

    def process_events(self) -> None:
        """Procesa todos los eventos de pygame según el estado actual."""
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self.running = False
            
            # Manejar F11 para pantalla completa en cualquier estado
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_F11:
                self.toggle_fullscreen()
            
            # Manejar menú de pausa
            if self.state == GameState.PLAYING and self.paused:
                self.handle_pause_events(ev)
                continue  # No procesar otros eventos mientras está pausado
            
            if self.state == GameState.MENU:
                self.name_input.handle_event(ev)
                if self.start_button.handle_event(ev):
                    if self.name_input.text.strip():
                        self.player_name = self.name_input.text.strip()
                        self.state = GameState.MODE_SELECT
                elif self.leaderboard_button.handle_event(ev):
                    self.state = GameState.LEADERBOARD
                    self.sound_manager.play_leaderboard_music()
                    
            elif self.state == GameState.MODE_SELECT:
                if self.story_mode_button.handle_event(ev):
                    self.game_mode = "story"
                    self.state = GameState.CHARACTER_SELECT
                elif self.arcade_mode_button.handle_event(ev):
                    self.game_mode = "arcade"
                    self.state = GameState.LEVEL_SELECT
                elif self.back_to_menu_button.handle_event(ev):
                    self.state = GameState.MENU
                    self.sound_manager.play_menu_music()
                    
            elif self.state == GameState.LEVEL_SELECT:
                for i, level_button in enumerate(self.level_buttons):
                    if level_button.handle_event(ev):
                        self.selected_level = i + 1
                        self.state = GameState.CHARACTER_SELECT
                if self.back_to_menu_button.handle_event(ev):
                    self.state = GameState.MODE_SELECT
                    
            elif self.state == GameState.LEADERBOARD:
                if ev.type == pygame.KEYDOWN:
                    action = self.leaderboard_screen.handle_input(ev.key)
                    if action == 'menu':
                        self.state = GameState.MENU
                        self.sound_manager.play_menu_music()
                        
            elif self.state == GameState.CHARACTER_SELECT:
                if ev.type == pygame.KEYDOWN:
                    if self.character_selector.handle_input(ev.key, self.sound_manager):
                        # Personaje seleccionado
                        char_type = self.character_selector.get_selected_character()
                        self.selected_character = self.character_manager.get_character(char_type)
                        self.start_game()
                
            elif self.state == GameState.PLAYING:
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    mp = Vector2D(*pygame.mouse.get_pos())
                    if ev.button == 1:
                        # Disparo normal
                        proj = self.player.shoot(mp)
                        if proj:
                            self.projectiles.append(proj)
                            self.sound_manager.play_sound('laser_shot')
                    elif ev.button == 3:
                        # Super disparo (click derecho)
                        super_projs = self.player.super_shoot(mp)
                        if super_projs:
                            self.projectiles.extend(super_projs)
                            self.sound_manager.play_sound('super_shot')
                            print(f"¡SUPER DISPARO! Cargas restantes: {self.player.super_shot_charges}/{self.player.max_super_charges}")
                elif ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_e:
                        # Recoger objetos cercanos
                        self.try_pickup()
                    elif ev.key == pygame.K_q:
                        # Vender primer objeto del inventario
                        self.sell_first_inventory_item()
                    elif ev.key == pygame.K_ESCAPE:
                        self.toggle_pause()
            
            elif self.state == GameState.LEVEL_COMPLETE:
                if self.continue_button.handle_event(ev):
                    self.state = GameState.SHOP
                    self.shop.reset_purchases()
                elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_SPACE:
                    self.state = GameState.SHOP
                    self.shop.reset_purchases()
            
            elif self.state == GameState.SHOP:
                if self.player:
                    item_purchased, continue_pressed, selected_item = self.shop.handle_event(ev, self.player.gold)
                    
                    if item_purchased:
                        self.apply_shop_item(item_purchased)
                        self.player.gold -= item_purchased.price
                        print(f"Comprado: {item_purchased.name}")
                    
                    if continue_pressed:
                        self.next_level()
            
            elif self.state in [GameState.GAME_OVER, GameState.VICTORY]:
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_r:
                        self.restart_game()
                    elif ev.key == pygame.K_ESCAPE:
                        self.state = GameState.MENU

    def try_pickup(self) -> None:
        """Intenta recoger objetos cercanos al jugador."""
        # Recoger tesoros
        picked_treasure = None
        for t in self.scene.treasures:
            if Vector2D(t.pos.x, t.pos.y).__sub__(self.player.pos).magnitude() <= (TREASURE_RADIUS + self.player.radio + 5):
                self.player.gold += t.valor
                self.player.gain_xp(int(t.valor * XP_PER_TREASURE_VALUE))
                picked_treasure = t
                break
        if picked_treasure:
            self.scene.treasures.remove(picked_treasure)
            print(f"Recogiste Tesoro valor {picked_treasure.valor}. Oro: {self.player.gold}")
            # Agregar texto flotante
            treasure_text = create_treasure_text(picked_treasure.valor)
            self.floating_text.add_text(picked_treasure.pos.x, picked_treasure.pos.y, treasure_text, "treasure")

        # Recoger trampas como objetos del inventario
        picked_trap = None
        for tr in self.scene.traps:
            dist = (Vector2D(tr.pos.x, tr.pos.y) - self.player.pos).magnitude()
            if dist <= (tr.radius + self.player.radio + 5):
                self.player.inventory.append(tr)
                picked_trap = tr
                break
        if picked_trap:
            self.scene.traps.remove(picked_trap)
            print("Recogiste una trampa explosiva en el inventario.")
            # Agregar texto flotante
            self.floating_text.add_text(picked_trap.pos.x, picked_trap.pos.y, "Trampa explosiva recogida", "item")

        # Recoger equipamiento del suelo
        picked_item = None
        for it in self.scene.items_ground:
            dist = (Vector2D(it.pos.x, it.pos.y) - self.player.pos).magnitude()
            if dist <= (it.radius + self.player.radio + 5):
                self.player.inventory.append(it)
                picked_item = it
                break
        if picked_item:
            self.scene.items_ground.remove(picked_item)
            print("Recogiste equipo en el suelo.")
            # Agregar texto flotante
            item_text = create_item_text(type(picked_item).__name__)
            self.floating_text.add_text(picked_item.pos.x, picked_item.pos.y, item_text, "equipment")

    def sell_first_inventory_item(self) -> None:
        """Vende el primer objeto del inventario."""
        if not self.player.inventory:
            print("Inventario vacío.")
            return
        
        item = self.player.inventory.pop(0)
        if isinstance(item, ArmamentoDefensa):
            sell_value = item.price // 2
            self.player.gold += sell_value
            print(f"Vendiste {item.name} por {sell_value} oro.")
        elif isinstance(item, TrampaExplosiva):
            self.player.gold += 10
            print("Vendiste una trampa por 10 oro.")
        else:
            self.player.gold += 5
            print("Vendiste un objeto por 5 oro.")

    def start_game(self) -> None:
        """Inicia un nuevo juego."""
        # Set starting level based on mode
        if self.game_mode == "story":
            self.current_level = 1
        else:  # arcade mode
            self.current_level = self.selected_level
            
        self.score = 0
        # Crear jugador con personaje seleccionado
        self.player = Jugador(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, self.player_name, self.selected_character)
        
        # Arcade mode gets infinite credits (lives)
        if self.game_mode == "arcade":
            self.player.lives = 999  # Effectively infinite
            print("¡MODO ARCADE! Créditos infinitos activados.")
            
        self.player_engine_trail = EngineTrail(self.player.pos, self.player.radio)
        self.explosions = []
        self.damage_effect = DamageEffect()
        self.floating_text.clear()  # Limpiar textos anteriores
        self.death_cause = "unknown"  # Resetear causa de muerte
        self.load_level()
        self.state = GameState.PLAYING
        
        # Iniciar música de nivel
        self.sound_manager.play_level_music()
    
    def load_level(self) -> None:
        """Carga el nivel actual."""
        if self.current_level <= MAX_LEVELS:
            difficulty = 1.0 + (self.current_level - 1) * 0.3
            self.scene = Escenario(SCREEN_WIDTH, SCREEN_HEIGHT, difficulty)
            
            # Aplicar tema estelar del nivel
            from core.visual_effects import get_stellar_background_color, get_stellar_accent_color, get_stellar_name
            bg_color = get_stellar_background_color(self.current_level)
            star_color = get_stellar_accent_color(self.current_level)
            stellar_name = get_stellar_name(self.current_level)
            
            # Actualizar fondo con tema del nivel
            self.space_background.set_theme(bg_color, star_color)
            self.space_background.set_planetary_level(self.current_level)
            
            print(f"Explorando {stellar_name}...")
            
            # Check if this is a boss level (every 2 levels)
            is_boss_level = (self.current_level % 2 == 0)
            
            if is_boss_level:
                # Boss levels have fewer regular enemies but spawn a boss
                regular_enemies = max(1, ENEMIES_PER_LEVEL[self.current_level - 1] // 2)
                self.scene.generate(
                    n_enemies=regular_enemies,
                    n_treasures=TREASURES_PER_LEVEL[self.current_level - 1],
                    n_traps=TRAPS_PER_LEVEL[self.current_level - 1],
                    n_meteorites=min(3, 1 + self.current_level // 3),
                    n_power_ups=min(3, 1 + self.current_level // 4),  # Power-ups más raros
                    n_hazards=min(2, 1 + self.current_level // 5)     # Peligros aún más raros
                )
                
                # Spawn boss enemy in center of screen
                boss = BossEnemy(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100, self.current_level)
                self.scene.enemies.append(boss)
                print(f"¡Nivel BOSS {self.current_level} cargado! Boss + {regular_enemies} enemigos regulares")
            else:
                # Regular level
                self.scene.generate(
                    n_enemies=ENEMIES_PER_LEVEL[self.current_level - 1],
                    n_treasures=TREASURES_PER_LEVEL[self.current_level - 1],
                    n_traps=TRAPS_PER_LEVEL[self.current_level - 1],
                    n_meteorites=min(4, 2 + self.current_level // 2),
                    n_power_ups=min(4, 2 + self.current_level // 3),  # Más power-ups en niveles normales
                    n_hazards=min(3, 1 + self.current_level // 4)     # Más peligros gradualmente
                )
                print(f"¡Nivel {self.current_level} cargado! Enemigos: {ENEMIES_PER_LEVEL[self.current_level - 1]}")
            
            self.projectiles = []
    
    def next_level(self) -> None:
        """Avanza al siguiente nivel."""
        self.current_level += 1
        if self.current_level > MAX_LEVELS:
            self.save_final_score()
            self.state = GameState.VICTORY
        else:
            self.load_level()
            self.state = GameState.PLAYING
    
    def restart_game(self) -> None:
        """Reinicia el juego desde el nivel 1."""
        self.start_game()
    
    def apply_shop_item(self, item) -> None:
        """Aplica los efectos de un artículo comprado en la tienda."""
        if not self.player:
            return
        
        if item.item_type == "health":
            self.player.hp = min(self.player.hp + item.bonus_value, 200)  # Cap máximo
            print(f"HP restaurado: +{item.bonus_value}")
        
        elif item.item_type == "max_health":
            self.player.hp += item.bonus_value
            print(f"HP máximo aumentado: +{item.bonus_value}")
        
        elif item.item_type == "attack":
            self.player.attack += item.bonus_value
            print(f"Ataque aumentado: +{item.bonus_value}")
        
        elif item.item_type == "defense":
            self.player.defense += item.bonus_value
            print(f"Defensa aumentada: +{item.bonus_value}")
        
        elif item.item_type == "speed":
            self.player.move_speed += item.bonus_value
            print(f"Velocidad aumentada: +{item.bonus_value}")
        
        elif item.item_type == "invulnerability":
            self.player.invulnerable_time += item.bonus_value / 10  # Convertir a segundos
            print(f"Invulnerabilidad aumentada: +{item.bonus_value/10}s")

    def update(self, dt: float) -> None:
        """
        Actualiza la lógica del juego según el estado actual.
        
        Args:
            dt: Tiempo transcurrido desde la última actualización
        """
        # Actualizar fondo espacial en todos los estados
        self.space_background.update(dt)
        
        # Actualizar efectos visuales y texto flotante
        self.damage_effect.update(dt)
        self.floating_text.update(dt)
        
        # Actualizar explosiones
        for explosion in self.explosions[:]:
            if not explosion.update(dt):
                self.explosions.remove(explosion)
        
        if self.state == GameState.MENU:
            self.name_input.update(dt)
            return
        
        elif self.state == GameState.SHOP:
            return
        
        elif self.state != GameState.PLAYING:
            return
            
        # No actualizar el juego si está pausado
        if self.paused:
            return
        
        # Solo actualizar lógica del juego si estamos jugando
        if not self.player or not self.scene:
            return
            
        # Actualizar temporizadores del jugador
        self.player.update_timers(dt)
        
        # Actualizar estela del motor del jugador
        if self.player_engine_trail:
            keys = pygame.key.get_pressed()
            moving = any([keys[pygame.K_w], keys[pygame.K_s], keys[pygame.K_a], keys[pygame.K_d]])
            self.player_engine_trail.update(dt, self.player.pos, moving)

        # Actualizar proyectiles del jugador
        for p in list(self.projectiles):
            p.update(dt)
            # Eliminar proyectiles fuera de pantalla o inactivos
            if (p.pos.x < -10 or p.pos.x > SCREEN_WIDTH + 10 or 
                p.pos.y < -10 or p.pos.y > SCREEN_HEIGHT + 10) or not p.activo:
                self.projectiles.remove(p)
        
        # Actualizar proyectiles enemigos (láser de boss)
        for ep in list(self.enemy_projectiles):
            ep.update(dt)
            # Eliminar proyectiles enemigos fuera de pantalla o inactivos
            if (ep.pos.x < -50 or ep.pos.x > SCREEN_WIDTH + 50 or 
                ep.pos.y < -50 or ep.pos.y > SCREEN_HEIGHT + 50) or not ep.activo:
                self.enemy_projectiles.remove(ep)
            
            # Colisión proyectil enemigo -> jugador
            dist = (Vector2D(ep.pos.x, ep.pos.y) - self.player.pos).magnitude()
            if dist <= self.player.radio + ep.radio:
                dmg = max(0, ep.damage - self.player.defense)
                dealt = self.player.receive_damage(dmg)
                ep.activo = False
                if ep in self.enemy_projectiles:
                    self.enemy_projectiles.remove(ep)
                
                if dealt > 0:
                    print(f"¡Láser enemigo impacta! {dealt} daño. HP={self.player.hp}")
                    # Activar efecto de daño
                    self.damage_effect.trigger(intensity=min(dealt, 15))
                    # Reproducir sonido de daño
                    self.sound_manager.play_sound('damage')
                    # Establecer causa de muerte si el jugador muere
                    if self.player.hp <= 0:
                        self.death_cause = "boss_laser"

        # Actualizar enemigos y colisiones
        for e in list(self.scene.enemies):
            # Special handling for boss enemies
            if isinstance(e, BossEnemy):
                # Update boss with proper position parameter
                boss_projectiles = e.update(dt, self.player.pos)
                
                # Handle projectile collisions with boss weak points
                self.projectiles = e.check_weak_point_hits(self.projectiles)
                
                # Add boss projectiles to scene (enemy projectiles)
                if not hasattr(self, 'enemy_projectiles'):
                    self.enemy_projectiles = []
                    
                # Play boss laser sound when boss fires
                if boss_projectiles:
                    self.sound_manager.play_sound('boss_laser')
                    
                self.enemy_projectiles.extend(boss_projectiles)
            else:
                # Regular enemy update
                e.update(dt, self.player)
            
            # Colisión proyectil -> enemigo
            for p in list(self.projectiles):
                dist = (Vector2D(e.pos.x, e.pos.y) - Vector2D(p.pos.x, p.pos.y)).magnitude()
                if dist <= e.radio + p.radio:
                    dmg = e.receive_damage(int(p.damage))
                    p.activo = False
                    if p in self.projectiles:
                        try:
                            self.projectiles.remove(p)
                        except ValueError:
                            pass
                    if dmg > 0:
                        print(f"Impacto: {dmg} daño a {e.tipo} (hp restante {e.hp})")
                    if e.hp <= 0:
                        # Check if this is a boss enemy
                        if isinstance(e, BossEnemy):
                            # Boss defeat - bigger explosion and special effects
                            explosion = Explosion(Vector2D(e.pos.x, e.pos.y), 30)
                            self.explosions.append(explosion)
                            
                            # Boss defeat sounds
                            self.sound_manager.play_sound('boss_defeat')
                            self.sound_manager.play_sound('explosion')
                            
                            # Higher rewards for boss
                            self.player.gain_xp(XP_PER_KILL * 5)  # 5x XP for boss
                            self.score += 200  # Bonus score for boss
                            print(f"¡BOSS DERROTADO! XP bonificada: {XP_PER_KILL * 5}")
                        else:
                            # Regular enemy defeat
                            explosion = Explosion(Vector2D(e.pos.x, e.pos.y), 15)
                            self.explosions.append(explosion)
                            
                            # Regular sounds
                            self.sound_manager.play_sound('explosion')
                            self.sound_manager.play_sound('enemy_death')
                            
                            # Regular rewards
                            self.player.gain_xp(XP_PER_KILL)
                            self.score += 30
                        
                        self.scene.enemies.remove(e)
                        
                        # Cargar super disparo
                        ready = self.player.add_kill()
                        if ready:
                            print("¡SUPER DISPARO LISTO! Click derecho para usar.")
                        
                        print(f"Enemigo derrotado. XP ganada. Nivel: {self.player.level} XP:{self.player.xp}")
                    break

            # Colisión enemigo -> jugador (combate cuerpo a cuerpo)
            if e.collides_with(self.player):
                dmg = max(0, e.attack - self.player.defense)
                dealt = self.player.receive_damage(dmg)
                if dealt > 0:
                    print(f"Recibiste {dealt} de daño. HP={self.player.hp}")
                    # Activar efecto de daño
                    self.damage_effect.trigger(intensity=min(dealt, 10))
                    # Reproducir sonido de daño
                    self.sound_manager.play_sound('damage')
                    # Establecer causa de muerte si el jugador muere
                    if self.player.hp <= 0:
                        if isinstance(e, BossEnemy):
                            self.death_cause = "boss_contact"
                        else:
                            self.death_cause = "enemy_contact"
                # Pequeño retroceso
                vec = Vector2D(self.player.pos.x - e.pos.x, self.player.pos.y - e.pos.y).normalized()
                self.player.pos = Vector2D(self.player.pos.x + vec.x * 8, self.player.pos.y + vec.y * 8)

        # Verificar trampas
        for tr in list(self.scene.traps):
            dist = (Vector2D(tr.pos.x, tr.pos.y) - self.player.pos).magnitude()
            if dist <= (tr.radius + self.player.radio):
                # Detonar trampa inmediatamente
                affected = tr.detonar(self.scene.enemies + [self.player])
                for ent, dmg in affected:
                    if isinstance(ent, Jugador):
                        self.player.receive_damage(dmg)
                        self.damage_effect.trigger(intensity=min(dmg, 15))
                        print(f"Trampa explotó: recibiste {dmg}")
                        # Sonidos de explosión y daño
                        self.sound_manager.play_sound('explosion')
                        self.sound_manager.play_sound('damage')
                        # Establecer causa de muerte si el jugador muere
                        if self.player.hp <= 0:
                            self.death_cause = "trap_explosion"
                    else:
                        ent.receive_damage(dmg)
                        if ent.hp <= 0 and ent in self.scene.enemies:
                            self.scene.enemies.remove(ent)
                            self.player.gain_xp(XP_PER_KILL)
                # Eliminar trampa después de detonación
                if tr in self.scene.traps:
                    self.scene.traps.remove(tr)
                self.score -= 10

        # Auto-recolección de tesoros cercanos
        for t in list(self.scene.treasures):
            dist = (Vector2D(t.pos.x, t.pos.y) - self.player.pos).magnitude()
            if dist <= (TREASURE_RADIUS + self.player.radio):
                self.player.gold += t.valor
                self.player.gain_xp(int(t.valor * XP_PER_TREASURE_VALUE))
                print(f"Recolectado tesoro (auto). Valor {t.valor}. Oro:{self.player.gold}")
                self.scene.treasures.remove(t)

        # Actualizar meteoritos y colisiones
        for meteorite in list(self.scene.meteorites):
            meteorite.update(dt, SCREEN_WIDTH, SCREEN_HEIGHT)
            
            # Colisión meteorito -> jugador
            if meteorite.collides_with(self.player.pos, self.player.radio):
                damage = max(0, meteorite.damage - self.player.defense)
                dealt = self.player.receive_damage(damage)
                
                if dealt > 0:
                    print(f"¡Meteorito impacta! {dealt} daño. HP={self.player.hp}")
                    # Activar efecto de daño
                    self.damage_effect.trigger(intensity=min(dealt, 15))
                    # Reproducir sonido de daño
                    self.sound_manager.play_sound('damage')
                    # Crear explosión en la posición del meteorito
                    self.explosions.append(Explosion(Vector2D(meteorite.pos.x, meteorite.pos.y), 30))
                    # Establecer causa de muerte si el jugador muere
                    if self.player.hp <= 0:
                        self.death_cause = "meteorite_crash"
                
                # El meteorito se destruye al impactar
                self.scene.meteorites.remove(meteorite)
            
            # Colisión proyectiles -> meteorito
            for p in list(self.projectiles):
                if meteorite.collides_with(p.pos, p.radio):
                    p.activo = False
                    if p in self.projectiles:
                        self.projectiles.remove(p)
                    
                    # Los meteoritos pequeños se destruyen, los grandes se fragmentan
                    if meteorite.size == 1:
                        # Meteorito pequeño se destruye completamente
                        self.explosions.append(Explosion(Vector2D(meteorite.pos.x, meteorite.pos.y), 20))
                        self.scene.meteorites.remove(meteorite)
                        # Puntos por destruir meteorito
                        self.score += 15
                    else:
                        # Meteorito grande/mediano se fragmenta en 2 pequeños
                        import random
                        self.explosions.append(Explosion(Vector2D(meteorite.pos.x, meteorite.pos.y), 25))
                        
                        # Crear fragmentos
                        for i in range(2):
                            fragment_x = meteorite.pos.x + random.uniform(-20, 20)
                            fragment_y = meteorite.pos.y + random.uniform(-20, 20)
                            fragment = Meteorito(fragment_x, fragment_y, 1)  # Siempre pequeños
                            self.scene.meteorites.append(fragment)
                        
                        # Remover meteorito original
                        self.scene.meteorites.remove(meteorite)
                        # Puntos por fragmentar
                        self.score += 10
                    
                    # Reproducir sonido de explosión
                    self.sound_manager.play_sound('explosion')
                    break  # Solo un proyectil por meteorito

        # Actualizar objetos espaciales (power-ups y peligros)
        self.scene.update_space_objects(dt)
        
        # Colisiones con power-ups (ventajas)
        for power_up in list(self.scene.power_ups):
            if power_up.collides_with(self.player.pos, self.player.radio):
                # Aplicar efecto del power-up
                power_up.apply_effect(self.player)
                
                # Agregar texto flotante para power-up
                self.floating_text.add_text(
                    f"+{power_up.__class__.__name__}", 
                    self.player.pos.x, self.player.pos.y - 20,
                    color=(0, 255, 255)  # Color cian para power-ups
                )
                
                # Remover power-up
                self.scene.power_ups.remove(power_up)
                
                # Sonido de power-up
                self.sound_manager.play_sound('pickup')  # Reutilizar sonido de pickup
                
                # Puntos por recoger power-up
                self.score += 25

        # Colisiones con peligros espaciales (desventajas)
        for hazard in list(self.scene.hazards):
            if hazard.collides_with(self.player.pos, self.player.radio):
                # Aplicar efecto del peligro
                hazard.apply_effect(self.player)
                
                # Agregar texto flotante para peligro
                self.floating_text.add_text(
                    f"-{hazard.__class__.__name__}",
                    self.player.pos.x, self.player.pos.y - 20,
                    color=(255, 100, 0)  # Color rojo-naranja para peligros
                )
                
                # Remover peligro
                self.scene.hazards.remove(hazard)
                
                # Sonido de daño
                self.sound_manager.play_sound('damage')  # Reutilizar sonido de daño
                
                # Puntos negativos por tocar peligro
                self.score = max(0, self.score - 15)

        # Verificar condiciones de victoria/derrota
        if self.player.hp <= 0:
            death_message = self._get_death_message()
            print(f"¡Derrota! {death_message}")
            self.save_final_score()
            self.state = GameState.GAME_OVER
            # Reproducir música de muerte
            self.sound_manager.play_death_music()
        elif not self.scene.enemies:
            print(f"¡Nivel {self.current_level} completado! Todos los enemigos eliminados.")
            self.state = GameState.LEVEL_COMPLETE
            # Reproducir sonido de victoria de nivel
            self.sound_manager.play_sound('level_victory')
            
    def save_final_score(self) -> None:
        """Guarda la puntuación final en el leaderboard."""
        if self.player and self.selected_character:
            character_name = self.selected_character.get('name', 'Nave Desconocida')
            character_type = self.selected_character.get('ship_type', 'unknown')
            is_high_score = self.leaderboard.add_score(
                player_name=self.player_name,
                character_name=character_name,
                character_type=character_type,
                score=self.score,
                level_reached=self.current_level
            )
            if is_high_score:
                print(f"¡Nueva puntuación alta! {self.score} puntos alcanzando nivel {self.current_level}")

    def _get_death_message(self) -> str:
        """Retorna un mensaje específico basado en la causa de muerte."""
        death_messages = {
            "boss_laser": "Fuiste aniquilado por el rayo láser del jefe intergaláctico.",
            "boss_contact": "El jefe alienígena te destruyó en combate directo.",
            "enemy_contact": "Las naves enemigas te derrotaron en batalla.",
            "trap_explosion": "Una trampa explosiva acabó con tu nave.",
            "meteorite_crash": "Te estrellaste contra un meteorito espacial.",
            "unknown": "Tu nave fue destruida en combate."
        }
        return death_messages.get(self.death_cause, death_messages["unknown"])

    def draw_hud(self) -> None:
        """Dibuja la interfaz de usuario (HUD)."""
        if not self.player:
            return
            
        # Fondo del HUD superior
        hud_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 36)
        pygame.draw.rect(self.screen, COLORS['hud_background'], hud_rect)
        
        # Nombre del piloto y nivel del juego
        pilot_text = self.font.render(f"Piloto: {self.player_name}", True, COLORS['yellow'])
        level_text = self.font.render(f"Nivel: {self.current_level}/{MAX_LEVELS}", True, COLORS['white'])
        
        # Nombre del cuerpo estelar actual
        stellar_name = get_stellar_name(self.current_level)
        stellar_text = self.font.render(f"Sector: {stellar_name}", True, COLORS['cyan'])
        
        # Estadísticas del jugador
        hp_text = self.font.render(f"HP: {self.player.hp}", True, COLORS['white'])
        player_lvl_text = self.font.render(f"LVL: {self.player.level}", True, COLORS['white'])
        xp_text = self.font.render(f"XP: {self.player.xp}/{self.player.xp_to_next}", True, COLORS['white'])
        gold_text = self.font.render(f"Oro: {self.player.gold}", True, COLORS['yellow'])
        score_text = self.font.render(f"Puntos: {self.score}", True, COLORS['gray'])
        
        # Información de enemigos restantes
        enemies_left = len(self.scene.enemies) if self.scene else 0
        enemies_text = self.font.render(f"Enemigos: {enemies_left}", True, COLORS['enemy'])

        # Posicionar textos en el HUD
        self.screen.blit(pilot_text, (8, 6))
        self.screen.blit(level_text, (180, 6))
        self.screen.blit(stellar_text, (300, 6))
        self.screen.blit(hp_text, (450, 6))
        self.screen.blit(player_lvl_text, (520, 6))
        self.screen.blit(xp_text, (580, 6))
        self.screen.blit(gold_text, (720, 6))
        self.screen.blit(score_text, (820, 6))
        self.screen.blit(enemies_text, (920, 6))
    
    def draw_hud_on_surface(self, surface: pygame.Surface) -> None:
        """Dibuja el HUD en una superficie específica (para el shake effect)."""
        if not self.player:
            return
            
        # Fondo del HUD superior
        hud_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 36)
        pygame.draw.rect(surface, COLORS['hud_background'], hud_rect)
        
        # Nombre del piloto y nivel del juego
        pilot_text = self.font.render(f"Piloto: {self.player_name}", True, COLORS['yellow'])
        level_text = self.font.render(f"Nivel: {self.current_level}/{MAX_LEVELS}", True, COLORS['white'])
        
        # Nombre del cuerpo estelar actual
        stellar_name = get_stellar_name(self.current_level)
        stellar_text = self.font.render(f"Sector: {stellar_name}", True, COLORS['cyan'])
        
        # Estadísticas del jugador
        hp_text = self.font.render(f"HP: {self.player.hp}", True, COLORS['white'])
        player_lvl_text = self.font.render(f"LVL: {self.player.level}", True, COLORS['white'])
        xp_text = self.font.render(f"XP: {self.player.xp}/{self.player.xp_to_next}", True, COLORS['white'])
        gold_text = self.font.render(f"Oro: {self.player.gold}", True, COLORS['yellow'])
        score_text = self.font.render(f"Puntos: {self.score}", True, COLORS['gray'])
        
        # Información de enemigos restantes
        enemies_left = len(self.scene.enemies) if self.scene else 0
        enemies_text = self.font.render(f"Enemigos: {enemies_left}", True, COLORS['enemy'])

        # Posicionar textos en el HUD
        surface.blit(pilot_text, (8, 6))
        surface.blit(level_text, (180, 6))
        surface.blit(stellar_text, (300, 6))
        surface.blit(hp_text, (450, 6))
        surface.blit(player_lvl_text, (520, 6))
        surface.blit(xp_text, (580, 6))
        surface.blit(gold_text, (720, 6))
        surface.blit(score_text, (820, 6))
        surface.blit(enemies_text, (920, 6))

    def render(self) -> None:
        """Renderiza la pantalla según el estado actual."""
        # Fondo espacial para todos los estados
        self.space_background.draw(self.screen)
        
        if self.state == GameState.MENU:
            self.render_menu()
        elif self.state == GameState.MODE_SELECT:
            self.render_mode_select()
        elif self.state == GameState.LEVEL_SELECT:
            self.render_level_select()
        elif self.state == GameState.PLAYING:
            self.render_game()
            # Renderizar menú de pausa si está pausado
            if self.paused:
                self.render_pause_menu()
        elif self.state == GameState.LEADERBOARD:
            self.render_leaderboard()
        elif self.state == GameState.CHARACTER_SELECT:
            self.render_character_select()
        elif self.state == GameState.LEVEL_COMPLETE:
            self.render_level_complete()
        elif self.state == GameState.SHOP:
            self.render_shop()
        elif self.state == GameState.GAME_OVER:
            self.render_game_over()
        elif self.state == GameState.VICTORY:
            self.render_victory()
        
        pygame.display.flip()
    
    def render_menu(self) -> None:
        """Renderiza el menú principal."""
        # Crear superficie temporal para el menú
        menu_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.space_background.draw(menu_surface)
        
        # Título
        title_text = self.title_font.render("ODISEA EN EL ESPACIO by AXL", True, COLORS['white'])
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//6))
        menu_surface.blit(title_text, title_rect)
        
        # Subtítulo
        subtitle_text = self.font.render("Un juego de acción y supervivencia en el espacio", True, COLORS['gray'])
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//6 + 80))
        menu_surface.blit(subtitle_text, subtitle_rect)
        
        # Campo de nombre
        name_label = self.font.render("Nombre del Piloto:", True, COLORS['white'])
        name_label_rect = name_label.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 90))
        menu_surface.blit(name_label, name_label_rect)
        
        self.name_input.draw(menu_surface)
        self.start_button.draw(menu_surface)
        self.leaderboard_button.draw(menu_surface)
        
        # Instrucciones
        instructions = [
            "CONTROLES:",
            "WASD - Mover nave",
            "Click - Disparar",
            "E - Recoger objetos",
            "Q - Vender objetos"
        ]
        
        for i, instruction in enumerate(instructions):
            color = COLORS['yellow'] if i == 0 else COLORS['light_gray']
            text = self.font.render(instruction, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 120 + i * 20))
            menu_surface.blit(text, text_rect)
        
        # Renderizar con escalado
        self.render_scaled_surface(menu_surface)
    
    def render_mode_select(self) -> None:
        """Renderiza la selección de modo de juego."""
        # Crear superficie temporal
        mode_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.space_background.draw(mode_surface)
        
        # Título
        title = self.title_font.render("SELECCIONA MODO", True, COLORS['white'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 150))
        mode_surface.blit(title, title_rect)
        
        # Botones de modo
        self.story_mode_button.draw(mode_surface)
        self.arcade_mode_button.draw(mode_surface)
        self.back_to_menu_button.draw(mode_surface)
        
        # Descripción de modos
        story_desc = [
            "MODO HISTORIA",
            "Juega del nivel 1 al 10",
            "Progresión completa",
            "Créditos limitados"
        ]
        
        arcade_desc = [
            "MODO ARCADE", 
            "Selecciona cualquier nivel",
            "Créditos infinitos",
            "Práctica libre"
        ]
        
        # Descripción Modo Historia
        for i, desc in enumerate(story_desc):
            color = COLORS['player'] if i == 0 else COLORS['light_gray']
            text = self.font.render(desc, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//4, 300 + i * 25))
            mode_surface.blit(text, text_rect)
        
        # Descripción Modo Arcade
        for i, desc in enumerate(arcade_desc):
            color = COLORS['yellow'] if i == 0 else COLORS['light_gray']
            text = self.font.render(desc, True, color)
            text_rect = text.get_rect(center=(3*SCREEN_WIDTH//4, 300 + i * 25))
            mode_surface.blit(text, text_rect)
        
        # Renderizar con escalado
        self.render_scaled_surface(mode_surface)
    
    def render_level_select(self) -> None:
        """Renderiza el selector de nivel para modo arcade."""
        # Crear superficie temporal
        level_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.space_background.draw(level_surface)
        
        # Título
        title = self.title_font.render("SELECCIONA NIVEL", True, COLORS['white'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 100))
        level_surface.blit(title, title_rect)
        
        # Subtítulo
        subtitle = self.big_font.render("MODO ARCADE", True, COLORS['yellow'])
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH//2, 140))
        level_surface.blit(subtitle, subtitle_rect)
        
        # Botones de nivel
        for i, level_button in enumerate(self.level_buttons):
            level_num = i + 1
            # Highlight boss levels
            if level_num % 2 == 0:  # Boss level
                level_button.color = COLORS['enemy']
                level_button.text_color = COLORS['white']
            else:
                level_button.color = COLORS['button']
                level_button.text_color = COLORS['light_gray']
            
            level_button.draw(level_surface)
            
            # Boss indicator
            if level_num % 2 == 0:
                boss_text = self.font.render("BOSS", True, COLORS['enemy'])
                text_rect = boss_text.get_rect(center=(level_button.rect.centerx, 
                                                     level_button.rect.bottom + 15))
                level_surface.blit(boss_text, text_rect)
        
        # Back button
        self.back_to_menu_button.draw(level_surface)
        
        # Instructions
        inst_text = self.font.render("Selecciona un nivel para comenzar", True, COLORS['white'])
        inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 50))
        level_surface.blit(inst_text, inst_rect)
        
        # Renderizar con escalado
        self.render_scaled_surface(level_surface)
    
    def render_leaderboard(self) -> None:
        """Renderiza la pantalla de puntuaciones."""
        # Renderizar fondo espacial
        self.space_background.draw(self.screen)
        
        # Usar la pantalla de leaderboard
        self.leaderboard_screen.render(self.screen)
    
    def render_character_select(self) -> None:
        """Renderiza la pantalla de selección de personajes."""
        # Renderizar fondo espacial
        self.space_background.draw(self.screen)
        
        # Usar el selector de personajes
        self.character_selector.render(self.screen, SCREEN_WIDTH, SCREEN_HEIGHT)
    
    def render_game(self) -> None:
        """Renderiza el juego en curso."""
        if not self.player or not self.scene:
            return
        
        # Aplicar shake de pantalla si está activo
        shake_x, shake_y = self.damage_effect.get_screen_shake()
        
        # Crear superficie temporal para aplicar el shake
        game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        game_surface.fill(COLORS['space_bg'])  # Fondo temporal
        
        # Dibujar tesoros
        for t in self.scene.treasures:
            pygame.draw.circle(game_surface, COLORS['treasure'], (int(t.pos.x), int(t.pos.y)), TREASURE_RADIUS)
        
        # Dibujar trampas explosivas
        from core.visual_effects import draw_explosive_trap
        for tr in self.scene.traps:
            draw_explosive_trap(game_surface, tr.pos, TRAP_RADIUS, armed=True)
            # Círculo del rango de explosión (sutil)
            try:
                pygame.draw.circle(game_surface, COLORS['trap_range'], (int(tr.pos.x), int(tr.pos.y)), int(tr.alcance), 1)
            except Exception:
                pass
        
        # Dibujar meteoritos
        for meteorite in self.scene.meteorites:
            draw_meteorite(game_surface, (int(meteorite.pos.x), int(meteorite.pos.y)), 
                          meteorite.size, meteorite.rotation)
        
        # Dibujar power-ups (ventajas espaciales)
        for power_up in self.scene.power_ups:
            # Determinar tipo de power-up para el renderizado basado en el nombre de la clase
            class_name = power_up.__class__.__name__
            if "Escudo" in class_name:
                power_type = "shield" 
            elif "Velocidad" in class_name:
                power_type = "speed"
            elif "Armas" in class_name:
                power_type = "weapon"
            elif "Reparacion" in class_name:
                power_type = "repair"
            else:
                power_type = "shield"  # Default
            
            draw_power_up(game_surface, (int(power_up.pos.x), int(power_up.pos.y)), 
                         power_type, power_up.glow_intensity)
        
        # Dibujar peligros espaciales (desventajas)
        for hazard in self.scene.hazards:
            # Determinar tipo de peligro para el renderizado basado en el nombre de la clase
            class_name = hazard.__class__.__name__
            if "Drenaje" in class_name:
                hazard_type = "shield_drain"
            elif "Virulencia" in class_name:
                hazard_type = "speed_reduction" 
            elif "Interferencia" in class_name:
                hazard_type = "weapon_malfunction"
            elif "Radiacion" in class_name:
                hazard_type = "radiation"
            else:
                hazard_type = "radiation"  # Default
            
            draw_space_hazard(game_surface, (int(hazard.pos.x), int(hazard.pos.y)),
                            hazard_type, hazard.glow_intensity)
        
        # Dibujar equipamiento en el suelo
        for it in self.scene.items_ground:
            pygame.draw.rect(game_surface, COLORS['equipment'], pygame.Rect(int(it.pos.x) - 8, int(it.pos.y) - 8, 16, 16))

        # Dibujar estela del motor del jugador
        if self.player_engine_trail:
            self.player_engine_trail.draw(game_surface)
        
        # Dibujar proyectiles del jugador
        for p in self.projectiles:
            pygame.draw.circle(game_surface, p.color, p.pos.to_int_tuple(), p.radio)
            
        # Dibujar proyectiles enemigos (láser)
        for ep in self.enemy_projectiles:
            # Láser con efecto especial
            pygame.draw.circle(game_surface, (255, 0, 0), ep.pos.to_int_tuple(), ep.radio + 2)
            pygame.draw.circle(game_surface, (255, 255, 0), ep.pos.to_int_tuple(), ep.radio)

        # Dibujar enemigos como naves espaciales
        for e in self.scene.enemies:
            if isinstance(e, BossEnemy):
                # Dibujar boss especial
                self._draw_boss_enemy(game_surface, e)
            else:
                # Dibujar enemigo regular
                Spaceship.draw_enemy_ship(game_surface, e.pos, e.radio, e.tipo)
                # Barra de vida del enemigo
                hp_w = int(2 * e.radio * max(0.0, e.hp) / (60 if e.tipo == "terrestre" else 45))
                pygame.draw.rect(game_surface, COLORS['black'], pygame.Rect(int(e.pos.x - e.radio), int(e.pos.y - e.radio - 8), 2 * e.radio, 5))
                pygame.draw.rect(game_surface, COLORS['green'], pygame.Rect(int(e.pos.x - e.radio), int(e.pos.y - e.radio - 8), hp_w, 5))

        # Dibujar jugador como nave espacial
        Spaceship.draw_player_ship(game_surface, self.player.pos, self.player.radio, self.player.color)
        
        # Dibujar efectos visuales de mejoras de la tienda
        Spaceship.draw_ship_upgrades(game_surface, self.player.pos, self.player.radio, self.player)
        
        # Dibujar explosiones
        for explosion in self.explosions:
            explosion.draw(game_surface)
        
        # Barra de vida del jugador
        pygame.draw.rect(game_surface, COLORS['health_bg'], pygame.Rect(10, SCREEN_HEIGHT - 28, 220, 16))
        pygame.draw.rect(game_surface, COLORS['health_green'], pygame.Rect(10, SCREEN_HEIGHT - 28, int(220 * max(0, self.player.hp) / 200), 16))

        # Dibujar HUD
        self.draw_hud_on_surface(game_surface)
        
        # Aplicar shake de pantalla y escalar para pantalla completa si es necesario
        self.render_scaled_surface(game_surface, shake_x, shake_y)
        
        # Dibujar texto flotante (después del shake para que no se vea afectado)
        self.floating_text.render(self.screen)
        
        # Aplicar flash de daño
        self.damage_effect.draw_flash(self.screen)
    
    def render_level_complete(self) -> None:
        """Renderiza la pantalla de nivel completado."""
        # Overlay semi-transparente
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(COLORS['black'])
        self.screen.blit(overlay, (0, 0))
        
        # Mensaje de nivel completado
        title_text = self.big_font.render(f"NIVEL {self.current_level} COMPLETADO", True, COLORS['yellow'])
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
        self.screen.blit(title_text, title_rect)
        
        if self.current_level < MAX_LEVELS:
            next_text = self.font.render(f"Preparándose para el Nivel {self.current_level + 1}...", True, COLORS['white'])
            next_rect = next_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
            self.screen.blit(next_text, next_rect)
            
            self.continue_button.draw(self.screen)
            
            space_text = self.font.render("O presiona ESPACIO para ir a la tienda", True, COLORS['gray'])
            space_rect = space_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 160))
            self.screen.blit(space_text, space_rect)
    
    def render_shop(self) -> None:
        """Renderiza la tienda."""
        if self.player:
            self.shop.draw(self.screen, self.player.gold, self.player_name, self.current_level)
    
    def render_game_over(self) -> None:
        """Renderiza la pantalla de game over."""
        # Overlay semi-transparente
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(COLORS['black'])
        self.screen.blit(overlay, (0, 0))
        
        # Mensaje de derrota
        title_text = self.big_font.render("NAVE DESTRUIDA", True, COLORS['enemy'])
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80))
        self.screen.blit(title_text, title_rect)
        
        # Mensaje específico de causa de muerte
        death_message = self._get_death_message()
        death_text = self.font.render(death_message, True, COLORS['yellow'])
        death_rect = death_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40))
        self.screen.blit(death_text, death_rect)
        
        score_text = self.font.render(f"Puntuación Final: {self.score}", True, COLORS['white'])
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 10))
        self.screen.blit(score_text, score_rect)
        
        level_text = self.font.render(f"Nivel Alcanzado: {self.current_level}", True, COLORS['gray'])
        level_rect = level_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))
        self.screen.blit(level_text, level_rect)
        
        restart_text = self.font.render("Presiona R para reiniciar o ESC para volver al menú", True, COLORS['gray'])
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 80))
        self.screen.blit(restart_text, restart_rect)
    
    def render_victory(self) -> None:
        """Renderiza la pantalla de victoria."""
        # Overlay semi-transparente
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(COLORS['black'])
        self.screen.blit(overlay, (0, 0))
        
        # Mensaje de victoria
        title_text = self.big_font.render("¡VICTORIA TOTAL!", True, COLORS['yellow'])
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
        self.screen.blit(title_text, title_rect)
        
        pilot_text = self.font.render(f"El piloto {self.player_name} ha salvado la galaxia", True, COLORS['white'])
        pilot_rect = pilot_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        self.screen.blit(pilot_text, pilot_rect)
        
        score_text = self.font.render(f"Puntuación Final: {self.score}", True, COLORS['white'])
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.screen.blit(score_text, score_rect)
        
        levels_text = self.font.render(f"Niveles Completados: {MAX_LEVELS}/{MAX_LEVELS}", True, COLORS['green'])
        levels_rect = levels_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 30))
        self.screen.blit(levels_text, levels_rect)
        
        restart_text = self.font.render("Presiona R para jugar de nuevo o ESC para volver al menú", True, COLORS['gray'])
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 80))
        self.screen.blit(restart_text, restart_rect)

    def _draw_boss_enemy(self, surface: pygame.Surface, boss: BossEnemy):
        """Dibuja el boss enemy con efectos especiales."""
        # Usar el diseño de ojo intergaláctico
        current_time = pygame.time.get_ticks() / 1000.0
        draw_intergalactic_eye_boss(surface, boss.pos.to_int_tuple(), boss.radius, 
                                   current_time, boss.weak_points)
        
        # Laser charging indicator
        if boss.is_charging_laser():
            progress = boss.get_laser_charge_progress()
            charge_radius = int(boss.radius + 20 * progress)
            pygame.draw.circle(surface, (255, 0, 0, int(100 * progress)), boss.pos.to_int_tuple(), charge_radius, 3)
        
        # Boss health bar - larger and more prominent
        max_hp = 80 + (boss.level * 20)  # Match boss constructor
        hp_percentage = max(0.0, boss.hp / max_hp)
        bar_width = boss.radius * 3
        bar_height = 8
        bar_x = int(boss.pos.x - bar_width // 2)
        bar_y = int(boss.pos.y - boss.radius - 15)
        
        # Background
        pygame.draw.rect(surface, (0, 0, 0), pygame.Rect(bar_x, bar_y, bar_width, bar_height))
        # Health
        pygame.draw.rect(surface, (255, 0, 0), pygame.Rect(bar_x, bar_y, int(bar_width * hp_percentage), bar_height))
        
        # Boss level indicator
        text = self.font.render(f"BOSS LV.{boss.level}", True, (255, 255, 255))
        text_rect = text.get_rect(center=(boss.pos.x, boss.pos.y - boss.radius - 30))
        surface.blit(text, text_rect)

    def render_pause_menu(self) -> None:
        """Renderiza el menú de pausa encima del juego."""
        # Crear superficie semi-transparente
        pause_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        pause_surface.set_alpha(180)
        pause_surface.fill((0, 0, 0))
        
        # Título del menú de pausa
        title_text = self.big_font.render("JUEGO PAUSADO", True, COLORS['white'])
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 150))
        pause_surface.blit(title_text, title_rect)
        
        # Actualizar texto de los botones según el estado actual
        if self.sound_manager.music_enabled:
            self.toggle_music_button.text = "MÚSICA: ON"
        else:
            self.toggle_music_button.text = "MÚSICA: OFF"
            
        if self.sound_manager.sound_enabled:
            self.toggle_sound_button.text = "SONIDOS: ON"
        else:
            self.toggle_sound_button.text = "SONIDOS: OFF"
        
        # Dibujar botones del menú de pausa
        self.resume_button.draw(pause_surface)
        self.toggle_music_button.draw(pause_surface)
        self.toggle_sound_button.draw(pause_surface)
        self.quit_to_menu_button.draw(pause_surface)
        
        # Instrucciones
        instructions = [
            "ESC - Reanudar juego",
            "F11 - Pantalla completa"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.font.render(instruction, True, COLORS['light_gray'])
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 150 + i * 25))
            pause_surface.blit(text, text_rect)
        
        # Aplicar superficie con escalado
        self.render_scaled_surface(pause_surface)

    def run(self) -> None:
        """Ejecuta el bucle principal del juego."""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.process_events()
            self.handle_input(dt)
            self.update(dt)
            self.render()
        pygame.quit()