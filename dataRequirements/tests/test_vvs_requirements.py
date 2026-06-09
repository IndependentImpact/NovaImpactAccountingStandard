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
from rdflib.namespace import DCTERMS, RDF


REPO_ROOT = Path(__file__).resolve().parents[2]
NIAS_BASE = "https://nova.org.za/novaimpactaccountingstandard/"
VVS_BASE = f"{NIAS_BASE}vvs/"

VVS_SHAPES_FILE = REPO_ROOT / "dataRequirements/vvs-requirement-shapes.ttl"
ARTIFACT_ANCHOR_SHAPES_FILE = REPO_ROOT / "dataRequirements/artifact-anchor-shapes.ttl"

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
EXACT_ANCHOR_MAPPING_FILE = MAPPINGS_DIR / "vvs-requirement-anchor-map.ttl"
ANCHOR_DEFINITION_FILES = [
    MAPPINGS_DIR / "pdd-anchor-definitions.ttl",
    MAPPINGS_DIR / "monitoring-anchor-definitions.ttl",
    MAPPINGS_DIR / "dlr-anchor-definitions.ttl",
]
DEPRECATION_MAP_FILE = MAPPINGS_DIR / "vvs-deprecation-map.ttl"


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

    def test_vvs_shapes_declares_all_requirement_shapes(self):
        from rdflib.namespace import SH
        from rdflib import URIRef

        NIAS = "https://nova.org.za/novaimpactaccountingstandard/"
        expected_shapes = [
            URIRef(f"{NIAS}ReqPdd001Shape"),
            URIRef(f"{NIAS}ReqPdd002Shape"),
            URIRef(f"{NIAS}ReqPdd003Shape"),
            URIRef(f"{NIAS}ReqPdd004Shape"),
            URIRef(f"{NIAS}ReqPdd005Shape"),
            URIRef(f"{NIAS}ReqDlr001Shape"),
            URIRef(f"{NIAS}ReqDlr002Shape"),
            URIRef(f"{NIAS}ReqMr001Shape"),
            URIRef(f"{NIAS}ReqMr002Shape"),
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
    """Positive and negative fixture tests for each active VVS requirement."""

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
    # REQ-PDD-003 — PDD-C schema conformance
    # ------------------------------------------------------------------

    def test_req_pdd_003_valid_fixture_conforms(self):
        self._assert_conforms("req-pdd-003-valid.ttl")

    def test_req_pdd_003_invalid_fixture_fails_with_requirement_message(self):
        self._assert_violates_requirement("req-pdd-003-invalid.ttl", "REQ-PDD-003")

    # ------------------------------------------------------------------
    # REQ-PDD-004 — Section-level qualitative review completion
    # ------------------------------------------------------------------

    def test_req_pdd_004_valid_fixture_conforms(self):
        self._assert_conforms("req-pdd-004-valid.ttl")

    def test_req_pdd_004_invalid_fixture_fails_with_requirement_message(self):
        self._assert_violates_requirement("req-pdd-004-invalid.ttl", "REQ-PDD-004")

    # ------------------------------------------------------------------
    # REQ-PDD-005 — Document-level qualitative review completion
    # ------------------------------------------------------------------

    def test_req_pdd_005_valid_fixture_conforms(self):
        self._assert_conforms("req-pdd-005-valid.ttl")

    def test_req_pdd_005_invalid_fixture_fails_with_requirement_message(self):
        self._assert_violates_requirement("req-pdd-005-invalid.ttl", "REQ-PDD-005")

    # ------------------------------------------------------------------
    # REQ-DLR-001 — Data Lineage Report evidence traceability
    # ------------------------------------------------------------------

    def test_req_dlr_001_valid_fixture_conforms(self):
        self._assert_conforms("req-dlr-001-valid.ttl")

    def test_req_dlr_001_invalid_fixture_fails_with_requirement_message(self):
        self._assert_violates_requirement("req-dlr-001-invalid.ttl", "REQ-DLR-001")

    # ------------------------------------------------------------------
    # REQ-DLR-002 — Data Lineage Report final dataset artifact
    # ------------------------------------------------------------------

    def test_req_dlr_002_valid_fixture_conforms(self):
        self._assert_conforms("req-dlr-002-valid.ttl")

    def test_req_dlr_002_invalid_fixture_fails_with_requirement_message(self):
        self._assert_violates_requirement("req-dlr-002-invalid.ttl", "REQ-DLR-002")

    # ------------------------------------------------------------------
    # REQ-MR-001 — Monitoring Report measured impact observation
    # ------------------------------------------------------------------

    def test_req_mr_001_valid_fixture_conforms(self):
        self._assert_conforms("req-mr-001-valid.ttl")

    def test_req_mr_001_invalid_fixture_fails_with_requirement_message(self):
        self._assert_violates_requirement("req-mr-001-invalid.ttl", "REQ-MR-001")

    # ------------------------------------------------------------------
    # REQ-MR-002 — Monitoring Report issuance account declaration
    # ------------------------------------------------------------------

    def test_req_mr_002_valid_fixture_conforms(self):
        self._assert_conforms("req-mr-002-valid.ttl")

    def test_req_mr_002_invalid_fixture_fails_with_requirement_message(self):
        self._assert_violates_requirement("req-mr-002-invalid.ttl", "REQ-MR-002")

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
            URIRef(f"{VVS_BASE}REQ-PDD-003"): URIRef(f"{NIAS_BASE}ReqPdd003Shape"),
            URIRef(f"{VVS_BASE}REQ-PDD-004"): URIRef(f"{NIAS_BASE}ReqPdd004Shape"),
            URIRef(f"{VVS_BASE}REQ-PDD-005"): URIRef(f"{NIAS_BASE}ReqPdd005Shape"),
            URIRef(f"{VVS_BASE}REQ-DLR-001"): URIRef(f"{NIAS_BASE}ReqDlr001Shape"),
            URIRef(f"{VVS_BASE}REQ-DLR-002"): URIRef(f"{NIAS_BASE}ReqDlr002Shape"),
            URIRef(f"{VVS_BASE}REQ-MR-001"): URIRef(f"{NIAS_BASE}ReqMr001Shape"),
            URIRef(f"{VVS_BASE}REQ-MR-002"): URIRef(f"{NIAS_BASE}ReqMr002Shape"),
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
            URIRef(f"{NIAS_BASE}PddSectionCReport"),
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


class VvsRequirementAnchorMappingsIntegrityTest(unittest.TestCase):
    """Exact requirement-to-anchor mapping integrity checks."""

    @classmethod
    def setUpClass(cls):
        cls.requirement_mapping = URIRef(f"{NIAS_BASE}RequirementMapping")
        cls.anchor_definition = URIRef(f"{NIAS_BASE}AnchorDefinition")
        cls.validation_requirement = URIRef(f"{NIAS_BASE}ValidationRequirement")
        cls.verification_requirement = URIRef(f"{NIAS_BASE}VerificationRequirement")

        cls.mapped_requirement = URIRef(f"{NIAS_BASE}mappedRequirement")
        cls.mapped_anchor = URIRef(f"{NIAS_BASE}mappedAnchor")
        cls.mapped_shape = URIRef(f"{NIAS_BASE}mappedShape")
        cls.review_mandate = URIRef(f"{NIAS_BASE}reviewMandate")
        cls.target_artifact_type = URIRef(f"{NIAS_BASE}targetArtifactType")
        cls.implemented_by_shape = URIRef(f"{NIAS_BASE}implementedByShape")
        cls.requirement_status = URIRef(f"{NIAS_BASE}requirementStatus")
        cls.active_status = URIRef(f"{VVS_BASE}active")
        cls.anchor_key = URIRef(f"{NIAS_BASE}anchorKey")
        cls.render_order = URIRef(f"{NIAS_BASE}renderOrder")
        cls.source_shape = URIRef(f"{NIAS_BASE}sourceShape")

        cls.validation_mandate = URIRef(f"{NIAS_BASE}validation")
        cls.verification_mandate = URIRef(f"{NIAS_BASE}verification")
        cls.allowed_mandates = {
            cls.validation_mandate,
            cls.verification_mandate,
        }
        cls.allowed_artifact_types = {
            "pdd",
            "monitoring-report",
            "data-lineage-report",
        }
        cls.coarse_anchor_classes = {
            URIRef(f"{NIAS_BASE}PddSectionAReport"),
            URIRef(f"{NIAS_BASE}PddSectionBReport"),
            URIRef(f"{NIAS_BASE}PddSectionCReport"),
            URIRef(f"{NIAS_BASE}DataLineageReport"),
            URIRef(f"{NIAS_BASE}MonitoringReport"),
        }

        cls.vvs_graph = Graph()
        cls.vvs_graph.parse(REPO_ROOT / "glossary/ValidationVerificationStandard.ttl")

        cls.mapping_graph = Graph()
        cls.mapping_graph.parse(EXACT_ANCHOR_MAPPING_FILE)

        cls.anchor_graph = _load_graph(ANCHOR_DEFINITION_FILES)

    def _active_requirements(self):
        return {
            requirement
            for requirement, _, _ in self.vvs_graph.triples(
                (None, self.requirement_status, self.active_status)
            )
        }

    def _mapping_subjects(self):
        return set(self.mapping_graph.subjects(RDF.type, self.requirement_mapping))

    def _mappings_for_requirement(self, requirement, mandate=None):
        mappings = set(
            self.mapping_graph.subjects(self.mapped_requirement, requirement)
        )
        if mandate is None:
            return mappings
        return {
            mapping
            for mapping in mappings
            if (mapping, self.review_mandate, mandate) in self.mapping_graph
        }

    def _single_value(self, subject, predicate):
        values = list(self.mapping_graph.objects(subject, predicate))
        self.assertEqual(
            len(values),
            1,
            msg=f"{subject} must declare exactly one {predicate}.",
        )
        return values[0]

    def test_exact_anchor_mapping_file_parses_without_errors(self):
        self.assertGreater(
            len(self.mapping_graph),
            0,
            msg="vvs-requirement-anchor-map.ttl must not be empty",
        )

    def test_anchor_definition_graph_conforms_to_anchor_shapes(self):
        conforms, _, validation_text = validate(
            data_graph=self.anchor_graph,
            shacl_graph=_load_graph([ARTIFACT_ANCHOR_SHAPES_FILE]),
            ont_graph=_load_graph(ONTOLOGY_FILES),
            inference="none",
            abort_on_first=False,
            allow_infos=False,
            allow_warnings=False,
            advanced=True,
        )
        self.assertTrue(conforms, msg=validation_text)

    def test_every_mapping_declares_required_fields(self):
        required_properties = [
            self.mapped_requirement,
            self.review_mandate,
            self.target_artifact_type,
            self.mapped_anchor,
            self.mapped_shape,
        ]
        mappings = self._mapping_subjects()
        self.assertGreater(len(mappings), 0, "At least one exact mapping is required.")
        for mapping in mappings:
            with self.subTest(mapping=mapping):
                for predicate in required_properties:
                    self._single_value(mapping, predicate)

    def test_every_active_requirement_has_exact_anchor_mapping(self):
        mapped_requirements = set(
            self.mapping_graph.objects(None, self.mapped_requirement)
        )
        self.assertEqual(
            self._active_requirements() - mapped_requirements,
            set(),
            msg="Every active VVS requirement must have at least one exact anchor mapping.",
        )

    def test_active_requirement_types_have_expected_mandate_coverage(self):
        validation_requirements = {
            requirement
            for requirement in self._active_requirements()
            if (requirement, RDF.type, self.validation_requirement) in self.vvs_graph
        }
        verification_requirements = {
            requirement
            for requirement in self._active_requirements()
            if (requirement, RDF.type, self.verification_requirement) in self.vvs_graph
        }

        for requirement in validation_requirements:
            with self.subTest(requirement=requirement, mandate="validation"):
                self.assertTrue(
                    self._mappings_for_requirement(
                        requirement,
                        self.validation_mandate,
                    ),
                    msg=f"{requirement} must have at least one validation exact-anchor mapping.",
                )

        for requirement in verification_requirements:
            with self.subTest(requirement=requirement, mandate="verification"):
                self.assertTrue(
                    self._mappings_for_requirement(
                        requirement,
                        self.verification_mandate,
                    ),
                    msg=f"{requirement} must have at least one verification exact-anchor mapping.",
                )

    def test_mapped_requirements_are_active_and_shape_linked(self):
        active_requirements = self._active_requirements()
        for mapping in self._mapping_subjects():
            requirement = self._single_value(mapping, self.mapped_requirement)
            mapped_shape = self._single_value(mapping, self.mapped_shape)
            mapping_mandate = self._single_value(mapping, self.review_mandate)
            with self.subTest(mapping=mapping):
                self.assertIn(
                    requirement,
                    active_requirements,
                    msg=f"{mapping} references inactive or unknown requirement {requirement}.",
                )
                self.assertIn(
                    (requirement, self.implemented_by_shape, mapped_shape),
                    self.vvs_graph,
                    msg=(
                        f"{mapping} must use the same SHACL shape that "
                        f"{requirement} declares with nias-o:implementedByShape."
                    ),
                )
                self.assertIn(
                    mapping_mandate,
                    set(self.vvs_graph.objects(requirement, self.review_mandate)),
                    msg=(
                        f"{mapping} mandate {mapping_mandate} must match a "
                        f"nias-o:reviewMandate declared by {requirement}."
                    ),
                )

    def test_mapped_anchors_are_known_anchor_definitions(self):
        for mapping in self._mapping_subjects():
            anchor = self._single_value(mapping, self.mapped_anchor)
            with self.subTest(mapping=mapping, anchor=anchor):
                self.assertIn(
                    (anchor, RDF.type, self.anchor_definition),
                    self.anchor_graph,
                    msg=f"{mapping} points to unknown anchor definition {anchor}.",
                )
                self.assertNotIn(
                    anchor,
                    self.coarse_anchor_classes,
                    msg=f"{mapping} must point to an exact AnchorDefinition, not a coarse artifact class.",
                )
                for predicate in [
                    self.anchor_key,
                    DCTERMS.title,
                    self.render_order,
                    self.source_shape,
                ]:
                    self.assertIn(
                        (anchor, predicate, None),
                        self.anchor_graph,
                        msg=f"Mapped anchor {anchor} must declare {predicate}.",
                    )

    def test_mapping_mandates_and_artifact_types_are_controlled(self):
        for mapping in self._mapping_subjects():
            mandate = self._single_value(mapping, self.review_mandate)
            artifact_type = self._single_value(mapping, self.target_artifact_type)
            with self.subTest(mapping=mapping):
                self.assertIn(mandate, self.allowed_mandates)
                self.assertIn(str(artifact_type), self.allowed_artifact_types)

    def test_no_duplicate_requirement_mandate_anchor_mappings(self):
        seen = set()
        for mapping in self._mapping_subjects():
            key = (
                self._single_value(mapping, self.mapped_requirement),
                self._single_value(mapping, self.review_mandate),
                self._single_value(mapping, self.target_artifact_type),
                self._single_value(mapping, self.mapped_anchor),
            )
            with self.subTest(mapping=mapping):
                self.assertNotIn(
                    key,
                    seen,
                    msg=f"Duplicate exact requirement-anchor mapping tuple: {key}",
                )
                seen.add(key)


class VvsRequirementDeprecationIntegrityTest(unittest.TestCase):
    """Phase 5 deprecation governance checks."""

    @classmethod
    def setUpClass(cls):
        cls.requirement_status = URIRef(f"{NIAS_BASE}requirementStatus")
        cls.requirement_id = URIRef(f"{NIAS_BASE}requirementId")
        cls.derived_from_rule = URIRef(f"{NIAS_BASE}derivedFromRule")
        cls.active_status = URIRef(f"{VVS_BASE}active")
        cls.deprecated_status = URIRef(f"{VVS_BASE}deprecated")
        cls.owl_deprecated = URIRef("http://www.w3.org/2002/07/owl#deprecated")
        cls.is_replaced_by = URIRef("http://purl.org/dc/terms/isReplacedBy")
        cls.boolean_true = {
            "true",
            "1",
            "True",
            "TRUE",
        }

        cls.vvs_graph = Graph()
        cls.vvs_graph.parse(REPO_ROOT / "glossary/ValidationVerificationStandard.ttl")

        cls.deprecation_map_graph = Graph()
        cls.deprecation_map_graph.parse(DEPRECATION_MAP_FILE)

    def _is_deprecated_node(self, node) -> bool:
        return any(
            str(value) in self.boolean_true
            for _, _, value in self.vvs_graph.triples((node, self.owl_deprecated, None))
        )

    def test_deprecation_map_file_parses_without_errors(self):
        self.assertGreater(
            len(self.deprecation_map_graph),
            0,
            msg="vvs-deprecation-map.ttl must not be empty",
        )

    def test_deprecated_terms_have_machine_readable_annotations(self):
        deprecated_requirements = {
            requirement
            for requirement, _, _ in self.vvs_graph.triples(
                (None, self.requirement_status, self.deprecated_status)
            )
        }
        self.assertGreater(
            len(deprecated_requirements),
            0,
            msg="Phase 5 requires at least one deprecated VVS term in ValidationVerificationStandard.ttl.",
        )

        for requirement in deprecated_requirements:
            with self.subTest(requirement=requirement):
                self.assertTrue(
                    self._is_deprecated_node(requirement),
                    msg=f"{requirement} must include owl:deprecated true.",
                )
                self.assertIn(
                    (requirement, self.is_replaced_by, None),
                    self.vvs_graph,
                    msg=f"{requirement} must include dcterms:isReplacedBy to its replacement requirement.",
                )

    def test_deprecation_map_targets_known_active_requirements(self):
        active_requirements = {
            requirement
            for requirement, _, _ in self.vvs_graph.triples(
                (None, self.requirement_status, self.active_status)
            )
        }
        for legacy_term, _, replacement in self.deprecation_map_graph.triples(
            (None, self.is_replaced_by, None)
        ):
            with self.subTest(legacy_term=legacy_term, replacement=replacement):
                self.assertIn(
                    (legacy_term, self.requirement_id, None),
                    self.vvs_graph,
                    msg=f"Deprecated term {legacy_term} must exist in ValidationVerificationStandard.ttl.",
                )
                self.assertTrue(
                    self._is_deprecated_node(legacy_term),
                    msg=f"Deprecated term {legacy_term} must have owl:deprecated true.",
                )
                self.assertIn(
                    replacement,
                    active_requirements,
                    msg=f"Replacement {replacement} must be an active VVS requirement.",
                )

    def test_active_requirements_do_not_depend_on_deprecated_controls(self):
        active_requirements = {
            requirement
            for requirement, _, _ in self.vvs_graph.triples(
                (None, self.requirement_status, self.active_status)
            )
        }
        for requirement in active_requirements:
            for _, _, control in self.vvs_graph.triples(
                (requirement, self.derived_from_rule, None)
            ):
                with self.subTest(requirement=requirement, control=control):
                    self.assertFalse(
                        self._is_deprecated_node(control),
                        msg=(
                            f"Active requirement {requirement} must not derive from deprecated "
                            f"control term {control}."
                        ),
                    )


if __name__ == "__main__":
    unittest.main()
