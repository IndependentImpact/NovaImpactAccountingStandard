"""Tests for Principle, ScoringRules, and ReputationRules concept schemes.

Validates that:
  - Each TTL file parses correctly.
  - All concepts carry the required SKOS predicates (skos:prefLabel,
    skos:definition, skos:inScheme).
  - All concept schemes carry the required SKOS predicates (skos:prefLabel,
    skos:definition, skos:hasTopConcept).
  - Each concept scheme file conforms to its accompanying SHACL shapes file.
"""

import unittest
from pathlib import Path

from pyshacl import validate
from rdflib import Graph, Namespace, RDF

REPO_ROOT = Path(__file__).resolve().parents[2]
GLOSSARY = REPO_ROOT / "glossary"

SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")

# Pairs of (concept-scheme file, SHACL shapes file)
SCHEME_SHAPE_PAIRS = [
    (GLOSSARY / "Principle.ttl", GLOSSARY / "PrincipleShapes.ttl"),
    (GLOSSARY / "ScoringRules.ttl", GLOSSARY / "ScoringRulesShapes.ttl"),
    (GLOSSARY / "ReputationRules.ttl", GLOSSARY / "ReputationRulesShapes.ttl"),
]


def _load_graph(path: Path) -> Graph:
    g = Graph()
    g.parse(path)
    return g


class ConceptSchemeTtlParsingTests(unittest.TestCase):
    """Each new TTL file must parse without error."""

    def _assert_parses(self, path: Path):
        g = _load_graph(path)
        self.assertGreater(len(g), 0, msg=f"{path.name} should contain at least one triple")

    def test_principle_ttl_parses(self):
        self._assert_parses(GLOSSARY / "Principle.ttl")

    def test_scoring_rules_ttl_parses(self):
        self._assert_parses(GLOSSARY / "ScoringRules.ttl")

    def test_reputation_rules_ttl_parses(self):
        self._assert_parses(GLOSSARY / "ReputationRules.ttl")

    def test_principle_shapes_ttl_parses(self):
        self._assert_parses(GLOSSARY / "PrincipleShapes.ttl")

    def test_scoring_rules_shapes_ttl_parses(self):
        self._assert_parses(GLOSSARY / "ScoringRulesShapes.ttl")

    def test_reputation_rules_shapes_ttl_parses(self):
        self._assert_parses(GLOSSARY / "ReputationRulesShapes.ttl")


class ConceptSchemeSkosCompletenessTests(unittest.TestCase):
    """Every concept scheme and concept must carry required SKOS predicates."""

    def _assert_skos_complete(self, path: Path):
        g = _load_graph(path)
        errors = []

        for scheme in g.subjects(RDF.type, SKOS.ConceptScheme):
            if not list(g.objects(scheme, SKOS.prefLabel)):
                errors.append(f"Scheme {scheme} missing skos:prefLabel")
            if not list(g.objects(scheme, SKOS.definition)):
                errors.append(f"Scheme {scheme} missing skos:definition")
            if not list(g.objects(scheme, SKOS.hasTopConcept)):
                errors.append(f"Scheme {scheme} missing skos:hasTopConcept")

        for concept in g.subjects(RDF.type, SKOS.Concept):
            if not list(g.objects(concept, SKOS.prefLabel)):
                errors.append(f"Concept {concept} missing skos:prefLabel")
            if not list(g.objects(concept, SKOS.definition)):
                errors.append(f"Concept {concept} missing skos:definition")
            if not list(g.objects(concept, SKOS.inScheme)):
                errors.append(f"Concept {concept} missing skos:inScheme")

        self.assertFalse(
            errors,
            msg=f"{path.name} SKOS completeness errors:\n" + "\n".join(errors),
        )

    def test_principle_skos_complete(self):
        self._assert_skos_complete(GLOSSARY / "Principle.ttl")

    def test_scoring_rules_skos_complete(self):
        self._assert_skos_complete(GLOSSARY / "ScoringRules.ttl")

    def test_reputation_rules_skos_complete(self):
        self._assert_skos_complete(GLOSSARY / "ReputationRules.ttl")


class ConceptSchemeExpectedContentsTests(unittest.TestCase):
    """Expected concept schemes and concepts must be present in each file."""

    def _concepts_in_scheme(self, g: Graph, scheme_iri: str) -> set:
        from rdflib import URIRef
        return {
            str(c)
            for c in g.subjects(SKOS.inScheme, URIRef(scheme_iri))
        }

    def _scheme_iris(self, g: Graph) -> set:
        return {str(s) for s in g.subjects(RDF.type, SKOS.ConceptScheme)}

    def test_principle_has_impact_principle_scheme(self):
        g = _load_graph(GLOSSARY / "Principle.ttl")
        self.assertIn(
            "https://nova.org.za/novaimpactaccountingstandard/ImpactPrinciple",
            self._scheme_iris(g),
        )

    def test_principle_has_accounting_principle_scheme(self):
        g = _load_graph(GLOSSARY / "Principle.ttl")
        self.assertIn(
            "https://nova.org.za/novaimpactaccountingstandard/AccountingPrinciple",
            self._scheme_iris(g),
        )

    def test_impact_principle_has_six_concepts(self):
        g = _load_graph(GLOSSARY / "Principle.ttl")
        concepts = self._concepts_in_scheme(
            g, "https://nova.org.za/novaimpactaccountingstandard/ImpactPrinciple"
        )
        self.assertEqual(len(concepts), 6, msg=f"Expected 6 ImpactPrinciple concepts, got {concepts}")

    def test_accounting_principle_has_seven_concepts(self):
        g = _load_graph(GLOSSARY / "Principle.ttl")
        concepts = self._concepts_in_scheme(
            g, "https://nova.org.za/novaimpactaccountingstandard/AccountingPrinciple"
        )
        self.assertEqual(len(concepts), 7, msg=f"Expected 7 AccountingPrinciple concepts, got {concepts}")

    def test_scoring_rules_has_five_schemes(self):
        g = _load_graph(GLOSSARY / "ScoringRules.ttl")
        self.assertEqual(len(self._scheme_iris(g)), 5)

    def test_scoring_rules_review_mandate_has_validation_and_verification(self):
        g = _load_graph(GLOSSARY / "ScoringRules.ttl")
        concepts = self._concepts_in_scheme(
            g, "https://nova.org.za/novaimpactaccountingstandard/ReviewMandate"
        )
        base = "https://nova.org.za/novaimpactaccountingstandard/"
        self.assertIn(base + "validation", concepts)
        self.assertIn(base + "verification", concepts)

    def test_scoring_rules_indicator_quality_has_three_concepts(self):
        g = _load_graph(GLOSSARY / "ScoringRules.ttl")
        concepts = self._concepts_in_scheme(
            g, "https://nova.org.za/novaimpactaccountingstandard/IndicatorQualityDimension"
        )
        self.assertEqual(len(concepts), 3)

    def test_scoring_rules_methodology_quality_has_eleven_concepts(self):
        g = _load_graph(GLOSSARY / "ScoringRules.ttl")
        concepts = self._concepts_in_scheme(
            g, "https://nova.org.za/novaimpactaccountingstandard/MethodologyQualityDimension"
        )
        self.assertEqual(len(concepts), 11)

    def test_scoring_rules_instrument_quality_has_fourteen_concepts(self):
        g = _load_graph(GLOSSARY / "ScoringRules.ttl")
        concepts = self._concepts_in_scheme(
            g, "https://nova.org.za/novaimpactaccountingstandard/InstrumentQualityDimension"
        )
        self.assertEqual(len(concepts), 14)

    def test_reputation_rules_has_reputation_lifecycle_term_scheme(self):
        g = _load_graph(GLOSSARY / "ReputationRules.ttl")
        self.assertIn(
            "https://nova.org.za/novaimpactaccountingstandard/ReputationLifecycleTerm",
            self._scheme_iris(g),
        )

    def test_reputation_rules_has_five_concepts(self):
        g = _load_graph(GLOSSARY / "ReputationRules.ttl")
        concepts = self._concepts_in_scheme(
            g, "https://nova.org.za/novaimpactaccountingstandard/ReputationLifecycleTerm"
        )
        self.assertEqual(len(concepts), 5)


class ConceptSchemeShaclConformanceTests(unittest.TestCase):
    """Each concept scheme file must conform to its accompanying SHACL shapes."""

    def _assert_conforms(self, data_path: Path, shapes_path: Path):
        data_graph = _load_graph(data_path)
        shapes_graph = _load_graph(shapes_path)

        conforms, _, results_text = validate(
            data_graph=data_graph,
            shacl_graph=shapes_graph,
            inference="none",
            abort_on_first=False,
            allow_infos=False,
            allow_warnings=False,
            advanced=True,
        )

        self.assertTrue(
            conforms,
            msg=f"{data_path.name} does not conform to {shapes_path.name}:\n{results_text}",
        )

    def test_principle_conforms_to_principle_shapes(self):
        self._assert_conforms(GLOSSARY / "Principle.ttl", GLOSSARY / "PrincipleShapes.ttl")

    def test_scoring_rules_conforms_to_scoring_rules_shapes(self):
        self._assert_conforms(GLOSSARY / "ScoringRules.ttl", GLOSSARY / "ScoringRulesShapes.ttl")

    def test_reputation_rules_conforms_to_reputation_rules_shapes(self):
        self._assert_conforms(
            GLOSSARY / "ReputationRules.ttl", GLOSSARY / "ReputationRulesShapes.ttl"
        )


if __name__ == "__main__":
    unittest.main()
