import json
import os
from datetime import datetime, date, timedelta

# The file where gamification stats are saved
STATS_JSON_FILE = "stats.json"

# How much XP you earn for completing a task, depending on its priority
PRIORITY_XP = {"High": 30, "Medium": 20, "Low": 10}

# How much total XP you need to reach each level
# Level 1 needs 0 XP (you start here), Level 2 needs 100 XP, etc.
LEVEL_THRESHOLDS = {
    1: 0,
    2: 100,
    3: 250,
    4: 450,
    5: 700,
    6: 1000,
    7: 1350,
    8: 1750,
    9: 2200,
    10: 2700,
}


# The highest level a user can reach
MAX_LEVEL = max(LEVEL_THRESHOLDS.keys())

LEVEL_TITLES = {
    1: "Novice",      
    2: "Squire",       
    3: "Apprentice",  
    4: "Warrior",      
    5: "Knight",       
    6: "Champion",     
    7: "Crusader",
    8: "Vanguard",     
    9: "Paladin",      
    10: "Legend",     
}


def streak_bonus_multiplier(streak):
    """
    Return a number that multiplies your XP based on your streak.
    A 2-day streak gives 1.1x, a 14-day streak gives 2.0x, etc.

    IMPORTANT: We check the biggest streaks first.
    If we checked >= 2 before >= 14, a 14-day streak would
    match the 2-day rule and return 1.1 instead of 2.0.
    """
    if streak >= 14:
        return 2.0
    if streak >= 7:
        return 1.5
    if streak >= 5:
        return 1.3
    if streak >= 3:
        return 1.2
    if streak >= 2:
        return 1.1
    return 1.0


class GamificationManager:
    """Tracks XP, levels, and daily streaks."""

    def __init__(self, stats_file=STATS_JSON_FILE):
        self.stats_file = stats_file
        self.stats = self.load_stats()

    def load_stats(self):
        """Load stats from JSON. If the file doesn't exist or is empty, start fresh."""
        if not os.path.exists(self.stats_file):
            return self.default_stats()

        with open(self.stats_file, "r", encoding="utf-8") as f:
            content = f.read().strip()
            # An empty file means no stats yet
            if not content:
                return self.default_stats()
            stats = json.loads(content)

        # If any key is missing from the saved data, fill it with the default
        for key, value in self.default_stats().items():
            if key not in stats:
                stats[key] = value

        return stats

    def default_stats(self):
        """Return the starting stats for a brand new user."""
        return {
            "total_xp": 0,
            "level": 1,
            "current_streak": 0,
            "longest_streak": 0,
            "last_completion_date": "",
            "tasks_completed": 0,
        }

    def save_stats(self):
        """Save the current stats to JSON so they survive between sessions."""
        with open(self.stats_file, "w", encoding="utf-8") as f:
            json.dump(self.stats, f, indent=4)

    def calculate_xp(self, priority):
        """
        Calculate how much XP you earn for completing a task.
        Base XP comes from PRIORITY_XP, then your streak multiplies it.
        We use int() to round down — 1.1 * 20 = 22.0, int() gives 22.
        """
        base_xp = PRIORITY_XP.get(priority, PRIORITY_XP["Medium"])
        multiplier = streak_bonus_multiplier(self.stats["current_streak"])
        return int(base_xp * multiplier)

    def update_level(self):
        """
        Figure out what level the user should be based on their total XP.
        Returns True if they leveled up, False otherwise.
        """
        xp = self.stats["total_xp"]
        new_level = 1

        # Go through each level in order (1, 2, 3, ...)
        for level, threshold in sorted(LEVEL_THRESHOLDS.items()):
            if xp >= threshold:
                new_level = level
            else:
                # Once XP is below a threshold, all higher levels need even more
                break

        old_level = self.stats["level"]
        # min() makes sure we never go above MAX_LEVEL
        self.stats["level"] = min(new_level, MAX_LEVEL)

        # Did we level up? Compare old vs new
        return self.stats["level"] > old_level
    
    def get_level_title(self):
        level = self.stats["level"]
        return LEVEL_TITLES.get(level,"Unknown")

    def xp_progress_in_level(self):
        """
        Return two numbers: how much XP you have in the current level,
        and how much XP you need total to reach the next level.

        Example: If you're Level 1 (threshold 0) with 50 total XP,
        and Level 2 needs 100 XP, you return (50, 100).
        The GUI uses these for the progress bar.
        """
        current_level = self.stats["level"]
        current_threshold = LEVEL_THRESHOLDS[current_level]

        if current_level >= MAX_LEVEL:
            # Already at max level, no progress to show
            return 0, 0

        next_threshold = LEVEL_THRESHOLDS[current_level + 1]
        xp_in_level = self.stats["total_xp"] - current_threshold
        needed = next_threshold - current_threshold
        return xp_in_level, needed

    def update_streak(self):
        """
        Update the daily streak. Returns True if the streak changed.

        Three cases:
        1. Last completion was today → no change (already counted)
        2. Last completion was yesterday → streak continues (+1)
        3. Last completion was 2+ days ago → streak broken (reset to 1)
        """
        today = date.today()
        last_str = self.stats["last_completion_date"]

        if not last_str:
            # First ever completion — streak starts at 1
            self.stats["current_streak"] = 1
        else:
            last_date = datetime.strptime(last_str, "%d-%m-%Y").date()

            if last_date == today:
                # Already completed a task today, streak stays the same
                return False
            elif last_date == today - timedelta(days=1):
                # Completed yesterday — streak continues!
                self.stats["current_streak"] += 1
            else:
                # Gap of 2+ days — streak broken, start over
                self.stats["current_streak"] = 1

        # Track the best streak ever
        if self.stats["current_streak"] > self.stats["longest_streak"]:
            self.stats["longest_streak"] = self.stats["current_streak"]

        self.stats["last_completion_date"] = today.strftime("%d-%m-%Y")
        return True

    def record_completion(self, priority):
        """
        Called when a task is marked as done.
        Updates streak, awards XP, checks for level up.
        Returns a dictionary with all the info the GUI needs to show a popup.
        """
        streak_changed = self.update_streak()
        xp_earned = self.calculate_xp(priority)

        self.stats["total_xp"] += xp_earned
        self.stats["tasks_completed"] += 1
        leveled_up = self.update_level()
        self.save_stats()

        return {
            "xp_earned": xp_earned,
            "total_xp": self.stats["total_xp"],
            "leveled_up": leveled_up,
            "level": self.stats["level"],
            "streak": self.stats["current_streak"],
            "streak_changed": streak_changed,
            "multiplier": streak_bonus_multiplier(self.stats["current_streak"]),
        }

    def get_stats(self):
        """Return a copy of all stats so the GUI can display them."""
        return dict(self.stats)
