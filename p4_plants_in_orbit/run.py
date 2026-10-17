"""Project 4: which stress genes do plants switch on when grown in orbit?

Usage:  python -m p4_plants_in_orbit.run      (from the repo root)
"""
from pathlib import Path

from common import study_scan
from p4_plants_in_orbit.genes import GENES

OUT = Path(__file__).parent / "results"

if __name__ == "__main__":
    # match on TAIR IDs and names; study_scan matches the 'symbol' column,
    # which for plant tables falls back to the TAIR ID when empty
    flat = {grp: list(d) + [n for n in d.values() if n] for grp, d in GENES.items()}
    s = study_scan.run("Arabidopsis thaliana", None, flat, OUT, "plant stress genes")
    print(s.to_string())
