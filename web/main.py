from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Form, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from database.db import SessionLocal
from database.models import Priority
from toshu.user_commands.helpers import get_category_from_database
from utils.task import (
    all_task,
    complete,
    delete_task_util,
    single_task,
    update_task_independantly,
)

templates = Jinja2Templates(Path(__file__).parent / "templates")

app = FastAPI()

app.mount(
    "/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static"
)


@app.get("/")
async def home_page(request: Request, app_name: str = "Toshu"):
    return templates.TemplateResponse(
        "index.html", {"request": request, "name": app_name}
    )


@app.get("/tasks", name="task_list")
async def list_page(request: Request):
    with SessionLocal() as session:
        tasks = all_task(session)

    return templates.TemplateResponse(
        "task_list.html", {"request": request, "tasks": tasks}
    )


@app.get("/detail/{task_id}", name="task_detail")
async def task_detail(request: Request, task_id: int):
    with SessionLocal() as session:
        task = single_task(session, pk=task_id)
        if task is None:
            return templates.TemplateResponse(
                "task_not_found.html",
                {"request": request, "task_id": task_id},
            )
    return templates.TemplateResponse(
        "task_detail.html", {"request": request, "task": task}
    )


@app.get("/complete/{task_id}", name="complete_task")
async def complete_task(request: Request, task_id: int):
    with SessionLocal() as session:
        is_updated = complete(session, task_id)
        if not is_updated:
            raise HTTPException(
                status_code=403, detail="Task is already completed or doesn't exist"
            )
        else:
            # Correctly use `url_for` to generate the route dynamically
            detail_url = app.url_path_for("task_detail", task_id=task_id)
            return RedirectResponse(detail_url, status_code=303)


@app.get("/delete/{task_id}", name="delete_task")
async def delete_task(request: Request, task_id: int):
    _, task = delete_task_util(task_id, confirm=True)
    if not task:
        raise HTTPException(
            status_code=403, detail="Task not found, or altready deleted"
        )
    else:
        list_url = app.url_path_for("task_list")
        return RedirectResponse(list_url, status_code=303)


# @app.post("/update/{task_id}",name="update_task")
# async def update_task(request: Request, task_id: int, new_title, new_description, new_completion, new_priority: Priority, new_category)
# first implement update form logic


@app.get("/update/{task_id}", name="update_form_render")
async def upate_form_render(request: Request, task_id: int):
    with SessionLocal() as session:
        task = single_task(session, task_id)

        if not task:
            return templates.TemplateResponse(
                "task_not_found.html",
                {"request": request, "task_id": task_id},
            )
        categories = get_category_from_database()
        return templates.TemplateResponse(
            "task_update_form.html",
            {
                "request": request,
                "task": task,
                "categories": categories,
                "priorities": Priority,
            },
        )


@app.post("/update/{task_id}", name="update_validation")
async def update_task(
    request: Request,
    task_id: int,
    title: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    priority: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    completed: Optional[bool] = Form(False),
):
    # Create a dictionary from the form data
    form_data = {
        "title": title,
        "category": category,
        "priority": priority,
        "description": description,
        "completed": completed,
    }

    print(form_data)

    # Validate the form data using the Pydantic model
    # try:
    #     validated_data = TaskUpdateForm(**form_data)
    # except ValueError as e:
    #     raise HTTPException(status_code=400, detail=str(e))

    # Fetch the task from the database
    with SessionLocal() as session:
        task = single_task(session, task_id)
        if not task:
            return templates.TemplateResponse(
                "task_not_found.html",
                {"request": request, "task_id": task_id},
            )

        # Update the task with the validated data
        try:
            update_task_independantly(session, task, form_data)
        except AttributeError as e:
            print(e)
            return "something went extrement wrong"

    return {"message": "Task updated successfully"}
