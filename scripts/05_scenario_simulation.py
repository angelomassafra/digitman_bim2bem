# ---
# jupyter:
#   jupytext:
#     formats: notebooks//ipynb,scripts//py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 05 · Scenario simulations
#
# Runs the annual EnergyPlus 24.2 simulations of the twelve scenarios of both buildings
# (**Section 3.3.3**). Each run writes its outputs next to the scenario model
# (`results/scenarios/scenario<N>/<building>.csv`, `.eio`, `.err`, ...).
#
# The hourly CSV files (~170 MB each for Building 09) are not versioned: they are produced by
# this script and read by `06_scenario_kpis`.

# %%
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent if '__file__' in globals() else Path.cwd()
ROOT = next(p for p in (HERE, *HERE.parents) if (p / 'config.py').exists())
sys.path.insert(0, str(ROOT))
import config

from digitmanpy.Operation import Eppy

# %%
# Number of parallel EnergyPlus runs
WORKERS = int(config.cli_option('workers', 4))

runs = sorted(config.SCENARIO_RESULTS_DIR.glob('scenario*/building*.idf'))
print(f'{len(runs)} scenario models to simulate with {WORKERS} parallel runs')


def simulate(idf_path):
    ok = Eppy.EnergyPlus_RunSimulation(idfFilePath=str(idf_path), epwFilePath=str(config.EPW_PATH),
                                       energyPlusExePath=str(config.ENERGYPLUS_EXE))
    return idf_path, ok


with ThreadPoolExecutor(max_workers=WORKERS) as pool:
    for idf_path, ok in pool.map(simulate, runs):
        print(f'{idf_path.parent.name} {idf_path.stem}: {"OK" if ok else "FAILED (see the .err file)"}', flush=True)
