# GenerateStandardText

This directory contains tooling to deterministically generate standard-text
markdown files from the SKOS Turtle sources in [`../glossary/`](../glossary/).

## What is here

| File | Description |
| --- | --- |
| `tool/generate_skos_markdown.py` | Core generator: renders any SKOS Turtle file to a markdown section with one subsection per `skos:ConceptScheme`. |
| `generate_all.sh` | Shell script that runs the generator for every relevant Turtle source and writes the outputs listed below. |
| `02-a-Glossary.md` | Generated from `glossary/NovaImpactAccountingStandardGlossary.ttl`. |
| `03-a-Principles.md` | Generated from `glossary/Principle.ttl`. |
| `04-a-KnowledgeAndSkillsReputationRules.md` | Generated from `glossary/ReputationRules.ttl`. |
| `05-a-ScoringRules.md` | Generated from `glossary/ScoringRules.ttl`. |
| `VVS-RequirementStatus.md` | Generated from `glossary/ValidationVerificationStandard.ttl`. |

## Usage

Generate all files (from the repository root):

```bash
bash GenerateStandardText/generate_all.sh
```

Check that committed files are up to date (CI mode):

```bash
bash GenerateStandardText/generate_all.sh --check
```

Generate a single file:

```bash
python GenerateStandardText/tool/generate_skos_markdown.py \
  --ttl glossary/NovaImpactAccountingStandardGlossary.ttl \
  --output GenerateStandardText/02-a-Glossary.md \
  --section-heading "## Glossary"
```

## Authoring workflow

1. Edit the canonical Turtle files in `glossary/`.
2. Run `bash GenerateStandardText/generate_all.sh` to regenerate the markdown.
3. Commit both the Turtle changes and the regenerated markdown.
4. CI will run `generate_all.sh --check` to prevent drift.

## Generator options

```
generate_skos_markdown.py --ttl <path> --output <path> [--section-heading <heading>] [--check]
```

| Flag | Description |
| --- | --- |
| `--ttl` | Path to the input SKOS Turtle file. |
| `--output` | Path to the output markdown file. |
| `--section-heading` | Top-level markdown heading (default: `## Vocabulary`). |
| `--check` | Exit non-zero if the generated content differs from the existing output file. |
