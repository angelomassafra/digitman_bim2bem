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
# # 06 · Scenario KPIs
#
# Building-level KPIs of the twelve scenarios (**Sections 3.3.3 and 4.3**, Table 5) from the
# EnergyPlus outputs of `05_scenario_simulation`:
#
# * annual end uses: heating and cooling (ideal-load supply-air total energy), ventilation
#   (AHU fan electricity: rated power × hours 08:00–18:00 with non-zero supply flow), lighting
#   and equipment electricity;
# * energy need (TOE), operating cost (EUR) and CO₂ emissions (kgCO₂eq), with heating supplied by
#   natural gas and the other end uses by electricity;
# * utilisation and occupancy rates, averaged over the zones weighting by their design capacity.
#
# End uses are normalised by the net floor area of the IfcSpace entities of the IFC model.
#
# **Outputs** (`results/scenarios/`): `scenario_kpis.csv` (absolute values),
# `scenario_kpis_summary.csv` (per m² and change from Scenario 0), `zone_annual_totals.csv`
# (annual totals per zone, used by the dashboard).

# %%
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent if '__file__' in globals() else Path.cwd()
ROOT = next(p for p in (HERE, *HERE.parents) if (p / 'config.py').exists())
sys.path.insert(0, str(ROOT))
import config

import pandas as pd

from digitmanpy.Operation import KPI

scenario_definitions = json.loads((config.SCENARIO_DATA_DIR / 'scenario_definitions.json').read_text())['scenarios']
END_USES = ['heat', 'cool', 'vent', 'light', 'equip']

# %% [markdown]
# ## 1. Building KPIs of each scenario

# %%
rows = []
for building in config.BUILDINGS:
    net_floor_area = KPI.NetFloorAreaByIFC(str(config.building_file(building, 'tbim_ifc_design_transfer_view.ifc')))
    ahu_power = pd.read_excel(config.building_file(building, 'ahu_electrical_power.xlsx'), 'ahu_rated_power')
    for definition in scenario_definitions:
        run = config.SCENARIO_RESULTS_DIR / definition['uid'] / building
        kpis = KPI.BuildingKPIsByEnergyPlusResults(csvFilePath=f'{run}.csv', eioFilePath=f'{run}.eio', ahuElectricalPower=ahu_power)
        rows.append({'building': building, 'scenario': definition['uid'], 'label': definition['label'],
                     'name': definition['name'], 'net_floor_area_m2': net_floor_area, **kpis})
    print(f"{config.BUILDINGS[building]['name']}: net floor area {net_floor_area:,.0f} m²")

kpis = pd.DataFrame(rows).rename(columns={'heat': 'heating_kWh', 'cool': 'cooling_kWh', 'vent': 'ventilation_kWh',
                                          'light': 'lighting_kWh', 'equip': 'equipment_kWh',
                                          'UR': 'utilisation_rate_pct', 'OR': 'occupancy_rate_pct',
                                          'capacity': 'design_capacity_people', 'TOE': 'energy_need_TOE',
                                          'EUR': 'cost_EUR', 'CO2': 'co2_emissions_kgCO2eq'})
kpis.to_csv(config.SCENARIO_RESULTS_DIR / 'scenario_kpis.csv', index=False)

# %% [markdown]
# ## 2. Summary table (Table 5)
#
# End uses per m² of net floor area, aggregate KPIs and change from Scenario 0 (percentage
# change; percentage points for the utilisation and occupancy rates).

# %%
summary = kpis[['building', 'label', 'name']].copy()
for end_use in ['heating', 'cooling', 'ventilation', 'lighting', 'equipment']:
    summary[f'{end_use}_kWh_m2'] = kpis[f'{end_use}_kWh'] / kpis['net_floor_area_m2']
summary['total_kWh_m2'] = summary[[c for c in summary if c.endswith('_kWh_m2')]].sum(axis=1)
summary['energy_need_TOE'] = kpis['energy_need_TOE']
summary['cost_kEUR'] = kpis['cost_EUR'] / 1000
summary['co2_emissions_tCO2eq'] = kpis['co2_emissions_kgCO2eq'] / 1000
summary['utilisation_rate_pct'] = kpis['utilisation_rate_pct']
summary['occupancy_rate_pct'] = kpis['occupancy_rate_pct']

values = [c for c in summary.columns if c not in ('building', 'label', 'name')]
for building, group in summary.groupby('building'):
    reference = group[group['label'] == 'S0'].iloc[0]
    for column in values:
        change = (group[column] - reference[column]) if column.endswith('rate_pct') else (group[column] / reference[column] - 1) * 100
        summary.loc[group.index, f'{column}_change'] = change
summary.to_csv(config.SCENARIO_RESULTS_DIR / 'scenario_kpis_summary.csv', index=False)

pd.set_option('display.width', 200)
summary.pivot(index='label', columns='building', values=['total_kWh_m2', 'energy_need_TOE', 'energy_need_TOE_change']).round(1).loc[[d['label'] for d in scenario_definitions]]

# %% [markdown]
# ## 3. Annual totals per zone
#
# Annual totals of the zone output variables shown in the 3D view of the dashboard
# (energy in kWh, occupant count in person-hours), so that the dashboard does not need the
# hourly EnergyPlus results.

# %%
ZONE_VARIABLES = ['Zone Ideal Loads Zone Total Heating Energy', 'Zone Ideal Loads Zone Total Cooling Energy',
                  'Zone Lights Electricity Energy', 'Zone Electric Equipment Electricity Energy', 'Zone People Occupant Count']

totals = []
for building in config.BUILDINGS:
    for definition in scenario_definitions:
        results = pd.read_csv(config.SCENARIO_RESULTS_DIR / definition['uid'] / f'{building}.csv')
        for column in results.columns:
            if any(variable in column for variable in ZONE_VARIABLES):
                total = results[column].sum()
                if '[J]' in column:
                    total, column = total / 3.6e6, column.replace('[J]', '[kWh]')
                totals.append({'building': building, 'scenario': definition['uid'], 'column': column, 'annual_total': total})
pd.DataFrame(totals).to_csv(config.SCENARIO_RESULTS_DIR / 'zone_annual_totals.csv', index=False)
print(f'{len(totals)} zone totals written')
