from pathlib import Path
from database.models import Category, Task
import yaml
import os
from typing import List, Union
from time import sleep

from database.db import SessionLocal

from rich import print

from todo.user_commands.helpers import fake_progress_bar


def serve_yaml_file(file: Path, tasks_or_cats: Union[List[Task], List[Category]]):
    if tasks_or_cats:
        if isinstance(tasks_or_cats[0], Task):
            with file.open(mode="+wt") as file_cont:
                dict_to_dump = [
                    {
                        "id": task.id,
                        "title": task.title,
                        "description": task.description,
                        "category": task.category,
                        "completion status": task.completed,
                    }
                    for task in tasks_or_cats
                ]
                yaml.dump(dict_to_dump, file_cont)
        elif isinstance(tasks_or_cats[0], Category):
            with file.open(mode="+wt") as file_cont:
                dict_to_dump = [
                    {
                        "id": task.id,
                        "title": task.name,
                        "no of tasks": task.no_of_tasks,
                    }
                    for task in tasks_or_cats
                ]
                yaml.dump(dict_to_dump, file_cont)

    file_size = os.stat(file).st_size
    print(f"{file_size} bytes written to {file.name}")


def create_task_using_yaml(file: Path):
    with file.open(encoding="utf-8") as file_cont:
        rows = yaml.safe_load(file_cont)
        total_rows = len(rows)

        if total_rows == 0:
            print("[red]No rows in the CSV file.[/red]")
            return

        with SessionLocal() as session:
            tasks = []
            for i, row in enumerate(rows):
                task_content = {}
                title = row.get("Title")
                if not title:
                    print(f"[yellow]Skipping row {i + 1}: Title is missing.[/yellow]")
                    continue

                task_content["title"] = title

                if category_id := row.get("Category ID"):
                    task_content["category_id"] = category_id
                if priority := row.get("Priority"):
                    if priority in ["L", "M", "T"]:
                        task_content["priority"] = priority
                if completed := row.get("Completion Status"):
                    task_content["completed"] = completed.lower() in ["true", "1"]

                try:
                    task = Task(**task_content)
                except Exception as e:
                    print(e)
                else:
                    tasks.append(task)
            fake_progress_bar(100, 0.01)
            session.add_all(tasks)
            session.commit()
        sleep(0.01)
        print(f"\n[green]Added [red]{len(tasks)}[/] tasks to the database.[/]")
