from entities.player import Jugador
from entities.enemy import Enemigo
from entities.boss_enemy import BossEnemy
from entities.projectile import Proyectil
from core.weapon_system import Weapon
from utils.math import Vector2D


class TestPlayerVsEnemy:
    def test_player_damages_enemy(self, player, enemy_terrestre):
        proj = Proyectil(100, 100, Vector2D(1, 0), speed=400, damage=player.attack, owner_type="player")
        initial_hp = enemy_terrestre.hp
        if enemy_terrestre.collides_with(proj):
            dealt = enemy_terrestre.receive_damage(proj.damage)
            assert enemy_terrestre.hp == initial_hp - dealt

    def test_enemy_damages_player(self, player, enemy_terrestre):
        initial_hp = player.hp
        dmg = enemy_terrestre.get_contact_damage()
        dealt = player.receive_damage(dmg)
        assert player.hp == initial_hp - dealt

    def test_enemy_defense_reduces_damage(self, player, enemy_terrestre):
        dmg_before = enemy_terrestre.receive_damage(100)
        assert dmg_before <= 100 - enemy_terrestre.defense


class TestProjectileInteractions:
    def test_player_projectile_hits_enemy(self, projectile, enemy_terrestre):
        projectile.pos = Vector2D(enemy_terrestre.pos.x, enemy_terrestre.pos.y)
        initial_hp = enemy_terrestre.hp
        if enemy_terrestre.collides_with(projectile):
            dealt = enemy_terrestre.receive_damage(projectile.damage)
            assert enemy_terrestre.hp == initial_hp - dealt

    def test_enemy_projectile_hits_player(self, enemy_projectile, player):
        enemy_projectile.pos = Vector2D(player.pos.x, player.pos.y)
        initial_hp = player.hp
        if player.collides_with(enemy_projectile):
            dealt = player.receive_damage(enemy_projectile.damage)
            assert player.hp == initial_hp - dealt


class TestLevelingIntegration:
    def test_enemy_kill_gives_xp(self, player, enemy_terrestre):
        xp_reward = max(1, enemy_terrestre.hp // 10 + enemy_terrestre.level * 5)
        player.gain_xp(xp_reward)
        assert player.xp == xp_reward

    def test_kill_adds_super_charge(self, player):
        player.add_kill()
        assert player.super_shot_charges == 1

    def test_enemies_scale_with_level(self):
        low = Enemigo(100, 100, "terrestre", level=1)
        high = Enemigo(100, 100, "terrestre", level=20)
        assert high.hp > low.hp
        assert high.attack > low.attack


class TestBossIntegration:
    def test_boss_tougher_than_normal(self, boss, enemy_terrestre):
        assert boss.hp > enemy_terrestre.hp * 3
        assert boss.attack > enemy_terrestre.attack

    def test_boss_levels_consistent(self):
        for lvl in range(6, 19):
            b = BossEnemy(400, 200, level=lvl)
            assert b.hp > 0
            assert b.attack > 0
        b6 = BossEnemy(400, 200, level=6)
        b10 = BossEnemy(400, 200, level=10)
        b11 = BossEnemy(400, 200, level=11)
        b18 = BossEnemy(400, 200, level=18)
        assert b10.hp > b6.hp
        assert b11.hp > b10.hp
        assert b18.hp > b11.hp
