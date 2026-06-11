# CVSS Design Draft

## Purpose

The ClinVar Submission Service (CVSS) is an intermediary between ClinGen curation
applications and the ClinVar Submission API. It accepts curations from upstream apps,
stores them, and handles the mechanics of batching, submitting, and polling ClinVar on
behalf of ClinGen affiliations, so that each upstream app does not have to solve these
problems independently.

## Affiliations and API Keys

ClinGen is organized into groups called **affiliations**. Each affiliation has its own
ClinVar API key (`SP-API-KEY`). CVSS stores these keys in **AWS Secrets Manager** and
retrieves them at submission time.

Affiliation managers log into CVSS directly. The affiliation identity of a logged-in
user determines which API key is used for their submissions. The affiliation is never
caller-supplied.

## Upstream App Integration

When a curation is approved within an upstream ClinGen application, it is automatically
sent to CVSS as an individual record. Upstream apps speak an internal ClinGen data
model; **CVSS is responsible for translating each curation into ClinVar's JSON schema**
before submission.

The decision to translate within CVSS (rather than requiring upstream apps to produce
ClinVar-formatted JSON) was made because:

- All upstream apps are maintained by the same team as CVSS.
- The upstream apps have meaningfully different data models from each other and from
  ClinVar's schema.
- Centralizing translation means schema changes only need to be addressed in one place.

## Batch Creation and Submission

Curations accumulate in CVSS as they arrive from upstream apps. An **affiliation
manager** logs into the CVSS dashboard, reviews pending curations, and manually creates
and submits batches when ready. There is no automated timer-based submission.

This approach gives affiliations control over their submission cadence and avoids
overburdening ClinVar with small, frequent requests.

## Status Polling

After a batch is submitted to ClinVar, CVSS receives a submission ID (`SUBnnnnnn`).
Because ClinVar's API is pull-based (no webhooks), CVSS polls the ClinVar status
endpoint approximately **once per hour** for all in-flight submissions until they reach
a terminal state (`processed` or `error`). The resulting status is stored locally.

## Status Visibility

Submission status is surfaced in two ways:

1. **Dashboard**: Affiliation managers can see the status of their submissions.
2. **API endpoint**: Upstream apps can query CVSS for the status of a submission if they
   choose to.

Notifications (email, etc.) are out of scope for now.

## Error Handling

- **Transient Errors** (network failures, ClinVar 429/5xx responses): CVSS will
  auto-retry. Retry policy to be defined.
- **Data Errors** (ClinVar rejects records due to schema or content problems): Status is
  surfaced in the dashboard for human review and intervention.
- **Partial Failures**: Records that succeeded within a batch are considered done.
  Failed records are flagged for human review.

## Out of Scope (For Now)

- Notifications on submission success or failure.
- Detailed retry policy.
- Polling interval tuning.
