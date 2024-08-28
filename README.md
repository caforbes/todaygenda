# Todaygenda

This app allows you to create an agenda based on what you would like to accomplish today. Provide your todo list and some estimates, and it will construct an agenda that shows you the best order to accomplish your daily tasks.

## Use the CLI todo list locally

1. Clone the package repository, and set up the package environment and dependencies.
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

## Development

## Local setup

1. Follow the instructions from step 1 above, AND ALSO:
    1. Install development dependencies with `pipenv install --dev`
    2. Ensure you have Postgres installed. <!-- FIX: add details -->
    3. Install [`dbmate`](https://github.com/amacneil/dbmate) to manage database migrations.
2. Environment variables should be setup in your `.env` file. (Use `docker.env` as a sample.)
    * `DATABASE_URL` and `TEST_DATABASE_URL`: Should be SQL connection strings with your credentials. Example: `postgresql://<USER>:<PW>@localhost:5432/todaygenda?sslmode=disable`
    * `ALLOWED_ORIGINS`: Should be a JSON string containing a list of origins that will be connecting. Example: `'["http://localhost:5173","https://www.example.com:5173"]'`
    <!-- TODO: more steps for how to run + migrate -->
3. Apply migrations. ([Get familiar with dbmate commands here.](https://github.com/amacneil/dbmate))

    ```sh
    dbmate up
    ```

4. Run the API dev server.

    ```sh
    fastapi dev api/main.py
    ```

5. Visit the server at [http://localhost:8000/docs](http://localhost:8000/docs)

### Testing and helpful commands

Some commands have been setup in the [Makefile](./Makefile) for helpful development workflows.

* Typecheck, format, lint: `make` or `make default`
* Test: `make pytest`
* Coverage report: `make coverage`
* Format/lint (plus build dependencies): `make testall`

## Setup with Docker

1. Clone the package repository.
2. Create a file `db/password.txt` containing your preferred user password for the database. Update the password in your copy of the `docker.env` file.
    * You may also wish to update other environment variables in that file for your purposes..
3. Run `docker compose up --build`. Confirm that the containers built successfully.
4. <!-- TODO: migration step --> ?
5. You are set up. Future runs can use:
    * Run the server with `docker compose up`
    * Visit the api docs running at: [http://localhost:8000/docs](http://localhost:8000/docs)
