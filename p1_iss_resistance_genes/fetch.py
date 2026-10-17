"""Step 1: list and download NASA's files for the ISS resistance-gene study.

OSD-66: 'Microbial Observatory (ISS-MO): Antimicrobial resistance genes'.
Wipes from 8 surfaces on the ISS, two sessions three months apart; a
panel of 500 resistance genes was measured, plus 16S and metagenomes.

Usage:  python -m p1_iss_resistance_genes.fetch
Writes data/OSD-66/manifest.csv and downloads every table under 200 MB.
"""
from pathlib import Path

from common import osdr

STUDIES = ["OSD-66"]
TABLE_EXT = (".csv", ".tsv", ".txt", ".xlsx", ".xls", ".zip")
MAX_BYTES = 200 * 1024 ** 2
DATA = Path(__file__).resolve().parent.parent / "data"

if __name__ == "__main__":
    for acc in STUDIES:
        files = osdr.study_files(acc)
        out = DATA / acc
        out.mkdir(parents=True, exist_ok=True)
        files.to_csv(out / "manifest.csv", index=False)
        print(f"{acc}: {len(files)} files")
        print(files[["file_name", "category", "size_bytes"]].to_string(index=False))
        for _, f in files.iterrows():
            if str(f.file_name).lower().endswith(TABLE_EXT) and (f.size_bytes or 0) < MAX_BYTES:
                osdr.download(f.url, out / f.file_name)
                print("  downloaded", f.file_name)
