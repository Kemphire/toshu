from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.future import select

from database.db import SessionLocal
from database.models import Task

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


@app.get("/tasks")
async def list_page(request: Request):
    with SessionLocal() as session:
        result = session.execute(select(Task))
        tasks = result.scalars().all()

        return templates.TemplateResponse(
            "task_list.html", {"request": request, "tasks": tasks}
        )
