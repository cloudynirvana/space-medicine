# Results on live NASA data

Run on 15 and 16 October 2026. To rebuild everything, run `./run_all.sh`.

| # | Project | Status | Data used |
|---|---|---|---|
| 1 | ISS resistance genes | Not run. OSD-66 is published only as raw reads, with no gene table. | none |
| 2 | Mars radiation | Ran | 494 solar particle storms and 3,394 flares, 2010 to 2026 |
| 3 | Muscle and bone | Ran, one study only | 1 of 9 mouse muscle studies (OSD-714) |
| 4 | Plants in orbit | Ran, then pooled | 10 of 33 Arabidopsis studies |
| 5 | Liver and medicines | Ran, then pooled | 7 of 12 mouse liver studies |
| 6 | Antibiotics in space | Ran, then pooled | 32 antibiotics; liver (7 missions), kidney (3 of 6), colon (1) |

Studies were dropped only when NASA had no processed table for them or no spaceflight vs ground
comparison. Each `results/run.log` lists every study and gives the reason for each one dropped.

## 1. The liver: the enzymes that clear common crew medicines shift in space
*Chart: `p5_liver_drug_genes/results/meta_analysis_panel.png`*

All 7 missions were pooled into one test per gene (Stouffer's method). The correction for testing
many genes covers all 23,394 genes, not just the 48 we picked. A gene counts only if it also stays
significant after dropping any one mission.

| Gene | Human counterpart | Typical drugs it clears | Spaceflight | Missions agreeing |
|---|---|---|---|---|
| Cyp1a2 | CYP1A2 | caffeine, melatonin | down about 30% | 6 of 7 |
| Cyp3a11 | CYP3A4 | zolpidem, modafinil, about half of all drugs | up about 30% | 6 of 7 |
| Cyp2b10 | CYP2B6 | bupropion, ketamine | up | 5 of 7 |
| Cyp4a10, Cyp4a14 | CYP4A | fatty acids, not drugs | up | 5 and 4 of 7 |
| Cyp3a16 | CYP3A | | down | 4 of 5 |

**Why it matters (a hypothesis to test, not a finding):** if people respond the same way,
caffeine and melatonin could last longer in space, and the sleep aid zolpidem and the alertness
drug modafinil could wear off sooner. This is mouse liver mRNA. It is not enzyme activity, and
it was not measured in people. Counting single missions alone (at least doubled or halved,
adjusted p < 0.05) missed Cyp3a11 entirely, because its change is steady but modest.

## 1b. Antibiotics: most are cleared normally; the CYP3A-cleared ones may not be
*Chart: `p6_antibiotics_in_space/results/antibiotics_vs_spaceflight.png`; full table: `antibiotics_vs_spaceflight.csv`*

For 32 common antibiotics, `p6_antibiotics_in_space/antibiotics.csv` records how each one works,
what it treats, how it leaves the body, and which human genes clear it, each matched to its mouse
counterpart. Each gene was then checked in the pooled NASA data: the liver (7 missions) for drugs
the liver clears, and the kidney (3 missions) for drugs that leave in urine.

- **Changed:** clarithromycin, erythromycin and clindamycin are cleared mainly by CYP3A4. Its
  mouse version, Cyp3a11, is about 30% higher in space (6 of 7 missions). These drugs might be
  cleared faster, which would mean lower levels in the blood.
- **No clear change:** the kidney pumps that push penicillins, cephalosporins, carbapenems and
  fluoroquinolones into urine (OAT1, OAT3, OCT2, MATE1, PEPT2), and the kidney-injury markers
  KIM-1 and NGAL. The liver genes for azithromycin, metronidazole, rifampicin, isoniazid and
  moxifloxacin also showed no clear change.
- **Weak signal:** megalin (Lrp2), which pulls gentamicin and amikacin into kidney cells and so
  causes their kidney damage, leans lower in space. It does not hold up when any one mission is
  dropped.
- **Interaction to flag (inferred, not measured):** ciprofloxacin blocks CYP1A2, and CYP1A2 is
  already lower in space. On the ISS, ciprofloxacin plus coffee could therefore raise caffeine
  levels more than it would on Earth.
- **11 of the 32 drugs can't be tested.** Some, like vancomycin and daptomycin, are simply
  filtered out by the kidney. Others, like doxycycline and linezolid, have no well-defined
  clearance gene. For these, kidney
  filtration rate matters more, and these datasets don't measure it.

Caveats: only 3 of the 6 kidney studies could be used (2 have no processed table, and 1 table is
1 GB). With 3 missions, "no clear change" is weak evidence of no change. The only colon study
used gene-modified (p21-null) mice. All of this is mouse mRNA, not drug levels in people.

## 2. Mars radiation: the limit is broken before any solar storm
*Charts: `p2_mars_radiation/results/storms_per_year.png`, `mission_dose_distribution.png`*

- Over an 860-day mission (180 days out, 500 days on Mars, 180 days back), cosmic rays alone
  give about **980 mSv**. NASA's career limit is 600 mSv. This uses dose rates measured by
  Curiosity (Zeitlin 2013, Hassler 2014).
- Solar storms come on top of that. Across 20,000 simulated missions, the median total is
  about 1,040 mSv if a typical storm adds 1 mSv, and 2,180 mSv if it adds 20 mSv. Every
  simulated mission goes over the limit.
- Storm counts follow the 11-year solar cycle and peaked in 2024, with 119 storms. The dose a
  single storm gives depends on shielding, so it is a chosen input, not data.

## 3. Muscle: a nerve-loss signature in mice flown on the ISS (one study)
*Chart: `p3_muscle_bone/results/soleus/per_study/OSD-714_gene_panel.png`*

In the soleus muscle of mice from the JAXA MHU-1 mission, several genes that switch on when a
muscle loses its nerve went up: Scn5a (32 times higher), Runx1, Musk and Myog. Trim63, a
muscle-breakdown gene, also went up. The other main breakdown gene, Fbxo32, went down. This
fits the idea that part of muscle loss in space is a nerve-signalling problem. It is one study
with a small group, so it is a lead, not a result. The bone genes here were measured in muscle
tissue, so they say little about bone itself.

## 4. Plants: touch and heat-shock genes respond in orbit
*Chart: `p4_plants_in_orbit/results/meta_analysis_panel.png`*

Pooled across 10 studies, the touch-response gene TCH3 is the strongest signal (higher in 7 of
10). The heat-shock genes HSP101, HSP90.1 and HSFA2 and the stress-signalling gene RBOHD also
rise. The antioxidant CSD1 falls. One caution: the plant studies differ a lot from each other,
and 40% of all plant genes pass the pooled test, so read the plant results by direction and
rank, not by p-value.

## Method notes
- Single-study call: the gene at least doubles or halves, with adjusted p < 0.05, spaceflight
  vs ground control. NASA GeneLab's own processed tables are used.
- Pooled call: Stouffer z across studies, Benjamini-Hochberg correction genome-wide (FDR < 0.05),
  plus a leave-one-out check (p < 0.05 with any one study dropped). See `common/meta.py`.
- Mouse and plant results do not transfer directly to people, and the groups are small.

## Code fixes made while running on live data
- `common/osdr.py`: NASA now puts "study/assay/" in front of every table column, so the code
  strips it to find the comparisons.
- `p2_mars_radiation/donki.py`: moved to DONKI's new address (NASA moved it on 30 Sep 2026),
  which serves 60 days per call and needs no key.
- `asteroid-tracker/neows.py`: names like "144900 (2004 VG64)" were losing their closing bracket.
