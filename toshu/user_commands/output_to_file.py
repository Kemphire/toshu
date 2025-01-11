from pathlib import Path
from typing import Annotated, Optional

import typer
from sqlalchemy.orm import joinedload

from database.db import SessionLocal
from database.models import Category, Task
from file_io import serve_csv, serve_json, serve_yaml
from toshu.user_commands.helpers import panic

app = typer.Typer()


@app.command(short_help="Get the list of task in file", name="out")
def get_tasks_in_file(
    file: Annotated[
        Path,
        typer.Option(
            "-f",
            "--file",
            exists=False,
            file_okay=True,
            writable=True,
            dir_okay=False,
            resolve_path=True,
        ),
    ],
    category: Annotated[Optional[bool], typer.Option("-c", "--categ")] = False,
):
    if not category:
        with SessionLocal() as session:
            tasks = session.query(Task).options(joinedload(Task.category)).all()
            if len(tasks) < 1:
                panic("You have not tasks, to add")
                return typer.Exit
        file_extension = file.suffix
        if file_extension == ".csv":
            serve_csv(file, tasks)
        elif file_extension == ".json":
            serve_json(file, tasks)
        elif file_extension in [".yml", ".yaml"]:
            serve_yaml(file, tasks)
    else:
        with SessionLocal() as session:
            cats = session.query(Category).all()
            if len(cats) < 1:
                panic("You have not cats, to add")
                return typer.Exit
        file_extension = file.suffix
        if file_extension == ".csv":
            serve_csv(file, cats)
        elif file_extension == ".json":
            serve_json(file, cats)
        elif file_extension in [".yml", ".yaml"]:
            serve_yaml(file, cats)
