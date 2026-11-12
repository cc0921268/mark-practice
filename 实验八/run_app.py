"""Launch Streamlit with its home and config lookup confined to this project."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

from src.path_security import project_path


def isolated_environment() -> dict[str, str]:
    config_dir = project_path(ROOT / ".streamlit")
    config_dir.mkdir(exist_ok=True)
    project_path(ROOT / ".config")
    project_path(ROOT / ".cache")
    env = os.environ.copy()
    # Streamlit's global config path is Path.home() / '.streamlit'.
    env["USERPROFILE"] = str(ROOT)
    env["HOME"] = str(ROOT)
    env["XDG_CONFIG_HOME"] = str(ROOT / ".config")
    env["XDG_CACHE_HOME"] = str(ROOT / ".cache")
    env["MARKETING_OS_PROJECT_HOME"] = str(ROOT)
    env["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    return env


def main() -> int:
    env = isolated_environment()
    if "--check-config" in sys.argv:
        script = "from pathlib import Path; print(Path.home() / '.streamlit' / 'config.toml')"
        return subprocess.call([sys.executable, "-c", script], cwd=ROOT, env=env)
    return subprocess.call([sys.executable, "-m", "streamlit", "run", str(ROOT / "app.py"),
                            "--server.headless=true"], cwd=ROOT, env=env)


if __name__ == "__main__":
    raise SystemExit(main())

