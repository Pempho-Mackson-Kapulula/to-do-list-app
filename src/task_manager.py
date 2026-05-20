import json
from datetime import datetime
import os
from gamification import GamificationManager, STATS_JSON_FILE

JSON_FILE = "todos.json"

PRIORITY_VALUES = {"High" : 1, "Medium" : 2, "Low":3}


class TaskManager:
    def __init__(self, json_file=JSON_FILE,stats_file=STATS_JSON_FILE):
        self.json_file = json_file
        self.tasks = self.load_tasks()
        self.gamification = GamificationManager(stats_file)
        
    def  load_tasks(self):
        if not os.path.exists(self.json_file):
            return []
        
        with open(self.json_file, mode = "rt") as f:
            data = f.read().strip()
            if not data:
                return []
            tasks = json.loads(data)
            
        for task in tasks:
            if "task_description" not in task:
                task["task_description"] = ""
            if "task_name" not in task:
                task["task_name"] = ""
            if "category" not in task:
                task["category"] = "Personal"
            if "priority" not in task:
                task["priority"] = "Medium"
            if "deadline" not in task:
                task["deadline"] = ""
            if "done" not in task:
                task["done"] = False
            if "xp_awarded" not in task:
                task["xp_awarded"] = False
         
        return tasks
    
    def save_tasks(self):
        with open(self.json_file, mode = "w") as f:
            json.dump(self.tasks,f,indent=5) 
            
    
    def add_task(self,task_name,task_description="",category="Personal",priority="Low",deadline=""):
        task_name = task_name.strip()
        if not task_name:
            raise ValueError("Task name field cannot be empty. Please fill it")
        
        if deadline:
            try:
                datetime.strptime(deadline, "%d-%m-%Y %H:%M")
            except ValueError:
                raise ValueError("Invalid deadline format. Use DD-MM-YYYY HH:MM")

        task = {
            "task_name": task_name,
            "task_description": task_description.strip(),
            "done": False,
            "category": category,
            "priority": priority,
            "deadline": deadline,
            "xp_awarded": False,
            "created": datetime.now().strftime("%d-%m-%Y %H:%M")
        }   
        
        self.tasks.append(task)
        self.save_tasks()
        return task
    
    def toggle_task(self,index):
        if index < 0 or index >= len(self.tasks):
            raise IndexError("Invalid task index")
        
        task = self.tasks[index]
        
        gamification_result = None
        if task["done"] == True:
            task["done"] = False
        else:
            task["done"] = True
            
        if task["done"] == True and task["xp_awarded"] == False:
            gamification_result = self.gamification.record_completion(task["priority"])
            task["xp_awarded"] = True
            
        elif task["done"] == False:
            task["xp_awarded"] = False
            
        self.save_tasks()
        return  {"task": task, "gamification": gamification_result}
    
    def delete_task(self, index):
        if index < 0 or index >= len(self.tasks):
            raise IndexError("Invalid task index.")
        removed_task = self.tasks.pop(index)
        self.save_tasks()
        return removed_task
    
    def get_sort_value(self, task, field):
        if field == "priority":
            current_priority = task.get("priority", "Medium")
            return PRIORITY_VALUES.get(current_priority, 2)

        if field == "status":
            if task.get("done") == True:
                return 0
            else:
                return 1

        if field == "deadline":
            deadline_str = task.get("deadline", "")
            if deadline_str == "":
                return datetime(2099, 1, 1)
            else:
                return datetime.strptime(deadline_str, "%d-%m-%Y %H:%M")

        fallback_value = task.get(field, "")
        return str(fallback_value).lower()
    
    def get_sort_value(self, task, field):
        if field == "priority":
            current_priority = task.get("priority", "Medium")
            return PRIORITY_VALUES.get(current_priority, 2)

        if field == "status":
            if task.get("done") == True:
                return 0
            else:
                return 1

        if field == "deadline":
            deadline_str = task.get("deadline", "")
            if deadline_str == "":
                return datetime.max
            else:
                return datetime.strptime(deadline_str, "%d-%m-%Y %H:%M")

        fallback_value = task.get(field, "")
        return str(fallback_value).lower()
    
    def sort_tasks(self, field="deadline", reverse=False):
        self.tasks.sort(key=lambda task: self.get_sort_value(task, field), reverse=reverse)
        self.save_tasks()
        
    def get_stats(self):
        done = sum(1 for task in self.tasks if task["done"])
        return done, len(self.tasks)


        