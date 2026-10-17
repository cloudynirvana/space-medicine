"""Mouse genes that decide how the liver handles drugs and other foreign chemicals.

Neuro-relevant notes are drugs astronauts actually take: sleep aids,
alertness drugs and pain relief are among the most used medicines on the ISS.
"""
GENES = {
    # Phase I: oxidise the drug (CYP450 enzymes)
    "Phase I (CYP450)": [
        "Cyp1a2",   # human CYP1A2: caffeine, melatonin
        "Cyp2c29", "Cyp2c37", "Cyp2c38", "Cyp2c39", "Cyp2c40", "Cyp2c50", "Cyp2c54", "Cyp2c55",  # human CYP2C9/19 family
        "Cyp2d22",  # human CYP2D6: many antidepressants, codeine, opioids
        "Cyp2e1",   # paracetamol toxicity, alcohol
        "Cyp3a11", "Cyp3a13", "Cyp3a16", "Cyp3a25", "Cyp3a41a", "Cyp3a44",  # human CYP3A4: zolpidem, modafinil, ~half of drugs
        "Cyp2b10",  # human CYP2B6
        "Cyp4a10", "Cyp4a14",  # fatty-acid oxidation, PPARa targets
        "Cyp7a1",   # bile acid synthesis
        "Por",      # partner enzyme every CYP needs
    ],
    # Phase II: attach a tag so the drug can be flushed out
    "Phase II (conjugation)": [
        "Ugt1a1", "Ugt1a6a", "Ugt2b5", "Ugt2b36",
        "Sult1a1", "Sult2a1",
        "Gsta1", "Gsta2", "Gstm1", "Gstp1",
        "Nat2",
    ],
    # Phase III: pumps that move drugs in and out of liver cells
    "Transporters": ["Abcb1a", "Abcb1b", "Abcc2", "Abcc3", "Abcg2", "Slco1b2", "Slc22a1"],
    # Master switches that turn the above on
    "Regulators": ["Nr1i2", "Nr1i3", "Ahr", "Ppara", "Nr1h4", "Nfe2l2", "Hnf4a"],
}
