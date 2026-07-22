# Análisis del Proyecto: "Odisea En El Espacio by AXL"

## Resumen

Juego 2D _top-down_ tipo space-shooter/action-RPG desarrollado en **Python 3.12 + Pygame** como proyecto académico de Programación Orientada a Objetos. El jugador pilota una nave a través de 18 niveles con boss fights cada 2 niveles, combatiendo 6 tipos de enemigos, recolectando tesoros, power-ups, y comprando mejoras en una tienda entre niveles.

---

## Aspectos Positivos

1. **Arquitectura modular clara**: Separación en `core/`, `entities/`, `world/`, `config/`, `utils/` que facilita la navegación y el mantenimiento.

2. **Uso correcto de OOP**: Herencia (`Figura` → `Jugador`/`Enemigo`/`Proyectil`), polimorfismo (6 tipos de enemigos, 4 personajes, 6 armas), composición (`GameManager` compone múltiples sistemas).

3. **Máquina de estados robusta**: 10 estados de juego bien definidos (`GameState` enum) con transiciones claras.

4. **Síntesis de audio procedural**: Todo el audio se genera matemáticamente con NumPy — logros notables en sonido y música sin usar archivos externos.

5. **Sistema de efectos visuales rico**: Partículas, trails, glow, screen shake, animaciones de fondo por nivel (10+ temas planetarios), representaciones detalladas de naves enemigas.

6. **Escalado de dificultad progresivo**: 18 niveles con estadísticas que escalan, nuevos tipos de enemigos desbloqueables en distintos rangos de nivel, dificultad más agresiva después del nivel 10.

7. **Persistencia de puntuaciones**: Leaderboard en JSON con top 10, nombres de piloto, fechas.

---

## Fallas y Soluciones Aplicadas

### 1. Duplicación masiva de lógica de colisiones

**Archivo:** `core/game_manager.py` — L640-665 y L954-990

**Problema:** Dos bloques separados manejaban `enemy_projectiles` con lógica casi idéntica. El primero (L640-665) procesaba colisiones dentro del bucle de enemigos; el segundo (L954-990) era un bucle independiente que repetía la misma lógica. Cualquier cambio requería sincronización manual entre ambos.

**Solución aplicada:**
- El bloque L954-990 se eliminó por completo.
- El bloque unificado (L640-665) actualiza los proyectiles, verifica límites de pantalla, y maneja colisiones con el jugador usando defensa (`ep.damage - self.player.defense`).
- Se agregó `can_damage_player()` para filtrar proyectiles que no dañan al jugador.
- Se agregó `floating_text` para feedback visual del daño recibido.

---

### 2. Código muerto: `draw_hud()` vs `draw_hud_on_surface()`

**Archivo:** `core/game_manager.py` — L1039-1078 (eliminado)

**Problema:** Existían dos métodos para dibujar el HUD. `draw_hud()` (L1039) nunca era llamado — el flujo real usaba `draw_hud_on_surface()`. El método muerto engañaba a los desarrolladores y duplicaba ~40 líneas.

**Solución aplicada:**
- Se eliminó `draw_hud()` completamente.
- Se mantuvo `draw_hud_on_surface()` como el único punto de renderizado del HUD.

---

### 3. Duplicación de datos de personajes

**Archivo:** `entities/player.py` — L41-54, `core/character_system.py` — L40-97

**Problema:** Las estadísticas base de los 4 personajes se definían en `CharacterManager` y también como valores _default_ en el constructor de `Jugador`. Si se añadía un nuevo personaje a `CharacterManager` pero se olvidaban los defaults, el juego usaba valores incorrectos sin advertir.

**Solución aplicada:**
- Se eliminaron los valores por defecto del constructor de `Jugador`.
- `character_data` ahora es obligatorio (se quitó `Optional` y el valor por defecto `None`).
- Las stats se obtienen exclusivamente de `character_data['stats']` — si no se provee el diccionario, Python lanza `TypeError` explícito.

---

### 4. Import circular potencial

**Archivo:** `core/visual_effects.py` — L793-812 (eliminado)

**Problema:** Las funciones `get_stellar_background_color()`, `get_stellar_accent_color()`, `get_stellar_name()` usaban `from config.settings import STELLAR_BODIES` dentro del cuerpo (import tardío). Funcionaba pero era frágil — si `settings.py` llegaba a importar `visual_effects`, ocurría un _circular import_.

**Solución aplicada:**
- Las tres funciones se movieron a `config/settings.py` como funciones de módulo.
- `core/visual_effects.py` ahora importa desde `config.settings` en el tope del archivo.
- `core/game_manager.py` también importa directamente desde `config.settings`.

---

### 5. Múltiples sistemas de power-ups conviviendo

**Archivos:** `world/scene.py` L141-157, `core/powerup_system.py`, `world/objects.py` L188-279

**Problema:** Existían tres sistemas de power-ups activos: (a) `world/objects.py` con `PowerUpEspacial` y subclases, (b) `core/powerup_system.py` con `PowerUp` y `PowerUpManager`, (c) generación en `Escenario`. Causaba confusión, código duplicado, efectos solapados y mantenimiento imposible.

**Solución aplicada:**
- Se eliminó la generación de power-ups/hazards de `world/scene.py` (se quitaron los parámetros `n_power_ups` y `n_hazards` de `generate()`, y los atributos `power_ups`/`hazards` de `Escenario`).
- Se eliminó el método `update_space_objects()` que solo actualizaba esos objetos.
- Se eliminaron las colisiones y renderizado de los power-ups antiguos en `game_manager.py`.
- El sistema `core/powerup_system.py` es ahora la **única** fuente de power-ups, gestionados por `PowerUpManager`.

---

### 6. README.md con URLs rotas

**Archivo:** `README.md`

**Problema:** Todas las URLs apuntaban a un archivo `.zip` dentro de `.venv` en `raw.githubusercontent.com`. Ninguna funcionaba. Las instrucciones de instalación y los badges eran inaccesibles.

**Solución aplicada:**
- Se reescribió completamente el README.md con URLs correctas del repositorio.
- Se eliminaron los badges rotos.
- Se agregó una tabla de controles legible.
- Las instrucciones de instalación ahora usan rutas y URLs válidas.

---

### 7. Sin tests automatizados

**Archivo:** `tests/` (nuevo directorio)

**Problema:** No existía ningún test. ~7000 líneas de código sin cobertura de pruebas hacía que cualquier refactorización fuese riesgosa.

**Solución aplicada:**
- Se creó el directorio `tests/` con 14 archivos de test (186 tests en total) usando `pytest`.
- Se implementó un mock completo de Pygame en `conftest.py` para ejecutar tests en entornos headless (servidores CI, terminals sin X11).
- Cobertura actual: 186 tests, 0 fallos.
- Se documentó la suite en `tests/tests.md` con instrucciones de ejecución, descripción de cada archivo, y objetivos de cobertura.

---

### 8. Colisión duplicada jugador-enemigo (daño doble)

**Archivo:** `core/game_manager.py` — L748-766 y L928-953 (eliminado)

**Problema:** El jugador recibía daño por contacto **dos veces por frame**: una en L748-766 (colisión con `e.collides_with()`) y otra en L928-953 (distancia entre centros). El primer bloque usaba `e.attack - defensa`, el segundo usaba `e.get_contact_damage()`. Esto causaba el doble de daño del esperado.

**Solución aplicada:**
- Se eliminó el bloque duplicado (L928-953).
- El bloque restante (L748-766) ahora usa `e.get_contact_damage() - defensa` para el cálculo de daño.
- Se agregó `floating_text` de feedback visual.
- Se eliminó el `continue` que impedía procesar al resto de enemigos tras una colisión.

---

### 9. Efectos de power-ups sin limpiar

**Archivo:** `world/objects.py` L231-278 y `core/powerup_system.py`

**Problema:** Los power-ups del sistema antiguo (`ImpulsoVelocidad`, `MejoraArmas`) asignaban atributos directamente al jugador (`player.speed_boost`, `player.weapon_boost`) sin nunca limpiarlos al expirar. Al eliminar el sistema antiguo, este problema se resuelve automáticamente.

**Solución aplicada:** *(Resuelto como consecuencia de la unificación de power-ups — issue #5.)* El sistema `core/powerup_system.py` maneja la expiración de efectos correctamente mediante `_update_active_effects()`.

---

### 10. Lógica muerta en `_create_multi_shot()`

**Archivo:** `entities/player.py` L211-213

**Problema:** Las líneas `self._shoot_timer = self.shoot_cooldown` y `return proj` estaban después del `return projectiles` (L196), por lo que nunca se ejecutaban. `proj` ni siquiera estaba definido en ese ámbito.

**Solución aplicada:**
- Se eliminaron las líneas inalcanzables (L211-213 originales).
- El método ahora termina limpiamente con `return projectiles`.

---

### 11. Uso inconsistente de `enemy_projectiles`

**Archivo:** `core/game_manager.py` L677-678

**Problema:** Se verificaba `if not hasattr(self, 'enemy_projectiles')` en tiempo de ejecución, a pesar de que `enemy_projectiles` ya se inicializa como lista vacía en `__init__` (L114). Esta verificación era siempre falsa.

**Solución aplicada:**
- Se eliminó el bloque `hasattr` redundante.

---

### 12. Escalado inconsistente del boss

**Archivo:** `entities/boss_enemy.py` L76-98

**Problema:** El cálculo de stats para niveles 11-18 reiniciaba desde valores base incorrectos. Usaba `(10 * 20)` como si fuera `hp_bonus` en lugar de `80 + (10 * 20)` como `hp` total. Esto hacía que los bosses de niveles 11+ fueran mucho más débiles de lo diseñado.

**Solución aplicada:**
- Se simplificó la lógica de escalado usando multiplicadores directos:
  - Niveles 1-10: `level * 20` para HP
  - Niveles 11-18: `(10 * 20) + (level - 10) * 40` — continúa desde donde quedó el nivel 10
- Se eliminaron las variables redundantes (`hp_bonus` → `hp_mult`, etc.)

---

### 13. Sin manejo de errores en archivos

**Archivo:** `core/leaderboard.py`

**Problema:** `scores.json` se lee/escribe sin locks ni escritura atómica. Si el archivo se corrompe (escritura concurrente, corte de energía), se pierden todas las puntuaciones o el juego crashea.

**Solución:** *(Mejora pendiente — implementar escritura con `tempfile` + `os.replace()` para atomicidad.)*

---

### 14. Falta de límite de proyectiles

**Archivo:** `core/game_manager.py` L632-637

**Problema:** Los proyectiles se acumulaban sin límite. Con armas rápidas (rapid fire, multi-shot) podían haber cientos de proyectiles simultáneos, degradando el rendimiento.

**Solución aplicada:**
- Se agregó un límite de 100 proyectiles: `if len(self.projectiles) > 100: self.projectiles = self.projectiles[-100:]`

---

### 15. Atributos dinámicos sin validación

**Archivos:** `entities/player.py`, `world/objects.py`

**Problema:** Atributos como `player.shield_hp`, `player.speed_boost`, `player.weapon_malfunction` se asignaban dinámicamente sin declaración explícita. Un typo (ej. `speeed_boost`) no generaba error — fallaba silenciosamente.

**Solución aplicada:**
- Se agregaron todos los atributos dinámicos explícitamente en `Jugador.__init__()`:
  - `self.shield_hp = 0`
  - `self.speed_boost = 1.0`
  - `self.speed_boost_timer = 0.0`
  - `self.speed_penalty = 1.0`
  - `self.speed_penalty_timer = 0.0`
  - `self.weapon_boost = 0`
  - `self.weapon_boost_timer = 0.0`
  - `self.weapon_malfunction = 0`
  - `self.weapon_malfunction_timer = 0.0`
- Se eliminaron los `hasattr()` checks en `core/powerup_system.py`.

---

### 16. Superposición de HUD

**Archivo:** `core/game_manager.py` L1113-1124 (actual L1010-1020)

**Problema:** `gold_text` y `score_text` compartían la posición `x=820`, superponiéndose. `enemies_text` se posicionaba en `x=920` con `SCREEN_WIDTH=900`, fuera de la pantalla.

**Solución aplicada:**
- Se reorganizaron las posiciones X: 8, 140, 250, 390, 460, 540, 590, 710, 800.
- Se eliminó `enemies_text` del HUD superior (información redundante con el conteo de enemigos visible en juego).

---

### 17. NumPy ausente en requirements.txt

**Archivo:** `requirements.txt`

**Problema:** NumPy es necesario para la síntesis de audio procedural en `sound_manager.py`, pero no estaba listado en `requirements.txt`. Solo se instalaba como fallback en `ejecutar_juego.sh`.

**Solución aplicada:**
- Se agregó `numpy>=1.24.0` a `requirements.txt`.

---

### 18. Variable `proj` indefinida

**Archivo:** `entities/player.py` L213

**Problema:** `return proj` al final de `_create_multi_shot()` referenciaba una variable no definida. No causaba error porque estaba después de un `return`, pero era código muerto que confundía.

**Solución aplicada:** *(Resuelto junto con issue #10 — se eliminaron las líneas L211-213.)*

---

### 19. Importaciones dentro de métodos

**Múltiples archivos**

**Problema:** Había 17 imports dentro de funciones/métodos. Aunque funcional, va contra PEP8 y añade overhead de 2-3µs por llamada.

**Solución aplicada:**
- Se movieron todos los imports inline al tope de sus respectivos archivos:
  - `world/objects.py`: `import math`, `import random`
  - `core/game_states.py`: `import math`
  - `core/visual_effects.py`: `import time`, `import random`
  - `entities/player.py`: `import math`
  - `core/powerup_system.py`: `import math`
  - `core/game_manager.py`: `import math`, `import random`
  - `core/character_system.py`: `import pygame`
  - `core/leaderboard.py`: `import pygame`

---

### 20. Sin `.gitignore` real

**Archivo:** `.gitignore`

**Problema:** El archivo solo contenía un comentario. `__pycache__/`, `.venv/`, `*.pyc` no se ignoraban, pudiendo subirse accidentalmente al repositorio.

**Solución aplicada:**
- Se reescribió `.gitignore` con reglas para: Python cache, entornos virtuales, IDEs, archivos del sistema, `scores.json`, y archivos `.pen`.

---

## Áreas de Mejora Pendientes

### Arquitectura y Diseño

- **Separar `GameManager`** (~1516 líneas): Es un _God Class_ que mezcla entrada, actualización, renderizado, colisiones, HUD y estados. Dividir en `CollisionSystem`, `InputHandler`, `Renderer`, `GameLoop`.
- **Sistema ECS**: Los efectos temporales se manejan con atributos sueltos. Un sistema basado en componentes sería más limpio.
- **Factory pattern para enemigos**: La creación de 6 tipos mezcla lógica de stats, escalado y selección de tipo.

### Rendimiento

- **Caché de superficies**: Se crean y descartan decenas de `pygame.Surface` por frame para efectos alpha/glow. Pre-renderizar.
- **Object pool para partículas**: `list.remove()` en partículas es O(n). Usar pool.
- **Cálculos trigonométricos**: Senos/cosenos repetidos múltiples veces por frame. Pre-calcular.

### Game Design

- **Balance de dificultad N11+**: Escalado 25% por nivel puede ser frustrante.
- **Indicadores visuales de power-ups**: El HUD muestra texto pequeño, fácil de pasar por alto.
- **Sistema de logros**: Listado como O4 en opcionales, no implementado.

### Ingeniería

- **Ampliar cobertura de tests**: Tests de integración para `GameManager` (con mock pesado), tests de estrés para el sistema de partículas/explosiones, tests de regresión para el pipeline de audio.
- **Escritura atómica de `scores.json`**: Usar `tempfile` + `os.replace()`.
- **Logging en lugar de `print()`**: Usar módulo `logging` para control de verbosidad.
- **Config externalizada**: Valores de balance hardcodeados → mover a JSON/TOML.

---

## Resumen de Cambios Realizados

| # | Problema | Archivos modificados | Líneas cambiadas |
|---|----------|---------------------|-------------------|
| 1 | Duplicación enemy_projectiles | `core/game_manager.py` | ~30 |
| 2 | Código muerto draw_hud | `core/game_manager.py` | ~43 eliminadas |
| 3 | Stats duplicadas | `entities/player.py` | ~20 |
| 4 | Import circular potencial | `config/settings.py`, `core/visual_effects.py`, `core/game_manager.py` | ~30 |
| 5 | Power-ups duplicados | `world/scene.py`, `core/game_manager.py`, `world/objects.py` | ~100 |
| 6 | README roto | `README.md` | ~140 reescritas |
| 7 | Tests automatizados | `tests/` (14 archivos) | ~1200 nuevas |
| 8 | Colisión duplicada | `core/game_manager.py` | ~50 |
| 10/18 | Dead code multi-shot | `entities/player.py` | 2 eliminadas |
| 11 | hasattr redundante | `core/game_manager.py` | 3 eliminadas |
| 12 | Boss scaling | `entities/boss_enemy.py` | ~20 |
| 14 | Límite proyectiles | `core/game_manager.py` | 3 agregadas |
| 15 | Atributos dinámicos | `entities/player.py`, `core/powerup_system.py` | ~15 |
| 16 | HUD overlap | `core/game_manager.py` | ~15 |
| 17 | numpy faltante | `requirements.txt` | 1 agregada |
| 19 | Inline imports | 8 archivos | ~17 eliminados |
| 20 | .gitignore | `.gitignore` | ~20 reescritas |
