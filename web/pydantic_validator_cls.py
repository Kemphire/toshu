from typing import Optional

from pydantic import BaseModel, Field, validator

from database.models import Priority
from toshu.user_commands.helpers import get_category_names_from_database


class TaskUpdateForm(BaseModel):
    title: Optional[str] = Field(
        None, min_length=1, max_length=100, description="title of the task"
    )
    category: Optional[str] = None
    priority: Optional[Priority] = None
    description: Optional[str] = Field(
        None, min_length=1, max_length=600, description="description of the task"
    )
    completed: Optional[bool] = None

    @validator("category")
    def category_must_be_valid(cls, value):
        if value and value not in get_category_names_from_database():
            raise ValueError("Not a valid category")
        return value
