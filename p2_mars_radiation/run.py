"""Project 2: how much radiation would a Mars crew absorb, and how often would storms push them over the limit?

Usage:  python -m p2_mars_radiation.run          (no key needed)
"""
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from p2_mars_radiation import donki, mission

OUT = Path(__file__).parent / "results"
FIRST_YEAR = 2010  # DONKI coverage is fuller from about here on

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    last = date.today().year
    seps = donki.sep_table(donki.fetch_range("SEP", FIRST_YEAR, last))
    flares = donki.flare_table(donki.fetch_range("FLR", FIRST_YEAR, last))
    seps.to_csv(OUT / "sep_events.csv", index=False)
    flares.to_csv(OUT / "flares.csv", index=False)

    per_year = seps.groupby(seps.time.dt.year).size().reindex(range(FIRST_YEAR, last + 1), fill_value=0)
    # the current year is incomplete: scale it up to a full-year rate
    frac = (date.today() - date(last, 1, 1)).days / 365.25
    rates = per_year.astype(float)
    rates.loc[last] = per_year.loc[last] / max(frac, 0.05)
    big_flares = flares[flares.letter == "X"].groupby(flares.time.dt.year).size().reindex(per_year.index, fill_value=0)

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(per_year.index, per_year.values, color="#d1495b", label="Solar particle storms (SEP)")
    ax.plot(big_flares.index, big_flares.values, "k.-", label="X-class flares")
    ax.set_xlabel(f"Year ({last} counts only up to {date.today():%d %b})"); ax.set_ylabel("Events per year")
    ax.set_xticks(per_year.index[::2])
    ax.set_title("Solar storms rise and fall with the 11-year solar cycle (NASA DONKI)")
    ax.legend(frameon=False); ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(OUT / "storms_per_year.png", dpi=160)

    m = mission.Mission()
    print(f"Cosmic-ray dose alone for a {m.total}-day mission: {mission.gcr_dose(m):.0f} mSv "
          f"(NASA career limit {mission.CAREER_LIMIT_MSV} mSv)")
    table = mission.risk_table(m, rates.values)
    table.to_csv(OUT / "mission_risk.csv", index=False)
    print(table.to_string(index=False))

    fig, ax = plt.subplots(figsize=(7, 4))
    for d in (5, 20, 50):
        t = mission.simulate(m, rates.values, d)
        ax.hist(t, bins=80, histtype="step", lw=1.5, label=f"{d} mSv per storm")
    ax.axvline(mission.CAREER_LIMIT_MSV, color="k", ls="--", lw=1)
    ax.text(mission.CAREER_LIMIT_MSV, ax.get_ylim()[1] * 0.9, " NASA career limit", fontsize=9)
    ax.set_xlabel("Total mission dose (mSv)"); ax.set_ylabel("Simulated missions")
    ax.set_title("Total radiation dose across 20,000 simulated Mars missions")
    ax.legend(frameon=False, title="Typical storm dose"); ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(OUT / "mission_dose_distribution.png", dpi=160)
