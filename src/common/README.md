# `common`

Shared utilities used across the entire application: context processors, template tags,
reusable form/UI templates, and base test helpers. Nothing in this directory is specific
to any one feature app.

### `__init__.py`

Marks `common` as a Django app so it can be listed in `INSTALLED_APPS` and have its
template tags and templates discovered automatically.

### `context_processors.py`

Injects the `GIT_SHA` variable into every template context. The SHA is read from
`version.txt` at startup (falling back to `"dev"` if the file is absent), and is
rendered in the footer to show the deployed version.

### `templates/common/form/input/radio.html`

Reusable partial for rendering a Django form radio-button field. Accepts `field`,
`hide_label`, and `show_help` context variables. Iterates over the radio choices and
wraps each in its own `<div>`.

### `templates/common/form/input/text.html`

Reusable partial for rendering a Django form text input. Accepts `field`, `hide_label`,
`show_help`, `type`, `autocomplete`, and `placeholder`. Applies Bulma's `.input` class
and optionally hides the label for compact layouts.

### `templates/common/form/select/default.html`

Reusable partial for a plain Bulma `<select>` dropdown. Accepts `field`, `show_label`,
`show_help`, and an optional `class` string appended to the `.select` wrapper (e.g.,
`is-fullwidth`).

### `templates/common/form/select/search.html`

Reusable partial for a searchable select powered by Choices.js. Initializes a `Choices`
instance on `htmx:load` so it works inside HTMX-swapped fragments. Accepts `field`,
`hide_label`.

### `templates/common/form/textarea.html`

Reusable partial for a Bulma-styled `<textarea>`. Accepts `field` and renders the label
and control wrapper.

### `templates/common/icon.html`

One-liner partial that renders a Bootstrap Icon inline. Accepts `icon_name` (the icon
slug, e.g. `"house"`) and produces `<i class="bi bi-{icon_name} mr-2"></i>`.

### `templates/common/linkout.html`

Renders an anchor tag that opens in a new tab with `rel="noopener noreferrer"`. Accepts
`url` and `text`, and appends a Bootstrap Icon arrow to signal the external link.

### `templatetags/__init__.py`

Marks `templatetags` as a Python package so Django's template engine can discover the
custom filters defined in `custom_filters.py`.

### `templatetags/custom_filters.py`

Defines three custom Django template filters:

- `get_val` — returns the value of a named attribute on a model instance.
- `get_item` — returns the value for a key in a dictionary.
- `in_get` — returns `True` if a string is present as a key in `request.GET`.

### `tests.py`

Provides `BaseViewTestMixin`, a mixin class inherited by view test cases across the
project. It supplies three standard tests (`test_template`,
`test_page_name_in_response`, `test_expected_text_in_response`) that verify the correct
template is used and that expected content appears in the response.
