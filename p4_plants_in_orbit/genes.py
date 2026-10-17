"""Arabidopsis stress genes, by TAIR locus ID and common name.

GeneLab plant tables are keyed by TAIR IDs (AT1G01010 style); the symbol
column is not always filled, so matching uses both.
"""
GENES = {
    "Heat-shock / protein folding": {"AT5G12020": "HSP17.6II", "AT3G12580": "HSP70", "AT1G74310": "HSP101", "AT5G52640": "HSP90.1", "AT2G26150": "HSFA2"},
    "Oxidative stress": {"AT1G07890": "APX1", "AT1G20630": "CAT1", "AT1G08830": "CSD1", "AT2G28190": "CSD2", "AT5G47910": "RBOHD"},
    "Touch / gravity sensing": {"AT2G41100": "TCH3", "AT5G37770": "TCH2", "AT4G27280": "", "AT2G36400": ""},
    "Cell wall remodelling": {"AT4G30270": "XTH24", "AT5G57560": "TCH4", "AT4G25810": "XTH23"},
    "Light / photosynthesis": {"AT1G29920": "CAB2", "AT1G67090": "RBCS1A", "AT2G05070": "LHCB2.2"},
    "Pathogen defence": {"AT2G14610": "PR1", "AT3G57260": "PR2", "AT1G75040": "PR5"},
}
