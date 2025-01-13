from datetime import datetime
from enum import Enum
from typing import Union

from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    event,
)
from sqlalchemy import (
    Enum as SEnum,
)
from sqlalchemy.orm import (
    Mapped,
    Session,
    attributes,
    declarative_base,
    mapped_column,
    relationship,
)

Base = declarative_base()


# enum for priority of priorities
class Priority(str, Enum):
    T = "Top"
    M = "Medium"
    L = "Low"

    def __str__(self) -> str:
        return self.value


class Category(Base):
    __tablename__ = "category"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=True)
    no_of_tasks: Mapped[int] = mapped_column(default=0)

    tasks = relationship(
        "Task",
        back_populates="category",
    )

    def __repr__(self):
        return self.name


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)

    title = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)
    completed = Column(Boolean, default=False)
    category_id = Column(
        Integer,
        ForeignKey(
            "category.id",
        ),
        nullable=True,
    )
    priority = Column(SEnum(Priority), default=Priority.L, nullable=False)

    created_at: Mapped[datetime] = mapped_column(default=datetime.now())

    category = relationship("Category", back_populates="tasks")

    def __repr__(self) -> str:
        return f"<Task(id = {self.id}), title='{self.title}', completed={self.completed}, priority={self.priority}>"


@event.listens_for(Task, "after_insert")
def increment_task_count(mapper, connection, target: Task):
    """
    Increase the number_of_task column in Category table, when a new task is inserted in Task table
    """
    session = Session(bind=connection)
    if target.category_id is not None:
        category: Union[Category, None] = session.get(Category, target.category_id)
    else:
        category = None
    if category:
        category.no_of_tasks += 1
        session.commit()
    session.close()


@event.listens_for(Task, "after_update")
def handle_no_of_task_after_update(mapper, connection, target: Task):
    """
    Properly handles the number of tasks in category column, after and update is performed on the task object
    """
    with Session(bind=connection) as session:
        if attributes.get_history(target, "category_id").has_changes():
            old_category_id, new_category_id = (
                attributes.get_history(target, "category_id").deleted[0],
                target.category_id,
            )

            if old_category_id:
                old_category = session.get(Category, old_category_id)
            else:
                old_category = None
            if old_category and old_category.no_of_tasks >= 1:
                old_category.no_of_tasks -= 1

            new_category = session.get(Category, new_category_id)
            if new_category:
                new_category.no_of_tasks += 1

            session.commit()


@event.listens_for(Task, "after_delete")
def handle_task_deletion(mapper, connection, target: Task):
    """Decrease the no_of_tasks columns when a task associated with the category gets deleted"""
    with Session(bind=connection) as session:
        category_obj = session.get(Category, target.category_id)
        if category_obj:
            category_obj.no_of_tasks -= 1
        session.commit()
