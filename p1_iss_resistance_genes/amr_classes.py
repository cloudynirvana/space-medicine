"""Map antimicrobial-resistance gene names to the antibiotic class they defeat.

Gene families follow the standard naming used by CARD and ResFinder.
`CREW_KIT` marks classes that matter most for treating a sick crew member
with a small pharmacy; it is a judgement call, documented in the README.
"""
import re

FAMILY_TO_CLASS = [
    (r"^(bla|amp[CHR]?|pbp|oxa|tem|shv|ctx|kpc|ndm|vim|imp)", "beta-lactams (penicillins, cephalosporins)"),
    (r"^mec", "beta-lactams (methicillin: MRSA)"),
    (r"^(erm|mef|msr|mph|ere|lnu|vga|vat)", "macrolides / lincosamides"),
    (r"^tet|^otr", "tetracyclines"),
    (r"^van", "glycopeptides (vancomycin)"),
    (r"^(aac|aad|aph|ant|str|rmt|arm|npm)", "aminoglycosides"),
    (r"^(sul|fol)", "sulfonamides"),
    (r"^dfr", "trimethoprim"),
    (r"^(qnr|gyr|par|qep|oqx)", "fluoroquinolones"),
    (r"^(cat|cml|flo|cfr)", "phenicols"),
    (r"^(mcr|arn|pmr)", "polymyxins (colistin)"),
    (r"^fos", "fosfomycin"),
    (r"^(mup|ile)", "mupirocin"),
    (r"^(acr|mex|ade|mdt|emr|nor|qac|sme|mep|tolc)", "multidrug efflux pumps"),
]
CREW_KIT = {
    "beta-lactams (penicillins, cephalosporins)", "beta-lactams (methicillin: MRSA)",
    "macrolides / lincosamides", "tetracyclines", "fluoroquinolones", "sulfonamides", "trimethoprim",
}


def classify(gene: str) -> str:
    g = re.sub(r"[^a-z0-9]", "", str(gene).lower())
    for pat, cls in FAMILY_TO_CLASS:
        if re.match(pat, g):
            return cls
    return "other / unknown"


def looks_like_amr_gene(name: str) -> bool:
    return classify(name) != "other / unknown"
