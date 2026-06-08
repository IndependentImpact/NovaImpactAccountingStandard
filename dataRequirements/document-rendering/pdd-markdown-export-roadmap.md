# PDD Markdown Export Design And Roadmap

## Purpose

This document specifies how NIAS PDD workflow data should be projected into a
single human-readable Project Design Document (PDD) in Markdown, with later
compilation to PDF or a website.

The export is a document-rendering projection of the semantic standard. It does
not create a second data model and does not add independent data requirements.
The canonical data requirements remain the SHACL shapes in `dataRequirements/`.

## Location

This document lives in `dataRequirements/document-rendering/` because PDD
Markdown/PDF/website generation is not specific to `shape2flutter`, Fluree,
IPFS, Hedera, or any single UI. It consumes the semantic standard, a rendering
profile, and filled-in PDD data.

Related implementation inputs are currently:

- `dataRequirements/report-shapes.ttl`
- `dataRequirements/project-design-shapes.ttl`
- `dataRequirements/impact-declaration-shapes.ttl`
- `dataRequirements/stakeholder-engagement-shapes.ttl`
- `dataRequirements/pdd-certificate-shapes.ttl`
- `dataRequirements/review-shapes.ttl`
- `dataRequirements/document-shapes.ttl`
- `dataRequirements/common-shapes.ttl`
- `dataRequirements/shape2flutter/pdd-workflow-ui-shapes.ttl`
- `dataRequirements/fixtures/pdd-workflow/*.ttl`
- `dataRequirements/shape2flutter/pdd_workflow_shell/`
- `dataRequirements/document-rendering/pdd-markdown-export-phase1-assessment.md`

## Conceptual Model

The PDD export has three layers:

1. SHACL
   - Defines the canonical data contract.
   - Specifies field paths, cardinality, datatypes, nested structures, and
     controlled value sets.
   - Remains the authority for whether a PDD payload is complete and valid.

2. Rendering Profile
   - Defines how canonical content is presented as a document.
   - Specifies document title, heading order, heading levels, labels, table/list
     formatting, standard boilerplate, draft/final behavior, and version
     metadata.
   - Must not define new required fields or conflict with SHACL.

3. Filled-In Data
   - Contains the project-specific RDF/JSON-LD payload produced by the PDD
     workflow.
   - Is rendered through the profile into Markdown after validation or in an
     explicitly marked draft mode.

The projection rules are:

- `SHACL + rendering profile` produces a blank Markdown PDD template.
- `SHACL + rendering profile + filled-in data` produces a complete Markdown PDD.
- Markdown can then be compiled to PDF, HTML, or a static website.

## Design Principles

- Canonical predicates and SHACL shapes remain the source of truth.
- The rendering profile is presentation metadata, not a data model.
- Exported documents must be deterministic for the same inputs.
- Draft output must be visibly marked as draft.
- Final output must include the standard version, document schema version,
  rendering profile version, renderer version, source artifact identifiers, and
  generation timestamp.
- Human-readable labels should be used where available, while canonical IRIs
  remain available in metadata or footnotes when needed.
- The main PDD body should contain project design content only. Document wrapper
  metadata and workflow/process evidence belong in a back-matter metadata
  appendix and sidecar files, with only a short document ID, hash, or version
  reference in the footer.
- Missing required data must not be hidden. Draft exports may show placeholders;
  final exports must require successful validation.
- The renderer should support Markdown first. PDF and website output should be
  compilation targets of Markdown, not separate hand-authored renderers.

## Resolved Design Decisions

### Rendering Profile Format

The PDD rendering profile should be a Markdown document with YAML front matter.
This is the most natural format for human-maintained document templates and for
Pandoc-based PDF, HTML, and website generation.

The Markdown body should define the human-readable document structure. The YAML
front matter should define profile metadata and rendering options.

Example:

```markdown
---
profile: nias-pdd-rendering-profile
profileVersion: 0.1.0
standard: NIAS
documentType: Project Design Document
defaultOutputTargets:
  - markdown
  - pdf
  - html
---

# {{ project.title }}

{{ render: keyProjectInformation }}

## Section A. Description Of Project

{{ render: pdd.sectionA }}

## Section B. Impact Claims And Monitoring

{{ render: pdd.sectionB }}

## Section C. Stakeholder Engagement

{{ render: pdd.sectionC }}

## Appendix A. Document Metadata

{{ render: metadataAppendix }}
```

The render directives are profile instructions. They must resolve only to
canonical SHACL-backed data paths or to standard rendering metadata.

### Renderer Input

The primary renderer input should be JSON-LD payloads from the PDD workflow
shell. JSON-LD is the natural exchange boundary because the workflow shell
already works with JSON-like maps and JSON-LD preserves canonical semantic
predicates.

Internally, the renderer should normalize input to an RDF/JSON-LD graph model
before rendering. This keeps the renderer compatible with future Turtle,
N-Quads, Fluree export, or other graph inputs without changing the document
profile.

The interface policy is:

- primary local input: JSON-LD from the workflow shell;
- internal model: canonical expanded JSON-LD or RDF graph;
- future-compatible inputs: Turtle, N-Quads, and Fluree ledger exports.

### PDF Compiler

Pandoc should be the default Markdown compiler for PDF and HTML output. Pandoc
supports YAML front matter, document templates, headers, footers, PDF output,
HTML output, and future DOCX export if needed.

### Title Page And Front Matter

The visible title page and key project information section should contain
human-facing fields, following the pattern used by conventional PDD templates:

- project ID;
- PDD version number;
- completion or publication date;
- project developer;
- project representative;
- project participants and involved communities;
- host country or countries;
- activity type or requirements applied;
- methodology and methodology version;
- product or impact claim type;
- project cycle or status.

YAML front matter should hold machine-facing provenance and rendering metadata:

- standard version;
- document schema IRI;
- rendering profile version;
- renderer version;
- generated timestamp;
- validation status;
- source workflow message IDs;
- source IPFS URIs where available;
- source data hash;
- output document hash where available;
- canonical context and graph identifiers.

The title and subtitle already identify the standard, document type, and project
title, so those values should not be repeated as rows in the key-information
table.

### Repeated Impact And Parameter Sections

Large repeated impact, data, and monitoring parameter sections should remain
under the same subsection. Each parameter should render as its own table, one
below the other.

Example:

```markdown
### Data And Parameters To Be Monitored

#### Parameter: Electricity generated

| Field | Value |
| --- | --- |
| Unit | kWh |
| Source of data | Meter records |
| Monitoring frequency | Monthly |
| QA/QC procedures | Monthly reconciliation against meter logs |

#### Parameter: Operating hours

| Field | Value |
| --- | --- |
| Unit | hours |
| Source of data | Controller logs |
| Monitoring frequency | Monthly |
| QA/QC procedures | Automated log validation |
```

### Metadata, Predicate IRIs, And Hashes

Final rendered PDDs should keep the human document readable. Canonical predicate
IRIs should not be injected as footnotes throughout the main body by default.

Instead:

- include a short document ID, source hash, or version reference in the PDF
  footer;
- include a full metadata appendix at the end of the Markdown/PDF;
- emit a machine-readable sidecar file alongside the human-readable outputs.

The main body, from Section A through Section C, should not render document or
workflow wrapper fields such as document IPFS URI, document schema IRI,
encryption status, document author, authenticity proof, workflow submission
evidence, validation review evidence, or PDD-CIR evidence. Those fields are
process and provenance records, so they belong in the metadata appendix or
machine-readable sidecars.

The appendix should include:

- document metadata;
- workflow submission and process metadata;
- rendering metadata;
- validation report summary;
- source artifact references;
- IPFS and Hedera references where available;
- field-to-predicate mapping;
- concept scheme versions;
- hash and signature details.

The expected output set for a final export is:

```text
pdd.md
pdd.pdf
pdd.html
pdd.metadata.jsonld
pdd.validation.json
```

## Rendering Profile Scope

The rendering profile should define:

- PDD document title pattern.
- Front matter fields.
- Standard boilerplate and format/version statement.
- Top-level section order.
- Field label overrides where SHACL/UI labels are not publication quality.
- Heading depth rules.
- Whether repeated nested structures render as repeated subsections, tables, or
  bullet lists.
- How optional missing values render in draft mode.
- How concept IRIs are converted to labels.
- How IPFS URIs, Hedera message IDs, document references, and account IDs render.
- Appendix and references rules.
- Output target options for Markdown, PDF, and website.

The rendering profile should not define:

- new required fields;
- validation rules that conflict with SHACL;
- project-specific values;
- workflow approval rules;
- storage or platform integration behavior.

## Proposed File Layout

Implementation should use a layout similar to:

```text
dataRequirements/document-rendering/
  pdd-markdown-export-roadmap.md
  pdd-rendering-profile.md
  templates/
    pdd-boilerplate.md
  fixtures/
    pdd-alpha-input.jsonld
    pdd-alpha-template.md
    pdd-alpha-rendered.md
  tool/
    render_pdd_markdown.py
    compile_pdd_pdf.sh
  tests/
    test_pdd_markdown_rendering.py
```

The exact implementation language can change, but the renderer should be easy to
run locally and easy to add to regression checks.

## Implementation Phases

### Phase 1: Confirm Document Rendering Boundary

Status: completed on 2026-05-25.

Tasks:

- Confirmed that Markdown/PDF/website export is a document-rendering projection,
  not a SHACL extension and not a Flutter-only feature.
- Confirmed that `dataRequirements/document-rendering/` is the correct home.
- Identified the PDD source shapes that define PDD-A, PDD-B, PDD-C, reviews, and
  PDD-CIR references.
- Recorded fields that are required for human document rendering but are not
  yet explicit in the semantic model.
- Added the Phase 1 assessment in
  `dataRequirements/document-rendering/pdd-markdown-export-phase1-assessment.md`.

End-of-phase criteria:

- A reviewed design document exists in `dataRequirements/document-rendering/`.
- The three-layer model is documented.
- No new data requirements have been introduced in the rendering layer.
- Open questions are listed explicitly.
- The assessment confirms there is no standalone `dataRequirements/pdd-shapes.ttl`;
  PDD rendering source shapes are split across report, project design, impact
  declaration, stakeholder engagement, review, certificate, document, and common
  shape files.

### Phase 2: Define The PDD Rendering Profile

Status: completed on 2026-05-25.

Tasks:

- Created `pdd-rendering-profile.md` with YAML front matter.
- Defined PDD title, front matter, standard/version statement, section order, and
  heading-depth rules.
- Mapped each top-level PDD workflow section to publication headings.
- Defined default rendering behavior for scalars, nested objects, repeated
  objects, controlled vocabularies, document references, and links.
- Defined draft and final rendering modes.
- Defined footer metadata rules, metadata appendix rules, and sidecar output
  rules.
- Added `dataRequirements/tests/test_pdd_rendering_profile.py` to prove the
  profile parses and stays presentation-only.

End-of-phase criteria:

- The profile front matter parses successfully.
- Every PDD workflow section has a rendering entry.
- Every top-level PDD-A/B/C content shape has a deterministic heading location.
- The profile contains only rendering metadata and no independent validation
  constraints.
- A short human review of the blank structure confirms it resembles a
  conventional PDD document.

### Phase 3: Generate A Blank Markdown Template

Status: completed on 2026-05-25.

Tasks:

- Added `tooling/document-rendering/render_pdd_markdown.py` as a
  local command that projects `SHACL + rendering profile` into a blank PDD
  Markdown template.
- Added deterministic placeholder rendering using SHACL/UI labels and
  rendering-profile heading overrides from `{{ render: ... }}` directives.
- Added visible required/optional markers in template mode based on
  `sh:minCount`.
- Added `dataRequirements/document-rendering/fixtures/pdd-blank-template.md` as
  the golden blank template fixture.
- Added `dataRequirements/tests/test_pdd_blank_template.py` to validate command
  output and protect against template drift.

End-of-phase criteria:

- A local command produces a deterministic blank Markdown PDD template.
- The generated template includes PDD-A, PDD-B, and PDD-C.
- Required fields appear in the template.
- Nested structures render at the expected heading depth.
- A golden test proves the generated template has not drifted unexpectedly.

### Phase 4: Render Filled-In PDD Data To Markdown

Status: completed on 2026-05-25.

Tasks:

- Implement Markdown rendering from filled-in RDF/JSON-LD payloads.
- Treat JSON-LD payloads from the PDD workflow shell as the primary local input.
- Normalize JSON-LD into an expanded JSON-LD or RDF graph model before
  rendering.
- Resolve values using canonical predicates.
- Render repeated structures as repeated subsections, tables, or lists according
  to the rendering profile.
- Render repeated impact, data, and monitoring parameters as one table per
  parameter under the relevant subsection.
- Resolve concept IRIs to labels where available.
- Include source artifact metadata and rendering metadata in Markdown front
  matter and back-matter metadata, not in the PDD content sections.
- Include a metadata appendix in the rendered Markdown.
- Add fixture data and expected rendered Markdown output.
- Added `dataRequirements/document-rendering/fixtures/pdd-alpha-input.jsonld`
  as a filled fixture payload.
- Added `dataRequirements/document-rendering/fixtures/pdd-alpha-rendered.md` as
  the deterministic golden filled output.
- Added `dataRequirements/tests/test_pdd_filled_rendering.py` to validate
  deterministic rendering, required PDD-A/B/C placement, and label rendering.

End-of-phase criteria:

- A local command renders a complete Markdown PDD from a fixture payload.
- No raw JSON is emitted in the document body.
- Required PDD-A/B/C content appears under the expected headings.
- Concept IRIs render as labels where labels are available.
- The rendered output is deterministic and covered by a golden test.

### Phase 5: Add Validation-Aware Export Modes

Status: completed on 2026-05-26.

Tasks:

- Add draft mode for incomplete working data.
- Add final mode that requires SHACL-valid input before rendering.
- Define placeholder and warning behavior for missing draft values.
- Include validation status in generated front matter.
- Added `--render-mode {draft,final}` to
  `tooling/document-rendering/render_pdd_markdown.py`.
- Added final-mode SHACL validation against NIAS shapes and ontology graphs,
  with explicit export failure on non-conformant input.
- Added draft/final validation status rendering in metadata appendix output.
- Extended `dataRequirements/tests/test_pdd_filled_rendering.py` to cover draft
  rendering, final-mode failure for non-conformant input, and final-mode success
  for conformant input.

End-of-phase criteria:

- Draft mode renders incomplete data with visible placeholders or warnings.
- Final mode fails when required SHACL constraints are not met.
- Final mode succeeds for a valid PDD fixture.
- Tests cover valid, invalid, and draft inputs.

### Phase 6: Compile Markdown To PDF And Website Output

Status: completed on 2026-05-26.

Tasks:

- Add a PDF compilation command using Pandoc as the default compiler.
- Add an HTML/static-site output path.
- Define deterministic output filenames.
- Include generated artifact metadata for Markdown, PDF, and website outputs.
- Emit `pdd.metadata.jsonld` and `pdd.validation.json` sidecar files for final
  exports.
- Include a short document ID, source hash, or version reference in the PDF
  footer.
- Added `--output-dir` and repeatable `--output-target {markdown,pdf,html}` to
  `tooling/document-rendering/render_pdd_markdown.py`.
- Added deterministic export filenames (`pdd.md`, `pdd.pdf`, `pdd.html`) with
  Pandoc-based PDF/HTML compilation.
- Added final-export sidecars (`pdd.metadata.jsonld`, `pdd.validation.json`)
  with generated artifact metadata.
- Added PDF footer injection with a short deterministic document ID reference.
- Added Pandoc discovery via `PANDOC_BIN`, PATH, `/usr/local/bin/pandoc`, and
  `/opt/homebrew/bin/pandoc`.
- Added `xelatex` as the default Pandoc PDF engine for local and release PDF
  compilation, with `PANDOC_PDF_ENGINE` as the explicit override.
- Added validated PDF fallback output when Pandoc is unavailable or cannot
  compile the Markdown.
- Added `dataRequirements/tests/test_pdd_output_compilation.py` to cover
  deterministic artifact names, sidecar generation, actual PDF output, and clear
  compilation failures.

End-of-phase criteria:

- A local command produces Markdown and PDF from the same valid fixture.
- A local command produces HTML or static website output from the same Markdown.
- Generated PDF and HTML include the same PDD content as the Markdown source.
- Blank-template and draft filled-data PDF outputs are real displayable PDF
  files, not text files with a `.pdf` extension.
- Compilation failures are surfaced clearly.
- The PDF footer includes the expected document ID/hash/version reference.
- Sidecar metadata and validation files are produced for final exports.
- PDF/HTML build outputs are ignored unless an explicit release workflow stores
  them.
- The default Pandoc PDF engine is documented and test-covered.

### Phase 7: Integrate With The PDD Workflow Shell

Status: completed on 2026-05-26.

Tasks:

- Add a local shell action or command that exports the current PDD workflow
  payload to Markdown.
- Keep export logic outside generated shape2flutter Dart files.
- Allow the user to export draft Markdown before final validation.
- Allow final export only after the workflow gates and SHACL validation pass.
- Confirmed Phase 6 output compilation remains complete via
  `dataRequirements/tests/test_pdd_output_compilation.py`.
- Added
  `dataRequirements/shape2flutter/pdd_workflow_shell/tool/export_pdd_workflow_markdown.py`
  to map shell PDD-A/B/C payload handoff into renderer JSON-LD input and invoke
  `render_pdd_markdown.py`.
- Added final-mode workflow gate checks in the shell export tool for approved
  PDD-A/B/C validation reviews before invoking renderer final mode.
- Added `dataRequirements/tests/test_pdd_workflow_shell_export.py` to cover
  draft export payload handoff and final export gate enforcement.

End-of-phase criteria:

- The workflow shell can produce a draft Markdown PDD from entered PDD data.
- The export includes PDD-A, PDD-B, and PDD-C content, not only document wrapper
  metadata.
- The shell does not duplicate rendering rules that belong in the rendering
  profile.
- Shell tests cover the export trigger or export payload handoff.

### Phase 8: Add Regression And Release Checks

Status: completed on 2026-05-26.

Tasks:

- Added an explicit PDD Markdown rendering regression step to
  `dataRequirements/shape2flutter/check-pdd-workflow.sh`.
- Kept the rendering regression suite in `dataRequirements/tests/test_pdd_*.py`,
  covering profile parsing, blank template generation, filled rendering,
  validation-aware modes, workflow-shell export handoff, and PDF/HTML
  compilation behavior.
- Added `dataRequirements/document-rendering/README.md` to document blank
  template rendering, draft and final Markdown rendering, deterministic output
  targets, and workflow-shell export commands.
- Decided that repository automation should keep Markdown-first checks as the
  default CI requirement, while full PDF/HTML compilation remains a local or
  release check when Pandoc is installed.

End-of-phase criteria:

- One local command proves the PDD rendering workflow is healthy.
- Regression tests cover both template projection and filled-data projection.
- Documentation explains how to generate blank templates, draft PDD Markdown,
  final PDD Markdown, PDF, and website output.
- The implementation remains independent of Fluree/IPFS/Hedera platform
  deployment.

## Resolved Decisions

- Pandoc PDF output defaults to `xelatex` for local development and release
  checks because NIAS PDD content may include Unicode labels, names, units, and
  concept-scheme terms.
- Routine CI remains Markdown-first and does not require a system Pandoc or TeX
  installation. PDF/HTML compilation stays in local and release verification.
- `PANDOC_PDF_ENGINE` is the explicit override for local or release workflows
  that need another Pandoc-supported engine.

## Open Questions

- Which visual style template should be used for NIAS PDFs?
- Which concept schemes must be loaded for label resolution in the first
  implementation?
- Which title-page fields are mandatory for the first NIAS PDD profile versus
  optional later additions?
- Should later render directives support filters or formatting options beyond
  the Phase 2 `{{ render: ... }}` syntax?

## Immediate Next Step

Choose the NIAS release styling so the documented PDF/HTML release checks can
be standardized further.
