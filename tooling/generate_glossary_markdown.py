import argparse
import sys
from pathlib import Path

from rdflib import Graph
from rdflib.namespace import RDF, SKOS


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TTL = REPO_ROOT / "glossary/NovaImpactAccountingStandardGlossary.ttl"
DEFAULT_OUTPUT = REPO_ROOT / "02-a-Glossary.md"


def _escape_markdown_cell(value):
    return str(value).replace("|", "\\|").replace("\n", "<br>")


def _label_sort_key(label, iri):
    if label is None:
        return (1, str(iri).casefold())
    return (0, str(label).casefold(), str(iri).casefold())


def _first_value(graph, subject, predicate):
    for value in graph.objects(subject, predicate):
        return value
    return None


def _collect_validation_errors(graph, schemes):
    errors = []
    for scheme in sorted(schemes, key=lambda iri: str(iri)):
        if _first_value(graph, scheme, SKOS.prefLabel) is None:
            errors.append(f"Scheme missing skos:prefLabel: {scheme}")
        if _first_value(graph, scheme, SKOS.definition) is None:
            errors.append(f"Scheme missing skos:definition: {scheme}")

    scheme_set = set(schemes)
    concepts = list(graph.subjects(RDF.type, SKOS.Concept))
    for concept in sorted(set(concepts), key=lambda iri: str(iri)):
        if _first_value(graph, concept, SKOS.prefLabel) is None:
            errors.append(f"Concept missing skos:prefLabel: {concept}")
        if _first_value(graph, concept, SKOS.definition) is None:
            errors.append(f"Concept missing skos:definition: {concept}")
        in_schemes = list(graph.objects(concept, SKOS.inScheme))
        if not in_schemes:
            errors.append(f"Concept missing skos:inScheme: {concept}")
            continue
        for in_scheme in in_schemes:
            if in_scheme not in scheme_set:
                errors.append(
                    f"Concept references missing scheme via skos:inScheme: {concept} -> {in_scheme}"
                )
    return errors


def render_glossary_markdown(ttl_path: Path) -> str:
    graph = Graph()
    graph.parse(str(ttl_path), format="turtle")

    schemes = list(set(graph.subjects(RDF.type, SKOS.ConceptScheme)))
    errors = _collect_validation_errors(graph, schemes)
    if errors:
        raise ValueError("Glossary validation failed:\n- " + "\n- ".join(errors))

    sorted_schemes = sorted(
        schemes,
        key=lambda scheme: _label_sort_key(
            _first_value(graph, scheme, SKOS.prefLabel),
            scheme,
        ),
    )

    lines = ["## Glossary", ""]
    for scheme in sorted_schemes:
        scheme_label = _first_value(graph, scheme, SKOS.prefLabel)
        scheme_definition = _first_value(graph, scheme, SKOS.definition)
        lines.append(f"### {scheme_label}")
        lines.append("")
        lines.append(str(scheme_definition))
        lines.append("")
        lines.append("| Term | Definition | IRI |")
        lines.append("| --- | --- | --- |")

        concepts = set(graph.subjects(SKOS.inScheme, scheme))
        sorted_concepts = sorted(
            concepts,
            key=lambda concept: _label_sort_key(
                _first_value(graph, concept, SKOS.prefLabel),
                concept,
            ),
        )
        for concept in sorted_concepts:
            label = _first_value(graph, concept, SKOS.prefLabel)
            definition = _first_value(graph, concept, SKOS.definition)
            lines.append(
                "| "
                f"{_escape_markdown_cell(label)} | "
                f"{_escape_markdown_cell(definition)} | "
                f"{_escape_markdown_cell(concept)} |"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser(
        description="Generate 02-a-Glossary.md from NIAS glossary Turtle."
    )
    parser.add_argument(
        "--ttl",
        type=Path,
        default=DEFAULT_TTL,
        help="Path to glossary TTL file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Path to generated markdown file.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero if generated markdown differs from --output.",
    )
    args = parser.parse_args()

    rendered = render_glossary_markdown(args.ttl)
    if args.check:
        if not args.output.exists():
            print(f"Output file does not exist for --check: {args.output}", file=sys.stderr)
            return 1
        existing = args.output.read_text(encoding="utf-8")
        if existing != rendered:
            print(
                f"Glossary markdown differs from generated output: {args.output}",
                file=sys.stderr,
            )
            return 1
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
