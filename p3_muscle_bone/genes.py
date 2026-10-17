"""Mouse genes behind muscle and bone loss, plus nerve-muscle contact genes.

The 'Nerve-muscle junction' group is the neurotech angle: when a muscle
loses contact with its nerve, these genes switch on. If they rise in
spaceflight, part of the muscle loss is a nerve-signalling problem.
"""
GENES = {
    "Muscle breakdown": ["Fbxo32", "Trim63", "Foxo1", "Foxo3", "Mstn", "Cdkn1a", "Gadd45a", "Klf15", "Ddit4"],
    "Muscle building": ["Igf1", "Myod1", "Myog", "Ppargc1a", "Mtor"],
    "Muscle fibre type": ["Myh7", "Myh2", "Myh1", "Myh4", "Tnni1", "Tnni2"],
    "Nerve-muscle junction": ["Chrna1", "Chrng", "Chrnd", "Musk", "Ncam1", "Runx1", "Scn5a", "Gdf15"],
    "Bone breakdown": ["Tnfsf11", "Ctsk", "Acp5", "Mmp9", "Nfatc1"],
    "Bone building": ["Runx2", "Sp7", "Col1a1", "Bglap", "Alpl", "Spp1", "Tnfrsf11b", "Sost", "Dkk1"],
}
# Human versions of the genes, for the drug lookup
HUMAN = {
    "Fbxo32": "FBXO32", "Trim63": "TRIM63", "Mstn": "MSTN", "Foxo1": "FOXO1", "Foxo3": "FOXO3",
    "Gdf15": "GDF15", "Tnfsf11": "TNFSF11", "Ctsk": "CTSK", "Sost": "SOST", "Dkk1": "DKK1",
    "Mmp9": "MMP9", "Igf1": "IGF1", "Mtor": "MTOR", "Cdkn1a": "CDKN1A", "Acp5": "ACP5",
}
