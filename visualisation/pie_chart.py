from typing import List

import termcharts

from .helper_functions import get_category_with_number_of_sizes

names, tasks = get_category_with_number_of_sizes()


def plot_pie(xticks: List[str] = names, yticks: List[int] = tasks):
    chart = termcharts.pie(
        {name: count for name, count in zip(xticks, yticks)}, title="categories"
    )

    print(chart)
