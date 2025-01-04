import csv
import os
from time import sleep
from pathlib import Path
from typing import List, Union
from rich import print

from database.models import Category, Task
from database.db import SessionLocal

from todo.user_commands.helpers import fake_progress_bar


def serve_csv_file(file: Path, tasks_or_cats: Union[List[Task], List[Category]]):
    if tasks_or_cats:
        if isinstance(tasks_or_cats[0], Task):
            with file.open(encoding="utf-8", newline="", mode="+wt") as file_cont:
                writter = csv.writer(file_cont, delimiter=",")
                headers = [
                    "ID",
                    "Title",
                    "Description",
                    "Category",
                    "Category ID",
                    "Priority",
                    "Completion Status",
                ]

                writter.writerow(headers)
                print(tasks_or_cats)
                for task in tasks_or_cats:
                    row_content = [task.id, task.title]
                    if task.description is None:
                        row_content.append("No Description")
                    else:
                        row_content.append(task.description)
                    if task.category is not None:
                        row_content.append(task.category.name)
                        row_content.append(task.category_id)
                    else:
                        row_content.append("Orphan Task")
                        row_content.append(None)
                    row_content.extend([task.priority, bool(task.completed)])
                    writter.writerow(row_content)
        elif isinstance(tasks_or_cats[0], Category):
            with file.open(encoding="utf-8", newline="", mode="+wt") as file_cont:
                writter = csv.writer(file_cont, delimiter=",")
                headers = ["ID", "Title", "No of tasks"]

                writter.writerow(headers)
                print(tasks_or_cats)
                for task in tasks_or_cats:
                    row_content = [task.id, task.name, task.no_of_tasks]
                    writter.writerow(row_content)

    file_size = os.stat(file).st_size
    print(f"{file_size} bytes written on {file.name}")


def create_task_using_csv(file: Path):
    with file.open(encoding="utf-8") as file_cont:
        rows = list(csv.DictReader(file_cont))  # Convert to list immediately
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
