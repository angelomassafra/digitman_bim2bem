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
# # 07 · Sensitivity of the KPIs to the scenario assumptions
#
# One-at-a-time sensitivity of the Scenario 0 KPIs (energy need, cost, CO₂ emissions) to the
# assumptions of the scenario matrix (Figure 10):
#
# | Assumption | Low / high value | Runs |
# |---|---|---|
# | Occupancy level | 25% / 100% of the booked hours | S8 / S5 |
# | Equipment density of the classrooms | 2.7 / 8.1 W/m² | new runs |
# | Outdoor air per floor area of the classrooms | −20% / +20% | new runs |
# | Ventilation control | CAV-person (S1), VAV-person (S2) | categorical switch |
# | Space use | closed offices (S9) | categorical switch |
#
# **Inputs**: Scenario 0 model and KPIs (`results/scenarios/`).
#
# **Outputs** (`results/sensitivity/`): variant models and results, `sensitivity_kpis.csv`,
# `sensitivity_tornado_values.csv` (plotted by `scripts/figures/fig_sensitivity_tornado.py`).

# %%
import copy
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent if '__file__' in globals() else Path.cwd()
ROOT = next(p for p in (HERE, *HERE.parents) if (p / 'config.py').exists())
sys.path.insert(0, str(ROOT))
import config

import pandas as pd
from eppy.modeleditor import IDF

from digitmanpy.Operation import Eppy, KPI, Scenario

# %%
# Run the EnergyPlus simulations of the variants (otherwise the results of a previous run are read)
RUN_SIMULATIONS = config.cli_option('simulate', 'yes') == 'yes'
WORKERS = int(config.cli_option('workers', 4))

NOMINAL_EQUIPMENT_DENSITY = 5.4  # W/m², classrooms in Scenario 0
VARIANTS = {
    'equipLow': ('equipment_density', 2.7),
    'equipHigh': ('equipment_density', 8.1),
    'outdoorAirLow': ('outdoor_air_factor', 0.8),
    'outdoorAirHigh': ('outdoor_air_factor', 1.2),
}
# (label, run of the low value, run of the high value); None for the categorical switches
ASSUMPTIONS = [
    ('Occupancy level 25% / 100% of booked hours', 'scenario8', 'scenario5'),
    ('Equipment density 2.7 / 8.1 W/m²', 'equipLow', 'equipHigh'),
    ('Outdoor air per floor area −20% / +20%', 'outdoorAirLow', 'outdoorAirHigh'),
    ('Ventilation: CAV-person (S1)', None, 'scenario1'),
    ('Ventilation: VAV-person (S2)', None, 'scenario2'),
    ('Space use: closed offices (S9)', None, 'scenario9'),
]

# %% [markdown]
# ## 1. Variant models
#
# Derived from the Scenario 0 model by changing one parameter of the classroom zones.

# %%
IDF.setiddname(str(config.IDD_V24_2))
runs = []
for building in config.BUILDINGS:
    baseline = IDF(str(config.SCENARIO_RESULTS_DIR / 'scenario0' / f'{building}.idf'))
    classrooms = Scenario.ClassroomZones(baseline)
    for variant, (parameter, value) in VARIANTS.items():
        idf = copy.deepcopy(baseline)
        if parameter == 'equipment_density':
            for equipment in idf.idfobjects['ELECTRICEQUIPMENT']:
                if Scenario.ZoneNameOf(equipment) in classrooms:
                    assert float(equipment.Watts_per_Floor_Area) == NOMINAL_EQUIPMENT_DENSITY
                    equipment.Watts_per_Floor_Area = value
        else:
            for outdoor_air in idf.idfobjects['DESIGNSPECIFICATION:OUTDOORAIR']:
                if Scenario.ZoneNameOf(outdoor_air) in classrooms:
                    outdoor_air.Outdoor_Air_Flow_per_Zone_Floor_Area = float(outdoor_air.Outdoor_Air_Flow_per_Zone_Floor_Area) * value
        variant_dir = config.SENSITIVITY_RESULTS_DIR / variant
        variant_dir.mkdir(parents=True, exist_ok=True)
        idf.saveas(str(variant_dir / f'{building}.idf'))
        runs.append(variant_dir / f'{building}.idf')
print(f'{len(runs)} variant models written')

# %% [markdown]
# ## 2. Simulations

# %%
if RUN_SIMULATIONS:
    def simulate(idf_path):
        return idf_path, Eppy.EnergyPlus_RunSimulation(idfFilePath=str(idf_path), epwFilePath=str(config.EPW_PATH),
                                                       energyPlusExePath=str(config.ENERGYPLUS_EXE))

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        for idf_path, ok in pool.map(simulate, runs):
            print(f'{idf_path.parent.name} {idf_path.stem}: {"OK" if ok else "FAILED"}', flush=True)

# %% [markdown]
# ## 3. KPIs of the variants and of the scenarios

# %%
rows = []
for building in config.BUILDINGS:
    ahu_power = pd.read_excel(config.building_file(building, 'ahu_electrical_power.xlsx'), 'ahu_rated_power')
    for variant in VARIANTS:
        run = config.SENSITIVITY_RESULTS_DIR / variant / building
        kpis = KPI.BuildingKPIsByEnergyPlusResults(csvFilePath=f'{run}.csv', eioFilePath=f'{run}.eio', ahuElectricalPower=ahu_power)
        rows.append({'building': building, 'run': variant, 'energy_need_TOE': kpis['TOE'],
                     'cost_EUR': kpis['EUR'], 'co2_emissions_kgCO2eq': kpis['CO2']})

scenario_kpis = pd.read_csv(config.SCENARIO_RESULTS_DIR / 'scenario_kpis.csv').rename(columns={'scenario': 'run'})
sensitivity_kpis = pd.concat([scenario_kpis[['building', 'run', 'energy_need_TOE', 'cost_EUR', 'co2_emissions_kgCO2eq']],
                              pd.DataFrame(rows)], ignore_index=True)
sensitivity_kpis.to_csv(config.SENSITIVITY_RESULTS_DIR / 'sensitivity_kpis.csv', index=False)

# %% [markdown]
# ## 4. Change from Scenario 0 (tornado values)

# %%
KPIS = ['energy_need_TOE', 'cost_EUR', 'co2_emissions_kgCO2eq']
indexed = sensitivity_kpis.set_index(['building', 'run'])
tornado = []
for building in config.BUILDINGS:
    reference = indexed.loc[(building, 'scenario0')]
    change = lambda run, kpi: (indexed.loc[(building, run), kpi] / reference[kpi] - 1) * 100 if run else 0.0
    for kpi in KPIS:
        for label, low, high in ASSUMPTIONS:
            tornado.append({'building': building, 'kpi': kpi, 'assumption': label, 'categorical': low is None,
                            'low_pct': change(low, kpi), 'high_pct': change(high, kpi)})
tornado = pd.DataFrame(tornado)
tornado.to_csv(config.SENSITIVITY_RESULTS_DIR / 'sensitivity_tornado_values.csv', index=False)
tornado[tornado['kpi'] == 'energy_need_TOE'].round(1)
