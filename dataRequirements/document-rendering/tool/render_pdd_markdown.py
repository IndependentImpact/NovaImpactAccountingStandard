import argparse
import re
from pathlib import Path

from rdflib import Graph, URIRef
from rdflib.namespace import RDF, Namespace


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PROFILE = (
    REPO_ROOT / "dataRequirements/document-rendering/pdd-rendering-profile.md"
)
DEFAULT_UI_SHAPES = (
    REPO_ROOT / "dataRequirements/shape2flutter/pdd-workflow-ui-shapes.ttl"
)

SH = Namespace("http://www.w3.org/ns/shacl#")
UI = Namespace("https://shape2flutter.dev/vocab/ui#")
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


def main():
    parser = argparse.ArgumentParser(
        description="Generate a blank NIAS PDD Markdown template from the rendering profile."
    )
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
    parser.add_argument("--ui-shapes", type=Path, default=DEFAULT_UI_SHAPES)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    rendered = render_blank_template(args.profile, args.ui_shapes)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
