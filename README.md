# Odisea En El Espacio by AXL

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Pygame](https://img.shields.io/badge/Pygame-2.6-00CC00?logo=pygame&logoColor=white)](https://pygame.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-186_passing-brightgreen)](tests/tests.md)
[![code style](https://img.shields.io/badge/code%20style-pep8-FFD700)](https://peps.python.org/pep-0008/)

**Un space-shooter 2D top-down con mecánicas RPG, 18 niveles, 6 tipos de enemigos, jefes finales, power-ups y tienda entre niveles.**

</div>

---

## Captura de Pantalla

<!--![Screenshot](docs/screenshot.png)-->

> *Añade una captura de pantalla o GIF animado del gameplay en `docs/screenshot.png`.*

---

## Tabla de Contenidos

- [Características](#características)
- [Arquitectura](#arquitectura)
- [Requisitos del Sistema](#requisitos-del-sistema)
- [Instalación](#instalación)
- [Ejecución](#ejecución)
- [Controles](#controles)
- [Gameplay](#gameplay)
  - [Personajes](#personajes)
  - [Enemigos](#enemigos)
  - [Armas](#armas)
  - [Power-ups y Peligros](#power-ups-y-peligros)
  - [Sistema de Progresión](#sistema-de-progresión)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Tests](#tests)
- [Tecnologías Utilizadas](#tecnologías-utilizadas)
- [Contribuir](#contribuir)
- [Licencia](#licencia)

---

## Características

- **4 personajes jugables** con estadísticas únicas (Caza Estelar, Acorazado, Francotirador, Explorador).
- **6 tipos de enemigos** con comportamientos distintos, escalado de dificultad en 18 niveles y dificultad agresiva desde el nivel 11.
- **Jefes finales** cada 2 niveles con ataques láser, puntos débiles destruibles y patrones de movimiento avanzados.
- **6 sistemas de armas** desbloqueables (Básico, Ametralladora, Escopeta, Láser, Plasma, Misil).
- **Power-ups temporales** (salud, escudo, daño, velocidad, ráfaga) y **peligros espaciales** (drenaje de escudo, lentitud, interferencia, radiación).
- **Tienda entre niveles** con mejoras permanentes y objetos consumibles.
- **Leaderboard persistente** con top 10 puntuaciones guardadas en JSON.
- **18 temas visuales** (escenarios planetarios con paletas de colores únicas).
- **Síntesis de audio procedural** — todos los efectos de sonido y música generados matemáticamente con NumPy, sin archivos externos.
- **Sistema de partículas** para explosiones, estelas de motores, brillo de power-ups y efectos de daño.
- **186 tests automatizados** con mock completo de Pygame para ejecución headless.

---

## Arquitectura

El proyecto sigue una arquitectura modular basada en principios **SOLID** y **POO**:

```
core/           → Lógica central del juego (manager, estados, sistemas)
entities/       → Entidades del juego (jugador, enemigos, proyectiles)
world/          → Objetos del mundo y escenarios
config/         → Configuración y constantes
utils/          → Utilidades matemáticas y helpers
```

### Flujo Principal

1. `main.py` inicia el bucle del juego y delega en `GameManager`.
2. `GameManager` orquesta la máquina de estados (`MenuState`, `PlayingState`, `ShopState`, etc.).
3. Cada estado gestiona su propia lógica de entrada, actualización y renderizado.
4. Las entidades (`Jugador`, `Enemigo`, `Proyectil`) heredan de `Figura` y se comunican mediante colisiones.
5. Los sistemas (`PowerUpManager`, `Leaderboard`, `Shop`) son componentes independientes inyectados en `GameManager`.

---

## Requisitos del Sistema

- **Python** 3.12 o superior
- **Pygame** 2.6+
- **NumPy** 1.24+ (para síntesis de audio)
- Sistema operativo: Linux, Windows o macOS

---

## Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/axlcraft/lpa1-taller-videojuegos.git
cd lpa1-taller-videojuegos

# 2. Crear y activar entorno virtual
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows

# 3. Instalar dependencias
pip install -r requirements.txt
```

---

## Ejecución

```bash
python main.py
```

O mediante el script de inicio:

```bash
bash ejecutar_juego.sh
```

### Ejecutar Tests

```bash
# Todos los tests
python -m pytest tests/ -v

# Con cobertura
python -m pytest tests/ --cov=entities --cov=core --cov=utils --cov=world --cov=config -v
```

> *Los tests funcionan en entornos headless gracias al mock de Pygame en `tests/conftest.py`.*

---

## Controles

|        **Tecla**     |                **Acción**                       |
|----------------------|------------------------------------------------ |
|    `W` `A` `S` `D`   |               Mover la nave                     |
|    `←` `↑` `↓` `→`   |        Mover la nave (alternativo)              |
|    Click izquierdo   |     Disparar hacia la posición del cursor       |
|    Click derecho     |       Super disparo (requiere 4 kills)          |
|          `E`         | Recoger objetos cercanos (tesoros, equipamiento)|
|          `Q`         |     Vender el primer objeto del inventario      |
|          `ESC`       |          Pausar / Salir al menú                 |
|          `F11`       |          Alternar pantalla completa             |
|   `1` `2` `3` `4`    |Seleccionar personaje en la pantalla de selección|
|        `ENTER`       |             Confirmar selección                 |

---

## Gameplay

### Personajes

|       Clase      | HP  | Ataque | Defensa | Velocidad | Habilidad Especial |
|------------------|-----|--------|---------|-----------|--------------------|
| **Caza Estelar** | 120 |   20   |    6    |    180    |  Disparo Rápido    |  
| **Acorazado**    | 180 |   15   |    12   |    140    |  Escudo Reforzado  |
| **Francotirador**| 90  |   35   |    3    |    160    |  Precisión Letal   |
| **Explorador**   | 100 |   12   |    4    |    250    |  Movilidad Mejorada|

### Enemigos

|       **Tipo**      |**HP Base**|**Ataque Base**|         **Comportamiento**           |
|---------------------|-----------|---------------|--------------------------------------|
|   **Terrestre**     |     60    |       15      |         Persigue al jugador          | 
|    **Volador**      |     45    |       10      |    Se mueve erráticamente y dispara  |
|   **Artillero**     |     80    |       20      |   Se posiciona y dispara a distancia |
|   **Élite** (N11+)  |     120   |       30      |     Rápido, dispara con frecuencia   |
| **Berserker** (N13+)|     100   |       40      |     Carga sin disparar, muy veloz    |
| **Guardián** (N15+) |     180   |       25      |Defensa alta, disparo de largo alcance|

El escalado de dificultad aumenta las estadísticas un **15 % por nivel** hasta el nivel 10, y un **25 % por nivel** a partir del nivel 11.

### Armas

|    **Arma**    |**Daño**|**Cadencia**|     **Especialidad**     |
|----------------|--------|------------|--------------------------|
|  Cañón Básico  |   25   |    0.3s    |         Estándar         |
| Ametralladora  |   18   |    0.15s   |     Alta cadencia        |
|Escopeta Plasma |   20   |    0.8s    |   5 proyectiles en cono  |
|Láser de Combate|   35   |    0.4s    | Alta velocidad, preciso  |
|Cañón de Plasma |   40   |    0.6s    |Radio de impacto aumentado|
|  Lanzamisiles  |   60   |    1.2s    |   Daño explosivo +50%    |

### Power-ups y Peligros

**Power-ups** (ventajas temporales):
- **Salud**: Recupera HP
- **Escudo**: Otorga escudo absorbente
- **Daño**: Aumenta el ataque un 50 %
- **Velocidad**: Multiplica velocidad por 1.5
- **Ráfaga**: Reduce el cooldown de disparo un 40 %

**Peligros espaciales** (desventajas):
- **Drenaje de Escudo**: Reduce el escudo
- **Lentitud**: Reduce la velocidad al 60 %
- **Interferencia**: Penaliza el daño de armas
- **Radiación**: Daño instantáneo por exposición

### Sistema de Progresión

- **Experiencia**: Obtienes XP al eliminar enemigos y recolectar tesoros.
- **Subida de nivel**: Cada 100 XP (escala ×1.4 por nivel) aumentas HP, ataque y defensa.
- **Oro**: Se obtiene de tesoros y se gasta en la tienda entre niveles.
- **Super disparo**: Cada 4 kills cargas un disparo devastador de 5 proyectiles en abanico.
- **Tienda**: Después de cada nivel puedes comprar armas, mejoras y consumibles.
- **Leaderboard**: Al morir o completar el juego, tu puntuación se guarda en el top 10.

---

## Estructura del Proyecto

```
├── main.py                     # Punto de entrada del juego
├── ejecutar_juego.sh           # Script de inicio
├── requirements.txt            # Dependencias del proyecto
├── .gitignore
├── README.md
│
├── config/
│   ├── settings.py             # Constantes, colores, temas visuales
│   └── __init__.py
│
├── core/
│   ├── game_manager.py         # Bucle principal y orquestación
│   ├── game_states.py          # Máquina de estados (10 estados)
│   ├── character_system.py     # Sistema de personajes y selección
│   ├── weapon_system.py        # Armas, fábrica y mejoras
│   ├── powerup_system.py       # Power-ups y gestor
│   ├── shop.py                 # Tienda entre niveles
│   ├── leaderboard.py          # Leaderboard persistente
│   ├── visual_effects.py       # Efectos visuales, partículas, naves
│   ├── floating_text.py        # Texto flotante (daño, XP)
│   ├── sound_manager.py        # Síntesis de audio procedural
│   └── __init__.py
│
├── entities/
│   ├── base.py                 # Figura — clase base para colisiones
│   ├── player.py               # Jugador — stats, niveles, efectos
│   ├── enemy.py                # Enemigos — 6 tipos con escalado
│   ├── boss_enemy.py           # Jefes finales — láser, puntos débiles
│   ├── projectile.py           # Proyectiles — colisiones, efectos
│   └── __init__.py
│
├── world/
│   ├── scene.py                # Escenario — niveles y distribución
│   ├── objects.py              # Objetos del mundo (tesoros, trampas,
│   │                           #   meteoritos, power-ups, peligros)
│   └── __init__.py
│
├── utils/
│   ├── math.py                 # Vector2D — operaciones vectoriales
│   └── __init__.py
│
└── tests/
    ├── conftest.py             # Mock de Pygame y fixtures
    ├── tests.md                # Documentación de la suite de tests
    ├── test_math.py            # Vector2D (9 tests)
    ├── test_base.py            # Figura (6 tests)
    ├── test_player.py          # Jugador (25 tests)
    ├── test_enemy.py           # Enemigos (17 tests)
    ├── test_boss.py            # Jefes (19 tests)
    ├── test_character.py       # Personajes (8 tests)
    ├── test_weapon.py          # Armas (24 tests)
    ├── test_powerup.py         # Power-ups (8 tests)
    ├── test_leaderboard.py     # Leaderboard (12 tests)
    ├── test_shop.py            # Tienda (8 tests)
    ├── test_objects.py         # Objetos del mundo (17 tests)
    ├── test_settings.py        # Configuración (9 tests)
    ├── test_integration.py     # Integración (12 tests)
    └── __init__.py
```

---

## Tests

El proyecto incluye **186 tests automatizados** con `pytest` que cubren toda la lógica de negocio:

- Colisiones y detección de impactos
- Cálculo de daño con defensa y escudo
- Escalado de enemigos y jefes por nivel
- Sistema de armas (6 tipos, cooldowns, proyectiles)
- Power-ups (aplicación, expiración, colisiones)
- Leaderboard (persistencia, ordenamiento, archivo corrupto)
- Tienda (compras, límites, reinicio)
- Personajes (estadísticas, selección)
- Objetos del mundo (trampas, tesoros, meteoritos, peligros)
- Integración multi-módulo

Consulta [`tests/tests.md`](tests/tests.md) para más detalles.

---

## Tecnologías Utilizadas

- **Python 3.12+** — Lenguaje principal
- **Pygame 2.6+** — Motor gráfico y de audio
- **NumPy 1.24+** — Síntesis de audio procedural
- **pytest 9+** — Framework de tests
- **pytest-cov** — Medición de cobertura

---

## Contribuir

Las contribuciones son bienvenidas. Para mantener la calidad del proyecto, sigue estos pasos:

1. Haz un **fork** del repositorio.
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`).
3. Haz commit de tus cambios (`git commit -am 'Añade nueva funcionalidad'`).
4. Pushea a tu fork (`git push origin feature/nueva-funcionalidad`).
5. Abre un **Pull Request** desde GitHub.

### Guía de Estilo

- Sigue **PEP 8** para el código Python.
- Mantén la cobertura de tests por encima del 80 %.
- Documenta clases y métodos públicos con docstrings.
- Usa nombres descriptivos en español para la lógica del juego y en inglés para utilidades genéricas.

---

## Licencia

Este proyecto se distribuye bajo la **Licencia MIT**. Consulta el archivo [`LICENSE`](LICENSE) para los términos completos.

*El proyecto Odisea En El Espacio by AXL es un trabajo académico de Programación Orientada a Objetos. Se permite su uso, modificación y distribución siempre que se mantenga el aviso de copyright original.*
--- 

<div align="center">

**Desarrollado por [@axlcraft](https://github.com/axlcraft)** • Proyecto académico de Programación Orientada a Objetos

</div>
