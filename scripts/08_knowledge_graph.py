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
# # 08 · Knowledge graph of models, scenarios and KPIs
#
# Integrates the models, simulation results and KPIs of the case study in a Labelled Property
# Graph (**Section 3.4**, Figures 3–4) with the BTwin library:
#
# 1. spatial hierarchy: portfolio → region → `bot:Site` → `bot:Building` → `bot:Storey` → `bot:Space`,
#    with the thermal zones of the BEM (`brick:Energy_Zone`) and one fire zone per building;
# 2. `btwin:Scenario` nodes of the twelve what-if scenarios;
# 3. `btwin:Document` nodes of the IFC model, the TBIM, the scenario BEMs (IDF) and their results (CSV);
# 4. `btwin:KPISet` nodes with the building KPIs of each scenario (from `06_scenario_kpis`).
#
# A KPI of a building in a scenario is retrieved following
# `bot:Building ← eko:hasAssociatedObject ← btwin:KPISet → btwin:hasScenario → btwin:Scenario`.
#
# **Output**: JSON-LD graph `results/knowledge_graph/ewi_knowledge_graph.json`, read by the dashboard.
# Optionally, the graph is also written to a Neo4j database (`--neo4j yes`): the connection URI,
# username and password are asked at run time and never stored.

# %% [markdown]
# ## 0. Set-up

# %%
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent if '__file__' in globals() else Path.cwd()
ROOT = next(p for p in (HERE, *HERE.parents) if (p / 'config.py').exists())
sys.path.insert(0, str(ROOT))
import config

import ifcopenshell
import pandas as pd

from btwinpy.DataFormat import DataFormat
from btwinpy.Document import Document
from btwinpy.IFC import IFC
from btwinpy.KnowledgeGraph import KnowledgeGraph
from btwinpy.KPISet import KPISet, KPI
from btwinpy.Plot import Plot
from btwinpy.Scenario import Scenario
from btwinpy.SpatialElement import SpatialElement

config.KNOWLEDGE_GRAPH_DIR.mkdir(parents=True, exist_ok=True)
graph_path = config.KNOWLEDGE_GRAPH_DIR / 'ewi_knowledge_graph.json'
scenario_definitions = json.loads((config.SCENARIO_DATA_DIR / 'scenario_definitions.json').read_text())['scenarios']


def relative(path):
    """Documents are identified by their path relative to the repository root"""
    return Path(path).resolve().relative_to(config.ROOT).as_posix()


def ifc_path(building):
    return config.building_file(building, 'tbim_ifc_design_transfer_view.ifc')


def tbim_path(building):
    return config.MODELS_DIR / f'{building}_tbim_topologic_with_zones.json'


# %% [markdown]
# ## 1. Spatial elements

# %% [markdown]
# ### 1.1 Portfolio, region and site

# %%
portfolio = SpatialElement.Constructor(spatialElementUID=config.SITE['portfolio'][0], spatialElementType='brick:Portfolio', name=config.SITE['portfolio'][1])
region = SpatialElement.Constructor(spatialElementUID=config.SITE['region'][0], spatialElementType='brick:Region', name=config.SITE['region'][1])
region = SpatialElement.SetRelationship(spatialElementObject=region, relationshipName='brick:hasLocation', linkedObject=portfolio)
site = SpatialElement.Constructor(spatialElementUID=config.SITE['site'][0], spatialElementType='bot:Site', name=config.SITE['site'][1])
site = SpatialElement.SetRelationship(spatialElementObject=site, relationshipName='brick:hasLocation', linkedObject=region)

# %% [markdown]
# ### 1.2 Buildings and storeys (from the IFC models)

# %%
# 'Nome' ("Name"): room-code property of the IFC files exported from the Italian-language Revit
buildings, storeys = [], []
for building, metadata in config.BUILDINGS.items():
    hierarchy = DataFormat.SpatialHierarchyByIFC(ifcPath=str(ifc_path(building)), siteObject=site, humanReadableUIDs=True,
                                                 buildingUID=metadata['uid'], buildingName=metadata['name'],
                                                 includePSets=False, spaceUIDPropertyName='Nome')['@graph']
    buildings += [o for o in hierarchy if o['@type'] == 'bot:Building']
    storeys += [o for o in hierarchy if o['@type'] == 'bot:Storey']

# %% [markdown]
# ### 1.3 Spaces
#
# One `bot:Space` per IfcSpace, identified by the room code of the university inventory and
# located in its storey. The room code is stored in the `Nome` ("Name") property, as the IFC
# files were exported from an Italian-language Revit installation.

# %%
spaces = {}
for building, metadata in config.BUILDINGS.items():
    for ifc_space in ifcopenshell.open(str(ifc_path(building))).by_type('IfcSpace'):
        space_name = IFC.IfcSpaceGetPropertyValue(ifcSpace=ifc_space, propertyName='UID')
        space_uid = IFC.IfcSpaceGetPropertyValue(ifcSpace=ifc_space, propertyName='Nome')
        if space_uid == 'Space':      # spaces without a room code
            space_uid = f"{metadata['uid']}_{space_name}"
        if space_uid in spaces:
            continue
        space = SpatialElement.Constructor(spatialElementUID=space_uid, name=space_name, spatialElementType='bot:Space')
        storey = IFC.IfcStoreyByIfcSpace(ifcSpace=ifc_space)
        spaces[space_uid] = SpatialElement.SetRelationship(spatialElementObject=space, relationshipName='brick:hasLocation',
                                                           linkedObjectUID=storey.Name, linkedObjectType='bot:Storey')
print(f'{len(spaces)} spaces')

# %% [markdown]
# ### 1.4 Thermal zones and fire zones
#
# Thermal zones from the TBIM cells (`rl_HasLocation_tpZN`, set by the BIM-to-BEM zoning); each
# space is linked to its thermal zone and to the fire zone of its building.

# %%
energy_zones, fire_zones = {}, []
for building, metadata in config.BUILDINGS.items():
    building_uid = metadata['uid']
    fire_zone_uid = f'fireZone_{building_uid}'
    fire_zone = SpatialElement.Constructor(spatialElementUID=fire_zone_uid, name='', spatialElementType='brick:Fire_Zone')
    fire_zones.append(SpatialElement.SetRelationship(spatialElementObject=fire_zone, relationshipName='brick:hasLocation',
                                                     linkedObjectUID=building_uid, linkedObjectType='bot:Building'))
    cells = [o['dictionary'] for o in json.loads(tbim_path(building).read_text()) if o.get('type') == 'Cell']
    for cell in cells:
        zone = cell.get('rl_HasLocation_tpZN')
        if zone is None:
            continue
        zone_uid = f'{building_uid}_{zone}'
        if zone_uid not in energy_zones:
            energy_zone = SpatialElement.Constructor(spatialElementUID=zone_uid, name='', spatialElementType='brick:Energy_Zone')
            energy_zones[zone_uid] = SpatialElement.SetRelationship(spatialElementObject=energy_zone, relationshipName='brick:hasLocation',
                                                                    linkedObjectUID=building_uid, linkedObjectType='bot:Building')
        space_uid = cell.get('rl_HasLocation_tpSP')
        if space_uid == 'Space':
            space_uid = f"{building_uid}_{cell['UID']}"
        if space_uid in spaces:
            space = spaces[space_uid]
            if 'Energy' not in str(space['relationships']['brick:hasLocation']):
                space = SpatialElement.SetRelationship(spatialElementObject=space, relationshipName='brick:hasLocation',
                                                       linkedObjectUID=zone_uid, linkedObjectType='brick:Energy_Zone')
            spaces[space_uid] = SpatialElement.SetRelationship(spatialElementObject=space, relationshipName='brick:hasLocation',
                                                               linkedObjectUID=fire_zone_uid, linkedObjectType='brick:Fire_Zone')
print(f'{len(energy_zones)} thermal zones')

# %% [markdown]
# ## 2. Scenarios and documents

# %%
scenarios = [Scenario.Constructor(scenarioUID=d['uid'], name=f"{d['label']} - {d['name']}", description=d['description'])
             for d in scenario_definitions]


def document(path, name, building_uid, scenario_uids):
    doc = Document.Constructor(relative(path), 'btwin:Document', name=name)
    doc = Document.SetRelationship(doc, relationshipName='btwin:isDocumentOf', linkedObjectUID=building_uid, linkedObjectType='bot:Building')
    for scenario_uid in scenario_uids:
        doc = Document.SetRelationship(doc, relationshipName='btwin:hasScenario', linkedObjectUID=scenario_uid, linkedObjectType='btwin:Scenario')
    return doc


documents = []
all_scenarios = [d['uid'] for d in scenario_definitions]
for building, metadata in config.BUILDINGS.items():
    building_uid = metadata['uid']
    # Models shared by all the scenarios
    documents.append(document(ifc_path(building), f'IFC model of {building_uid}', building_uid, all_scenarios))
    documents.append(document(tbim_path(building), f'TBIM (Topologic JSON) of {building_uid}', building_uid, all_scenarios))
    # Scenario BEMs and EnergyPlus results
    for d in scenario_definitions:
        run = config.SCENARIO_RESULTS_DIR / d['uid'] / building
        documents.append(document(f'{run}.idf', f"IDF model of {building_uid} for scenario {d['label']}", building_uid, [d['uid']]))
        documents.append(document(f'{run}.csv', f"EnergyPlus results of {building_uid} for scenario {d['label']}", building_uid, [d['uid']]))
print(f'{len(scenarios)} scenarios, {len(documents)} documents')

# %% [markdown]
# ## 3. KPI sets
#
# Building KPIs of each scenario over the simulated year: utilisation and occupancy rates
# (ratios), energy need (TOE), operating cost (EUR) and CO₂ emissions (kgCO₂eq), also per m² of
# net floor area.

# %%
scenario_kpis = pd.read_csv(config.SCENARIO_RESULTS_DIR / 'scenario_kpis.csv')
KPI_COLUMNS = [
    ('kp_BuildingUtilizationRate', 'utilisation_rate_pct', 'ratio', 0.01, False),
    ('kp_BuildingOccupancyRate', 'occupancy_rate_pct', 'ratio', 0.01, False),
    ('kp_BuildingEnergyNeed', 'energy_need_TOE', 'TOE', 1, True),
    ('kp_BuildingCosts', 'cost_EUR', 'EUR', 1, True),
    ('kp_BuildingCO2Emissions', 'co2_emissions_kgCO2eq', 'kgCO2eq', 1, True),
]

kpi_sets = []
for _, row in scenario_kpis.iterrows():
    building_uid = config.BUILDINGS[row['building']]['uid']
    kpi_set = KPISet.Constructor(uid=f"{building_uid}-{row['scenario']}_OperationKPIs-WhatIf",
                                 name='Operational KPIs for the what-if analysis of the DIGITMAN project')
    for kpi_uid, column, unit, factor, per_area in KPI_COLUMNS:
        values = [(kpi_uid, unit, row[column] * factor)]
        if per_area:
            values.append((f'{kpi_uid}_mq', f'{unit}/mq', row[column] * factor / row['net_floor_area_m2']))
        for uid, kpi_unit, value in values:
            kpi = KPI.Constructor(kpiUID=uid, kpiName=uid, kpiValue=float(value), kpiUnit=kpi_unit,
                                  kpiType=None, kpiHasBeginning='2024-01-01', kpiHasEnd='2024-12-31')
            kpi_set = KPISet.SetKPI(kpiSet=kpi_set, kpi=kpi, overwrite=True)
    kpi_set['relationships']['eko:hasAssociatedObject'] = [{'@id': building_uid, '@type': 'bot:Building'}]
    kpi_set['relationships']['btwin:hasScenario'] = [{'@id': row['scenario'], '@type': 'btwin:Scenario'}]
    kpi_sets.append(kpi_set)
print(f'{len(kpi_sets)} KPI sets')

# %% [markdown]
# ## 4. JSON-LD graph

# %%
objects = [portfolio, region, site, buildings, storeys, list(spaces.values()), list(energy_zones.values()), fire_zones,
           documents, scenarios, kpi_sets]
jsonld = DataFormat.ByObjects(objects=objects, savePath=str(graph_path))
graph = KnowledgeGraph.ByJSONLDData(JSONLD=jsonld)
print(f'Knowledge graph saved to {relative(graph_path)}: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges')
Counter(type_ for _, type_ in graph.nodes(data='label'))

# %% [markdown]
# ### 4.1 Example query: energy need of each building in each scenario

# %%
rows = []
for kpi_set_node in KnowledgeGraph.SubGraphByObjectTypes(graph, objectTypes=['btwin:KPISet']):
    kpi_set = graph.nodes[kpi_set_node]
    building = KnowledgeGraph.NodeLinkedNodes(graph=graph, nodeObjectUID=kpi_set['UID'], linkedNodesType='bot:Building', relationshipName='eko:hasAssociatedObject')
    scenario = KnowledgeGraph.NodeLinkedNodes(graph=graph, nodeObjectUID=kpi_set['UID'], linkedNodesType='btwin:Scenario', relationshipName='btwin:hasScenario')
    rows.append({'building': building[0][1]['UID'], 'scenario': scenario[0][1]['UID'],
                 'energy need (TOE)': kpi_set['hasKPIs']['kp_BuildingEnergyNeed']['nominalValue']['value']})
pd.DataFrame(rows).pivot(index='scenario', columns='building', values='energy need (TOE)').round(1).loc[all_scenarios]

# %% [markdown]
# ### 4.2 Graph views (Figure 4)

# %%
figures_dir = config.KNOWLEDGE_GRAPH_DIR / 'figures'
figures_dir.mkdir(exist_ok=True)
Plot.KnowledgeGraphByMatplotlib(
    graph=KnowledgeGraph.SubGraphByObjectTypes(graph, ['bot:Site', 'bot:Building', 'brick:Energy_Zone', 'bot:Space']),
    figsize=(25, 15), nodeSize=200, nodeColorMap='viridis', showNodeLabels=True,
    savePath=str(figures_dir / 'spatial_graph.png'))
Plot.KnowledgeGraphByMatplotlib(
    graph=KnowledgeGraph.SubGraphByObjectTypes(graph, ['bot:Building', 'btwin:Document', 'btwin:Scenario', 'btwin:KPISet']),
    figsize=(15, 10), nodeColorMap='plasma', edgeColorMap='jet', showNodeLabels=False, nodeSize=300, edgeWidth=1,
    savePath=str(figures_dir / 'energy_scenario_graph.png'))

# %% [markdown]
# ## 5. Neo4j (optional)

# %%
# Asked interactively unless given on the command line (--neo4j yes|no)
write_to_neo4j = config.cli_option('neo4j', None)
if write_to_neo4j is None:
    try:
        write_to_neo4j = 'yes' if input('Write the knowledge graph to Neo4j? [y/N] ').strip().lower() in ('y', 'yes') else 'no'
    except EOFError:  # non-interactive run
        write_to_neo4j = 'no'
if write_to_neo4j == 'yes':
    KnowledgeGraph.ToNEO4J(btwinGraph=graph)  # URI, username and password are asked at run time
else:
    print('The knowledge graph is not written to Neo4j')
