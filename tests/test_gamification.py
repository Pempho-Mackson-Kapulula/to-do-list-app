import os
import unittest
from src.gamification import GamificationManager, PRIORITY_XP, LEVEL_THRESHOLDS


class TestGamificationManager(unittest.TestCase):
    """Tests for the GamificationManager class."""

    def setUp(self):
        """Create a temporary stats file before each test."""
        self.tmp = "test_gamification_stats.json"
        self.g = GamificationManager(self.tmp)

    def tearDown(self):
        """Delete the temporary stats file after each test."""
        if os.path.exists(self.tmp):
            os.remove(self.tmp)

    def test_default_stats(self):
        """A new user should start at level 1 with 0 XP and 0 streak."""
        stats = self.g.get_stats()
        self.assertEqual(stats["total_xp"], 0)
        self.assertEqual(stats["level"], 1)
        self.assertEqual(stats["current_streak"], 0)
        self.assertEqual(stats["longest_streak"], 0)

    def test_xp_per_priority(self):
        """Each priority should give the correct base XP."""
        self.assertEqual(self.g.calculate_xp("Low"), PRIORITY_XP["Low"])
        self.assertEqual(self.g.calculate_xp("Medium"), PRIORITY_XP["Medium"])
        self.assertEqual(self.g.calculate_xp("High"), PRIORITY_XP["High"])

    def test_xp_with_streak_bonus(self):
        """A 2-day streak should multiply XP by 1.1."""
        self.g.stats["current_streak"] = 2
        base = PRIORITY_XP["High"]
        expected = int(base * 1.1)
        self.assertEqual(self.g.calculate_xp("High"), expected)

    def test_streak_progression(self):
        """First completion starts a streak. Same-day completion doesn't increase it."""
        result = self.g.record_completion("Medium")
        self.assertEqual(result["streak"], 1)
        self.assertTrue(result["streak_changed"])

        # Completing again on the same day should not change the streak
        result2 = self.g.record_completion("Medium")
        self.assertEqual(result2["streak"], 1)
        self.assertFalse(result2["streak_changed"])

    def test_level_up(self):
        """Earning enough XP should trigger a level up."""
        # Set XP just below the level 2 threshold
        self.g.stats["total_xp"] = LEVEL_THRESHOLDS[2] - 10
        self.g.save_stats()
        result = self.g.record_completion("High")
        self.assertTrue(result["leveled_up"])
        self.assertEqual(self.g.stats["level"], 2)

    def test_xp_progress(self):
        """Progress should show how much XP is in the current level vs needed."""
        self.g.stats["total_xp"] = 50
        self.g.stats["level"] = 1
        xp_in_level, needed = self.g.xp_progress_in_level()
        self.assertEqual(xp_in_level, 50)
        self.assertEqual(needed, 100)

    def test_max_level(self):
        """At max level, progress should return 0 and xp_to_next should be 0."""
        max_level = max(LEVEL_THRESHOLDS.keys())
        self.g.stats["total_xp"] = LEVEL_THRESHOLDS[max_level]
        self.g.update_level()
        self.assertEqual(self.g.stats["level"], max_level)
        xp_in, needed = self.g.xp_progress_in_level()
        self.assertEqual(needed, 0)


if __name__ == "__main__":
    unittest.main()
