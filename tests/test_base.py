from entities.base import Figura
from utils.math import Vector2D


class TestFigura:
    def test_creation(self):
        f = Figura(100, 200, 15, (255, 0, 0))
        assert f.pos.x == 100
        assert f.pos.y == 200
        assert f.radio == 15
        assert f.color == (255, 0, 0)
        assert f.activo is True

    def test_distance_to(self):
        a = Figura(0, 0, 10, (255, 0, 0))
        b = Figura(3, 4, 10, (0, 255, 0))
        d = a.distance_to(b)
        assert d == 5.0

    def test_collides_with_hit(self):
        a = Figura(0, 0, 10, (255, 0, 0))
        b = Figura(15, 0, 10, (0, 255, 0))
        assert a.collides_with(b) is True

    def test_collides_with_miss(self):
        a = Figura(0, 0, 10, (255, 0, 0))
        b = Figura(30, 0, 10, (0, 255, 0))
        assert a.collides_with(b) is False

    def test_collides_with_touching(self):
        a = Figura(0, 0, 10, (255, 0, 0))
        b = Figura(20, 0, 10, (0, 255, 0))
        assert a.collides_with(b) is True

    def test_collides_with_self(self):
        a = Figura(0, 0, 10, (255, 0, 0))
        assert a.collides_with(a) is True
