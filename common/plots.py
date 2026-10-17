"""Shared chart helpers so every project's figures look the same."""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

UP, DOWN, NS, HIGHLIGHT = "#d1495b", "#2e86ab", "#c7c7c7", "#1b1b1b"


def volcano(t, highlight=(), title="", path=None, label_top=12):
    """Fold change against significance; genes in `highlight` are named."""
    fig, ax = plt.subplots(figsize=(7, 5.5))
    y = -np.log10(t.padj.clip(lower=1e-300))
    colours = t.call.map({"up": UP, "down": DOWN}).fillna(NS)
    ax.scatter(t.log2fc, y, s=5, c=colours, alpha=0.6, linewidths=0)
    hl = t[t.symbol.isin(set(highlight))]
    ax.scatter(hl.log2fc, -np.log10(hl.padj.clip(lower=1e-300)), s=22, facecolors="none", edgecolors=HIGHLIGHT)
    for _, r in hl.assign(y=-np.log10(hl.padj.clip(lower=1e-300))).nlargest(label_top, "y").iterrows():
        ax.annotate(r.symbol, (r.log2fc, r.y), fontsize=8, xytext=(3, 3), textcoords="offset points")
    ax.axhline(-np.log10(0.05), color="#888", lw=0.8, ls="--")
    ax.set_xlabel("log2 fold change, spaceflight vs ground (1 = doubled)")
    ax.set_ylabel("-log10 adjusted p-value (higher = more certain)")
    ax.set_title(title)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    if path:
        fig.savefig(path, dpi=160)
    plt.close(fig)
    return fig


def gene_bars(t, genes, title="", path=None):
    """Horizontal bars of fold change for a chosen gene list, stars for FDR < 0.05."""
    sub = t[t.symbol.isin(genes)].sort_values("log2fc")
    fig, ax = plt.subplots(figsize=(6.5, max(2.5, 0.28 * len(sub) + 1)))
    colours = np.where(sub.log2fc > 0, UP, DOWN)
    ax.barh(sub.symbol, sub.log2fc, color=colours)
    for i, (_, r) in enumerate(sub.iterrows()):
        if r.padj < 0.05:
            ax.text(r.log2fc, i, " *" if r.log2fc >= 0 else "* ", va="center",
                    ha="left" if r.log2fc >= 0 else "right", fontsize=10)
    ax.axvline(0, color="#444", lw=0.8)
    ax.set_xlabel("log2 fold change, spaceflight vs ground  (* = adjusted p < 0.05)")
    ax.set_title(title)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    if path:
        fig.savefig(path, dpi=160)
    plt.close(fig)
    return fig
