"""
Shared configuration of the workflow: repository paths, EnergyPlus installation and
case-study metadata. Every script and notebook imports this module first.

The EnergyPlus installation folder can be overridden with the ENERGYPLUS_DIR
environment variable (default: C:\\EnergyPlusV24-2-0).
"""

import os
import sys
from pathlib import Path

# --- Repository paths
ROOT = Path(__file__).resolve().parent
SRC_DIR = ROOT / 'src'
DATA_DIR = ROOT / 'data'
MODELS_DIR = ROOT / 'models'
RESULTS_DIR = ROOT / 'results'
FIGURES_DIR = ROOT / 'figures'

SCHEDULES_DIR = DATA_DIR / 'schedules'
WEATHER_DIR = DATA_DIR / 'weather'
MONITORING_DIR = DATA_DIR / 'monitoring'
SCENARIO_DATA_DIR = DATA_DIR / 'scenarios'

BEM_RESULTS_DIR = RESULTS_DIR / 'bem'                       # 01_bim_to_bem
CALIBRATION_RESULTS_DIR = RESULTS_DIR / 'calibration'       # 02_bem_calibration
BASELINE_RESULTS_DIR = RESULTS_DIR / 'baseline_analysis'    # 03_baseline_analysis
SCENARIO_RESULTS_DIR = RESULTS_DIR / 'scenarios'            # 04-06 scenario modelling, simulation, KPIs
SENSITIVITY_RESULTS_DIR = RESULTS_DIR / 'sensitivity'       # 07_sensitivity_analysis
KNOWLEDGE_GRAPH_DIR = RESULTS_DIR / 'knowledge_graph'       # 08_knowledge_graph

# UTF-8 console output (units such as m² and CO₂ on the Windows console)
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, 'reconfigure'):
        stream.reconfigure(encoding='utf-8')

# Local settings and credentials from .env (see .env.example); existing variables win
if (ROOT / '.env').exists():
    for line in (ROOT / '.env').read_text().splitlines():
        if '=' in line and not line.lstrip().startswith('#'):
            key, value = line.split('=', 1)
            os.environ.setdefault(key.strip(), value.strip())

# Make the project libraries (src/digitmanpy, src/btwinpy) importable
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# --- EnergyPlus
# The BEMs are generated for EnergyPlus 24.1 (as in the paper) and converted to 24.2
# before simulation; only the 24.2 installation is required, since it ships the
# 24.1 dictionary and the 24.1 -> 24.2 transition program.
ENERGYPLUS_DIR = Path(os.environ.get('ENERGYPLUS_DIR', r'C:\EnergyPlusV24-2-0'))
ENERGYPLUS_EXE = ENERGYPLUS_DIR / 'energyplus.exe'
IDF_UPDATER_DIR = ENERGYPLUS_DIR / 'PreProcess' / 'IDFVersionUpdater'
IDD_V24_1 = IDF_UPDATER_DIR / 'V24-1-0-Energy+.idd'
IDD_V24_2 = ENERGYPLUS_DIR / 'Energy+.idd'
TRANSITION_V24_1_TO_V24_2 = IDF_UPDATER_DIR / 'Transition-V24-1-0-to-V24-2-0.exe'

# Weather data: on-site measurements of the Lecco campus station (EPW) and design days
EPW_PATH = WEATHER_DIR / 'Lecco_IT-hour.epw'
DDY_PATH = WEATHER_DIR / 'ITA_LM_Grigna.Settentrion.160700_TMYx.ddy'

# Annual run period of all simulations
RUN_PERIOD = {'beginMonth': 1, 'beginDayOfMonth': 1, 'endMonth': 12, 'endDayOfMonth': 31,
              'beginYear': 2024, 'endYear': 2024}

# --- Case study: Lecco Campus, Politecnico di Milano
SITE = {'portfolio': ('SK001', 'POLIMI'), 'region': ('LCF', 'Lecco'), 'site': ('LCF04', 'Via Ghislanzoni')}

# Asset codes of the university portfolio (used as building UIDs in the knowledge graph)
BUILDINGS = {
    'building09': {'uid': 'LCF0406', 'name': 'Building 09', 'idf_name': 'building09'},
    'building10': {'uid': 'LCF0407', 'name': 'Building 10', 'idf_name': 'building10'},
}

# Monitored classrooms used for the BEM calibration (Section 4.2): EnergyPlus zone of the
# classroom and column of the monitoring dataset with its mean indoor air temperature
MONITORED_ROOMS = {
    'building09': {'room': 'B1.5', 'zone': 'ZONE45', 'sensor_column': 'B15_AirTemperature_Mean'},
    'building10': {'room': 'A1.3', 'zone': 'ZONE18', 'sensor_column': 'A13_AirTemperature_Mean'},
}


def cli_option(name, default=None):
    """
    Value of a '--name value' command-line option, or the default. Unknown arguments are
    ignored, so that the same code runs as a script and inside a Jupyter kernel.
    """
    flag = f'--{name}'
    if flag in sys.argv[:-1]:
        return sys.argv[sys.argv.index(flag) + 1]
    return default


def show_figure(figure, name, folder):
    """
    Displays a Plotly figure inline when running in Jupyter; when running as a script the
    figure is saved as <folder>/<name>.html instead.
    """
    if 'ipykernel' in sys.modules:
        figure.show()
    else:
        folder = Path(folder)
        folder.mkdir(parents=True, exist_ok=True)
        figure.write_html(folder / f'{name}.html', include_plotlyjs='cdn')


def building_data_dir(building):
    """Folder with the input data of a building (TBIM, IFC, shades, AHU data)."""
    return DATA_DIR / building


def building_file(building, suffix):
    """Input file of a building, e.g. building_file('building09', 'tbim_topologic.json')."""
    return building_data_dir(building) / f'{building}_{suffix}'
