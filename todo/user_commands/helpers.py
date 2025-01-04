import typer
from time import sleep
from sqlalchemy.orm import Session
from database.db import SessionLocal
from database.models import Task, Category
from rich import print
from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner
from typing import List
from sqlalchemy import func
from rich.prompt import Prompt
from rich.progress import track


def find_category(session: Session, categ: str) -> Category:
    category = (
        session.query(Category)
        .filter(func.lower(Category.name) == categ.lower())
        .first()
    )
    if not category:
        print("You should enter the category from the avialable category")
        raise typer.Exit()
    return category


def get_category_names_from_database():
    with SessionLocal() as session:
        category_names = [
            str(category.name) for category in session.query(Category).all()
        ]
    return category_names


def interactive_add_task_int(categ: str, console: Console):
    title = Prompt.ask("Enter the title")
    description = Prompt.ask("Enter the description")
    priority = Prompt.ask("Enter the priority", choices=["Top", "Medium", "Low"])

    spinner = Spinner("bouncingBall", text="Adding task...")
    with Live(spinner, refresh_per_second=10, console=console) as live:
        with SessionLocal() as session:
            try:
                category_id = find_category(session, categ).id

                new_task = Task(
                    title=title,
                    description=description,
                    category_id=category_id,
                    priority=priority,
                )
                session.add(new_task)
                console.print(
                    f"Task with title [red]{title}[/] in category [yello]{categ}[/] create [green]succesfully[/] :beer_mug:",
                    style="conceal",
                )
                session.commit()
            except Exception as e:
                print(e)
        for _ in range(10):
            sleep(0.1)
            live.refresh()


def panic(message: str):
    print(message)
    raise typer.Exit


def count_not_completed(query: List[Task]) -> int:
    return sum(1 for task in query if not task.completed)


def fake_progress_bar(range_progress: int, interval: float):
    for _ in track(range(range_progress), description="Reading from file..."):
        sleep(interval)
    for _ in track(range(range_progress), description="Adding task..."):
        sleep(interval)
