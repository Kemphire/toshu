import typer
from database.db import SessionLocal
from database.models import Task
from rich import print

app = typer.Typer()


@app.command()
def delete(id: int):
    """Delete the task for given id"""
    # session: Session = SessionLocal()
    #
    # task = session.get(Task, id)
    # if not task:
    #     print(f"[bold red]Session with [blue]{id}[/blue] not present[/bold red]")
    #     raise typer.Exit()
    #
    # task_str = typer.style(
    #     task.title,
    #     underline=True,
    #     fg=typer.colors.RED,
    #     bold=True,
    # )
    # task_id = typer.style(task.id, fg=typer.colors.GREEN)
    # confirmation = typer.confirm(
    #     f"Do you really want to delete the task with title {task_str} with id {task_id}"
    # )
    #
    # if not confirmation:
    #     print("[magenta]Task deletion cancelled[/magenta]")
    #     session.close()
    #     raise typer.Exit()
    #
    # session.delete(task)
    # session.commit()
    # session.close()
    #
    # print(f"Task with title [bold red]{task.title}[/bold red] got deleted!")

    with SessionLocal() as session:
        task = session.get(Task, id)
        if not task:
            print(f"[bold red]task with id [blue]{id}[/blue] not present[/bold red]")
            raise typer.Exit()

        task_str = typer.style(
            task.title,
            underline=True,
            fg=typer.colors.RED,
            bold=True,
        )
        task_id = typer.style(task.id, fg=typer.colors.GREEN)
        confirmation = typer.confirm(
            f"Do you really want to delete the task with title {task_str} with id {task_id}"
        )

        if not confirmation:
            print("[magenta]Task deletion cancelled[/magenta]")
            session.close()
            raise typer.Exit()

        session.delete(task)
        session.commit()
        session.close()

        print(f"Task with title [bold red]{task.title}[/bold red] got deleted!")
