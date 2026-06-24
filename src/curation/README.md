# `curation`

The `curation` Django app is the core data layer for the service. It defines the domain
models that represent the entities involved in a ClinVar submission: the genomic variant
being classified, the disease it is associated with, the supporting publications, the
curation record itself, and the batches used to group curations for submission. All
models use `django-simple-history` for full audit trails.

### `__init__.py`

Empty file that marks this directory as a Python package.

### `apps.py`

Registers the `curation` app with Django via `CurationConfig`, setting `BigAutoField` as
the default primary key type.

### `models.py`

Defines the five core Django models:

- **`Variant`** — a genomic variant identified by HGVS expression, with an optional
  ClinGen canonical allele ID (`ca_id`), gene symbol, reference sequence, and alternate
  designations.
- **`Disease`** — a disease or condition identified by a typed external ID (e.g.,
  `OMIM:123456`). Uniqueness is enforced on the `(id_type, id_value)` pair.
- **`Publication`** — a supporting publication referenced by PubMed ID or DOI, with
  optional title, authors, and year.
- **`Batch`** — a named group of curations submitted together to ClinVar. Tracks a
  ClinVar `submission_id`, the raw JSON payload sent, and a lifecycle status
  (`Created → Submitted → Processed / Error`).
- **`Curation`** — the central record linking a variant and disease, optionally attached
  to a batch and zero or more publications. Stores the full germline classification,
  mode of inheritance, collection method, allele origin, affected status, the assigned
  SCV, source app metadata, and the raw incoming payload. Has its own lifecycle status
  (`Pending → In Batch → Submitted → Processed / Error`).
