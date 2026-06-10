# `config`

Django project configuration package. It contains the root URL routing, WSGI entry
point, and a split settings system that separates shared configuration from
environment-specific overrides. The `settings/` sub-package (base, dev, prod) holds all
Django settings; the active module is selected at runtime via the
`DJANGO_SETTINGS_MODULE` environment variable.

### `__init__.py`

Empty file that marks `config` as a Python package.

### `settings/__init__.py`

Empty file that makes `settings` a Python package so that `config.settings.dev` and
`config.settings.prod` are valid dotted-path imports for `DJANGO_SETTINGS_MODULE`.

### `settings/base.py`

Shared Django settings inherited by both `dev.py` and `prod.py`. Defines installed
apps (`core`, `common`, and the standard Django contrib suite), middleware stack,
template configuration (including the `common.context_processors.git_sha` processor),
SQLite database, auth password validators, and static-file paths. Reads `SECRET_KEY`
from the environment and attempts to load `GIT_SHA` from `version.txt`, falling back to
`"dev"`.

### `settings/dev.py`

Development environment overrides. Extends `base.py` with `DEBUG = True`, an empty
`ALLOWED_HOSTS`, `MESSAGE_LEVEL` set to `messages.DEBUG`, console-only logging at the
`DEBUG` level, and `USE_TZ = False`.

### `settings/prod.py`

Production environment overrides. Extends `base.py` with `DEBUG = False`,
`ALLOWED_HOSTS` locked to `cvss.clinicalgenome.org` and `cvss-test.clinicalgenome.org`,
`MESSAGE_LEVEL` set to `messages.INFO`, `USE_TZ = True`, and a two-handler logging setup
(console at `INFO` and a rotating file handler writing to `<project_root>/logs/cvss.log`
with 5 MB max size and 5 backups). Creates the log directory and file on startup if they
do not exist.

### `urls.py`

Root URL configuration. Mounts `core.urls` at the site root and the Django admin at
`/admin/`.

### `wsgi.py`

WSGI entry point. Loads environment variables from `.env` via `python-dotenv` (which
supplies `DJANGO_SETTINGS_MODULE` and other secrets) and exposes the `application`
callable for the web server.
