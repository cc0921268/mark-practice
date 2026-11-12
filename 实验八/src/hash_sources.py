"""Print hashes for project data sources without modifying them."""
import hashlib
from pathlib import Path

from src.path_security import project_path

root = Path(__file__).resolve().parents[1]
for name in ("data/raw/reviews.csv", "data/processed/clean_data.csv",
             "data/processed/semantic_annotations.json", "data/processed/encoded_reviews.json"):
    path = root / name
    print(name, hashlib.sha256(project_path(path).read_bytes()).hexdigest())

