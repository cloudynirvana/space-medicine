"""Simulate the radiation dose of a crewed Mars mission.

Two sources of radiation:
  1. Galactic cosmic rays (GCR): a steady drizzle of very fast particles
     from outside the solar system. Uses dose rates MEASURED by the RAD
     instrument on NASA's Curiosity rover (values and sources below).
  2. Solar particle events (SEP): sudden storms. How OFTEN they happen
     comes from NASA's DONKI records. How much dose ONE storm gives the
     crew depends heavily on the storm and the shielding, so it is an
     input you choose, and the results show how the answer changes with it.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

# --- measured values (cite these in the README) -------------------------
GCR_CRUISE_MSV_PER_DAY = 1.84   # Zeitlin et al. 2013, Science 340:1080 (MSL cruise, inside spacecraft)
GCR_SURFACE_MSV_PER_DAY = 0.64  # Hassler et al. 2014, Science 343:1244797 (Gale Crater surface)
CAREER_LIMIT_MSV = 600          # NASA-STD-3001 Vol. 1 Rev B (2022): 600 mSv effective dose, all ages/sexes


@dataclass
class Mission:
    """A long-stay ('conjunction class') Mars mission, durations in days."""
    outbound: int = 180
    surface: int = 500
    inbound: int = 180

    @property
    def total(self) -> int:
        return self.outbound + self.surface + self.inbound


def gcr_dose(m: Mission) -> float:
    return (m.outbound + m.inbound) * GCR_CRUISE_MSV_PER_DAY + m.surface * GCR_SURFACE_MSV_PER_DAY


def simulate(m: Mission, sep_per_year: np.ndarray, dose_per_sep_msv: float,
             dose_spread: float = 1.0, surface_shield_factor: float = 0.5,
             n: int = 20_000, seed: int = 0) -> np.ndarray:
    """Total mission dose (mSv) for n simulated missions.

    sep_per_year: observed yearly SEP counts from DONKI; each simulated
      mission draws one year's rate at random, so busy and quiet parts of
      the solar cycle are both represented.
    dose_per_sep_msv: median dose to the crew from one SEP event (your choice).
    dose_spread: log-normal sigma; storms vary a lot in size.
    surface_shield_factor: fraction of SEP dose received on Mars, where the
      planet blocks half the sky and the thin atmosphere absorbs some more.
    """
    rng = np.random.default_rng(seed)
    rate = rng.choice(np.asarray(sep_per_year, float), size=n) / 365.25
    cruise_days = m.outbound + m.inbound
    n_cruise = rng.poisson(rate * cruise_days)
    n_surface = rng.poisson(rate * m.surface)
    total = np.full(n, gcr_dose(m))
    mu = np.log(dose_per_sep_msv)
    for counts, factor in ((n_cruise, 1.0), (n_surface, surface_shield_factor)):
        for k in range(counts.max(initial=0)):
            hit = counts > k
            total[hit] += factor * rng.lognormal(mu, dose_spread, hit.sum())
    return total


def risk_table(m: Mission, sep_per_year, doses=(1, 5, 20, 50, 100), **kw):
    import pandas as pd
    rows = []
    for d in doses:
        t = simulate(m, sep_per_year, d, **kw)
        rows.append({"median_dose_per_storm_msv": d,
                     "median_mission_dose_msv": float(np.median(t)),
                     "p95_mission_dose_msv": float(np.percentile(t, 95)),
                     "share_over_career_limit": float((t > CAREER_LIMIT_MSV).mean())})
    return pd.DataFrame(rows)
