"""Pool every mission's results into one answer per gene (projects 4 and 5).

Run after the gene projects:  python meta_analysis.py
Writes results/meta_analysis_*.csv and a chart into each project's folder.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import meta
from common.plots import UP, DOWN, NS
from p4_plants_in_orbit.genes import GENES as PLANT_GENES
from p5_liver_drug_genes.genes import GENES as LIVER_GENES

FDR = 0.05
PROJECTS = [
    ("p5_liver_drug_genes", LIVER_GENES, "Liver drug-processing genes"),
    ("p4_plants_in_orbit", PLANT_GENES, "Plant stress genes"),
]


def chart(panel: pd.DataFrame, n_studies: int, title: str, path: Path) -> None:
    p = panel.sort_values("combined_z")
    p.index = [f"{n} ({g})" if n else g for g, n in zip(p.index, p.name)]
    colours = np.where(p.robust, np.where(p.combined_z > 0, UP, DOWN), NS)
    fig, ax = plt.subplots(figsize=(7, max(3, 0.24 * len(p))))
    ax.barh(p.index, p.combined_z, color=colours)
    ax.axvline(0, color="#444", lw=0.8)
    ax.set_xlabel("Combined evidence across missions (z; right = higher in space)")
    ax.set_title(f"{title}: {n_studies} missions pooled\n"
                 f"coloured = genome-wide FDR < {FDR} and survives dropping any one mission", fontsize=10)
    ax.tick_params(axis="y", labelsize=7)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    pd.set_option("display.width", 200)
    for folder, genes, title in PROJECTS:
        out = Path(folder) / "results"
        tables = meta.load_per_study(out / "per_study")
        if len(tables) < 3:
            print(f"{folder}: only {len(tables)} studies, skipped")
            continue
        m = meta.stouffer(tables)
        m["robust"] = (m.fdr < FDR) & (m.leave_one_out_p < 0.05)
        m.to_csv(out / "meta_analysis_all_genes.csv")
        group_of = {g: grp for grp, gs in genes.items() for g in gs}
        panel = m[m.index.isin(group_of)].copy()
        names = {g: n for gs in genes.values() if isinstance(gs, dict) for g, n in gs.items()}
        panel.insert(0, "group", panel.index.map(group_of))
        panel.insert(1, "name", [names.get(g, "") for g in panel.index])
        panel.to_csv(out / "meta_analysis_panel.csv")
        chart(panel, len(tables), title, out / "meta_analysis_panel.png")
        print(f"\n{folder}: {len(tables)} studies, {len(m)} genes measured in 3+ of them, "
              f"{int((m.fdr < FDR).sum())} pass genome-wide FDR {FDR}, {int(m.robust.sum())} also robust")
        print(panel[panel.fdr < FDR].to_string())
