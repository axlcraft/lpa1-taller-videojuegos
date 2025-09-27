# programa principal
# pygame_demo.py
"""
Demo interactiva con Pygame
- Implementa clases del diagrama: Vector2D, Figura, Proyectil, Jugador, Enemigo, Escenario, GameManager
- Mecánicas: movimiento, disparo, IA básica, trampas explosivas, tesoros, inventario, XP y subida de nivel
- Controles:
    WASD - mover
    Mouse left - disparar hacia el cursor
    E - recoger objetos cercanos (tesoro / trampas como item)
    Q - vender primer item del inventario (simula tienda)
    ESC - salir
"""
from __future__ import annotations
import pygame
import random
import math
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

# -------------------------
# Config
# -------------------------
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
FPS = 60

PLAYER_RADIUS = 16
ENEMY_RADIUS = 14
PROJECTILE_RADIUS = 4
TRAP_RADIUS = 12
TREASURE_RADIUS = 10

XP_PER_KILL = 40
XP_PER_TREASURE_VALUE = 0.1  # XP gain = value * this factor

# -------------------------
# Math helper: Vector2D
# -------------------------
@dataclass
class Vector2D:
    x: float
    y: float

    def __add__(self, other: "Vector2D") -> "Vector2D":
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vector2D") -> "Vector2D":
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Vector2D":
        return Vector2D(self.x * scalar, self.y * scalar)

    def magnitude(self) -> float:
        return math.hypot(self.x, self.y)

    def normalized(self) -> "Vector2D":
        mag = self.magnitude()
        if mag == 0:
            return Vector2D(0, 0)
        return Vector2D(self.x / mag, self.y / mag)

    def to_int_tuple(self) -> Tuple[int, int]:
        return int(self.x), int(self.y)


# -------------------------
# Figura base
# -------------------------
class Figura:
    """Clase base para elementos con posición y radio."""

    def __init__(self, x: float, y: float, radio: int, color: Tuple[int, int, int]):
        self.pos = Vector2D(x, y)
        self.radio = radio
        self.color = color
        self.activo = True

    def distance_to(self, other: "Figura") -> float:
        return (self.pos - other.pos).magnitude()

    def collides_with(self, other: "Figura") -> bool:
        return self.distance_to(other) <= (self.radio + other.radio)


# -------------------------
# Objetos del mundo
# -------------------------
class Objeto:
    """Base para objetos recolectables (Trampa, Tesoro, Armamento)."""

    def __init__(self, x: float, y: float, name: str):
        self.pos = Vector2D(x, y)
        self.name = name


class TrampaExplosiva(Objeto):
    def __init__(self, x: float, y: float, alcance: float, dano: int):
        super().__init__(x, y, "TrampaExplosiva")
        self.alcance = alcance
        self.dano = dano
        self.radius = TRAP_RADIUS

    def detonar(self, entities: List[Figura]) -> List[Tuple[Figura, int]]:
        """Aplica daño a entidades dentro del alcance y retorna lista de (entity, damage)."""
        affected = []
        for e in entities:
            dist = (Vector2D(e.pos.x, e.pos.y) - Vector2D(self.pos.x, self.pos.y)).magnitude()
            if dist <= self.alcance + getattr(e, "radio", 0):
                affected.append((e, self.dano))
        return affected


class Tesoro(Objeto):
    def __init__(self, x: float, y: float, valor: int):
        super().__init__(x, y, "Tesoro")
        self.valor = valor
        self.radius = TREASURE_RADIUS


class ArmamentoDefensa(Objeto):
    def __init__(self, x: float, y: float, bonus_atk: int, bonus_def: int, price: int):
        super().__init__(x, y, "Equipo")
        self.bonus_atk = bonus_atk
        self.bonus_def = bonus_def
        self.price = price
        self.radius = 12


# -------------------------
# Proyectil
# -------------------------
class Proyectil(Figura):
    """Proyectil disparado por el jugador."""

    def __init__(self, x: float, y: float, direction: Vector2D, speed: float = 400.0, damage: int = 10):
        super().__init__(x, y, PROJECTILE_RADIUS, (255, 220, 0))
        self.direction = direction.normalized()
        self.speed = speed
        self.damage = damage
        self.lifetime = 2.5  # segundos

    def update(self, dt: float):
        self.pos = Vector2D(self.pos.x + self.direction.x * self.speed * dt,
                            self.pos.y + self.direction.y * self.speed * dt)
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.activo = False


# -------------------------
# Jugador
# -------------------------
class Jugador(Figura):
    def __init__(self, x: float, y: float, name: str = "Hero"):
        super().__init__(x, y, PLAYER_RADIUS, (50, 130, 240))
        self.name = name
        self.hp = 120
        self.attack = 18
        self.defense = 6
        self.level = 1
        self.xp = 0
        self.xp_to_next = 100
        self.inventory: List[Objeto] = []
        self.gold = 0
        self.move_speed = 180.0  # px/s
        self.shoot_cooldown = 0.35
        self._shoot_timer = 0.0
        self.invulnerable_time = 0.6
        self._inv_timer = 0.0

    def update_timers(self, dt: float):
        self._shoot_timer = max(0.0, self._shoot_timer - dt)
        self._inv_timer = max(0.0, self._inv_timer - dt)

    def can_shoot(self) -> bool:
        return self._shoot_timer <= 0.0

    def shoot(self, target_pos: Vector2D) -> Optional[Proyectil]:
        if not self.can_shoot():
            return None
        dir_vec = Vector2D(target_pos.x - self.pos.x, target_pos.y - self.pos.y)
        proj = Proyectil(self.pos.x, self.pos.y, dir_vec, speed=480.0, damage=self.attack // 1)
        self._shoot_timer = self.shoot_cooldown
        return proj

    def receive_damage(self, amount: int) -> int:
        if self._inv_timer > 0:
            return 0
        damage_final = max(0, amount - self.defense)
        self.hp -= damage_final
        self._inv_timer = self.invulnerable_time
        return damage_final

    def gain_xp(self, amount: int):
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


# -------------------------
# Enemigo
# -------------------------
class Enemigo(Figura):
    def __init__(self, x: float, y: float, tipo: str = "terrestre"):
        super().__init__(x, y, ENEMY_RADIUS, (230, 70, 70))
        self.tipo = tipo  # "volador" o "terrestre"
        self.hp = 60 if tipo == "terrestre" else 45
        self.attack = 12 if tipo == "terrestre" else 10
        self.defense = 3 if tipo == "terrestre" else 1
        self.speed = 80.0 if tipo == "terrestre" else 110.0
        self._invulnerable_timer = 0.0

    def update(self, dt: float, player: Jugador):
        # IA simple: perseguir al jugador si está vivo
        if self.hp <= 0:
            return
        dir_to_player = Vector2D(player.pos.x - self.pos.x, player.pos.y - self.pos.y)
        step = dir_to_player.normalized()
        self.pos = Vector2D(self.pos.x + step.x * self.speed * dt,
                            self.pos.y + step.y * self.speed * dt)
        self._invulnerable_timer = max(0.0, self._invulnerable_timer - dt)

    def receive_damage(self, amount: int) -> int:
        if self._invulnerable_timer > 0:
            return 0
        dmg = max(0, amount - self.defense)
        self.hp -= dmg
        self._invulnerable_timer = 0.15
        return dmg


# -------------------------
# Escenario: genera enemigos y objetos
# -------------------------
class Escenario:
    def __init__(self, width: int, height: int, difficulty: float = 1.0):
        self.width = width
        self.height = height
        self.difficulty = difficulty
        self.enemies: List[Enemigo] = []
        self.traps: List[TrampaExplosiva] = []
        self.treasures: List[Tesoro] = []
        self.items_ground: List[ArmamentoDefensa] = []

    def generate(self, n_enemies: int = 5, n_treasures: int = 4, n_traps: int = 3):
        self.enemies = []
        for _ in range(n_enemies):
            x = random.uniform(50, self.width - 50)
            y = random.uniform(50, self.height - 50)
            tipo = random.choice(["terrestre", "volador"])
            self.enemies.append(Enemigo(x, y, tipo))
        self.treasures = []
        for _ in range(n_treasures):
            x = random.uniform(40, self.width - 40)
            y = random.uniform(40, self.height - 40)
            valor = random.randint(10, 120)
            self.treasures.append(Tesoro(x, y, valor))
        self.traps = []
        for _ in range(n_traps):
            x = random.uniform(40, self.width - 40)
            y = random.uniform(40, self.height - 40)
            alcance = random.uniform(30.0, 60.0)
            dano = random.randint(12, 36)
            self.traps.append(TrampaExplosiva(x, y, alcance, dano))
        self.items_ground = []
        # small chance to spawn equipment
        if random.random() < 0.6:
            x = random.uniform(40, self.width - 40)
            y = random.uniform(40, self.height - 40)
            self.items_ground.append(ArmamentoDefensa(x, y, bonus_atk=4, bonus_def=2, price=40))


# -------------------------
# Game Manager: loop + rendering + eventos
# -------------------------
class GameManager:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Taller Videojuegos - Demo Pygame")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 18)
        self.running = True

        self.player = Jugador(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.scene = Escenario(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.scene.generate(n_enemies=6, n_treasures=5, n_traps=4)
        self.projectiles: List[Proyectil] = []
        self.score = 0
        self.victory_score = 300  # ejemplo de condición por puntaje

    def handle_input(self, dt: float):
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
            self.player.pos = Vector2D(self.player.pos.x + norm.x * self.player.move_speed * dt,
                                       self.player.pos.y + norm.y * self.player.move_speed * dt)
            # clamp to screen
            self.player.pos.x = max(self.player.radio, min(SCREEN_WIDTH - self.player.radio, self.player.pos.x))
            self.player.pos.y = max(self.player.radio, min(SCREEN_HEIGHT - self.player.radio, self.player.pos.y))

    def process_events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self.running = False
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                # disparar
                mp = Vector2D(*pygame.mouse.get_pos())
                proj = self.player.shoot(mp)
                if proj:
                    self.projectiles.append(proj)
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_e:
                    # pick up nearby things (within a radius)
                    self.try_pickup()
                elif ev.key == pygame.K_q:
                    # sell first item in inventory for gold (simple shop)
                    self.sell_first_inventory_item()
                elif ev.key == pygame.K_ESCAPE:
                    self.running = False

    def try_pickup(self):
        # pick treasures
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

        # pick traps as items (player can pick up trap to use)
        picked_trap = None
        for tr in self.scene.traps:
            dist = (Vector2D(tr.pos.x, tr.pos.y) - self.player.pos).magnitude()
            if dist <= (tr.radius + self.player.radio + 5):
                # pick trap into inventory (store the object)
                self.player.inventory.append(tr)
                picked_trap = tr
                break
        if picked_trap:
            self.scene.traps.remove(picked_trap)
            print("Recogiste una trampa explosiva en el inventario.")

        # pick equipment on ground
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

    def sell_first_inventory_item(self):
        if not self.player.inventory:
            print("Inventario vacío.")
            return
        item = self.player.inventory.pop(0)
        if isinstance(item, ArmamentoDefensa):
            sell_value = item.price // 2
            self.player.gold += sell_value
            print(f"Vendiste {item.name} por {sell_value} oro.")
        elif isinstance(item, TrampaExplosiva):
            # selling trap yields less gold
            self.player.gold += 10
            print("Vendiste una trampa por 10 oro.")
        else:
            self.player.gold += 5
            print("Vendiste un objeto por 5 oro.")

    def update(self, dt: float):
        # timers
        self.player.update_timers(dt)

        # update projectiles
        for p in list(self.projectiles):
            p.update(dt)
            # remove if outside bounds or inactive
            if (p.pos.x < -10 or p.pos.x > SCREEN_WIDTH + 10 or p.pos.y < -10 or p.pos.y > SCREEN_HEIGHT + 10) or not p.activo:
                self.projectiles.remove(p)

        # update enemies
        for e in list(self.scene.enemies):
            e.update(dt, self.player)
            # collision proj -> enemy
            for p in list(self.projectiles):
                # treat projectiles as figuras for collision test
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
                        # enemy dies
                        self.scene.enemies.remove(e)
                        self.player.gain_xp(XP_PER_KILL)
                        self.score += 30
                        print(f"Enemigo derrotado. XP ganada. Nivel: {self.player.level} XP:{self.player.xp}")
                    break

            # enemy collision player (melee)
            if e.collides_with(self.player):
                # enemy attack
                dmg = max(0, e.attack - self.player.defense)
                dealt = self.player.receive_damage(dmg)
                if dealt > 0:
                    print(f"Recibiste {dealt} de daño. HP={self.player.hp}")
                # small knockback
                vec = Vector2D(self.player.pos.x - e.pos.x, self.player.pos.y - e.pos.y).normalized()
                self.player.pos = Vector2D(self.player.pos.x + vec.x * 8, self.player.pos.y + vec.y * 8)

        # check traps - if player steps on trap, either detonate (if ground trap) or if trap in inventory can be placed
        for tr in list(self.scene.traps):
            dist = (Vector2D(tr.pos.x, tr.pos.y) - self.player.pos).magnitude()
            if dist <= (tr.radius + self.player.radio):
                # detonate immediately as environment trap
                affected = tr.detonar(self.scene.enemies + [self.player])
                for ent, dmg in affected:
                    if isinstance(ent, Jugador):
                        self.player.receive_damage(dmg)
                        print(f"Trampa explotó: recibiste {dmg}")
                    else:
                        ent.receive_damage(dmg)
                        if ent.hp <= 0 and ent in self.scene.enemies:
                            self.scene.enemies.remove(ent)
                            self.player.gain_xp(XP_PER_KILL)
                # remove trap after detonation
                if tr in self.scene.traps:
                    self.scene.traps.remove(tr)
                self.score -= 10

        # treasures don't move; if player near auto-collect small ones
        for t in list(self.scene.treasures):
            dist = (Vector2D(t.pos.x, t.pos.y) - self.player.pos).magnitude()
            if dist <= (TREASURE_RADIUS + self.player.radio):
                # auto collect
                self.player.gold += t.valor
                self.player.gain_xp(int(t.valor * XP_PER_TREASURE_VALUE))
                print(f"Recolectado tesoro (auto). Valor {t.valor}. Oro:{self.player.gold}")
                self.scene.treasures.remove(t)

        # check victory conditions
        if self.score >= self.victory_score:
            print("¡Victoria por puntaje alcanzado!")
            self.running = False
        if not self.scene.enemies:
            print("¡Victoria por exploración/completitud! Todos los enemigos eliminados.")
            self.running = False

    def draw_hud(self):
        # background for hud
        hud_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 36)
        pygame.draw.rect(self.screen, (20, 20, 20), hud_rect)
        # texts: HP, Level, XP, Gold, Score
        hp_text = self.font.render(f"HP: {self.player.hp}", True, (255, 255, 255))
        lvl_text = self.font.render(f"LVL: {self.player.level}", True, (255, 255, 255))
        xp_text = self.font.render(f"XP: {self.player.xp}/{self.player.xp_to_next}", True, (255, 255, 255))
        gold_text = self.font.render(f"Gold: {self.player.gold}", True, (255, 255, 0))
        score_text = self.font.render(f"Score: {self.score}", True, (200, 200, 200))
        inv_text = self.font.render(f"Inv: {len(self.player.inventory)} items (E recoger / Q vender)", True, (180, 180, 180))

        self.screen.blit(hp_text, (8, 6))
        self.screen.blit(lvl_text, (110, 6))
        self.screen.blit(xp_text, (180, 6))
        self.screen.blit(gold_text, (360, 6))
        self.screen.blit(score_text, (460, 6))
        self.screen.blit(inv_text, (580, 6))

    def render(self):
        self.screen.fill((28, 28, 28))
        # draw treasures
        for t in self.scene.treasures:
            pygame.draw.circle(self.screen, (255, 215, 0), (int(t.pos.x), int(t.pos.y)), TREASURE_RADIUS)
        # draw traps
        for tr in self.scene.traps:
            pygame.draw.circle(self.screen, (150, 30, 30), (int(tr.pos.x), int(tr.pos.y)), TRAP_RADIUS)
            # small outline for range
            try:
                pygame.draw.circle(self.screen, (120, 30, 30), (int(tr.pos.x), int(tr.pos.y)), int(tr.alcance), 1)
            except Exception:
                pass
        # draw equipment on ground
        for it in self.scene.items_ground:
            pygame.draw.rect(self.screen, (100, 200, 150), pygame.Rect(int(it.pos.x) - 8, int(it.pos.y) - 8, 16, 16))

        # draw projectiles
        for p in self.projectiles:
            pygame.draw.circle(self.screen, p.color, p.pos.to_int_tuple(), p.radio)

        # draw enemies
        for e in self.scene.enemies:
            col = e.color
            pygame.draw.circle(self.screen, col, (int(e.pos.x), int(e.pos.y)), e.radio)
            # hp bar
            hp_w = int(2 * e.radio * max(0.0, e.hp) / (60 if e.tipo == "terrestre" else 45))
            pygame.draw.rect(self.screen, (0, 0, 0), pygame.Rect(int(e.pos.x - e.radio), int(e.pos.y - e.radio - 8), 2 * e.radio, 5))
            pygame.draw.rect(self.screen, (0, 255, 0), pygame.Rect(int(e.pos.x - e.radio), int(e.pos.y - e.radio - 8), hp_w, 5))

        # draw player
        pygame.draw.circle(self.screen, self.player.color, (int(self.player.pos.x), int(self.player.pos.y)), self.player.radio)
        # player hp bar
        pygame.draw.rect(self.screen, (80, 80, 80), pygame.Rect(10, SCREEN_HEIGHT - 28, 220, 16))
        pygame.draw.rect(self.screen, (0, 200, 0), pygame.Rect(10, SCREEN_HEIGHT - 28, int(220 * max(0, self.player.hp) / 200), 16))

        # draw hud
        self.draw_hud()

        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.process_events()
            self.handle_input(dt)
            self.update(dt)
            self.render()
        pygame.quit()


# -------------------------
# Main
# -------------------------
if __name__ == "__main__":
    gm = GameManager()
    gm.run()
