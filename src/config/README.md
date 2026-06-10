# `config`

Django project configuration. Contains settings, the root URL dispatcher, and the WSGI
entry point.

### `__init__.py`

Marks `config` as a Python package.

### `settings.py`

Central Django settings module.

### `urls.py`

Root URL configuration. Routes all top-level paths to `core.urls` and mounts Django's
admin interface at `/admin/`.

### `wsgi.py`

WSGI entry point for production servers (e.g., Gunicorn). Sets `DJANGO_SETTINGS_MODULE`
to `config.settings` and exposes the standard `application` callable.
