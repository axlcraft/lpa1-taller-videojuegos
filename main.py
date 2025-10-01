#!/usr/bin/env python3
"""
Taller Videojuegos - Demo interactiva con Pygame

Juego 2D tipo RPG de acción que implementa los principios de POO.
- Mecánicas: movimiento, disparo, IA básica, trampas explosivas, tesoros, inventario, XP y subida de nivel
- Controles:
    WASD - mover
    Mouse left - disparar hacia el cursor
    E - recoger objetos cercanos (tesoro / trampas como item)
    Q - vender primer item del inventario (simula tienda)
    ESC - salir

Proyecto refactorizado con arquitectura modular para facilitar mantenimiento y extensibilidad.
"""
from core.game_manager import GameManager


def main():
    """Función principal que inicia el juego."""
    print("Iniciando Taller Videojuegos...")
    print("Controles:")
    print("  WASD - Mover jugador")
    print("  Click izquierdo - Disparar hacia el cursor")
    print("  E - Recoger objetos cercanos")
    print("  Q - Vender primer objeto del inventario")
    print("  ESC - Salir del juego")
    print("=" * 50)
    
    try:
        game = GameManager()
        game.run()
        print("¡Gracias por jugar!")
    except KeyboardInterrupt:
        print("\nJuego interrumpido por el usuario.")
    except Exception as e:
        print(f"Error al ejecutar el juego: {e}")
        raise


# -------------------------
# Punto de entrada
# -------------------------
if __name__ == "__main__":
    main()