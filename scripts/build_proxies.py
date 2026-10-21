"""Build (and cache) the proxies of one or all scenarios.   python scripts/build_proxies.py [scenario ...] [--force]"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from pipeline import SCENARIOS, build_scenario

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    for name in args or SCENARIOS:
        build_scenario(name, force="--force" in sys.argv)
