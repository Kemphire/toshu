from typing import Annotated

from typer import Typer

from visualisation import plot_bar, plot_pie

app = Typer()


@app.command(short_help="plot charts related to the statistics of tasks", name="plot")
def plot_charts(type: Annotated[str, "type of chart to plot"]):
    if type.lower() == "bar":
        plot_bar()
    elif type.lower() == "pie":
        plot_pie()
