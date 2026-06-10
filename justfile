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
# Continuous Integration Recipe
#=====================================================================

# Run all checks and tests that are run in CI. -----------------------
continuous-integration: py-format-check js-format-check py-lint js-lint py-type-check django-check django-collectstatic test-all
alias ci := continuous-integration

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

#=====================================================================
# JavaScript Recipes
#=====================================================================

# Run all JavaScript checks. -----------------------------------------
[group('javascript')]
js-all: js-format-check js-lint
alias jal := js-all

# Format JavaScript code. --------------------------------------------
[group('javascript')]
js-format:
    bunx biome format --write .
alias jsfm := js-format

# Check the JavaScript code for formatting issues. -------------------
[group('javascript')]
js-format-check:
    bunx biome format .
alias jsfc := js-format-check

# Check the JavaScript code for lint errors. -------------------------
[group('javascript')]
js-lint:
    bunx biome lint .
alias jslt := js-lint

# Try to fix lint errors in the JavaScript code. ---------------------
[group('javascript')]
js-lint-fix:
    bunx biome lint --write .
alias jslf := js-lint-fix

# Build our JavaScript dependencies. ---------------------------------
[group('javascript')]
js-build:
    bun build.js
alias jsbl := js-build

#=====================================================================
# Django Recipes
#=====================================================================

# Inspect the project for common problems. ---------------------------
[group('django')]
django-check:
    cd src && uv run manage.py check
alias djch := django-check

# Collect static files. ----------------------------------------------
[group('django')]
django-collectstatic: js-build
    rm -rf src/public/
    cd src && uv run manage.py collectstatic
alias djcs := django-collectstatic

# Make migrations. ---------------------------------------------------
[group('django')]
django-makemigrations:
    cd src && uv run manage.py makemigrations
alias djmm := django-makemigrations

# Apply migrations. --------------------------------------------------
[group('django')]
django-migrate:
    cd src && uv run manage.py migrate
alias djmi := django-migrate

# Run the development server. ----------------------------------------
[group('django')]
django-runserver:
    cd src && uv run manage.py runserver
alias djru := django-runserver

# Enter the shell. ---------------------------------------------------
[group('django')]
django-shell:
    cd src && uv run manage.py shell
alias djsh := django-shell

#=====================================================================
# Test Recipes
#=====================================================================

# Run all tests. -----------------------------------------------------
[group('test')]
test-all:
    cd src && uv run manage.py test --shuffle --parallel auto
alias tal := test-all
