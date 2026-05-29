import os
import tempfile
from pathlib import Path


def load_repo_env(repo_root: Path) -> None:
    """Load simple KEY=VALUE settings from the repository .env file."""
    env_path = Path(repo_root) / ".env"
    if env_path.exists():
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[len("export ") :].lstrip()
            key, separator, value = line.partition("=")
            if not separator:
                continue
            key = key.strip()
            if not key or not key.replace("_", "").isalnum():
                continue
            value = value.strip().strip("'\"")
            value = os.path.expandvars(os.path.expanduser(value))
            os.environ.setdefault(key, value)

    tmp_dir = os.environ.get("NIAS_TMP_DIR")
    if tmp_dir:
        tmp_path = Path(os.path.expandvars(os.path.expanduser(tmp_dir)))
        tmp_path.mkdir(parents=True, exist_ok=True)
        tmp_value = str(tmp_path)
        os.environ["NIAS_TMP_DIR"] = tmp_value
        os.environ["TMPDIR"] = tmp_value
        os.environ["TEMP"] = tmp_value
        os.environ["TMP"] = tmp_value
        tempfile.tempdir = tmp_value
