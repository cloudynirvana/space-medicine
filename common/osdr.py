"""Small client for NASA's Open Science Data Repository (OSDR / GeneLab).

Uses the Biological Data API documented at
https://osdr-tutorials.readthedocs.io/en/latest/pages/guides/biological_data_api.html
Everything downloaded is cached under data/ so each file is fetched once.
"""
from __future__ import annotations

import hashlib
import io
import re
from pathlib import Path
from urllib.parse import quote

import pandas as pd
import requests

API = "https://visualization.osdr.nasa.gov/biodata/api/v2"
OSDR_FILES = "https://osdr.nasa.gov/osdr/data/osd/files/{num}"
CACHE = Path(__file__).resolve().parent.parent / "data" / "osdr_cache"


def _query_string(params: dict[str, str | None]) -> str:
    # the API takes bare keys (no value) as "this field must exist"
    parts = []
    for k, v in params.items():
        k = quote(k, safe=".")
        parts.append(k if v is None else f"{k}={quote(str(v), safe='')}")
    return "&".join(parts)


def _get_csv(url: str, refresh: bool = False) -> pd.DataFrame:
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / (hashlib.sha1(url.encode()).hexdigest()[:16] + ".csv")
    if refresh or not path.exists():
        r = requests.get(url, timeout=300)
        r.raise_for_status()
        path.write_bytes(r.content)
        (path.with_suffix(".url")).write_text(url)
    text = path.read_text()
    # the API sends a two-row header (field group / field) on metadata queries
    return pd.read_csv(io.StringIO(text), header=[0, 1] if text.startswith("id,") or text.startswith('"id"') else 0, low_memory=False)


def metadata(params: dict[str, str | None], refresh: bool = False) -> pd.DataFrame:
    """Sample-level metadata rows matching the query, flattened column names."""
    df = _get_csv(f"{API}/query/metadata/?{_query_string(params)}", refresh)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [b if str(b).startswith(("accession", "sample name", "assay name")) or a == "id" else f"{a}.{b}"
                      for a, b in df.columns]
    return df


def data(params: dict[str, str | None], refresh: bool = False) -> pd.DataFrame:
    """One processed data table (e.g. differential expression) for one study."""
    return _get_csv(f"{API}/query/data/?{_query_string(params)}", refresh)


def differential_expression(accession: str, refresh: bool = False) -> pd.DataFrame:
    """GeneLab's processed differential-expression table for one study."""
    df = data({"id.accession": accession, "file.datatype": "differential expression"}, refresh)
    # columns arrive as "<accession>/<assay name>/<column>"; keep the first assay, drop the prefix
    pre = re.compile(r"^(OSD-\d+/[^/]+)/")
    first = next((m.group(1) for c in df.columns if (m := pre.match(str(c)))), None)
    if first:
        df = df[[c for c in df.columns if str(c).startswith(first + "/")]]
        df.columns = [str(c)[len(first) + 1:] for c in df.columns]
    return df


def study_files(accession: str) -> pd.DataFrame:
    """List of all files NASA publishes for one OSD study (name, size, URL)."""
    num = re.sub(r"\D", "", accession)
    r = requests.get(OSDR_FILES.format(num=num), timeout=60)
    r.raise_for_status()
    rows = []
    for study in r.json().get("studies", {}).values():
        for f in study.get("study_files", []):
            rows.append({
                "file_name": f.get("file_name"),
                "category": f.get("category"),
                "subcategory": f.get("subcategory"),
                "size_bytes": f.get("file_size"),
                "url": "https://osdr.nasa.gov" + f["remote_url"] if f.get("remote_url", "").startswith("/") else f.get("remote_url"),
            })
    return pd.DataFrame(rows)


def download(url: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        with requests.get(url, stream=True, timeout=300) as r:
            r.raise_for_status()
            with open(dest, "wb") as fh:
                for chunk in r.iter_content(1 << 20):
                    fh.write(chunk)
    return dest
