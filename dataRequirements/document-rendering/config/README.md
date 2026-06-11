# Export Config YAML Files

This directory contains YAML configuration files used by workflow-shell export
commands before they invoke document renderers.

Current configs:

- `pdd-export.yaml`
- `validation-report-export.yaml`
- `monitoring-report-export.yaml`
- `verification-report-export.yaml`
- `validation-verification-export.yaml` (legacy combined demo path)

## How These Files Fit The Rendering Flow

1. A workflow-shell export command builds a canonical JSON-LD payload.
2. The command loads one config file with
   `tooling/document-rendering/export_workflow_report.py:load_export_config`.
3. `run_renderer_with_payload` uses the config to:
   - select the renderer script;
   - choose a temporary payload filename;
   - choose default `--output-target` values when `--output-dir` is used.
4. The target renderer generates deterministic markdown/PDF/HTML outputs.

## YAML Syntax

Each config file is a YAML mapping with these required keys:

- `renderer_script`  
  Repository-relative path to the renderer CLI to execute.
- `payload_filename`  
  Filename for the temporary JSON-LD payload written during export.
- `default_output_targets`  
  YAML list of output targets used when the caller passes `--output-dir`
  without explicit targets. Example:
  ```yaml
  default_output_targets:
    - markdown
  ```

Optional key:

- `renderer_args`  
  Optional CLI arguments appended before any exporter-provided renderer args.
  Use this to pin renderer mode selectors such as `--report-type`.
- `final_gate_requirements`  
  Section-to-gate mapping used by `evaluate_final_gate_failures` for
  final-mode approval checks.

## When To Add A New Config File

Add a new config when you introduce a new workflow export path that needs a
different renderer, payload filename, or default output target set.

## How To Add One Safely

1. Copy the closest existing file in this directory.
2. Set:
   - `renderer_script` to the new/target renderer entry point in
     `tooling/document-rendering/`;
   - `payload_filename` to a unique descriptive filename;
   - `default_output_targets` to the expected default outputs.
   - `renderer_args` when the renderer needs fixed selector flags.
3. Update the relevant exporter script (for example under
   `dataRequirements/shape2flutter/.../tool/`) to point to the new config path.
4. Add or update tests in `dataRequirements/tests/test_workflow_export_engine.py`
   (and exporter-specific tests) to cover the new config behavior.
