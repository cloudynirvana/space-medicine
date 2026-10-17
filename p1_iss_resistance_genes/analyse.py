"""Step 2: which resistance genes live on the ISS, where, and do they change?

Finds the table in data/OSD-66/ whose rows (or columns) are resistance
genes, reads which genes were detected in which sample, and reports:
  * how many genes were found per ISS location and per sampling session
  * which antibiotic classes those genes defeat
  * genes present in both sessions (persistent) vs one only

Usage:  python -m p1_iss_resistance_genes.analyse [path/to/table]
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from p1_iss_resistance_genes.amr_classes import CREW_KIT, classify, looks_like_amr_gene

HERE = Path(__file__).parent
DATA = HERE.parent / "data" / "OSD-66"
OUT = HERE / "results"


def read_any(path: Path) -> pd.DataFrame:
    if path.suffix in (".xlsx", ".xls"):
        return pd.read_excel(path)
    return pd.read_csv(path, sep=None, engine="python")


def to_gene_by_sample(df: pd.DataFrame) -> pd.DataFrame:
    """Return a table with genes as rows and samples as columns (numbers)."""
    first = df.columns[0]
    row_hits = df[first].astype(str).map(looks_like_amr_gene).mean()
    col_hits = pd.Series(df.columns.astype(str)).map(looks_like_amr_gene).mean()
    m = df.set_index(first) if row_hits >= col_hits else df.set_index(first).T
    m = m.apply(pd.to_numeric, errors="coerce")
    m = m.loc[m.index.astype(str).map(looks_like_amr_gene)]
    return m.dropna(axis=1, how="all")


def find_table() -> Path:
    """Pick the downloaded file with the most resistance-gene names in it."""
    best, score = None, 0
    for p in DATA.glob("*"):
        if p.suffix.lower() not in (".csv", ".tsv", ".txt", ".xlsx", ".xls"):
            continue
        try:
            n = len(to_gene_by_sample(read_any(p)))
        except Exception:
            continue
        if n > score:
            best, score = p, n
    if best is None:
        raise SystemExit(f"No resistance-gene table found in {DATA}. Run fetch.py first, "
                         "then pass the right file as an argument.")
    return best


def detected(m: pd.DataFrame, threshold: float = 0.0) -> pd.DataFrame:
    """True where a gene was detected in a sample (value above threshold).

    For qPCR Ct-value tables, lower means more, and 'not detected' is often
    40 or blank; pass the table through `ct_to_detected` instead.
    """
    return m.fillna(0) > threshold


def ct_to_detected(m: pd.DataFrame, max_ct: float = 35.0) -> pd.DataFrame:
    return m.notna() & (m < max_ct)


def summarise(det: pd.DataFrame, sample_info: pd.DataFrame | None = None) -> dict[str, pd.DataFrame]:
    genes = pd.DataFrame({"gene": det.index, "antibiotic_class": det.index.map(classify),
                          "samples_detected": det.sum(axis=1).values})
    genes["in_crew_kit_class"] = genes.antibiotic_class.isin(CREW_KIT)
    by_class = (genes[genes.samples_detected > 0].groupby("antibiotic_class")
                .agg(genes=("gene", "count"), detections=("samples_detected", "sum"))
                .sort_values("genes", ascending=False))
    per_sample = det.sum().rename("genes_detected").to_frame()
    out = {"genes": genes.sort_values("samples_detected", ascending=False),
           "by_class": by_class, "per_sample": per_sample}
    if sample_info is not None and {"sample", "session"} <= set(sample_info.columns):
        sess = sample_info.set_index("sample").session.reindex(det.columns)
        per_session = det.T.groupby(sess.values).any().T
        out["persistence"] = pd.DataFrame({
            "gene": per_session.index,
            "sessions_detected": per_session.sum(axis=1).values,
        }).assign(persistent=lambda d: d.sessions_detected == per_session.shape[1])
        if "location" in sample_info.columns:
            loc = sample_info.set_index("sample").location.reindex(det.columns)
            out["per_location"] = det.T.groupby(loc.values).any().sum(axis=1).rename("genes_detected").to_frame()
    return out


def plot_classes(by_class: pd.DataFrame, path: Path):
    fig, ax = plt.subplots(figsize=(7, 0.4 * len(by_class) + 1.2))
    colours = ["#d1495b" if c in CREW_KIT else "#8d99ae" for c in by_class.index]
    ax.barh(by_class.index[::-1], by_class.genes[::-1], color=colours[::-1])
    ax.set_xlabel("Number of different resistance genes found on the ISS")
    ax.set_title("Which antibiotics ISS microbes could resist\n(red = drug classes a crew medical kit relies on)")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else find_table()
    print("using", path)
    m = to_gene_by_sample(read_any(path))
    info_path = HERE / "sample_info.csv"
    info = pd.read_csv(info_path) if info_path.exists() else None
    res = summarise(detected(m), info)
    OUT.mkdir(exist_ok=True)
    for k, v in res.items():
        v.to_csv(OUT / f"{k}.csv")
    plot_classes(res["by_class"], OUT / "antibiotic_classes.png")
    print(res["by_class"].to_string())
