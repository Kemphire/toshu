import random
from typer.testing import CliRunner
from todo.user_commands.task import app

runner = CliRunner(mix_stderr=False)


def test_add_task_non_interactive():
    result = runner.invoke(
        app, ["add-task", "second_task", "--categ", "from_file_json"]
    )
    assert result.exit_code == 0
    assert "succesfully" in result.stdout
    assert "second_task" in result.stdout


def test_add_interactive():
    random_prefix = random.random()
    result = runner.invoke(
        app,
        ["add-task", "--categ", "first_categ", "--interactive"],
        input=f"test_task_{random_prefix}\n No need for description\nLow\n",
    )
    assert result.exit_code == 0
    assert "succesfully" in result.stdout
    assert f"test_task_{random_prefix}" in result.stdout


def test_mark_update():
    random_prefix = random.random()
    task = f"test_task_{random_prefix}"
    runner.invoke(
        app,
        ["add-task", "--categ", "first_categ", "--interactive"],
        input=f"{task}\n No need for description\nLow\n",
    )
    result2 = runner.invoke(app, ["mark-updated", f"{task}"])
    assert result2.exit_code == 0
    assert "completed" in result2.stdout.rsplit()
    result3 = runner.invoke(app, ["mark-updated", f"{task}"])
    assert result3.exit_code != 0
    assert "already completed 💩" in result3.stderr


def test_task_update_title():
    random_prefix = random.random()
    task = f"test_task_{random_prefix}"
    runner.invoke(app, ["add-task", task, "--categ", "first_categ"])
    id_of_task = runner.invoke(app, ["get-id", task]).output

    result = runner.invoke(
        app,
        [
            "update-task",
            id_of_task,
        ],
        input="n\nn\nn\nn\n",
    )
    assert result.exit_code == 0
    assert "No changes have been made" in result.stdout

    new_task = f"{task}_{random.random()}"
    input_sequence = "\n".join(["y", "n", "n", "n", f"{new_task}"])
    result1 = runner.invoke(
        app,
        [
            "update-task",
            id_of_task,
        ],
        # add a escape sequence at the end of the input
        input=f"{input_sequence}\n",
    )
    assert result1.exit_code == 0
    assert all(
        word
        for word in f"Task with title {task} has been changed!"
        if word in result1.stdout
    )


def test_task_update_description():
    random_prefix = random.random()
    task = f"test_task_{random_prefix}"
    runner.invoke(app, ["add-task", task, "--categ", "first_categ"])
    id_of_task = runner.invoke(app, ["get-id", task]).output

    new_description = f"{task}_{random.random()}_for_description"
    input_sequence = "\n".join(["n", "y", "n", "n", f"{new_description}"])
    result1 = runner.invoke(
        app,
        [
            "update-task",
            id_of_task,
        ],
        # add a escape sequence at the end of the input
        input=f"{input_sequence}\n",
    )
    assert result1.exit_code == 0
    assert all(
        word
        for word in f"Task with title {task} has been changed!"
        if word in result1.stdout
    )


def test_task_update_completion_status():
    random_prefix = random.random()
    task = f"test_task_{random_prefix}"
    runner.invoke(app, ["add-task", task, "--categ", "first_categ"])
    id_of_task = runner.invoke(app, ["get-id", task]).output

    new_description = f"{task}_{random.random()}_for_description"
    input_sequence = "\n".join(["n", "n", "y", "n"])
    result1 = runner.invoke(
        app,
        [
            "update-task",
            id_of_task,
        ],
        # add a escape sequence at the end of the input
        input=f"{input_sequence}\n",
    )
    assert result1.exit_code == 0
    assert all(
        word
        for word in f"Task with title {task} has been changed!"
        if word in result1.stdout
    )


# test in the file which contains test related to category
# def test_task_update_category():
#     random_prefix = random.random()
#     task = f"test_task_{random_prefix}"
#     runner.invoke(app, ["add-task", task, "--categ", "first_categ"])
#     id_of_task = runner.invoke(app, ["get-id", task]).output
#
#     new_description = f"{task}_{random.random()}_for_description"
#     input_sequence = "\n".join(["n", "n", "y", "n"])
#     result1 = runner.invoke(
#         app,
#         [
#             "update-task",
#             id_of_task,
#         ],
#         # add a escape sequence at the end of the input
#         input=f"{input_sequence}\n",
#     )
#     assert result1.exit_code == 0
#     assert all(
#         word
#         for word in f"Task with title {task} has been changed!"
#         if word in result1.stdout
#     )
