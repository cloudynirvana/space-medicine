"""Run the same spaceflight-vs-ground gene analysis across every matching study.

A finding that shows up in one mission might be a fluke of that mission.
A finding that shows up in several missions is much more believable, so
each gene project scans all studies of one tissue and counts agreement.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from common import de, osdr, plots

RNASEQ = "RNA Sequencing (RNA-Seq)"


def find_studies(organism: str, material: str | None, technology: str = RNASEQ) -> list[str]:
    """Accessions of OSDR studies with spaceflight samples of one tissue (None = any tissue)."""
    q = {"study.characteristics.organism": organism}
    if material:
        q["study.characteristics.material type"] = material
    q["study.factor value.spaceflight"] = None
    q["investigation.study assays.study assay technology type"] = technology
    md = osdr.metadata(q)
    col = next((c for c in md.columns if c in ("accession", "id.accession")), None)
    if col is None or md.empty:
        return []
    return sorted(md[col].dropna().unique(), key=lambda s: int("".join(ch for ch in s if ch.isdigit()) or 0))


def analyse_study(acc: str, genes: list[str], outdir: Path, title: str) -> pd.DataFrame | None:
    """Fold changes for one study; writes a table and two charts."""
    try:
        raw = osdr.differential_expression(acc)
        a, b = de.flight_vs_ground(raw)
    except Exception as e:  # some studies have no processed table, or no ground group
        print(f"  {acc}: skipped ({e})")
        return None
    t = de.label_hits(de.tidy(raw, a, b))
    # plant tables are keyed by locus ID (AT1G01010); use the ID when it is on our list
    by_id = t.gene_id.astype(str).str.upper()
    wanted = {g.upper() for g in genes}
    t.loc[by_id.isin(wanted) & ~t.symbol.isin(genes), "symbol"] = by_id
    outdir.mkdir(parents=True, exist_ok=True)
    t.to_csv(outdir / f"{acc}_all_genes.csv", index=False)
    plots.volcano(t, genes, f"{acc}: {title}", outdir / f"{acc}_volcano.png")
    if t.symbol.isin(genes).any():
        plots.gene_bars(t, genes, f"{acc}: {title}", outdir / f"{acc}_gene_panel.png")
    t = t.assign(study=acc, contrast=f"{a} vs {b}")
    print(f"  {acc}: {len(t)} genes, {int((t.call != 'ns').sum())} changed; contrast '{a}' vs '{b}'")
    return t


def consistency(tables: list[pd.DataFrame], genes: list[str]) -> pd.DataFrame:
    """Per gene of interest: in how many studies is it significantly up or down?"""
    if not tables:
        return pd.DataFrame()
    allt = pd.concat(tables)
    sub = allt[allt.symbol.isin(genes)]
    g = sub.groupby("symbol")
    out = pd.DataFrame({
        "studies_measured": g.study.nunique(),
        "studies_up": g.apply(lambda x: (x.call == "up").sum(), include_groups=False),
        "studies_down": g.apply(lambda x: (x.call == "down").sum(), include_groups=False),
        "median_log2fc": g.log2fc.median(),
    })
    out["direction_agreement"] = (sub.assign(sign=sub.log2fc > 0).groupby("symbol").sign.mean()
                                  .map(lambda f: max(f, 1 - f)))
    return out.sort_values(["studies_up", "studies_down", "median_log2fc"], ascending=False)


def run(organism: str, material: str, genes: dict[str, list[str]], outdir: Path, title: str,
        accessions: list[str] | None = None) -> pd.DataFrame:
    """Whole pipeline for one tissue. `genes` maps a group name to gene symbols."""
    flat = sorted({g for gs in genes.values() for g in gs})
    accs = accessions or find_studies(organism, material)
    print(f"{len(accs)} {organism} {material or 'any-tissue'} studies: {', '.join(accs)}")
    if not accs:
        return pd.DataFrame()
    tables = [t for acc in accs if (t := analyse_study(acc, flat, outdir / "per_study", title)) is not None]
    summary = consistency(tables, flat)
    group_of = {g: grp for grp, gs in genes.items() for g in gs}
    summary.insert(0, "group", summary.index.map(group_of))
    outdir.mkdir(parents=True, exist_ok=True)
    summary.to_csv(outdir / "gene_consistency_across_studies.csv")
    (outdir / "run_info.json").write_text(json.dumps({
        "organism": organism, "material": material, "studies_found": accs,
        "studies_analysed": [t.study.iloc[0] for t in tables],
        "contrasts": {t.study.iloc[0]: t.contrast.iloc[0] for t in tables},
        "thresholds": {"adjusted_p": 0.05, "min_abs_log2fc": 1.0},
    }, indent=2))
    return summary
