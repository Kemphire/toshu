from functools import wraps
from typing import List, Tuple

from database.db import SessionLocal
from database.models import Category, Task


def randomize_the_list(func):
    """
    returns a reshuffeled randomized list
    """

    @wraps(func)
    def wrapper(*args, **kwargs) -> Tuple[List[str], List[int]]:
        result: List[Tuple[str, int]] = func(*args, **kwargs)
        names: List[str] = []
        counts: List[int] = []
        for i, j in result:
            names.append(i)
            counts.append(j)
        return names, counts

    return wrapper


@randomize_the_list
def get_category_with_number_of_sizes() -> List[Tuple[str, int]]:
    """
    Returs a tuple with two elements,
        1. names of categories
        2. no of tasks in those categories
    """
    with SessionLocal() as session:
        cats = session.query(Category).all()
        cat_name_and_total_tasks = [(cat.name, cat.no_of_tasks) for cat in cats]
        orphan_task_count = session.query(Task).filter(Task.category_id == None).count()
        cat_name_and_total_tasks.append(("Orphans", orphan_task_count))
        final_data: List[Tuple[str, int]] = sorted(
            cat_name_and_total_tasks, key=lambda x: x[1], reverse=True
        )
        names: List[str] = []
        counts: List[int] = []
        for i, j in final_data:
            names.append(i)
            counts.append(j)
    return final_data[:5]
