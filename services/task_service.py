from datetime import datetime, date
import pandas as pd
from database import init_db, execute_query, fetch_query

# Initialize DB on import
init_db()

class TaskService:
    @staticmethod
    def get_projects():
        return fetch_query("SELECT * FROM projects ORDER BY name ASC")

    @staticmethod
    def add_project(name, description=""):
        if not name.strip():
            raise ValueError("O nome do projeto não pode estar vazio.")
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        execute_query(
            "INSERT INTO projects (name, description, created_at) VALUES (?, ?, ?)",
            (name.strip(), description.strip(), created_at)
        )

    @staticmethod
    def delete_project(project_id):
        # Check if project has tasks
        project = fetch_query("SELECT name FROM projects WHERE id = ?", (project_id,))
        if project:
            proj_name = project[0]["name"]
            tasks = fetch_query("SELECT id FROM tasks WHERE project = ?", (proj_name,))
            if tasks:
                raise ValueError("Não é possível excluir um projeto que possui tarefas associadas.")
        execute_query("DELETE FROM projects WHERE id = ?", (project_id,))

    @staticmethod
    def get_tasks():
        return fetch_query("SELECT * FROM tasks ORDER BY due_date ASC")

    @staticmethod
    def get_task(task_id):
        res = fetch_query("SELECT * FROM tasks WHERE id = ?", (task_id,))
        return res[0] if res else None

    @staticmethod
    def add_task(title, description, project, priority, status, due_date):
        if not title.strip():
            raise ValueError("O título da tarefa não pode estar vazio.")
        if not project:
            raise ValueError("Selecione ou cadastre um projeto válido.")
        
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        due_date_str = due_date.strftime("%Y-%m-%d") if isinstance(due_date, (date, datetime)) else str(due_date)
        
        execute_query(
            """INSERT INTO tasks (title, description, project, priority, status, created_at, due_date)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (title.strip(), description.strip(), project, priority, status, created_at, due_date_str)
        )

    @staticmethod
    def update_task(task_id, title, description, project, priority, status, due_date):
        if not title.strip():
            raise ValueError("O título da tarefa não pode estar vazio.")
        if not project:
            raise ValueError("Selecione um projeto válido.")
        
        due_date_str = due_date.strftime("%Y-%m-%d") if isinstance(due_date, (date, datetime)) else str(due_date)
        
        execute_query(
            """UPDATE tasks SET title = ?, description = ?, project = ?, priority = ?, status = ?, due_date = ?
               WHERE id = ?""",
            (title.strip(), description.strip(), project, priority, status, due_date_str, task_id)
        )

    @staticmethod
    def delete_task(task_id):
        execute_query("DELETE FROM tasks WHERE id = ?", (task_id,))

    @staticmethod
    def get_statistics():
        tasks = TaskService.get_tasks()
        total = len(tasks)
        completed = sum(1 for t in tasks if t["status"] == "Concluída")
        in_progress = sum(1 for t in tasks if t["status"] == "Em Andamento")
        pending = sum(1 for t in tasks if t["status"] == "Pendente")
        
        today_str = date.today().strftime("%Y-%m-%d")
        overdue = sum(1 for t in tasks if t["due_date"] < today_str and t["status"] != "Concluída")
        
        return {
            "total": total,
            "completed": completed,
            "in_progress": in_progress,
            "pending": pending,
            "overdue": overdue
        }

    @staticmethod
    def get_tasks_dataframe():
        tasks = TaskService.get_tasks()
        if not tasks:
            return pd.DataFrame(columns=["id", "title", "description", "project", "priority", "status", "created_at", "due_date"])
        df = pd.DataFrame(tasks)
        return df
