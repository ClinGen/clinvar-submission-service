# `templates`

Project-level Django templates. These templates are not tied to any specific app and are
loaded from `src/templates/` via the `DIRS` setting in `config/settings.py`.
App-specific templates (e.g., `core/`, `common/`) live inside their respective app
directories.

### `400.html`

Rendered when Django raises a `SuspiciousOperation` or another bad-request error.
Displays a Bulma warning message box with a link back to the home page.

### `403.html`

Rendered when a user attempts to access a resource they are not permitted to view (
`PermissionDenied`). Displays a Bulma warning message box with a link back to the home
page.

### `404.html`

Rendered when a requested URL does not match any route. Displays a Bulma warning message
box with a link back to the home page.

### `500.html`

Rendered on unhandled server errors. Displays a Bulma danger message box with the CVSS
support email address and a link back to the home page.

### `layouts/base.html`

The root layout template that all page templates extend. Responsibilities:

- Loads all CSS (Bulma, Bootstrap Icons, Choices.js, DataTables) and JavaScript (HTMX,
  Choices.js, jQuery, DataTables) from the `cvss/` static namespace.
- Sets the `<title>` and `<meta name="description">` via `{% block title %}` and
  `{% block description %}`.
- Injects the CSRF token into HTMX requests via the `hx-headers` attribute on `<html>`.
- Includes the `navbar`, `messages`, and `footer` partials.
- Exposes `{% block main %}` for page content.

### `partials/footer.html`

Site footer. Displays the ClinGen and Stanford Medicine logos (linking to their
respective homesites), a navigation list (About, Contact, Help), copyright notice,
NIH/NHGRI funding attribution, a link to the open-source repository, and the
`{{ GIT_SHA }}` version string injected by `common.context_processors.git_sha`.

### `partials/messages.html`

Renders Django's one-time `messages` framework notifications as styled Bulma message
components. Maps each message level (`debug`, `info`, `success`, `warning`, `error`) to
the appropriate Bulma color modifier and Bootstrap Icon. Each message includes a dismiss
button that removes it from the DOM via an `hx-on-click` handler.

### `partials/navbar.html`

Top navigation bar built with Bulma's navbar component.

### `partials/navbar_link.html`

Helper partial for a single navbar link. Accepts `url` (a named URL) and `text`. Applies
`has-text-weight-bold` when the link's named URL matches the current page
(`request.resolver_match.view_name`), providing active-link highlighting.
