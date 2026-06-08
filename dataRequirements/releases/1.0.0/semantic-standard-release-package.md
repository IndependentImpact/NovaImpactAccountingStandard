# NIAS Semantic Standard Release Package 1.0.0

This document defines the local semantic standard release package for NIAS
1.0.0. It describes the file set that expresses the standard before any Hedera,
IPFS, or Fluree integration.

The machine-readable companion manifest is
`semantic-standard-release-manifest.jsonld`.

## Release Boundary

The release package includes artifacts needed to express and operate the
standard locally:

- ontology and concept schemes;
- canonical SHACL constraints;
- canonical anchor definitions;
- requirement-to-anchor mappings;
- rendering profiles and export configuration;
- shape2flutter workflow and UI adapter inputs;
- reference semantic fixtures and proof artifacts.

The package does not include generated Flutter applications, rendered Markdown,
PDF files, websites, deployed ledger state, Hedera messages, or IPFS-hosted
content. Those are downstream outputs or integration-layer artifacts.

## Source Status

The manifest uses these source-status values:

| Status | Meaning |
| --- | --- |
| `canonical-source` | Normative semantic source of truth for the standard. |
| `operational-profile` | Operational profile or configuration that projects canonical semantics into rendered or exported artifacts. |
| `ui-adapter` | Shape2flutter input that adapts canonical semantics for UI generation. |
| `compatibility-source` | Legacy or transitional source retained for compatibility. |
| `reference-fixture` | Test fixture proving that the standard can operate locally. |
| `documentation` | Human-readable release documentation. |

## Dependency Order

The package dependency order is:

1. Ontology and concept schemes.
2. Concept scheme SHACL shapes.
3. Release-level schema resources.
4. Shared SHACL helper shapes.
5. Document, reference, report, review, and workflow identity shapes.
6. Domain artifact shapes for PDD, Monitoring Report, DLR, and certificates.
7. Artifact anchor shapes.
8. Artifact identity contract shapes for submitted, reviewed, and aligned
   artifacts.
9. VVS requirement SHACL shapes.
10. Anchor definitions.
11. Requirement mappings and proof shapes.
12. Rendering profiles and export configurations.
13. Shape2flutter UI adapter shapes and workflow YAMLs.
14. Reference fixtures and proof fixture data.

This order is for local verification and packaging. It is not a ledger bootstrap
order.

## Local Release Verification Command

Run the full semantic standard release verification suite with:

```bash
dataRequirements/check-semantic-standard-release.sh
```

The script is a single local entry point that runs:

- ontology and concept-scheme parsing/conformance checks;
- canonical SHACL validation suites;
- requirement-to-anchor mapping integrity and traceability checks;
- end-to-end semantic fixture checks;
- report rendering checks, including JSON-LD proof sidecar validation.

Underlying command:

```bash
python3 -m unittest \
  dataRequirements.tests.test_semantic_standard_release_package \
  dataRequirements.tests.test_concept_schemes \
  dataRequirements.tests.test_phase7_validation \
  dataRequirements.tests.test_vvs_requirements \
  dataRequirements.tests.test_requirement_anchor_traceability \
  dataRequirements.tests.test_pdd_output_compilation \
  dataRequirements.tests.test_monitoring_report_rendering \
  dataRequirements.tests.test_validation_verification_report_rendering \
  -q
```

## UI Bundle Contract

Primary shape2flutter workflow files declare a `canonical_bundle` block. This
block is the authoritative local description of the UI bundle:

- `ui_shape_bundle` points to the UI-facing SHACL adapter file consumed by
  shape2flutter.
- `canonical_shape_sources` lists the ontology, concept scheme, canonical SHACL,
  anchor definition, and mapping files that the UI bundle projects.
- `generated_output_status` must be `downstream-generated`, because generated
  Flutter code and emitted form schemas are operational outputs rather than
  normative release sources.

The primary workflow files are:

- `dataRequirements/shape2flutter/workflows/pdd-design.yaml`;
- `dataRequirements/shape2flutter/workflows/validation-report.yaml`;
- `dataRequirements/shape2flutter/workflows/monitoring-report.yaml`;
- `dataRequirements/shape2flutter/workflows/verification-report.yaml`.

## Manifest Contract

Each release artifact in the JSON-LD manifest must declare:

- stable artifact IRI;
- human-readable title;
- relative repository path;
- artifact role;
- source status;
- parse format;
- dependency order.

For later IPFS/Hedera integration, the manifest also reserves room for schema
CID and content CID values. In this local package those identifiers may remain
absent or be simulated in fixtures.
