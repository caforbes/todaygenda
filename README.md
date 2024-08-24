# Todaygenda

This app allows you to create an agenda based on what you would like to accomplish today. Provide your todo list and some estimates, and it will construct an agenda that shows you the best order to accomplish your daily tasks.

## Use the CLI todo list

1. First, set up the package environment.
    1. You'll need a working installation of Python 3.12
    2. Setup CLI dependencies by installing Pipenv and installing packages.
    <!-- FIX: add details to these steps -->
2. Open the program environment with `pipenv shell`. Or, prefix all the following commands with `pipenv run`.
3. View the program documentation and available commands:

    ```sh
    python -m cli.app --help
    ```

4. Try out the program commands:

    1. Add tasks to your todolist, with time estimates in minutes:

        ```sh
        python -m cli.app add "task I have to do" 15
        ```

    2. View your entire todolist and estimated finish time:

        ```sh
        python -m cli.app show
        ```

    3. Complete a task you've finished by providing its number.

        ```sh
        python -m cli.app complete 3
        ```

5. **Optional:** Make a command line alias to speed up your typing experience.

    ```sh
    alias today='pipenv run python -m cli.app'
    ```

    Now you can run commands more quickly.

    ```sh
    today add "get groceries" 45m
    today show
    ```
