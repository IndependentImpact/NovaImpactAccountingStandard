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
from rdflib import Graph, URIRef


REPO_ROOT = Path(__file__).resolve().parents[2]
NIAS_BASE = "https://nova.org.za/novaimpactaccountingstandard/"
VVS_BASE = f"{NIAS_BASE}vvs/"

VVS_SHAPES_FILE = REPO_ROOT / "dataRequirements/vvs-requirement-shapes.ttl"

ONTOLOGY_FILES = [
    REPO_ROOT / "glossary/NovaImpactAccountingStandardOntology.ttl",
    REPO_ROOT / "glossary/NovaImpactAccountingStandardGlossary.ttl",
]

FIXTURES = REPO_ROOT / "dataRequirements/fixtures/vvs"
MAPPINGS_DIR = REPO_ROOT / "dataRequirements/mappings"
MAPPING_FILES = [
    MAPPINGS_DIR / "pdd-requirement-map.ttl",
    MAPPINGS_DIR / "dlr-requirement-map.ttl",
    MAPPINGS_DIR / "mr-requirement-map.ttl",
]


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
        cls.IMPLEMENTED_BY_SHAPE = URIRef(f"{NIAS_BASE}implementedByShape")
        cls.expected_links = {
            URIRef(f"{VVS_BASE}REQ-PDD-001"): URIRef(f"{NIAS_BASE}ReqPdd001Shape"),
            URIRef(f"{VVS_BASE}REQ-PDD-002"): URIRef(f"{NIAS_BASE}ReqPdd002Shape"),
            URIRef(f"{VVS_BASE}REQ-DLR-001"): URIRef(f"{NIAS_BASE}ReqDlr001Shape"),
            URIRef(f"{VVS_BASE}REQ-MR-001"): URIRef(f"{NIAS_BASE}ReqMr001Shape"),
            URIRef(f"{VVS_BASE}REQ-CROSS-001"): URIRef(f"{NIAS_BASE}ReqCross001Shape"),
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


class VvsRequirementMappingsIntegrityTest(unittest.TestCase):
    """Phase 3 mapping graph integrity checks."""

    @classmethod
    def setUpClass(cls):
        cls.validated_at = URIRef(f"{NIAS_BASE}validatedAt")
        cls.verified_by = URIRef(f"{NIAS_BASE}verifiedBy")
        cls.implemented_by_shape = URIRef(f"{NIAS_BASE}implementedByShape")
        cls.requirement_status = URIRef(f"{NIAS_BASE}requirementStatus")
        cls.active_status = URIRef(f"{VVS_BASE}active")
        cls.requirement_id = URIRef(f"{NIAS_BASE}requirementId")
        cls.known_anchors = {
            URIRef(f"{NIAS_BASE}PddSectionAReport"),
            URIRef(f"{NIAS_BASE}PddSectionBReport"),
            URIRef(f"{NIAS_BASE}DataLineageReport"),
            URIRef(f"{NIAS_BASE}MonitoringReport"),
        }

        cls.vvs_graph = Graph()
        cls.vvs_graph.parse(REPO_ROOT / "glossary/ValidationVerificationStandard.ttl")

        cls.mapping_graph = _load_graph(MAPPING_FILES)

    def _mapped_requirements(self):
        return {
            req
            for req, _, _ in self.mapping_graph.triples((None, self.validated_at, None))
        } | {
            req
            for req, _, _ in self.mapping_graph.triples((None, self.verified_by, None))
        }

    def test_mapping_files_parse_without_errors(self):
        for mapping_file in MAPPING_FILES:
            with self.subTest(file=mapping_file.name):
                graph = Graph()
                graph.parse(mapping_file)
                self.assertGreater(
                    len(graph),
                    0,
                    msg=f"{mapping_file.name} must not be empty",
                )

    def test_every_active_requirement_has_mapping_triples(self):
        active_requirements = {
            requirement
            for requirement, _, _ in self.vvs_graph.triples(
                (None, self.requirement_status, self.active_status)
            )
        }
        mapped_requirements = self._mapped_requirements()
        self.assertEqual(
            active_requirements - mapped_requirements,
            set(),
            msg=(
                "Every active requirement must have at least one Phase 3 mapping triple "
                "(nias-o:validatedAt or nias-o:verifiedBy)."
            ),
        )

    def test_every_active_requirement_has_validation_and_verification_anchor(self):
        active_requirements = {
            requirement
            for requirement, _, _ in self.vvs_graph.triples(
                (None, self.requirement_status, self.active_status)
            )
        }
        for requirement in active_requirements:
            with self.subTest(requirement=requirement):
                self.assertIn(
                    (requirement, self.validated_at, None),
                    self.mapping_graph,
                    msg=(
                        f"{requirement} must have at least one mapped PDD validation "
                        "anchor in Phase 3 mappings."
                    ),
                )
                self.assertIn(
                    (requirement, self.verified_by, None),
                    self.mapping_graph,
                    msg=(
                        f"{requirement} must have at least one mapped DLR or MR "
                        "verification anchor in Phase 3 mappings."
                    ),
                )

    def test_mapping_subjects_reference_known_requirements(self):
        for requirement in self._mapped_requirements():
            with self.subTest(requirement=requirement):
                self.assertIn(
                    (requirement, self.requirement_id, None),
                    self.vvs_graph,
                    msg=(
                        f"Mapped requirement {requirement} must exist in "
                        "ValidationVerificationStandard.ttl with nias-o:requirementId."
                    ),
                )

    def test_mapped_requirements_have_shape_links(self):
        for requirement in self._mapped_requirements():
            with self.subTest(requirement=requirement):
                self.assertIn(
                    (requirement, self.implemented_by_shape, None),
                    self.vvs_graph,
                    msg=(
                        f"Mapped requirement {requirement} must include "
                        "nias-o:implementedByShape in ValidationVerificationStandard.ttl."
                    ),
                )

    def test_mappings_only_reference_known_anchor_classes(self):
        for requirement, _, anchor in self.mapping_graph.triples(
            (None, self.validated_at, None)
        ):
            with self.subTest(requirement=requirement, anchor=anchor):
                self.assertIn(
                    anchor,
                    self.known_anchors,
                    msg=(
                        f"Mapped validation anchor {anchor} is not a supported "
                        "Phase 3 anchor class."
                    ),
                )

        for requirement, _, anchor in self.mapping_graph.triples(
            (None, self.verified_by, None)
        ):
            with self.subTest(requirement=requirement, anchor=anchor):
                self.assertIn(
                    anchor,
                    self.known_anchors,
                    msg=(
                        f"Mapped verification anchor {anchor} is not a supported "
                        "Phase 3 anchor class."
                    ),
                )


if __name__ == "__main__":
    unittest.main()
