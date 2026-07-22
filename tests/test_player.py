from entities.player import Jugador


class TestJugadorCreation:
    def test_create_fighter(self, fighter_character):
        p = Jugador(400, 300, "Test", fighter_character)
        assert p.name == "Test"
        assert p.character_type == "fighter"
        assert p.hp == 120
        assert p.attack == 20
        assert p.defense == 6
        assert abs(p.move_speed - 180.0) < 0.01
        assert abs(p.shoot_cooldown - 0.3) < 0.01

    def test_create_tank(self, tank_character):
        p = Jugador(400, 300, "Tank", tank_character)
        assert p.hp == 180
        assert p.attack == 15
        assert p.defense == 12

    def test_create_sniper(self, sniper_character):
        p = Jugador(400, 300, "Sniper", sniper_character)
        assert p.hp == 90
        assert p.attack == 35
        assert p.defense == 3

    def test_create_scout(self, scout_character):
        p = Jugador(400, 300, "Scout", scout_character)
        assert abs(p.move_speed - 250.0) < 0.01
        assert p.attack == 12

    def test_no_character_data_raises_error(self):
        import traceback
        try:
            Jugador(400, 300, "NoData", None)
            assert False, "Should have raised TypeError"
        except (TypeError, AttributeError):
            pass

    def test_initial_state(self, player):
        assert player.level == 1
        assert player.xp == 0
        assert player.xp_to_next == 100
        assert player.gold == 0
        assert player.inventory == []
        assert player.super_shot_charges == 0
        assert player.shield == 0
        assert player.max_shield == 200


class TestJugadorDamage:
    def test_receive_damage(self, player):
        initial_hp = player.hp
        dealt = player.receive_damage(30)
        expected = max(0, 30 - player.defense)
        assert dealt == expected
        assert player.hp == initial_hp - expected

    def test_receive_damage_with_shield(self, player):
        player.shield = 50
        player._inv_timer = 0.0
        initial_hp = player.hp
        initial_shield = player.shield
        damage_after_defense = max(0, 30 - player.defense)
        dealt = player.receive_damage(30)
        assert dealt == 0
        assert player.hp == initial_hp
        assert player.shield == initial_shield - damage_after_defense

    def test_receive_damage_zero(self, player):
        dealt = player.receive_damage(0)
        assert dealt == max(0, 0 - player.defense)

    def test_invulnerability_after_damage(self, player):
        player.receive_damage(30)
        hp_after_first = player.hp
        dealt = player.receive_damage(30)
        assert dealt == 0
        assert player.hp == hp_after_first

    def test_invulnerability_timer(self, player):
        player.receive_damage(30)
        assert player._inv_timer > 0

    def test_shield_absorbs_damage(self, player):
        player.shield = 50
        player._inv_timer = 0.0
        hp_before = player.hp
        dealt = player.receive_damage(100)
        assert player.shield < 50
        assert dealt <= 100 - player.defense


class TestJugadorLeveling:
    def test_gain_xp_no_level(self, player):
        assert player.gain_xp(50) is False
        assert player.xp == 50
        assert player.level == 1

    def test_gain_xp_level_up(self, player):
        assert player.gain_xp(100) is True
        assert player.level == 2
        assert player.xp == 0

    def test_gain_xp_multi_level(self, player):
        player.gain_xp(350)
        assert player.level >= 2

    def test_level_up_stats_increase(self, player):
        hp_before = player.hp
        atk_before = player.attack
        def_before = player.defense
        player.gain_xp(100)
        assert player.hp == hp_before + 20
        assert player.attack == atk_before + 4
        assert player.defense == def_before + 2
        assert player.xp_to_next == int(100 * 1.4)

    def test_xp_to_next_increases(self, player):
        xp_before = player.xp_to_next
        player.gain_xp(100)
        assert player.xp_to_next > xp_before


class TestJugadorSuperShot:
    def test_add_kill_charges(self, player):
        assert player.super_shot_charges == 0
        player.add_kill()
        assert player.super_shot_charges == 1

    def test_add_kill_ready(self, player):
        for _ in range(3):
            player.add_kill()
        assert player.add_kill() is True
        assert player.super_shot_charges == 4

    def test_add_kill_capped(self, player):
        for _ in range(5):
            player.add_kill()
        assert player.super_shot_charges == 4

    def test_can_super_shoot(self, player):
        assert player.can_super_shoot() is False
        for _ in range(4):
            player.add_kill()
        assert player.can_super_shoot() is True

    def test_super_shoot_consumes_charges(self, player):
        from utils.math import Vector2D
        for _ in range(4):
            player.add_kill()
        projs = player.super_shoot(Vector2D(500, 300))
        assert len(projs) == 5
        assert player.super_shot_charges == 0


class TestJugadorEffects:
    def test_add_effect(self, player):
        player.add_effect("speed", 10.0, 30, "Speed Boost")
        assert player.has_effect("speed") is True
        assert player.get_effect_time_remaining("speed") == 10.0

    def test_remove_effect(self, player):
        player.add_effect("speed", 10.0, 30, "Speed Boost")
        player.active_effects.pop("speed")
        player._recalculate_stats()
        assert player.has_effect("speed") is False

    def test_effect_speed_boost(self, player):
        base_speed = player.base_move_speed
        player.add_effect("speed", 10.0, 50, "Speed Boost")
        assert player.move_speed == base_speed * 1.5

    def test_effect_damage_boost(self, player):
        base_atk = player.base_attack
        player.add_effect("damage", 10.0, 50, "Damage Boost")
        assert player.attack == int(base_atk * 1.5)

    def test_effect_rapid_fire(self, player):
        base_cd = player.base_shoot_cooldown
        player.add_effect("rapid_fire", 10.0, 40, "Rapid Fire")
        assert abs(player.shoot_cooldown - base_cd * 0.6) < 0.001

    def test_effect_timer_expiry(self, player):
        player.add_effect("speed", 5.0, 30, "Speed Boost")
        player._update_active_effects(5.1)
        assert player.has_effect("speed") is False


class TestJugadorAttributes:
    def test_explicit_attributes(self, player):
        assert player.shield_hp == 0
        assert player.speed_boost == 1.0
        assert player.speed_boost_timer == 0.0
        assert player.speed_penalty == 1.0
        assert player.speed_penalty_timer == 0.0
        assert player.weapon_boost == 0
        assert player.weapon_boost_timer == 0.0
        assert player.weapon_malfunction == 0
        assert player.weapon_malfunction_timer == 0.0
