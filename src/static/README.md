# `static`

Vendored static assets served by Django's static-files framework. All assets live under
the `cvss/` namespace to avoid collisions when `collectstatic` merges assets from
multiple apps into `src/public/`.

No build step is required — all JavaScript and CSS files are already bundled/minified by
their upstream projects.

### `cvss/css/bootstrap-icons.css`

CSS stylesheet for the [Bootstrap Icons](https://icons.getbootstrap.com/) icon font.
References the WOFF/WOFF2 font files in `cvss/css/fonts/`.

### `cvss/css/bulma.css`

Full [Bulma](https://bulma.io/) CSS framework. Provides the grid, layout utilities,
components (navbar, card, message, button, etc.), and form styles used throughout the
application.

### `cvss/css/choices.css.map`

Source map for `choices.min.css`. Used by browser developer tools to map minified styles
back to the original source.

### `cvss/css/choices.min.css`

Minified stylesheet for the Choices.js select-enhancement library. Styles the searchable
dropdown widgets used in
`common/templates/common/form/select/search.html`.

### `cvss/css/custom.css`

Project-specific styles that extend or override the Bulma defaults.

- `.entity-type-logo` — constrains logo height inside entity-type selectors.
- `.footer-logo-container` — adds padding around footer logos.
- `.scroll-container` — horizontal scroll wrapper for wide content (e.g., data tables).

### `cvss/css/dataTables.dataTables.min.css`

Minified stylesheet for the [DataTables](https://datatables.net/) jQuery plugin.
Provides base table styling (sort icons, pagination controls).

### `cvss/css/fonts/bootstrap-icons.woff`

Bootstrap Icons icon font in WOFF format. Referenced by `bootstrap-icons.css` for
browsers that do not support WOFF2.

### `cvss/css/fonts/bootstrap-icons.woff2`

Bootstrap Icons icon font in WOFF2 format (preferred; smaller file size than WOFF).

### `cvss/img/clingen-logo-with-text.svg`

SVG logo for the [ClinGen](https://clinicalgenome.org) Clinical Genome Resource.
Displayed in the footer.

### `cvss/img/stanford-medicine-logo.png`

PNG logo for [Stanford Medicine](https://med.stanford.edu). Displayed in the footer
alongside the ClinGen logo to identify institutional affiliation.

### `cvss/img/under-construction.gif`

Placeholder image indicating a page or feature is not yet complete.

### `cvss/js/choices.js`

Unminified source of the Choices.js library.
Kept for reference/debugging; the minified version (`choices.min.js`) is what the
templates load.

### `cvss/js/choices.min.js`

Minified Choices.js library. Enhances `<select>` elements with search, multi-select, and
custom styling. Initialised per-widget in
`common/templates/common/form/select/search.html`.

### `cvss/js/dataTables.bulma.min.js`

Minified DataTables integration plugin for Bulma. Applies Bulma CSS classes to
DataTables-generated markup so pagination and controls match the rest of the UI.

### `cvss/js/dataTables.min.js`

Minified [DataTables](https://datatables.net/) jQuery plugin. Adds client-side sorting,
filtering, and pagination to HTML tables.

### `cvss/js/htmx.js`

[HTMX](https://htmx.org/) library. Enables declarative, attribute-driven AJAX requests
and HTML partial swaps without writing JavaScript. Used throughout the application for
dynamic interactions (form submissions, partial page updates).

### `cvss/js/jquery.min.js`

Minified [jQuery](https://jquery.com/) library. Required by DataTables.
