# Phase 4 Compatibility Adapters

`phase4_compatibility_toFluree.R` contains SHACL-oriented replacements for the
frozen legacy functions in `reference/`.

Use these adapters when transforming old API payloads into the canonical NIAS
RDF model. The `reference/` directory remains the Phase 0 audit baseline and
should not be edited for migration compatibility work.

The adapters keep the old function names where possible, but emit:

- canonical AIAO, Claim Ontology, Impact Ontology, InfoComm, and NIAS namespace
  IRIs;
- SKOS concept IRIs for controlled values;
- `impactont:hasIndicatorValue` plus `rdf:value` for state values;
- `ind:hasUnit` QUDT unit links instead of `nias-o:unitOfMeasure` strings;
- stable local indicator and methodology IRIs where they can be resolved;
- Hashgraph Ontology `hedera:TopicMessage` nodes for workflow consensus
  evidence.
