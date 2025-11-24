import sys
from pathlib import Path

# Ensure the repository root (project) is on sys.path so tests can import the
# `search` package using `from search.main import ...` when pytest changes the
# working directory during collection.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
