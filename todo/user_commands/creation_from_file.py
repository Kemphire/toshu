from pathlib import Path
from typing import Annotated

import typer

from file_io import (
    create_task_using_csv,
    create_task_using_json,
    create_task_using_yaml,
)


app = typer.Typer()


@app.command(short_help="Gernerate tasks from various types of files", name="create")
def get_tasks_in_file(
    file: Annotated[
        Path,
        typer.Option(
            "-f",
            "--file",
            exists=True,
            file_okay=True,
            writable=True,
            readable=True,
            dir_okay=False,
            resolve_path=True,
        ),
    ],
):
    file_extension = file.suffix
    if file_extension == ".csv":
        create_task_using_csv(file)
    elif file_extension == ".json":
        create_task_using_json(file)
    elif file_extension in [".yml", ".yaml"]:
        create_task_using_yaml(file)
