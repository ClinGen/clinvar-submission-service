# `curation`

The core Django app for the ClinVar submission service. It defines the data models that
represent the lifecycle of a ClinGen curation from receipt to ClinVar submission:
variants, diseases, publications, batches, and curations. Each model tracks full edit
history via `django-simple-history`.

### `__init__.py`

Empty file that marks `curation` as a Python package.

### `apps.py`

Django app configuration. Registers the app under the name `curation` and sets
`BigAutoField` as the default primary key type.

### `fixtures/dummy.json`

Django fixture with sample data for local development and testing. Loads two `Variant`
records, two `Disease` records, two `Publication` records, and two `Curation` records in
`Pending` status. Load with `uv run manage.py loaddata dummy`.

### `models.py`

Defines five models:

- **`Variant`** — a genomic variant identified by HGVS expression, gene symbol,
  reference sequence, and optional ClinGen Allele Registry ID (`car_id`).
- **`Disease`** — a disease identified by a controlled-vocabulary type/value pair (e.g.
  `MONDO:0000001` or `OMIM:123456`).
- **`Publication`** — a supporting publication identified by PubMed ID or DOI, with
  author list and year.
- **`Batch`** — a named group of curations submitted together to ClinVar. Tracks
  submission ID, the raw ClinVar payload, and status
  (`Created → Submitted → Processed / Error`).
- **`Curation`** — the central record linking a variant, disease, and zero or more
  publications. Stores ClinVar-required fields (germline classification, mode of
  inheritance, collection method, allele origin, affected status) plus provenance fields
  (source app, schema version, raw payload). Status flows from
  `Pending → In Batch → Submitted → Processed / Error`; the assigned SCV is written back
  once ClinVar returns it.
