from core.character_system import CharacterManager


class TestCharacterManager:
    def test_all_characters_available(self, character_manager):
        chars = character_manager.get_all_characters()
        keys = list(chars.keys())
        assert "fighter" in keys
        assert "tank" in keys
        assert "sniper" in keys
        assert "scout" in keys
        assert len(chars) == 4

    def test_get_fighter(self, character_manager):
        c = character_manager.get_character("fighter")
        assert c["name"] == "CAZA ESTELAR"
        assert c["stats"].hp == 120
        assert c["stats"].attack == 20
        assert c["stats"].defense == 6
        assert abs(c["stats"].move_speed - 180.0) < 0.01
        assert abs(c["stats"].shoot_cooldown - 0.3) < 0.01

    def test_get_tank(self, character_manager):
        c = character_manager.get_character("tank")
        assert c["name"] == "ACORAZADO"
        assert c["stats"].hp == 180
        assert c["stats"].attack == 15
        assert c["stats"].defense == 12
        assert c["stats"].special_ability == "Escudo Reforzado"

    def test_get_sniper(self, character_manager):
        c = character_manager.get_character("sniper")
        assert c["name"] == "FRANCOTIRADOR"
        assert c["stats"].hp == 90
        assert c["stats"].attack == 35
        assert c["stats"].defense == 3

    def test_get_scout(self, character_manager):
        c = character_manager.get_character("scout")
        assert c["name"] == "EXPLORADOR"
        assert abs(c["stats"].move_speed - 250.0) < 0.01
        assert c["stats"].attack == 12

    def test_get_invalid_character_fallback(self, character_manager):
        c = character_manager.get_character("nonexistent")
        assert c is not None
        assert c["name"] == "CAZA ESTELAR"

    def test_get_character_list(self, character_manager):
        lst = character_manager.get_character_list()
        assert "fighter" in lst
        assert "tank" in lst
        assert len(lst) == 4
