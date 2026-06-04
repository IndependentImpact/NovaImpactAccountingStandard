import unittest
from pathlib import Path

from pyshacl import validate
from rdflib import Graph


REPO_ROOT = Path(__file__).resolve().parents[2]

ARTIFACT_ANCHOR_SHAPES_FILE = REPO_ROOT / "dataRequirements/artifact-anchor-shapes.ttl"

ONTOLOGY_FILES = [
    REPO_ROOT / "glossary/NovaImpactAccountingStandardOntology.ttl",
    REPO_ROOT / "glossary/NovaImpactAccountingStandardGlossary.ttl",
]


VALID_ANCHOR_GRAPH = """
@prefix claimont: <http://w3id.org/claimont#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix nias-o: <https://nova.org.za/novaimpactaccountingstandard/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<https://example.org/anchor-definitions/pdd.sectionA.projectPurpose>
    a nias-o:AnchorDefinition ;
    nias-o:anchorKey "pdd.sectionA.projectPurpose" ;
    dcterms:title "A.1 Purpose And General Description" ;
    nias-o:sourceShape nias-o:PddSectionAReportShape ;
    nias-o:sourcePath claimont:hasSubject ;
    nias-o:renderOrder 110 .

<https://example.org/artifacts/pdd-alpha-v1/anchors/pdd.sectionA.projectPurpose>
    a nias-o:ArtifactAnchor ;
    nias-o:anchorDefinition <https://example.org/anchor-definitions/pdd.sectionA.projectPurpose> ;
    nias-o:anchorKey "pdd.sectionA.projectPurpose" ;
    dcterms:isPartOf <https://example.org/artifacts/pdd-alpha-v1> ;
    nias-o:sourceNode <https://example.org/reports/pdd-alpha-section-a> ;
    nias-o:sourcePath claimont:hasSubject ;
    nias-o:renderHeading "A.1 Purpose And General Description" ;
    nias-o:contentHash "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" .

<https://example.org/review-targets/pdd-alpha-project-purpose>
    a nias-o:ReviewTarget ;
    nias-o:reviewedArtifact <https://example.org/artifacts/pdd-alpha-v1> ;
    nias-o:reviewedAnchor <https://example.org/artifacts/pdd-alpha-v1/anchors/pdd.sectionA.projectPurpose> .
"""


INVALID_REVIEW_TARGET_GRAPH = """
@prefix nias-o: <https://nova.org.za/novaimpactaccountingstandard/> .

<https://example.org/review-targets/pdd-alpha-project-purpose>
    a nias-o:ReviewTarget ;
    nias-o:reviewedArtifact <https://example.org/artifacts/pdd-alpha-v1> .
"""


def _load_graph(paths):
    graph = Graph()
    for path in paths:
        graph.parse(path)
    return graph


class ArtifactAnchorShapeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shapes_graph = _load_graph([ARTIFACT_ANCHOR_SHAPES_FILE])
        cls.ontology_graph = _load_graph(ONTOLOGY_FILES)

    def _validate_turtle(self, turtle: str):
        data_graph = Graph()
        data_graph.parse(data=turtle, format="turtle")

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

    def test_artifact_anchor_shapes_parse(self):
        graph = Graph()
        graph.parse(ARTIFACT_ANCHOR_SHAPES_FILE)
        self.assertGreater(len(graph), 0, "artifact-anchor-shapes.ttl must not be empty")

    def test_review_target_with_artifact_anchor_conforms(self):
        conforms, _, validation_text = self._validate_turtle(VALID_ANCHOR_GRAPH)
        self.assertTrue(conforms, msg=validation_text)

    def test_review_target_requires_reviewed_anchor(self):
        conforms, _, validation_text = self._validate_turtle(INVALID_REVIEW_TARGET_GRAPH)
        self.assertFalse(conforms, msg="Review target without anchor should fail.")
        self.assertIn("reviewedAnchor", validation_text)


if __name__ == "__main__":
    unittest.main()
