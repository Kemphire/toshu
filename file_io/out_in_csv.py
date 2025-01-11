import csv
import os
from pathlib import Path
from time import sleep
from typing import Annotated, List, Union

from rich import print

from database.db import SessionLocal
from database.models import Category, Task
from toshu.user_commands.helpers import (
    fake_progress_bar,
    panic,
    wheahter_a_list_of_dict,
)


def serve_csv_file(
    file: Path, tasks_or_cats: Union[List[Task], List[Category]]
) -> None:
    if tasks_or_cats:
        if isinstance(tasks_or_cats[0], Task):
            serve_when_task(file, tasks_or_cats)
        elif isinstance(tasks_or_cats[0], Category):
            serve_when_category(file, tasks_or_cats)
    file_size = os.stat(file).st_size
    print(f"{file_size} bytes written on {file.name}")


def serve_when_task(
    file: Path, tasks: List[Task]
) -> Annotated[int, "Number of tasks written on the file"]:
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
        for task in tasks:
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
        return len(tasks)


def serve_when_category(
    file: Path, categories: List[Category]
) -> Annotated[int, "Number of tasks written on the file"]:
    with file.open(encoding="utf-8", newline="", mode="+wt") as file_cont:
        writter = csv.writer(file_cont, delimiter=",")
        headers = ["ID", "Title", "No of tasks"]

        writter.writerow(headers)
        print(categories)
        for task in categories:
            row_content = [task.id, task.name, task.no_of_tasks]
            writter.writerow(row_content)
    return len(categories)


def create_task_using_csv(
    file: Path,
) -> Annotated[int, "total number of tasks sucessfully imported"]:
    with file.open(encoding="utf-8") as file_cont:
        rows = list(csv.DictReader(file_cont))  # Convert to list immediately
        total_rows = len(rows)

        if total_rows == 0:
            print("[red]No rows in the CSV file.[/red]")
            return 0

        correct_format = wheahter_a_list_of_dict(rows)
        if not correct_format:
            panic(f"{file.name} is not of correct format")

        total_sucessfully_created = 0
        with SessionLocal() as session:
            tasks = []
            for i, row in enumerate(rows):
                task_content = {}
                title = row.get("Title")
                if not title:
                    print(f"[yellow]Skipping row {i + 1}: Title is missing.[/yellow]")
                    continue

                task_content["title"] = title
                total_sucessfully_created += 1

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
        print(
            f"\n[green]Added [red]{total_sucessfully_created}[/] tasks to the database.[/]"
        )
        return total_sucessfully_created


def create_category_using_csv(
    file: Path,
) -> Annotated[int, "Total number of categories sucessfully imported"]:
    with file.open("r", encoding="utf-8") as file_cont:
        rows = list(csv.DictReader(file_cont))
        if len(rows) == 0:
            panic("There are 0 categories to add, exiting...")
            return 0

        correct_format = wheahter_a_list_of_dict(rows)
        if not correct_format:
            panic(f"{file.name} is not of correct format")

        successfully_imported = 0
        with SessionLocal() as session:
            categories = []
            for i, cat in enumerate(rows):
                category_content = {}
                title = cat.get("Title")
                if not title:
                    print(f"[yellow]Skippig row [red]{i + 1}[/]: Title is missing.[/]")
                    continue
                category_content["title"] = title
                successfully_imported += 1

                try:
                    categ = Category(**category_content)
                except Exception as e:
                    print(e)
                else:
                    categories.append(categ)
            fake_progress_bar(50, 0.001)
            session.add_all(categories)
            session.commit()
        sleep(0.01)
        print(
            f"\n[green]Added [red]{successfully_imported}[/] tasks to the database.[/]"
        )
        return successfully_imported
