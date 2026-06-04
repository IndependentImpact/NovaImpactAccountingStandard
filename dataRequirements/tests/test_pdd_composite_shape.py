import unittest
from pathlib import Path

from pyshacl import validate
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF, SH


REPO_ROOT = Path(__file__).resolve().parents[2]

SHAPE_FILES = [
    REPO_ROOT / "dataRequirements/common-shapes.ttl",
    REPO_ROOT / "dataRequirements/project-design-shapes.ttl",
    REPO_ROOT / "dataRequirements/impact-declaration-shapes.ttl",
    REPO_ROOT / "dataRequirements/document-shapes.ttl",
    REPO_ROOT / "dataRequirements/report-shapes.ttl",
    REPO_ROOT / "dataRequirements/stakeholder-engagement-shapes.ttl",
]

ONTOLOGY_FILES = [
    REPO_ROOT / "glossary/NovaImpactAccountingStandardOntology.ttl",
    REPO_ROOT / "glossary/NovaImpactAccountingStandardGlossary.ttl",
]

NIAS = Namespace("https://nova.org.za/novaimpactaccountingstandard/")
PDD_SCHEMA = URIRef(f"{NIAS}document-schema/PDD-1.0.0")

VALID_COMPOSITE_GRAPH = """
@prefix aiao: <http://w3id.org/aiao#> .
@prefix claimont: <http://w3id.org/claimont#> .
@prefix data: <https://jellyfiiish.xyz/ns/> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix hedera: <https://hashgraphontology.xyz/core/> .
@prefix impactont: <http://w3id.org/impactont#> .
@prefix infocomm: <http://w3id.org/infocomm#> .
@prefix meth: <http://independentimpact.org/methodology/> .
@prefix nias-cs: <https://nova.org.za/novaimpactaccountingstandard/> .
@prefix nias-o: <https://nova.org.za/novaimpactaccountingstandard/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix schema: <https://schema.org/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<https://nova.org.za/novaimpactaccountingstandard/projects/pdd-alpha>
    a aiao:Project ;
    nias-o:title "PDD Alpha Solar Irrigation Project" ;
    aiao:hasObjective [
        a aiao:Objective ;
        schema:description "Reduce diesel consumption for irrigation pumping."
    ] ;
    impactont:hasSpatialLocation [
        a impactont:SpatialLocation ;
        nias-o:resourceIpfsUri "ipfs://bafypddalphalocation"^^xsd:anyURI
    ] ;
    nias-o:technologyOrMeasure [
        a nias-o:TechnologyOrMeasure ;
        nias-o:techMeasType nias-cs:facility ;
        schema:description "Solar photovoltaic pump and inverter equipment." ;
        nias-o:currentAgeInYears 1 ;
        nias-o:estimatedLifespanInYears 20
    ] ;
    nias-o:projectParty [
        a nias-o:ProjectParty ;
        nias-o:partyName "PDD Alpha Project Developer" ;
        nias-o:isHostParty true ;
        nias-o:isParticipantParty true ;
        nias-o:publicPrivateClassification nias-cs:private ;
        nias-o:additionalInfo "Responsible for project implementation and maintenance."
    ] ;
    nias-o:legalMatters "No outstanding legal encumbrances." ;
    nias-o:publicFundingStatus false ;
    nias-o:projectHistory "The project replaces diesel pumping equipment used before 2026." ;
    nias-o:debundlingAssessment "The project is a standalone installation and is not debundled from a larger activity." ;
    nias-o:eligibilityDescription "The project meets the applicable renewable energy eligibility criteria." .

<https://nova.org.za/novaimpactaccountingstandard/impacts/pdd-alpha-landscape>
    a impactont:Impact ;
    nias-o:impactIntentionality nias-cs:unintentional ;
    nias-o:beneficialOrAdverse nias-cs:beneficial ;
    schema:description "Minor positive local air-quality co-benefit that will not be quantified." ;
    nias-o:monitored false ;
    nias-o:notMonitoredJustification "The co-benefit is expected to be immaterial relative to the primary monitored impact." .

<https://nova.org.za/novaimpactaccountingstandard/claims/pdd-alpha-impact-claim>
    a aiao:ImpactClaim ;
    claimont:hasSubject <https://nova.org.za/novaimpactaccountingstandard/projects/pdd-alpha> ;
    nias-o:usesMethodology <https://nova.org.za/novaimpactaccountingstandard/methodologies/nias-solar-001> .

<https://nova.org.za/novaimpactaccountingstandard/methodologies/nias-solar-001>
    a meth:Methodology ;
    rdfs:label "NIAS Solar Generation Methodology 1.0" .

<https://nova.org.za/novaimpactaccountingstandard/reports/pdd-alpha-section-a>
    a nias-o:PddSectionAReport ;
    claimont:isMadeBy <https://nova.org.za/novaimpactaccountingstandard/users/project-developer-1> ;
    claimont:hasSubject <https://nova.org.za/novaimpactaccountingstandard/projects/pdd-alpha> ;
    dcterms:conformsTo <https://nova.org.za/novaimpactaccountingstandard/document-schema/PDDxA-1.0.0> .

<https://nova.org.za/novaimpactaccountingstandard/reports/pdd-alpha-section-b>
    a nias-o:PddSectionBReport ;
    claimont:isMadeBy <https://nova.org.za/novaimpactaccountingstandard/users/project-developer-1> ;
    claimont:hasSubject <https://nova.org.za/novaimpactaccountingstandard/projects/pdd-alpha> ;
    nias-o:hasDeclaredImpact <https://nova.org.za/novaimpactaccountingstandard/impacts/pdd-alpha-landscape> ;
    nias-o:impactClaim <https://nova.org.za/novaimpactaccountingstandard/claims/pdd-alpha-impact-claim> ;
    nias-o:usesMethodology <https://nova.org.za/novaimpactaccountingstandard/methodologies/nias-solar-001> ;
    dcterms:conformsTo <https://nova.org.za/novaimpactaccountingstandard/document-schema/PDDxB-9.0.0> .

<https://nova.org.za/novaimpactaccountingstandard/documents/pdd-alpha-section-c>
    a data:Document,
        nias-o:PddSectionCStakeholderEngagement ;
    claimont:isMadeBy <https://nova.org.za/novaimpactaccountingstandard/users/project-developer-1> ;
    claimont:hasSubject <https://nova.org.za/novaimpactaccountingstandard/projects/pdd-alpha> ;
    dcterms:conformsTo <https://nova.org.za/novaimpactaccountingstandard/document-schema/PDDxC-4.0.0> ;
    nias-o:resourceIpfsUri "ipfs://bafypddsectionc"^^xsd:anyURI ;
    nias-o:documentSchema <https://nova.org.za/novaimpactaccountingstandard/document-schema/PDDxC-4.0.0> ;
    nias-o:isEncrypted false ;
    nias-o:documentAuthor <https://nova.org.za/novaimpactaccountingstandard/users/project-developer-1> ;
    nias-o:authProof nias-cs:eddsa-signature ;
    nias-o:hasWorkflowSubmission <https://nova.org.za/novaimpactaccountingstandard/submissions/pdd-alpha-section-c> ;
    nias-o:stakeholderEngagementModalities "In-person meetings and public notice periods in affected communities." ;
    nias-o:stakeholderCommentSummary "Stakeholders requested clear maintenance responsibilities and local training." ;
    nias-o:stakeholderCommentConsideration "The project design includes a local maintenance and training plan." .

<https://nova.org.za/novaimpactaccountingstandard/reports/pdd-alpha>
    a nias-o:PddReport ;
    claimont:isMadeBy <https://nova.org.za/novaimpactaccountingstandard/users/project-developer-1> ;
    claimont:hasSubject <https://nova.org.za/novaimpactaccountingstandard/projects/pdd-alpha> ;
    nias-o:hasPddSectionA <https://nova.org.za/novaimpactaccountingstandard/reports/pdd-alpha-section-a> ;
    nias-o:hasPddSectionB <https://nova.org.za/novaimpactaccountingstandard/reports/pdd-alpha-section-b> ;
    nias-o:hasPddSectionC <https://nova.org.za/novaimpactaccountingstandard/documents/pdd-alpha-section-c> ;
    dcterms:conformsTo <https://nova.org.za/novaimpactaccountingstandard/document-schema/PDD-1.0.0> .

<https://nova.org.za/novaimpactaccountingstandard/documents/pdd-alpha>
    a data:Document ;
    nias-o:resourceIpfsUri "ipfs://bafycompositepdd"^^xsd:anyURI ;
    nias-o:documentSchema <https://nova.org.za/novaimpactaccountingstandard/document-schema/PDD-1.0.0> ;
    nias-o:isEncrypted false ;
    nias-o:documentAuthor <https://nova.org.za/novaimpactaccountingstandard/users/project-developer-1> ;
    nias-o:authProof nias-cs:eddsa-signature ;
    nias-o:reportContent <https://nova.org.za/novaimpactaccountingstandard/reports/pdd-alpha> ;
    nias-o:hasWorkflowSubmission <https://nova.org.za/novaimpactaccountingstandard/submissions/pdd-alpha> .

<https://nova.org.za/novaimpactaccountingstandard/submissions/pdd-alpha-section-c>
    a nias-o:WorkflowDocumentSubmission ;
    nias-o:submittedDocument <https://nova.org.za/novaimpactaccountingstandard/documents/pdd-alpha-section-c> ;
    nias-o:workflow <https://nova.org.za/novaimpactaccountingstandard/workflows/pdd> ;
    nias-o:workflowStep [
        a nias-o:WorkflowStep ;
        rdfs:label "Submit PDD section C"
    ] ;
    nias-o:workflowSubject <https://nova.org.za/novaimpactaccountingstandard/projects/pdd-alpha> ;
    nias-o:workflowDocumentSubmittedBy <https://nova.org.za/novaimpactaccountingstandard/users/project-developer-1> ;
    nias-o:workflowDocumentRecipient <https://nova.org.za/novaimpactaccountingstandard/registry/nova-registry> ;
    nias-o:workflowSubmissionConsensusMessage [
        a hedera:TopicMessage ;
        hedera:inTopic [
            a hedera:ConsensusTopic ;
            hedera:hasTopicId "0.0.1001"
        ] ;
        hedera:hasConsensusTimestamp "2026-01-03T00:00:00Z"^^xsd:dateTimeStamp
    ] .

<https://nova.org.za/novaimpactaccountingstandard/submissions/pdd-alpha>
    a nias-o:WorkflowDocumentSubmission ;
    nias-o:submittedDocument <https://nova.org.za/novaimpactaccountingstandard/documents/pdd-alpha> ;
    nias-o:workflow <https://nova.org.za/novaimpactaccountingstandard/workflows/pdd> ;
    nias-o:workflowStep [
        a nias-o:WorkflowStep ;
        rdfs:label "Publish composite PDD"
    ] ;
    nias-o:workflowSubject <https://nova.org.za/novaimpactaccountingstandard/projects/pdd-alpha> ;
    nias-o:workflowDocumentSubmittedBy <https://nova.org.za/novaimpactaccountingstandard/users/project-developer-1> ;
    nias-o:workflowDocumentRecipient <https://nova.org.za/novaimpactaccountingstandard/registry/nova-registry> ;
    nias-o:workflowSubmissionConsensusMessage [
        a hedera:TopicMessage ;
        hedera:inTopic [
            a hedera:ConsensusTopic ;
            hedera:hasTopicId "0.0.1001"
        ] ;
        hedera:hasConsensusTimestamp "2026-01-04T00:00:00Z"^^xsd:dateTimeStamp
    ] .

<https://nova.org.za/novaimpactaccountingstandard/users/project-developer-1>
    a nias-o:PlatformUser .

<https://nova.org.za/novaimpactaccountingstandard/registry/nova-registry>
    a infocomm:CommunicationParty .

<https://nova.org.za/novaimpactaccountingstandard/workflows/pdd>
    a nias-o:Workflow .
"""

INVALID_COMPOSITE_GRAPH = VALID_COMPOSITE_GRAPH.replace(
    '    nias-o:hasPddSectionB <https://nova.org.za/novaimpactaccountingstandard/reports/pdd-alpha-section-b> ;\n',
    "",
)


def _load_graph(paths):
    graph = Graph()
    for path in paths:
        graph.parse(path)
    return graph


class PddCompositeShapeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shapes_graph = _load_graph(SHAPE_FILES)
        cls.ontology_graph = _load_graph(ONTOLOGY_FILES)
        cls.document_graph = _load_graph([REPO_ROOT / "dataRequirements/document-shapes.ttl"])
        cls.report_graph = _load_graph([REPO_ROOT / "dataRequirements/report-shapes.ttl"])

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

    def test_composite_pdd_graph_conforms(self):
        conforms, _, validation_text = self._validate_turtle(VALID_COMPOSITE_GRAPH)
        self.assertTrue(conforms, msg=validation_text)

    def test_composite_pdd_requires_all_sections(self):
        conforms, _, validation_text = self._validate_turtle(INVALID_COMPOSITE_GRAPH)
        self.assertFalse(conforms, msg="Composite PDD missing Section B should fail.")
        self.assertIn("hasPddSectionB", validation_text)

    def test_composite_pdd_schema_is_registered(self):
        self.assertIn((PDD_SCHEMA, RDF.type, NIAS.DocumentSchema), self.document_graph)
        self.assertIn((PDD_SCHEMA, NIAS.validatingShape, NIAS.PddReportShape), self.document_graph)

    def test_composite_pdd_section_order_is_stable(self):
        expected_orders = {
            NIAS.hasPddSectionA: 10,
            NIAS.hasPddSectionB: 20,
            NIAS.hasPddSectionC: 30,
        }

        for property_shape in self.report_graph.objects(NIAS.PddReportShape, SH.property):
            path = self.report_graph.value(property_shape, SH.path)
            order = self.report_graph.value(property_shape, SH.order)
            if path in expected_orders:
                self.assertEqual(int(order.toPython()), expected_orders[path])
                expected_orders.pop(path)

        self.assertEqual(expected_orders, {})


if __name__ == "__main__":
    unittest.main()
