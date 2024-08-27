# Todaygenda

This app allows you to create an agenda based on what you would like to accomplish today. Provide your todo list and some estimates, and it will construct an agenda that shows you the best order to accomplish your daily tasks.

## Installation

1. First, set up the package environment.
    1. You'll need a working installation of Python 3.12
    2. Setup CLI dependencies by installing Pipenv and installing packages.
    <!-- FIX: add details to these steps -->
2. Open the program environment with `pipenv shell`. Or, prefix all the following commands with `pipenv run`.

<!-- TODO: or use docker instead -->

## Use the CLI todo list

1. View the program documentation and available commands:

    ```sh
    python -m cli.app --help
    ```

2. Try out the program commands:

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

3. **Optional:** Customize where your list is stored by setting an environnment variable.
    <!-- TODO: add more -->

4. **Optional:** Make a command line alias to speed up your typing experience.

    ```sh
    alias today='pipenv run python -m cli.app'
    ```

    Now you can run commands more quickly.

    ```sh
    today add "get groceries" 45m
    today show
    ```

## Run the API

1. Environment variables can be setup directly or loaded in an `.env` file.
    * `ALLOWED_ORIGINS`: Should be a JSON string containing a list of origins e.g. `'["http://localhost:5173","https://www.example.com:5173"]'`
2. How to run:

    * Development

        ```sh
        fastapi dev api/main.py
        ```

    * Production

        ```sh
        uvicorn 'api.main:app' --host=0.0.0.0 --port=8000
        ```

    * From Docker

        ```sh
        docker compose up --build
        ```
