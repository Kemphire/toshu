import typer
from database.db import init_db
from .version import app as version_app
from .user_commands import app as user_app

init_db()

app = typer.Typer()

app.add_typer(version_app)
app.add_typer(user_app, name="td", help="User commads")

if __name__ == "__main__":
    app()
