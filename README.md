# Space medicine with NASA data

Six small research projects on how spaceflight affects the body, the
medicines astronauts rely on, and the life around them. Each one uses
free, real NASA data and asks one question a crew doctor would care about.

> **Status:** run on live NASA data on 15 and 16 October 2026. Four of the five projects
> have results; see **[RESULTS.md](RESULTS.md)** for findings, charts and caveats. Project 1
> could not run, because NASA publishes only raw reads for that study. 17 offline tests pass.

## The six projects

| # | Question | Angle | NASA data |
|---|---|---|---|
| 1 | Which antibiotics could microbes on the space station resist? | Space medicine | OSDR study OSD-66 (ISS Microbial Observatory) |
| 2 | How much radiation would a Mars crew absorb? | Space medicine, brain risk | NASA DONKI space-weather API |
| 3 | Which genes drive muscle and bone loss in space, and are there drugs for them? | Biotech, neuromuscular | OSDR mouse muscle studies (e.g. GLDS-104) + ChEMBL |
| 4 | Which stress genes do plants switch on in orbit? | Biotech, life support | OSDR Arabidopsis spaceflight studies |
| 5 | Does spaceflight change how the liver handles medicines? | Pharmacology, neuro drugs | OSDR mouse liver studies (e.g. GLDS-48, GLDS-168) |
| 6 | Would common antibiotics be cleared differently in space? | Pharmacology, infection | OSDR mouse liver and kidney studies |

### 1. Antibiotic-resistance genes on the ISS
A crew member who falls ill on the way to Mars can't be sent home, and the
ship's pharmacy is small. If microbes on board carry genes that defeat the
antibiotics in that pharmacy, an ordinary infection becomes dangerous.
NASA swabbed 8 surfaces on the ISS, twice, three months apart, and tested
for 500 resistance genes. This project sorts the genes found by the drug
class they defeat. It flags the classes a crew medical kit depends on, and
checks which genes were still there at the second sampling.

### 2. Radiation dose on a trip to Mars
Curiosity measured radiation inside its spacecraft on the way to Mars
(1.84 mSv per day; Zeitlin et al., *Science* 2013) and on the surface
(0.64 mSv per day; Hassler et al., *Science* 2014). For a typical
860-day mission (180 days out, 500 on Mars, 180 back) that adds up to
about 980 mSv from cosmic rays alone. NASA's career limit is 600 mSv
(NASA-STD-3001, 2022). This project adds solar storms on top. It uses
NASA's real storm records to see how often they happen, then simulates
20,000 missions to show how far over the limit a crew could go.
**Brain angle:** the heavy particles in cosmic rays are a main worry for
the nervous system on long missions, not only cancer.

### 3. Muscle and bone loss
Astronauts lose muscle and bone in weightlessness. This project reads
NASA's gene-activity data from mice flown on the ISS and checks groups of
genes for muscle breakdown, muscle building, fibre type, bone breakdown
and bone building. One more group, the **nerve-muscle junction** genes, is
the neurotech angle. These genes switch on when a muscle loses contact
with its nerve. If they rise in space, part of the loss is a
nerve-signalling problem, not just lack of use.
Changed genes are matched to existing drugs from the ChEMBL database
(`p3_muscle_bone/drug_targets.csv`, looked up 15 Oct 2026). For example,
two approved bone drugs, denosumab and romosozumab, target genes on the list.

### 4. Plants in orbit
Any long mission will need to grow food. This project checks which stress
genes switch on in plants grown on the ISS: heat-shock, oxidative stress,
touch and gravity sensing, cell walls, light and defence. It is the least
medical of the five; its value is the link to life support.

### 5. The liver and medicines
Astronauts take sleep aids, alertness drugs and painkillers. Most are
broken down by liver enzymes such as CYP3A (zolpidem, modafinil), CYP2D
(many antidepressants, codeine) and CYP1A2 (caffeine, melatonin). If
spaceflight turns these enzymes up or down, the same dose could act
stronger or weaker in space. This project checks about 50
drug-processing genes in every NASA mouse liver study.

## How the gene projects work (3, 4 and 5)
1. Ask NASA's Open Science Data Repository for every study of that tissue
   with spaceflight samples.
2. Download NASA's own processed table of gene changes for each study.
3. Pick the "spaceflight vs ground control" comparison.
4. Call a gene changed if it at least doubles or halves, with an adjusted
   p-value under 0.05.
5. Count in how many separate missions each gene changed the same way. One
   mission can be a fluke. The same change in several missions is much
   more convincing.

## Run it
```bash
pip install -r requirements.txt
pytest                     # offline tests
./run_all.sh               # all five plus the cross-mission meta-analysis
```
Needs internet access to `osdr.nasa.gov`, `visualization.osdr.nasa.gov` and
`ccmc.gsfc.nasa.gov`. No API key is needed. The first full run downloads about 1.3 GB of
NASA tables into `data/`, and later runs reuse them.

## Known gaps before results can be trusted
- **Project 1:** NASA publishes OSD-66 only as raw sequencing reads (1.2 GB), with no table
  of resistance genes, so `analyse.py` finds nothing to count. Running it needs the reads to be
  processed first.
- **Project 2:** the dose from one solar storm depends on the storm and the
  shielding. It is a chosen input (1 to 100 mSv), not data, and the results
  show every value side by side. The Curiosity rates are dose equivalent;
  NASA's limit is effective dose, which is close but not identical.
- **Projects 3 to 5:** mouse results don't transfer directly to people,
  and mouse groups are small (often 3 to 6 animals).

## Data sources
- NASA Open Science Data Repository (OSDR/GeneLab): https://osdr.nasa.gov
- NASA DONKI space-weather database, https://ccmc.gsfc.nasa.gov/DONKI-API/ (moved there from api.nasa.gov on 30 Sep 2026)
- ChEMBL drug database (EMBL-EBI), for the project 3 drug matches
- Dose rates: Zeitlin et al. 2013, *Science* 340:1080; Hassler et al. 2014,
  *Science* 343:1244797. Limit: NASA-STD-3001 Vol. 1 Rev B (2022).

Developed with AI assistance.
