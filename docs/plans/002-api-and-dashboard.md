# Plan for the Inbound API and Classification Dashboard

## The Problem

ClinGen curators use the Variant Curation Interface (VCI) to classify genetic variants.
When a classification is approved, it needs to be submitted to ClinVar, NCBI's public
archive of variant interpretations. Today, ClinGen handles this by preparing and
uploading spreadsheets. The ClinVar Submission Service (CVSS) replaces this workflow by
providing an API that VCI can push approved classifications to directly. Once
classifications are in CVSS, a submitter can review them, group them into a batch, and
submit the batch to ClinVar.

## The Technical Plan

```
  +---------+   POST /api/v1/classification/create    +------------------+
  |   VCI   | --------------------------------------> |   CVSS REST API  |
  +---------+               (API key auth)            +------------------+
                                                              |
                                                         [Database]
                                                              |
                                                    +------------------+
                                                    | Dashboard        |
                                                    | (classification  |
                                                    |  list)           |
                                                    +------------------+
```

There are two components in scope for this plan: the inbound API and the classification
list view.

**Inbound API:** When a curator submits an approved classification to the CVSS, the VCI
sends a single POST request to CVSS containing everything about that classification —
the variant, the disease, any supporting publications, and the classification details.
The CVSS authenticates the request using an API key issued to VCI, stores the data in
its database, and returns a confirmation. If VCI later needs to correct a
classification, it can send a PUT request to replace it.

**Classification list view:** Once classifications are in the CVSS, logged-in submitters
can view them in a simple table in the CVSS dashboard. The table shows the key fields —
variant, disease, classification, affiliation, status, and when the classification was
received — and supports sorting and filtering so submitters can find what they're
looking for. This view is read-only; batch creation and submission to ClinVar are
handled separately and are out of scope for this plan.

## Alternatives

**Translation in CVSS vs. translation in VCI.** The original design called for CVSS to
own translation: VCI would send its native payload and CVSS would convert it into
ClinVar fields. This keeps upstream apps ignorant of ClinVar's schema and centralizes
any fixes when ClinVar's schema changes. We decided against it for now because it adds a
translation layer before the API is even working. VCI will produce ClinVar fields
directly, and a translation layer can be added later if needed. The `raw_payload`,
`source_app`, and `schema_version` fields are kept on the `Classification` model as an
escape hatch should re-translation ever become necessary.

**PATCH vs. PUT for updates.** A PATCH endpoint would let VCI send only the fields that
changed, which is a smaller payload and a more idiomatic REST design for partial
updates. We chose PUT (full replacement) to avoid the complexity of partial-state merges
— if a field is omitted from a PATCH, it's ambiguous whether it should be cleared or
left alone. A full replacement is unambiguous.

**Storing affiliation vs. validating and discarding it.** One option was to validate the
affiliation in the payload against the Affiliations Service cache at receipt time, then
discard it. We rejected this because the dashboard needs to filter classifications by
affiliation, which requires the value to be persisted on the `Classification` record.

**Separate API endpoints for variant, disease, and publication.** Rather than a single
nested POST, VCI could manage related records through separate endpoints — creating a
variant first, then a disease, then referencing their CVSS IDs in the classification
payload. This would be more RESTful but would require VCI to manage CVSS-internal IDs
and make multiple requests per classification. A single nested payload is simpler for
VCI and keeps the integration surface small.

**Distinct `local_id` and `linking_id` values.** ClinVar's submission schema uses these
two identifiers for different structural purposes. We considered generating distinct
UUIDs for each field, but the distinction isn't fully understood yet and VCI currently
sends the same value for both (as shown in the original spreadsheet data). We'll use the
same UUID for both until ClinVar's behavior during submission clarifies whether they
need to differ.

## Detailed Implementation

### Step 1 — `src/classification/models.py` (changed)

Add `affiliation = models.CharField(max_length=100)` to the `Classification` model. This
field stores the affiliation identifier asserted by the upstream app and is required for
dashboard filtering. No other model changes are needed.

### Step 2 — Migration (created, auto-generated)

Run `uv run manage.py makemigrations classification` to generate a migration that adds
the `affiliation` column to the `classification_classification` table. The exact
filename will be assigned by Django (e.g., `0002_classification_affiliation.py`).

### Step 3 — `src/classification/serializers.py` (created)

New file. Defines four DRF serializers:

- **`VariantSerializer`** — fields: `car_id`, `gene_symbol`, `reference_sequence`,
  `hgvs`, `alternate_designations`. Used only as a nested serializer; not exposed as a
  standalone endpoint.
- **`DiseaseSerializer`** — fields: `id_type`, `id_value`.
- **`PublicationSerializer`** — fields: `pubmed_id`, `doi`, `title`, `authors`,
  `publication_year`.
- **`ClassificationSerializer`** — top-level serializer. Nests the three serializers
  above. Includes all `Classification` fields: `affiliation`, `source_app`,
  `schema_version`, `raw_payload`, `local_id`, `linking_id`, `germline_classification`,
  `mode_of_inheritance`, `date_last_evaluated`, `comment_on_classification`,
  `collection_method`, `allele_origin`, `affected_status`.

`ClassificationSerializer.create()` contains the upsert logic for related records:

- `Variant` — looked up by `car_id` if present; otherwise by `hgvs` +
  `reference_sequence`
- `Disease` — looked up by `id_type` + `id_value`
- `Publication` — looked up by `pubmed_id` if present; otherwise by `doi`

Variant and Publication are upserted with `update_or_create` (their non-key fields may
change). Disease is fetched with `get_or_create` (its two fields are both the key; there
is nothing to update). Publications are linked to the classification via `.set()` after
the classification record is created. Classification status is set to pending on
creation and is not accepted from the caller.

`ClassificationSerializer.update()` replaces all classification fields and re-runs the
same upsert logic for related records, then calls `publications.set()` to replace the
M2M links.

### Step 4 — `src/api/views.py` (changed)

Defines two DRF API views. Both use the `HasAPIKey` permission class (already the global
default in `REST_FRAMEWORK` settings; stated explicitly per-view for clarity).

- **`ClassificationCreateView(APIView)`** — handles
  `POST /api/v1/classification/create`. Deserializes the request body with
  `ClassificationSerializer`. If a `Classification` with the given `local_id` already
  exists, returns 409. Otherwise, calls `serializer.save()` and returns 201 with
  `{"local_id": "...", "status": "pending"}`.
- **`ClassificationUpdateView(APIView)`** — handles
  `PUT /api/v1/classification/<local_id>/update`. Looks up the classification by
  `local_id`; returns 404 if not found. If `status` is anything other than pending,
  returns 409 with
  `{"detail": "Classification cannot be updated in status '<status>'."}`. Otherwise,
  deserializes the request body, calls `serializer.save()`, and returns 200 with
  `{"local_id": "...", "status": "pending"}`.

### Step 5 — `src/api/urls.py` (changed)

Add two URL patterns pointing to the new views in `api.views`:

```
POST  v1/classification/create                   → ClassificationCreateView
PUT   v1/classification/<uuid:local_id>/update   → ClassificationUpdateView
```

This file already exists and is mounted at `/api/` in `config/urls.py`, so no changes to
`config/urls.py` are needed for the API routes.

### Step 6 — `src/classification/views.py` (created)

New file. Defines a single built-in class-based generic views, `ClassificationList`,
that queries
`Classification.objects.select_related("variant", "disease").order_by("-added_at")` and
renders `classification/list.html`. Requires login.

### Step 7 — `src/classification/urls.py` (created)

New file. Defines one URL pattern: `GET /classification/list` → `ClassificationList`,
named `"classification-list"`.

### Step 8 — `src/config/urls.py` (changed)

Include `classification.urls` at the root so that `/classification/list` resolves to the
classification list view. The API routes are already handled by `api.urls`.

### Step 9 — `src/classification/templates/classification/list.html` (created)

New file. Extends `layouts/base.html`. Renders a `<table>` initialised with DataTables
(already vendored) for client-side sorting and filtering. Columns:

- Local ID — `classification.local_id`
- Variant — `classification.variant.hgvs`
- Disease — `classification.disease` (renders as `id_type:id_value` via `__str__`)
- Classification — `classification.germline_classification`
- Affiliation — `classification.affiliation`
- Status — `classification.get_status_display()`
- Received — `classification.added_at`

### Step 10 — `src/templates/partials/navbar.html` (changed)

Add a "Classifications" link using the `navbar_link.html` partial, pointing to the
`classification-list` named URL. This gives submitters a direct path to the
classification list from the top navigation.

### Step 11 — `src/api/tests.py` (changed)

Add tests for the two API endpoints. Each test case uses an API key created in `setUp`.

Tests for `POST /api/v1/classification/create`:

- Returns 201 and `{"local_id": "...", "status": "pending"}` for a valid payload.
- Creates the expected `Classification`, `Variant`, `Disease`, and `Publication` records
  in the database.
- Reuses an existing `Variant` record when a classification with the same `car_id` is
  posted again.
- Reuses an existing `Disease` record when a classification with the same `id_type` +
  `id_value` is posted again.
- Returns 409 when a classification with the same `local_id` already exists.
- Returns 403 when no API key is provided.
- Returns 400 for a payload missing required fields.

Tests for `PUT /api/v1/classification/<local_id>/update`:

- Returns 200 and updates the classification record for a valid payload on a pending
  classification.
- Returns 404 when the `local_id` does not exist.
- Returns 409 when the classification status is in batch.
- Returns 409 when the classification status is submitted.
- Returns 403 when no API key is provided.

### Step 12 — `src/classification/tests.py` (created)

New file. Add tests for the `ClassificationList` view.

- Returns 200 and renders `classification/list.html` for a logged-in user.
- Redirects to the login page for an unauthenticated request.
- Classifications appear in the response.
