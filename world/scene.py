"""
Escenario del juego.
Contiene la clase Escenario que maneja la generación y gestión del mundo.
"""
import random
from typing import List
from entities.enemy import Enemigo
from world.objects import (TrampaExplosiva, Tesoro, ArmamentoDefensa, Meteorito,
                          EscudoEnergia, ImpulsoVelocidad, MejoraArmas, ReparacionNano,
                          DrenajeEscudo, VirulenciaEspacial, InterferenciaSistemas, RadiacionCosmica)


class Escenario:
    """Generador y gestor del escenario del juego."""

    def __init__(self, width: int, height: int, difficulty: float = 1.0):
        """
        Inicializa el escenario.
        
        Args:
            width: Ancho del escenario
            height: Alto del escenario
            difficulty: Nivel de dificultad (afecta generación)
        """
        self.width = width
        self.height = height
        self.difficulty = difficulty
        self.enemies: List[Enemigo] = []
        self.traps: List[TrampaExplosiva] = []
        self.treasures: List[Tesoro] = []
        self.items_ground: List[ArmamentoDefensa] = []
        self.meteorites: List[Meteorito] = []
        # Nuevos objetos espaciales
        self.power_ups: List = []  # Power-ups (ventajas)
        self.hazards: List = []    # Peligros (desventajas)

    def generate(self, n_enemies: int = 5, n_treasures: int = 4, n_traps: int = 3, 
                n_meteorites: int = 2, n_power_ups: int = 2, n_hazards: int = 2) -> None:
        """
        Genera un nuevo escenario completo con todos los objetos espaciales.
        
        Args:
            n_enemies: Número de enemigos a generar
            n_treasures: Número de tesoros a generar
            n_traps: Número de trampas a generar
            n_meteorites: Número de meteoritos a generar
            n_power_ups: Número de power-ups (ventajas) a generar
            n_hazards: Número de peligros (desventajas) a generar
        """
        # Generar enemigos
        self.enemies = []
        for _ in range(n_enemies):
            x = random.uniform(50, self.width - 50)
            y = random.uniform(50, self.height - 50)
            tipo = random.choice(["terrestre", "volador"])
            self.enemies.append(Enemigo(x, y, tipo))
        
        # Generar tesoros
        self.treasures = []
        for _ in range(n_treasures):
            x = random.uniform(40, self.width - 40)
            y = random.uniform(40, self.height - 40)
            valor = random.randint(10, 120)
            self.treasures.append(Tesoro(x, y, valor))
        
        # Generar trampas
        self.traps = []
        for _ in range(n_traps):
            x = random.uniform(40, self.width - 40)
            y = random.uniform(40, self.height - 40)
            alcance = random.uniform(30.0, 60.0)
            dano = random.randint(12, 36)
            self.traps.append(TrampaExplosiva(x, y, alcance, dano))
        
        # Generar equipamiento ocasionalmente
        self.items_ground = []
        if random.random() < 0.6:
            x = random.uniform(40, self.width - 40)
            y = random.uniform(40, self.height - 40)
            self.items_ground.append(ArmamentoDefensa(x, y, bonus_atk=4, bonus_def=2, price=40))
        
        # Generar meteoritos
        self.meteorites = []
        for _ in range(n_meteorites):
            x = random.uniform(60, self.width - 60)
            y = random.uniform(60, self.height - 60)
            size = random.choice([1, 1, 2, 3])  # Más probabilidad de pequeños
            self.meteorites.append(Meteorito(x, y, size))
        
        # Generar power-ups (ventajas espaciales)
        self.power_ups = []
        power_up_classes = [EscudoEnergia, ImpulsoVelocidad, MejoraArmas, ReparacionNano]
        for _ in range(n_power_ups):
            x = random.uniform(80, self.width - 80)
            y = random.uniform(80, self.height - 80)
            power_up_class = random.choice(power_up_classes)
            self.power_ups.append(power_up_class(x, y))
        
        # Generar peligros espaciales (desventajas)
        self.hazards = []
        hazard_classes = [DrenajeEscudo, VirulenciaEspacial, InterferenciaSistemas, RadiacionCosmica]
        for _ in range(n_hazards):
            x = random.uniform(80, self.width - 80)
            y = random.uniform(80, self.height - 80)
            hazard_class = random.choice(hazard_classes)
            self.hazards.append(hazard_class(x, y))
    
    def update_space_objects(self, dt: float) -> None:
        """
        Actualiza todos los objetos espaciales (power-ups y peligros).
        
        Args:
            dt: Delta time en segundos
        """
        # Actualizar power-ups
        for power_up in self.power_ups[:]:
            power_up.update(dt)
            # Remover power-ups expirados
            if hasattr(power_up, 'lifetime') and power_up.lifetime <= 0:
                self.power_ups.remove(power_up)
        
        # Actualizar peligros
        for hazard in self.hazards[:]:
            hazard.update(dt)
            # Remover peligros expirados
            if hasattr(hazard, 'lifetime') and hazard.lifetime <= 0:
                self.hazards.remove(hazard)
    
    def clear_all(self) -> None:
        """Limpia todos los objetos del escenario."""
        self.enemies.clear()
        self.traps.clear()
        self.treasures.clear()
        self.items_ground.clear()
        self.meteorites.clear()
        self.power_ups.clear()
        self.hazards.clear()
    
    def get_all_objects(self) -> dict:
        """
        Retorna un diccionario con todos los objetos del escenario.
        Útil para sistemas de colisión y renderizado.
        """
        return {
            'enemies': self.enemies,
            'traps': self.traps,
            'treasures': self.treasures,
            'items_ground': self.items_ground,
            'meteorites': self.meteorites,
            'power_ups': self.power_ups,
            'hazards': self.hazards
        }