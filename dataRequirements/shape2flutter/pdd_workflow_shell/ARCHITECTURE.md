# PDD Workflow Shell — Architecture and Usage Patterns

**Document scope:** This paper analyses the `dataRequirements/shape2flutter/pdd_workflow_shell`
Flutter package. It documents how the shell composes generated shape2flutter Dart
widgets into a complete workflow UI, and provides concrete guidance for developers
building equivalent shells around other generated form bundles (e.g. the
monitoring-report Flutter files).

---

## Table of Contents

1. [Overview](#1-overview)
2. [Code Layout](#2-code-layout)
3. [Build Pipeline — from SHACL to Dart](#3-build-pipeline--from-shacl-to-dart)
4. [Generated Widget Import Contract](#4-generated-widget-import-contract)
5. [Routing and Navigation](#5-routing-and-navigation)
6. [State Ownership](#6-state-ownership)
7. [Seed Data and Form Pre-population](#7-seed-data-and-form-pre-population)
8. [Role-Based Step Access](#8-role-based-step-access)
9. [The Workflow Gate](#9-the-workflow-gate)
10. [The WorkflowArtifact Record](#10-the-workflowartifact-record)
11. [The Export Bridge](#11-the-export-bridge)
12. [Shared Vocabulary — NiasTerm](#12-shared-vocabulary--niasterm)
13. [Tests](#13-tests)
14. [Reusable Patterns for Other Workflow Shells](#14-reusable-patterns-for-other-workflow-shells)
15. [Known Limitations](#15-known-limitations)
16. [Applying This Pattern to the Monitoring-Report Shell](#16-applying-this-pattern-to-the-monitoring-report-shell)

---

## 1. Overview

The `pdd_workflow_shell` is an intentionally thin Flutter web application whose
sole purpose is to **host generated SHACL-driven form widgets in a sequenced,
role-gated workflow**. The package README (lines 6–14) captures this intent
directly:

> The shell routes between PDD-A, PDD-B, PDD-C, PDD-A/B/C validation reviews,
> and PDD-CIR; keeps generated JSON-LD-like payload maps between steps; captures
> local document message IDs and IPFS URI references; separates project developer
> and PDD validator roles; blocks PDD-CIR until the approval gate passes.

Everything related to canonical payload validation stays in SHACL assets and
(future) Fluree services. The shell is deliberately free of canonical validation
logic.

**Key design axiom:** the shell never modifies the generated widgets and does not
re-implement any field-level validation. It relies entirely on the `initial:`
seed map and the submitted snapshot it receives from each widget.

---

## 2. Code Layout

```
pdd_workflow_shell/
│
├── lib/
│   ├── main.dart                         Seven-line entrypoint; calls runApp()
│   ├── generated/                        NOT committed; populated by prepare script
│   │   └── README.md                     Explains gitignore policy
│   └── src/
│       ├── pdd_workflow_shell_app.dart   Full UI: layout, routing, form embedding
│       └── workflow_contract.dart        State, enums, roles, gate logic, seeds
│
├── test/
│   ├── workflow_contract_test.dart       Unit tests for gate and seed logic
│   └── payload_visibility_test.dart      Widget test for payload dialog
│
├── tool/
│   ├── prepare_pdd_workflow_shell.sh     Builds & copies generated Dart files
│   ├── check_pdd_workflow_shell.sh       flutter test + analyze + build web
│   └── export_pdd_workflow_markdown.py   Bridge: submitted JSON → PDD renderer
│
├── pubspec.yaml                          No external state packages
├── analysis_options.yaml
└── web/                                  Standard Flutter web host files
```

There are exactly **two hand-authored Dart files** (`main.dart` and
`workflow_contract.dart`); everything else is either generated or tooling.

---

## 3. Build Pipeline — from SHACL to Dart

### 3.1 Shape source

The canonical shape bundle is
`dataRequirements/shape2flutter/pdd-workflow-ui-shapes.ttl`. It contains one
`sh:NodeShape` per workflow step:

| Shape | Workflow step |
|---|---|
| `PddSectionAUiShape` | PDD-A (project developer) |
| `PddSectionBUiShape` | PDD-B (project developer) |
| `PddSectionCUiShape` | PDD-C (project developer) |
| `PddSectionAValidationReviewUiShape` | Validate PDD-A (validator) |
| `PddSectionBValidationReviewUiShape` | Validate PDD-B (validator) |
| `PddSectionCValidationReviewUiShape` | Validate PDD-C (validator) |
| `PddCertificateIssuanceRequestUiShape` | PDD-CIR (project developer) |

### 3.2 Build script (`build-pdd-workflow.sh`)

```bash
"$SHAPE2FLUTTER_BIN" lint   -allow-path-prefixes "$ALLOWED_PREFIXES" "$SHAPES_FILE"
"$SHAPE2FLUTTER_BIN" emit-jsonld -format jsonld -o "$SCHEMA_DIR/forms.jsonld" "$SHAPES_FILE"
"$SHAPE2FLUTTER_BIN" build  -outdir "$FLUTTER_DIR" "$SHAPES_FILE"
```

Outputs land in `/tmp/nias-shape2flutter/pdd-workflow/{schema,flutter}` (or the
path set by `$OUT_ROOT`).

### 3.3 Prepare script (`tool/prepare_pdd_workflow_shell.sh`)

```bash
"$ROOT_DIR/dataRequirements/shape2flutter/build-pdd-workflow.sh"  # run shape2flutter
rm -f "$SHELL_DIR/lib/generated"/*.dart                            # clean old files
cp "$OUT_ROOT/flutter"/*.dart "$SHELL_DIR/lib/generated/"          # copy new files
flutter pub get
dart format "$SHELL_DIR/lib" "$SHELL_DIR/test"
```

The generated files are **never committed** (`.gitignore` covers
`lib/generated/*.dart`). The canonical source remains the SHACL bundle.

### 3.4 CI check script (`tool/check_pdd_workflow_shell.sh`)

```bash
"$SHELL_DIR/tool/prepare_pdd_workflow_shell.sh"
flutter test
flutter analyze
flutter build web
```

The prepare step always runs before tests so CI always works against a freshly
generated widget set.

---

## 4. Generated Widget Import Contract

### 4.1 Import pattern

Each generated file is imported with a short namespace alias:

```dart
// lib/src/pdd_workflow_shell_app.dart lines 5–11
import '../generated/pddcertificateissuancerequestuishape.dart' as cir;
import '../generated/pddsectionauishape.dart'                   as pdda;
import '../generated/pddsectionavalidationreviewuishape.dart'   as pdda_review;
import '../generated/pddsectionbuishape.dart'                   as pddb;
import '../generated/pddsectionbvalidationreviewuishape.dart'   as pddb_review;
import '../generated/pddsectioncuishape.dart'                   as pddc;
import '../generated/pddsectioncvalidationreviewuishape.dart'   as pddc_review;
```

One import per shape file; always aliased to avoid name collisions between
generated classes that follow a common naming pattern.

### 4.2 Instantiation contract

Every generated `FormWidget` accepts exactly one named parameter:

```dart
SomeShapeFormWidget(initial: Map<String, dynamic>)
```

The widget reads `initial` once on `initState` and manages its own field state
internally. The shell **never** calls `setState` on field-level changes and
**never** wires `onChanged` callbacks. The only interaction between the shell and
the widget is:

1. **Input:** the `initial:` seed map, provided at construction time.
2. **Output:** the widget returns nothing to the shell until the user taps
   **Submit**, at which point `_submitActiveStep()` reads `_drafts[_activeStep]`
   — the *last seed* the shell gave to that step, not a live read-back from the
   widget's internal state.

> **Important limitation:** if the user edits a form, navigates to another step
> without submitting, and returns, the form recreates from the seed. In-progress
> edits are lost unless the widget itself persists them.

### 4.3 Form switch

```dart
// lib/src/pdd_workflow_shell_app.dart lines 126–152
Widget _buildForm(PddWorkflowStep step) {
  final draft = _drafts[step]!;
  switch (step) {
    case PddWorkflowStep.pddA:
      return pdda.PddSectionAUiShapeFormWidget(initial: draft);
    case PddWorkflowStep.pddB:
      return pddb.PddSectionBUiShapeFormWidget(initial: draft);
    case PddWorkflowStep.pddC:
      return pddc.PddSectionCUiShapeFormWidget(initial: draft);
    case PddWorkflowStep.reviewA:
      return pdda_review.PddSectionAValidationReviewUiShapeFormWidget(initial: draft);
    case PddWorkflowStep.reviewB:
      return pddb_review.PddSectionBValidationReviewUiShapeFormWidget(initial: draft);
    case PddWorkflowStep.reviewC:
      return pddc_review.PddSectionCValidationReviewUiShapeFormWidget(initial: draft);
    case PddWorkflowStep.pddCir:
      return cir.PddCertificateIssuanceRequestUiShapeFormWidget(initial: draft);
  }
}
```

---

## 5. Routing and Navigation

There is **no `Navigator`, no named routes, and no URL routing**. Navigation is
entirely tab-style within a single `Scaffold`.

```
Scaffold
├── AppBar  — title + role switcher (SegmentedButton)
└── body: Row
    ├── SizedBox(width: 300)  ← _StepRail (ListView of _StepTile cards)
    └── Expanded              ← _WorkflowPanel (header + form or blocked panel + submit button)
```

Selecting a `_StepTile` calls `onStepSelected` which does:

```dart
setState(() {
  _activeStep = step;
  _refreshDerivedDraft(step);   // re-seeds review/CIR drafts from submitted artifacts
});
```

`_WorkflowPanel` rebuilds and `_buildForm(_activeStep)` returns the appropriate
widget.

**Consequence:** there is no deep-linking, back-button handling, or browser
history integration. Pressing the browser back button exits the app. Any shell
that needs URL-addressable steps must add a `Router` / `GoRouter` layer on top
of this pattern.

### 5.1 _FormSurface scroll wrapper

Generated forms can exceed viewport width. The shell wraps each form in a
dual-axis scroll container with a minimum content width of 1160 px:

```dart
// lib/src/pdd_workflow_shell_app.dart lines 345–367
LayoutBuilder(builder: (context, constraints) {
  final contentWidth = constraints.maxWidth < 1160 ? 1160.0 : constraints.maxWidth;
  return SingleChildScrollView(
    padding: const EdgeInsets.all(20),
    child: SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: SizedBox(width: contentWidth - 40, child: child),
    ),
  );
})
```

This pattern should be carried into any monitoring-report shell.

---

## 6. State Ownership

All mutable state lives in `_PddWorkflowShellPageState`, a single `StatefulWidget`.
There is **no external state management library** — `pubspec.yaml` lists only
`flutter` and `flutter_web_plugins`.

| Variable | Type | Purpose |
|---|---|---|
| `_workflow` | `PddWorkflowState` | Holds submitted `WorkflowArtifact` records keyed by step |
| `_drafts` | `Map<PddWorkflowStep, Map<String,dynamic>>` | Current seed map for each step |
| `_role` | `WorkflowRole` | Currently selected role (developer / validator) |
| `_activeStep` | `PddWorkflowStep` | Which step panel is visible |

`PddWorkflowState` (`workflow_contract.dart` lines 279–590) is a plain Dart
class. Changes propagate exclusively through `setState` calls.

### 6.1 Submit flow

```
user taps Submit
  → _submitActiveStep()
      draft = _drafts[_activeStep]
      artifact = _workflow.submit(_activeStep, draft)   # stores WorkflowArtifact
      setState(() { … })                                # triggers gate re-evaluation
      ScaffoldMessenger.showSnackBar(...)               # shows documentMessageId
```

---

## 7. Seed Data and Form Pre-population

### 7.1 Initial seeding

`initState` seeds every step's draft before the first frame:

```dart
// lib/src/pdd_workflow_shell_app.dart lines 49–54
void initState() {
  super.initState();
  for (final step in PddWorkflowStep.values) {
    _drafts[step] = _workflow.documentSeed(step);
  }
}
```

`documentSeed(step)` (`workflow_contract.dart` lines 399–449) supplies:

- `resourceIpfsUri` — placeholder `ipfs://draft-{stepName}`
- `documentSchema` — step-specific schema IRI (e.g. `PDDxA-1.0.0`)
- `isEncrypted: false`
- `documentAuthor` — role-appropriate placeholder IRI
- `authProof` — `eddsa-signature` placeholder
- `hasWorkflowSubmission` — a fully-structured list with `submittedDocument`,
  `workflow`, `workflowStep`, `workflowSubject`, `workflowDocumentSubmittedBy`,
  `workflowDocumentRecipient`, and a `workflowSubmissionConsensusMessage` submap

For PDD-A and PDD-B, `documentSeed` also pre-builds the nested `reportContent`
submap, including `hasObjective`, `hasSpatialLocation`, `technologyOrMeasure`,
`projectParty` (PDD-A) and `hasDeclaredImpact`, `impactClaim` (PDD-B). This
ensures the generated subform widgets open with at least one item in each
repeating list.

### 7.2 Derived draft refresh on tab selection

When a review step or PDD-CIR step is selected, `_refreshDerivedDraft` re-seeds
the draft from already-submitted artifacts:

```dart
// lib/src/pdd_workflow_shell_app.dart lines 154–162
void _refreshDerivedDraft(PddWorkflowStep step) {
  final section = step.reviewSection;
  if (section != null) {
    _drafts[step] = _workflow.reviewSeed(section);   // copies isReviewOf from source artifact
  }
  if (step == PddWorkflowStep.pddCir) {
    _drafts[step] = _workflow.pddCirSeed();          // injects three DocumentReference values
  }
}
```

`reviewSeed(section)` (`workflow_contract.dart` lines 529–556):
- Copies the source document IRI into `isReviewOf`.
- Pre-sets `finalReviewDecision` to `reviewApprove`.
- Pre-builds a `fieldReview` list with a `reviewTarget` subform pointing to an
  anchor in the source document.

`pddCirSeed()` (lines 387–397):
- Iterates approved review artifacts and writes each as a `DocumentReference`
  `{documentMessageId, resourceIpfsUri}` under the section-specific predicate
  (`pddSectionAValidationReview`, etc.).
- Pre-sets `requestedIssuanceAccountId` to `'0.0.2002'`.

---

## 8. Role-Based Step Access

```dart
// workflow_contract.dart lines 3–7
enum WorkflowRole { developer, validator }
enum PddWorkflowStep { pddA, pddB, pddC, reviewA, reviewB, reviewC, pddCir }
```

Each step declares its `requiredRole`:

```dart
// workflow_contract.dart lines 205–217
WorkflowRole get requiredRole {
  switch (this) {
    case PddWorkflowStep.reviewA:
    case PddWorkflowStep.reviewB:
    case PddWorkflowStep.reviewC:
      return WorkflowRole.validator;
    default:
      return WorkflowRole.developer;
  }
}
```

`PddWorkflowState.canOpen(step, role)` (lines 290–305) checks:

1. Role matches the step's `requiredRole`.
2. For review steps: the source section has been submitted.
3. For PDD-CIR: the gate result is `allowed`.

`blockers(step, role)` (lines 307–323) returns human-readable strings describing
each unmet prerequisite. These strings appear as subtitle text in the locked
`_StepTile`.

The AppBar role switcher is a `SegmentedButton<WorkflowRole>` that calls
`setState` on selection, causing the entire step rail to re-evaluate access.

---

## 9. The Workflow Gate

### 9.1 In-shell implementation

`PddWorkflowState.gateResult()` (`workflow_contract.dart` lines 339–385)
evaluates the cross-document consistency of the three submitted section reviews:

| Check | Failure message |
|---|---|
| Section source submitted | `"{section} has not been submitted."` |
| Section review submitted | `"{section} validation review has not been submitted."` |
| `finalReviewDecision == reviewApprove` | `"{section} validation review is not approved."` |
| `isReviewOf == source.documentIri` | `"{section} review does not point to the submitted document."` |
| `source.documentSchema == expectedSchema` | `"{section} source document has the wrong schema."` |
| `review.workflowSubject == source.workflowSubject` | `"{section} review workflow subject does not match the source."` |
| Review IRI unique across sections | `"{section} review duplicates another review artifact."` |

PDD-CIR becomes accessible only when `gateResult().allowed` is `true`.

### 9.2 Formal gate specification vs. shell implementation

The full gate contract is specified in
`dataRequirements/shape2flutter/pdd-workflow-gate.md`. The shell implements
a **subset** of that contract. Notably absent from the in-memory implementation:

- Stale-link detection (step 7 in the gate spec, lines 43–65).
- Ledger lookup via `resourceIpfsUri` / `documentMessageId`.
- The two qualitative review layers (`pddSectionQualitativeReview`,
  `pddDocumentLevelQualitativeReview`) listed in the gate spec table (lines 37–39).

These checks are deferred to the Fluree-backed service layer described in the
gate spec and the README integration boundary note (lines 78–88).

---

## 10. The WorkflowArtifact Record

```dart
// workflow_contract.dart lines 242–266
class WorkflowArtifact {
  final String documentIri;         // e.g. "https://nova.org.za/.../documents/pdd-alpha/pddA"
  final String documentSchema;      // e.g. "https://nova.org.za/.../document-schema/PDDxA-1.0.0"
  final String workflowSubject;     // IRI of the project
  final String documentMessageId;   // e.g. "0.0.1001-2026-01-01T00:00:00Z"
  final String resourceIpfsUri;     // e.g. "ipfs://draft-pdda"
  final Map<String, dynamic> payload;
}
```

`toDocumentReference()` serializes to the exact `DocumentReference` node the
PDD-CIR form expects:

```dart
Map<String, dynamic> toDocumentReference() => {
  '@type': '${NiasTerm.base}DocumentReference',
  NiasTerm.documentMessageId: documentMessageId,
  NiasTerm.resourceIpfsUri: resourceIpfsUri,
};
```

`documentMessageId` is derived from the `workflowSubmissionConsensusMessage`
embedded in the submitted payload:
`{topicId}-{consensusTimestamp}`, falling back to a placeholder if the payload
lacks those fields (lines 566–584).

---

## 11. The Export Bridge

`tool/export_pdd_workflow_markdown.py` is the off-device integration point
between submitted form JSON and the document rendering pipeline.

### 11.1 Inputs

```bash
tool/export_pdd_workflow_markdown.py \
  --pdd-a-json /tmp/pdd-a.json \
  --pdd-b-json /tmp/pdd-b.json \
  --pdd-c-json /tmp/pdd-c.json \
  --render-mode draft \
  --output /tmp/pdd.md
```

The three JSON files are the raw `Map<String,dynamic>` payloads that the shell
holds in `_drafts` after submission.

### 11.2 Processing (`build_renderer_payload`)

The function (lines 139–484 of the export script):

1. Extracts nested values from PDD-A, B, C payloads using helper functions
   (`_first`, `_as_list`, `_as_node_reference`, `_as_bool`).
2. Assigns deterministic IRIs to blank-node-like structures via
   `_resource_nodes` — location, technology, party, impact, claim nodes all
   receive `nias:.../suffix-{index}` IRIs.
3. Builds a flat JSON-LD `@graph` list with typed nodes for the project, report
   sections A/B/C, submission, topic, and message.
4. Collects artifact identity fields (`artifactContentCid`,
   `artifactSchemaCid`, `artifactSchemaVersionLabel`, `submissionEventKey`,
   `submissionMessageUrl`) from CLI flags.

### 11.3 IRI-value fields

Fields that require `{"@id": ...}` wrapping rather than plain string values are
enumerated explicitly:

```python
# export_pdd_workflow_markdown.py lines 34–38
IRI_VALUE_FIELDS = {
    f"{NIAS}publicPrivateClassification",
    f"{NIAS}techMeasType",
    f"{IND}hasUnit",
}
```

Any equivalent export bridge for another workflow must maintain a similar set.

### 11.4 Shared rendering infrastructure

The export script delegates to `run_renderer_with_payload` from
`tooling/document-rendering/export_workflow_report.py`. This shared helper
invokes the appropriate document renderer (e.g.
`render_pdd_markdown.py`) with the assembled JSON-LD graph, supporting both
`--render-mode draft` (no SHACL conformance check) and
`--render-mode final` (enforces SHACL before rendering).

The `--review-*-json` flags that appeared in older documentation are now
**deprecated** (lines 494–508). Validation reports are exported through a
separate pipeline.

### 11.5 Equivalent bridge for monitoring report

`dataRequirements/shape2flutter/monitoring_report/tool/export_monitoring_report_markdown.py`
follows the same structure:

1. Reads `--monitoring-json` (a single submitted JSON payload).
2. Calls `normalize_identity_field_names` from the shared helper.
3. Builds `_build_workflow_nodes`, `_build_interval_nodes`,
   `_build_observation_nodes`, `_build_dataset_nodes`,
   `_build_resource_node` — all domain-specific analogues of the PDD bridge's
   helper functions.
4. Calls `run_renderer_with_payload` with the assembled graph.

---

## 12. Shared Vocabulary — NiasTerm

`workflow_contract.dart` centralises all IRI constants in a `NiasTerm` class
(lines 9–98):

```dart
class NiasTerm {
  static const base    = 'https://nova.org.za/novaimpactaccountingstandard/';
  static const aiaoBase  = 'http://w3id.org/aiao#';
  static const claimBase = 'http://w3id.org/claimont#';
  // ...
  static const documentMessageId   = '${base}documentMessageId';
  static const finalReviewDecision = '${base}finalReviewDecision';
  static const resourceIpfsUri     = '${base}resourceIpfsUri';
  // schema version IRIs
  static const pddASchema  = '${base}document-schema/PDDxA-1.0.0';
  static const pddBSchema  = '${base}document-schema/PDDxB-9.0.0';
  static const pddCSchema  = '${base}document-schema/PDDxC-4.0.0';
  static const pddCirSchema = '${base}document-schema/PDDCIR-3.0.0';
  // placeholder identities (replace in production)
  static const project    = '${base}projects/pdd-alpha';
  static const developer  = '${base}users/project-developer-1';
  static const validator  = '${base}users/pdd-validator-1';
  static const registry   = '${base}registry/nova-registry';
  static const workflow   = '${base}workflows/pdd';
}
```

The placeholder identities at the bottom of `NiasTerm` (lines 92–97) are
**mock values**. A production integration must inject real project, user, and
registry IRIs — likely from URL parameters or an identity service.

---

## 13. Tests

### 13.1 `workflow_contract_test.dart`

Five pure-Dart unit tests covering:

- `documentSeed` shapes: verifies the nested `hasObjective`, `hasSpatialLocation`,
  `technologyOrMeasure`, `projectParty`, `hasDeclaredImpact`, `impactClaim` lists
  are present in seeds.
- Gate opens after all three sections and reviews submitted with `reviewApprove`.
- Rejected review (`reviewReject`) blocks the gate.
- `reviewSeed` emits `reviewTarget` as a list-wrapped node and does not include
  a deprecated `fieldKey` field.
- Wrong `isReviewOf` IRI blocks the gate.

### 13.2 `payload_visibility_test.dart`

One widget test verifying the payload inspector dialog:
- Is hidden until the "Open payload" icon is tapped.
- Shows `Payload` heading and a "Close payload" button when open.
- Dismisses on close.

The test sets `tester.view.physicalSize = Size(1400, 1000)` and
`devicePixelRatio = 1` to simulate a desktop browser viewport — important for
any shell that has minimum-width layout constraints.

---

## 14. Reusable Patterns for Other Workflow Shells

The following patterns can be lifted directly:

| Pattern | File | Lines | Notes |
|---|---|---|---|
| Aliased import per generated shape | `pdd_workflow_shell_app.dart` | 5–11 | One alias per shape, prevents class name collisions |
| `initial: Map<String,dynamic>` instantiation | `pdd_workflow_shell_app.dart` | 126–152 | Generated widget API; do not modify |
| `documentSeed()` factory | `workflow_contract.dart` | 399–449 | Pre-populate framework fields before form opens |
| `WorkflowArtifact` snapshot on submit | `workflow_contract.dart` | 325–337 | Captures IRI, schema, messageId, ipfsUri, payload |
| `toDocumentReference()` serializer | `workflow_contract.dart` | 259–265 | Produces `DocumentReference` node for downstream cross-refs |
| Payload inspector dialog | `pdd_workflow_shell_app.dart` | 509–562 | `JsonEncoder.withIndent('  ')` view; reuse as-is |
| `_FormSurface` dual-axis scroll wrapper | `pdd_workflow_shell_app.dart` | 345–367 | Minimum 1160 px content width |
| Role-based `canOpen` / `blockers` | `workflow_contract.dart` | 290–323 | Returns `List<String>` for UI display |
| `_StepTile` lock / check / radio icons | `pdd_workflow_shell_app.dart` | 237–257 | Visual state: locked, open, submitted |
| `export_*_markdown.py` bridge pattern | `monitoring_report/tool/` | — | Same structure: load JSON → build graph → call renderer |

---

## 15. Known Limitations

### 15.1 No live form read-back

The shell reads `_drafts[step]` only at submit time. If a user edits a form,
navigates away without submitting, and returns, the form widget is recreated
from the original seed and in-progress edits are lost. The generated
`FormWidget` holds its own internal state; the shell holds no mirror of it.

### 15.2 In-memory only — no persistence

Refreshing the browser resets all submitted artifacts. The README (lines 78–88)
explicitly designates this as the integration boundary for a future Fluree
backend. Production use must replace the in-memory `_submitted` map with
transaction calls described in `../../fluree/pdd-workflow-transactions.md`.

### 15.3 Partial gate implementation

The in-memory `gateResult()` implements only a subset of the formal gate
contract. Absent from the Dart gate:

- Stale-link detection.
- Ledger resolution of `resourceIpfsUri` / `documentMessageId`.
- The two qualitative review layers (`pddSectionQualitativeReview`,
  `pddDocumentLevelQualitativeReview`).

### 15.4 No `onChanged` callback from generated widgets

The shell cannot observe field-level changes. Progressive validation or
inter-field dependencies must be encoded inside the generated widget or handled
by a SHACL post-submit check.

### 15.5 Hard-coded placeholder identities

`NiasTerm.developer`, `NiasTerm.validator`, `NiasTerm.project`,
`NiasTerm.registry` (lines 92–97) are placeholder IRIs. A real deployment must
inject project-specific IRIs from the authentication layer or URL parameters.

### 15.6 No multi-step monitoring-report shell

The monitoring-report workflow is single-step
(`workflows/monitoring-report.yaml` lines 23–28). There is no Flutter shell
package equivalent to `pdd_workflow_shell` for it — only the standalone export
script in `monitoring_report/tool/`. Section 16 describes how to build one.

---

## 16. Applying This Pattern to the Monitoring-Report Shell

The monitoring-report UI shape bundle (`monitoring-report-ui-shapes.ttl`) defines
a single root shape, `MonitoringReportUiShape`, with ten properties:

| Property | Type | UI widget |
|---|---|---|
| `hasWorkflowSubmission` | subform (`WorkflowDocumentSubmissionUiShape`) | `ui:subform` |
| `alignedWithPDD` | `xsd:anyURI` | `ui:text` |
| `reportedIndicatorLabel` | `xsd:string` | text |
| `forPeriod` | subform (`DateTimeIntervalUiShape`) | `ui:subform` |
| `reportedObservation` | subform (`IndicatorObservationUiShape`) | `ui:subform` |
| `usesDataset` | subform (`DatasetUiShape`), 1–99 | `ui:subform` (repeating) |
| `calculationCode` | subform (`ResourceArtifactUiShape`) | `ui:subform` |
| `impactResultResource` | subform (`ResourceArtifactUiShape`) | `ui:subform` |
| `calculationReport` | subform (`ResourceArtifactUiShape`) | `ui:subform` |
| `requestedIssuanceAccountId` | `xsd:string` | text |

### 16.1 Build step

Run `dataRequirements/shape2flutter/build-monitoring-report.sh`. This produces
`MonitoringReportUiShapeFormWidget` (and supporting subform widgets) in
`/tmp/nias-shape2flutter/monitoring-report/flutter/`.

### 16.2 Import and instantiate

```dart
import '../generated/monitoringreportuishape.dart' as mr;

// in _buildForm:
return mr.MonitoringReportUiShapeFormWidget(initial: draft);
```

### 16.3 Build a `documentSeed` factory

The MR seed must pre-populate the ten fields above. The
`alignedWithPDD` field is a cross-workflow reference (IRI of the approved PDD
version) that **cannot come from the form itself** — it must be supplied
externally (e.g. via a URL parameter or a picker that resolves known PDD
artifacts from the ledger).

For the repeating `usesDataset` field, provide at least one empty `Dataset`
submap so the generated widget opens with a visible list item.

### 16.4 No gate needed for MR

The monitoring report is a single-step, single-role workflow. No gate logic
is required. A `WorkflowArtifact` should still be captured on submit so that
downstream verification and verification-report shells can cross-reference the
MR `documentMessageId` and `resourceIpfsUri`.

### 16.5 Wrap in `_FormSurface`

The `usesDataset` repeating subform with nested `DatasetUiShape`,
`DocumentReferenceUiShape`, and `ResourceArtifactUiShape` will exceed
viewport width. Use the same dual-axis scroll wrapper as the PDD shell.

### 16.6 Export bridge

Use `monitoring_report/tool/export_monitoring_report_markdown.py` directly —
it already follows the same build-graph-then-render pattern. For final-mode
export, the following CLI flags become required:

- `--artifact-content-cid`
- `--artifact-schema-cid`
- `--artifact-schema-version-label`
- `--aligned-pdd-content-cid`
- `--aligned-pdd-submission-topic-id`
- `--aligned-pdd-submission-consensus-timestamp`
- `--linked-dlr-content-cid`

---

## File Reference Index

| File | Role |
|---|---|
| `lib/main.dart` | Application entrypoint |
| `lib/src/pdd_workflow_shell_app.dart` | UI layout, routing, form embedding, payload dialog |
| `lib/src/workflow_contract.dart` | State, enums, roles, gate, seeds, NiasTerm vocabulary |
| `lib/generated/README.md` | Explains generated files are gitignored |
| `tool/prepare_pdd_workflow_shell.sh` | Builds and copies generated Dart files |
| `tool/check_pdd_workflow_shell.sh` | Runs `flutter test + analyze + build web` |
| `tool/export_pdd_workflow_markdown.py` | Export bridge: JSON payloads → JSON-LD graph → renderer |
| `test/workflow_contract_test.dart` | Gate and seed unit tests |
| `test/payload_visibility_test.dart` | Payload dialog widget test |
| `pubspec.yaml` | Flutter package descriptor (no external state packages) |
| `../pdd-workflow-ui-shapes.ttl` | SHACL shape source for generated widgets |
| `../pdd-workflow-gate.md` | Formal gate contract (superset of in-memory implementation) |
| `../build-pdd-workflow.sh` | Runs shape2flutter lint / emit-jsonld / build |
| `../check-pdd-workflow.sh` | Full local regression including shell check |
| `../monitoring-report-ui-shapes.ttl` | SHACL shape source for monitoring-report widgets |
| `../build-monitoring-report.sh` | Equivalent build script for monitoring report |
| `../monitoring_report/tool/export_monitoring_report_markdown.py` | MR export bridge |
| `../workflows/monitoring-report.yaml` | Monitoring-report workflow YAML descriptor |
