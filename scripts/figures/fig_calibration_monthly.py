"""
Figures 8 and 9: monthly mean measured vs simulated indoor temperature after the tuning, and
monthly difference between the mean measured and mean simulated temperature, for Building 10
(top) and Building 09 (bottom).

Input: results/calibration/<building>_monthly_temperature_comparison.csv (02_bem_calibration).
Output: figures/calibration_monthly_means.png|pdf|svg, figures/calibration_monthly_difference.png|pdf|svg
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from figure_style import config, CM, MEASURED, SIMULATED, BUILDING_TITLES, save

MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
BUILDINGS = ('building10', 'building09')
monthly = {b: pd.read_csv(config.CALIBRATION_RESULTS_DIR / f'{b}_monthly_temperature_comparison.csv', index_col='month') for b in BUILDINGS}

# Figure 8: monthly means
fig, axes = plt.subplots(2, 1, figsize=(17.4 * CM, 11 * CM), sharex=True)
for ax, building in zip(axes, BUILDINGS):
    m, x = monthly[building], np.arange(12)
    ax.bar(x - 0.2, m['measured'], width=0.4, color=MEASURED, label='Measured')
    ax.bar(x + 0.2, m['tuned'], width=0.4, color=SIMULATED, label='Simulated (tuned BEM)')
    ax.set_ylabel('Mean temperature (°C)')
    ax.set_title(BUILDING_TITLES[building], loc='left')
    ax.grid(axis='x', visible=False)
axes[-1].set_xticks(np.arange(12)); axes[-1].set_xticklabels(MONTHS)
axes[0].legend(loc='upper right', frameon=False, ncol=2)
fig.tight_layout()
save(fig, 'calibration_monthly_means')

# Figure 9: monthly difference measured − simulated, with the ±1 °C band (≈5% of 20 °C)
fig, axes = plt.subplots(2, 1, figsize=(17.4 * CM, 10 * CM), sharex=True)
for ax, building in zip(axes, BUILDINGS):
    difference = monthly[building]['measured'] - monthly[building]['tuned']
    ax.axhspan(-1, 1, color='#eeeeee', lw=0, zorder=0)
    ax.bar(np.arange(12), difference, width=0.6, color=[MEASURED if abs(d) <= 1 else SIMULATED for d in difference])
    ax.axhline(0, color='black', lw=0.7)
    ax.set_ylabel('Measured − simulated (°C)')
    ax.set_title(BUILDING_TITLES[building], loc='left')
    ax.grid(axis='x', visible=False)
axes[-1].set_xticks(np.arange(12)); axes[-1].set_xticklabels(MONTHS)
fig.tight_layout()
save(fig, 'calibration_monthly_difference')
