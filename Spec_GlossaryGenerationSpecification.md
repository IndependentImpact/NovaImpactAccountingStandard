# Specification: Generate `02-a-Glossary.md` from `glossary/NovaImpactAccountingStandardGlossary.ttl`

## 1. Objective

Make `glossary/NovaImpactAccountingStandardGlossary.ttl` the canonical source for glossary content and deterministically generate `02-a-Glossary.md` from it so printed/HTML/PDF outputs cannot drift.

## 2. Scope

- **In scope:** generation of the glossary markdown section from SKOS concept schemes and concepts in `glossary/NovaImpactAccountingStandardGlossary.ttl`.
- **Out of scope:** changing the canonical source from Turtle to markdown.

## 3. Source and data model assumptions

The generator reads one RDF graph from:

- `glossary/NovaImpactAccountingStandardGlossary.ttl`

The graph is expected to use SKOS with:

- `skos:ConceptScheme` with `skos:prefLabel`, `skos:definition`, `skos:hasTopConcept`
- `skos:Concept` with `skos:prefLabel`, `skos:definition`, `skos:inScheme`
- optional hierarchy/relations (`skos:broader`, `skos:narrower`, `skos:related`) may be rendered if present later

## 4. Deterministic generation requirements

1. Parse Turtle to RDF.
2. Select all `skos:ConceptScheme` resources.
3. For each scheme, gather concepts where `skos:inScheme` references the scheme.
4. Sort schemes by case-insensitive `skos:prefLabel` (fallback: IRI).
5. Sort concepts inside each scheme by case-insensitive `skos:prefLabel` (fallback: IRI).
6. Render markdown with a stable template:
   - `## Glossary`
   - for each scheme:
     - `### <scheme prefLabel>`
     - scheme definition paragraph
     - table with columns: `Term`, `Definition`, `IRI`
7. Overwrite `02-a-Glossary.md` in full (no manual edits retained).

## 5. Validation and failure policy

Generation must fail fast if any selected scheme/concept is missing required fields:

- Scheme missing `skos:prefLabel` or `skos:definition`
- Concept missing `skos:prefLabel`, `skos:definition`, or `skos:inScheme`
- Concept references a scheme that does not exist in graph

If validation fails, output a clear error list with offending IRIs and do not emit a partial markdown file.

## 6. Suggested command contract

Implement a dedicated script (for example under `tooling/` or `tooling/document-rendering/`) with a CLI similar to:

```bash
python <script>.py \
  --ttl glossary/NovaImpactAccountingStandardGlossary.ttl \
  --output 02-a-Glossary.md
```

Optional future flags:

- `--check` (non-zero exit if generated output differs)
- `--include-iri/--no-include-iri`

## 7. CI/authoring workflow

1. Edit only `.ttl` glossary terms/schemes.
2. Run glossary markdown generator.
3. Commit both TTL and regenerated markdown (if changed).
4. CI runs generator in `--check` mode to prevent drift.

---

## 8. Reverse analysis: markdown concepts not represented in current concept schemes

The following conceptual lists are present in markdown but not currently modelled as SKOS concept schemes in `glossary/NovaImpactAccountingStandardGlossary.ttl`.

| Source markdown | Concept list in markdown | Gap vs current concept schemes | Proposed concept scheme(s) |
|---|---|---|---|
| `03-a-Principles.md` | Impact principles: Purposefulness, Do no harm, Effectiveness, Efficiency, Equity & inclusivity, Adaptiveness | No principle schemes exist | `ImpactPrinciple` |
| `03-a-Principles.md` | Accounting principles: Relevance, Completeness, Consistency, Accuracy, Conservativeness, Verifiability, Accountability | No accounting-principle scheme exists | `AccountingPrinciple` |
| `05-a-ActivityScoringRules.md` | Review mandates and scoring framing: Validation, Verification, reviewable aspects, expert-threshold weighting | No scheme for mandate/type of review exists | `ReviewMandate`, `ScoringModelTerm` |
| `06-a-IndicatorScoringRules.md` | Indicator quality dimensions: Validity, Reliability, Sensitivity, Specificity, Timeliness | No indicator-dimension scheme exists | `IndicatorQualityDimension` |
| `07-a-MethodologyScoringRules.md` | Methodology quality dimensions (11 listed) | No methodology-dimension scheme exists | `MethodologyQualityDimension` |
| `08-a-InstrumentScoringRules.md` | Instrument quality dimensions (accuracy, precision, calibration, drift, traceability, etc.) | No instrument-dimension scheme exists | `InstrumentQualityDimension` |
| `04-a-KnowledgeAndSkillsReputationRules.md` | Time-based decay parameters and related KSR lifecycle terms | No scheme for reputation dynamics terms | `ReputationLifecycleTerm` |

## 9. Plan to update concept schemes

1. **Triage terms by intent**
   - Keep narrative-only prose in markdown.
   - Promote controlled, repeatable choices/rubrics into SKOS concept schemes.

2. **Add new schemes incrementally to `NovaImpactAccountingStandardGlossary.ttl`**
   - Start with high-value controlled vocabularies used in scoring/review workflows:
     1. `ReviewMandate`
     2. `ImpactPrinciple`
     3. `AccountingPrinciple`
     4. `IndicatorQualityDimension`
   - Add methodology/instrument/reputation schemes next.

3. **Define each concept with stable IDs and definitions**
   - Use consistent NIAS IRI pattern.
   - Add `skos:prefLabel`, `skos:definition`, `skos:inScheme`, `skos:topConceptOf`.

4. **Link markdown narrative to concept IRIs**
   - Keep explanatory text in markdown.
   - Render canonical term lists from TTL into the relevant sections (not only glossary) where controlled lists are required.

5. **Introduce governance checks**
   - For each controlled list in markdown sections, either:
     - generate directly from TTL, or
     - maintain an explicit “narrative-only” marker so drift checks ignore non-canonical prose.

6. **Rollout order**
   - Phase 1: glossary generation + drift check.
   - Phase 2: principles and activity/indicator scoring controlled lists.
   - Phase 3: methodology/instrument/reputation controlled lists.
