"""Create a source release archive inside this project directory."""
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from src.path_security import project_path

root = Path(__file__).resolve().parents[1]
target = root / "实验八-v1.0.zip"
excluded = {"vendor", ".venv", ".pip-cache", ".tmp", "__pycache__", ".pytest_cache"}
with ZipFile(target, "w", ZIP_DEFLATED) as archive:
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            continue
        if path.is_file() and path != target and not set(path.relative_to(root).parts) & excluded:
            archive.write(project_path(path), Path("实验八") / path.relative_to(root))
print(target, target.stat().st_size)

