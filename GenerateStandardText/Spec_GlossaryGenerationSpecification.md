# Specification: Generate standard-text markdown from glossary SKOS Turtle

## 1. Objective

Keep SKOS Turtle files in `glossary/` as the canonical source and deterministically generate the markdown outputs in `GenerateStandardText/` so committed documentation cannot drift.

## 2. Scope

- **In scope:** deterministic generation of the following markdown outputs from SKOS Turtle inputs:
  - `02-a-Glossary.md` ← `glossary/NovaImpactAccountingStandardGlossary.ttl`
  - `03-a-Principles.md` ← `glossary/Principle.ttl`
  - `03-b-GuidingAndReviewQuestions.md` ← `glossary/GuidingReviewQuestions.ttl`
  - `04-a-KnowledgeAndSkillsReputationRules.md` ← `glossary/ReputationRules.ttl`
  - `05-a-ScoringRules.md` ← `glossary/ScoringRules.ttl`
  - `VVS-RequirementStatus.md` ← `glossary/ValidationVerificationStandard.ttl`
- **Out of scope:** changing canonical content ownership from Turtle to markdown.

## 3. Implemented command contracts

Single-file generator:

```bash
python GenerateStandardText/tool/generate_skos_markdown.py \
  --ttl <input.ttl> \
  --output <output.md> \
  --section-heading "## <Heading>" \
  [--check]
```

Batch generator:

```bash
bash GenerateStandardText/generate_all.sh [--check]
```

`--check` must return non-zero when generated output differs from the committed file (or when the expected output file does not exist).

## 4. Deterministic rendering requirements

1. Parse Turtle into RDF.
2. Select all `skos:ConceptScheme` resources.
3. For each scheme, gather concepts where `skos:inScheme` references the scheme.
4. Sort schemes by case-insensitive `skos:prefLabel` (fallback: IRI).
5. Sort concepts by case-insensitive `skos:prefLabel` (fallback: IRI).
6. Render stable markdown with:
   - top heading from `--section-heading`
   - `### <scheme prefLabel>` per scheme
   - scheme definition paragraph
   - table columns `Term`, `Definition`, `IRI`
7. Escape markdown table-cell pipe characters and normalize multiline values for stable output.

## 5. Validation and failure policy

Generation fails with a clear error list if any required fields are missing:

- Scheme missing `skos:prefLabel` or `skos:definition`
- Concept missing `skos:prefLabel`, `skos:definition`, or `skos:inScheme`
- Concept references a non-existent scheme via `skos:inScheme`

On validation failure, the command exits non-zero and does not write partial markdown output.

## 6. Authoring and CI workflow

1. Edit canonical Turtle files in `glossary/`.
2. Regenerate with `bash GenerateStandardText/generate_all.sh`.
3. Commit Turtle and regenerated markdown together.
4. CI (or local checks) runs `bash GenerateStandardText/generate_all.sh --check` to detect drift.

## 7. Placement rationale

This specification lives in `GenerateStandardText/` because it defines the behavior and workflow of the generator scripts and outputs owned by this directory.
