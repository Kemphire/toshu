import typer

from .user_commands import app as user_app
from .user_commands.category_related import app as category_related
from .user_commands.creation_from_file import app as app_for_create_using_file
from .user_commands.output_to_file import app as file_output_app
from .user_commands.plot_charts import app as plot_app
from .version import app as version_app

app = typer.Typer()

app.add_typer(version_app)
app.add_typer(file_output_app)
app.add_typer(app_for_create_using_file)
app.add_typer(plot_app)
app.add_typer(user_app, name="task", help="task realated commands")
app.add_typer(category_related, name="category", help="category related commands")


# for info dashboard


if __name__ == "__main__":
    app()
