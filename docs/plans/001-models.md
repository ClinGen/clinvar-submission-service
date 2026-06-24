# Plan for Creating Models

This document works through the design of Django models for ClinVar submission data. It
has three sections: the proposed VCI submission fields (taken from Christine's
slideshow), a decisions and questions section capturing design choices made and open
questions to follow up on, and a models section summarizing the agreed-upon model
structure.

## Proposed fields for ClinVar API submission

The following information is taken from one of Christine's slideshows. The format is:

```
**<data summary>**                                                                                       
- <VCI spreadsheet field name>: <example data>                                                                
- <VCI spreadsheet field name>: <example data> 
```

**Keys**

- Local ID: `91d8a5fd-ca4f-426d-9b06-68e7858e7d7e`
- Linking ID: `91d8a5fd-ca4f-426d-9b06-68e7858e7d7e`

**Classification**

- Germline classification: Likely Pathogenic

**Mode of inheritance**

- Mode of inheritance: Autosomal recessive inheritance

**Disease information**

- Condition ID type: MONDO
- Condition ID: MONDO:0019497

**Date**

- Date last evaluated: 2024-06-28

**Summary eval**

- Comment on classification: "The c.1849T>C variant in MYOA is a missense variant
  predicted to cause substitution of serine by proline at amino acid 617 (p.Ser617Pro).
  The highest population minor allele frequency in gnomAD v4 is 0.00009496 (8/84244
  alleles) in the South Asian population (PM2_Supporting, BS1, and BA1 are not met). The
  computational predictor REVEL gives a score of 0.922, which is above the threshold of
  0.7, evidence that correlates with impact to MYOTA function (PP3). This variant has
  been detected in 3 individuals with nonsyndromic hearing loss. Of those individuals, 2
  were compound heterozygous for the variant and a pathogenic or likely pathogenic
  variant and both of those were..."

**Variant ID**

- Gene symbol: MYOTA
- Reference sequence: NC_000011.10
- HGVS: g.77172799T>C
- Alternate designations: NM_000260.4(MYO7A):c. 1849T>C|p.Ser617Pro

**ERepo link**

- Citations or URLs for classification without database identifiers:
  https://erepo.clinicalgenome.org/evrepo/ui/interpretation/91d8a5fd-ca4f-426d-9b06-68e7858e7d7e

**Test details**

- Collection method: curation
- Allele origin: germline
- Affected status: unknown

**PMIDs**

- N/A: ""

**ClinVar Details**

- ClinVarAccession: Manually added right now.
- Novel or Update: Manually added right now.

**Assertion Criteria**

- N/A: Manually added right now. Is a PDF uploaded to ClinVar designating the methods
  used to classify.

## Decisions and questions

**Question — Keys** In the example, Local ID and Linking ID are the same UUID. Are they
always the same? If they can differ, what is the distinction? *(Ask Christine.)*

**Decision — Variant ID** Variant should be its own model, with curations pointing to it
via a foreign key.

**Question — Variant ID** ClinGen CA IDs should be used as the stable, unique identifier
for a variant. Does VCI include the CA ID in the payload it sends to CVSS, or does CVSS
need to look it up from the ClinGen Allele Registry? *(Needs investigation.)*

**Question — ERepo link** The example URL contains the same UUID as the Local ID,
suggesting it is always derivable. Leaning towards not storing it as a separate field.
*(Confirm with Christine.)*

**Decision — Publication model** PMIDs should live in a separate `Publication` model
with a many-to-many relationship to curations. The fields will be: `pubmed_id`, `doi`,
`title`, `authors` `added_at`, `updated_at`, and `history` (django-simple-history).

**Decision — ClinVar Accession (SCV)** SCVs are assigned per curation, not per batch.
After a batch is processed, each curation receives its own SCV from ClinVar, which is
stored on the curation record. This is also what makes "Novel or Update" derivable.

**Decision — Novel or Update** "Novel or Update" is derivable from whether a ClinVar
accession (SCV) already exists for the curation. CVSS should determine this
automatically rather than storing it as a field.

**Question — Assertion Criteria** Is Assertion Criteria configured once per affiliation,
or does it vary per curation? If per affiliation, it doesn't belong on the curation
record. *(Needs investigation.)*

**Decision — Disease information** Disease should be its own model. VCI uses MONDO
almost exclusively, but to avoid a sparse table and future schema migrations, the model
should use two fields — `id_type` (e.g. `"MONDO"`) and `id_value` (e.g.
`"MONDO:0019497"`) — rather than separate per-ontology ID fields. The unique constraint
is on `id_type` + `id_value`. Curations point to a Disease via a foreign key.

## Models

**`Variant`**

- CA ID (stable unique identifier from the ClinGen Allele Registry; open question on
  whether VCI provides this or CVSS must look it up)
- Gene symbol
- Reference sequence
- HGVS
- Alternate designations

**`Disease`**

- `id_type` (e.g. `"MONDO"`)
- `id_value` (e.g. `"MONDO:0019497"`)
- Unique constraint on `id_type` + `id_value`

**`Publication`**

- `pubmed_id`
- `doi`
- `title`
- `authors` (JSON array of author names)
- `publication_year`
- `added_at`, `updated_at`
- `history` (django-simple-history)

**`Curation`**

- FK to `Variant`
- FK to `Disease`
- M2M to `Publication`
- nullable FK to `Batch`
- Local ID, Linking ID (open question on distinction)
- Germline classification
- Mode of inheritance
- Date last evaluated
- Comment on classification
- Collection method, allele origin, affected status
- ClinVar accession (SCV) — populated after first successful submission
- Status (`pending` → `in_batch` → `submitted` → `processed` / `error`)

**`Batch`**

- User-defined name (optional)
- ClinVar submission ID (`SUBnnnnnn`) — populated after batch is posted to ClinVar
- Assembled submission payload (JSON blob)
- Status
