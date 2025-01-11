import typer

from .category import app as category_app
from .console_output import app as terminal_print_ap
from .delete_category import app as delete_category_app
from .delete_task import app as delete_task_app
from .filter_tasks import app as filter_task_app
from .task import app as task_app

app = typer.Typer()

app.add_typer(category_app)
app.add_typer(task_app)
app.add_typer(terminal_print_ap)
app.add_typer(delete_task_app)
app.add_typer(delete_category_app)
app.add_typer(filter_task_app)
