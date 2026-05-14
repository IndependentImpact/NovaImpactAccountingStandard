# Migration Path From Legacy Reference Schemas To SHACL Data Requirements

This note captures a practical migration path for turning the legacy
`reference/` JSON-LD-producing R functions into SHACL data requirements that
use the local Nova Impact Accounting Standard ontology, the local concept schemes, and the
AIA ontology suite:

- AIAO: `http://w3id.org/aiao#`
- Impact Ontology: `http://w3id.org/impactont#`
- Claim Ontology: `http://w3id.org/claimont#`
- Information Communication Ontology: `http://w3id.org/infocomm#`
- Indicator Ontology: `http://independentimpact.org/indicator-owl/`
- QUDT schema: `http://qudt.org/schema/qudt/`
- QUDT unit vocabulary: `http://qudt.org/vocab/unit/`

The current `reference/` directory contains both legacy R functions and JSON
schema-like files. The R functions show how selected legacy payloads were
converted to JSON-LD-like lists. The JSON files show the broader user-facing
document requirements that need to become SHACL shapes.

## Current Repository State

The repository already has three useful semantic layers:

- `glossary/NovaImpactAccountingStandardOntology.ttl`: local ontology terms such
  as `nias-o:PlatformUser`, `nias-o:TechnologyOrMeasure`,
  `nias-o:CreditingPeriod`, `nias-o:Workflow`,
  `nias-o:WorkflowDocumentSubmission`, document metadata predicates, and
  project or impact predicates.
- `glossary/NovaImpactAccountingStandardGlossary.ttl`: local SKOS concept schemes
  for user types, agent license scopes, authenticity proof mechanisms,
  technology or measure types, impact intentionality, beneficial/adverse
  classification, and monitoring status.
- `glossary/NovaImpactAccountingStandardShapes.ttl`: early SHACL shapes for local
  controlled vocabularies, license numbers, and IPFS URI strings.

An external indicator ontology is available at
`http://independentimpact.org/indicator-owl/` (prefix `ind:`). It provides
indicator-specific classes and properties aligned with the AIA ontology suite,
including `ind:IndicatorDefinition`, `ind:hasUnit` (pointing to QUDT units),
`ind:hasIndicatorStage`, `ind:IndicatorFormula`, `ind:IndicatorRationale`, and
the `ind:IndicatorObservation` pattern for reporting observed values. SHACL
shapes that describe indicators should import or reference this ontology where
relevant rather than inventing parallel local terms.

Status update (2026-05-14): concept scheme directories are now populated:

- ✅ `methodologies/GHGMethodologies.ttl`
- ✅ `indicators/GHGIndicators.ttl`
- ✅ `knowledgeDomains/GHGKnowledgeDomains.ttl`

The JSON files are schema arrays whose first entry is usually an object with
`title`, `description`, `properties`, `required`, `additionalProperties`, and
sometimes `allOf`.

Strict JSON parsing now passes for all JSON files under `reference/`. The
previous blockers were cleaned up in:

- `reference/#DataLineageReport4.0.0.json`
- `reference/#ImpactSummary&1.0.0.json`
- `reference/#PDDCIR&3.0.0.json`

Those fixes removed trailing commas and invalid empty top-level `context`
entries so automated JSON Schema tooling can safely consume the reference
schemas before generating SHACL.

The legacy R functions already produce JSON-LD-like structures, so the
migration should not start from a blank slate. The key shift is that those
functions should become adapters from legacy input into the canonical RDF
model, while SHACL becomes the source of truth for user-facing data
requirements.

## JSON Reference Schema Inventory

The JSON files cover more workflows than the original R adapters. Treat them as
the complete legacy data requirement inventory, with the R files acting as
partial transformation examples.

### Reusable Schemas

- `#DocumentHeaders&1.0.0`: predecessor message/IPFS references, submitter
  license references, subject ID, and subject type (`PROJECT` or `AGENT`).
- `#DateTimePeriod&1.0.0`: `datetime_start` and `datetime_end`.
- `#Methodology&1.0.0`: methodology title, label, and version.
- `#MethodologyApplicability&3.0.0`: methodology plus applicability rationale.
- `#TechnologyOrMeasure&1.0.0`: technology/measure type, description, current
  age, estimated lifespan, optional type explanation, and additional info.
- `#ProjectParty&1.0.0`: party name, host status, public/private type,
  participant status, and additional info.
- `#TableRow-DataParameterMonitoring&1.0.0`: monitored or fixed data parameter
  details for impact quantification.
- `#Dataset&1.0.0`: dataset name and approved data lineage review references.
- `#DocumentFieldReview&1.0.0`: field-level review decision and feedback.

### Project And PDD Workflow Schemas

- `#PLA&1.0.0`: project listing application.
- `#PDDxA&1.0.0`: PDD section A, project description.
- `#PDDxB&9.0.0`: PDD section B, methodologies and impacts.
- `#Impact&3.0.0`: impact declaration used inside PDD section B.
- `#PDDxC&4.0.0`: PDD section C, stakeholder engagement.
- `#PDDCIR&3.0.0`: PDD certificate issuance request.
- `#ProjectRegistrationRequest&1.0.0`: project registration request after an
  approved PDD certificate issuance request.

### Agent And License Schemas

- `#AgentDetails&1.0.0`: agent details and evidence.
- `#LicenseApplication&1.0.0`: application for project developer, PDD
  validator, or monitoring report verifier license.
- `#DR-LicenseApplication&1.0.0`: document review for license applications.
- `#IndependentImpactAgentLicense&1.0.0`: issued agent license payload.

### Review, Monitoring, Data, And Certificate Schemas

- `#GenericDocumentReview&5.0.0`: generic document review composed of field
  reviews and a final approve/reject decision.
- `#DRVICIR&1.0.0`: document review for a verified impact certificate issuance
  request.
- `#MonitoringReport&6.0.0`: monitoring report, including indicator label,
  monitoring period, datasets, calculation artifacts, impact value, unit, and
  issuance account.
- `#DataLineageReport4.0.0`: data lineage report.
- `#ImpactSummary&1.0.0`: summarized verified impact.
- `#VICIR&1.0.0`: verified impact certificate issuance request.
- `#VIC&2.0.0`: issued verified impact certificate.

## Semantic Model Decisions To Make First

### 1. Controlled Values Should Be SKOS Concept IRIs

The glossary defines values like `nias-o:beneficial`, `nias-o:intentional`,
`nias-o:yes`, and `nias-o:facility` as `skos:Concept`s. The existing SHACL
already expects concept IRIs via `sh:class skos:Concept` and `sh:in`.

Several local ontology properties are currently declared as datatype
properties with `xsd:string` ranges while the shapes expect SKOS concepts:

- `nias-o:authProof`
- `nias-o:beneficialOrAdverse`
- `nias-o:impactIntentionality`
- `nias-o:licenseScope`
- `nias-o:monitored`
- `nias-o:techMeasType`

Migration target: make these object properties, or create replacement object
properties, because the semantic representation should point to concept IRIs
rather than string labels or legacy codes.

Legacy values should be normalized through lookup tables. Examples:

- `REGULAR_UNSIGNED` or `NONE` -> `nias-o:none`
- `REGULAR_SIGNED` or `EDDSA` -> `nias-o:eddsa-signature`
- `VC` -> `nias-o:vc`
- `RENEWABLE` -> `true` for `nias-o:creditingPeriodIsRenewable`
- `counterfactual` -> the Impact Ontology literal value for state modality
- `real` -> the Impact Ontology literal value for state modality

### 2. Reports Should Become Claims, Not Only Data Records

The reference functions currently produce direct domain objects such as
`aiao:Project` and `impactont:Impact`. That is useful, but a user-submitted
document is also a claim/report made by an agent under a workflow.

Use this distinction:

- Domain graph: the project, impacts, states, indicators, technologies,
  methodologies, periods, and documents.
- Claim graph: statements that a user or agent makes about those domain
  objects.
- Workflow graph: who submitted which document to which workflow step for
  which subject.

Claim Ontology gives the required terms:

- `claimont:Report`: a claim made according to a specification.
- `claimont:Claim`: a defeasible statement.
- `claimont:isMadeBy`: links a claim/report to the claimant.
- `claimont:hasSubject`: links a claim/report to the subject.
- `claimont:isSupportedBy`: links claims to substantiation.

AIAO adds impact-specific claim classes:

- `aiao:ImpactClaim`
- `aiao:StateClaim`
- `aiao:StateProvenanceClaim`

Migration target: keep the direct domain shape for the project and impact data,
but add wrapper shapes for report/claim documents once the basic domain shapes
are stable.

### 3. Document Submission Can Later Align With InfoComm

The local ontology already has `nias-o:WorkflowDocumentSubmission`, which is
the right immediate anchor for the existing workflow metadata. The InfoComm
ontology can be added later for richer communication semantics:

- `infocomm:CommunicationEvent`: the act of submitting or transmitting a
  document.
- `infocomm:hasSender`: the submitting platform user.
- `infocomm:hasRecipient`: the platform, registry, workflow endpoint, or
  receiving agent.
- `infocomm:transmits`: the document or report.
- `infocomm:hasFormat`: JSON-LD, PDF, CSV, or other document format.
- `infocomm:hasMedium`: IPFS, Hedera Consensus Service, web upload, or another
  medium.

Recommendation: do not force InfoComm into the first SHACL milestone. First
stabilize `nias-o:WorkflowDocumentSubmission`; then add an optional InfoComm
profile.

## Reference Artifact Inventory

This section records how the legacy JSON schemas and R transformation examples
map into target RDF and SHACL. Where the JSON schema and R adapter disagree,
prefer the JSON schema for user-facing required fields and prefer the R adapter
only as evidence of intended RDF modeling.

### Project Design Document A

Sources:

- `reference/#PDDxA&1.0.0.json`
- `reference/sPDDxA_1x0x0_toFluree.R`

Legacy input fields:

- `headers`
- `headers$id_subject`
- `title_project`
- `purpose_project`
- `location_project[]`
- `techmeas_project[]`
- `parties_project[]`
- `eligibility_project`
- `legal_matters`
- `status_public_funding`
- `source_public_funding[]`
- `history_project`
- `debundling`

Current RDF output:

- `@id` -> `nias-o:activities/{id_subject}`
- `@type` -> `aiao:Project`
- `nias-o:title`
- `aiao:hasObjective`
- `nias-o:locationShapefile`
- `nias-o:technologyOrMeasure`
- `nias-o:projectHistory`

Additional JSON-only requirements:

- `parties_project`
- `legal_matters`
- `status_public_funding`
- `debundling`

The JSON schema also contains optional `eligibility_project` and conditional
`source_public_funding` when `status_public_funding` is `YES`.

Target SHACL shape:

- `ProjectDesignShape`, target class `aiao:Project`.
- Require a stable IRI for the project subject.
- Require exactly one title.
- Require at least one objective (`aiao:hasObjective`).
- Allow one or more location resources, each with an IPFS URI or equivalent
  resource content/location.
- Require one or more technologies or measures if the workflow depends on
  project implementation details.
- Require one or more project parties or participants.
- Require legal matters, public funding status, project history, and
  debundling text if these remain mandatory in the migrated standard.
- Require project history if it remains mandatory in the legacy form.
- If public funding status is `nias-o:yes`, require at least one public funding
  source. This will need a local concept scheme or property for public funding
  status if it should not reuse the generic yes/no monitoring concept.

Use `aiao:hasObjective` for project purpose, with `aiao:Objective` as the
value. The local `nias-o:purpose` property has been removed in favour of this
AIAO predicate in line with the semantic web principle of reusing existing
vocabulary rather than duplicating it.

Open modeling question: project parties probably need a local class such as
`nias-o:ProjectParty` or should be represented as `aiao:AgentActivityRelation`
nodes linking `aiao:Agent`s to the project with role/status controls. Avoid
leaving them as anonymous strings if they are used for accountability.

### Technology Or Measure

Sources:

- `reference/#TechnologyOrMeasure&1.0.0.json`
- `reference/sTechnologyOrMeasure_1x0x0_toFluree.R`

Legacy input fields:

- `type_techmeas`
- `type_techmeas_otherexplain`
- `description`
- `age_current`
- `lifespan_estimated`
- `info_additional`

Current RDF output:

- `@type` -> `nias-o:TechnologyOrMeasure`
- `nias-o:techMeasType`
- `schema:description`
- `nias-o:currentAgeInYears`
- `nias-o:estimatedLifespanInYears`

Target SHACL shape:

- `TechnologyOrMeasureShape`, target class `nias-o:TechnologyOrMeasure`.
- `nias-o:techMeasType` must be an IRI from `nias-o:TechMeasType`.
- `schema:description` should be a required string unless the ontology gets a
  local description property.
- `nias-o:currentAgeInYears` and `nias-o:estimatedLifespanInYears` are
  required in the JSON schema and should be decimals with minimum value `0`.
- `nias-o:additionalInfo` can carry `info_additional`.
- If `nias-o:techMeasType` is `nias-o:other`, require
  `type_techmeas_otherexplain` mapped to `nias-o:additionalInfo` or a more
  specific local explanation property.
- If both ages are present, current age should not exceed estimated lifespan.
  That check needs a SHACL-SPARQL constraint.

### Project Design Document B / Impact Declaration

Sources:

- `reference/#PDDxB&9.0.0.json`
- `reference/#Impact&3.0.0.json`
- `reference/#MethodologyApplicability&3.0.0.json`
- `reference/#TableRow-DataParameterMonitoring&1.0.0.json`
- `reference/sPDDxB_9x0x0_toFluree.R`
- `reference/sImpact_3x0x0_toFluree.R`
- `reference/state_toFluree.R`
- `reference/indicator_toFluree.R`
- `reference/creditingPeriod_toFluree.R`
- `reference/dateTimePeriod_toFluree.R`
- `reference/dateTimeInstant_toFluree.R`
- `reference/sMethodology_1x0x0_toFluree.R`

Legacy input fields:

- `impacts[]`
- `intentionality`
- `beneficial_or_adverse`
- `description`
- `monitored`
- `not_monitored_justification`
- `indicator`
- `additionality`
- `indicator_label`
- `indicator_unit_of_measure`
- `data_and_parameters[]`
- `state_baseline`
- `state_project`
- `impact_estimation_ex_ante`
- `crediting_period$datetime_start`
- `crediting_period$datetime_end`
- `crediting_period_type`
- `monitoring_periods[]$datetime_start`
- `monitoring_periods[]$datetime_end`
- `methodologies[]$methodology$title`
- `methodologies[]$methodology$label`
- `methodologies[]$methodology$version`

Current RDF output:

- `@type` -> `impactont:Impact`
- `nias-o:impactIntentionality`
- `nias-o:beneficialOrAdverse`
- `schema:description`
- `nias-o:monitored`
- `nias-o:notMonitoredJustification`
- `nias-o:additionalityJustification`
- `impactont:hasStateA`
- `impactont:hasStateB`
- `impactont:hasProvenance`
- `nias-o:monitoringPeriod`
- `nias-o:creditingPeriod`
- `nias-o:indicatorMethodology`

Additional JSON-only requirements:

- `data_and_parameters` references
  `#TableRow-DataParameterMonitoring&1.0.0`.
- `impact_estimation_ex_ante` captures the expected ex-ante impact quantity
  for the first crediting period.
- `indicator` is a free-text indicator description separate from
  `indicator_label` and `indicator_unit_of_measure`.

Target SHACL shape:

- `ImpactRequirementShape`, target class `impactont:Impact`.
- Require intentionality, beneficial/adverse classification, description, and
  monitoring status.
- If `nias-o:monitored` is `nias-o:no`, require
  `nias-o:notMonitoredJustification` and do not require states, monitoring
  periods, crediting period, or methodology.
- If `nias-o:monitored` is `nias-o:yes`, require:
  - `nias-o:additionalityJustification`
  - exactly one `impactont:hasStateA`
  - exactly one `impactont:hasStateB`
  - at least one provenance event, normally the project or activity
  - exactly one crediting period
  - one or more monitoring periods
  - one or more methodologies from the methodology concept scheme
  - one or more data/parameter monitoring rows if these are part of the
    migrated PDD-B requirements
  - an ex-ante impact estimate if this remains required for project validation

Open modeling issue: `nias-o:indicatorMethodology` is used by the R function
but is not defined in the local ontology. Add a property such as
`nias-o:usesMethodology`, or use an existing control relation such as
`aiao:isGovernedBy` or `aiao:governs` once the direction is decided.

Open implementation issue: the R function checks
`not_monitored_justifcation` but then reads `not_monitored_justification`. The
misspelled field name should not be carried into SHACL.

Open JSON schema issue: `#Impact&3.0.0.json` expresses monitored/unmonitored
branches with `allOf`, but both branch `required` arrays are empty. If those
fields are genuinely mandatory, SHACL should be stricter than the current JSON
schema and the JSON schema should be corrected during migration.

Open JSON schema issue: the `data_and_parameters` `$ref` appears twice with
different spellings: `#TableRow-DataParameterMonitoring&1.0.0` and
`#(Table Row: Data/Parameter Monitoring)&1.0.0`. Normalize this to the actual
file name.

### Data Or Parameter Monitoring Row

Source: `reference/#TableRow-DataParameterMonitoring&1.0.0.json`

Legacy input fields:

- `label`
- `unit_of_measure`
- `description`
- `purpose`
- `monitored_or_fixed`
- `value_applied`
- `data_source`
- `measurement_methods_and_procedures`
- `qa_qc_procedures`
- `monitoring_frequency`
- `sampling_plan`

Target SHACL shape:

- `DataParameterMonitoringShape`, probably a local class such as
  `nias-o:DataParameterRequirement` unless a suitable external class is chosen.
- Require label, unit of measure, description, purpose, and monitored/fixed
  status.
- Model `unit_of_measure` as `ind:hasUnit` pointing to a `qudt:Unit` IRI rather
  than a free-text string. Accept a plain string only as a legacy fallback and
  flag it as a migration warning.
- Model `monitored_or_fixed` as a SKOS concept scheme with concepts for
  monitored and fixed ex-ante.
- If fixed ex-ante, require the applied value and data source.
- If monitored, require measurement methods/procedures, QA/QC procedures,
  monitoring frequency, and sampling plan if these are semantically mandatory.

Open JSON schema issue: the conditional branches in this schema also use empty
`required` arrays. The migration should decide whether the branch-specific
fields are truly optional or whether the JSON schema under-specifies the old
workflow.

### State

Source: `reference/state_toFluree.R`

Current RDF output:

- `@type` -> `impactont:State`
- `impactont:hasTemporalLocation`
- `impactont:hasModality`
- `impactont:isDefinedByIndicator`
- `impactont:hasValue`

Target SHACL shape:

- `StateShape`, target class `impactont:State`.
- Require exactly one temporal location.
- Require exactly one modality with value `counterfactual` or `real`.
- Require exactly one indicator.
- Require an indicator value when the form asks for a measured or projected
  value.

Open modeling issue: `impactont:hasValue` does not exist in the fetched Impact
Ontology. The ontology defines `impactont:IndicatorValue` and
`impactont:hasIndicatorValue`, with the actual value expected on `rdf:value`.
New SHACL should use:

```turtle
impactont:hasIndicatorValue [
  a impactont:IndicatorValue ;
  rdf:value "..."^^xsd:decimal
] .
```

The adapter can keep accepting the legacy `state_baseline` and `state_project`
fields, but it should emit the canonical indicator value structure.

### Time Instant, Time Period, And Crediting Period

Sources:

- `reference/dateTimeInstant_toFluree.R`
- `reference/dateTimePeriod_toFluree.R`
- `reference/creditingPeriod_toFluree.R`

Current RDF output:

- `time:Instant`
- `time:Interval`
- `time:hasBeginning`
- `time:hasEnd`
- `time:inXSDDateTimeStamp`
- `nias-o:CreditingPeriod`
- `nias-o:creditingPeriodIsRenewable`

Target SHACL shapes:

- `DateTimeInstantShape`
- `DateTimeIntervalShape`
- `CreditingPeriodShape`

Required checks:

- Beginning and end must each be present for intervals.
- Date-time values should be `xsd:dateTimeStamp`.
- End must be later than beginning. This needs SHACL-SPARQL.
- Crediting period must include the renewable boolean.
- Monitoring periods should be contained within the crediting period. This also
  needs SHACL-SPARQL and can be deferred until the core data shape validates.

Open modeling issue: Impact Ontology ranges `impactont:hasTemporalLocation` to
`impactont:TemporalLocation`, while the R functions emit OWL-Time nodes
directly. Decide whether to:

- type the temporal node as both `impactont:TemporalLocation` and the OWL-Time
  class, or
- define local SHACL that accepts OWL-Time `time:Instant` and `time:Interval`
  as temporal locations.

### Indicator

Source: `reference/indicator_toFluree.R`

Current RDF output:

- `@type` -> `impactont:Indicator`
- `rdfs:label`
- `nias-o:unitOfMeasure`

Target model:

- Indicators should live in `indicators/` as stable resources.
- Each indicator should be typed as `ind:IndicatorDefinition`, which is a
  subclass of both `impactont:Indicator` and `infocomm:Information`. Indicators
  that are not yet formally defined may also be typed as plain
  `impactont:Indicator` until they gain a canonical definition.
- If the platform wants indicators selectable in UIs, also type each one as
  `skos:Concept` and place it in an indicator concept scheme.
- Replace `nias-o:unitOfMeasure` (a plain string) with `ind:hasUnit` pointing
  to a `qudt:Unit` IRI from the QUDT unit vocabulary. Examples:
  - carbon dioxide equivalent tonnes: `unit:T_CO2e` or the appropriate QUDT IRI
  - kilowatt-hours: `unit:KiloW-HR`
  - hectares: `unit:HA`

  Keep a UCUM code on the unit individual for machine-to-machine exchange, as
  recommended in the indicator ontology.
- Use `ind:hasIndicatorStage` to classify indicators according to their position
  in a theory of change. Values come from `ind:IndicatorStageScheme`:
  `ind:ActivityIndicator`, `ind:OutputIndicator`, `ind:OutcomeIndicator`, or
  `ind:ImpactIndicator`.
- Use `ind:hasFormula` with an `ind:IndicatorFormula` resource if the indicator
  has a computation method that should be recorded alongside the definition.
  The formula node may carry `ind:expressionText` and optionally
  `ind:mathTextRepresentationType` (one of `"LaTeX"`, `"AsciiMath"`, or
  `"ContentMathML"`).
- Use `ind:hasRationale` with an `ind:IndicatorRationale` resource to carry the
  narrative justification for why the indicator is relevant to the objective or
  state being monitored.
- The SHACL requirement should prefer `impactont:isDefinedByIndicator` pointing
  to a known `ind:IndicatorDefinition` IRI.
- For observed/reported indicator values, use `ind:IndicatorObservation` in
  addition to `impactont:IndicatorValue`. The `ind:obsValue` datatype property
  records the decimal value and `ind:hasUnit` records the QUDT unit. Link the
  observation to its indicator definition via `ind:observesIndicator`.
- For legacy free-text indicators, mint draft indicator IRIs and route them
  through curation instead of embedding one-off blank indicator nodes forever.

### Methodology

Source: `reference/sMethodology_1x0x0_toFluree.R`

Current RDF output:

- `@type` -> `nias-o:Methodology`
- `dcterms:title`
- `rdfs:label`
- `data:versionTag`

Target model:

- Methodologies should live in `methodologies/` as stable resources.
- Each methodology can be both `nias-o:Methodology` and `skos:Concept` if it
  needs to be selected from a concept scheme.
- Versioning should be explicit. If `data:versionTag` is retained, normalize
  the `data:` namespace because the local ontology uses
  `https://jellyfiiish.xyz/ns/`, while reference functions use
  `http://jellyfiiish.xyz/ns/`.
- Shapes for impact declarations should point to methodology IRIs rather than
  embedding methodology title/label/version objects in each submission.

### Agent Details

Sources:

- `reference/#AgentDetails&1.0.0.json`
- `reference/sAgentDetails_1x0x0_toFluree .R`

Legacy input fields:

- `headers`
- `agentId`
- `id_acc_h`
- `initials`
- `name_first`
- `name_last`
- `date_of_birth`
- `country`
- `supporting_evidence_pp1`
- `supporting_evidence_pp2`
- `email_address`
- `supporting_evidence_email`
- `contact_number`
- `supporting_evidence_contact_no`

Current RDF output:

- `@type` -> `aiao:Agent`, `nias-o:PlatformUser`
- `@id` -> `nias-o:agents/{agentId}`
- `schema:givenName`
- `schema:familyName`
- `schema:birthDate`
- `schema:nationality`

Additional JSON-only requirements:

- `headers`
- `id_acc_h`
- `initials`
- `email_address`
- supporting evidence fields for personal particulars, email address, and
  contact number

Only `headers`, `id_acc_h`, `initials`, `name_last`, `date_of_birth`,
`country`, and `email_address` are required by the JSON schema.

Target SHACL shape:

- `PlatformUserShape`, target class `nias-o:PlatformUser`.
- Require a stable agent IRI.
- Require a Hedera account identifier or account-link node if agent onboarding
  still depends on account linkage.
- Require given name and family name if natural-person users remain in scope.
  The JSON schema currently requires `name_last` but not `name_first`.
- Use `xsd:date` for birth date.
- Represent nationality as a country code concept or IRI if the system needs
  cross-jurisdiction interoperability. A string can be accepted during the
  first migration phase.
- Represent email address and supporting evidence either as document/resource
  links or as claims with substantiation.

### License Application And Agent License

Sources:

- `reference/#LicenseApplication&1.0.0.json`
- `reference/#DR-LicenseApplication&1.0.0.json`
- `reference/#IndependentImpactAgentLicense&1.0.0.json`

Legacy input fields:

- `headers`
- `license`
- `id_acc_h`
- `final_rd`
- `commentary_r`
- `id_msg_drad`
- `url_ipfs_drad`
- `did_licensee`
- `email_address`
- `scope`
- `license_number`

Target SHACL shapes:

- `LicenseApplicationShape` for applications by agents.
- `LicenseApplicationReviewShape` for approval/rejection review records.
- `AgentLicenseShape` for issued license credentials or license payloads.
- Map `PROJECT_DEVELOPER`, `PDD_VALIDATOR`, and `MR_VERIFIER` to
  `nias-o:project-developer`, `nias-o:pdd-validator`, and
  `nias-o:mr-verifier`.
- Reuse or extend `nias-o:LicenseNumberShape` for `license_number`.
- Use `nias-o:hasAgentLicense`, `nias-o:licenseScope`, and
  `nias-o:licenseNumber` for issued license data.

Open modeling issue: `#IndependentImpactAgentLicense&1.0.0.json` allows
`scope` as an array, while the current `licenseScopeShape` has `sh:maxCount 1`.
Decide whether a license can have multiple scopes or whether one license
resource must be minted per scope.

### Document Reviews

Sources:

- `reference/#GenericDocumentReview&5.0.0.json`
- `reference/#DocumentFieldReview&1.0.0.json`
- `reference/#DRVICIR&1.0.0.json`

Legacy input fields:

- `headers`
- `review[]`
- `final_rd`
- `field_key`
- `field_title`
- `field_prompt`
- `original_response`
- `reviewer_decision`
- `reviewer_feedback`
- `id_acc_h`

Target SHACL shapes:

- `DocumentReviewShape`, probably a `claimont:Attestation` or a local subclass
  of `claimont:Attestation`.
- `DocumentFieldReviewShape` for field-level findings.
- Represent final decisions and field decisions as SKOS concepts rather than
  string enums. Existing enum values are `APPROVE`, `REJECT`,
  `FORWARD_ACTION_REQUEST`, and `CORRECTIVE_ACTION_REQUEST`.
- Use `claimont:hasSubject` to point the review/attestation to the reviewed
  document or claim.
- Use `claimont:isMadeBy` for the reviewer/attester.
- Use `claimont:supports` or `claimont:isSupportedBy` where a review supports
  the issuance of a certificate/license or the acceptance of a report.

Open modeling issue: the old review payload stores field prompts and original
responses as copied strings. The semantic target should preferably point to the
reviewed document, field path, and reviewed value, with copied strings retained
only for audit snapshots.

### Project Listing, PDD Certificate, And Project Registration

Sources:

- `reference/#PLA&1.0.0.json`
- `reference/#PDDCIR&3.0.0.json`
- `reference/#ProjectRegistrationRequest&1.0.0.json`

Legacy input fields:

- `title_project`
- `location_project`
- `purpose_project`
- `id_msg_pred_drxa`
- `url_ipfs_pred_drxa`
- `id_msg_pred_drxb`
- `url_ipfs_pred_drxb`
- `id_msg_pred_drxc`
- `url_ipfs_pred_drxc`
- `id_msg_pred_drcir`
- `url_ipfs_pred_drcir`
- `id_acc_h`

Target SHACL shapes:

- `ProjectListingApplicationShape` for the early listing request.
- `PddCertificateIssuanceRequestShape` for proving PDD section reviews have
  approved sections A, B, and C.
- `ProjectRegistrationRequestShape` for registration after approved PDD
  certificate issuance.
- Model predecessor message/IPFS references as document or submission links,
  not just string fields, once Hedera message IDs and IPFS resources have
  canonical shapes.
- Use `nias-o:WorkflowDocumentSubmission` to tie each request to the workflow
  step and project subject.

### PDD Section C Stakeholder Engagement

Source: `reference/#PDDxC&4.0.0.json`

Legacy input fields:

- `headers`
- `modalities`
- `summary_comments`
- `consideration_comments`

Target SHACL shape:

- `StakeholderEngagementShape` or `PddSectionCShape`.
- Require consultation modalities.
- Optionally require comment summary and consideration of comments if the
  standard treats these as mandatory after consultation has occurred.
- Consider whether stakeholder engagement is best modeled as an
  `aiao:Control`, `claimont:Report`, or both.

### Monitoring Report, Dataset, And Data Lineage

Sources:

- `reference/#MonitoringReport&6.0.0.json`
- `reference/#Dataset&1.0.0.json`
- `reference/#DataLineageReport4.0.0.json`
- `reference/sMonitoringReport_6x0x0_toFluree.R`

Legacy input fields:

- `indicator_label`
- `monitoring_period`
- `datasets[]`
- `ipfs_uri_rmd_calculation`
- `ipfs_uri_impact`
- `ipfs_uri_report_calculation`
- `value_impact`
- `unit_impact`
- `id_acc_h`
- `name_dataset`
- `id_msg_drdlr`
- `uri_ipfs_drdlr`
- `uri_ipfs_dataset_final`
- `uri_ipfs_data_raw`
- `uri_ipfs_report_transfer`
- `uri_ipfs_rmd_transfer`
- `uri_ipfs_data_final`
- `uri_ipfs_rmd_cleaning`
- `uri_ipfs_report_cleaning`

Target SHACL shapes:

- `MonitoringReportShape` as a `claimont:Report` describing measured impact
  for a monitoring period.
- `DatasetShape` for datasets used in impact calculations.
- `DataLineageReportShape` for provenance of raw, transferred, cleaned, and
  final datasets.
- Require the monitoring period, dataset references, calculation code/report
  IPFS resources, impact result resource, numeric impact value, unit, and
  issuance account.
- Use `ind:hasUnit` pointing to a `qudt:Unit` IRI for `unit_impact` rather than
  a bare string. This aligns the monitoring report with the indicator ontology
  unit-of-measure pattern used in indicator definitions.
- Use `ind:IndicatorObservation` to carry the observed impact value: link it to
  the indicator definition via `ind:observesIndicator`, record the decimal value
  via `ind:obsValue`, and record the unit via `ind:hasUnit`. Attach it to the
  monitoring period via `ind:timePeriod` and to the monitoring report via
  `ind:reportsObservation`.
- Link the measured impact to `impactont:Impact`, `impactont:State`, and
  `impactont:IndicatorValue` rather than treating `value_impact` as a detached
  number.
- Consider using `claimont:isSupportedBy` from the monitoring report to data
  lineage reports, datasets, RMD calculation files, and calculation reports.
- Consider using InfoComm later for publication/transmission events involving
  IPFS and Hedera.

### Verified Impact Certificate And Issuance Request

Sources:

- `reference/#VICIR&1.0.0.json`
- `reference/#VIC&2.0.0.json`
- `reference/#ImpactSummary&1.0.0.json`

Legacy input fields:

- `id_msg_pred_drmr`
- `url_ipfs_pred_drmr`
- `summary_impact`
- `id_acc_h`
- `indicator_impact`
- `unit_impact`
- `extent_impact`
- `period_impact`
- `id_msg_drmr`
- `uri_ipfs_drmr`
- `certificate_number`

Target SHACL shapes:

- `VerifiedImpactCertificateIssuanceRequestShape`.
- `VerifiedImpactCertificateShape`, likely as a `vcdm:VerifiableCredential` or
  local subclass if the certificate will be issued as a credential.
- `ImpactSummaryShape` for summarized impact values used in issuance requests.
- Link certificates to approved monitoring report reviews, measured impacts,
  impact period, unit, extent, certificate number, and issuance account.
- Reuse the same measured impact model used by monitoring reports to avoid
  certificate-specific duplicate impact semantics.

### Workflow Document Metadata

Sources:

- `reference/#DocumentHeaders&1.0.0.json`
- `reference/workflowDocumentMetadata_toFluree.R`

Legacy input fields:

- `id_msg_pred`
- `url_ipfs_pred`
- `id_msg_lic`
- `url_ipfs_lic`
- `id_subject`
- `type_subject`
- `id`
- `uri_ipfs`
- `id_schema`
- `encrypted`
- `did_author`
- `type_doc`
- `id_workflow`
- `step_workflow`
- `id_entity`
- `id_message_h`

Current RDF output:

- `@type` -> `data:Document`
- `nias-o:resourceIpfsUri`
- `nias-o:documentSchema`
- `nias-o:isEncrypted`
- `nias-o:documentAuthor`
- `nias-o:authProof`
- `nias-o:hasWorkflowSubmission`
- `nias-o:workflow`
- `nias-o:workflowStep`
- `nias-o:workflowSubject`
- `nias-o:workflowDocumentSubmissionHederaMessageId`

Additional JSON header fields:

- predecessor message and IPFS references
- submitter license message and IPFS references
- subject ID and subject type

The JSON schema does not require any header fields, but most workflow-specific
document schemas require the `headers` object itself.

Target SHACL shapes:

- `DocumentShape`, target class `data:Document`.
- `WorkflowDocumentSubmissionShape`, target class
  `nias-o:WorkflowDocumentSubmission`.
- Require IPFS URI or another resolvable content location.
- Require document schema.
- Require encryption status.
- Require document author.
- Require authenticity proof as a SKOS concept IRI.
- Require workflow, workflow step, workflow subject, and Hedera message ID when
  the document has entered a workflow.
- Use predecessor and license references to enforce workflow sequence where a
  later document depends on a prior document or a submitter license.

Open modeling issue: `nias-o:workflowDocumentSubmissionHederaMessageId` is an
object property in the ontology, but the R function emits a literal string.
Either model Hedera message IDs as resources consistently, or change this
property to a datatype property with a strict pattern.

## Proposed SHACL File Structure

Use `dataRequirements/` for the authoritative data requirement shapes:

```text
dataRequirements/
  common-shapes.ttl
  document-shapes.ttl
  project-design-shapes.ttl
  impact-declaration-shapes.ttl
  monitoring-report-shapes.ttl
  review-shapes.ttl
  license-shapes.ttl
  certificate-shapes.ttl
  data-lineage-shapes.ttl
  legacy-field-map.ttl
  shacl-migration-path.md
```

Suggested responsibilities:

- `common-shapes.ttl`: reusable shapes for SKOS concept properties, IPFS
  resources, date-time instants, date-time intervals, indicator values, and
  controlled vocabulary checks.
- `document-shapes.ttl`: document metadata and workflow submission shapes.
- `project-design-shapes.ttl`: PDD-A project, objective, location, and
  technology/measure shapes.
- `impact-declaration-shapes.ttl`: PDD-B impact, state, indicator, methodology,
  monitoring period, and crediting period shapes.
- `monitoring-report-shapes.ttl`: measured impact/report shapes once the
  monitoring report migration is designed.
- `review-shapes.ttl`: generic and specialized document review shapes,
  including field-level review nodes.
- `license-shapes.ttl`: license application, license review, and issued agent
  license shapes.
- `certificate-shapes.ttl`: PDD certificate request, VIC issuance request, and
  issued VIC shapes.
- `data-lineage-shapes.ttl`: dataset and data lineage report shapes.
- `legacy-field-map.ttl`: machine-readable mapping from old field paths to RDF
  predicates and node shapes.

## SHACL Authoring Patterns

### Controlled Concept Property

Use this pattern for local vocabularies:

```turtle
[
  sh:path nias-o:beneficialOrAdverse ;
  sh:nodeKind sh:IRI ;
  sh:class skos:Concept ;
  sh:in ( nias-o:beneficial nias-o:adverse ) ;
  sh:minCount 1 ;
  sh:maxCount 1 ;
] .
```

If the data graph will not include the SKOS concept triples during validation,
drop `sh:class skos:Concept` and rely on `sh:in`, or ensure validation loads
the glossary graph as the shapes/ontology graph.

### Conditional Monitored Impact

Represent the monitored/unmonitored branches with `sh:or` first. Add
SHACL-SPARQL only if the simple branch shape cannot express the needed rule.

```turtle
nias-o:ImpactRequirementShape
  a sh:NodeShape ;
  sh:targetClass impactont:Impact ;
  sh:property [
    sh:path nias-o:monitored ;
    sh:in ( nias-o:yes nias-o:no ) ;
    sh:minCount 1 ;
    sh:maxCount 1 ;
  ] ;
  sh:or (
    nias-o:MonitoredImpactShape
    nias-o:UnmonitoredImpactShape
  ) .
```

### Versioned Document Schema As Shape Link

Every legacy schema version should become a document schema resource that points
to its validating shape:

```turtle
<https://nova.org.za/novaimpactaccountingstandard/document-schema/PDDxA-1.0.0>
  a nias-o:DocumentSchema ;
  dcterms:title "Project Design Document A 1.0.0" ;
  sh:targetClass aiao:Project ;
  nias-o:validatingShape nias-o:ProjectDesignShape .
```

`nias-o:validatingShape` does not exist yet. Add it only if this pattern is
accepted. Otherwise use `dcterms:conformsTo` from the document schema resource
to the shape resource.

### Indicator Definition With Unit Of Measure

Use the indicator ontology to constrain indicator resources in
`impact-declaration-shapes.ttl` and `common-shapes.ttl`. The prefix declarations
needed are:

```turtle
@prefix ind:   <http://independentimpact.org/indicator-owl/> .
@prefix qudt:  <http://qudt.org/schema/qudt/> .
@prefix unit:  <http://qudt.org/vocab/unit/> .
```

A minimal shape for a canonical indicator definition:

```turtle
nias-o:IndicatorDefinitionShape
  a sh:NodeShape ;
  sh:targetClass ind:IndicatorDefinition ;
  sh:property [
    sh:path rdfs:label ;
    sh:datatype xsd:string ;
    sh:minCount 1 ;
  ] ;
  sh:property [
    sh:path ind:hasUnit ;
    sh:nodeKind sh:IRI ;
    sh:class qudt:Unit ;
    sh:minCount 1 ;
    sh:maxCount 1 ;
    sh:message "Each indicator definition must declare exactly one QUDT unit via ind:hasUnit." ;
  ] ;
  sh:property [
    sh:path ind:hasIndicatorStage ;
    sh:nodeKind sh:IRI ;
    sh:class skos:Concept ;
    sh:in (
      ind:ActivityIndicator
      ind:OutputIndicator
      ind:OutcomeIndicator
      ind:ImpactIndicator
    ) ;
    sh:maxCount 1 ;
  ] .
```

A shape for an indicator observation (reported measured value):

```turtle
nias-o:IndicatorObservationShape
  a sh:NodeShape ;
  sh:targetClass ind:IndicatorObservation ;
  sh:property [
    sh:path ind:observesIndicator ;
    sh:nodeKind sh:IRI ;
    sh:class ind:IndicatorDefinition ;
    sh:minCount 1 ;
    sh:maxCount 1 ;
  ] ;
  sh:property [
    sh:path ind:obsValue ;
    sh:datatype xsd:decimal ;
    sh:minCount 1 ;
    sh:maxCount 1 ;
  ] ;
  sh:property [
    sh:path ind:hasUnit ;
    sh:nodeKind sh:IRI ;
    sh:class qudt:Unit ;
    sh:minCount 1 ;
    sh:maxCount 1 ;
  ] .
```

If the data graph will not include the QUDT ontology triples during validation,
drop `sh:class qudt:Unit` and rely on `sh:nodeKind sh:IRI` alone, or load the
QUDT schema graph alongside the shapes graph.

## Migration Phases

### Phase 0: Freeze And Inventory Legacy Inputs

Goal: make the migration auditable.

Actions:

- Freeze the current `reference/` scripts as legacy adapters.
- Extract every legacy input field path, output RDF predicate, expected
  datatype, cardinality, and conditional rule into a table.
- Store the result as `dataRequirements/legacy-field-map.ttl` or a CSV that can
  later be converted to TTL.
- Create minimal JSON-LD fixtures for each reference function branch:
  monitored impact, unmonitored impact, project design, technology/measure,
  agent details, document metadata, and time periods.

### Phase 1: Normalize Namespaces And Value Semantics

Goal: prevent parallel vocabularies from entering production data.

Actions:

- Maintain the canonical external prefixes already used locally:
  `http://w3id.org/aiao#`, `http://w3id.org/impactont#`,
  `http://w3id.org/claimont#`, and `http://w3id.org/infocomm#`.
- Keep local ontology, shapes, concept schemes, adapters, and fixtures aligned
  to those prefixes.
- Decide whether controlled value properties are object properties to
  `skos:Concept`s. This is the recommended path. ✅ completed
- Add missing local properties or choose external properties for:
  - methodology used by an impact or impact calculation
  - shape associated with a document schema
  - Hedera message ID representation
  - document format and content location if IPFS is not the only medium
- Normalize `data:` namespace usage.

### Phase 2: Build Concept Schemes

Goal: make selectable values resolvable and reusable.

Actions:

- Populate `methodologies/` with methodology resources. ✅ completed
- Populate `indicators/` with indicator resources. Type each indicator as
  `ind:IndicatorDefinition` (a subclass of `impactont:Indicator`) and attach
  `ind:hasUnit` pointing to a `qudt:Unit` IRI from the QUDT unit vocabulary.
  Use `ind:hasIndicatorStage` to classify each indicator using a concept from
  `ind:IndicatorStageScheme`. ✅ completed
- Populate `knowledgeDomains/` with knowledge domain resources for reputation
  requirements. ✅ completed
- For UI-selectable resources, type them as both domain resources and
  `skos:Concept`s. ✅ completed
- Add `skos:inScheme`, `skos:prefLabel`, `skos:definition`, version metadata,
  and deprecation metadata where relevant.

### Phase 3: Author Core SHACL Shapes

Goal: encode the data the user must provide, independent of legacy R code.

Actions:

- Create common node shapes for:
  - IPFS resources
  - OWL-Time instant and interval
  - crediting period
  - SKOS concept values
  - technology or measure
  - state and indicator value
  - `ind:IndicatorDefinition` with `ind:hasUnit` (QUDT), `ind:hasIndicatorStage`,
    and optional `ind:hasFormula` and `ind:hasRationale`
  - `ind:IndicatorObservation` with `ind:obsValue`, `ind:hasUnit`,
    `ind:observesIndicator`, and `ind:timePeriod`
- Create project design shapes from PDD-A.
- Create impact declaration shapes from PDD-B.
- Create document metadata and workflow submission shapes.
- Keep shapes open by default during migration. Use `sh:closed true` only for
  narrow nested nodes where unknown fields would signal a real data issue.

### Phase 4: Convert R Functions Into Compatibility Adapters

Goal: keep old inputs working while making SHACL authoritative.

Actions:

- Replace hard-coded string outputs for controlled values with SKOS IRIs.
- Emit canonical namespace IRIs.
- Emit `impactont:hasIndicatorValue` instead of `impactont:hasValue`.
- Replace `nias-o:unitOfMeasure` string literals with `ind:hasUnit` links to
  `qudt:Unit` IRIs.
- Replace embedded ad hoc methodologies and indicators with links to stable
  local concept resources where possible.
- Keep a legacy-to-canonical mapping table so old API payloads can still be
  transformed without leaking old field names into new shapes.
- Run SHACL validation after adapter output generation.

### Phase 5: Add Claim And Report Wrappers

Goal: distinguish the underlying impact data from a user-submitted assertion.

Actions:

- Model PDD and monitoring report content as `claimont:Report` instances.
- Use `claimont:isMadeBy` for the reporting user/agent.
- Use `claimont:hasSubject` to point to the project, impact, state, or document
  being claimed.
- Use `aiao:ImpactClaim`, `aiao:StateClaim`, and
  `aiao:StateProvenanceClaim` for claim-level decomposition where needed.
- Link document metadata to report content through a clear property, for
  example `data:resourceContent`, `dcterms:hasPart`, or a local property if the
  data ontology already defines one.

### Phase 6: Design Monitoring Report Shapes

Goal: close the gap left by `sMonitoringReport_6x0x0_toFluree.R`.

The monitoring report TODO asks whether report contents should be packaged as
`impactont:Impact` and how to distinguish projected ex-ante impacts from
measured impacts.

Recommendation:

- Use the same `impactont:Impact` pattern for the measured impact.
- Use report/claim context to distinguish ex-ante projection from ex-post
  measurement.
- Add a local SKOS concept scheme for report or estimate status if needed,
  e.g., `projected`, `measured`, `verified`, `revised`.
- Require measured states and indicator values in monitoring report shapes.
- Link measured impacts back to the project, monitoring period, methodology,
  supporting documents, and verification attestation.

### Phase 7: Validation And Cutover

Goal: make the migration measurable and reversible.

Actions:

- Validate fixtures with pySHACL or an equivalent SHACL engine.
- Validate with ontology and concept scheme graphs loaded.
- Add regression tests for:
  - each controlled vocabulary
  - monitored impact branch
  - unmonitored impact branch
  - invalid monitoring period outside crediting period
  - invalid IPFS URI
  - invalid namespace IRI
  - missing workflow submission fields
- Publish versioned SHACL files and document schema resources.
- Deprecate old R schema names after canonical shapes and adapters pass
  validation.

## Priority Backlog

1. Fix ontology property kinds for controlled values, or create replacement
   object properties. ✅ completed
2. Add or choose a methodology relation; do not keep undefined
   `nias-o:indicatorMethodology`.
3. Replace `impactont:hasValue` with `impactont:hasIndicatorValue` plus
   `rdf:value`.
4. Create initial methodology and indicator concept scheme files, typing
   indicators as `ind:IndicatorDefinition` and attaching QUDT unit IRIs via
   `ind:hasUnit`. ✅ completed
5. Create `common-shapes.ttl`, `project-design-shapes.ttl`, and
   `impact-declaration-shapes.ttl`, including indicator definition and
   observation shapes that reference the indicator ontology.
6. Turn the R functions into compatibility adapters that output canonical RDF,
   replacing `nias-o:unitOfMeasure` string literals with `ind:hasUnit` QUDT IRIs.
8. Add claim/report wrappers after the direct domain shapes validate.
9. Design monitoring report requirements as measured impact reports using
   `ind:IndicatorObservation`.
10. Add validation fixtures and CI checks.

## Working Principle

The migration should not try to make the old R functions more sophisticated
schemas. Instead:

- Ontology defines meaning.
- SKOS concept schemes define controlled choices.
- SHACL defines user data requirements and validation.
- R adapters translate old inputs into canonical RDF until old clients can be
  retired.
- Claim/report wrappers record who asserted what, under which workflow, and
  with what substantiation.
