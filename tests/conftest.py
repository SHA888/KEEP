"""Put src/ on the path so the probe runs with no install: `python -m pytest -q`."""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))
