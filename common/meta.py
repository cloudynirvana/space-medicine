"""Combine one gene's results across several missions into a single answer.

Counting "significant in 3 of 7 missions" throws information away: a gene that
rises a little in every mission never passes the cut in any single one. A
meta-analysis pools the evidence instead.

Method (Stouffer, unweighted): each study's two-sided p-value and the sign of
its fold change become a z-score; the z-scores are summed and divided by
sqrt(number of studies). The combined p-values are then corrected for testing
every gene in the genome (Benjamini-Hochberg), not just the genes of interest,
so the threshold is as strict as in a single study.
"""
from __future__ import annotations

import math
from pathlib import Path
from statistics import NormalDist

import numpy as np
import pandas as pd

_N = NormalDist()
_inv = np.vectorize(lambda q: _N.inv_cdf(q), otypes=[float])
_two_sided = np.vectorize(lambda z: math.erfc(abs(z) / math.sqrt(2)), otypes=[float])  # exact in the far tail


def bh(p: np.ndarray) -> np.ndarray:
    """Benjamini-Hochberg adjusted p-values."""
    p = np.asarray(p, float)
    order = np.argsort(p)
    ranked = p[order] * len(p) / np.arange(1, len(p) + 1)
    adj = np.minimum.accumulate(ranked[::-1])[::-1].clip(max=1)
    out = np.empty_like(adj)
    out[order] = adj
    return out


def _leave_one_out(z: pd.Series) -> float:
    z = z.to_numpy()
    if len(z) < 2:
        return 0.0
    full = np.sign(z.sum()) or 1.0
    loo = (z.sum() - z) / np.sqrt(len(z) - 1)
    return float(full * max(0.0, (full * loo).min()))


def stouffer(tables: dict[str, pd.DataFrame], min_studies: int = 3) -> pd.DataFrame:
    """tables: study -> per-gene table with symbol, log2fc, p. One row per gene out."""
    long = pd.concat([t[["symbol", "log2fc", "p"]].assign(study=s) for s, t in tables.items()])
    long = long.dropna(subset=["log2fc", "p"])
    # one row per gene per study (a few symbols map to several IDs: keep the most certain)
    long = long.sort_values("p").drop_duplicates(["symbol", "study"])
    p = long.p.clip(1e-300, 1.0).to_numpy()
    long["z"] = -np.sign(long.log2fc.to_numpy()) * _inv(p / 2)  # p/2 avoids rounding 1 - tiny to 1
    g = long.groupby("symbol")
    out = pd.DataFrame({
        "studies": g.study.nunique(),
        "studies_same_direction": g.log2fc.apply(lambda x: max((x > 0).sum(), (x < 0).sum())),
        "mean_log2fc": g.log2fc.mean(),
        "combined_z": g.z.sum() / np.sqrt(g.z.size()),
        # robustness: the weakest combined z left after dropping any one study, in the
        # direction of the full result. Guards against one huge study carrying the answer.
        "leave_one_out_z": g.z.apply(_leave_one_out),
    })
    out = out[out.studies >= min_studies].copy()
    out["combined_p"] = _two_sided(out.combined_z.to_numpy()).clip(1e-300)
    out["leave_one_out_p"] = _two_sided(out.leave_one_out_z.to_numpy()).clip(1e-300)
    out["fdr"] = bh(out.combined_p.to_numpy())
    return out.sort_values("combined_p")


def load_per_study(folder: Path) -> dict[str, pd.DataFrame]:
    """The *_all_genes.csv tables the gene projects write, keyed by study."""
    return {f.name.split("_")[0]: pd.read_csv(f) for f in sorted(folder.glob("*_all_genes.csv"))}
