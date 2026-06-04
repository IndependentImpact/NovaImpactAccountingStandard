import re
import unittest
from pathlib import Path

from pyshacl import validate
from rdflib import Graph, Namespace, RDF
from rdflib.namespace import DCTERMS


REPO_ROOT = Path(__file__).resolve().parents[2]
PROFILE = REPO_ROOT / "dataRequirements/document-rendering/pdd-rendering-profile.md"
PDD_ANCHOR_DEFINITIONS = REPO_ROOT / "dataRequirements/mappings/pdd-anchor-definitions.ttl"
ARTIFACT_ANCHOR_SHAPES = REPO_ROOT / "dataRequirements/artifact-anchor-shapes.ttl"

ONTOLOGY_FILES = [
    REPO_ROOT / "glossary/NovaImpactAccountingStandardOntology.ttl",
    REPO_ROOT / "glossary/NovaImpactAccountingStandardGlossary.ttl",
]

NIAS = Namespace("https://nova.org.za/novaimpactaccountingstandard/")
DIRECTIVE_PATTERN = re.compile(r"^\{\{\s*render:\s*([^}\s]+)\s*\}\}$")
HEADING_PATTERN = re.compile(r"^(#{2,3})\s+(.+)$")


def _load_graph(paths):
    graph = Graph()
    for path in paths:
        graph.parse(path)
    return graph


def _profile_body():
    text = PROFILE.read_text(encoding="utf-8")
    marker = "---\n"
    if not text.startswith(marker):
        raise AssertionError("PDD rendering profile must start with YAML front matter.")
    end = text.find("\n---\n", len(marker))
    if end == -1:
        raise AssertionError("PDD rendering profile YAML front matter must be closed.")
    return text[end + len("\n---\n") :]


def _rendered_pdd_body_sections():
    entries = []
    current_heading = None
    in_pdd_body = False

    for raw_line in _profile_body().splitlines():
        line = raw_line.strip()
        if line == "## Section A. Description Of Project":
            in_pdd_body = True
        if line == "## Appendix A. Document And Process Metadata":
            break
        if not in_pdd_body:
            continue

        heading_match = HEADING_PATTERN.match(line)
        if heading_match:
            current_heading = heading_match.group(2).strip()
            continue

        directive_match = DIRECTIVE_PATTERN.match(line)
        if not directive_match or current_heading is None:
            continue

        directive = directive_match.group(1)
        if directive.startswith("pdd.section"):
            entries.append((directive, current_heading))
            current_heading = None

    return entries


def _anchor_definition_records(graph):
    records = []
    for subject in graph.subjects(RDF.type, NIAS.AnchorDefinition):
        key = graph.value(subject, NIAS.anchorKey)
        title = graph.value(subject, DCTERMS.title)
        order = graph.value(subject, NIAS.renderOrder)
        records.append(
            {
                "key": str(key),
                "subject": subject,
                "title": str(title) if title is not None else None,
                "order": int(order.toPython()) if order is not None else None,
            }
        )
    return records


def _anchor_definitions_by_key(records):
    return {
        record["key"]: {
            "subject": record["subject"],
            "title": record["title"],
            "order": record["order"],
        }
        for record in records
    }


class PddAnchorDefinitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.anchor_graph = _load_graph([PDD_ANCHOR_DEFINITIONS])
        cls.anchor_records = _anchor_definition_records(cls.anchor_graph)
        cls.anchor_definitions = _anchor_definitions_by_key(cls.anchor_records)
        cls.rendered_sections = _rendered_pdd_body_sections()

    def test_pdd_anchor_definitions_conform_to_artifact_anchor_shape(self):
        shapes_graph = _load_graph([ARTIFACT_ANCHOR_SHAPES])
        ontology_graph = _load_graph(ONTOLOGY_FILES)

        conforms, _, validation_text = validate(
            data_graph=self.anchor_graph,
            shacl_graph=shapes_graph,
            ont_graph=ontology_graph,
            inference="none",
            abort_on_first=False,
            allow_infos=False,
            allow_warnings=False,
            advanced=True,
        )

        self.assertTrue(conforms, msg=validation_text)

    def test_every_rendered_pdd_body_section_has_anchor_definition(self):
        self.assertEqual(
            len(self.rendered_sections),
            17,
            "The current PDD body profile should expose 17 section render targets.",
        )

        for directive, heading in self.rendered_sections:
            with self.subTest(directive=directive):
                self.assertIn(directive, self.anchor_definitions)
                self.assertEqual(self.anchor_definitions[directive]["title"], heading)

    def test_pdd_anchor_definitions_match_rendering_profile_order(self):
        profile_order = [directive for directive, _ in self.rendered_sections]
        anchor_order = [
            record["key"]
            for record in sorted(self.anchor_records, key=lambda record: record["order"])
        ]

        self.assertEqual(anchor_order, profile_order)

    def test_pdd_anchor_keys_and_render_orders_are_unique(self):
        keys = [record["key"] for record in self.anchor_records]
        subjects = [record["subject"] for record in self.anchor_records]
        orders = [record["order"] for record in self.anchor_records]

        self.assertEqual(len(subjects), len(set(subjects)))
        self.assertEqual(len(keys), len(set(keys)))
        self.assertEqual(len(orders), len(set(orders)))


if __name__ == "__main__":
    unittest.main()
