from entities.boss_enemy import BossEnemy, WeakPoint
from utils.math import Vector2D


class TestWeakPoint:
    def test_creation(self):
        wp = WeakPoint(10, 20, 15)
        assert wp.offset_x == 10
        assert wp.offset_y == 20
        assert wp.radius == 15
        assert wp.is_destroyed is False
        assert wp.hit_points == 3

    def test_get_position(self):
        wp = WeakPoint(10, 20, 15)
        pos = wp.get_position(Vector2D(100, 200))
        assert pos.x == 110
        assert pos.y == 220

    def test_take_damage(self):
        wp = WeakPoint(0, 0, 15)
        assert wp.take_damage() is False
        assert wp.hit_points == 2
        wp.take_damage()
        assert wp.hit_points == 1
        assert wp.take_damage() is True
        assert wp.is_destroyed is True

    def test_destroyed_weak_point_no_collision(self):
        from entities.projectile import Proyectil
        wp = WeakPoint(0, 0, 15)
        wp.is_destroyed = True
        proj = Proyectil(0, 0, Vector2D(0, 0), speed=0, damage=10, owner_type="player")
        assert wp.collides_with_projectile(Vector2D(0, 0), proj) is False

    def test_collision_with_projectile(self):
        from entities.projectile import Proyectil
        wp = WeakPoint(0, 0, 15)
        proj = Proyectil(5, 5, Vector2D(0, 0), speed=0, damage=10, owner_type="player")
        assert wp.collides_with_projectile(Vector2D(0, 0), proj) is True

    def test_no_collision_out_of_range(self):
        from entities.projectile import Proyectil
        wp = WeakPoint(0, 0, 15)
        proj = Proyectil(100, 100, Vector2D(0, 0), speed=0, damage=10, owner_type="player")
        assert wp.collides_with_projectile(Vector2D(0, 0), proj) is False


class TestBossEnemy:
    def test_creation(self, boss):
        assert boss.is_defeated is False
        assert len(boss.weak_points) == 4
        assert boss.radius == 30
        assert boss.size == 60

    def test_boss_stats_level_6(self, boss):
        expected_hp = 80 + (6 * 20)
        expected_atk = 25 + (6 * 5)
        expected_def = 8 + (6 * 2)
        assert boss.hp == expected_hp
        assert boss.attack == expected_atk
        assert boss.defense == expected_def

    def test_boss_stats_level_15(self, boss_high_level):
        hp_mult = (10 * 20) + (15 - 10) * 40
        atk_mult = (10 * 5) + (15 - 10) * 12
        def_mult = (10 * 2) + (15 - 10) * 5
        assert boss_high_level.hp == 80 + hp_mult
        assert boss_high_level.attack == 25 + atk_mult
        assert boss_high_level.defense == 8 + def_mult

    def test_boss_stronger_than_regular(self, boss, enemy_terrestre):
        assert boss.hp > enemy_terrestre.hp
        assert boss.attack > enemy_terrestre.attack
        assert boss.defense > enemy_terrestre.defense

    def test_boss_weak_points_initialized(self, boss):
        assert len(boss.weak_points) == 4
        for wp in boss.weak_points:
            assert wp.is_destroyed is False

    def test_all_weak_points_destroyed_defeats_boss(self, boss):
        for wp in boss.weak_points:
            while not wp.is_destroyed:
                wp.take_damage()
        remaining = boss._remaining_weak_points()
        assert remaining == 0
        boss._defeat_boss()
        assert boss.is_defeated is True
        assert boss.hp == 0

    def test_collision_with_defeated_boss(self, boss, player):
        boss._defeat_boss()
        assert boss.collides_with(player) is False

    def test_laser_system(self, boss):
        from utils.math import Vector2D
        boss.laser_cooldown = 0
        boss._start_laser_charge(Vector2D(500, 300))
        assert boss.is_charging_laser() is True

    def test_laser_fires_after_charge(self, boss):
        from utils.math import Vector2D
        boss.laser_cooldown = 0
        boss._update_laser_system(0.1, Vector2D(500, 300))
        assert boss.is_charging_laser() is True
        projs = boss._update_laser_system(2.1, Vector2D(500, 300))
        assert len(projs) == 8

    def test_laser_has_cooldown(self, boss):
        from utils.math import Vector2D
        boss.laser_cooldown = 0
        boss._update_laser_system(0.1, Vector2D(500, 300))
        boss._update_laser_system(2.1, Vector2D(500, 300))
        assert boss.laser_cooldown > 0
        assert boss.is_charging_laser() is False

    def test_laser_projectile_properties(self, boss):
        from utils.math import Vector2D
        boss.laser_cooldown = 0
        projs = boss._update_laser_system(2.5, Vector2D(500, 300))
        for p in projs:
            assert p.owner_type == "enemy"
            assert p.damage == boss.attack
            assert hasattr(p, 'is_laser')

    def test_movement_pattern(self, boss):
        pos_before = Vector2D(boss.pos.x, boss.pos.y)
        boss._update_movement(0.5)
        pos_after = boss.pos
        assert pos_before.x != pos_after.x or pos_before.y != pos_after.y

    def test_boss_level_up_increases_stats(self):
        low = BossEnemy(400, 200, level=2)
        high = BossEnemy(400, 200, level=8)
        assert high.hp > low.hp
        assert high.attack > low.attack
        assert high.defense > low.defense
        assert high.speed > low.speed
