"""Project 3: which genes drive muscle and bone loss in space, and are there drugs for them?

Usage:  python -m p3_muscle_bone.run      (from the repo root)
"""
from pathlib import Path

import pandas as pd

from common import study_scan
from p3_muscle_bone.genes import GENES, HUMAN

HERE = Path(__file__).parent

if __name__ == "__main__":
    muscle = study_scan.run("Mus musculus", "soleus", GENES, HERE / "results" / "soleus", "muscle and bone genes")
    for tissue in ("gastrocnemius", "quadriceps", "femur"):
        study_scan.run("Mus musculus", tissue, GENES, HERE / "results" / tissue, "muscle and bone genes")
    drugs = pd.read_csv(HERE / "drug_targets.csv")
    changed = muscle[(muscle.studies_up + muscle.studies_down) > 0].index
    hits = drugs[drugs.mouse_gene.isin(changed)]
    hits.to_csv(HERE / "results" / "changed_genes_with_drugs.csv", index=False)
    print(hits.to_string(index=False))
