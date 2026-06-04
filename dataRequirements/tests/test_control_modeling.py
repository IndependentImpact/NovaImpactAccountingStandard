import unittest
from pathlib import Path

from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF, RDFS


REPO_ROOT = Path(__file__).resolve().parents[2]
ONTOLOGY_FILE = REPO_ROOT / "glossary/NovaImpactAccountingStandardOntology.ttl"
VVS_FILE = REPO_ROOT / "glossary/ValidationVerificationStandard.ttl"

AIAO = Namespace("http://w3id.org/aiao#")
METH = Namespace("http://independentimpact.org/methodology/")
NIAS = Namespace("https://nova.org.za/novaimpactaccountingstandard/")


class ControlSubclassAxiomsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = Graph()
        cls.graph.parse(ONTOLOGY_FILE)

    def test_methodologies_rules_and_requirements_are_controls(self):
        expected_control_subclasses = [
            URIRef(f"{METH}Methodology"),
            URIRef(f"{NIAS}ScoringRule"),
            URIRef(f"{NIAS}DataParameterRequirement"),
            URIRef(f"{NIAS}ValidationVerificationRequirement"),
        ]
        for subject in expected_control_subclasses:
            with self.subTest(subject=subject):
                self.assertIn(
                    (subject, RDFS.subClassOf, AIAO.Control),
                    self.graph,
                    msg=f"{subject} must be marked as an aiao:Control subclass.",
                )

    def test_validation_and_verification_links_are_control_relations(self):
        expected_subproperties = [
            URIRef(f"{NIAS}validatedAt"),
            URIRef(f"{NIAS}verifiedBy"),
        ]
        for predicate in expected_subproperties:
            with self.subTest(predicate=predicate):
                self.assertIn(
                    (predicate, RDFS.subPropertyOf, AIAO.governs),
                    self.graph,
                    msg=f"{predicate} must be marked as a subproperty of aiao:governs.",
                )


class VvsRequirementControlLinksTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = Graph()
        cls.graph.parse(VVS_FILE)
        cls.requirement_id = URIRef(f"{NIAS}requirementId")
        cls.validated_at = URIRef(f"{NIAS}validatedAt")
        cls.verified_by = URIRef(f"{NIAS}verifiedBy")

    def _requirements(self):
        return {
            requirement
            for requirement, _, _ in self.graph.triples((None, self.requirement_id, None))
        }

    def test_every_requirement_resource_is_explicitly_a_control(self):
        for requirement in self._requirements():
            with self.subTest(requirement=requirement):
                self.assertIn(
                    (requirement, RDF.type, AIAO.Control),
                    self.graph,
                    msg=f"{requirement} must be explicitly typed as aiao:Control.",
                )

    def test_governance_links_have_explicit_inverse_triples(self):
        for requirement in self._requirements():
            anchors = {
                anchor
                for _, _, anchor in self.graph.triples((requirement, self.validated_at, None))
            } | {
                anchor
                for _, _, anchor in self.graph.triples((requirement, self.verified_by, None))
            }
            for anchor in anchors:
                with self.subTest(requirement=requirement, anchor=anchor):
                    self.assertIn(
                        (requirement, AIAO.governs, anchor),
                        self.graph,
                        msg=f"{requirement} must explicitly aiao:governs {anchor}.",
                    )
                    self.assertIn(
                        (anchor, AIAO.isGovernedBy, requirement),
                        self.graph,
                        msg=f"{anchor} must explicitly aiao:isGovernedBy {requirement}.",
                    )


if __name__ == "__main__":
    unittest.main()
