import csv
import os
from pathlib import Path
from typing import List, Union
from rich import print

from database.models import Category, Task


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
                    "Priority",
                    "Compltion Status",
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
                    else:
                        row_content.append("Orphan Task")
                    row_content.append(bool(task.completed))
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
