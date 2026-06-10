# `core`

The primary Django app for the ClinVar Submission Service. Houses the top-level pages
(home, about, contact, help) and their corresponding URL routes, views, and templates.
Feature-specific submission logic will live in separate apps; `core` owns only the
application shell.

### `__init__.py`

Marks `core` as a Python package.

### `apps.py`

Defines `CoreConfig`, which registers the app with Django under the name `"core"` and
sets `BigAutoField` as the default primary key type.

### `templates/core/about.html`

Extends `layouts/base.html`. Describes the ClinVar Submission Service (CVSS) and its
purpose — providing ClinGen applications with a convenient way to submit curations to
ClinVar.

### `templates/core/contact.html`

Extends `layouts/base.html`. Displays the CVSS support email address
(`cvss@clinicalgenome.org`) for questions, comments, and concerns.

### `templates/core/help.html`

Extends `layouts/base.html`. Instructs users how to report issues, listing the
information to include in a support email (description, reproduction steps, OS, browser,
screenshots).

### `templates/core/home.html`

Extends `layouts/base.html`. Landing page for the application. Shows the authenticated
user's email when logged in, or a "not logged in" notice otherwise.

### `urls.py`

Maps the four top-level routes to their view functions.

### `views.py`

Simple view functions that render the four core pages. Each accepts an `HttpRequest` and
returns an `HttpResponse` via `render`. The help view is named `help_` (with trailing
underscore) to avoid shadowing Python's built-in `help`.
