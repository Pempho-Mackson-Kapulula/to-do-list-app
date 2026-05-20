import unittest
import tempfile
import json
import os
from task_manager import TaskManager, PRIORITY_VALUES


class TestTaskManager(unittest.TestCase):
    """Tests for the TaskManager class."""

    def setUp(self):
        """Create a temporary file for tasks and stats before each test."""
        self.tmp = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json")
        self.tmp.close()
        self.stats_tmp = "test_stats.json"
        # Pass both file paths so tests don't touch real data
        self.manager = TaskManager(json_file=self.tmp.name, stats_file=self.stats_tmp)

    def tearDown(self):
        """Delete the temporary files after each test."""
        if os.path.exists(self.tmp.name):
            os.remove(self.tmp.name)
        if os.path.exists(self.stats_tmp):
            os.remove(self.stats_tmp)

    def test_load_empty_file(self):
        """An empty file should give us an empty task list."""
        self.assertEqual(self.manager.tasks, [])

    def test_add_task(self):
        """Adding a task should store all fields correctly."""
        task = self.manager.add_task(
            "Buy milk",
            task_description="Get full fat from corner shop",
            category="Shopping",
            priority="High",
            deadline="10-05-2027 14:30"
        )
        self.assertEqual(task["task_name"], "Buy milk")
        self.assertEqual(task["task_description"], "Get full fat from corner shop")
        self.assertEqual(task["category"], "Shopping")
        self.assertEqual(task["priority"], "High")
        self.assertEqual(task["deadline"], "10-05-2027 14:30")
        self.assertFalse(task["done"])
        self.assertEqual(len(self.manager.tasks), 1)

    def test_add_task_no_deadline(self):
        """A task with no deadline should store an empty string."""
        task = self.manager.add_task("Simple task")
        self.assertEqual(task["deadline"], "")

    def test_add_task_empty_name_raises(self):
        """An empty task name should raise ValueError."""
        with self.assertRaises(ValueError):
            self.manager.add_task("   ")

    def test_add_task_invalid_deadline_format_raises(self):
        """A bad date format should raise ValueError."""
        with self.assertRaises(ValueError):
            self.manager.add_task("Buy milk", deadline="2024-05-10 14:30")

    def test_toggle_task(self):
        """Toggling a task should flip done and award XP on first completion."""
        self.manager.add_task("Task A")

        # First toggle: mark as done, XP should be awarded
        result = self.manager.toggle_task(0)
        self.assertTrue(result["task"]["done"])
        self.assertIsNotNone(result["gamification"])
        self.assertGreater(result["gamification"]["xp_earned"], 0)

        # Second toggle: mark as not done, no XP
        result = self.manager.toggle_task(0)
        self.assertFalse(result["task"]["done"])
        self.assertIsNone(result["gamification"])

    def test_toggle_invalid_index_raises(self):
        """Toggling a task that doesn't exist should raise IndexError."""
        with self.assertRaises(IndexError):
            self.manager.toggle_task(0)

    def test_delete_task(self):
        """Deleting a task should remove it and shift the remaining tasks."""
        self.manager.add_task("Task A")
        self.manager.add_task("Task B")
        removed = self.manager.delete_task(0)
        self.assertEqual(removed["task_name"], "Task A")
        self.assertEqual(len(self.manager.tasks), 1)
        self.assertEqual(self.manager.tasks[0]["task_name"], "Task B")

    def test_delete_invalid_index_raises(self):
        """Deleting a task that doesn't exist should raise IndexError."""
        with self.assertRaises(IndexError):
            self.manager.delete_task(0)

  
    def test_get_stats(self):
        """get_stats should return (completed_count, total_count)."""
        self.manager.add_task("A")
        self.manager.add_task("B")
        self.manager.add_task("C")
        self.manager.toggle_task(1)
        self.assertEqual(self.manager.get_stats(), (1, 3))

    def test_sort_by_priority(self):
        """Sorting by priority should put High first, Low last."""
        self.manager.add_task("Low", priority="Low")
        self.manager.add_task("High", priority="High")
        self.manager.add_task("Medium", priority="Medium")
        self.manager.sort_tasks("priority")
        names = [task["task_name"] for task in self.manager.tasks]
        self.assertEqual(names, ["High", "Medium", "Low"])

    def test_sort_by_deadline(self):
        """Sorting by deadline should put earliest first, no-deadline last."""
        self.manager.add_task("Old", deadline="01-01-2027 08:00")
        self.manager.add_task("New", deadline="01-01-2028 08:00")
        self.manager.add_task("None")
        self.manager.sort_tasks("deadline")
        names = [task["task_name"] for task in self.manager.tasks]
        self.assertEqual(names, ["Old", "New", "None"])

    def test_sort_by_status(self):
        """Sorting by status should put done tasks before pending ones."""
        self.manager.add_task("Pending")
        self.manager.add_task("Done")
        self.manager.toggle_task(1)
        self.manager.sort_tasks("status")
        names = [task["task_name"] for task in self.manager.tasks]
        self.assertEqual(names, ["Done", "Pending"])

    def test_sort_descending(self):
        """Sorting descending by name should reverse the order."""
        self.manager.add_task("Apple")
        self.manager.add_task("Banana")
        self.manager.sort_tasks("task_name", reverse=True)
        names = [task["task_name"] for task in self.manager.tasks]
        self.assertEqual(names, ["Banana", "Apple"])