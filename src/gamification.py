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

ACHIEVEMENTS = {
    "first_blood": {
        "name": "First Blood",
        "description": "Complete your first task",
        "icon": "\u2694\ufe0f",          # crossed swords
    },
    "ember_spark": {
        "name": "Ember Spark",
        "description": "Reach a 3-day streak",
        "icon": "\ud83d\udd25",          # fire
    },
    "iron_will": {
        "name": "Iron Will",
        "description": "Reach a 7-day streak",
        "icon": "\ud83d\udee1\ufe0f",    # shield
    },
    "two_week_siege": {
        "name": "Two-Week Siege",
        "description": "Reach a 14-day streak",
        "icon": "\u2692\ufe0f",          # hammer and pick
    },
    "dragon_slayer": {
        "name": "Dragon Slayer",
        "description": "Complete 5 High-priority tasks",
        "icon": "\ud83d\udc09",          # dragon
    },
    "decimator": {
        "name": "Decimator",
        "description": "Complete 10 tasks total",
        "icon": "\ud83d\udc80",          # skull
    },
    "centurion": {
        "name": "Centurion",
        "description": "Complete 100 tasks total",
        "icon": "\ud83c\udff0",          # castle
    },
    "renaissance_scribe": {
        "name": "Renaissance Scribe",
        "description": "Complete tasks in 3+ different categories",
        "icon": "\ud83d\udcdc",          # scroll
    },
    "knights_oath": {
        "name": "Knight's Oath",
        "description": "Reach Level 5 (Knight)",
        "icon": "\u2694\ufe0f",          # crossed swords
    },
    "legend": {
        "name": "Legend",
        "description": "Reach Level 10 (Legend)",
        "icon": "\ud83d\udc51",          # crown
    },
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
            "achievements": [],               # List of earned achievement IDs, e.g. ["first_blood"]
            "high_priority_completed": 0,      # How many High-priority tasks completed (for Dragon Slayer)
            "categories_completed": [],         # List of unique categories completed (for Renaissance Scribe)
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
    
    def check_achievements(self):
        stats = self.stats
        achievements = stats["achievements"]
        
        rules = {
            "first_blood": ("tasks_completed", 1),
            "ember_spark": ("current_streak", 3),
            "iron_will": ("current_streak", 7),
            "two_week_siege": ("current_streak", 14),
            "dragon_slayer": ("high_priority_completed", 5),
            "decimator": ("tasks_completed", 10),
            "centurion": ("tasks_completed", 100),
            "knights_oath": ("level", 5),
            "legend": ("level", 10),
        }

        newly_earned = []

        for id, (key, target) in rules.items():
            if id not in achievements and stats[key] >= target:
                newly_earned.append(id)

        if "renaissance_scribe" not in achievements and len(stats["categories_completed"]) >= 3:
            newly_earned.append("renaissance_scribe")

        achievements.extend(newly_earned)
        return newly_earned

    def refresh_achievements(self):
        earned = self.manager.gamification.stats.get("achievements", [])

        # Remove everything currently in the achievements frame
        for widget in self.achievements_frame.winfo_children():
            widget.destroy()

        if not earned:
            # No achievements earned yet — show the placeholder
            ttk.Label(
                self.achievements_frame,
                text="No achievements yet",
                font=("Helvetica", 8, "italic"),
            ).pack(anchor=tk.W)
            return

        # Show each earned achievement as a small label: "icon name"
        for achievement_id in earned:
            # Look up the display info from the ACHIEVEMENTS dictionary
            info = ACHIEVEMENTS.get(achievement_id, {"icon": "?", "name": achievement_id})
            badge_text = info["icon"] + " " + info["name"]
            ttk.Label(
                self.achievements_frame,
                text=badge_text,
                font=("Helvetica", 8),
            ).pack(anchor=tk.W)

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

    
    def record_completion(self, priority, category="Personal"):
        """
        Called when a task is marked as done.
        Updates streak, awards XP, checks for level up, and checks achievements.
        Returns a dictionary with all the info the GUI needs to show a popup.

        The 'category' parameter is new — it lets us track which categories
        the user has completed tasks in (for the Renaissance Scribe achievement).
        """
        streak_changed = self.update_streak()
        xp_earned = self.calculate_xp(priority)

        self.stats["total_xp"] += xp_earned
        self.stats["tasks_completed"] += 1

        # Track High-priority completions for the Dragon Slayer achievement
        if priority == "High":
            self.stats["high_priority_completed"] += 1

        # Track unique categories for the Renaissance Scribe achievement
        # We only add the category if it's not already in the list
        if category not in self.stats["categories_completed"]:
            self.stats["categories_completed"].append(category)

        leveled_up = self.update_level()

        # Check if any new achievements were earned
        new_achievements = self.check_achievements()

        self.save_stats()

        return {
            "xp_earned": xp_earned,
            "total_xp": self.stats["total_xp"],
            "leveled_up": leveled_up,
            "level": self.stats["level"],
            "streak": self.stats["current_streak"],
            "streak_changed": streak_changed,
            "multiplier": streak_bonus_multiplier(self.stats["current_streak"]),
            "new_achievements": new_achievements,
        }

    def get_stats(self):
        """Return a copy of all stats so the GUI can display them."""
        return dict(self.stats)
