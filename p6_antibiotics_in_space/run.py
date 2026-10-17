"""Project 6: would antibiotics behave differently in space?

For each common antibiotic, finds the genes that clear it from the body and asks how
NASA's spaceflight mice changed those genes, pooled across missions.
Usage:  python -m p6_antibiotics_in_space.run   (after p5 and meta_analysis.py)
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import meta, study_scan
from common.plots import UP, DOWN, NS
from p6_antibiotics_in_space.genes import GUT_GENES, KIDNEY_GENES

HERE = Path(__file__).parent
OUT = HERE / "results"
LIVER_META = HERE.parent / "p5_liver_drug_genes" / "results" / "meta_analysis_all_genes.csv"
FDR = 0.05


def kidney_meta() -> pd.DataFrame:
    accs = sorted(set(study_scan.find_studies("Mus musculus", "left kidney"))
                  | set(study_scan.find_studies("Mus musculus", "kidney")),
                  key=lambda s: int(s.split("-")[1]))
    study_scan.run("Mus musculus", "kidney", KIDNEY_GENES, OUT / "kidney", "kidney antibiotic genes", accs)
    tables = meta.load_per_study(OUT / "kidney" / "per_study")
    m = meta.stouffer(tables)
    m["robust"] = (m.fdr < FDR) & (m.leave_one_out_p < 0.05)
    m.to_csv(OUT / "kidney" / "meta_analysis_all_genes.csv")
    print(f"kidney: {len(tables)} studies pooled")
    return m, len(tables)


def verdict(r) -> str:
    if r.studies != r.studies or r.studies == 0:
        return "not measured"
    if r.robust:
        return "higher in space" if r.combined_z > 0 else "lower in space"
    if r.fdr < FDR:
        return "leans higher (not robust)" if r.combined_z > 0 else "leans lower (not robust)"
    return "no clear change"


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    kid, n_kid = kidney_meta()
    study_scan.run("Mus musculus", "colon", GUT_GENES, OUT / "colon", "colon absorption genes")
    liver = pd.read_csv(LIVER_META, index_col=0)
    n_liv = len(list((LIVER_META.parent / "per_study").glob("*_all_genes.csv")))

    drugs = pd.read_csv(HERE / "antibiotics.csv")
    rows = []
    for _, d in drugs.iterrows():
        genes = [g.strip() for g in str(d.clearance_genes_mouse).split(";") if g.strip() and d.clearance_genes_mouse == d.clearance_genes_mouse]
        if not genes:
            rows.append({**d, "gene": "", "verdict": "no clearance gene to test"})
            continue
        src = kid if d.organ == "kidney" else liver
        for g in genes:
            r = src.loc[g] if g in src.index else pd.Series({"studies": 0})
            rows.append({**d, "gene": g, "studies": r.get("studies"), "studies_same_direction": r.get("studies_same_direction"),
                         "mean_log2fc": r.get("mean_log2fc"), "combined_z": r.get("combined_z"), "fdr": r.get("fdr"),
                         "robust": r.get("robust"), "verdict": verdict(r) if g in src.index else "not measured"})
    table = pd.DataFrame(rows)
    table.to_csv(OUT / "antibiotics_vs_spaceflight.csv", index=False)

    # chart: one bar per antibiotic-gene pair that could be tested
    t = table[table.combined_z.notna()].copy()
    t["label"] = t.antibiotic + "  ·  " + t.gene + " (" + t.organ + ")"
    t = t.sort_values("combined_z")
    colours = np.where(t.robust.astype(bool), np.where(t.combined_z > 0, UP, DOWN), NS)
    fig, ax = plt.subplots(figsize=(8, max(3, 0.26 * len(t))))
    ax.barh(t.label, t.combined_z, color=colours)
    ax.axvline(0, color="#444", lw=0.8)
    ax.set_xlabel("Change in the clearance gene in space (pooled z; right = higher)")
    ax.set_title(f"Antibiotic clearance genes in spaceflight mice (liver: {n_liv} missions, kidney: {n_kid})\n"
                 f"coloured = FDR < {FDR} and robust to dropping any one mission", fontsize=10)
    ax.tick_params(axis="y", labelsize=7)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / "antibiotics_vs_spaceflight.png", dpi=160)
    pd.set_option("display.width", 220)
    print(table[["antibiotic", "gene", "organ", "studies", "studies_same_direction", "mean_log2fc", "fdr", "verdict"]].to_string())
