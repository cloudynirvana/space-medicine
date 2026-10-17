"""Project 5: does spaceflight change how the liver processes medicines?

Usage:  python -m p5_liver_drug_genes.run      (from the repo root)
"""
from pathlib import Path

from common import study_scan
from p5_liver_drug_genes.genes import GENES

OUT = Path(__file__).parent / "results"

if __name__ == "__main__":
    s = study_scan.run("Mus musculus", "liver", GENES, OUT, "liver drug-processing genes")
    print(s.head(25).to_string())
