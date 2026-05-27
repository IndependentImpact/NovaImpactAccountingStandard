import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import textwrap
import unicodedata
from datetime import datetime, timezone
import re
from pathlib import Path

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF, Namespace


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PROFILE = (
    REPO_ROOT / "dataRequirements/document-rendering/pdd-rendering-profile.md"
)
DEFAULT_UI_SHAPES = (
    REPO_ROOT / "dataRequirements/shape2flutter/pdd-workflow-ui-shapes.ttl"
)
DEFAULT_VALIDATION_SHAPES = [
    REPO_ROOT / "dataRequirements/common-shapes.ttl",
    REPO_ROOT / "dataRequirements/project-design-shapes.ttl",
    REPO_ROOT / "dataRequirements/impact-declaration-shapes.ttl",
    REPO_ROOT / "dataRequirements/stakeholder-engagement-shapes.ttl",
    REPO_ROOT / "dataRequirements/document-shapes.ttl",
    REPO_ROOT / "dataRequirements/report-shapes.ttl",
]
DEFAULT_VALIDATION_ONTOLOGIES = [
    REPO_ROOT / "glossary/NovaImpactAccountingStandardOntology.ttl",
    REPO_ROOT / "glossary/NovaImpactAccountingStandardGlossary.ttl",
]
DEFAULT_PANDOC_PDF_ENGINE = "xelatex"

SH = Namespace("http://www.w3.org/ns/shacl#")
UI = Namespace("https://shape2flutter.dev/vocab/ui#")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
DCTERMS = Namespace("http://purl.org/dc/terms/")
SCHEMA = Namespace("https://schema.org/")
AIAO = Namespace("http://w3id.org/aiao#")
CLAIMONT = Namespace("http://w3id.org/claimont#")
IMPACTONT = Namespace("http://w3id.org/impactont#")
IND = Namespace("http://independentimpact.org/indicator-owl/")
NIAS = Namespace("https://nova.org.za/novaimpactaccountingstandard/")
DIRECTIVE_PATTERN = re.compile(r"^\{\{ render: ([a-zA-Z0-9_.-]+) \}\}$")
WORKFLOW_ROW_PATTERN = re.compile(
    r"^\|[^|]+\|\s*`([^`]+)`\s*/\s*`[^`]+`\s*\|[^|]+\|\s*`\{\{ render: ([^\s}]+) \}\}`\s*\|$"
)


def _read_front_matter_and_body(path: Path):
    text = path.read_text(encoding="utf-8")
    marker = "---\n"
    if not text.startswith(marker):
        raise ValueError("Profile must start with YAML front matter.")
    end = text.find("\n---\n", len(marker))
    if end == -1:
        raise ValueError("Profile YAML front matter must be closed.")
    return text[: end + len("\n---\n")], text[end + len("\n---\n") :]


def _local_name(node):
    if isinstance(node, URIRef):
        return str(node).rstrip("/").split("/")[-1].split("#")[-1]
    return str(node)


def _as_markdown_value(graph: Graph, node):
    if isinstance(node, Literal):
        py_value = node.toPython()
        if isinstance(py_value, bool):
            return "Yes" if py_value else "No"
        return str(py_value)
    if isinstance(node, URIRef):
        label = graph.value(node, RDFS.label)
        if label is not None:
            return str(label)
    return _local_name(node)


def _escape_table_cell(value):
    return str(value).replace("|", "\\|").replace("\n", "<br>")


def _two_column_table(rows):
    lines = ["| Field | Value |", "| --- | --- |"]
    for label, value in rows:
        lines.append(f"| {_escape_table_cell(label)} | {_escape_table_cell(value)} |")
    return lines


def _heading_anchor(title):
    slug = title.lower().replace("&", "and")
    slug = re.sub(r"`([^`]+)`", r"\1", slug)
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    slug = re.sub(r"-+", "-", slug)
    return slug


def _document_headings_for_toc(body: str):
    headings = []
    collecting = False
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if line == "## Workflow Section Rendering Map":
            break
        match = re.match(r"^(#{2,3})\s+(.+)$", line)
        if not match:
            continue
        level = len(match.group(1))
        title = match.group(2).strip()
        if title == "Section A. Description Of Project":
            collecting = True
        if not collecting or title == "Table Of Contents":
            continue
        headings.append((level, title))
    return headings


def _render_table_of_contents(body: str):
    lines = []
    for level, title in _document_headings_for_toc(body):
        indent = "  " if level >= 3 else ""
        lines.append(f"{indent}- [{title}](#{_heading_anchor(title)})")
    return lines or ["- _[table of contents to be generated]_"]


def _render_blank_title_page_table():
    rows = [
        ("Project ID", "_[optional: project display ID or project IRI]_"),
        ("PDD/schema version", "_[optional: document version or schema IRI]_"),
        ("Completion/publication date", "_[optional: completion or publication date]_"),
        ("Project developer", "_[required: project developer or responsible party]_"),
        ("Project representative", "_[optional: representative]_"),
        ("Host party or country", "_[required where applicable]_"),
        ("Project participants and communities", "_[required: project parties]_"),
        ("Methodology and version", "_[required: methodology reference(s)]_"),
        ("Product or impact type", "_[optional: product requirement or impact type]_"),
        ("Project cycle", "_[optional: regular, retroactive, or other cycle]_"),
    ]
    return _two_column_table(rows)


def _render_blank_metadata_appendix():
    return _two_column_table(
        [
            ("Document IPFS URI", "_[required: source document artifact URI]_"),
            ("Document schema IRI", "_[required: source document schema IRI]_"),
            ("Encrypted", "_[required: yes/no]_"),
            ("Document author", "_[required: author or reporting agent IRI]_"),
            ("Authenticity proof", "_[required: none, signature, or verifiable credential]_"),
            ("Workflow submission", "_[required: workflow submission evidence]_"),
            ("Source artifact", "_[rendering source artifact identifier]_"),
            ("Rendering profile", "nias-pdd-rendering-profile"),
            ("Rendering mode", "_[draft or final]_"),
            ("Source graph/hash evidence", "_[see Appendix C]_"),
        ]
    )


def _render_blank_data_parameter_table():
    return [
        "#### Parameter: _[parameter label]_",
        "",
        "| Field | Value |",
        "| --- | --- |",
        "| Description | _[required]_ |",
        "| Purpose | _[required]_ |",
        "| Unit | _[required unit IRI or label]_ |",
        "| Monitoring status | _[required: monitored or fixed ex ante]_ |",
        "| Measurement methods and procedures | _[optional]_ |",
        "| QA/QC procedures | _[optional]_ |",
        "| Monitoring frequency | _[optional]_ |",
        "| Sampling plan | _[optional]_ |",
        "| Applied value | _[optional]_ |",
        "| Data source | _[optional]_ |",
    ]


BLANK_CONTENT_DIRECTIVES = {
    "pdd.sectionA": [],
    "pdd.sectionA.projectPurpose": [
        "- **[required]** Project title: _[to be populated]_",
        "- **[required]** Objective: _[to be populated]_",
    ],
    "pdd.sectionA.locations": [
        "- **[required]** Project locations: _[location, boundary, map, or resource reference]_",
    ],
    "pdd.sectionA.technologiesAndMeasures": [
        "- **[required]** Type: _[facility, system, equipment, or other]_",
        "- **[required]** Description: _[to be populated]_",
        "- **[required]** Current age in years: _[to be populated]_",
        "- **[required]** Estimated lifespan in years: _[to be populated]_",
        "- **[optional]** Additional information: _[to be populated]_",
    ],
    "pdd.sectionA.projectParties": [
        "- **[required]** Party name: _[to be populated]_",
        "- **[required]** Host party: _[yes/no]_",
        "- **[required]** Participant party: _[yes/no]_",
        "- **[required]** Public or private: _[to be populated]_",
        "- **[optional]** Additional information: _[to be populated]_",
    ],
    "pdd.sectionA.legalFundingHistoryEligibility": [
        "- **[required]** Legal matters: _[to be populated]_",
        "- **[required]** Public funding: _[yes/no]_",
        "- **[optional]** Public funding sources: _[to be populated]_",
        "- **[required]** Project history: _[to be populated]_",
        "- **[required]** Debundling assessment: _[to be populated]_",
        "- **[optional]** Eligibility description: _[to be populated]_",
    ],
    "pdd.sectionB": [],
    "pdd.sectionB.methodologyReferences": [
        "- **[required]** Methodology reference and version: _[to be populated]_",
    ],
    "pdd.sectionB.declaredImpacts": [
        "- **[required]** Intentionality: _[intentional or unintentional]_",
        "- **[required]** Beneficial or adverse: _[beneficial or adverse]_",
        "- **[required]** Impact description: _[to be populated]_",
        "- **[required]** Monitored: _[yes/no]_",
        "- **[optional]** Not monitored justification: _[to be populated]_",
        "- **[optional]** Additionality justification: _[to be populated]_",
        "- **[optional]** Baseline or counterfactual state: _[indicator, value, unit, date/time]_",
        "- **[optional]** Project or real state: _[indicator, value, unit, date/time]_",
        "- **[optional]** Provenance resources: _[to be populated]_",
    ],
    "pdd.sectionB.impactClaims": [
        "- **[required]** Impact claim subject: _[project or activity]_",
        "- **[required]** Methodology references: _[to be populated]_",
    ],
    "pdd.sectionB.creditingAndMonitoringPeriods": [
        "- **[optional]** Crediting period start: _[to be populated]_",
        "- **[optional]** Crediting period end: _[to be populated]_",
        "- **[optional]** Renewable crediting period: _[yes/no]_",
        "- **[optional]** Monitoring periods: _[start and end date/time]_",
    ],
    "pdd.sectionB.exAnteEstimates": [
        "- **[optional]** Ex-ante impact estimate: _[to be populated]_",
    ],
    "pdd.sectionC": [],
    "pdd.sectionC.stakeholderEngagementModalities": [
        "- **[required]** Stakeholder engagement modalities: _[to be populated]_",
    ],
    "pdd.sectionC.stakeholderCommentSummary": [
        "- **[optional]** Stakeholder comment summary: _[to be populated]_",
    ],
    "pdd.sectionC.stakeholderCommentConsideration": [
        "- **[optional]** Stakeholder comment consideration: _[to be populated]_",
    ],
}


def _render_blank_directive(directive: str, profile_body: str):
    if directive == "titlePage.projectTitle":
        return ["### _[Project title to be populated]_"]
    if directive == "titlePage.keyProjectInformation":
        return _render_blank_title_page_table()
    if directive == "tableOfContents":
        return _render_table_of_contents(profile_body)
    if directive == "metadataAppendix":
        return _render_blank_metadata_appendix()
    if directive == "pdd.sectionB.dataParameterTables":
        return _render_blank_data_parameter_table()
    if directive in BLANK_CONTENT_DIRECTIVES:
        return BLANK_CONTENT_DIRECTIVES[directive]
    return None


def _first_subject_of_type(graph: Graph, rdf_type):
    return next(iter(graph.subjects(RDF.type, rdf_type)), None)


def _first_value(graph: Graph, subject, predicate):
    if subject is None:
        return None
    return next(iter(graph.objects(subject, predicate)), None)


def _sorted_values(graph: Graph, subject, predicate):
    if subject is None:
        return []
    values = list(graph.objects(subject, predicate))
    return sorted(values, key=lambda item: _as_markdown_value(graph, item))


def _insert_front_matter_metadata(front_matter: str, metadata: dict):
    lines = front_matter.splitlines()
    if not lines or lines[0] != "---" or lines[-1] != "---":
        raise ValueError("Profile front matter is malformed.")
    for key, value in metadata.items():
        lines.insert(-1, f"{key}: {value}")
    return "\n".join(lines) + "\n"


def _shape_lookup(graph: Graph):
    lookup = {}
    for shape in graph.subjects(RDF.type, SH.NodeShape):
        lookup[_local_name(shape)] = shape
    return lookup


def _workflow_section_shape_map(body: str):
    in_workflow_map = False
    directive_to_shape = {}
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if line == "## Workflow Section Rendering Map":
            in_workflow_map = True
            continue
        if in_workflow_map and line.startswith("## "):
            break
        if not in_workflow_map or not line.startswith("|"):
            continue
        match = WORKFLOW_ROW_PATTERN.match(line)
        if not match:
            continue
        shape_name, directive = match.groups()
        directive_to_shape[directive] = shape_name
    return directive_to_shape


def _ordered_fields(graph: Graph, shape, recurse_limit: int):
    fields = []
    for prop in graph.objects(shape, SH.property):
        order_lit = graph.value(prop, UI.order)
        order = int(order_lit.toPython()) if order_lit is not None else 10_000
        label = graph.value(prop, UI.label) or graph.value(prop, SH.name)
        path = graph.value(prop, SH.path)
        field_label = str(label) if label is not None else _local_name(path)
        min_count = graph.value(prop, SH.minCount)
        required = int(min_count.toPython()) >= 1 if min_count is not None else False
        node_shape = graph.value(prop, SH.node) if recurse_limit > 0 else None
        node_shape_name = _local_name(node_shape) if node_shape is not None else None
        fields.append((order, field_label, required, node_shape_name))
    return sorted(fields, key=lambda item: (item[0], item[1]))


def _render_shape_placeholders(graph, shape_lookup, shape_name, depth=0, seen=None):
    seen = seen or set()
    if shape_name in seen:
        return []
    shape = shape_lookup.get(shape_name)
    if shape is None:
        return []

    lines = []
    for _, label, required, nested in _ordered_fields(graph, shape, recurse_limit=1):
        status = "required" if required else "optional"
        indent = "  " * depth
        lines.append(f"{indent}- **[{status}]** {label}: _[to be populated]_")
        if nested:
            lines.extend(
                _render_shape_placeholders(
                    graph,
                    shape_lookup,
                    nested,
                    depth=depth + 1,
                    seen=seen | {shape_name},
                )
            )
    return lines


def render_blank_template(profile_path: Path, ui_shapes_path: Path):
    front_matter, body = _read_front_matter_and_body(profile_path)
    graph = Graph()
    graph.parse(str(ui_shapes_path), format="turtle")
    shape_lookup = _shape_lookup(graph)
    directive_map = _workflow_section_shape_map(body)

    lines = []
    for raw_line in body.splitlines():
        stripped = raw_line.strip()
        if stripped == "## Workflow Section Rendering Map":
            break

        directive_match = DIRECTIVE_PATTERN.match(stripped)
        if not directive_match:
            lines.append(raw_line)
            continue

        directive = directive_match.group(1)
        custom_lines = _render_blank_directive(directive, body)
        if custom_lines is not None:
            lines.extend(custom_lines)
            lines.append("")
            continue

        shape_name = directive_map.get(directive)
        if shape_name is None:
            lines.append(f"- **[optional]** {directive}: _[to be populated]_")
            lines.append("")
            continue

        placeholders = _render_shape_placeholders(graph, shape_lookup, shape_name)
        if not placeholders:
            lines.append(f"- **[optional]** {directive}: _[to be populated]_")
            lines.append("")
            continue

        lines.extend(placeholders)
        lines.append("")

    rendered_body = "\n".join(lines).rstrip() + "\n"
    return f"{front_matter}{rendered_body}"


def _render_data_parameter_tables(graph: Graph, section_b):
    rows = []
    impact_nodes = _sorted_values(graph, section_b, NIAS.hasDeclaredImpact)
    parameters = []
    for impact_node in impact_nodes:
        parameters.extend(_sorted_values(graph, impact_node, NIAS.dataParameterRequirement))

    for parameter in parameters:
        title = _first_value(graph, parameter, RDFS.label)
        rows.extend(
            [
                f"#### Parameter: {_as_markdown_value(graph, title) if title is not None else _local_name(parameter)}",
                "",
                "| Field | Value |",
                "| --- | --- |",
                f"| Description | {_as_markdown_value(graph, _first_value(graph, parameter, SCHEMA.description) or Literal(''))} |",
                f"| Purpose | {_as_markdown_value(graph, _first_value(graph, parameter, NIAS.dataParameterPurpose) or Literal(''))} |",
                f"| Unit | {_as_markdown_value(graph, _first_value(graph, parameter, IND.hasUnit) or Literal(''))} |",
                f"| Monitoring status | {_as_markdown_value(graph, _first_value(graph, parameter, NIAS.monitoredOrFixed) or Literal(''))} |",
                f"| Monitoring frequency | {_as_markdown_value(graph, _first_value(graph, parameter, NIAS.monitoringFrequency) or Literal(''))} |",
                f"| QA/QC procedures | {_as_markdown_value(graph, _first_value(graph, parameter, NIAS.qaQcProcedures) or Literal(''))} |",
                f"| Data source | {_as_markdown_value(graph, _first_value(graph, parameter, NIAS.dataSource) or Literal(''))} |",
                "",
            ]
        )
    return rows or ["- No parameter tables available.", ""]


def _is_truthy_value(graph: Graph, node):
    if node is None:
        return False
    if isinstance(node, Literal):
        value = node.toPython()
        if isinstance(value, bool):
            return value
    return _as_markdown_value(graph, node).strip().lower() in {"yes", "true", "1"}


def _project_party_names(graph: Graph, project, flag_predicate=None):
    names = []
    for party in _sorted_values(graph, project, NIAS.projectParty):
        if flag_predicate is not None and not _is_truthy_value(
            graph, _first_value(graph, party, flag_predicate)
        ):
            continue
        name = _first_value(graph, party, NIAS.partyName)
        names.append(
            _as_markdown_value(graph, name) if name is not None else _local_name(party)
        )
    return names


def _joined_or_unavailable(values):
    return ", ".join(values) if values else "Unavailable"


def _methodology_labels(graph: Graph, section_b):
    methodologies = _sorted_values(graph, section_b, NIAS.usesMethodology)
    if not methodologies:
        for claim in _sorted_values(graph, section_b, NIAS.impactClaim):
            methodologies.extend(_sorted_values(graph, claim, NIAS.usesMethodology))
    return [_as_markdown_value(graph, item) for item in methodologies]


def _impact_type_summary(graph: Graph, section_b):
    summaries = []
    for impact in _sorted_values(graph, section_b, NIAS.hasDeclaredImpact):
        description = _first_value(graph, impact, SCHEMA.description)
        intentionality = _first_value(graph, impact, NIAS.impactIntentionality)
        impact_kind = _first_value(graph, impact, NIAS.beneficialOrAdverse)
        detail = []
        if intentionality is not None:
            detail.append(_as_markdown_value(graph, intentionality))
        if impact_kind is not None:
            detail.append(_as_markdown_value(graph, impact_kind))
        label = (
            _as_markdown_value(graph, description)
            if description is not None
            else _local_name(impact)
        )
        if detail:
            label = f"{label} ({', '.join(detail)})"
        summaries.append(label)
    return summaries


def _render_title_page_table(
    graph: Graph,
    project,
    section_a,
    section_b,
    generated_at: str,
):
    schema = _first_value(graph, section_a, DCTERMS.conformsTo)
    developer = _first_value(graph, section_a, CLAIMONT.isMadeBy) or _first_value(
        graph, section_b, CLAIMONT.isMadeBy
    )
    host_parties = _project_party_names(graph, project, NIAS.isHostParty)
    participant_parties = _project_party_names(graph, project, NIAS.isParticipantParty)
    all_parties = _project_party_names(graph, project)
    if not participant_parties:
        participant_parties = all_parties

    rows = [
        (
            "Project ID",
            _as_markdown_value(graph, project) if project is not None else "Unavailable",
        ),
        (
            "PDD/schema version",
            _as_markdown_value(graph, schema) if schema is not None else "Unavailable",
        ),
        ("Completion/publication date", generated_at),
        (
            "Project developer",
            _as_markdown_value(graph, developer) if developer is not None else "Unavailable",
        ),
        ("Project representative", "Unavailable"),
        ("Host party or country", _joined_or_unavailable(host_parties)),
        (
            "Project participants and communities",
            _joined_or_unavailable(participant_parties),
        ),
        (
            "Methodology and version",
            _joined_or_unavailable(_methodology_labels(graph, section_b)),
        ),
        (
            "Product or impact type",
            _joined_or_unavailable(_impact_type_summary(graph, section_b)),
        ),
        ("Project cycle", "Unavailable"),
    ]
    return _two_column_table(rows)


def _render_filled_directive(
    directive: str,
    graph: Graph,
    source_artifact: str,
    validation_status: str,
    render_mode: str,
    generated_at: str,
    profile_body: str,
):
    section_a = _first_subject_of_type(graph, NIAS.PddSectionAReport)
    section_b = _first_subject_of_type(graph, NIAS.PddSectionBReport)
    section_c = _first_subject_of_type(graph, NIAS.PddSectionCStakeholderEngagement)
    project = _first_subject_of_type(graph, AIAO.Project)

    if project is None and section_a is not None:
        project = _first_value(graph, section_a, CLAIMONT.hasSubject)

    if directive == "titlePage.projectTitle":
        project_title = _first_value(graph, project, NIAS.title)
        return [
            f"### {_as_markdown_value(graph, project_title) if project_title is not None else 'Project title unavailable'}"
        ]

    if directive == "titlePage.keyProjectInformation":
        return _render_title_page_table(
            graph,
            project,
            section_a,
            section_b,
            generated_at=generated_at,
        )

    if directive == "tableOfContents":
        return _render_table_of_contents(profile_body)

    if directive == "documentControl.versionSummary":
        schema = _first_value(graph, section_a, DCTERMS.conformsTo)
        return [f"- Section A schema: {_as_markdown_value(graph, schema) if schema is not None else 'Unavailable'}"]

    if directive == "documentControl.validationStatus":
        return [f"- Validation status: {validation_status}"]

    if directive == "pdd.sectionA":
        return []

    if directive == "pdd.sectionA.projectPurpose":
        objective = _first_value(graph, project, AIAO.hasObjective)
        description = _first_value(graph, objective, SCHEMA.description)
        return [f"- {_as_markdown_value(graph, description) if description is not None else 'Unavailable'}"]

    if directive == "pdd.sectionA.locations":
        lines = []
        for location in _sorted_values(graph, project, IMPACTONT.hasSpatialLocation):
            ipfs_uri = _first_value(graph, location, NIAS.resourceIpfsUri)
            lines.append(f"- {_as_markdown_value(graph, ipfs_uri) if ipfs_uri is not None else _local_name(location)}")
        return lines or ["- No locations provided."]

    if directive == "pdd.sectionA.technologiesAndMeasures":
        lines = []
        for technology in _sorted_values(graph, project, NIAS.technologyOrMeasure):
            tech_type = _first_value(graph, technology, NIAS.techMeasType)
            description = _first_value(graph, technology, SCHEMA.description)
            lines.append(
                f"- {_as_markdown_value(graph, tech_type) if tech_type is not None else 'Technology'}: "
                f"{_as_markdown_value(graph, description) if description is not None else 'Unavailable'}"
            )
        return lines or ["- No technologies or measures provided."]

    if directive == "pdd.sectionA.projectParties":
        lines = []
        for party in _sorted_values(graph, project, NIAS.projectParty):
            name = _first_value(graph, party, NIAS.partyName)
            host = _first_value(graph, party, NIAS.isHostParty)
            participant = _first_value(graph, party, NIAS.isParticipantParty)
            lines.append(
                f"- {_as_markdown_value(graph, name) if name is not None else _local_name(party)} "
                f"(host: {_as_markdown_value(graph, host) if host is not None else 'No'}, "
                f"participant: {_as_markdown_value(graph, participant) if participant is not None else 'No'})"
            )
        return lines or ["- No project parties provided."]

    if directive == "pdd.sectionA.legalFundingHistoryEligibility":
        return [
            f"- Legal matters: {_as_markdown_value(graph, _first_value(graph, project, NIAS.legalMatters) or Literal('Unavailable'))}",
            f"- Public funding: {_as_markdown_value(graph, _first_value(graph, project, NIAS.publicFundingStatus) or Literal('Unavailable'))}",
            f"- Project history: {_as_markdown_value(graph, _first_value(graph, project, NIAS.projectHistory) or Literal('Unavailable'))}",
            f"- Debundling assessment: {_as_markdown_value(graph, _first_value(graph, project, NIAS.debundlingAssessment) or Literal('Unavailable'))}",
        ]

    if directive == "pdd.sectionB":
        return []

    if directive == "pdd.sectionB.methodologyReferences":
        values = _sorted_values(graph, section_b, NIAS.usesMethodology)
        return [f"- {_as_markdown_value(graph, item)}" for item in values] or ["- No methodology references provided."]

    if directive == "pdd.sectionB.declaredImpacts":
        lines = []
        for impact in _sorted_values(graph, section_b, NIAS.hasDeclaredImpact):
            description = _first_value(graph, impact, SCHEMA.description)
            intentionality = _first_value(graph, impact, NIAS.impactIntentionality)
            impact_kind = _first_value(graph, impact, NIAS.beneficialOrAdverse)
            lines.append(
                f"- {_as_markdown_value(graph, description) if description is not None else _local_name(impact)} "
                f"({_as_markdown_value(graph, intentionality) if intentionality is not None else 'unknown'}, "
                f"{_as_markdown_value(graph, impact_kind) if impact_kind is not None else 'unknown'})"
            )
        return lines or ["- No declared impacts provided."]

    if directive == "pdd.sectionB.impactClaims":
        lines = []
        for claim in _sorted_values(graph, section_b, NIAS.impactClaim):
            subject = _first_value(graph, claim, CLAIMONT.hasSubject)
            methodologies = [
                _as_markdown_value(graph, item)
                for item in _sorted_values(graph, claim, NIAS.usesMethodology)
            ]
            methods = ", ".join(methodologies) if methodologies else "Unavailable"
            lines.append(
                f"- Subject: {_as_markdown_value(graph, subject) if subject is not None else 'Unavailable'}; "
                f"Methodologies: {methods}"
            )
        return lines or ["- No impact claims provided."]

    if directive == "pdd.sectionB.creditingAndMonitoringPeriods":
        lines = []
        for impact in _sorted_values(graph, section_b, NIAS.hasDeclaredImpact):
            crediting = _first_value(graph, impact, NIAS.creditingPeriod)
            renewable = _first_value(graph, crediting, NIAS.creditingPeriodIsRenewable)
            lines.append(
                f"- Crediting period renewable: {_as_markdown_value(graph, renewable) if renewable is not None else 'Unavailable'}"
            )
        return lines or ["- No crediting period data provided."]

    if directive == "pdd.sectionB.dataParameterTables":
        return _render_data_parameter_tables(graph, section_b)

    if directive == "pdd.sectionB.exAnteEstimates":
        lines = []
        for impact in _sorted_values(graph, section_b, NIAS.hasDeclaredImpact):
            value = _first_value(graph, impact, NIAS.exAnteImpactEstimate)
            if value is not None:
                lines.append(f"- {_as_markdown_value(graph, value)}")
        return lines or ["- No ex-ante estimates provided."]

    if directive == "pdd.sectionC":
        return []

    if directive == "pdd.sectionC.stakeholderEngagementModalities":
        value = _first_value(graph, section_c, NIAS.stakeholderEngagementModalities)
        return [f"- {_as_markdown_value(graph, value) if value is not None else 'Unavailable'}"]

    if directive == "pdd.sectionC.stakeholderCommentSummary":
        value = _first_value(graph, section_c, NIAS.stakeholderCommentSummary)
        return [f"- {_as_markdown_value(graph, value) if value is not None else 'Unavailable'}"]

    if directive == "pdd.sectionC.stakeholderCommentConsideration":
        value = _first_value(graph, section_c, NIAS.stakeholderCommentConsideration)
        return [f"- {_as_markdown_value(graph, value) if value is not None else 'Unavailable'}"]

    if directive == "metadataAppendix":
        schema = _first_value(graph, section_a, DCTERMS.conformsTo)
        developer = _first_value(graph, section_a, CLAIMONT.isMadeBy) or _first_value(
            graph, section_b, CLAIMONT.isMadeBy
        )
        return _two_column_table(
            [
                ("Document IPFS URI", "Unavailable"),
                (
                    "Document schema IRI",
                    _as_markdown_value(graph, schema) if schema is not None else "Unavailable",
                ),
                ("Encrypted", "Unavailable"),
                (
                    "Document author",
                    _as_markdown_value(graph, developer) if developer is not None else "Unavailable",
                ),
                ("Authenticity proof", "Unavailable"),
                ("Workflow submission", "Unavailable"),
                ("Validation status", validation_status),
                ("Source artifact", source_artifact),
                ("Rendering profile", "nias-pdd-rendering-profile"),
                ("Rendering mode", render_mode),
            ]
        )

    if directive == "predicateMapAppendix":
        return [
            "- Project title -> https://nova.org.za/novaimpactaccountingstandard/title",
            "- Declared impact description -> https://schema.org/description",
            "- Stakeholder modalities -> https://nova.org.za/novaimpactaccountingstandard/stakeholderEngagementModalities",
        ]

    if directive == "sourceEvidenceAppendix":
        return [f"- Source graph identifier: {source_artifact}"]

    return [f"- No data provided for `{directive}`."]


def render_filled_markdown(
    profile_path: Path,
    ui_shapes_path: Path,
    data_path: Path,
    source_artifact: str,
    generated_at: str,
    render_mode: str = "draft",
):
    front_matter, body = _read_front_matter_and_body(profile_path)
    graph = Graph()
    graph.parse(str(data_path), format="json-ld")
    validation_status = "draft (validation not enforced)"

    if render_mode == "final":
        try:
            from pyshacl import validate
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "Final render mode requires pySHACL. Install dependency `pyshacl`."
            ) from exc

        shape_graph = Graph()
        for shape_path in DEFAULT_VALIDATION_SHAPES:
            shape_graph.parse(str(shape_path), format="turtle")
        ontology_graph = Graph()
        for ontology_path in DEFAULT_VALIDATION_ONTOLOGIES:
            ontology_graph.parse(str(ontology_path), format="turtle")
        conforms, _, validation_text = validate(
            data_graph=graph,
            shacl_graph=shape_graph,
            ont_graph=ontology_graph,
            inference="rdfs",
            abort_on_first=False,
            allow_infos=False,
            allow_warnings=False,
            advanced=True,
        )
        if not conforms:
            raise ValueError(
                "Final render mode requires SHACL-conformant input.\n"
                f"{validation_text}"
            )
        validation_status = "final (SHACL validation passed)"

    front_matter = _insert_front_matter_metadata(
        front_matter,
        {
            "renderMode": render_mode,
            "rendererVersion": "0.5.0",
            "sourceArtifact": source_artifact,
            "generatedAt": generated_at,
        },
    )
    lines = []
    project = _first_subject_of_type(graph, AIAO.Project)
    project_title = _first_value(graph, project, NIAS.title)
    for raw_line in body.splitlines():
        stripped = raw_line.strip()
        if stripped == "## Workflow Section Rendering Map":
            break

        if stripped == "# {{ project.title }}":
            lines.append(
                f"# {_as_markdown_value(graph, project_title) if project_title is not None else 'Project Design Document'}"
            )
            continue

        directive_match = DIRECTIVE_PATTERN.match(stripped)
        if not directive_match:
            lines.append(raw_line)
            continue

        directive = directive_match.group(1)
        lines.extend(
            _render_filled_directive(
                directive,
                graph,
                source_artifact,
                validation_status,
                render_mode,
                generated_at,
                body,
            )
        )
        lines.append("")

    rendered_body = "\n".join(lines).rstrip() + "\n"
    return f"{front_matter}{rendered_body}"


def _sha256_text(text: str):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sha256_file(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _resolve_pandoc_bin():
    configured = os.environ.get("PANDOC_BIN")
    if configured:
        candidate = Path(configured)
        return str(candidate) if candidate.exists() else None

    discovered = shutil.which("pandoc")
    if discovered:
        return discovered

    for candidate in (
        Path("/usr/local/bin/pandoc"),
        Path("/opt/homebrew/bin/pandoc"),
    ):
        if candidate.exists():
            return str(candidate)

    return None


def _resolve_pandoc_pdf_engine():
    return os.environ.get("PANDOC_PDF_ENGINE") or DEFAULT_PANDOC_PDF_ENGINE


def _compile_pandoc_output(
    markdown_path: Path,
    output_path: Path,
    output_format: str,
    document_reference: str,
):
    pandoc_bin = _resolve_pandoc_bin()
    if pandoc_bin is None:
        raise RuntimeError(
            "Pandoc command `pandoc` was not found. Install Pandoc, add it to PATH, "
            "or set PANDOC_BIN to compile Pandoc outputs."
        )

    command = [
        pandoc_bin,
        str(markdown_path),
        "--from",
        "markdown",
        "--output",
        str(output_path),
    ]
    if output_format == "html":
        command.extend(["--to", "html5", "--standalone"])
        header_path = None
    elif output_format == "pdf":
        command.extend(["--to", "pdf", "--pdf-engine", _resolve_pandoc_pdf_engine()])
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", suffix=".tex", delete=False
        ) as header_file:
            header_file.write("\\usepackage{enumitem}\n")
            header_file.write("\\setlistdepth{9}\n")
            header_file.write("\\renewlist{itemize}{itemize}{9}\n")
            header_file.write("\\setlist[itemize]{label=\\textbullet,leftmargin=*}\n")
            header_file.write("\\setlist[itemize,2]{label=--}\n")
            header_file.write("\\setlist[itemize,3]{label=*}\n")
            header_file.write("\\setlist[itemize,4]{label=+}\n")
            header_file.write("\\setlist[itemize,5]{label=--}\n")
            header_file.write("\\setlist[itemize,6]{label=*}\n")
            header_file.write("\\setlist[itemize,7]{label=+}\n")
            header_file.write("\\setlist[itemize,8]{label=--}\n")
            header_file.write("\\setlist[itemize,9]{label=*}\n")
            header_file.write("\\usepackage{fancyhdr}\n")
            header_file.write("\\pagestyle{fancy}\n")
            header_file.write("\\fancyhf{}\n")
            header_file.write(f"\\lfoot{{Document ID: {document_reference}}}\n")
            header_file.write("\\rfoot{\\thepage}\n")
            header_file.write("\\renewcommand{\\headrulewidth}{0pt}\n")
            header_file.write("\\renewcommand{\\footrulewidth}{0.4pt}\n")
            header_path = Path(header_file.name)
        command.extend(["--include-in-header", str(header_path)])
    else:
        raise ValueError(f"Unsupported output format: {output_format}")

    try:
        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except subprocess.CalledProcessError as exc:
        details = (exc.stderr or exc.stdout or "").strip()
        raise RuntimeError(
            f"Pandoc failed while compiling {output_format.upper()}: {details}"
        ) from exc
    finally:
        if output_format == "pdf" and header_path is not None and header_path.exists():
            header_path.unlink()


def _pdf_safe_text(value: str):
    normalized = unicodedata.normalize("NFKD", value)
    latin_text = normalized.encode("latin-1", errors="replace").decode("latin-1")
    return (
        latin_text.replace("\\", "\\\\")
        .replace("(", "\\(")
        .replace(")", "\\)")
    )


def _markdown_to_pdf_lines(markdown: str):
    if markdown.startswith("---\n"):
        end = markdown.find("\n---\n", 4)
        if end != -1:
            markdown = markdown[end + len("\n---\n") :]

    lines = []
    in_fenced_block = False
    for raw_line in markdown.splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("```"):
            in_fenced_block = not in_fenced_block
            continue
        if not in_fenced_block:
            stripped = re.sub(r"^#{1,6}\s+", "", stripped)
            stripped = stripped.replace("**", "").replace("`", "")
            stripped = re.sub(r"\{\{ render: ([^}]+) \}\}", r"[to be populated: \1]", stripped)
        if not stripped:
            lines.append("")
            continue
        wrapped = textwrap.wrap(stripped, width=92) or [stripped]
        lines.extend(wrapped)
    return lines or ["Project Design Document"]


def _paginate_lines(lines: list[str], lines_per_page: int):
    pages = []
    for index in range(0, len(lines), lines_per_page):
        pages.append(lines[index : index + lines_per_page])
    return pages or [[]]


def _content_stream_for_page(lines: list[str], document_reference: str, page_number: int):
    commands = ["BT", "/F1 10 Tf", "54 790 Td", "14 TL"]
    for line in lines:
        commands.append(f"({_pdf_safe_text(line)}) Tj")
        commands.append("T*")
    commands.extend(
        [
            "ET",
            "BT",
            "/F1 8 Tf",
            f"54 36 Td (Document ID: {_pdf_safe_text(document_reference)} | Page {page_number}) Tj",
            "ET",
        ]
    )
    return "\n".join(commands).encode("latin-1", errors="replace")


def _write_minimal_pdf(markdown_path: Path, output_path: Path, document_reference: str):
    markdown = markdown_path.read_text(encoding="utf-8")
    pages = _paginate_lines(_markdown_to_pdf_lines(markdown), lines_per_page=52)

    objects: list[bytes] = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    page_object_numbers = []

    for page_number, page_lines in enumerate(pages, start=1):
        page_object_number = len(objects) + 1
        content_object_number = page_object_number + 1
        page_object_numbers.append(page_object_number)
        content = _content_stream_for_page(
            page_lines,
            document_reference=document_reference,
            page_number=page_number,
        )
        objects.append(
            (
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
                f"/Resources << /Font << /F1 3 0 R >> >> "
                f"/Contents {content_object_number} 0 R >>"
            ).encode("ascii")
        )
        objects.append(
            b"<< /Length " + str(len(content)).encode("ascii") + b" >>\n"
            b"stream\n" + content + b"\nendstream"
        )

    kids = " ".join(f"{obj_number} 0 R" for obj_number in page_object_numbers)
    objects[1] = f"<< /Type /Pages /Kids [{kids}] /Count {len(pages)} >>".encode(
        "ascii"
    )

    output = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for obj_number, obj in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{obj_number} 0 obj\n".encode("ascii"))
        output.extend(obj)
        output.extend(b"\nendobj\n")

    xref_offset = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode("ascii")
    )
    output_path.write_bytes(output)


def _validate_pdf(path: Path):
    payload = path.read_bytes()
    if not payload.startswith(b"%PDF-"):
        raise RuntimeError(f"{path} is not a PDF file.")
    if b"%%EOF" not in payload[-1024:]:
        raise RuntimeError(f"{path} is missing the PDF EOF marker.")

    try:
        subprocess.run(
            ["qpdf", "--check", str(path)],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except FileNotFoundError:
        return
    except subprocess.CalledProcessError as exc:
        details = (exc.stderr or exc.stdout or "").strip()
        raise RuntimeError(f"{path} failed qpdf validation: {details}") from exc


def _compile_pdf_output(markdown_path: Path, output_path: Path, document_reference: str):
    try:
        _compile_pandoc_output(
            markdown_path,
            output_path,
            output_format="pdf",
            document_reference=document_reference,
        )
        _validate_pdf(output_path)
        return
    except RuntimeError:
        if output_path.exists():
            output_path.unlink()

    _write_minimal_pdf(
        markdown_path,
        output_path,
        document_reference=document_reference,
    )
    _validate_pdf(output_path)


def export_rendered_outputs(
    rendered_markdown: str,
    output_dir: Path,
    output_targets: list[str],
    source_artifact: str,
    generated_at: str,
    render_mode: str,
):
    output_dir.mkdir(parents=True, exist_ok=True)
    document_hash = _sha256_text(rendered_markdown)
    document_id = f"pdd-{document_hash[:12]}"

    markdown_path = output_dir / "pdd.md"
    markdown_path.write_text(rendered_markdown, encoding="utf-8")

    artifacts = [
        {
            "artifact": "markdown",
            "path": markdown_path.name,
            "sha256": _sha256_file(markdown_path),
        }
    ]

    if "html" in output_targets:
        html_path = output_dir / "pdd.html"
        _compile_pandoc_output(
            markdown_path,
            html_path,
            output_format="html",
            document_reference=document_id,
        )
        artifacts.append(
            {
                "artifact": "website",
                "path": html_path.name,
                "sha256": _sha256_file(html_path),
            }
        )

    if "pdf" in output_targets:
        pdf_path = output_dir / "pdd.pdf"
        _compile_pdf_output(
            markdown_path,
            pdf_path,
            document_reference=document_id,
        )
        artifacts.append(
            {
                "artifact": "pdf",
                "path": pdf_path.name,
                "sha256": _sha256_file(pdf_path),
            }
        )

    if render_mode == "final":
        metadata_path = output_dir / "pdd.metadata.jsonld"
        metadata_payload = {
            "@context": {
                "dcterms": "http://purl.org/dc/terms/",
                "nias": "https://nova.org.za/novaimpactaccountingstandard/",
            },
            "@id": f"urn:nias:{document_id}",
            "@type": "dcterms:BibliographicResource",
            "dcterms:identifier": document_id,
            "dcterms:source": source_artifact,
            "dcterms:created": generated_at,
            "nias:renderMode": render_mode,
            "nias:artifacts": artifacts,
        }
        metadata_path.write_text(
            json.dumps(metadata_payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        validation_path = output_dir / "pdd.validation.json"
        validation_payload = {
            "documentId": document_id,
            "renderMode": render_mode,
            "status": "passed",
            "sourceArtifact": source_artifact,
            "generatedAt": generated_at,
            "artifacts": artifacts,
        }
        validation_path.write_text(
            json.dumps(validation_payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )


def main():
    parser = argparse.ArgumentParser(
        description="Render NIAS PDD Markdown from the rendering profile and optional JSON-LD payload."
    )
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
    parser.add_argument("--ui-shapes", type=Path, default=DEFAULT_UI_SHAPES)
    parser.add_argument("--input-jsonld", type=Path)
    parser.add_argument("--source-artifact-id")
    parser.add_argument("--generated-at")
    parser.add_argument(
        "--render-mode",
        choices=["draft", "final"],
        default="draft",
        help="Filled rendering mode: draft allows placeholders, final enforces SHACL validation.",
    )
    parser.add_argument(
        "--output-target",
        action="append",
        choices=["markdown", "pdf", "html"],
        help="Add compiled output target(s) for --output-dir. Repeat to include multiple targets.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Write deterministic export artifacts into this directory.",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    source_artifact = "blank-template"
    generated_at = datetime.now(timezone.utc).isoformat()
    if args.input_jsonld:
        source_artifact = args.source_artifact_id or args.input_jsonld.name
        generated_at = args.generated_at or generated_at
        try:
            rendered = render_filled_markdown(
                args.profile,
                args.ui_shapes,
                args.input_jsonld,
                source_artifact=source_artifact,
                generated_at=generated_at,
                render_mode=args.render_mode,
            )
        except (RuntimeError, ValueError) as exc:
            parser.exit(1, f"{exc}\n")
    else:
        rendered = render_blank_template(args.profile, args.ui_shapes)

    if args.output_dir:
        output_targets = args.output_target or ["markdown"]
        try:
            export_rendered_outputs(
                rendered_markdown=rendered,
                output_dir=args.output_dir,
                output_targets=output_targets,
                source_artifact=source_artifact,
                generated_at=generated_at,
                render_mode=args.render_mode,
            )
        except (RuntimeError, ValueError) as exc:
            parser.exit(1, f"{exc}\n")

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    elif not args.output_dir:
        print(rendered, end="")


if __name__ == "__main__":
    main()
