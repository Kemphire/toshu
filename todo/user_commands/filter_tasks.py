from datetime import datetime
from typing import Annotated, Optional

import typer

from database.models import Priority

app = typer.Typer()


@app.command(
    short_help="filter tasks based on parameters, based on logical Intersection"
)
def filter(
    task_title: Annotated[Optional[str], typer.Option("-t", "--task-title")],
    categ: Annotated[
        Optional[str], typer.Option("-c", "--category", help="None for orphan")
    ],
    created_before_delta: Annotated[
        Optional[datetime],
        typer.Option(
            "-c-before",
            "--created-before",
            help="task created withing the specified time frame",
            formats=[
                "%Y-%m-%d",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M:%S",
                "%m/%d/%Y",
                "%m/%d/%Y %H:%M:%S",
            ],
        ),
    ],
    priority: Annotated[
        Optional[Priority], typer.Option("-p", "--priority", show_choices=True)
    ],
):
    # not correct currently try to use sql where statement using sqlalchemy, it will be much better than finding all of the filter seperately
    # and then combining and converting them into set
    query_dict = {}
    if task_title:
        query_dict["title"] = task_title
    if categ:
        query_dict["category"] = categ
    if created_before_delta:
        ...
    if priority:
        query_dict["priority"] = priority
