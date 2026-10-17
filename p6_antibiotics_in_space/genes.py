"""Mouse genes that decide how the kidney and gut handle antibiotics."""
KIDNEY_GENES = {
    # pumps that pull drugs from blood into the tubule cell, then push them into urine
    "Uptake from blood": ["Slc22a6", "Slc22a8", "Slc22a2"],   # OAT1, OAT3, OCT2
    "Push into urine": ["Slc47a1", "Abcb1a", "Abcb1b", "Abcg2", "Abcc2", "Abcc4"],  # MATE1, P-gp, BCRP, MRP2/4
    "Reabsorb from urine": ["Slc15a2", "Lrp2"],  # PEPT2 (beta-lactams), megalin (aminoglycosides)
    "Kidney injury markers": ["Havcr1", "Lcn2"],  # KIM-1, NGAL
}
GUT_GENES = {
    "Absorption and efflux": ["Slc15a1", "Abcb1a", "Abcb1b", "Abcg2", "Cyp3a11"],  # PEPT1, P-gp, BCRP, CYP3A
}
