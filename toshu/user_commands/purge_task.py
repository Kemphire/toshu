from datetime import datetime
from typing import Annotated

import typer
from typer import Typer

from database.db import SessionLocal
from database.models import Task

from .helpers import panic

app = Typer()


@app.command(short_help="purge completed and/or overdue tasks")
def purge(
    completed: Annotated[bool, typer.Option()] = True,
    overdue: Annotated[bool, typer.Option()] = False,
):
    """
    purge completed and/or overdue tasks
    """
    with SessionLocal() as session:
        query = session.query(Task).filter(Task.completed == completed)
        if overdue:
            query = query.filter(Task.due < datetime.now())
        if (rows_affected := query.count()) > 0:
            confirm = typer.confirm(
                f"Really wanna delete {rows_affected} tasks", default=False
            )
            if confirm:
                query.delete(synchronize_session=False)
                panic(f"Total [green]{rows_affected}[/] task got deleted", severe=2)
            else:
                typer.echo("Aborting deletion")
                raise typer.Abort()
        else:
            panic("There are [red]0[/] overdue tasks", severe=2)
        session.commit()
    if not (overdue | completed):
        typer.echo("Error: No filter option specified", err=True)
        raise typer.Abort()
