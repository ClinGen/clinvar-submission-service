# Provides a simple way to run commands for this project.
#
# This file also documents command line "recipes" for this project. In order to use it,
# you must install the `just` program: https://github.com/casey/just.
#
# To list the available recipes and what they do, invoke `just -l` at the command line.
# (The dashes after the comment describing the recipe are there to help the formatting
# of the output of the `just -l` command.)
#
# NOTE: For the sake of simplicity, we assume the user of this justfile is invoking the
# recipes from the root of the repository.

# Load the .env file before we run commands.
set dotenv-load := true

#=====================================================================
# Python Recipes
#=====================================================================

# Run all Python code quality checks. --------------------------------
[group('python')]
py-all: py-format-check py-lint py-type-check
alias pyal := py-all

# Format the Python code. --------------------------------------------
[group('python')]
py-format:
    uv run ruff format
alias pyfm := py-format

# Check the Python code for formatting issues. -----------------------
[group('python')]
py-format-check:
    uv run ruff format --check
alias pyfc := py-format-check

# Check the Python code for lint errors. -----------------------------
[group('python')]
py-lint:
    uv run ruff check
alias pylt := py-lint

# Try to fix lint errors in the Python code. -------------------------
[group('python')]
py-lint-fix:
    uv run ruff check --fix
alias pylf := py-lint-fix

# Check Python type hints. -------------------------------------------
[group('python')]
py-type-check:
    uv run ty check
alias pytc := py-type-check