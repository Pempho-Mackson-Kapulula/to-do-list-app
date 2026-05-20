import json
import datetime


JSON_FILE = "todos.json"

PRIORITY_VALUES = {"High" : 1, "MEdium" : 2, "Low":3}


class TaskManager:
    def __init__(self, json_file=JSON_FILE):
        self.json_file = JSON_FILE
        self.tasks = self.load_tasks()
        
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