"""
Energy What-If (EWI) module of the DIGITMAN decision support system (Section 3.5).

Reads the knowledge graph produced by scripts/08_knowledge_graph.py and shows, for the
selected building and scenario: a 3D view of the thermal zones coloured by an annual
EnergyPlus output, the KPI cards of the current state (Scenario 0) and of the selected
scenario, and a radar chart comparing their normalised KPIs.

Created on 2025.07.30 by Angelo Massafra.
"""

import re
import sys
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import config

import networkx as nx
import pandas as pd
import plotly.graph_objects as go
import dash_daq as daq
from dash import dcc, html
from dash.dependencies import Input, Output
from topologicpy.Topology import Topology

from btwinpy.KnowledgeGraph import KnowledgeGraph
from btwinpy.Plot import Plot
from digitmanpy.Visualize import Color as DigitmanColor
from digitmanpy.Visualize import Show

ASSETS_DIR = Path(__file__).resolve().parent / 'assets'
GRAPH_PATH = config.KNOWLEDGE_GRAPH_DIR / 'ewi_knowledge_graph.json'
ZONE_TOTALS_PATH = config.SCENARIO_RESULTS_DIR / 'zone_annual_totals.csv'
CURRENT_SCENARIO = 'scenario0'
KPI_SET_TYPE = 'OperationKPIs-WhatIf'

print('EWI - loading the knowledge graph...')


#=====================================================================================================
# 01 - DATA
#=====================================================================================================

graph = KnowledgeGraph.ByJSONLDPath(str(GRAPH_PATH))
graph.remove_nodes_from(list(nx.isolates(graph)))


def nodes_of_type(object_type):
    return [graph.nodes[n] for n in KnowledgeGraph.SubGraphByObjectTypes(graph, objectTypes=[object_type])]


def linked_nodes(uid, node_type, relationship):
    return [n[1] for n in KnowledgeGraph.NodeLinkedNodes(graph=graph, nodeObjectUID=uid, linkedNodesType=node_type, relationshipName=relationship)]


BUILDING_KEYS = {metadata['uid']: building for building, metadata in config.BUILDINGS.items()}

# TBIMs with thermal zones, from the documents of the buildings
tbims = {}
for document in nodes_of_type('btwin:Document'):
    if document['UID'].endswith('_tbim_topologic_with_zones.json'):
        building_uid = linked_nodes(document['UID'], 'bot:Building', 'btwin:isDocumentOf')[0]['UID']
        tbims[building_uid] = Topology.ByJSONPath(str(config.ROOT / document['UID']))[0]

# Annual totals of the zone outputs of each scenario (from scripts/06_scenario_kpis.py)
zone_totals = pd.read_csv(ZONE_TOTALS_PATH)
# Zone floor plans and cell edges of each building, computed on the first 3D view and then reused
geometry_cache = {building_uid: {} for building_uid in tbims}

scenarios = {s['UID']: s for s in nodes_of_type('btwin:Scenario')}
scenario_order = sorted(scenarios, key=lambda uid: int(re.sub(r'\D', '', uid)))


#=====================================================================================================
# 02 - HELPERS
#=====================================================================================================

def prettify_kpi_name(kpi_name, prefix='kp_'):
    """'kp_BuildingCO2Emissions_mq' -> 'CO₂ Emissions/m²'"""
    kpi_name = kpi_name[len(prefix):] if kpi_name.startswith(prefix) else kpi_name
    kpi_name = re.sub(r'(?<!^)(?=[A-Z])', ' ', kpi_name)
    return kpi_name.replace('Building ', '').replace('C O2', 'CO₂').replace('_mq', '/m²')


def scenario_kpis(scenario_uid, building_uid):
    """KPIs of a building in a scenario: {kpi name: {'value': ..., 'unit': ...}}"""
    for kpi_set in linked_nodes(scenario_uid, 'btwin:KPISet', 'btwin:hasScenario'):
        if KPI_SET_TYPE in kpi_set['UID']:
            if linked_nodes(kpi_set['UID'], 'bot:Building', 'eko:hasAssociatedObject')[0]['UID'] == building_uid:
                return {name: kpi['nominalValue'] for name, kpi in kpi_set['hasKPIs'].items()}
    return {}


def zone_view(scenario_uid, building_uid, output_variable):
    """Floor plans of the thermal zones coloured by the annual total of an EnergyPlus output"""
    totals = zone_totals[(zone_totals['building'] == BUILDING_KEYS[building_uid]) & (zone_totals['scenario'] == scenario_uid)]
    return Show.TBIM_ByEnergyPlusCSV(tpBuilding=tbims[building_uid], outputVariable=output_variable,
                                     columnTotals=dict(zip(totals['column'], totals['annual_total'])),
                                     subTitle='Annual total, 1 January - 31 December 2024',
                                     colorScale='haline', normalizeArea=False, width=720, height=450,
                                     geometryCache=geometry_cache[building_uid])


def kpi_card(kpis, kpi_name, icon, colour):
    kpi = kpis[kpi_name]
    value, unit = kpi['value'], kpi['unit']
    if unit == 'ratio':
        value, unit = round(value * 100, 2), '%'
    return Plot.KPICardByKPIValue(kpiName=prettify_kpi_name(kpi_name), kpiValue=value, kpiUnit=unit, width=110, height=80,
                                  fontSize=11, numberSize=14, numberColor=colour, icon=str(icon), icon_size=(24, 24), icon_pad_y=0.4)


def kpi_cards(scenario_uid, building_uid, normalize, current):
    """KPI cards of the current scenario (green) or of the selected scenario (blue)"""
    colour, suffix = (DigitmanColor.Green(), '_green') if current else (DigitmanColor.Blue(), '')
    per_area = '_mq' if normalize else ''
    cards = [('kp_BuildingUtilizationRate', 'occupancy'), ('kp_BuildingOccupancyRate', 'occupancy'),
             (f'kp_BuildingEnergyNeed{per_area}', 'energy'), (f'kp_BuildingCosts{per_area}', 'cost'),
             (f'kp_BuildingCO2Emissions{per_area}', 'emission')]
    kpis = scenario_kpis(scenario_uid, building_uid)
    return [dcc.Graph(figure=kpi_card(kpis, name, ASSETS_DIR / f'icon_{icon}{suffix}.png', colour)) for name, icon in cards]


def radar_chart(building_uid, scenario_uids, colours, height=280):
    """KPIs of the selected scenarios normalised on the range of all the scenarios of the building"""
    data = {}
    for uid in scenario_order:
        kpis = scenario_kpis(uid, building_uid)
        data[uid] = {f"{prettify_kpi_name(k)} [{v['unit']}]": v['value'] for k, v in kpis.items() if not k.endswith('_mq')}
    df = pd.DataFrame.from_dict(data, orient='index')
    normalised = (df - df.min()) / (df.max() - df.min()).replace(0, 1)
    labels = [c.split('[')[0].strip() for c in df.columns]
    figure = go.Figure()
    for uid, colour in zip(scenario_uids, colours):
        r = normalised.loc[uid].tolist()
        values = df.loc[uid].tolist()
        figure.add_trace(go.Scatterpolar(
            r=r + r[:1], theta=labels + labels[:1], mode='lines', line=dict(color=colour, width=4),
            name=scenarios[uid]['name'],
            customdata=[f'{label}: {value:.2f}' for label, value in zip(labels + labels[:1], values + values[:1])],
            hovertemplate='%{customdata}<br><b>%{fullData.name}</b><extra></extra>'))
    figure.update_layout(font=dict(family=FONT), polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                         showlegend=True, height=height, margin=dict(l=60, r=60, t=80, b=60),
                         legend=dict(orientation='h', yanchor='bottom', y=1.15, xanchor='center', x=0.5))
    return figure


#=====================================================================================================
# 03 - STYLE
#=====================================================================================================

FONT = 'Lato'
style_div_left = {'flex': '1', 'display': 'flex', 'flexDirection': 'column', 'maxHeight': '550px', 'maxWidth': '800px',
                  'marginTop': '10px', 'marginRight': '5px', 'boxShadow': '0 4px 8px rgba(0,0,0,0.1)', 'padding': '10px'}
style_div_left_top = {'backgroundColor': 'white', 'flex': '1', 'display': 'flex', 'flexDirection': 'row', 'alignItems': 'center'}
style_div_left_bottom = {'backgroundColor': 'white', 'flex': '6', 'marginTop': '5px', 'marginBottom': '5px', 'overflow': 'auto'}
style_div_right = {'flex': '1', 'display': 'flex', 'flexDirection': 'column', 'maxHeight': '550px', 'marginTop': '10px', 'marginLeft': '5px'}
style_div_right_content = {'backgroundColor': 'white', 'flex': '1.8', 'boxShadow': '0 4px 8px rgba(0,0,0,0.1)', 'padding': '10px',
                           'display': 'flex', 'flexDirection': 'column', 'overflowY': 'auto'}
style_toggle = {'fontFamily': FONT, 'marginLeft': '0px', 'marginTop': '10px', 'fontSize': '8px', 'width': '120px'}
style_dropdown = {'fontFamily': FONT, 'fontSize': '12px', 'fontWeight': 500, 'marginTop': '3px'}
style_dropdown_title = {'fontFamily': FONT, 'fontSize': 13}
style_card_grid = {'display': 'grid', 'gridTemplateColumns': 'repeat(5, 1fr)', 'gridTemplateRows': 'repeat(1, auto)', 'gap': '10px'}
style_heading = {'fontFamily': FONT, 'fontSize': 11, 'marginLeft': '15px'}


#=====================================================================================================
# 04 - CONTENT
#=====================================================================================================

OUTPUT_VARIABLES = {
    'Heating Energy [kWh]': 'Zone Ideal Loads Zone Total Heating Energy',
    'Cooling Energy [kWh]': 'Zone Ideal Loads Zone Total Cooling Energy',
    'Lighting Energy [kWh]': 'Zone Lights Electricity Energy',
    'Equipment Energy [kWh]': 'Zone Electric Equipment Electricity Energy',
    'People Count [person-hours]': 'Zone People Occupant Count',
}

sites = sorted(({'label': s['name'], 'value': s['UID']} for s in nodes_of_type('bot:Site')), key=lambda o: o['label'])
default_site = sites[0]['value']
site_buildings = {b['UID']: b['name'] for b in linked_nodes(default_site, 'bot:Building', 'brick:hasLocation')}
default_building = next(iter(site_buildings))


def dropdown(title, component_id, options, value, width):
    return html.Div([
        html.Label(title, style={**style_dropdown_title, 'marginLeft': '15px'}),
        dcc.Dropdown(id=component_id, options=options, value=value, clearable=False,
                     style={**style_dropdown, 'width': width, 'marginLeft': '10px'}),
    ])


dropdowns = [
    dropdown('Select site', 'ewi_dropdown-site', sites, default_site, '140px'),
    dropdown('Select building', 'ewi_dropdown-building', [{'label': n, 'value': u} for u, n in site_buildings.items()], default_building, '150px'),
    dropdown('Select scenario', 'ewi_dropdown-scenario', [{'label': scenarios[u]['name'], 'value': u} for u in scenario_order], CURRENT_SCENARIO, '200px'),
    dropdown('Select output variable', 'ewi_dropdown-outputVar', [{'label': k, 'value': v} for k, v in OUTPUT_VARIABLES.items()],
             OUTPUT_VARIABLES['Heating Energy [kWh]'], '195px'),
]

DEFAULT_DESCRIPTION = ('You are visualizing the key performance indicators of the current scenario, which represents the '
                       'current condition of the building. Please select another scenario to compare it with the current one!')

kpi_panel = html.Div(children=[
    html.H3('KPIs of the selected building in the current scenario', style=style_heading),
    html.Div(id='ewi_figure-kpiScoreCard-currentScenario', style=style_card_grid,
             children=kpi_cards(CURRENT_SCENARIO, default_building, False, current=True)),
    html.H3('KPIs of the selected building in the selected scenario', style=style_heading),
    html.Div(id='ewi_figure-kpiScoreCard-newScenario', style=style_card_grid,
             children=kpi_cards(CURRENT_SCENARIO, default_building, False, current=False)),
    html.Div(style={'display': 'flex', 'flexDirection': 'row', 'alignItems': 'flex-start', 'justifyContent': 'space-between',
                    'marginTop': '10px', 'overflowY': 'auto'},
             children=[
                 html.Div(style={'display': 'flex', 'flexDirection': 'column', 'flex': '1', 'maxWidth': '50%', 'marginLeft': '25px'},
                          children=[
                              html.Label('Normalize KPIs (per m²)', style={**style_dropdown_title, 'textAlign': 'left', 'marginLeft': '10px'}),
                              daq.ToggleSwitch(id='toggle-normalizeKPIs', label=['Off', 'On'], value=False, style=style_toggle),
                              html.P(DEFAULT_DESCRIPTION, id='ewi_text-scenarioDescription',
                                     style={'fontSize': '12px', 'lineHeight': '1.5', 'marginTop': '10px', 'fontFamily': 'Lato, sans-serif',
                                            'whiteSpace': 'pre-line', 'textAlign': 'justify'}),
                          ]),
                 html.Div(style={'flex': '2.5', 'maxWidth': '80%', 'padding': '0px', 'overflow': 'hidden'},
                          children=dcc.Graph(id='ewi_figure-radarChart',
                                             figure=radar_chart(default_building, [CURRENT_SCENARIO], [DigitmanColor.Green()]))),
             ]),
])


#=====================================================================================================
# 05 - CALLBACKS
#=====================================================================================================

def register_callbacks(app):

    @app.callback(
        [Output('ewi_figure-radarChart', 'figure'),
         Output('ewi_figure-kpiScoreCard-newScenario', 'children'),
         Output('ewi_figure-kpiScoreCard-currentScenario', 'children'),
         Output('ewi_text-scenarioDescription', 'children')],
        [Input('ewi_dropdown-scenario', 'value'),
         Input('ewi_dropdown-building', 'value'),
         Input('toggle-normalizeKPIs', 'value')])
    def update_scenario(scenario_uid, building_uid, normalize):
        compared = [CURRENT_SCENARIO] if scenario_uid == CURRENT_SCENARIO else [CURRENT_SCENARIO, scenario_uid]
        radar = radar_chart(building_uid, compared, [DigitmanColor.Green(), DigitmanColor.Blue()])
        description = DEFAULT_DESCRIPTION if scenario_uid == CURRENT_SCENARIO else (
            f"You are comparing the key performance indicators of the current scenario with those of scenario "
            f"'{scenarios[scenario_uid]['name']}' for {site_buildings.get(building_uid, building_uid)}.\n\n"
            f"{scenarios[scenario_uid].get('description', '')}")
        return (radar,
                kpi_cards(scenario_uid, building_uid, normalize, current=False),
                kpi_cards(CURRENT_SCENARIO, building_uid, normalize, current=True),
                description)

    @app.callback(
        Output('ewi_figure-3d', 'figure'),
        [Input('ewi_dropdown-scenario', 'value'),
         Input('ewi_dropdown-building', 'value'),
         Input('ewi_dropdown-outputVar', 'value')])
    def update_zone_view(scenario_uid, building_uid, output_variable):
        return zone_view(scenario_uid, building_uid, output_variable)


#=====================================================================================================
# 06 - LAYOUT
#=====================================================================================================

def layout():
    return html.Div(
        id='ewi-root', style={'display': 'flex', 'flexDirection': 'row', 'minHeight': '580px'},
        children=[
            html.Div(style=style_div_left, children=[
                html.Div(style=style_div_left_top, children=dropdowns),
                dcc.Loading(type='circle', style={'height': '100%', 'width': '100%', 'display': 'flex'},
                            children=html.Div(style=style_div_left_bottom, children=[
                                dcc.Graph(id='ewi_figure-3d', figure=zone_view(CURRENT_SCENARIO, default_building, OUTPUT_VARIABLES['Heating Energy [kWh]']))])),
            ]),
            html.Div(style=style_div_right, children=[html.Div(style=style_div_right_content, children=kpi_panel)]),
        ])


def _warm_geometry_cache():
    """Computes the zone floor plans of all the buildings in the background, so that the 3D view
    updates in a few seconds after the first rendering"""
    for building_uid in tbims:
        zone_view(CURRENT_SCENARIO, building_uid, OUTPUT_VARIABLES['Heating Energy [kWh]'])
    print('EWI - 3D geometry of all the buildings ready')


threading.Thread(target=_warm_geometry_cache, daemon=True).start()
print('EWI - module ready')
