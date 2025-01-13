from typing import Annotated, Tuple

import typer
from rich.prompt import Prompt
from sqlalchemy.orm import Session

from database.db import SessionLocal
from database.models import Category, Task
from toshu.user_commands.helpers import panic

from ..helpers import *

app = typer.Typer()


@app.command(short_help="Delete category")
def delete(name_or_id: str):
    """
    Delete category and treat the orphan tasks according to the user choices.
    1. wheahter to delete all related tasks
    2. wheahter to make the related tasks orphan by marking their parent category as NULL
    1. wheahter to change their category
    """
    with SessionLocal() as session:
        try:
            if name_or_id.isdigit():
                _delete_when_digit(session, int(name_or_id))
            else:
                _delete_when_name_of_cat(session, name_or_id)
        except Exception as e:
            typer.echo(e)
        else:
            session.commit()


def ask_for_deletion_preference() -> int:
    """Ask for deletion method"""

    prefer = Prompt.ask(
        """
    1. Delete all tasks, associated with this category
    2. Set task of associated category to NULL
    3. Replace category with another category
    """,
        choices=list("123"),
    )
    return int(prefer)


def _delete_when_digit(session: Session, id: int):
    try:
        category_obj = session.query(Category).filter(Category.id == id)[0]
    except IndexError:
        category_obj = None
    if category_obj:
        preference = ask_for_deletion_preference()
        match preference:
            case 1:
                rows_deleted_of_task = _handle_case_1(session, category_obj)
                print(f"Total {rows_deleted_of_task} rows got deleted")
            case 2:
                rows_affected = _handle_case_2(session, category_obj)
                print(f"Total {rows_affected} got their category changed to None")
            case 3:
                rows_affected, new_category = _handle_case_3(
                    session, category_obj, category_obj.name
                )
                setattr(
                    new_category,
                    "no_of_tasks",
                    new_category.no_of_tasks + rows_affected,
                )
                print(f"Total {rows_affected} task got their category changed")
            case _:
                panic("Not expected")
    else:
        panic(f"[red]{id}[/] is not a valid ID of category")
    session.delete(category_obj)


def _delete_when_name_of_cat(session: Session, name: str) -> None:
    try:
        category_obj = session.query(Category).filter(Category.name == name)[0]
    except IndexError:
        category_obj = None
    if category_obj:
        preference = ask_for_deletion_preference()
        match preference:
            case 1:
                rows_deleted_of_task = _handle_case_1(session, category_obj)
                print(f"Total {rows_deleted_of_task} rows got deleted")
            case 2:
                rows_affected = _handle_case_2(session, category_obj)
                print(f"Total {rows_affected} got their category changed to None")
            case 3:
                rows_affected, new_category = _handle_case_3(
                    session, category_obj, name
                )
                setattr(
                    new_category,
                    "no_of_tasks",
                    new_category.no_of_tasks + rows_affected,
                )
                print(f"Total {rows_affected} got their category changed")
            case _:
                panic("Not expected")
    else:
        panic(f"[red]{name}[/] is not a valid category")
    session.delete(category_obj)


def _handle_case_1(
    session: Session, category_obj: Category
) -> Annotated[int, "Number of tasks got deleted"]:
    return session.query(Task).filter(Task.category_id == category_obj.id).delete()


def _handle_case_2(
    session: Session, category_obj: Category
) -> Annotated[int, "Number of tasks got orphan"]:
    return (
        session.query(Task)
        .filter(Task.category_id == category_obj.id)
        .update({"category_id": None})
    )


def _handle_case_3(
    session: Session, category_obj: Category, old_name: str
) -> Annotated[
    Tuple[int, Category],
    "Number of tasks got their category changed, and updated category of tasks",
]:
    available_cats = (
        session.query(Category).filter(Category.id != category_obj.id).all()
    )
    choices = [cat.name for cat in available_cats]
    new_category = Prompt.ask(
        f"Choose your new category for the the tasks with category name {old_name}",
        choices=choices,
    )
    new_category = available_cats[choices.index(new_category)]
    rows_affected = (
        session.query(Task)
        .filter(Task.category_id == category_obj.id)
        .update(
            {
                "category_id": new_category.id,
            },
        )
    )

    return rows_affected, new_category
