# Python To-Do List

A desktop to-do list application built with Python and Tkinter. It helps you manage tasks with a task name, optional description, categories, priorities, deadlines, and sorting — all through a simple, clean graphical interface.

## Features

- **Add tasks** with a task name, optional description, category, priority level, and optional deadline (date + time).
- **Mark tasks as complete** or toggle them back to pending.
- **Delete tasks** with a confirmation prompt to avoid accidental removal.
- **Sort tasks** by deadline, priority, category, status, or task name in ascending or descending order.
- **Calendar date picker** with time input for easy deadline selection.
- **Persistent storage** — all tasks are automatically saved to a local `todos.json` file.
- **Statistics footer** showing how many tasks you've completed.
- **Gamification** — earn XP for completing tasks, level up, and build daily streaks! Higher priority tasks give more XP, and maintaining a consecutive-day streak earns bonus multipliers.

## Prerequisites

To run this project, you'll need:

- **Python 3.8 or higher**
- The following Python packages:
  - `tkcalendar`

You can install the required package using pip:

```bash
pip install -r requirements.txt
```

Or install it directly:

```bash
pip install tkcalendar
```

## Installation

Follow these steps to set up and run the project on your local machine:

1. **Clone the repository** (or copy the project files into a folder):

```bash
git clone https://github.com/yourusername/python-todo-list.git
cd python-todo-list
```

2. **(Optional) Create a virtual environment** to keep dependencies isolated:

```bash
python -m venv venv
```

3. **Activate the virtual environment:**

- On Windows:

```bash
venv\Scripts\activate
```

- On macOS / Linux:

```bash
source venv/bin/activate
```

4. **Install dependencies:**

```bash
pip install -r requirements.txt
```

## Running the Application

### Option 1: Using the provided script

**On Windows (PowerShell / CMD):**

> **Note:** PowerShell requires the `.\` prefix to run scripts in the current directory. The batch file auto-detects a `venv` folder and uses its Python interpreter if available; otherwise it falls back to the system `py` launcher.

```batch
.\main.bat
```

**On Linux / macOS:**

```bash
chmod +x main.sh
./main.sh
```

### Option 2: Running directly with Python

**On Windows:**

```batch
py src/main.py
```

**On Linux / macOS:**

```bash
python src/main.py
```

A window will open where you can start adding and managing your tasks immediately.

## How It Works

- `src/todo_core.py` handles everything related to tasks: adding, toggling completion, deleting, sorting, and reading/writing the `todos.json` file. It manages **task name**, **description**, **category**, **priority**, and **deadline** fields.
- `src/gamification.py` manages the XP, level, and streak system. Completing a task awards XP based on its priority. Consecutive daily completions build streaks that multiply XP rewards. Stats are saved to `stats.json`.
- `src/todo_gui.py` creates the visual interface, connects buttons and inputs to the core logic, and displays a **stats panel** showing your current level, XP progress bar, and streak counter.
- `src/main.py` is the simple entry point you run to start the app.
- `tests/test_todo.py` verifies that all core and gamification functions work correctly using Python's built-in `unittest` module.

