from world.objects import (
    Objeto, TrampaExplosiva, Tesoro, ArmamentoDefensa,
    Meteorito, PowerUpEspacial, EscudoEnergia,
    ImpulsoVelocidad, MejoraArmas, ReparacionNano,
    PeligroEspacial, DrenajeEscudo, VirulenciaEspacial,
    InterferenciaSistemas, RadiacionCosmica
)
from utils.math import Vector2D


class TestObjeto:
    def test_creation(self):
        o = Objeto(100, 200, "TestObject")
        assert o.pos.x == 100
        assert o.pos.y == 200
        assert o.name == "TestObject"


class TestTrampaExplosiva:
    def test_creation(self):
        t = TrampaExplosiva(100, 200, 50, 30)
        assert t.pos.x == 100
        assert t.pos.y == 200
        assert t.alcance == 50
        assert t.dano == 30

    def test_detonar_hits(self):
        t = TrampaExplosiva(0, 0, 50, 30)
        from entities.base import Figura
        target = Figura(30, 0, 10, (255, 0, 0))
        affected = t.detonar([target])
        assert len(affected) == 1
        assert affected[0][1] == 30

    def test_detonar_miss(self):
        t = TrampaExplosiva(0, 0, 20, 30)
        from entities.base import Figura
        target = Figura(100, 100, 10, (255, 0, 0))
        affected = t.detonar([target])
        assert len(affected) == 0

    def test_detonar_multiple(self):
        t = TrampaExplosiva(0, 0, 60, 30)
        from entities.base import Figura
        targets = [Figura(20, 0, 10, (255, 0, 0)), Figura(50, 0, 10, (0, 255, 0))]
        affected = t.detonar(targets)
        assert len(affected) == 2


class TestTesoro:
    def test_creation(self):
        t = Tesoro(100, 200, 50)
        assert t.valor == 50
        assert t.name == "Tesoro"


class TestArmamentoDefensa:
    def test_creation(self):
        a = ArmamentoDefensa(100, 200, 5, 3, 100)
        assert a.bonus_atk == 5
        assert a.bonus_def == 3
        assert a.price == 100


class TestMeteorito:
    def test_creation_small(self):
        m = Meteorito(100, 200, size=1)
        assert m.radius == 15
        assert m.damage == 15
        assert m.speed == 2.0

    def test_creation_medium(self):
        m = Meteorito(100, 200, size=2)
        assert m.radius == 25
        assert m.damage == 25
        assert m.speed == 1.5

    def test_creation_large(self):
        m = Meteorito(100, 200, size=3)
        assert m.radius == 35
        assert m.damage == 35
        assert m.speed == 1.0

    def test_collision(self):
        m = Meteorito(100, 100, size=2)
        assert m.collides_with(Vector2D(110, 110), 10) is True

    def test_no_collision_far(self):
        m = Meteorito(100, 100, size=2)
        assert m.collides_with(Vector2D(500, 500), 10) is False


class TestPowerUpEspacial:
    def test_creation(self):
        p = PowerUpEspacial(100, 200, "test", 10.0)
        assert p.power_type == "test"
        assert p.duration == 10.0
        assert p.collected is False

    def test_collision(self):
        p = PowerUpEspacial(100, 100, "test", 10.0)
        assert p.collides_with(Vector2D(110, 110), 10) is True


class TestEscudoEnergia:
    def test_apply(self, player):
        e = EscudoEnergia(100, 100)
        msg = e.apply_effect(player)
        assert "escudo" in msg.lower()
        assert player.shield_hp >= 50


class TestImpulsoVelocidad:
    def test_apply(self, player):
        i = ImpulsoVelocidad(100, 100)
        msg = i.apply_effect(player)
        assert "velocidad" in msg.lower()
        assert player.speed_boost == 1.5


class TestMejoraArmas:
    def test_apply(self, player):
        m = MejoraArmas(100, 100)
        msg = m.apply_effect(player)
        assert "arma" in msg.lower()
        assert player.weapon_boost == 10


class TestReparacionNano:
    def test_apply_heals(self, player):
        player.hp = 10
        r = ReparacionNano(100, 100)
        msg = r.apply_effect(player)
        assert "hp" in msg.lower() or "reparación" in msg.lower()
        assert player.hp > 10


class TestPeligroEspacial:
    def test_creation(self):
        p = PeligroEspacial(100, 200, "test_hazard", 8.0)
        assert p.hazard_type == "test_hazard"
        assert p.triggered is False


class TestDrenajeEscudo:
    def test_apply_drains(self, player):
        player.shield_hp = 50
        d = DrenajeEscudo(100, 100)
        msg = d.apply_effect(player)
        assert "escudo" in msg.lower()
        assert player.shield_hp < 50


class TestVirulenciaEspacial:
    def test_apply_slows(self, player):
        v = VirulenciaEspacial(100, 100)
        msg = v.apply_effect(player)
        assert "motor" in msg.lower() or "velocidad" in msg.lower()
        assert player.speed_penalty == 0.6


class TestInterferenciaSistemas:
    def test_apply_weakens(self, player):
        i = InterferenciaSistemas(100, 100)
        msg = i.apply_effect(player)
        assert "interferencia" in msg.lower() or "daño" in msg.lower()
        assert player.weapon_malfunction == 8


class TestRadiacionCosmica:
    def test_apply_damages(self, player):
        r = RadiacionCosmica(100, 100)
        hp_before = player.hp
        msg = r.apply_effect(player)
        assert "radiación" in msg.lower() or "hp" in msg.lower()
        assert player.hp <= hp_before
