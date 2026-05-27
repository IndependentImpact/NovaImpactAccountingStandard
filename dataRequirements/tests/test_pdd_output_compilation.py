import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from rdflib import Graph


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "dataRequirements/document-rendering/tool/render_pdd_markdown.py"
VALID_TTL_INPUT = REPO_ROOT / "dataRequirements/fixtures/phase7/impact-monitored-valid.ttl"
INVALID_INPUT = (
    REPO_ROOT / "dataRequirements/document-rendering/fixtures/pdd-alpha-input.jsonld"
)


class PddOutputCompilationTests(unittest.TestCase):
    def _write_fake_pandoc(self, path: Path):
        path.write_text(
            "\n".join(
                [
                    "#!/usr/bin/env python3",
                    "import json",
                    "import os",
                    "import pathlib",
                    "import sys",
                    "args = sys.argv[1:]",
                    "args_path = os.environ.get('FAKE_PANDOC_ARGS_PATH')",
                    "if args_path:",
                    "    pathlib.Path(args_path).write_text(json.dumps(args), encoding='utf-8')",
                    "source = pathlib.Path(args[0])",
                    "output = pathlib.Path(args[args.index('--output') + 1])",
                    "header = None",
                    "if '--include-in-header' in args:",
                    "    header = pathlib.Path(args[args.index('--include-in-header') + 1]).read_text(encoding='utf-8')",
                    "if output.suffix == '.html':",
                    "    output.write_text('<html><body>' + source.read_text(encoding='utf-8') + '</body></html>', encoding='utf-8')",
                    "else:",
                    "    payload = source.read_text(encoding='utf-8')",
                    "    if header:",
                    "        payload += '\\n' + header",
                    "    output.write_bytes(payload.encode('utf-8'))",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        path.chmod(0o755)

    def test_final_export_writes_deterministic_targets_and_sidecars(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            final_input = tmp_path / "impact-monitored-valid.jsonld"
            graph = Graph()
            graph.parse(VALID_TTL_INPUT, format="turtle")
            graph.serialize(destination=final_input, format="json-ld")

            fake_pandoc = tmp_path / "pandoc"
            self._write_fake_pandoc(fake_pandoc)

            output_dir = tmp_path / "exported"
            env = os.environ.copy()
            env["PATH"] = f"{tmp_path}{os.pathsep}{env.get('PATH', '')}"

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--input-jsonld",
                    str(final_input),
                    "--source-artifact-id",
                    "impact-monitored-valid.jsonld",
                    "--generated-at",
                    "2026-05-26T00:00:00Z",
                    "--render-mode",
                    "final",
                    "--output-dir",
                    str(output_dir),
                    "--output-target",
                    "markdown",
                    "--output-target",
                    "pdf",
                    "--output-target",
                    "html",
                ],
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                cwd=REPO_ROOT,
                env=env,
            )

            markdown = output_dir / "pdd.md"
            pdf = output_dir / "pdd.pdf"
            html = output_dir / "pdd.html"
            metadata = output_dir / "pdd.metadata.jsonld"
            validation = output_dir / "pdd.validation.json"

            self.assertTrue(markdown.exists())
            self.assertTrue(pdf.exists())
            self.assertTrue(html.exists())
            self.assertTrue(metadata.exists())
            self.assertTrue(validation.exists())

            self.assertIn(
                "## Section A. Description Of Project",
                markdown.read_text(encoding="utf-8"),
            )
            pdf_bytes = pdf.read_bytes()
            self.assertTrue(pdf_bytes.startswith(b"%PDF-"))
            self.assertIn(b"%%EOF", pdf_bytes[-1024:])
            self.assertIn(b"Document ID: pdd-", pdf_bytes)

            metadata_payload = json.loads(metadata.read_text(encoding="utf-8"))
            artifact_types = {
                artifact["artifact"]
                for artifact in metadata_payload["nias:artifacts"]
            }
            self.assertEqual(artifact_types, {"markdown", "pdf", "website"})

            validation_payload = json.loads(validation.read_text(encoding="utf-8"))
            self.assertEqual(validation_payload["status"], "passed")
            self.assertEqual(validation_payload["renderMode"], "final")

    def test_pdf_compilation_defaults_to_xelatex(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            fake_pandoc = tmp_path / "pandoc"
            fake_args = tmp_path / "pandoc-args.json"
            self._write_fake_pandoc(fake_pandoc)

            output_dir = tmp_path / "exported"
            env = os.environ.copy()
            env["PATH"] = f"{tmp_path}{os.pathsep}{env.get('PATH', '')}"
            env["FAKE_PANDOC_ARGS_PATH"] = str(fake_args)

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--input-jsonld",
                    str(INVALID_INPUT),
                    "--render-mode",
                    "draft",
                    "--output-dir",
                    str(output_dir),
                    "--output-target",
                    "pdf",
                ],
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                cwd=REPO_ROOT,
                env=env,
            )

            args = json.loads(fake_args.read_text(encoding="utf-8"))
            self.assertIn("--pdf-engine", args)
            self.assertEqual(args[args.index("--pdf-engine") + 1], "xelatex")

    def test_pdf_compilation_allows_engine_override(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            fake_pandoc = tmp_path / "pandoc"
            fake_args = tmp_path / "pandoc-args.json"
            self._write_fake_pandoc(fake_pandoc)

            output_dir = tmp_path / "exported"
            env = os.environ.copy()
            env["PATH"] = f"{tmp_path}{os.pathsep}{env.get('PATH', '')}"
            env["FAKE_PANDOC_ARGS_PATH"] = str(fake_args)
            env["PANDOC_PDF_ENGINE"] = "lualatex"

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--input-jsonld",
                    str(INVALID_INPUT),
                    "--render-mode",
                    "draft",
                    "--output-dir",
                    str(output_dir),
                    "--output-target",
                    "pdf",
                ],
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                cwd=REPO_ROOT,
                env=env,
            )

            args = json.loads(fake_args.read_text(encoding="utf-8"))
            self.assertIn("--pdf-engine", args)
            self.assertEqual(args[args.index("--pdf-engine") + 1], "lualatex")

    def test_blank_template_pdf_output_is_valid_pdf(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "exported"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--output-dir",
                    str(output_dir),
                    "--output-target",
                    "pdf",
                ],
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                cwd=REPO_ROOT,
                env={"PATH": "", "PANDOC_BIN": str(Path(tmpdir) / "missing-pandoc")},
            )
            pdf = output_dir / "pdd.pdf"
            self.assertTrue(pdf.exists())
            pdf_bytes = pdf.read_bytes()
            self.assertTrue(pdf_bytes.startswith(b"%PDF-"))
            self.assertIn(b"%%EOF", pdf_bytes[-1024:])
            self.assertIn(b"Document ID: pdd-", pdf_bytes)

    def test_draft_pdf_output_succeeds_without_pandoc(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "exported"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--input-jsonld",
                    str(INVALID_INPUT),
                    "--render-mode",
                    "draft",
                    "--output-dir",
                    str(output_dir),
                    "--output-target",
                    "pdf",
                ],
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                cwd=REPO_ROOT,
                env={"PATH": "", "PANDOC_BIN": str(Path(tmpdir) / "missing-pandoc")},
            )
            pdf = output_dir / "pdd.pdf"
            self.assertTrue(pdf.exists())
            pdf_bytes = pdf.read_bytes()
            self.assertTrue(pdf_bytes.startswith(b"%PDF-"))
            self.assertIn(b"%%EOF", pdf_bytes[-1024:])
            self.assertIn(b"Document ID: pdd-", pdf_bytes)
            self.assertNotIn(b"pageref", pdf_bytes)
            pdf_text = pdf_bytes.decode("latin-1", errors="ignore")
            first_footer_start = pdf_text.index("Document ID: pdd-")
            first_footer_end = pdf_text.index(") Tj", first_footer_start)
            self.assertNotIn("Page", pdf_text[first_footer_start:first_footer_end])
            self.assertIn("Page i", pdf_text)

    def test_html_compilation_failure_surfaces_clear_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "exported"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--input-jsonld",
                    str(INVALID_INPUT),
                    "--render-mode",
                    "draft",
                    "--output-dir",
                    str(output_dir),
                    "--output-target",
                    "html",
                ],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                cwd=REPO_ROOT,
                env={"PATH": "", "PANDOC_BIN": str(Path(tmpdir) / "missing-pandoc")},
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("Pandoc command `pandoc` was not found", completed.stderr)


if __name__ == "__main__":
    unittest.main()
