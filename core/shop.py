"""
Sistema de tienda del juego.
Permite comprar mejoras entre niveles.
"""
import pygame
import math
from typing import List, Dict, Optional
from core.game_states import Button
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, COLORS


class ShopItem:
    """Artículo de la tienda."""
    
    def __init__(self, name: str, description: str, price: int, item_type: str, bonus_value: int, max_purchases: int = 5):
        self.name = name
        self.description = description
        self.base_price = price
        self.price = price  # Precio actual (aumenta con compras)
        self.item_type = item_type  # 'health', 'attack', 'defense', 'speed'
        self.bonus_value = bonus_value
        self.purchased = False  # Mantengo por compatibilidad
        self.purchase_count = 0  # Número de veces comprado
        self.max_purchases = max_purchases  # Máximo número de compras
        
    def can_purchase(self) -> bool:
        """Verifica si se puede comprar este item."""
        return self.purchase_count < self.max_purchases
        
    def get_current_price(self) -> int:
        """Obtiene el precio actual (aumenta 50% por compra)."""
        return int(self.base_price * (1.5 ** self.purchase_count))
        
    def purchase_item(self) -> bool:
        """Compra el item si es posible."""
        if self.can_purchase():
            self.purchase_count += 1
            self.price = self.get_current_price()
            if self.purchase_count >= self.max_purchases:
                self.purchased = True  # Marca como agotado
            return True
        return False


class Shop:
    """Sistema de tienda entre niveles."""
    
    def __init__(self, font: pygame.font.Font, big_font: pygame.font.Font):
        self.font = font
        self.big_font = big_font
        self.items: List[ShopItem] = []
        self.buttons: List[Button] = []
        self.continue_button = Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 80, 200, 50, "CONTINUAR", font)
        self.selected_item: Optional[ShopItem] = None
        
        self._create_shop_items()
        self._create_buttons()
    
    def _create_shop_items(self):
        """Crea los artículos disponibles en la tienda."""
        self.items = [
            ShopItem("Reparación Completa", "Restaura 100% HP", 120, "health", 999, 99),  # Siempre disponible
            ShopItem("Reactor Cuántico", "HP máximo +80", 200, "max_health", 80, 5),
            ShopItem("Cañones de Plasma", "Ataque +15", 180, "attack", 15, 5),
            ShopItem("Blindaje Titanio", "Defensa +10", 150, "defense", 10, 5),
            ShopItem("Motores Warp", "Velocidad +50%", 160, "speed", 50, 3),
            ShopItem("Escudo Deflector", "Invulnerabilidad +0.5s", 300, "invulnerability", 5, 3),
        ]
    
    def _create_buttons(self):
        """Crea los botones para cada artículo."""
        self.buttons = []
        for i, item in enumerate(self.items):
            x = 50 + (i % 3) * 280
            y = 200 + (i // 3) * 150
            button = Button(x, y, 250, 40, f"{item.name} - {item.price}g", self.font)
            self.buttons.append(button)
    
    def reset_purchases(self):
        """Reinicia las compras para un nuevo nivel (solo reparación)."""
        for item in self.items:
            # Solo resetear reparación de salud, las mejoras permanecen
            if item.item_type == "health":
                item.purchase_count = 0
                item.purchased = False
                item.price = item.base_price
    
    def handle_event(self, event: pygame.event.Event, player_gold: int) -> tuple:
        """
        Maneja eventos de la tienda.
        Retorna (item_purchased, continue_pressed, selected_item)
        """
        # Botón continuar
        if self.continue_button.handle_event(event):
            return (None, True, None)
        
        # Botones de artículos
        for i, button in enumerate(self.buttons):
            if button.handle_event(event):
                item = self.items[i]
                current_price = item.get_current_price()
                if item.can_purchase() and player_gold >= current_price:
                    item.purchase_item()
                    return (item, False, item)
                else:
                    self.selected_item = item
        
        return (None, False, None)
    
    def draw(self, screen: pygame.Surface, player_gold: int, player_name: str, current_level: int):
        """Dibuja la interfaz de la tienda."""
        # Título
        title_text = self.big_font.render("ESTACIÓN ESPACIAL - TIENDA", True, COLORS['yellow'])
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 50))
        screen.blit(title_text, title_rect)
        
        # Información del jugador
        info_text = self.font.render(f"Piloto: {player_name} | Oro: {player_gold}g | Nivel: {current_level}", True, COLORS['white'])
        info_rect = info_text.get_rect(center=(SCREEN_WIDTH//2, 100))
        screen.blit(info_text, info_rect)
        
        # Separador
        pygame.draw.line(screen, COLORS['white'], (50, 130), (SCREEN_WIDTH - 50, 130), 2)
        
        # Artículos de la tienda
        for i, (item, button) in enumerate(zip(self.items, self.buttons)):
            x = 50 + (i % 3) * 280
            y = 200 + (i // 3) * 150
            
            # Fondo del artículo
            item_rect = pygame.Rect(x - 10, y - 10, 270, 120)
            current_price = item.get_current_price()
            
            # Color según disponibilidad
            if not item.can_purchase():
                color = COLORS['green']  # Agotado
            elif player_gold < current_price:
                color = COLORS['trap']   # Sin fondos
            else:
                color = COLORS['menu_bg']  # Disponible
            
            pygame.draw.rect(screen, color, item_rect)
            pygame.draw.rect(screen, COLORS['white'], item_rect, 2)
            
            # Nombre del artículo (como botón)
            button_color = COLORS['button_hover'] if button.is_hovered else COLORS['button']
            if not item.can_purchase():
                button_color = COLORS['green']
            elif player_gold < current_price:
                button_color = COLORS['trap']
            
            button.rect.topleft = (x, y)
            pygame.draw.rect(screen, button_color, button.rect)
            pygame.draw.rect(screen, COLORS['white'], button.rect, 2)
            
            # Texto del botón con contadores
            if not item.can_purchase():
                button_text = "AGOTADO"
            elif player_gold < current_price:
                button_text = "SIN FONDOS"
            else:
                button_text = f"{item.name} - {current_price}g"
            
            text_color = COLORS['white']
            if player_gold < item.price and not item.purchased:
                text_color = COLORS['light_gray']
            
            text_surface = self.font.render(button_text, True, text_color)
            text_rect = text_surface.get_rect(center=button.rect.center)
            screen.blit(text_surface, text_rect)
            
            # Descripción del artículo  
            desc_text = self.font.render(item.description, True, COLORS['light_gray'])
            screen.blit(desc_text, (x, y + 50))
            
            # Contador de compras
            count_text = f"Comprado: {item.purchase_count}/{item.max_purchases}"
            count_color = COLORS['yellow'] if item.purchase_count > 0 else COLORS['light_gray']
            count_surface = self.font.render(count_text, True, count_color)
            screen.blit(count_surface, (x, y + 70))
            
            # Efecto visual del artículo (solo si no está comprado)
            if not item.purchased:
                effect_x = x + 200  # Esquina derecha del item
                effect_y = y + 40   # Centro vertical del item
                self.draw_item_effect_preview(screen, item, effect_x, effect_y)
            
            # Icono de tipo con efectos
            type_icons = {
                'health': '❤️',
                'max_health': '🛡️',
                'attack': '⚔️',
                'defense': '🛡️',
                'speed': '⚡',
                'invulnerability': '✨'
            }
            icon = type_icons.get(item.item_type, '📦')
            
            # Agregar brillo al icono si está disponible
            if not item.purchased and player_gold >= item.price:
                # Crear superficie con brillo
                time = pygame.time.get_ticks() * 0.001
                glow = 0.3 + 0.7 * abs(math.sin(time * 3))
                glow_color = (int(min(255, max(0, 255 * glow))), int(min(255, max(0, 255 * glow))), 0)
                
                # Dibujar halo dorado alrededor del icono
                for offset in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
                    glow_text = self.font.render(icon, True, glow_color)
                    screen.blit(glow_text, (x + offset[0], y + 75 + offset[1]))
            
            icon_text = self.font.render(icon, True, COLORS['yellow'])
            screen.blit(icon_text, (x, y + 75))
            
            # Valor del bonus con efectos
            bonus_color = COLORS['green']
            if not item.purchased and player_gold >= item.price:
                # Efecto pulsante en el bonus
                time = pygame.time.get_ticks() * 0.001
                pulse = 0.7 + 0.3 * abs(math.sin(time * 4))
                bonus_color = (0, int(min(255, max(0, 255 * pulse))), 0)
            
            bonus_text = self.font.render(f"+{item.bonus_value}", True, bonus_color)
            screen.blit(bonus_text, (x + 30, y + 75))
        
        # Instrucciones
        instructions = [
            "Haz clic en los artículos para comprarlos",
            "Las mejoras se aplicarán inmediatamente",
            "¡Prepárate para el siguiente nivel!"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.font.render(instruction, True, COLORS['light_gray'])
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 150 + i * 25))
            screen.blit(text, text_rect)
        
        # Botón continuar
        self.continue_button.draw(screen)
        
        # Información de artículo seleccionado
        if self.selected_item and player_gold < self.selected_item.price:
            warning_text = self.font.render("¡No tienes suficiente oro para este artículo!", True, COLORS['enemy'])
            warning_rect = warning_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 120))
            screen.blit(warning_text, warning_rect)

    def draw_item_effect_preview(self, screen: pygame.Surface, item: ShopItem, center_x: int, center_y: int):
        """
        Dibuja una vista previa del efecto visual de la mejora en la tienda.
        
        Args:
            screen: Superficie donde dibujar
            item: Artículo de la tienda
            center_x: Centro X para dibujar el efecto
            center_y: Centro Y para dibujar el efecto
        """
        time = pygame.time.get_ticks() * 0.001
        
        if item.item_type == "health" or item.item_type == "max_health":
            # Efecto de salud - Pulso verde/rojo
            pulse = 0.5 + 0.5 * abs(math.sin(time * 3))
            color = (int(min(255, max(0, 255 * pulse))), int(min(255, max(0, 200 * pulse))), int(min(255, max(0, 100 * pulse))))
            
            # Cruz médica animada
            size = int(8 + pulse * 4)
            pygame.draw.rect(screen, color, (center_x - size, center_y - 2, size * 2, 4))
            pygame.draw.rect(screen, color, (center_x - 2, center_y - size, 4, size * 2))
            
            # Partículas curativas
            for i in range(4):
                angle = time * 2 + i * math.pi / 2
                px = center_x + math.cos(angle) * 15
                py = center_y + math.sin(angle) * 15
                pygame.draw.circle(screen, (0, 255, 0), (int(px), int(py)), 2)
        
        elif item.item_type == "attack":
            # Efecto de ataque - Espadas cruzadas con chispas
            glow = 0.3 + 0.7 * abs(math.sin(time * 4))
            color = (int(min(255, max(0, 255 * glow))), int(min(255, max(0, 150 * glow))), 0)
            
            # Espadas cruzadas
            pygame.draw.line(screen, color, (center_x - 10, center_y - 10), (center_x + 10, center_y + 10), 3)
            pygame.draw.line(screen, color, (center_x + 10, center_y - 10), (center_x - 10, center_y + 10), 3)
            
            # Chispas de energía
            for i in range(6):
                spark_angle = time * 3 + i * math.pi / 3
                spark_dist = 12 + math.sin(time * 5) * 3
                sx = center_x + math.cos(spark_angle) * spark_dist
                sy = center_y + math.sin(spark_angle) * spark_dist
                pygame.draw.circle(screen, (255, 255, 0), (int(sx), int(sy)), 1)
        
        elif item.item_type == "defense":
            # Efecto de defensa - Escudo hexagonal
            shield_glow = 0.4 + 0.6 * abs(math.sin(time * 2))
            color = (0, int(min(255, max(0, 150 * shield_glow))), int(min(255, max(0, 255 * shield_glow))))
            
            # Hexágono del escudo
            points = []
            for i in range(6):
                angle = i * math.pi / 3 + time * 0.5
                radius = 10 + shield_glow * 2
                px = center_x + math.cos(angle) * radius
                py = center_y + math.sin(angle) * radius
                points.append((px, py))
            
            if len(points) >= 3:
                pygame.draw.polygon(screen, color, points, 2)
                
            # Centro del escudo
            pygame.draw.circle(screen, color, (center_x, center_y), 3)
        
        elif item.item_type == "speed":
            # Efecto de velocidad - Rayos de velocidad
            speed_pulse = 0.2 + 0.8 * abs(math.sin(time * 6))
            color = (int(min(255, max(0, 255 * speed_pulse))), int(min(255, max(0, 255 * speed_pulse))), 0)
            
            # Rayos de velocidad hacia atrás
            for i in range(3):
                ray_length = 15 + i * 5
                ray_alpha = int(255 - i * 60)
                trail_color = (*color, max(0, ray_alpha))
                
                trail_surf = pygame.Surface((ray_length, 3), pygame.SRCALPHA)
                trail_surf.fill(trail_color)
                screen.blit(trail_surf, (center_x - ray_length, center_y - 1 + i * 2))
            
            # Núcleo de energía
            pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), 2)
        
        elif item.item_type == "invulnerability":
            # Efecto de invulnerabilidad - Aura brillante
            aura_intensity = 0.3 + 0.7 * abs(math.sin(time * 4))
            
            # Múltiples capas de aura
            for radius in [15, 12, 9, 6]:
                alpha = int(50 * aura_intensity * (1 - radius / 20))
                if alpha > 0:
                    aura_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                    pygame.draw.circle(aura_surf, (255, 255, 255, alpha), (radius, radius), radius)
                    screen.blit(aura_surf, (center_x - radius, center_y - radius))
            
            # Estrella central
            star_points = []
            for i in range(8):
                angle = i * math.pi / 4 + time * 2
                if i % 2 == 0:
                    radius = 6
                else:
                    radius = 3
                px = center_x + math.cos(angle) * radius
                py = center_y + math.sin(angle) * radius
                star_points.append((px, py))
            
            if len(star_points) >= 3:
                pygame.draw.polygon(screen, (255, 255, 255), star_points)