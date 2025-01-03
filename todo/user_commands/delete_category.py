from rich.prompt import Prompt
import typer
from database.db import SessionLocal
from database.models import Category, Task
from todo.user_commands.helpers import panic


app = typer.Typer()


@app.command(short_help="Delete category", name="del_cat")
def delete_category(title_or_id: str):
    """
    Delete category and treat the orphan tasks according to the user choices.
    1. wheahter to delete all related tasks
    2. wheahter to make the related tasks orphan by marking their parent category as NULL
    1. wheahter to change their category
    """
    with SessionLocal() as session:
        if title_or_id.isdigit():
            category_obj = session.get(Category, title_or_id)
            if category_obj:
                preference = ask_for_deletion_preference()
                match preference:
                    case 1:
                        rows_deleted_of_task = (
                            session.query(Task)
                            .filter(Task.category_id == title_or_id)
                            .delete()
                        )
                        print(f"Total {rows_deleted_of_task} rows got deleted")
                    case 2:
                        rows_affected = (
                            session.query(Task)
                            .filter(Task.category_id == title_or_id)
                            .update({"category_id": None})
                        )
                        print(
                            f"Total {rows_affected} got their category changed to None"
                        )
                    case 3:
                        available_cats = (
                            session.query(Category)
                            .filter(Category.id != title_or_id)
                            .all()
                        )
                        choices = [cat.name for cat in available_cats]
                        new_category = Prompt.ask(
                            f"Choose your new category for the the task with category id as {title_or_id}",
                            choices=choices,
                        )
                        new_category = available_cats[choices.index(new_category)]
                        rows_affected = (
                            session.query(Task)
                            .filter(Task.category_id == title_or_id)
                            .update(
                                {
                                    "category": new_category,
                                    "category_id": new_category.id,
                                },
                                synchronize_session=False,
                            )
                        )
                        print(f"Total {rows_affected} got their category changed")
                    case _:
                        panic("Not expected")
        else:
            category_obj = session.get(Category, {"name": title_or_id})
            if category_obj:
                preference = ask_for_deletion_preference()
                match preference:
                    case 1:
                        rows_deleted_of_task = (
                            session.query(Task)
                            .filter(Task.category_id == category_obj.id)
                            .delete()
                        )
                        print(f"Total {rows_deleted_of_task} rows got deleted")
                    case 2:
                        rows_affected = (
                            session.query(Task)
                            .filter(Task.category_id == category_obj.id)
                            .update({"category_id": None})
                        )
                        print(
                            f"Total {rows_affected} got their category changed to None"
                        )
                    case 3:
                        available_cats = (
                            session.query(Category)
                            .filter(Category.id != category_obj.id)
                            .all()
                        )
                        choices = [cat.name for cat in available_cats]
                        new_category = Prompt.ask(
                            f"Choose your new category for the the task with category id as {title_or_id}",
                            choices=choices,
                        )
                        new_category = available_cats[choices.index(new_category)]
                        rows_affected = (
                            session.query(Task)
                            .filter(Task.category_id == title_or_id)
                            .update(
                                {
                                    "category": new_category,
                                    "category_id": new_category.id,
                                },
                                synchronize_session=False,
                            )
                        )
                        print(f"Total {rows_affected} got their category changed")
                    case _:
                        panic("Not expected")
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
