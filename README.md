# Todaygenda

This app allows you to create an agenda based on what you would like to accomplish today. Provide your todo list and some estimates, and it will construct an agenda that shows you the best order to accomplish your daily tasks.

## Use the CLI todo list

1. Set an environment variable `DAYLIST_FILE` for where your task list will be stored in JSON format. This can be stored in `.env`.

    ```sh
    export DAYLIST_FILE="daylist.json"
    ```

2. If needed, open the program environment with `pipenv shell`. Or, prefix all the following commands with `pipenv run`.
3. View the program documentation and available commands:

    ```sh
    python -m cli --help
    ```

4. Add tasks to your todolist, with time estimates in minutes:

    ```sh
    python -m cli add "task I have to do" 15
    ```

5. View your entire todolist and estimated finish time:

    ```sh
    python -m cli show
    ```
