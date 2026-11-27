"""Package locations, resolved from this file: <skill>/scripts/runtime/paths.py."""
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = SKILL_ROOT / 'scripts'
ASSETS = SKILL_ROOT / 'assets'
