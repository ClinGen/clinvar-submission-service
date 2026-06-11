# CVSS Design Doc

## Context and Scope

ClinGen organizes groups of curators into **affiliations**. Curators use the **Variant
Curation Interface (VCI)** to classify genetic variants. When a classification is
approved, it is eligible for submission to
[ClinVar](https://www.ncbi.nlm.nih.gov/clinvar/), NCBI's public archive of variant
interpretations.

Currently, ClinGen submits to ClinVar by uploading spreadsheets. This process is not as
streamlined as we'd like it to be.

The **ClinVar Submission Service (CVSS)** replaces this workflow. It accepts curations
from upstream ClinGen apps, stores them, translates them into ClinVar's JSON schema, and
handles batching, submission, and status polling on behalf of each affiliation.

The initial upstream app is **VCI v3**. A rewritten version, **VCI v4**, will integrate
with CVSS as a second upstream app once it is ready. Future ClinGen apps may also
integrate.

CVSS depends on the **Affiliations Service (AS)**, a separate, team-owned service that
maps users to affiliations and permissions. CVSS caches this data with a 24-hour TTL.

Human users of CVSS are **submitters**, curators with elevated permissions who are
authorized to submit on behalf of their affiliation. CVSS will share a single sign-on
(SSO) system with the VCI once that rollout is complete; until then, logins are
separate.

CVSS will be rolled out incrementally, affiliation by affiliation, as a replacement for
the spreadsheet workflow. An affiliation will use one system or the other at any given
time, never both simultaneously.

## Goals and Non-Goals

**Goals**

- Accept curations pushed from upstream ClinGen apps via a REST API.
- Translate curations from each upstream app's native format into ClinVar's JSON schema.
- Allow submitters to review pending curations, and manually create and submit batches.
- Poll ClinVar for submission status and surface results in a dashboard and a queryable
  API endpoint.
- Replace the existing spreadsheet-based submission workflow.

**Non-Goals**

- **Automated submission without human approval.** Affiliations have different
  submission cadences; some wait months between submissions. CVSS will not impose a
  schedule.
- **Submitting to repositories other than ClinVar.** CVSS is purpose-built for ClinVar.
- **Requiring upstream apps to produce ClinVar-format JSON.** CVSS owns translation so
  that upstream apps do not need to understand ClinVar's schema.

**Deferred**

The following are planned but out of scope for the initial release:

- Email or other notifications on submission events.
- Specific retry policy parameters (the retry mechanism is designed; parameters are
  TBD).
- Polling interval tuning (hourly is the working default; the value will be finalized
  later).

## Design

### System Context

```
  +-----------------+        +----------------------+
  |   VCI v3 / v4   |--POST->|                      |------> ClinVar Submission API
  +-----------------+        |        CVSS          |                                                           
                             |                      |<----- ClinVar Status API (polling)
  +-----------------+        +----------------------+                                                           
  | Affiliations    |<------------------------------
  | Service         |     (cached, 24-hour TTL)                                                                   
  +-----------------+
```

### Upstream Integration

When a curation is approved in an upstream app, that app POSTs it to the CVSS REST API
(built with Django REST Framework). CVSS does not poll upstream apps.

Each upstream app authenticates with a **service-level API key** issued by CVSS. The
affiliation the curation belongs to is asserted in the payload and validated against the
cached AS data. Because only trusted, authenticated upstream servers can call this
endpoint, the affiliation field is not considered caller-supplied in the untrusted
sense.

### Translation

CVSS contains one **translator** per upstream app (e.g., a VCI v3 translator, a VCI v4
translator). Each translator converts the upstream app's native curation format into
ClinVar's JSON schema. When a new upstream app integrates with CVSS, a new translator is
added to the CVSS codebase.

### Batch Creation and Submission

Curations accumulate in CVSS as they arrive. An affiliation manager logs into the CVSS
dashboard, reviews pending curations for their affiliation, and manually creates a batch
when ready. Batches are submitted to ClinVar using the affiliation's `SP-API-KEY`, which
is stored in **AWS Secrets Manager** and retrieved at submission time.

### Status Polling

ClinVar's API is pull-based (no webhooks). After a batch is submitted, CVSS receives a
submission ID (`SUBnnnnnn`). A scheduled job polls the ClinVar status endpoint
approximately once per hour for all in-flight submissions until they reach a terminal
state (`processed` or `error`). Status is stored locally and surfaced in the dashboard
and via API.

### Data Storage

**Curation records**

Each incoming curation is stored in two forms:

- The **raw pre-translated payload** as a JSON blob, alongside `source_app` (e.g.,
  `"vci_v3"`) and `schema_version` fields. This preserves the original data and provides
  the information needed to re-translate if the translator logic changes.
- The **translated ClinVar-format fields** in a relational table, used for dashboard
  queries and batch assembly.

Curation lifecycle: `pending` → `in_batch` → `submitted` → `processed` / `error`.

**Batch records**

A batch is a many-to-one grouping of curations (a curation belongs to at most one batch
at a time). The assembled ClinVar submission payload is stored as a JSON blob alongside
the batch record. If a curation in a batch fails, it returns to `pending` and can be
included in a future batch.

**Audit trail**

All model changes are tracked using `django-simple-history`.

### Error Handling

- **Transient errors** (network failures, ClinVar 429/5xx): CVSS will auto-retry. Retry
  parameters are TBD.
- **Data errors** (ClinVar rejects records due to schema or content problems): status is
  surfaced in the dashboard for human review.
- **Partial failures**: records that succeeded within a batch are considered done.
  Failed records return to `pending` for re-batching.

## Alternatives Considered

**Manual vs. automated batch submission**

Automated, timer-based submission was considered and rejected. Affiliations have
meaningfully different submission cadences — some submit weekly, others wait months. An
automated schedule would impose unwanted behavior on affiliations and remove the human
review step before submission. Manual submission is the correct model, not a temporary
limitation.

**Polling vs. webhooks**

Polling is not a design choice; it is a constraint. ClinVar's API does not support
webhooks. If ClinVar adds webhook support in the future, CVSS should adopt it in place
of the polling job.

**Centralized translation (in CVSS) vs. distributed translation (in each upstream app)**

An alternative design would require each upstream app to produce ClinVar-format JSON
before sending curations to CVSS. This was rejected because:

- All upstream apps and CVSS are maintained by the same small team.
- Centralizing translation means ClinVar schema changes require a fix in one place.
- It lowers the integration cost for upstream apps, which do not need to understand
  ClinVar's schema.

The accepted trade-off is that CVSS is coupled to the internal data models of its
upstream apps. This is acceptable given the team structure, the infrequency of data
model changes, and the low volume of data.

**Per-affiliation API keys vs. service-level API keys for upstream apps**

Issuing one API key per affiliation-app pair would have prevented any upstream app from
asserting a false affiliation. However, with many affiliations and multiple upstream
apps, this approach scales poorly. Provisioning, rotation, and revocation would become a
significant operational burden. A service-level API key per upstream app (with
affiliation validated against the AS) achieves equivalent security with far less
overhead.

## Cross-Cutting Concerns

### Security

- **ClinVar API keys** are stored in AWS Secrets Manager and retrieved at submission
  time. They are never stored in the application database or configuration files.
- **Upstream app authentication** uses service-level API keys issued by CVSS, one per
  upstream app.
- **Affiliation manager authentication** uses Django's auth system, transitioning to
  organization-wide SSO. Until SSO is in place, CVSS and VCI logins are independent.
- **AS cache**: affiliation and permission data is cached with a 24-hour TTL. This means
  there is an up-to-24-hour window during which a user whose permissions were revoked
  could still act. This window is an accepted trade-off for an internal tool that does
  not process PHI.

### Privacy

CVSS does not store or transmit protected health information (PHI). All curation data is
scientific and aggregate in nature. HIPAA compliance is out of scope.

### Observability

Application logs are written to a rotating log file in production (configured in
`config/settings/prod.py`). There is no automated alerting in the initial release.
submitters are expected to notice stale submission statuses via the dashboard. Alerting
and monitoring tooling is a candidate for a future iteration.
