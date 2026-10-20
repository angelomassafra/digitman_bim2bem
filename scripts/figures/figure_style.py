"""Shared matplotlib style, colours and output helper of the paper figures."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import config  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

CM = 1 / 2.54                       # figure sizes in cm (17.4 cm = double-column width)
MEASURED, SIMULATED = '#636EFA', '#EF553B'
NAVY, INK, AXIS, GRID = '#2a3f5f', '#444444', '#9a9a9a', '#dddddd'
BUILDING_TITLES = {'building10': 'Building 10 – Room A1.3', 'building09': 'Building 09 – Room B1.5'}

plt.rcParams.update({
    'font.family': 'Arial', 'font.size': 6.5, 'axes.titlesize': 6.8, 'axes.labelsize': 6.5,
    'xtick.labelsize': 6, 'ytick.labelsize': 6, 'pdf.fonttype': 42, 'svg.fonttype': 'none',
    'axes.edgecolor': AXIS, 'axes.linewidth': 0.5, 'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': 0.4,
    'axes.spines.top': False, 'axes.spines.right': False, 'axes.axisbelow': True,
    'xtick.major.size': 2, 'ytick.major.size': 2, 'xtick.color': INK, 'ytick.color': INK,
})


def save(figure, name, dpi=600):
    """Saves the figure as figures/<name>.png, .pdf and .svg"""
    config.FIGURES_DIR.mkdir(exist_ok=True)
    for extension in ('png', 'pdf', 'svg'):
        figure.savefig(config.FIGURES_DIR / f'{name}.{extension}', dpi=dpi)
    plt.close(figure)
    print(f'saved figures/{name}.png|pdf|svg')
