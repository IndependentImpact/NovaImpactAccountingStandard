# Tooling

This directory contains helper scripts that generate derived documentation from
canonical NIAS semantic sources.

## What is here

- `generate_glossary_markdown.py` renders
  [`02-a-Glossary.md`](../02-a-Glossary.md) from
  [`glossary/NovaImpactAccountingStandardGlossary.ttl`](../glossary/NovaImpactAccountingStandardGlossary.ttl).
- `document-rendering/` contains script entry points and shared helpers used to
  render PDD, Validation/Verification Report, and Monitoring Report markdown
  outputs from canonical semantic inputs.

## When to work here

- Use this directory when you need to regenerate or check derived documentation.
- Prefer editing the canonical Turtle files first and then using the script to
  update generated markdown.

## Command

```bash
python tooling/generate_glossary_markdown.py --help

python tooling/document-rendering/render_pdd_markdown.py --help
```
