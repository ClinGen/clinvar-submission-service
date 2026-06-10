# `core`

The `core` Django app provides the site-wide informational pages — home, about, contact,
and help — that are not specific to any submission workflow. It registers itself with
Django's app registry, defines URL routes for those pages, renders them via simple
function-based views, and verifies their behavior with a test suite.

### `__init__.py`

Empty module marker that makes `core` a Python package.

### `apps.py`

Defines `CoreConfig`, the Django `AppConfig` subclass that registers the `core` app and
sets `BigAutoField` as the default primary-key type.

### `templates/core/about.html`

Renders the About page, which gives a one-sentence description of the ClinVar Submission
Service (CVSS) and its role in allowing ClinGen applications to submit curations to
ClinVar.

### `templates/core/contact.html`

Renders the Contact page, directing users to email `cvss@clinicalgenome.org` with
questions, comments, or concerns.

### `templates/core/help.html`

Renders the Help page, instructing users to email `cvss@clinicalgenome.org` (with "CVSS
Help" in the subject) and listing the information they should include: a description of
the issue, reproduction steps, OS, browser, and any screenshots or error messages.

### `templates/core/home.html`

Renders the Home page, displaying the service title and a greeting that indicates
whether the current user is logged in (showing their email) or not.

### `tests.py`

Contains view tests for each of the four core pages (`HomeViewTest`, `AboutViewTest`,
`ContactViewTest`, `HelpViewTest`). Each test uses `BaseViewTestMixin` to assert the
correct URL, template, page name, and expected text strings.

### `urls.py`

Maps URL paths to the four core views.

### `views.py`

Defines four function-based views — `home`, `about`, `contact`, and `help_` — each of
which renders its corresponding template and returns an `HttpResponse`.
