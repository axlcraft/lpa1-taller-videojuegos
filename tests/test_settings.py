class TestSettings:
    def test_import_settings(self):
        import config.settings as s
        assert s is not None

    def test_settings_have_constants(self):
        import config.settings as s
        assert hasattr(s, 'SCREEN_WIDTH')
        assert hasattr(s, 'SCREEN_HEIGHT')
        assert hasattr(s, 'FPS')

    def test_screen_dimensions(self):
        import config.settings as s
        assert s.SCREEN_WIDTH == 900
        assert s.SCREEN_HEIGHT == 600
        assert s.FPS == 60

    def test_stellar_functions(self):
        import config.settings as s
        color = s.get_stellar_background_color(1)
        assert color is not None
        assert len(color) == 3

    def test_stellar_accent_color(self):
        import config.settings as s
        color = s.get_stellar_accent_color(1)
        assert color is not None
        assert len(color) == 3

    def test_stellar_name(self):
        import config.settings as s
        name = s.get_stellar_name(1)
        assert name is not None
        assert isinstance(name, str)

    def test_stellar_background_color_valid_level(self):
        import config.settings as s
        color = s.get_stellar_background_color(1)
        assert all(0 <= c <= 255 for c in color)
        color = s.get_stellar_background_color(18)
        assert all(0 <= c <= 255 for c in color)

    def test_stellar_accent_color_valid_level(self):
        import config.settings as s
        color = s.get_stellar_accent_color(1)
        assert all(0 <= c <= 255 for c in color)
        color = s.get_stellar_accent_color(18)
        assert all(0 <= c <= 255 for c in color)

    def test_colors_dict(self):
        import config.settings as s
        assert "player" in s.COLORS
        assert "enemy" in s.COLORS
        assert "space_bg" in s.COLORS
