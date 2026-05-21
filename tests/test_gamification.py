import os
import unittest
from gamification import GamificationManager, PRIORITY_XP, LEVEL_THRESHOLDS, ACHIEVEMENTS

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
    
    def test_level_titles(self):
        """Each level should have the correct title in LEVEL_TITLES."""
        # Check that every level from 1 to 10 has a title
        for level in range(1, 11):
            self.g.stats["level"] = level
            title = self.g.get_level_title()
            self.assertEqual(title, LEVEL_TITLES[level])
            # The title should be a non-empty string
            self.assertIsInstance(title, str)
            self.assertTrue(len(title) > 0)
            
    def test_level_title_unknown_level(self):
        """A level outside 1-10 should return 'Unknown', not crash."""
        # Level 0
        self.g.stats["level"] = 0
        self.assertEqual(self.g.get_level_title(), "Unknown")
        # Level 99
        self.g.stats["level"] = 99
        self.assertEqual(self.g.get_level_title(), "Unknown")
        
    def test_first_achievement_unlocked(self):
        """Completing a task for the first time should unlock 'first_blood'."""
        result = self.g.record_completion("Medium", "Personal")
        # Check that first_blood is in the newly earned list
        self.assertIn("first_blood", result["new_achievements"])
        # Check that it's also saved in the stats
        self.assertIn("first_blood", self.g.stats["achievements"])
    
    def test_achievement_not_re_earned(self):
        """Earning the same achievement twice should not duplicate it."""
        # First completion — unlocks first_blood
        result1 = self.g.record_completion("Medium", "Personal")
        self.assertIn("first_blood", result1["new_achievements"])

        # Second completion — first_blood should NOT appear again
        result2 = self.g.record_completion("Medium", "Personal")
        self.assertNotIn("first_blood", result2["new_achievements"])

        # But it should still be in the saved list (just once)
        count = self.g.stats["achievements"].count("first_blood")
        self.assertEqual(count, 1)
    
    def test_dragon_slayer_achievement(self):
        """Completing 5 High-priority tasks should unlock 'dragon_slayer'."""
        # Complete 4 High tasks — not enough yet
        for i in range(4):
            result = self.g.record_completion("High", "Personal")
            self.assertNotIn("dragon_slayer", result["new_achievements"])

        # 5th High task — should unlock dragon_slayer
        result = self.g.record_completion("High", "Personal")
        self.assertIn("dragon_slayer", result["new_achievements"])

        # Verify the counter was tracking correctly
        self.assertEqual(self.g.stats["high_priority_completed"], 5)
    
    def test_renaissance_scribe_achievement(self):
        """Completing tasks in 3+ different categories should unlock 'renaissance_scribe'."""
        # Complete tasks in 2 categories — not enough
        self.g.record_completion("Medium", "Work")
        self.g.record_completion("Medium", "Work")  # Same category, shouldn't duplicate
        self.assertEqual(len(self.g.stats["categories_completed"]), 1)

        self.g.record_completion("Medium", "Personal")
        self.assertEqual(len(self.g.stats["categories_completed"]), 2)
        # Not unlocked yet
        self.assertNotIn("renaissance_scribe", self.g.stats["achievements"])

        # 3rd unique category — should unlock
        result = self.g.record_completion("Medium", "Health")
        self.assertIn("renaissance_scribe", result["new_achievements"])
        self.assertEqual(len(self.g.stats["categories_completed"]), 3)
        
    



if __name__ == "__main__":
    unittest.main()
