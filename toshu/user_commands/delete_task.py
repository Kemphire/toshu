import typer
from rich import print
from rich.prompt import Confirm

from database.db import SessionLocal
from database.models import Task
from toshu.user_commands.helpers import panic

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


@app.command(short_help="delete all the orphan task", name="kill-orphan")
def delete_orphan():
    with SessionLocal() as session:
        orhphan_tasks = session.query(Task).filter(Task.category_id == None)
        orphan_tasks_count = orhphan_tasks.count()
        if orphan_tasks_count == 0:
            panic("There are not orphan tasks", severe=1)
        confirmation = Confirm.ask(f"Do you want to delete {orphan_tasks_count} tasks")
        if confirmation:
            orhphan_tasks.delete()
            print(f"Successfully deleted {orphan_tasks_count}")
        else:
            panic(f"Aborting delete for {orphan_tasks_count} tasks...", severe=1)
        session.commit()
