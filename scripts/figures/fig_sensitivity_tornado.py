"""
Figure 10: one-at-a-time sensitivity of the annual energy need, operating cost and CO₂ emissions
to the assumptions of the scenario matrix, for Building 10 (top) and Building 09 (bottom).
Each bar shows the percentage change from Scenario 0.

Input: results/sensitivity/sensitivity_tornado_values.csv (07_sensitivity_analysis).
Output: figures/sensitivity_tornado.png|pdf|svg
"""

import pandas as pd
import matplotlib.pyplot as plt

from figure_style import config, NAVY, INK, AXIS, GRID, save

LOW, HIGH = '#636efa', '#ef553b'
KPIS = [('energy_need_TOE', 'Energy need (TOE)'), ('cost_EUR', 'Operating cost (€)'), ('co2_emissions_kgCO2eq', 'CO$_2$ emissions (tCO$_2$eq)')]
BUILDINGS = [('building10', 'Building 10'), ('building09', 'Building 09')]
# Line breaks of the assumption labels
WRAP = {'Occupancy level 25% / 100% of booked hours': 'Occupancy level\n25% / 100% of booked hours',
        'Equipment density 2.7 / 8.1 W/m²': 'Equipment density\n2.7 / 8.1 W/m²',
        'Outdoor air per floor area −20% / +20%': 'Outdoor air per floor area\n−20% / +20%'}


def label(value):
    text = f'{value:+.1f}'
    return ('0.0' if text in ('+0.0', '-0.0') else text).replace('-', '−')


tornado = pd.read_csv(config.SENSITIVITY_RESULTS_DIR / 'sensitivity_tornado_values.csv')
plt.rcParams.update({'font.size': 8, 'axes.unicode_minus': True, 'mathtext.default': 'regular', 'text.color': INK,
                     'axes.labelcolor': INK, 'ytick.major.size': 0, 'axes.grid': False})
fig, axes = plt.subplots(2, 3, figsize=(7.2, 6.0), sharex=True)
for row, (building, title) in enumerate(BUILDINGS):
    values = tornado[tornado['building'] == building]
    # assumptions ordered by the largest swing of the energy need (largest on top)
    swing = values[values['kpi'] == 'energy_need_TOE'].set_index('assumption')[['low_pct', 'high_pct']].abs().max(axis=1)
    order = swing.sort_values().index.tolist()
    for col, (kpi, kpi_title) in enumerate(KPIS):
        ax = axes[row, col]
        data = values[values['kpi'] == kpi].set_index('assumption').loc[order]
        for y, (assumption, r) in enumerate(data.iterrows()):
            bars = [(y, r['high_pct'], NAVY, 0.6)] if r['categorical'] else [(y + 0.17, r['low_pct'], LOW, 0.32), (y - 0.17, r['high_pct'], HIGH, 0.32)]
            for y_bar, value, colour, height in bars:
                ax.barh(y_bar, value, color=colour, height=height)
                ax.text(value + (1 if value >= 0 else -1), y_bar, label(value), va='center', ha='left' if value >= 0 else 'right', fontsize=6.5)
        ax.axvline(0, color='k', lw=0.8)
        ax.set_yticks(range(len(order)))
        ax.set_yticklabels([WRAP.get(a, a) for a in order] if col == 0 else [], fontsize=7)
        ax.grid(axis='x', lw=0.5, color=GRID); ax.set_axisbelow(True)
        ax.set_title(kpi_title, loc='left', fontsize=8.5)
        if row == 1:
            ax.set_xlabel('Change from Scenario 0 (%)')
    fig.text(0.01, (0.905, 0.465)[row], title, color=NAVY, fontsize=10.5, fontweight='bold', ha='left')
limit = tornado[['low_pct', 'high_pct']].abs().max().max() * 1.5
for ax in axes.flat:
    ax.set_xlim(-limit, limit)
fig.legend([plt.Rectangle((0, 0), 1, 1, color=c) for c in (LOW, HIGH, NAVY)], ['Lower value', 'Higher value', 'Categorical switch'],
           loc='upper right', ncol=3, frameon=False, bbox_to_anchor=(0.99, 0.995), handlelength=1.8)
fig.tight_layout(rect=(0, 0, 1, 0.93), h_pad=3.2)
save(fig, 'sensitivity_tornado', dpi=300)
