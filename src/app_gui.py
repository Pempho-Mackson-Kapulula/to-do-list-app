import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import date
from task_manager import TaskManager
import os
from gamification import ACHIEVEMENTS
from theme import *

class TodoApp:
    """The main application window and all its widgets."""

    def __init__(self, root, manager=None):
        self.root = root
        self.root.title("To-Do List")
        self.root.geometry("900x650")
        self.root.minsize(800, 550)

        if manager is None:
            self.manager = TaskManager()
        else:
            self.manager = manager

        self.create_widgets()
        self.refresh_list()
        self.refresh_gamification_stats()
        apply_theme(self.root)

    def create_widgets(self):
        # Outer frame with tighter padding to save window edge space
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ---- LEFT PANEL: CONTROLS & STATS ----
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # Compact Stats Section
        stats_frame = ttk.LabelFrame(left_panel, text=" Your Stats ", padding="8")
        stats_frame.pack(fill=tk.X, pady=(0, 10))

        self.level_label = ttk.Label(stats_frame, text="Level 1", font=(SUBHEADING))
        self.level_label.pack(anchor=tk.W, pady=(0, 4))

        # Horizontal layout for progress tracking
        prog_frame = ttk.Frame(stats_frame)
        prog_frame.pack(fill=tk.X, pady=(0, 4))
        self.xp_progress = ttk.Progressbar(prog_frame, orient=tk.HORIZONTAL, length=120, mode="determinate")
        self.xp_progress.pack(side=tk.LEFT, padx=(0, 5))
        self.xp_label = ttk.Label(prog_frame, text="0 XP", font=(SMALL))
        self.xp_label.pack(side=tk.LEFT)

        self.streak_label = ttk.Label(stats_frame, text="Streak: 0 days", font=(SMALL))
        self.streak_label.pack(anchor=tk.W)
        self.achievements_frame = ttk.Frame(stats_frame)
        self.achievements_frame.pack(fill=tk.X, pady=(6, 0))
        

        # Compact Form Input Section
        input_frame = ttk.LabelFrame(left_panel, text=" New Task ", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))

        # Row 0: Task Name
        ttk.Label(input_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=3)
        self.name_entry = ttk.Entry(input_frame, width=22)
        self.name_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=3)
        self.name_entry.bind("<Return>", lambda e: self.add_task())

        # Row 1: Description
        ttk.Label(input_frame, text="Desc:").grid(row=1, column=0, sticky=tk.W, pady=3)
        self.desc_entry = ttk.Entry(input_frame, width=22)
        self.desc_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=3)
        self.desc_entry.bind("<Return>", lambda e: self.add_task())

        # Row 2: Category dropdown
        ttk.Label(input_frame, text="Category:").grid(row=2, column=0, sticky=tk.W, pady=3)
        self.category_var = tk.StringVar(value="Personal")
        self.category_combo = ttk.Combobox(
            input_frame, textvariable=self.category_var,
            values=["Work", "Personal", "Shopping", "Health", "Other"],
            state="readonly", width=18
        )
        self.category_combo.grid(row=2, column=1, sticky=tk.W, padx=5, pady=3)

        # Row 3: Priority dropdown
        ttk.Label(input_frame, text="Priority:").grid(row=3, column=0, sticky=tk.W, pady=3)
        self.priority_var = tk.StringVar(value="Medium")
        self.priority_combo = ttk.Combobox(
            input_frame, textvariable=self.priority_var,
            values=["High", "Medium", "Low"],
            state="readonly", width=18
        )
        self.priority_combo.grid(row=3, column=1, sticky=tk.W, padx=5, pady=3)

        # Row 4: Deadline (date picker + time field + clear button arranged horizontally)
        ttk.Label(input_frame, text="Deadline:").grid(row=4, column=0, sticky=tk.W, pady=3)
        deadline_frame = ttk.Frame(input_frame)
        deadline_frame.grid(row=4, column=1, sticky=tk.W, padx=5, pady=3)

        self.deadline_date = DateEntry(
            deadline_frame, width=10, date_pattern="dd-MM-yyyy",
            borderwidth=2, mindate=date.today()
        )
        self.deadline_date.delete(0, tk.END)
        self.deadline_date.pack(side=tk.LEFT)

        self.deadline_time = ttk.Entry(deadline_frame, width=6)
        self.deadline_time.insert(0, "HH:MM")
        self.deadline_time.pack(side=tk.LEFT, padx=(5, 0))

        self.clear_deadline_btn = ttk.Button(
            deadline_frame, text="X", width=2, command=self.clear_deadline
        )
        self.clear_deadline_btn.pack(side=tk.LEFT, padx=(5, 0))

        # Row 5: Action submission button moved directly below the fields to slim width
        self.add_btn = ttk.Button(input_frame, text="Add Task", command=self.add_task)
        self.add_btn.grid(row=5, column=0, columnspan=2, sticky=tk.EW, pady=(8, 0))
        input_frame.columnconfigure(1, weight=1)

        # Compact Sort Controls
        sort_frame = ttk.LabelFrame(left_panel, text=" Sorting ", padding="8")
        sort_frame.pack(fill=tk.X, pady=(0, 5))

        self.sort_var = tk.StringVar(value="deadline")
        self.sort_combo = ttk.Combobox(
            sort_frame, textvariable=self.sort_var,
            values=["deadline", "priority", "category", "status", "task_name"],
            state="readonly", width=14
        )
        self.sort_combo.pack(fill=tk.X, pady=(0, 4))

        self.sort_dir_var = tk.BooleanVar(value=False)
        self.sort_dir_check = ttk.Checkbutton(
            sort_frame, text="Descending", variable=self.sort_dir_var
        )
        self.sort_dir_check.pack(side=tk.LEFT)

        self.sort_btn = ttk.Button(sort_frame, text="Apply", command=self.apply_sort, width=8)
        self.sort_btn.pack(side=tk.RIGHT)

        # Minimalist Stats Footer placed inside the left sidebar context
        self.stats_label = ttk.Label(left_panel, text="", font=(SMALL))
        self.stats_label.pack(anchor=tk.W, pady=(5, 0))

        # ---- RIGHT PANEL: MAIN DATA VIEW ----
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Title Label
        title = ttk.Label(right_panel, text="To-Do List", font=(HEADING))
        title.pack(anchor=tk.W, pady=(0, 5))

        # Task List Layout
        list_frame = ttk.Frame(right_panel)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        columns = ("status", "task_name", "description", "category", "priority", "deadline")
        self.tree = ttk.Treeview(
            list_frame, columns=columns, show="headings", selectmode="browse"
        )

        self.tree.heading("status", text="Status")
        self.tree.heading("task_name", text="Task")
        self.tree.heading("description", text="Description")
        self.tree.heading("category", text="Category")
        self.tree.heading("priority", text="Priority")
        self.tree.heading("deadline", text="Deadline")

        # Optimized columns widths to prevent horizontal over-stretching
        self.tree.column("status", width=60, anchor=tk.CENTER)
        self.tree.column("task_name", width=110, anchor=tk.W)
        self.tree.column("description", width=180, anchor=tk.W)
        self.tree.column("category", width=80, anchor=tk.W)
        self.tree.column("priority", width=70, anchor=tk.W)
        self.tree.column("deadline", width=110, anchor=tk.W)
        self.tree.tag_configure("done", foreground=MUTED_BROWN, font=("Georgia", 10, "italic"))
        self.tree.tag_configure("pending", foreground=DARK_BROWN, font=("Georgia", 10))

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Data Action Row
        btn_frame = ttk.Frame(right_panel)
        btn_frame.pack(fill=tk.X)

        self.complete_btn = ttk.Button(
            btn_frame, text="Toggle Complete", command=self.toggle_complete
        )
        self.complete_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.delete_btn = ttk.Button(
            btn_frame, text="Delete Selected", command=self.delete_task
        )
        self.delete_btn.pack(side=tk.LEFT)

       


    def clear_deadline(self):
        """Reset both the date and time fields to empty."""
        self.deadline_date.delete(0, tk.END)
        self.deadline_time.delete(0, tk.END)
        self.deadline_time.insert(0, "HH:MM")

    def add_task(self):
        """Read the input fields, create a task, and refresh the list."""
        task_name = self.name_entry.get()
        task_description = self.desc_entry.get()

        date_str = self.deadline_date.get().strip()
        time_str = self.deadline_time.get().strip()

        # Build the deadline string by combining date + time
        deadline = ""
        if date_str:
            # User picked a date but didn't type a time — warn them
            if not time_str or time_str.upper() == "HH:MM":
                messagebox.showwarning("Missing Time", "Please enter a time (HH:MM) for the deadline.")
                return
            deadline = date_str + " " + time_str

        # Try to add the task — validate_deadline might raise ValueError
        try:
            self.manager.add_task(
                task_name=task_name,
                task_description=task_description,
                category=self.category_var.get(),
                priority=self.priority_var.get(),
                deadline=deadline
            )
        except ValueError as e:
            messagebox.showwarning("Input Error", str(e))
            return

        self.refresh_list()

        # Clear all input fields after adding
        self.name_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.clear_deadline()
        self.category_var.set("Personal")
        self.priority_var.set("Medium")
        # Put the cursor back in the task name field for fast entry
        self.name_entry.focus()

    def get_selected_index(self):
        """Return the index of the selected row, or None if nothing is selected."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("No Selection", "Please select a task from the list.")
            return None
        return self.tree.index(selected[0])

    def toggle_complete(self):
        """Mark the selected task as done (or undo it) and show XP popup."""
        index = self.get_selected_index()
        if index is None:
            return

        result = self.manager.toggle_task(index)
        self.refresh_list()

        gamification_result = result["gamification"]
        if gamification_result:
            xp = gamification_result["xp_earned"]
            total = gamification_result["total_xp"]
            streak = gamification_result["streak"]
            leveled_up = gamification_result["leveled_up"]
            level = gamification_result["level"]
            multiplier = gamification_result["multiplier"]

            # Show streak bonus text only if the multiplier is above 1.0
            bonus_text = ""
            if multiplier > 1.0:
                bonus_text = " (" + str(multiplier) + "x streak bonus!)"

            message = "+" + str(xp) + " XP!" + bonus_text + "\nTotal: " + str(total) + " XP\nStreak: " + str(streak) + " days"

            if leveled_up:
                title = self.manager.gamification.get_level_title()
                message = "LEVEL UP! You are now Level " + str(level) + " \u2014 " + title + "!\n\n" + message
                messagebox.showinfo("Level Up!", message)
            else:
                title = self.manager.gamification.get_level_title()
                message = "+" + str(xp) + " XP!" + bonus_text + "\nTotal: " + str(total) + " XP (" + title + ")\nStreak: " + str(streak) + " days"
                messagebox.showinfo("Level Up!", message)

        new_achievements = gamification_result.get("new_achievements", [])
        if new_achievements:
            lines = []
            for achievement_id in new_achievements:
                info = ACHIEVEMENTS.get(achievement_id, {"icon": "?", "name": achievement_id, "description": ""})
                lines.append(info["icon"] + " " + info["name"] + "\n   " + info["description"])
            messagebox.showinfo("Achievement Unlocked!", "\n\n".join(lines))
            
        self.refresh_gamification_stats()

    def delete_task(self):
        """Delete the selected task after asking for confirmation."""
        index = self.get_selected_index()
        if index is None:
            return
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this task?"):
            self.manager.delete_task(index)
            self.refresh_list()

    def apply_sort(self):
        """Sort the task list by the chosen field and direction."""
        field = self.sort_var.get()
        reverse = self.sort_dir_var.get()
        self.manager.sort_tasks(field=field, reverse=reverse)
        self.refresh_list()

    def refresh_gamification_stats(self):
        """Update the level label, XP progress bar, and streak label."""
        g = self.manager.gamification
        stats = g.get_stats()
        xp_in_level, xp_needed = g.xp_progress_in_level()

        self.level_label.config(text="Level " + str(stats["level"]) + " \u2014 " + g.get_level_title())
        self.xp_label.config(text=str(stats["total_xp"]) + " XP")
        self.streak_label.config(
            text="Streak: " + str(stats["current_streak"]) + " days (best: " + str(stats["longest_streak"]) + ")"
        )

        if xp_needed > 0:
            # Set the progress bar: maximum is the total needed, value is how far we are
            self.xp_progress["maximum"] = xp_needed
            self.xp_progress["value"] = xp_in_level
        else:
            # At max level — show a full progress bar
            self.xp_progress["maximum"] = 1
            self.xp_progress["value"] = 1

    def refresh_list(self):
        """Clear the table and refill it with all current tasks."""
        # Remove all existing rows
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add each task as a new row
        for task in self.manager.tasks:
            status = "Done" if task["done"] else "Pending"
            tag = "done" if task["done"] else "pending"
            self.tree.insert(
                "",
                tk.END,
                values=(
                    status,
                    task.get("task_name", ""),
                    task.get("task_description", ""),
                    task.get("category", ""),
                    task.get("priority", ""),
                    task.get("deadline", "")
                ),
                tags=(tag,)
            )

        # Update the footer stats
        done, total = self.manager.get_stats()
        self.stats_label.config(text=str(done) + " of " + str(total) + " tasks completed")
        self.refresh_gamification_stats()


def main():
    """Create the window and start the app."""
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
