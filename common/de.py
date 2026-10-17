"""Read GeneLab differential-expression tables.

GeneLab names its columns like
    Log2fc_(Space Flight)v(Ground Control)
    P.value_(Space Flight)v(Ground Control)
    Adj.p.value_(Space Flight)v(Ground Control)
with one set per pair of groups. These helpers find the pairs and pull
out a tidy table for the one you want.
"""
from __future__ import annotations

import re

import pandas as pd

LFC = re.compile(r"^Log2fc_\((?P<a>.+)\)v\((?P<b>.+)\)$")
FLIGHT_WORDS = ("space flight", "spaceflight", "flight")
GROUND_WORDS = ("ground control", "ground", "vivarium", "basal")


def contrasts(df: pd.DataFrame) -> list[tuple[str, str]]:
    """All (group A, group B) pairs that have a fold-change column."""
    return [(m["a"], m["b"]) for c in df.columns if (m := LFC.match(str(c)))]


def _is(label: str, words) -> bool:
    low = label.lower()
    return any(w in low for w in words)


def flight_vs_ground(df: pd.DataFrame) -> tuple[str, str]:
    """Pick the contrast closest to 'spaceflight vs ground control'.

    GeneLab group labels often carry extra factors joined with '&'
    (e.g. 'Space Flight & On Earth & Carcass'). We prefer a pair where the
    two labels differ only in the flight/ground part.
    """
    cands = []
    for a, b in contrasts(df):
        if _is(a, FLIGHT_WORDS) and not _is(a, GROUND_WORDS) and _is(b, ("ground",)):
            rest_a = set(x.strip() for x in a.split("&")) - {x for x in a.split("&") if _is(x, FLIGHT_WORDS)}
            rest_b = set(x.strip() for x in b.split("&")) - {x for x in b.split("&") if _is(x, GROUND_WORDS)}
            cands.append((rest_a != rest_b, len(a) + len(b), a, b))
    if not cands:
        raise ValueError(f"No spaceflight vs ground contrast. Found: {contrasts(df)}")
    _, _, a, b = sorted(cands)[0]
    return a, b


def tidy(df: pd.DataFrame, a: str, b: str) -> pd.DataFrame:
    """One row per gene: symbol, log2 fold change, p, adjusted p for A vs B."""
    sym = next((c for c in ("SYMBOL", "Symbol", "symbol", "GENENAME") if c in df.columns), None)
    gid = next((c for c in ("ENSEMBL", "TAIR", "ENTREZID", "Unnamed: 0") if c in df.columns), df.columns[0])
    tag = f"_({a})v({b})"
    out = pd.DataFrame({
        "gene_id": df[gid],
        "symbol": df[sym] if sym else df[gid],
        "log2fc": pd.to_numeric(df["Log2fc" + tag], errors="coerce"),
        "p": pd.to_numeric(df.get("P.value" + tag), errors="coerce"),
        "padj": pd.to_numeric(df.get("Adj.p.value" + tag), errors="coerce"),
    })
    out["symbol"] = out["symbol"].fillna(out["gene_id"]).astype(str)
    return out.dropna(subset=["log2fc"])


def label_hits(t: pd.DataFrame, fdr: float = 0.05, min_lfc: float = 1.0) -> pd.DataFrame:
    """Add a 'call' column: up, down or ns (not significant)."""
    t = t.copy()
    sig = (t.padj < fdr) & (t.log2fc.abs() >= min_lfc)
    t["call"] = "ns"
    t.loc[sig & (t.log2fc > 0), "call"] = "up"
    t.loc[sig & (t.log2fc < 0), "call"] = "down"
    return t
