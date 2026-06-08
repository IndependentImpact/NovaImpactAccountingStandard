# Data requirements

This directory contains the canonical data-validation and workflow requirements
for the Nova Impact Accounting Standard.

## What is here

- `*.ttl` SHACL shape files that define the required structure for NIAS
  artefacts such as project design documents, reports, certificates, reviews,
  anchors, and linked identities.
- `tests/` with Python validation and regression tests for the semantic
  standard, mappings, rendering, and workflow gates.
- `mappings/`, `fixtures/`, and `releases/` with supporting proof data, release
  packaging, and requirement traceability assets.
- `document-rendering/`, `shape2flutter/`, `fluree/`, and `adapters/` with
  downstream operational projections of the canonical model.

## When to work here

- Edit this directory when you are changing canonical NIAS constraints or
  release-packaged semantic assets.
- Start with the nested READMEs before changing operational projections:
  - [`document-rendering/`](document-rendering/README.md)
  - [`shape2flutter/`](shape2flutter/README.md)
  - [`fluree/`](fluree/README.md)
  - [`adapters/`](adapters/README.md)

## Verification

Run the local semantic standard verification entry point from the repository
root:

```bash
dataRequirements/check-semantic-standard-release.sh
```

For the broader unittest suite used in this repository:

```bash
python -m unittest discover -s dataRequirements/tests -p 'test_*.py'
```
