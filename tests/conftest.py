import sys
import os
from unittest.mock import MagicMock

os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'


class MockSurface:
    def __init__(self, size=(10, 10), flags=0, surface=None):
        self._size = size
        self._width, self._height = size
        self._alpha = 255
        self._colorkey = None

    def get_width(self): return self._width
    def get_height(self): return self._height
    def get_size(self): return self._size
    def get_rect(self): return MockRect(0, 0, self._width, self._height)
    def set_alpha(self, val): self._alpha = val
    def get_alpha(self): return self._alpha
    def set_colorkey(self, color, flags=0): self._colorkey = color
    def blit(self, source, dest, area=None, special_flags=0): pass
    def fill(self, color, rect=None, special_flags=0): pass
    def convert_alpha(self): return self
    def convert(self): return self
    def copy(self): return MockSurface(self._size)
    def subsurface(self, rect): return MockSurface((rect[2], rect[3]))
    def scroll(self, dx=0, dy=0): pass
    def lock(self): pass
    def unlock(self): pass
    def get_at(self, pos): return (0, 0, 0, 255)
    def set_at(self, pos, color): pass
    def __repr__(self): return f"MockSurface({self._size})"


class MockRect:
    def __init__(self, *args):
        if len(args) == 4:
            self._x, self._y, self._w, self._h = args
        elif len(args) == 2:
            p1, p2 = args[0], args[1]
            self._x = min(p1[0], p2[0])
            self._y = min(p1[1], p2[1])
            self._w = abs(p2[0] - p1[0])
            self._h = abs(p2[1] - p1[1])
        elif len(args) == 1:
            self._x, self._y, self._w, self._h = args[0]
        else:
            self._x = self._y = self._w = self._h = 0
        self.x = self._x
        self.y = self._y
        self.w = self._w
        self.h = self._h
        self.top = self._y
        self.left = self._x
        self.bottom = self._y + self._h
        self.right = self._x + self._w
        self.centerx = self._x + self._w // 2
        self.centery = self._y + self._h // 2
        self.center = (self.centerx, self.centery)
        self.topleft = (self._x, self._y)
        self.size = (self._w, self._h)
        self.width = self._w
        self.height = self._h

    def collidepoint(self, x, y):
        return self._x <= x <= self._x + self._w and self._y <= y <= self._y + self._h

    def colliderect(self, other):
        return (self._x < other._x + other._w and other._x < self._x + self._w
                and self._y < other._y + other._h and other._y < self._y + self._h)

    def inflate(self, x, y):
        return MockRect(self._x - x//2, self._y - y//2, self._w + x, self._h + y)

    def move(self, x, y):
        return MockRect(self._x + x, self._y + y, self._w, self._h)

    def clamp(self, other):
        nx = max(other._x, min(self._x, other._x + other._w - self._w))
        ny = max(other._y, min(self._y, other._y + other._h - self._h))
        return MockRect(nx, ny, self._w, self._h)

    def __repr__(self):
        return f"MockRect({self._x}, {self._y}, {self._w}, {self._h})"


class MockFont:
    def __init__(self, name=None, size=None):
        self.name = name
        self.size = size

    def render(self, text, antialias, color, bgcolor=None):
        return MockSurface((len(text) * (self.size or 10), self.size or 10))

    def size(self, text):
        return (len(text) * (self.size or 10), self.size or 10)


class MockClock:
    def tick(self, fps=60): return 16
    def get_fps(self): return 60.0


class MockEvent:
    def __init__(self, type, **kwargs):
        self.type = type
        for k, v in kwargs.items():
            setattr(self, k, v)


mock_module = MagicMock()
mock_module.init = MagicMock()
mock_module.quit = MagicMock()
mock_module.display.set_mode = MagicMock(return_value=MockSurface((900, 700)))
mock_module.display.set_caption = MagicMock()
mock_module.display.flip = MagicMock()
mock_module.display.get_surface = MagicMock(return_value=MockSurface((900, 700)))
mock_module.display.get_driver = MagicMock(return_value=b'dummy')
mock_module.font = MagicMock()
mock_module.font.Font = MockFont
mock_module.font.SysFont = MockFont
mock_module.font.get_init = MagicMock(return_value=True)
mock_module.font.init = MagicMock()
mock_module.Surface = MockSurface
mock_module.Rect = MockRect
mock_module.time = MagicMock()
mock_module.time.Clock = MockClock
mock_module.time.get_ticks = MagicMock(return_value=1000)
mock_module.event.get = MagicMock(return_value=[])
mock_module.event.wait = MagicMock(return_value=MockEvent(0))
mock_module.event.Event = MockEvent
mock_module.image.load = MagicMock(return_value=MockSurface((10, 10)))
mock_module.transform.scale = MagicMock(return_value=MockSurface((10, 10)))
mock_module.transform.rotate = MagicMock(return_value=MockSurface((10, 10)))
mock_module.transform.flip = MagicMock(return_value=MockSurface((10, 10)))
mock_module.draw.circle = MagicMock()
mock_module.draw.rect = MagicMock()
mock_module.draw.line = MagicMock()
mock_module.draw.polygon = MagicMock()
mock_module.draw.arc = MagicMock()
mock_module.draw.ellipse = MagicMock()
mock_module.mixer = MagicMock()
mock_module.mixer.Sound = MagicMock()
mock_module.mixer.init = MagicMock()
mock_module.mixer.get_init = MagicMock(return_value=(22050, -16, 2))
mock_module.mixer.music.load = MagicMock()
mock_module.mixer.music.play = MagicMock()
mock_module.mixer.music.stop = MagicMock()
mock_module.mixer.music.set_volume = MagicMock()
mock_module.key.get_pressed = MagicMock(return_value=[0] * 512)
mock_module.MOUSEBUTTONDOWN = 1
mock_module.KEYDOWN = 2
mock_module.KEYUP = 3
mock_module.QUIT = 4
mock_module.K_LEFT = 276
mock_module.K_RIGHT = 275
mock_module.K_UP = 273
mock_module.K_DOWN = 274
mock_module.K_SPACE = 32
mock_module.K_x = 120
mock_module.K_z = 122
mock_module.K_1 = 49
mock_module.K_2 = 50
mock_module.K_3 = 51
mock_module.K_4 = 52
mock_module.K_5 = 53
mock_module.K_ESCAPE = 27
mock_module.K_RETURN = 13
mock_module.K_TAB = 9
mock_module.K_LSHIFT = 304
mock_module.K_RSHIFT = 303
mock_module.BLEND_ALPHA_SDL2 = 1
mock_module.SRCALPHA = 0x00010000
mock_module.HWSURFACE = 0x00000001
mock_module.FULLSCREEN = 0x80000000
mock_module.RESIZABLE = 0x00000010
mock_module.NOFRAME = 0x00000020
mock_module.SCALED = 0x00000040

sys.modules['pygame'] = mock_module

import pygame
pygame.init()

import pytest


@pytest.fixture
def mock_font():
    return MockFont("test", 20)


@pytest.fixture
def mock_big_font():
    return MockFont("test", 40)


@pytest.fixture
def fighter_character():
    from core.character_system import CharacterManager
    mgr = CharacterManager()
    return mgr.get_character('fighter')


@pytest.fixture
def tank_character():
    from core.character_system import CharacterManager
    mgr = CharacterManager()
    return mgr.get_character('tank')


@pytest.fixture
def sniper_character():
    from core.character_system import CharacterManager
    mgr = CharacterManager()
    return mgr.get_character('sniper')


@pytest.fixture
def scout_character():
    from core.character_system import CharacterManager
    mgr = CharacterManager()
    return mgr.get_character('scout')


@pytest.fixture
def player(fighter_character):
    from entities.player import Jugador
    return Jugador(400, 300, "TestPilot", fighter_character)


@pytest.fixture
def enemy_terrestre():
    from entities.enemy import Enemigo
    return Enemigo(200, 200, "terrestre", level=1)


@pytest.fixture
def enemy_volador():
    from entities.enemy import Enemigo
    return Enemigo(200, 200, "volador", level=1)


@pytest.fixture
def enemy_artillero():
    from entities.enemy import Enemigo
    return Enemigo(200, 200, "artillero", level=5)


@pytest.fixture
def boss():
    from entities.boss_enemy import BossEnemy
    return BossEnemy(400, 200, level=6)


@pytest.fixture
def boss_high_level():
    from entities.boss_enemy import BossEnemy
    return BossEnemy(400, 200, level=15)


@pytest.fixture
def projectile():
    from entities.projectile import Proyectil
    from utils.math import Vector2D
    return Proyectil(100, 100, Vector2D(1, 0), speed=400, damage=20, owner_type="player")


@pytest.fixture
def enemy_projectile():
    from entities.projectile import Proyectil
    from utils.math import Vector2D
    return Proyectil(100, 100, Vector2D(0, 1), speed=300, damage=15, owner_type="enemy")


@pytest.fixture
def scene():
    from world.scene import Escenario
    return Escenario(900, 600, 1.0, 1)


@pytest.fixture
def shop():
    from core.shop import Shop
    return Shop(MockFont("test", 20), MockFont("test", 40))


@pytest.fixture
def leaderboard(tmp_path):
    from core.leaderboard import Leaderboard
    lb = Leaderboard()
    lb.scores_file = str(tmp_path / "test_scores.json")
    return lb


@pytest.fixture
def powerup_manager():
    from core.powerup_system import PowerUpManager
    return PowerUpManager()


@pytest.fixture
def character_manager():
    from core.character_system import CharacterManager
    return CharacterManager()
