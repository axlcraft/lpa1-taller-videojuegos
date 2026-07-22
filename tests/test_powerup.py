from core.powerup_system import PowerUpManager


class TestPowerUpManager:
    def test_creation(self, powerup_manager):
        assert powerup_manager is not None
        assert len(powerup_manager.power_ups) == 0
        assert abs(powerup_manager.spawn_interval - 8.0) < 0.01

    def test_collision_health(self, powerup_manager, player):
        from core.powerup_system import PowerUp
        pu = PowerUp(player.pos.x, player.pos.y, "health")
        powerup_manager.power_ups.append(pu)
        collected = powerup_manager.check_collisions(player)
        assert len(collected) == 1
        assert collected[0] == pu

    def test_collision_shield(self, powerup_manager, player):
        from core.powerup_system import PowerUp
        pu = PowerUp(player.pos.x, player.pos.y, "shield")
        powerup_manager.power_ups.append(pu)
        collected = powerup_manager.check_collisions(player)
        assert len(collected) == 1

    def test_no_collision_far(self, powerup_manager, player):
        from core.powerup_system import PowerUp
        pu = PowerUp(5000, 5000, "health")
        powerup_manager.power_ups.append(pu)
        collected = powerup_manager.check_collisions(player)
        assert len(collected) == 0

    def test_remove_powerup(self, powerup_manager):
        from core.powerup_system import PowerUp
        pu = PowerUp(100, 100, "health")
        powerup_manager.power_ups.append(pu)
        assert len(powerup_manager.power_ups) == 1
        powerup_manager.remove_power_up(pu)
        assert len(powerup_manager.power_ups) == 0

    def test_clear_all(self, powerup_manager):
        from core.powerup_system import PowerUp
        for _ in range(5):
            powerup_manager.power_ups.append(PowerUp(100, 100, "health"))
        powerup_manager.power_ups.clear()
        assert len(powerup_manager.power_ups) == 0

    def test_spawn_timer(self, powerup_manager):
        initial = powerup_manager.spawn_timer
        powerup_manager.update(4.0, (0, 0, 900, 700))
        assert powerup_manager.spawn_timer == initial + 4.0

    def test_spawn_after_interval(self, powerup_manager):
        count_before = len(powerup_manager.power_ups)
        powerup_manager.update(powerup_manager.spawn_interval + 0.1, (0, 0, 900, 700))
        assert len(powerup_manager.power_ups) == count_before + 1
        assert powerup_manager.spawn_timer == 0.0
