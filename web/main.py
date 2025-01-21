from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(Path(__file__).parent / "templates")

app = FastAPI()


@app.get("/")
async def home_page(request: Request, app_name: str = "Toshu"):
    return templates.TemplateResponse(
        "index.html", {"request": request, "name": app_name}
    )
