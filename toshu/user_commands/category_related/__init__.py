import typer

from .category import app as add_app
from .delete_category import app as delete_app
from .list_category import app as list_app

app = typer.Typer()

app.add_typer(add_app)
app.add_typer(delete_app)
app.add_typer(list_app)
