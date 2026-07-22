from utils.math import Vector2D


class TestVector2D:
    def test_creation(self):
        v = Vector2D(3, 4)
        assert v.x == 3
        assert v.y == 4

    def test_add(self):
        a = Vector2D(1, 2)
        b = Vector2D(3, 4)
        c = a + b
        assert c.x == 4
        assert c.y == 6

    def test_sub(self):
        a = Vector2D(5, 7)
        b = Vector2D(3, 4)
        c = a - b
        assert c.x == 2
        assert c.y == 3

    def test_mul(self):
        v = Vector2D(3, 4)
        r = v * 2
        assert r.x == 6
        assert r.y == 8

    def test_magnitude(self):
        v = Vector2D(3, 4)
        assert v.magnitude() == 5.0

    def test_magnitude_zero(self):
        v = Vector2D(0, 0)
        assert v.magnitude() == 0.0

    def test_normalized(self):
        v = Vector2D(3, 4)
        n = v.normalized()
        assert abs(n.x - 0.6) < 0.001
        assert abs(n.y - 0.8) < 0.001
        assert abs(n.magnitude() - 1.0) < 0.001

    def test_normalized_zero(self):
        v = Vector2D(0, 0)
        n = v.normalized()
        assert n.x == 0
        assert n.y == 0

    def test_to_int_tuple(self):
        v = Vector2D(3.7, 4.2)
        t = v.to_int_tuple()
        assert t == (3, 4)
        assert isinstance(t[0], int)
        assert isinstance(t[1], int)
