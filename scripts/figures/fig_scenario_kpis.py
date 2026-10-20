"""
Scenario KPIs (Table 5): (a, c) annual end uses per m² of net floor area with the occupancy
and utilisation rates; (b, d) change of energy need, cost and CO₂ emissions from Scenario 0,
for Building 10 (top) and Building 09 (bottom).

Input: results/scenarios/scenario_kpis_summary.csv (06_scenario_kpis).
Output: figures/scenario_kpis.png|pdf|svg
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from figure_style import config, CM, save

END_USES = [('heating_kWh_m2', 'Heating', '#EF553B'), ('cooling_kWh_m2', 'Cooling', '#636EFA'),
            ('ventilation_kWh_m2', 'Ventilation', '#2a9d8f'), ('lighting_kWh_m2', 'Lighting', '#e9c46a'),
            ('equipment_kWh_m2', 'Equipment', '#8e7cc3')]
CHANGES = [('energy_need_TOE_change', 'Energy need', '#264653'), ('cost_kEUR_change', 'Cost', '#f4a261'),
           ('co2_emissions_tCO2eq_change', 'CO$_2$ emissions', '#9a9a9a')]

summary = pd.read_csv(config.SCENARIO_RESULTS_DIR / 'scenario_kpis_summary.csv')
labels = [f'S{i}' for i in range(12)]
x = np.arange(12)

fig = plt.figure(figsize=(17.4 * CM, 15.5 * CM))
grid = fig.add_gridspec(2, 2, left=0.065, right=0.935, top=0.885, bottom=0.075, hspace=0.42, wspace=0.32, width_ratios=[1.35, 1])
letters = iter('abcd')
for row, (building, title) in enumerate((('building10', 'Building 10'), ('building09', 'Building 09'))):
    k = summary[summary['building'] == building].set_index('label').loc[labels]
    # end uses and occupancy indicators
    ax = fig.add_subplot(grid[row, 0])
    bottom = np.zeros(12)
    for column, _, colour in END_USES:
        ax.bar(x, k[column], bottom=bottom, color=colour, width=0.7, lw=0)
        bottom += k[column].values
    for xi, total in zip(x, bottom):
        ax.text(xi, total + bottom.max() * 0.01, f'{total:.0f}', ha='center', va='bottom', fontsize=5.3, color='#333333')
    ax.set_xticks(x); ax.set_xticklabels(labels)
    ax.set_ylabel('Annual energy need (kWh/m²)')
    ax.set_ylim(0, bottom.max() * 1.12)
    ax.grid(axis='x', visible=False)
    rates = ax.twinx()
    rates.plot(x, k['occupancy_rate_pct'], color='black', marker='o', ms=2.5, lw=0.8)
    rates.plot(x, k['utilisation_rate_pct'], color='black', marker='s', ms=2.3, lw=0.8, ls='--')
    rates.set_ylabel('Occupancy / utilisation rate (%)'); rates.set_ylim(0, 60)
    rates.spines['right'].set_visible(True); rates.grid(False)
    ax.set_title(f'({next(letters)}) {title}: energy need by end use and occupancy', loc='left')
    # change from Scenario 0
    ax = fig.add_subplot(grid[row, 1])
    width = 0.26
    for j, (column, _, colour) in enumerate(CHANGES):
        ax.bar(np.arange(1, 12) + (j - 1) * width, k[column].values[1:], width=width, color=colour, lw=0)
    ax.axhline(0, color='black', lw=0.7)
    ax.set_xticks(np.arange(1, 12)); ax.set_xticklabels(labels[1:])
    ax.set_ylabel('Change from S0 (%)')
    ax.grid(axis='x', visible=False)
    ax.set_title(f'({next(letters)}) {title}: change from Scenario 0', loc='left')

fig.legend(handles=[Patch(fc=c, label=l) for _, l, c in END_USES]
           + [Line2D([], [], color='black', marker='o', ms=2.5, lw=0.8, label='Occupancy rate'),
              Line2D([], [], color='black', marker='s', ms=2.3, lw=0.8, ls='--', label='Utilisation rate')]
           + [Patch(fc=c, label=l) for _, l, c in CHANGES],
           loc='upper center', ncol=5, frameon=False, fontsize=6.0, bbox_to_anchor=(0.5, 1.0), handlelength=1.4, columnspacing=1.2)
fig.text(0.5, 0.012, 'S0 current state (CAV-volume); S1 CAV-person; S2 VAV-person; S3/S4 ±20% capacity; '
         'S5–S8 classrooms 100/50/75/25% occupied; S9–S11 offices CAV-volume / CAV-person / VAV-person',
         ha='center', fontsize=5.6, color='#444444')
save(fig, 'scenario_kpis')
