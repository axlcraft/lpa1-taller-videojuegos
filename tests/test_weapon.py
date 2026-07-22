from core.weapon_system import Weapon, WeaponType, WeaponFactory, WeaponUpgrade
from utils.math import Vector2D


class TestWeaponType:
    def test_constants(self):
        assert WeaponType.BASIC == "basic"
        assert WeaponType.RAPID_FIRE == "rapid_fire"
        assert WeaponType.SHOTGUN == "shotgun"
        assert WeaponType.LASER == "laser"
        assert WeaponType.PLASMA == "plasma"
        assert WeaponType.MISSILE == "missile"


class TestWeapon:
    def test_create_basic(self):
        w = Weapon(WeaponType.BASIC, "Basic", 25, 0.3, 400, (255, 255, 255))
        assert w.weapon_type == WeaponType.BASIC
        assert w.damage == 25
        assert w.cooldown == 0.3
        assert w.projectile_speed == 400

    def test_can_shoot(self):
        w = Weapon(WeaponType.BASIC, "Basic", 25, 0.3, 400, (255, 255, 255))
        assert w.can_shoot() is True

    def test_cannot_shoot_on_cooldown(self):
        w = Weapon(WeaponType.BASIC, "Basic", 25, 0.3, 400, (255, 255, 255))
        w.shoot(Vector2D(100, 100), Vector2D(1, 0), "player")
        assert w.can_shoot() is False

    def test_cooldown_decreases(self):
        w = Weapon(WeaponType.BASIC, "Basic", 25, 0.3, 400, (255, 255, 255))
        w.shoot(Vector2D(100, 100), Vector2D(1, 0), "player")
        w.update(0.3)
        assert w.can_shoot() is True

    def test_basic_shoot(self):
        w = Weapon(WeaponType.BASIC, "Basic", 25, 0.3, 400, (255, 255, 255))
        projs = w.shoot(Vector2D(100, 100), Vector2D(1, 0), "player")
        assert len(projs) == 1
        assert projs[0].damage == 25
        assert projs[0].owner_type == "player"

    def test_enemy_shoot(self):
        w = Weapon(WeaponType.BASIC, "Basic", 25, 0.3, 400, (255, 255, 255))
        projs = w.shoot(Vector2D(100, 100), Vector2D(0, 1), "enemy")
        assert projs[0].owner_type == "enemy"
        assert projs[0].can_damage_player() is True

    def test_rapid_fire_projectile(self):
        w = WeaponFactory.create_weapon(WeaponType.RAPID_FIRE)
        projs = w.shoot(Vector2D(100, 100), Vector2D(1, 0), "player")
        assert len(projs) == 1
        assert w.weapon_type == WeaponType.RAPID_FIRE

    def test_shotgun_produces_multiple(self):
        w = WeaponFactory.create_weapon(WeaponType.SHOTGUN)
        projs = w.shoot(Vector2D(100, 100), Vector2D(1, 0), "player")
        assert len(projs) == 5

    def test_shotgun_damage_reduced(self):
        w = WeaponFactory.create_weapon(WeaponType.SHOTGUN)
        projs = w.shoot(Vector2D(100, 100), Vector2D(1, 0), "player")
        assert projs[0].damage < w.damage

    def test_laser_special_effect(self):
        w = WeaponFactory.create_weapon(WeaponType.LASER)
        projs = w.shoot(Vector2D(100, 100), Vector2D(1, 0), "player")
        assert projs[0].special_effect == "laser"

    def test_laser_high_speed(self):
        w = Weapon(WeaponType.LASER, "Laser", 35, 0.4, 600, (0, 255, 255))
        projs = w.shoot(Vector2D(100, 100), Vector2D(1, 0), "player")
        assert projs[0].vel_x > 500

    def test_plasma_has_special_effect(self):
        w = WeaponFactory.create_weapon(WeaponType.PLASMA)
        projs = w.shoot(Vector2D(100, 100), Vector2D(1, 0), "player")
        assert projs[0].special_effect == "plasma"

    def test_missile_damage_boosted(self):
        w = WeaponFactory.create_weapon(WeaponType.MISSILE)
        projs = w.shoot(Vector2D(100, 100), Vector2D(1, 0), "player")
        assert projs[0].damage > w.damage

    def test_cannot_shoot_returns_empty(self):
        w = Weapon(WeaponType.BASIC, "Basic", 25, 0.3, 400, (255, 255, 255))
        w.shoot(Vector2D(100, 100), Vector2D(1, 0), "player")
        empty = w.shoot(Vector2D(200, 200), Vector2D(1, 0), "player")
        assert empty == []


class TestWeaponFactory:
    def test_create_basic(self):
        w = WeaponFactory.create_weapon(WeaponType.BASIC)
        assert w.name == "Cañón Básico"
        assert w.damage == 25

    def test_create_rapid_fire(self):
        w = WeaponFactory.create_weapon(WeaponType.RAPID_FIRE)
        assert w.name == "Ametralladora"
        assert w.damage == 18
        assert w.cooldown < 0.3

    def test_create_shotgun(self):
        w = WeaponFactory.create_weapon(WeaponType.SHOTGUN)
        assert w.name == "Escopeta Plasma"
        assert w.weapon_type == WeaponType.SHOTGUN

    def test_create_laser(self):
        w = WeaponFactory.create_weapon(WeaponType.LASER)
        assert w.name == "Láser de Combate"

    def test_create_plasma(self):
        w = WeaponFactory.create_weapon(WeaponType.PLASMA)
        assert w.name == "Cañón de Plasma"

    def test_create_missile(self):
        w = WeaponFactory.create_weapon(WeaponType.MISSILE)
        assert w.name == "Lanzamisiles"

    def test_create_invalid_fallback(self):
        w = WeaponFactory.create_weapon("invalid")
        assert w.weapon_type == WeaponType.BASIC

    def test_projectile_color_varies(self):
        basic = WeaponFactory.create_weapon(WeaponType.BASIC)
        laser = WeaponFactory.create_weapon(WeaponType.LASER)
        assert basic.projectile_color != laser.projectile_color


class TestWeaponUpgrade:
    def test_creation(self):
        u = WeaponUpgrade("Test Upg", "+10 dmg", WeaponType.BASIC, damage_bonus=10)
        assert u.name == "Test Upg"
        assert u.damage_bonus == 10
        assert u.weapon_type == WeaponType.BASIC

    def test_with_speed_bonus(self):
        u = WeaponUpgrade("Speed Up", "+50 spd", WeaponType.LASER,
                         speed_bonus=50.0, cooldown_reduction=0.1)
        assert u.speed_bonus == 50.0
        assert u.cooldown_reduction == 0.1

    def test_zero_defaults(self):
        u = WeaponUpgrade("Basic Upg", "minimal", WeaponType.BASIC)
        assert u.damage_bonus == 0
        assert u.cooldown_reduction == 0.0
        assert u.speed_bonus == 0.0
