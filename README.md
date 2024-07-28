# Todaygenda

This app allows you to create an agenda based on what you would like to accomplish today. Provide your todo list and some estimates, and it will construct an agenda that shows you the best order to accomplish your daily tasks.

## How to use

1. For now, create a JSON file `today.json` in the project directory.

   ```json
   {
        "tasks": [
            "sample task    \t  15m",
        ]
    }
   ```

   Separate the task name and the duration with a tab.

2. Run the program: `pipenv run python -m main`
