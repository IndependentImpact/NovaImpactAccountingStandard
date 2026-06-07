import json
import unittest
from pathlib import Path

from rdflib import Graph


REPO_ROOT = Path(__file__).resolve().parents[2]
RELEASE_DIR = REPO_ROOT / "dataRequirements/releases/1.0.0"
MANIFEST = RELEASE_DIR / "semantic-standard-release-manifest.jsonld"

NIAS_RELEASE = (
    "https://nova.org.za/novaimpactaccountingstandard/releases/1.0.0/"
    "semantic-standard"
)

REQUIRED_ARTIFACT_ROLES = {
    "anchor-definitions",
    "concept-scheme",
    "exact-requirement-anchor-map",
    "export-config",
    "identity-contract-shapes",
    "ontology",
    "proof-shapes",
    "reference-fixture",
    "release-index",
    "rendering-profile",
    "requirement-shapes",
    "requirement-standard",
    "shacl-shapes",
    "shape2flutter-workflow",
    "ui-adapter-shapes",
}

REQUIRED_UI_WORKFLOWS = {
    "dataRequirements/shape2flutter/workflows/pdd-design.yaml",
    "dataRequirements/shape2flutter/workflows/validation-report.yaml",
    "dataRequirements/shape2flutter/workflows/monitoring-report.yaml",
    "dataRequirements/shape2flutter/workflows/verification-report.yaml",
}


def _manifest_payload():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def _manifest_graph_items():
    return _manifest_payload()["@graph"]


def _release_node():
    for item in _manifest_graph_items():
        if item.get("@id") == NIAS_RELEASE:
            return item
    raise AssertionError(f"Manifest does not declare release node {NIAS_RELEASE}.")


def _artifact_nodes():
    return [
        item
        for item in _manifest_graph_items()
        if item.get("@type") == "nias:ReleaseArtifact"
    ]


class SemanticStandardReleasePackageTests(unittest.TestCase):
    def test_release_manifest_jsonld_parses(self):
        graph = Graph()
        graph.parse(MANIFEST, format="json-ld")
        self.assertGreater(len(graph), 0)

    def test_release_node_links_every_artifact_once(self):
        release = _release_node()
        linked_artifacts = {
            artifact["@id"]
            for artifact in release["nias:releaseArtifact"]
        }
        artifact_ids = {artifact["@id"] for artifact in _artifact_nodes()}

        self.assertEqual(linked_artifacts, artifact_ids)
        self.assertEqual(len(linked_artifacts), len(release["nias:releaseArtifact"]))

    def test_artifacts_declare_required_manifest_fields(self):
        required_fields = {
            "@id",
            "@type",
            "dcterms:title",
            "nias:relativePath",
            "nias:artifactRole",
            "nias:sourceStatus",
            "nias:parseFormat",
            "nias:dependencyOrder",
        }
        for artifact in _artifact_nodes():
            with self.subTest(artifact=artifact.get("@id")):
                self.assertTrue(required_fields.issubset(artifact))
                self.assertIsInstance(artifact["nias:dependencyOrder"], int)

    def test_artifact_roles_cover_operating_model(self):
        roles = {artifact["nias:artifactRole"] for artifact in _artifact_nodes()}
        self.assertTrue(
            REQUIRED_ARTIFACT_ROLES.issubset(roles),
            msg=f"Missing release artifact roles: {REQUIRED_ARTIFACT_ROLES - roles}",
        )

    def test_manifest_includes_four_primary_ui_workflows(self):
        paths = {artifact["nias:relativePath"] for artifact in _artifact_nodes()}
        self.assertTrue(
            REQUIRED_UI_WORKFLOWS.issubset(paths),
            msg=f"Missing UI workflows: {REQUIRED_UI_WORKFLOWS - paths}",
        )

    def test_manifest_paths_exist_and_are_non_empty(self):
        for artifact in _artifact_nodes():
            relative_path = artifact["nias:relativePath"]
            path = REPO_ROOT / relative_path
            with self.subTest(path=relative_path):
                self.assertTrue(path.exists(), msg=f"{relative_path} is missing.")
                self.assertGreater(path.stat().st_size, 0)

    def test_rdf_release_artifacts_parse(self):
        rdf_formats = {
            "json-ld": "json-ld",
            "turtle": "turtle",
        }
        for artifact in _artifact_nodes():
            parse_format = artifact["nias:parseFormat"]
            if parse_format not in rdf_formats:
                continue
            relative_path = artifact["nias:relativePath"]
            path = REPO_ROOT / relative_path
            with self.subTest(path=relative_path):
                graph = Graph()
                graph.parse(path, format=rdf_formats[parse_format])
                self.assertGreater(len(graph), 0)

    def test_canonical_sources_do_not_point_to_generated_ui_outputs(self):
        for artifact in _artifact_nodes():
            if artifact["nias:sourceStatus"] != "canonical-source":
                continue
            relative_path = artifact["nias:relativePath"]
            with self.subTest(path=relative_path):
                self.assertNotIn("/generated/", relative_path)
                self.assertNotIn("pdd_workflow_shell/lib/generated", relative_path)


if __name__ == "__main__":
    unittest.main()
