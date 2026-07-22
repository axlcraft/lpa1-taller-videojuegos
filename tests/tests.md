# Suite de Tests — LPA1 Taller Videojuegos

## Ejecutar Tests

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar todos los tests
python -m pytest tests/ -v

# Ejecutar con cobertura
python -m pytest tests/ --cov=entities --cov=core --cov=utils --cov=world --cov=config -v

# Ejecutar un archivo específico
python -m pytest tests/test_math.py -v

# Ejecutar una clase específica
python -m pytest tests/test_player.py::TestJugadorLeveling -v

# Ejecutar una función específica
python -m pytest tests/test_math.py::TestVector2D::test_normalized -v
```

## Archivos de Test

| Archivo | Módulo | Qué prueba |
|---------|--------|------------|
| `test_math.py` | `utils/math.py` | `Vector2D` — suma, resta, multiplicación escalar, magnitud, normalización, conversión a entero |
| `test_base.py` | `entities/base.py` | `Figura` — creación, cálculo de distancia, detección de colisiones (impacto, fallo, tangencia, consigo mismo) |
| `test_player.py` | `entities/player.py` | `Jugador` — creación por clase de personaje, daño con/sin escudo/invulnerabilidad, subida de nivel, cargas de superdisparo, sistema de efectos (velocidad, daño, ráfaga, expiración) |
| `test_enemy.py` | `entities/enemy.py` | `Enemigo` — creación por tipo (terrestre, volador, artillero, élite, berserker, guardián), escalado por nivel (1-20), daño/defensa, movimiento, disparo, propiedad de proyectiles |
| `test_boss.py` | `entities/boss_enemy.py` | `BossEnemy` + `WeakPoint` — creación, escalado de estadísticas (niveles 6-18), daño/destrucción de puntos débiles, derrota del jefe, sistema láser (carga, disparo, enfriamiento), patrones de movimiento |
| `test_character.py` | `core/character_system.py` | `CharacterManager` — personajes disponibles, estadísticas por personaje (caza estelar/acorazado/francotirador/explorador), manejo de personaje inválido |
| `test_weapon.py` | `core/weapon_system.py` | `Weapon` — creación, enfriamiento, disparo, tipos de arma; `WeaponFactory` — creación de los 6 tipos de armas; `WeaponUpgrade` — mejoras |
| `test_powerup.py` | `core/powerup_system.py` | `PowerUpManager` — colisiones, eliminación, limpieza, temporizador de aparición, aparición tras intervalo |
| `test_leaderboard.py` | `core/leaderboard.py` | `Leaderboard` — agregar puntuación, orden descendente, límite, persistencia (guardar/cargar), mejor puntuación por jugador, archivo corrupto |
| `test_shop.py` | `core/shop.py` | `Shop` + `ShopItem` — propiedades de artículos, compra, límite de compras, tipos de artículo, reinicio de compras |
| `test_objects.py` | `world/objects.py` | `Objeto`, `TrampaExplosiva`, `Tesoro`, `ArmamentoDefensa`, `Meteorito`, `PowerUpEspacial`, `EscudoEnergia`, `ImpulsoVelocidad`, `MejoraArmas`, `ReparacionNano`, `PeligroEspacial`, `DrenajeEscudo`, `VirulenciaEspacial`, `InterferenciaSistemas`, `RadiacionCosmica` |
| `test_settings.py` | `config/settings.py` | Constantes (`SCREEN_WIDTH`, `SCREEN_HEIGHT`, `FPS`), funciones estelares (color de fondo, color de acento, nombre), diccionario de colores |
| `test_integration.py` | multi-módulo | Daño jugador vs enemigo, interacciones de proyectiles (jugador→enemigo, enemigo→jugador), experiencia por eliminaciones, acumulación de supercarga, escalado de enemigos, consistencia de jefes entre niveles |

## Objetivos de Cobertura

- **utils/math.py**: 100%
- **entities/base.py**: 100%
- **entities/player.py**: >90%
- **entities/enemy.py**: >85%
- **entities/boss_enemy.py**: >85%
- **core/character_system.py**: 100%
- **core/weapon_system.py**: >90%
- **core/powerup_system.py**: >85%
- **core/leaderboard.py**: >90%
- **core/shop.py**: >80%
- **world/objects.py**: >80%
- **config/settings.py**: >80%

## Notas

- SDL se inicializa con drivers dummy de video/audio en `conftest.py` para que los tests funcionen en entornos sin pantalla.
- `pygame.init()` se llama una sola vez en `conftest.py` — los tests individuales no deben llamarlo.
- Los tests de leaderboard usan `tmp_path` (fixture integrada de pytest) para no contaminar el archivo real de puntuaciones.
- El bucle principal del juego (`game_manager.py`) y el renderizado de escenas/mundo no tienen tests intencionalmente — requieren una pantalla activa y un mock muy pesado. La lógica de negocio vive en los módulos probados arriba.
