from entities.enemy import Enemigo


class TestEnemigoCreation:
    def test_create_terrestre(self):
        e = Enemigo(100, 100, "terrestre", level=1)
        assert e.tipo == "terrestre"
        assert e.hp == 60
        assert e.attack == 15
        assert e.defense == 3
        assert abs(e.speed - 80.0) < 0.01

    def test_create_volador(self):
        e = Enemigo(100, 100, "volador", level=1)
        assert e.tipo == "volador"
        assert e.hp == 45
        assert e.can_shoot is True
        assert abs(e.shoot_range - 200.0) < 0.01

    def test_create_artillero(self):
        e = Enemigo(100, 100, "artillero", level=1)
        assert e.tipo == "artillero"
        assert e.hp == 80
        assert e.attack == 20
        assert e.can_shoot is True

    def test_create_elite(self):
        e = Enemigo(100, 100, "elite", level=11)
        assert e.tipo == "elite"
        assert e.hp > 120
        assert e.can_shoot is True

    def test_create_berserker(self):
        e = Enemigo(100, 100, "berserker", level=13)
        assert e.tipo == "berserker"
        assert e.can_shoot is False
        assert abs(e.speed - 140.0) < 0.01

    def test_create_guardian(self):
        e = Enemigo(100, 100, "guardian", level=15)
        assert e.tipo == "guardian"
        assert e.hp > 180
        assert e.can_shoot is True

    def test_invalid_type_fallback(self):
        e = Enemigo(100, 100, "unknown_type", level=1)
        assert e.hp == 50


class TestEnemigoScaling:
    def test_level_1_scaling(self):
        e = Enemigo(100, 100, "terrestre", level=1)
        assert e.hp == 60
        assert e.attack == 15

    def test_level_5_scaling(self):
        e = Enemigo(100, 100, "terrestre", level=5)
        expected_mult = 1.0 + (5 - 1) * 0.15
        assert e.hp == int(60 * expected_mult)
        assert e.attack == int(15 * expected_mult)

    def test_level_10_scaling(self):
        e = Enemigo(100, 100, "terrestre", level=10)
        expected_mult = 1.0 + (10 - 1) * 0.15
        assert e.hp == int(60 * expected_mult)

    def test_level_11_aggressive_scaling(self):
        e = Enemigo(100, 100, "terrestre", level=11)
        base_mult = 1.0 + (10 - 1) * 0.15
        expected_mult = base_mult + (11 - 10) * 0.25
        assert e.hp == int(60 * expected_mult)
        assert e.attack == int(15 * expected_mult)

    def test_level_15_scaling(self):
        e = Enemigo(100, 100, "terrestre", level=15)
        base_mult = 1.0 + (10 - 1) * 0.15
        expected_mult = base_mult + (15 - 10) * 0.25
        assert e.hp == int(60 * expected_mult)

    def test_volador_scaling(self):
        e1 = Enemigo(100, 100, "volador", level=1)
        e10 = Enemigo(100, 100, "volador", level=10)
        assert e10.hp > e1.hp
        assert e10.attack > e1.attack
        assert e10.speed == e1.speed


class TestEnemigoDamage:
    def test_receive_damage(self, enemy_terrestre):
        initial_hp = enemy_terrestre.hp
        dealt = enemy_terrestre.receive_damage(20)
        expected = max(0, 20 - enemy_terrestre.defense)
        assert dealt == expected
        assert enemy_terrestre.hp == initial_hp - expected

    def test_receive_damage_under_defense(self, enemy_terrestre):
        dealt = enemy_terrestre.receive_damage(2)
        assert dealt == max(0, 2 - enemy_terrestre.defense)

    def test_invulnerability_after_hit(self, enemy_terrestre):
        enemy_terrestre.receive_damage(20)
        hp_after = enemy_terrestre.hp
        dealt = enemy_terrestre.receive_damage(20)
        assert dealt == 0
        assert enemy_terrestre.hp == hp_after

    def test_get_contact_damage(self, enemy_terrestre):
        dmg = enemy_terrestre.get_contact_damage()
        assert dmg > 0
        assert dmg == enemy_terrestre.contact_damage


class TestEnemigoMovement:
    def test_move_towards_player(self, enemy_terrestre):
        from utils.math import Vector2D
        from entities.player import Jugador
        from core.character_system import CharacterManager

        mgr = CharacterManager()
        char = mgr.get_character('fighter')
        player = Jugador(500, 300, "Target", char)
        pos_before = enemy_terrestre.pos.copy() if hasattr(enemy_terrestre.pos, 'copy') else Vector2D(enemy_terrestre.pos.x, enemy_terrestre.pos.y)

        before = Vector2D(enemy_terrestre.pos.x, enemy_terrestre.pos.y)
        enemy_terrestre.update(0.1, player)
        after = enemy_terrestre.pos

        # Should have moved closer
        dist_before = (Vector2D(player.pos.x, player.pos.y) - before).magnitude()
        dist_after = (Vector2D(player.pos.x, player.pos.y) - after).magnitude()
        assert dist_after < dist_before + 0.01


class TestEnemigoShooting:
    def test_volador_shoots_in_range(self, enemy_volador):
        from entities.player import Jugador
        from core.character_system import CharacterManager
        from utils.math import Vector2D

        mgr = CharacterManager()
        char = mgr.get_character('fighter')
        player = Jugador(200, 200, "Target", char)

        enemy_volador._shoot_timer = 0
        projectiles = enemy_volador._try_shoot(
            Vector2D(player.pos.x - enemy_volador.pos.x, player.pos.y - enemy_volador.pos.y),
            0.1
        )
        assert len(projectiles) >= 1

    def test_enemy_projectile_damage(self, enemy_projectile):
        assert enemy_projectile.damage == 15
        assert enemy_projectile.owner_type == "enemy"
        assert enemy_projectile.can_damage_player() is True
        assert enemy_projectile.can_damage_enemy() is False

    def test_player_projectile(self, projectile):
        assert projectile.owner_type == "player"
        assert projectile.can_damage_player() is False
        assert projectile.can_damage_enemy() is True
