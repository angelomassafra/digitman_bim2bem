"""
DIGITMAN decision support system (Section 3.5): dashboard for the energy what-if analysis
of occupancy-management scenarios.

Run from the repository root with `python app/app.py` and open http://127.0.0.1:8050.
Requires the results of scripts 06_scenario_kpis and 08_knowledge_graph.

Created on 2025.07.30 by Angelo Massafra; edited on 2025.09.08 by Roberto Villa and Guido Romano.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))       # app/ (ewi module)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # repository root (config)
import config  # noqa: F401  (repository paths and project libraries)

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output

import ewi
from digitmanpy.Visualize import Color as DigitmanColor

FONT = 'Lato'
GRADIENT = f'linear-gradient(45deg, {DigitmanColor.Blue()}, {DigitmanColor.Green()}, {DigitmanColor.Yellow()})'

app = dash.Dash(__name__, title='DIGITMAN – Energy What-If',
                external_stylesheets=['https://fonts.googleapis.com/css2?family=Lato&display=swap', dbc.themes.LUX],
                suppress_callback_exceptions=True)
server = app.server
ewi.register_callbacks(app)

#=====================================================================================================
# LAYOUT
#=====================================================================================================

banner = html.Div(
    style={'background': 'white', 'borderBottom': '5px solid', 'borderImage': f'{GRADIENT} 1', 'marginBottom': '10px', 'height': '40px'},
    children=[html.Img(src=app.get_asset_url('logo_color_extended.png'), style={'height': '35px', 'marginLeft': '20px', 'float': 'left'})])

footer = html.Div(
    style={'background': GRADIENT, 'marginTop': '10px', 'height': '45px', 'textAlign': 'center', 'padding': '1px'},
    children=[html.P('DIGITMAN: Occupant-based DIGITal predictive MANagement to improve the built environment. '
                     '© Università Politecnica delle Marche, Politecnico di Milano, Alma Mater Studiorum Università di Bologna (2025)',
                     style={'color': 'white', 'fontFamily': FONT, 'fontWeight': '400', 'fontSize': 12, 'marginTop': '12px'})])

TABS = {'Home': '🏢', 'Energy What-If (EWI)': '⚡'}
tab_style = {'fontFamily': FONT, 'fontSize': '15px', 'fontWeight': 400, 'backgroundColor': 'white', 'color': 'gray',
             'width': '370px', 'height': '30px', 'padding': '5px 0px', 'border': 'none'}
selected_tab_style = {**tab_style, 'fontWeight': 800, 'color': 'black', 'borderBottom': f'3px solid {DigitmanColor.Green()}'}
tabs = dcc.Tabs(id='tabSelection', value='Energy What-If (EWI)',
                children=[dcc.Tab(label=f'{icon} {name}', value=name, style=tab_style, selected_style=selected_tab_style)
                          for name, icon in TABS.items()])

home = html.Div(
    style={'display': 'flex', 'flex': '1', 'alignItems': 'center', 'justifyContent': 'center', 'backgroundColor': 'white'},
    children=html.Div(style={'textAlign': 'center', 'fontFamily': FONT}, children=[
        html.Div('Welcome!', style={'fontSize': '64px', 'fontWeight': '800', 'marginTop': '200px', 'marginBottom': '30px'}),
        html.Div('Select the Energy What-If tab to compare the occupancy-management scenarios.', style={'fontSize': '28px'}),
    ]))

app.layout = html.Div([
    banner,
    html.Div(tabs, style={'backgroundColor': 'white', 'textAlign': 'center'}),
    html.Div(id='content', style={'display': 'flex', 'flexDirection': 'row', 'minHeight': '580px'}),
    footer,
])


@app.callback(Output('content', 'children'), Input('tabSelection', 'value'))
def select_tab(tab):
    return ewi.layout() if tab == 'Energy What-If (EWI)' else home


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8050, debug=False)
