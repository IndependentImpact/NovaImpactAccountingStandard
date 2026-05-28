"""
Phase 2 VVS requirement shapes tests.

Tests cover:
  - TTL syntax validity of vvs-requirement-shapes.ttl
  - Positive fixtures (must conform) against VVS shapes only
  - Negative fixtures (must fail) against VVS shapes, asserting that the
    violation message contains the expected requirement ID
  - Zero regressions: existing pdd_workflow_shapes and pdd_workflow_gate tests
    are unaffected by the new shapes (verified by separate test modules)
"""

import unittest
from pathlib import Path

from pyshacl import validate
from rdflib import Graph


REPO_ROOT = Path(__file__).resolve().parents[2]

VVS_SHAPES_FILE = REPO_ROOT / "dataRequirements/vvs-requirement-shapes.ttl"

ONTOLOGY_FILES = [
    REPO_ROOT / "glossary/NovaImpactAccountingStandardOntology.ttl",
    REPO_ROOT / "glossary/NovaImpactAccountingStandardGlossary.ttl",
]

FIXTURES = REPO_ROOT / "dataRequirements/fixtures/vvs"


def _load_graph(paths):
    graph = Graph()
    for path in paths:
        graph.parse(path)
    return graph


class VvsRequirementShapesSyntaxTest(unittest.TestCase):
    """The shapes TTL must parse without errors."""

    def test_vvs_shapes_parses(self):
        graph = Graph()
        graph.parse(VVS_SHAPES_FILE)
        self.assertGreater(len(graph), 0, "vvs-requirement-shapes.ttl must not be empty")

    def test_vvs_shapes_declares_all_five_requirement_shapes(self):
        from rdflib.namespace import SH
        from rdflib import URIRef

        NIAS = "https://nova.org.za/novaimpactaccountingstandard/"
        expected_shapes = [
            URIRef(f"{NIAS}ReqPdd001Shape"),
            URIRef(f"{NIAS}ReqPdd002Shape"),
            URIRef(f"{NIAS}ReqDlr001Shape"),
            URIRef(f"{NIAS}ReqMr001Shape"),
            URIRef(f"{NIAS}ReqCross001Shape"),
        ]
        graph = Graph()
        graph.parse(VVS_SHAPES_FILE)
        for shape_iri in expected_shapes:
            self.assertIn(
                (shape_iri, SH.name, None),
                graph,
                msg=f"Shape {shape_iri} must have sh:name in vvs-requirement-shapes.ttl",
            )


class VvsRequirementShapesFixtureTest(unittest.TestCase):
    """Positive and negative fixture tests for each pilot VVS requirement."""

    @classmethod
    def setUpClass(cls):
        cls.shapes_graph = _load_graph([VVS_SHAPES_FILE])
        cls.ontology_graph = _load_graph(ONTOLOGY_FILES)

    def _validate_fixture(self, fixture_name: str):
        data_graph = Graph()
        data_graph.parse(FIXTURES / fixture_name)
        return validate(
            data_graph=data_graph,
            shacl_graph=self.shapes_graph,
            ont_graph=self.ontology_graph,
            inference="none",
            abort_on_first=False,
            allow_infos=False,
            allow_warnings=False,
            advanced=True,
        )

    def _assert_conforms(self, fixture_name: str):
        conforms, _, report_text = self._validate_fixture(fixture_name)
        self.assertTrue(
            conforms,
            msg=f"Fixture {fixture_name} should conform to VVS shapes.\n{report_text}",
        )

    def _assert_violates_requirement(self, fixture_name: str, requirement_id: str):
        conforms, _, report_text = self._validate_fixture(fixture_name)
        self.assertFalse(
            conforms,
            msg=(
                f"Fixture {fixture_name} should violate VVS shapes "
                f"(expected failure for {requirement_id})."
            ),
        )
        self.assertIn(
            requirement_id,
            report_text,
            msg=(
                f"Violation report for {fixture_name} must reference requirement "
                f"{requirement_id}.\nFull report:\n{report_text}"
            ),
        )

    # ------------------------------------------------------------------
    # REQ-PDD-001 — PDD-A structural completeness
    # ------------------------------------------------------------------

    def test_req_pdd_001_valid_fixture_conforms(self):
        self._assert_conforms("req-pdd-001-valid.ttl")

    def test_req_pdd_001_invalid_fixture_fails_with_requirement_message(self):
        self._assert_violates_requirement("req-pdd-001-invalid.ttl", "REQ-PDD-001")

    # ------------------------------------------------------------------
    # REQ-PDD-002 — PDD-B impact declaration completeness
    # ------------------------------------------------------------------

    def test_req_pdd_002_valid_fixture_conforms(self):
        self._assert_conforms("req-pdd-002-valid.ttl")

    def test_req_pdd_002_invalid_fixture_fails_with_requirement_message(self):
        self._assert_violates_requirement("req-pdd-002-invalid.ttl", "REQ-PDD-002")

    # ------------------------------------------------------------------
    # REQ-DLR-001 — Data Lineage Report evidence traceability
    # ------------------------------------------------------------------

    def test_req_dlr_001_valid_fixture_conforms(self):
        self._assert_conforms("req-dlr-001-valid.ttl")

    def test_req_dlr_001_invalid_fixture_fails_with_requirement_message(self):
        self._assert_violates_requirement("req-dlr-001-invalid.ttl", "REQ-DLR-001")

    # ------------------------------------------------------------------
    # REQ-MR-001 — Monitoring Report measured impact observation
    # ------------------------------------------------------------------

    def test_req_mr_001_valid_fixture_conforms(self):
        self._assert_conforms("req-mr-001-valid.ttl")

    def test_req_mr_001_invalid_fixture_fails_with_requirement_message(self):
        self._assert_violates_requirement("req-mr-001-invalid.ttl", "REQ-MR-001")

    # ------------------------------------------------------------------
    # REQ-CROSS-001 — Cross-artifact impact traceability
    # ------------------------------------------------------------------

    def test_req_cross_001_valid_fixture_conforms(self):
        self._assert_conforms("req-cross-001-valid.ttl")

    def test_req_cross_001_invalid_fixture_fails_with_requirement_message(self):
        self._assert_violates_requirement("req-cross-001-invalid.ttl", "REQ-CROSS-001")


class VvsImplementedByShapeLinksTest(unittest.TestCase):
    """Every pilot requirement must link to its implementing shape."""

    @classmethod
    def setUpClass(cls):
        from rdflib import URIRef
        from rdflib.namespace import RDF

        NIAS_O = "https://nova.org.za/novaimpactaccountingstandard/"
        VVS = f"{NIAS_O}vvs/"

        cls.IMPLEMENTED_BY_SHAPE = URIRef(f"{NIAS_O}implementedByShape")
        cls.expected_links = {
            URIRef(f"{VVS}REQ-PDD-001"): URIRef(f"{NIAS_O}ReqPdd001Shape"),
            URIRef(f"{VVS}REQ-PDD-002"): URIRef(f"{NIAS_O}ReqPdd002Shape"),
            URIRef(f"{VVS}REQ-DLR-001"): URIRef(f"{NIAS_O}ReqDlr001Shape"),
            URIRef(f"{VVS}REQ-MR-001"): URIRef(f"{NIAS_O}ReqMr001Shape"),
            URIRef(f"{VVS}REQ-CROSS-001"): URIRef(f"{NIAS_O}ReqCross001Shape"),
        }
        cls.vvs_graph = Graph()
        cls.vvs_graph.parse(REPO_ROOT / "glossary/ValidationVerificationStandard.ttl")

    def test_all_pilot_requirements_have_implemented_by_shape_link(self):
        for req_iri, shape_iri in self.expected_links.items():
            with self.subTest(requirement=str(req_iri)):
                self.assertIn(
                    (req_iri, self.IMPLEMENTED_BY_SHAPE, shape_iri),
                    self.vvs_graph,
                    msg=(
                        f"{req_iri} must declare "
                        f"nias-o:implementedByShape {shape_iri} "
                        f"in ValidationVerificationStandard.ttl"
                    ),
                )


if __name__ == "__main__":
    unittest.main()
