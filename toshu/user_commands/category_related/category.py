
import typer
from rich import print
from rich.console import Console
from sqlalchemy.exc import IntegrityError, OperationalError

from database.db import SessionLocal
from database.models import Category

from ..console_output import *
from ..helpers import *

app = typer.Typer()

console = Console()


@app.command(short_help="add a new category")
def add(cat_name: str):
    """
    Create a new category of give name
    """
    with SessionLocal() as session:
        try:
            new_cat = Category(name=cat_name)
            session.add(new_cat)
            session.commit()
            list_category_int(new_cat.name, console)
        except IntegrityError:
            session.rollback()
            print(
                f"[bold red]Integrity Error:[/] Task with name [yellow]{cat_name}[/] is already in database"
            )
        except OperationalError:
            session.rollback()
            print(
                f"[bold red]Operation Error:[/] Task with name [yellow]{cat_name}[/] can't be added"
            )
        except Exception as e:
            session.rollback()
            print(e)
