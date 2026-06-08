# Nova Impact Accounting Standard

On the [Nova Impact Accounting Standard](https://nova.org.za/novaimpactaccountingstandard), a standard provides the following artefacts:

* A **glossary** in the form of a `skos:ConceptScheme` with its terms, definitions and taxonomies.
* A list of relevant **indicators** (expressed in terms of the Indicator Ontology), as a `skos:ConceptScheme`
* A list of relevant **methodologies** (expressed in terms of the Methodology Ontology), as a `skos:ConceptScheme`
* The **data requirements** for all actions (defined in the glossary) that can be performed in terms of the standard, as SHACL constraints. Think of this as a set of templates. If it is required that actions be performed in a specific sequence, this is enforced by making a reference to the resulting artefact of a preceding step a requirement in a subsequent step. These can be tested and compiled to UIs of various formats and for various platforms using [shape2flutter](https://github.com/IndependentImpact/shape2flutter). 
* The **reputation requirement** for all actions that can be performed in terms of the standard, as SHACL constraints. The reputation requirements refer to either an existing `skos:ConceptScheme` with skills and knowledge domains, or one must accompany the standard. 

## Major directories

The repository is organised into a small number of top-level directories. Start
with the README in the directory you want to work in before making changes.

| Directory | What it contains | Start here |
| --- | --- | --- |
| [`dataRequirements/`](dataRequirements/README.md) | Canonical SHACL shapes, mappings, fixtures, tests, release packaging, and UI/rendering projections. | Use this for semantic validation, workflow shapes, and release verification. |
| [`glossary/`](glossary/README.md) | The core NIAS glossary, ontology, principles, scoring rules, and validation/verification vocabulary in Turtle. | Edit here when changing canonical concepts or ontology terms. |
| [`indicators/`](indicators/README.md) | Indicator concept schemes used by the standard. | Edit here when updating approved indicators. |
| [`knowledgeDomains/`](knowledgeDomains/README.md) | Knowledge-domain concept schemes used by the standard. | Edit here when updating taxonomy for required expertise areas. |
| [`methodologies/`](methodologies/README.md) | Methodology concept schemes referenced by the standard. | Edit here when updating approved methodologies. |
| [`reference/`](reference/README.md) | Legacy/reference schemas, transformation scripts, and template documents. | Usually reference-only; avoid changing these unless you are intentionally updating reference assets. |
| [`tooling/`](tooling/README.md) | Utility scripts that generate derived documentation from canonical semantic files. | Use this for regeneration and consistency checks. |
| [`d3/`](d3/README.md) | Browser-viewable D3 visualisations of glossary and ontology content. | Use these to explore the model; they are documentation/support assets rather than canonical sources. |

## Suggested starting points

- For the semantic standard itself, begin in [`glossary/`](glossary/README.md)
  and [`dataRequirements/`](dataRequirements/README.md).
- For generated or derived documentation, see [`tooling/`](tooling/README.md)
  and [`d3/`](d3/README.md).
- For legacy schemas, templates, or transformation references, see
  [`reference/`](reference/README.md).
