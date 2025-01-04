from pathlib import Path
from database.models import Category, Task
import yaml
import os
from typing import List, Union


def serve_yaml_file(file: Path, tasks_or_cats: Union[List[Task], List[Category]]):
    if tasks_or_cats:
        if isinstance(tasks_or_cats[0], Task):
            with file.open(mode="+wt") as file_cont:
                dict_to_dump = [
                    {
                        "id": task.id,
                        "title": task.title,
                        "description": task.description,
                        "category": task.category.name,
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
