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
# # 03 · Energy analysis of the tuned BEM
#
# Annual energy needs of the tuned BEM of a building (end of **Section 4.2**): building totals
# per end use normalised by the net floor area, monthly heating and cooling needs and zone-level
# maps of the annual heating and cooling needs.
#
# **Inputs**: simulation of the tuned BEM (`results/calibration/simulation/<building>_tuned.*`,
# from `02_bem_calibration`), TBIM with thermal zones (`models/`), IFC model, AHU electrical power.
#
# **Outputs** (`results/baseline_analysis/`): `<building>_annual_energy_needs.csv`,
# `<building>_monthly_energy_needs.csv` and figures.

# %%
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent if '__file__' in globals() else Path.cwd()
ROOT = next(p for p in (HERE, *HERE.parents) if (p / 'config.py').exists())
sys.path.insert(0, str(ROOT))
import config

import pandas as pd
import plotly.express as px
from topologicpy.Topology import Topology

from digitmanpy.Operation import KPI
from digitmanpy.Visualize import Show

# %%
BUILDING = config.cli_option('building', 'building10')

run = config.CALIBRATION_RESULTS_DIR / 'simulation' / f'{BUILDING}_tuned'
output_dir = config.BASELINE_RESULTS_DIR
figures_dir = output_dir / 'figures'
output_dir.mkdir(parents=True, exist_ok=True)
name = config.BUILDINGS[BUILDING]['name']

# %% [markdown]
# ## 1. Annual energy needs per end use

# %%
net_floor_area = KPI.NetFloorAreaByIFC(str(config.building_file(BUILDING, 'tbim_ifc_design_transfer_view.ifc')))
ahu_power = pd.read_excel(config.building_file(BUILDING, 'ahu_electrical_power.xlsx'), 'ahu_rated_power')
kpis = KPI.BuildingKPIsByEnergyPlusResults(csvFilePath=f'{run}.csv', eioFilePath=f'{run}.eio', ahuElectricalPower=ahu_power)

END_USES = {'heat': 'Heating', 'cool': 'Cooling', 'vent': 'Ventilation', 'light': 'Lighting', 'equip': 'Equipment'}
annual = pd.DataFrame({'end_use': list(END_USES.values()),
                       'annual_kWh': [kpis[k] for k in END_USES],
                       'annual_kWh_m2': [kpis[k] / net_floor_area for k in END_USES]})
annual.to_csv(output_dir / f'{BUILDING}_annual_energy_needs.csv', index=False)
print(f'{name}: net floor area {net_floor_area:,.0f} m²; energy need {kpis["TOE"]:.1f} TOE, '
      f'cost {kpis["EUR"] / 1000:.1f} k€, emissions {kpis["CO2"] / 1000:.1f} tCO₂eq')
annual.round(2)

# %% [markdown]
# ## 2. Monthly heating and cooling needs

# %%
results = pd.read_csv(f'{run}.csv')
month = results['Date/Time'].str.strip().str.slice(0, 2).astype(int)
monthly = pd.DataFrame({
    'heating_kWh': results.filter(like='Zone Ideal Loads Supply Air Total Heating Energy').sum(axis=1) * KPI.J_TO_KWH,
    'cooling_kWh': results.filter(like='Zone Ideal Loads Supply Air Total Cooling Energy').sum(axis=1) * KPI.J_TO_KWH,
}).groupby(month).sum()
monthly.index.name = 'month'
monthly.to_csv(output_dir / f'{BUILDING}_monthly_energy_needs.csv')

figure = px.bar(monthly.reset_index(), x='month', y=['heating_kWh', 'cooling_kWh'], barmode='group',
                labels={'value': 'Energy need (kWh)', 'variable': ''}, title=f'{name}: monthly heating and cooling needs')
config.show_figure(figure, f'{BUILDING}_monthly_heating_cooling', figures_dir)

# %% [markdown]
# ## 3. Annual heating and cooling needs of the thermal zones

# %%
tp_building = Topology.ByJSONPath(str(config.MODELS_DIR / f'{BUILDING}_tbim_topologic_with_zones.json'))[0]
for variable, colour_scale in (('Zone Ideal Loads Supply Air Total Heating Energy', 'reds'),
                               ('Zone Ideal Loads Supply Air Total Cooling Energy', 'blues')):
    figure = Show.TBIM_ByEnergyPlusCSV(epCSVPath=f'{run}.csv', outputVariable=variable, tpBuilding=tp_building,
                                       colorScale=colour_scale, normalizeArea=False)
    config.show_figure(figure, f"{BUILDING}_{variable.split()[-2].lower()}_by_zone", figures_dir)
