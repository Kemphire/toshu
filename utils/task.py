from typing import Any, Dict, List

from sqlalchemy.orm import Session

from database.db import SessionLocal
from database.models import Category, Task


def all_task(session: Session) -> List[Task]:
    """Returns all task availablei in the db"""
    tasks = session.query(Task).all()
    return tasks


def single_task(session: Session, pk: Any) -> Task:
    """Returns a single task based on pk"""
    return session.get(Task, ident=pk)


def complete(session: Session, id: int) -> bool:
    """Mark task completed"""
    task = single_task(session, pk=id)
    if task is None:
        return False
    if bool(task.completed):
        return False
    else:
        task.completed = True
        session.commit()
        return True


def delete_task_util(id: int, confirm=False) -> tuple[Task | None, bool]:
    """Delete task based on id
    - return [None,True] if task sucessfully deleted
    - return [None,False] if not sucessfully delete or not found
    - return [Task,False] if task found but not deleted
    """
    # task = single_task(session, pk=id)
    # if task is None:
    #     return False
    # session.delete(task)
    # session.commit()
    # return True

    with SessionLocal() as session:
        task = single_task(session, pk=id)
        if not task:
            return None, False
        if confirm:
            session.delete(task)
            session.commit()
            return None, True
        else:
            return task, False


def update_task_independantly(
    session: Session, task: Task, update_dict: Dict[str, Any]
) -> Dict[str, Any] | None:
    if not update_dict:
        return None
    for key, value in update_dict.items():
        print(key, value)
        if key == "category":
            category = session.query(Category).filter(Category.name == value).first()
            setattr(task, key, category)
        setattr(task, key, value)
    session.commit()
    return update_dict
