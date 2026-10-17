#!/usr/bin/env bash
# Runs all five projects in order, then pools the missions. Needs internet
# access to NASA sites; no API key.
set -e
cd "$(dirname "$0")"
python -m p1_iss_resistance_genes.fetch
python -m p1_iss_resistance_genes.analyse
python -m p2_mars_radiation.run
python -m p3_muscle_bone.run
python -m p4_plants_in_orbit.run
python -m p5_liver_drug_genes.run
python meta_analysis.py
python -m p6_antibiotics_in_space.run
