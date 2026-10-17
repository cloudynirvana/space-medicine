"""Offline tests. Every table here is hand-made in the format NASA uses,
to test the code only. None of it is real data."""
import numpy as np
import pandas as pd
import pytest

from common import de, osdr, study_scan
from p1_iss_resistance_genes import amr_classes, analyse
from p2_mars_radiation import donki, mission

C = "(Space Flight & On Earth)v(Ground Control & On Earth)"
C2 = "(Space Flight & On Earth)v(Basal Control & On Earth)"


def fake_de():
    return pd.DataFrame({
        "ENSEMBL": ["ENSMUSG01", "ENSMUSG02", "ENSMUSG03", "ENSMUSG04"],
        "SYMBOL": ["Cyp3a11", "Cyp2e1", "Actb", None],
        f"Log2fc_{C}": [2.0, -1.5, 0.1, 3.0],
        f"P.value_{C}": [1e-6, 1e-4, 0.8, 1e-3],
        f"Adj.p.value_{C}": [1e-4, 0.01, 0.9, 0.04],
        f"Log2fc_{C2}": [1.0, -1.0, 0.0, 0.0],
        f"Adj.p.value_{C2}": [0.5, 0.5, 0.5, 0.5],
    })


def test_finds_flight_vs_ground_contrast():
    a, b = de.flight_vs_ground(fake_de())
    assert a.startswith("Space Flight") and b.startswith("Ground Control")


def test_tidy_and_calls():
    t = de.label_hits(de.tidy(fake_de(), *de.flight_vs_ground(fake_de())))
    calls = dict(zip(t.symbol, t.call))
    assert calls == {"Cyp3a11": "up", "Cyp2e1": "down", "Actb": "ns", "ENSMUSG04": "up"}


def test_no_ground_contrast_raises():
    df = fake_de().drop(columns=[c for c in fake_de().columns if "Ground" in c])
    with pytest.raises(ValueError):
        de.flight_vs_ground(df)


def test_scan_across_studies(monkeypatch, tmp_path):
    monkeypatch.setattr(osdr, "differential_expression", lambda acc, refresh=False: fake_de())
    s = study_scan.run("Mus musculus", "liver", {"P450": ["Cyp3a11", "Cyp2e1"]}, tmp_path, "t",
                       accessions=["OSD-1", "OSD-2"])
    assert s.loc["Cyp3a11", "studies_up"] == 2 and s.loc["Cyp2e1", "studies_down"] == 2
    assert s.loc["Cyp3a11", "group"] == "P450"
    assert (tmp_path / "per_study" / "OSD-1_volcano.png").exists()


def test_query_string_keeps_bare_keys():
    q = osdr._query_string({"id.accession": "OSD-48", "study.factor value.spaceflight": None})
    assert q == "id.accession=OSD-48&study.factor%20value.spaceflight"


@pytest.mark.parametrize("gene,cls", [
    ("blaTEM-1", "beta-lactams (penicillins, cephalosporins)"), ("mecA", "beta-lactams (methicillin: MRSA)"),
    ("ermC", "macrolides / lincosamides"), ("tet(M)", "tetracyclines"), ("vanA", "glycopeptides (vancomycin)"),
    ("aac(6')-Ie", "aminoglycosides"), ("qnrS", "fluoroquinolones"), ("Actb", "other / unknown"),
])
def test_amr_classes(gene, cls):
    assert amr_classes.classify(gene) == cls


def test_amr_table_either_orientation():
    rows = pd.DataFrame({"gene": ["mecA", "ermC", "tetM", "16S"], "S1": [5, 0, 2, 9], "S2": [0, 1, 0, 9]})
    m1 = analyse.to_gene_by_sample(rows)
    m2 = analyse.to_gene_by_sample(rows.set_index("gene").T.reset_index())
    assert list(m1.index) == ["mecA", "ermC", "tetM"]
    assert sorted(m2.index) == sorted(m1.index)
    info = pd.DataFrame({"sample": ["S1", "S2"], "session": [1, 2], "location": ["galley", "toilet"]})
    res = analyse.summarise(analyse.detected(m1), info)
    assert res["per_sample"].loc["S1", "genes_detected"] == 2
    assert set(res["persistence"].query("persistent").gene) == set()
    assert res["per_location"].loc["galley", "genes_detected"] == 2


def test_donki_parsing():
    seps = donki.sep_table([{"sepID": "2024-05-11T02:15:00-SEP-001", "eventTime": "2024-05-11T02:15Z",
                             "instruments": [{"displayName": "GOES-P: EPEAD 100 MeV"}],
                             "linkedEvents": [{"activityID": "X"}]}])
    assert seps.time.dt.year.iloc[0] == 2024
    fl = donki.flare_table([{"flrID": "f", "peakTime": "2024-05-14T16:51Z", "classType": "X8.7"}])
    assert fl.letter.iloc[0] == "X"


def test_mission_dose():
    m = mission.Mission()
    assert mission.gcr_dose(m) == pytest.approx(360 * 1.84 + 500 * 0.64)
    quiet = mission.simulate(m, np.array([0.0]), 10)
    assert np.allclose(quiet, mission.gcr_dose(m))
    busy = mission.simulate(m, np.array([20.0]), 10)
    assert busy.mean() > quiet.mean()
    t = mission.risk_table(m, np.array([0, 5, 10]), doses=(1, 50), n=2000)
    assert t.median_mission_dose_msv.is_monotonic_increasing


def test_meta_analysis_pools_weak_consistent_signal():
    import numpy as np
    from common import meta
    assert np.allclose(meta.bh(np.array([0.01, 0.04, 0.03])), [0.03, 0.04, 0.04])
    # a gene that rises a little in each of 4 studies (p=0.1 each) is not significant
    # in any one of them, but is once pooled; a gene that flips direction is not
    t = {f"S{i}": pd.DataFrame({"symbol": ["A", "B"], "log2fc": [0.3, 0.3 if i % 2 else -0.3], "p": [0.1, 0.1]})
         for i in range(4)}
    m = meta.stouffer(t)
    assert m.loc["A", "combined_p"] < 0.01 and m.loc["A", "studies_same_direction"] == 4
    assert m.loc["B", "combined_p"] > 0.5
