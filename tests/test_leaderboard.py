from core.leaderboard import Leaderboard


class TestLeaderboard:
    def test_empty_leaderboard(self, leaderboard):
        leaderboard.scores.clear()
        scores = leaderboard.get_top_scores()
        assert scores == []

    def test_add_score(self, leaderboard):
        leaderboard.scores.clear()
        leaderboard.add_score("Player1", "CAZA ESTELAR", "fighter", 1000, 1)
        scores = leaderboard.get_top_scores()
        assert len(scores) == 1
        assert scores[0].player_name == "Player1"
        assert scores[0].score == 1000
        assert scores[0].level_reached == 1

    def test_scores_ordered_descending(self, leaderboard):
        leaderboard.scores.clear()
        leaderboard.add_score("Low", "CAZA ESTELAR", "fighter", 100, 1)
        leaderboard.add_score("High", "ACORAZADO", "tank", 1000, 5)
        leaderboard.add_score("Medium", "EXPLORADOR", "scout", 500, 3)
        scores = leaderboard.get_top_scores()
        assert scores[0].player_name == "High"
        assert scores[1].player_name == "Medium"
        assert scores[2].player_name == "Low"

    def test_top_scores_limit(self, leaderboard):
        leaderboard.scores.clear()
        for i in range(20):
            leaderboard.add_score(f"Player{i}", "CAZA ESTELAR", "fighter", i * 100, i)
        scores = leaderboard.get_top_scores()
        assert len(scores) == leaderboard.max_entries

    def test_persist_and_load(self, leaderboard):
        leaderboard.scores.clear()
        leaderboard.add_score("Persist", "ACORAZADO", "tank", 5000, 3)
        leaderboard.save_scores()
        leaderboard2 = Leaderboard()
        leaderboard2.scores_file = leaderboard.scores_file
        leaderboard2.load_scores()
        scores = leaderboard2.get_top_scores()
        assert len(scores) >= 1
        assert scores[0].player_name == "Persist"
        assert scores[0].score == 5000

    def test_is_high_score(self, leaderboard):
        leaderboard.scores.clear()
        assert leaderboard.is_high_score(1) is True
        for i in range(leaderboard.max_entries):
            leaderboard.add_score(f"A{i}", "CAZA ESTELAR", "fighter", 100, 1)
        assert leaderboard.is_high_score(50) is False
        assert leaderboard.is_high_score(200) is True

    def test_get_player_best(self, leaderboard):
        leaderboard.scores.clear()
        leaderboard.add_score("A", "CAZA ESTELAR", "fighter", 50, 1)
        leaderboard.add_score("A", "CAZA ESTELAR", "fighter", 200, 3)
        best = leaderboard.get_player_best("A")
        assert best.score == 200

    def test_player_best_nonexistent(self, leaderboard):
        leaderboard.scores.clear()
        best = leaderboard.get_player_best("Ghost")
        assert best is None

    def test_score_has_date(self, leaderboard):
        leaderboard.scores.clear()
        leaderboard.add_score("Dated", "CAZA ESTELAR", "fighter", 1000, 1)
        scores = leaderboard.get_top_scores()
        assert hasattr(scores[0], 'date')
        assert scores[0].date != ""

    def test_corrupted_file_handling(self, leaderboard):
        with open(leaderboard.scores_file, 'w') as f:
            f.write("not valid json")
        leaderboard.load_scores()
        scores = leaderboard.get_top_scores()
        assert scores == []

    def test_add_score_returns_bool(self, leaderboard):
        leaderboard.scores.clear()
        result = leaderboard.add_score("Test", "CAZA ESTELAR", "fighter", 9999, 99)
        assert isinstance(result, bool)
