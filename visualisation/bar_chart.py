from typing import List

import plotext as plt

from .helper_functions import get_category_with_number_of_sizes

cat_names, total_tasks = get_category_with_number_of_sizes()


def plot_bar(xticks: List[str] = cat_names, yticks: List[int] = total_tasks) -> None:
    plt.theme("dark")
    plt.bar(xticks, yticks)
    plt.plot_size(plt.terminal_width() / 2, plt.terminal_height() / 3)
    plt.title("Tasks in a Category")
    plt.show()
