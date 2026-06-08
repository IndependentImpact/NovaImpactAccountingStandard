# Glossary

This directory contains the canonical Nova Impact Accounting Standard semantic
vocabulary in Turtle (`.ttl`) files.

## What is here

- `NovaImpactAccountingStandardGlossary.ttl` is the main SKOS glossary.
- `NovaImpactAccountingStandardOntology.ttl` defines the ontology terms used by
  the standard.
- `Principle*.ttl`, `ScoringRules*.ttl`, and `ReputationRules*.ttl` define
  supporting principles and rule vocabularies together with their SHACL shapes.
- `ValidationVerificationStandard.ttl` contains the validation and verification
  vocabulary used elsewhere in the repository.

## When to work here

- Edit these files when you are changing canonical terms, definitions,
  taxonomies, or ontology relationships.
- Keep in mind that other repository outputs are derived from these files.

## Related tooling

The glossary markdown in [`../02-a-Glossary.md`](../02-a-Glossary.md) is
generated from these semantic sources by
[`../tooling/generate_glossary_markdown.py`](../tooling/generate_glossary_markdown.py).
