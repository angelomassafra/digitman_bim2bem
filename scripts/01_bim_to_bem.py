# ---
# jupyter:
#   jupytext:
#     formats: notebooks//ipynb,scripts//py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.6
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 01 · BIM-to-BEM conversion
#
# Converts the Topological BIM (TBIM) of a case-study building into an EnergyPlus Building
# Energy Model (BEM), following the steps of **Section 3.2.2** of the paper:
#
# 1. thermal zoning and geometry (TBIM cells → K-Means clusters → Honeybee rooms);
# 2. boundary conditions (outdoor, ground, adiabatic);
# 3. construction characteristics and openings (from the IFC material layer sets and window types);
# 4. external shading elements (BRep → Honeybee shades);
# 5. simulation parameters, infiltration, schedules, operational data and weather (via Eppy).
#
# **Inputs** (`data/<building>/`): TBIM in Topologic JSON and IFC format, IFC reference view with the
# material properties, BRep shading geometry, BIM-to-BEM settings; schedules (`data/schedules/`);
# design days (`data/weather/`).
#
# **Outputs** (`results/bem/`): TBIM with thermal zones (`<building>_tbim_topologic_with_zones.json`),
# baseline BEM (`<building>_bem_baseline.idf`) and, optionally, its annual simulation.
#
# Run as a script with `python scripts/01_bim_to_bem.py --building building09`.

# %% [markdown]
# ## 0. Set-up

# %%
import json
import sys
from pathlib import Path

# Repository root (works from the repository, scripts/ or notebooks/ folder)
HERE = Path(__file__).resolve().parent if '__file__' in globals() else Path.cwd()
ROOT = next(p for p in (HERE, *HERE.parents) if (p / 'config.py').exists())
sys.path.insert(0, str(ROOT))
import config

import ifcopenshell
import ifcopenshell.util.element
import pandas as pd
import honeybee_energy
from honeybee.room import Room as HBRoom
from honeybee.model import Model as HBModel
from honeybee_energy.construction.opaque import OpaqueConstruction
from eppy.modeleditor import IDF
from topologicpy.Cell import Cell
from topologicpy.CellComplex import CellComplex
from topologicpy.Dictionary import Dictionary
from topologicpy.Face import Face
from topologicpy.Topology import Topology
from topologicpy.Vertex import Vertex

from digitmanpy.Operation import Utils, HB, Eppy, TBIM
from digitmanpy.Visualize import Show
from btwinpy.IFC import IFC

# %% [markdown]
# ### 0.1 Case-study building and settings

# %%
# Building to convert: 'building09' or 'building10'
BUILDING = config.cli_option('building', 'building10')
# Run the annual EnergyPlus simulation of the baseline BEM at the end of the conversion
RUN_SIMULATION = config.cli_option('simulate', 'yes') == 'yes'

building = config.BUILDINGS[BUILDING]
settings = json.loads(config.building_file(BUILDING, 'bim2bem_settings.json').read_text())

# Input models
tbim_path = config.building_file(BUILDING, 'tbim_topologic.json')
ifc_path = config.building_file(BUILDING, 'tbim_ifc_design_transfer_view.ifc')
ifc_materials_path = config.building_file(BUILDING, 'tbim_ifc_reference_view.ifc')
shading_brep_paths = [config.building_file(BUILDING, f'shades_{name}.brep')
                      for name in ('balconies', 'context_buildings', 'adjacent_buildings')]

# Schedules modelled with the Honeybee API (Schedule Ruleset JSON)
schedule_paths = {use: config.SCHEDULES_DIR / f'Schedules_{use}_PoliMi_LC.json'
                  for use in ('Occupancy', 'Equipment', 'Lighting', 'Heating', 'Cooling', 'Ventilation')}

# Outputs
config.BEM_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
tbim_with_zones_path = config.BEM_RESULTS_DIR / f'{BUILDING}_tbim_topologic_with_zones.json'
bem_path = config.BEM_RESULTS_DIR / f'{BUILDING}_bem_baseline.idf'
figures_dir = config.BEM_RESULTS_DIR / 'figures'

print(f"{building['name']} ({building['uid']})")

# %% [markdown]
# ### 0.2 Model inputs not stored in the TBIM
#
# Infiltration flow rate per exterior surface area, from the airtightness classes of the
# Honeybee "Set EnergyPlus Zone Loads" component (m³/s·m²).

# %%
INFILTRATION_FLOW_RATES = {
    'PassiveHouse': 0.000071,
    'TightBuilding': 0.000100,
    'AverageBuilding': 0.000300,
    'LeakyBuilding': 0.000600,
}
infiltration_flow_rate = INFILTRATION_FLOW_RATES[settings['infiltration']['building_airtightness']]

adiabatic_face_uids = settings['boundary_conditions']['adiabatic_face_uids']
ground_face_uids = settings['boundary_conditions']['ground_face_uids']

# %% [markdown]
# ## 1. TBIM pre-processing

# %% [markdown]
# ### 1.1 Import the TBIM

# %%
tp_building = Topology.ByJSONPath(path=str(tbim_path))[0]
print(f'TBIM imported: {len(CellComplex.Cells(tp_building))} cells')

# %% [markdown]
# ### 1.2 Schedules of the spaces
#
# The schedules of each space are assigned in the TBIM authoring environment and exported as
# IfcSpace properties (`rl_IsScheduledBy_<use>`); they are copied to the matching Topologic cells.
# Spaces without a schedule are assigned an always-off (or unoccupied) schedule.

# %%
DEFAULT_SCHEDULES = {
    'rl_IsScheduledBy_Cooling': 'AlwaysOff',
    'rl_IsScheduledBy_Heating': 'AlwaysOff',
    'rl_IsScheduledBy_Lighting': 'AlwaysOff',
    'rl_IsScheduledBy_Occupancy': 'OccSch_Unoccupied',
    'rl_IsScheduledBy_Ventilation': 'AlwaysOff',
    'rl_IsScheduledBy_Equipment': 'AlwaysOff',
}

ifc_spaces = {IFC.IfcSpaceGetPropertyValue(ifcSpace=space, propertyName='UID'): space
              for space in ifcopenshell.open(str(ifc_path)).by_type('IfcSpace')}

for tp_cell in CellComplex.Cells(tp_building):
    cell_dictionary = Topology.Dictionary(tp_cell)
    ifc_space = ifc_spaces.get(Dictionary.ValueAtKey(cell_dictionary, 'UID'))
    if ifc_space is None:
        continue
    schedules = {}
    for key, default in DEFAULT_SCHEDULES.items():
        value = IFC.IfcSpaceGetPropertyValue(ifcSpace=ifc_space, propertyName=key)
        if value is None:
            value = default
        elif ';' in value:
            # lighting and equipment may list several schedules: the first one is used
            value = value.split(';')[0]
        schedules[key] = value
    merged = Dictionary.ByMergedDictionaries([cell_dictionary, Dictionary.ByKeysValues(list(schedules), list(schedules.values()))])
    Topology.SetDictionary(tp_cell, merged)

# %% [markdown]
# ### 1.3 Default values of missing space properties
#
# Applied to Building 09 only (`fill_missing_space_properties` in the settings). In Building 10
# the undefined occupant densities are left undefined and are imputed with the mean density
# by the clustering step (Section 2), as done for the models of the paper.

# %%
DEFAULT_SPACE_PROPERTIES = {
    'pr_IsOccupied': 0,
    'pr_IsHeated': 0,
    'pr_IsCooled': 0,
    'pr_OccupancyDensityOperation': 0,
    'pr_OccupancyDensitySafety': 0,
    'pr_OccupancyType': 'StorageSpaces:GeneralStorageSpace',
    'rl_HasLocation_tpBS': 'noneStorey',
    'pr_SpaceTemperatureSummerMax': 26,
    'pr_SpaceTemperatureSummerMin': 23,
    'pr_SpaceTemperatureWinterMax': 23.5,
    'pr_SpaceTemperatureWinterMin': 18,
    'pr_EquipmentPowerDensity': 0,
    'pr_LightingPowerDensity': 0,
    'pr_MechanicalVentilationRate': 0.0,
    'pr_MechanicalVentilationRatePerPerson': 0,
    'pr_MechanicalVentilationRatePerVolume': 0.0,
}

if settings['thermal_zoning']['fill_missing_space_properties']:
    for tp_cell in CellComplex.Cells(tp_building):
        cell_dictionary = Topology.Dictionary(tp_cell)
        for key, default in DEFAULT_SPACE_PROPERTIES.items():
            value = Dictionary.ValueAtKey(cell_dictionary, key)
            if value == 'Undefined' or value is None:
                cell_dictionary = Dictionary.SetValueAtKey(cell_dictionary, key, default)
        Topology.SetDictionary(tp_cell, cell_dictionary)

# %% [markdown]
# ### 1.4 Topological type of the faces
#
# Each face is labelled by its position in the cell complex (external/internal,
# vertical/horizontal); the label drives the Honeybee face type and the construction assignment.

# %%
TOPOLOGICAL_TYPES = {
    'bottomHorizontalFaces': 'botHor',
    'internalHorizontalFaces': 'intHor',
    'topHorizontalFaces': 'topHor',
    'internalVerticalFaces': 'intVer',
    'externalVerticalFaces': 'extVer',
}

faces_by_position = CellComplex.Decompose(tp_building)
for position, topological_type in TOPOLOGICAL_TYPES.items():
    for tp_face in faces_by_position[position]:
        face_dictionary = Topology.Dictionary(tp_face)
        if Dictionary.ValueAtKey(face_dictionary, 'pr_TopologicalType') is None:
            Topology.SetDictionary(tp_face, Dictionary.SetValueAtKey(face_dictionary, 'pr_TopologicalType', topological_type))

# %% [markdown]
# ## 2. Thermal zoning
#
# Cells are clustered with K-Means on their occupancy and conditioning attributes; clusters are
# then split by storey and adjacency, and some space types are merged (stairways and elevators
# with corridors) or kept as single-space zones (lecture halls, laboratories, storage).

# %%
zoning = settings['thermal_zoning']
tp_building = TBIM.Cells_ClusterizeIntoEnergyZones(
    n_clusters=zoning['n_clusters'],
    tpBuilding=tp_building,
    kmeansPropertyNames=zoning['kmeans_property_names'],
    singleZoneOccupancyTypes=zoning['single_zone_occupancy_types'],
    notUsefullCellUIDs=zoning['excluded_cell_uids'],
)

# Building 09: cells left without a zone are modelled as separate zones (debugZone<i>)
if zoning['unzoned_cells_as_separate_zones']:
    i = 0
    for tp_cell in CellComplex.Cells(tp_building):
        cell_dictionary = Topology.Dictionary(tp_cell)
        if Dictionary.ValueAtKey(cell_dictionary, 'rl_HasLocation_tpZN') is None:
            Topology.SetDictionary(tp_cell, Dictionary.SetValueAtKey(cell_dictionary, 'rl_HasLocation_tpZN', f'debugZone{i}'))
            i += 1

Topology.ExportToJSON(tp_building, str(tbim_with_zones_path), overwrite=True)

# Remaining undefined properties are set to neutral values
tp_building = TBIM.Cells_CleanUndefinedData(tpBuilding=tp_building)

zone_uids = {Dictionary.ValueAtKey(Topology.Dictionary(c), 'rl_HasLocation_tpZN') for c in CellComplex.Cells(tp_building)}
print(f'{len(zone_uids - {None})} thermal zones; TBIM with zones saved to {tbim_with_zones_path.name}')

# %%
config.show_figure(Show.TBIM_EnergyZones(tpBuilding=tp_building, colorScale='jet'), f'{BUILDING}_thermal_zones', figures_dir)

# %% [markdown]
# ## 3. Constructions

# %% [markdown]
# ### 3.1 Opaque constructions
#
# Material layers (thickness, conductivity, density, specific heat) are read from the
# IfcMaterialLayerSets of the IfcWall and IfcSlab types and converted into Honeybee
# EnergyMaterial / OpaqueConstruction objects.

# %%
hb_opaque_constructions = HB.HBOpaqueConstructionsByIFCPaths(ifcFilePath=str(ifc_path), ifcMaterialPath=str(ifc_materials_path))[0]

# The roof stratigraphy is not described in the IFC material file and is defined explicitly
# (layers from outside to inside)
ROOF_LAYERS = [
    # identifier, thickness (m), conductivity (W/m·K), density (kg/m³), specific heat (J/kg·K)
    ('dtu_MT_POLIMI_Ghiaia', 0.08, 1.2, 1700, 1000),
    ('dtu_MT_POLIMI_Massetto', 0.12, 1.2, 1700, 1000),
    ('dtu_MT_POLIMI_Isolante rigido', 0.08, 0.04, 30, 1452),
    ('dtu_MT_POLIMI_CLS', 0.25, 1.046, 2300, 657),
]
roof_construction = OpaqueConstruction.from_dict({
    'type': 'OpaqueConstruction',
    'identifier': 'RF_POLIMI-LC_IH-E',
    'display_name': 'RF_POLIMI-LC_IH-E',
    'materials': [{'type': 'EnergyMaterial', 'identifier': f'{name}-{thickness}', 'display_name': name,
                   'roughness': 'MediumRough', 'thickness': thickness, 'conductivity': conductivity,
                   'density': density, 'specific_heat': specific_heat, 'thermal_absorptance': 0.95,
                   'solar_absorptance': 0.7, 'visible_absorptance': 0.7}
                  for name, thickness, conductivity, density, specific_heat in ROOF_LAYERS],
})
hb_opaque_constructions.append(roof_construction)
hb_opaque_construction_names = HB.HBConstructionNamesByhbConstructions(hbOpaqueConstructions=hb_opaque_constructions)
print('Opaque constructions:', hb_opaque_construction_names)

# %% [markdown]
# ### 3.2 Glazed constructions
#
# Thermal transmittance, solar heat gain coefficient and visible transmittance of the
# IfcWindow/IfcDoor types and of the curtain walls → Honeybee WindowConstruction objects.

# %%
hb_window_constructions = HB.HBWindowConstructionsByIFC(ifcFilePath=str(ifc_path), thermalPSets='btwin')
hb_window_construction_names = HB.HBConstructionNamesByhbConstructions(hbOpaqueConstructions=hb_window_constructions)
print('Window constructions:', hb_window_construction_names)

# Construction name of each TBIM face (from its wall, floor or roof type)
tp_building = TBIM.Faces_SetHBConstructionName(tpBuilding=tp_building)

# %% [markdown]
# ## 4. Schedules
#
# Schedule Rulesets (Honeybee JSON) for occupancy (from the university booking service),
# equipment, lighting and the availability of heating, cooling and ventilation.

# %%
schedule_type_limits = HB.DefaultScheduleTypeLimits()

occupancy_schedules = HB.HBOccupancyScheduleRulesetDictsByJSONPath(occupancySchedulePath=schedule_paths['Occupancy'])
equipment_schedules = HB.HBEquipmentScheduleRulesetDictsByJSONPath(equipmentSchedulePath=schedule_paths['Equipment'])
lighting_schedules = HB.HBLightingScheduleRulesetDictsByJSONPath(lightingSchedulePath=schedule_paths['Lighting'])
heating_schedules = HB.HBSystemAvailabilityScheduleRulesetDictsByJSONPath(systemAvailabilitySchedulePath=schedule_paths['Heating'], prefix='HtnSch_')
cooling_schedules = HB.HBSystemAvailabilityScheduleRulesetDictsByJSONPath(systemAvailabilitySchedulePath=schedule_paths['Cooling'], prefix='ClnSch_')
ventilation_schedules = HB.HBSystemAvailabilityScheduleRulesetDictsByJSONPath(systemAvailabilitySchedulePath=schedule_paths['Ventilation'], prefix='VntSch_')

# Equipment schedule referenced by the TBIM but missing in the JSON library: created as a copy
# of the unoccupied schedule (it is redefined during the calibration, see 02_bem_calibration)
for schedule in list(equipment_schedules):
    if schedule['identifier'] == 'EqpSch_Unoccupied':
        equipment_schedules.append({**schedule, 'identifier': 'EqpSch_Costant'})

all_schedules = occupancy_schedules + equipment_schedules + lighting_schedules + heating_schedules + cooling_schedules + ventilation_schedules
print(f'{len(all_schedules)} schedule rulesets imported')

# %% [markdown]
# ## 5. Energy model

# %% [markdown]
# ### 5.1 Thermal zones and inherited space data
#
# Cells of the same zone are merged into a cell complex; zone properties are aggregated from
# the spaces (area-weighted densities, volume-weighted ventilation rates, prevailing occupancy
# type and schedules of the most occupied space).

# %%
tp_zones = TBIM.EnergyZones(tp_building)
tp_building = TBIM.Faces_SetZoneRelationships(tpBuilding=tp_building, tpZones=tp_zones)
tp_zones = Utils.TopologicZoneInheritSpaceData(tp_zones)

# %% [markdown]
# ### 5.2 Zoning and geometry: Honeybee rooms
#
# Topologic faces → Honeybee faces, Topologic apertures (and curtain walls) → Honeybee apertures;
# adjacencies between rooms are solved to set the interzone boundary conditions.

# %%
hb_rooms = []
for tp_zone in tp_zones:
    zone_dictionary = Topology.Dictionary(tp_zone)
    zone_uid = Dictionary.ValueAtKey(zone_dictionary, 'UID')
    hb_faces = HB.HBFacesByTopologicZone(tpZone=tp_zone, tpBuilding=tp_building, adiabaticFaceUIDs=adiabatic_face_uids)
    hb_room = HBRoom(zone_uid, hb_faces, 0.01, 1)
    hb_room.story = Dictionary.ValueAtKey(zone_dictionary, 'rl_HasLocation_tpBS')
    # Default program, ideal loads air system and setpoints (refined in the IDF below)
    hb_rooms.append(HB.HBRoomSetSetpointSchedules(hb_room))
HBRoom.solve_adjacency(hb_rooms, 0.01)
print(f'{len(hb_rooms)} Honeybee rooms')

# %% [markdown]
# ### 5.3 External shading elements
#
# Balconies, surrounding and adjacent buildings, modelled as BRep and linked as Honeybee shades.

# %%
hb_shades = HB.HBShadesByTopologicBRepPaths(shadingFacesPaths=[str(p) for p in shading_brep_paths], tbimUnits='cm')
hb_model = HBModel(identifier=building['idf_name'], rooms=hb_rooms, orphaned_shades=hb_shades)
print(f'{len(hb_shades)} shading faces')

# %% [markdown]
# ### 5.4 Honeybee model → IDF
#
# Default simulation parameters and design days, then export to IDF (EnergyPlus 24.1); from this
# point on the model is edited with Eppy.

# %%
simulation_parameter = HB.HBDefaultSimulationParameter()
simulation_parameter.sizing_parameter.add_from_ddy_996_004(str(config.DDY_PATH))
idf_string = '\n\n'.join((honeybee_energy.writer.energyplus_idf_version(version_array=[24, 1, 0]),
                          simulation_parameter.to_idf(),
                          hb_model.to.idf(hb_model)))
honeybee_idf_path = config.BEM_RESULTS_DIR / f"{building['idf_name']}.idf"
honeybee_idf_path.write_text(idf_string)

IDF.setiddname(str(config.IDD_V24_1))
idf = IDF(str(honeybee_idf_path))

idf_building = idf.idfobjects['BUILDING'][0]
idf_building.Name = building['idf_name']
idf_building.North_Axis = settings['energyplus']['north_axis_deg']   # degrees clockwise from true North
idf_building.Terrain = settings['energyplus']['terrain']

# %% [markdown]
# ### 5.5 Schedules
#
# Schedule Rulesets → Schedule:Compact objects.

# %%
idf = Eppy.IdfSetScheduleTypeLimits(idfFile=idf, scheduleTypeLimits=schedule_type_limits)
for schedule in all_schedules:
    idf = Eppy.IdfScheduleCompactByHBScheduleRulesetDict(schedule, idf)

always_off = idf.newidfobject('SCHEDULE:COMPACT')
always_off.Name = 'AlwaysOff'
always_off.Schedule_Type_Limits_Name = 'availabilityScheduleTypeLimit'
always_off.Field_1, always_off.Field_2, always_off.Field_3, always_off.Field_4 = 'Through: 12/31', 'For: AllDays', 'Until: 24:00', 0

# %% [markdown]
# ### 5.6 Operational data
#
# Zone by zone: occupant density and schedule (People), lighting and equipment power density
# and schedule (Lights, ElectricEquipment), humidity setpoints and availability schedules of the
# ideal loads air system, outdoor-air flow rates per person and per floor area.

# %%
def zone_value(zone_dictionary, key, default):
    value = Dictionary.ValueAtKey(zone_dictionary, key)
    return default if value is None else value


def clean_outdoor_air_name(name):
    return name.replace('Generic Office Ventilation', 'outdoorAir').replace('.. ', '_')


zones = {Dictionary.ValueAtKey(Topology.Dictionary(z), 'UID'): Topology.Dictionary(z) for z in tp_zones}
for zone_uid, d in zones.items():
    for people in idf.idfobjects['PEOPLE']:
        if people.Zone_or_ZoneList_or_Space_or_SpaceList_Name == zone_uid:
            people.People_per_Floor_Area = Dictionary.ValueAtKey(d, 'pr_OccupancyDensityOperation')
            people.Number_of_People_Schedule_Name = zone_value(d, 'rl_IsScheduledBy_Occupancy', 'OccSch_Unoccupied')
    for lights in idf.idfobjects['LIGHTS']:
        if lights.Zone_or_ZoneList_or_Space_or_SpaceList_Name == zone_uid:
            lights.Watts_per_Floor_Area = zone_value(d, 'pr_LightingPowerDensity', 0)
            lights.Schedule_Name = zone_value(d, 'rl_IsScheduledBy_Lighting', 'LghSch_Unoccupied')
            lights.Lighting_Level = 300
    for equipment in idf.idfobjects['ELECTRICEQUIPMENT']:
        if equipment.Zone_or_ZoneList_or_Space_or_SpaceList_Name == zone_uid:
            equipment.Watts_per_Floor_Area = zone_value(d, 'pr_EquipmentPowerDensity', 0)
            equipment.Schedule_Name = zone_value(d, 'rl_IsScheduledBy_Equipment', 'EqpSch_Unoccupied')
    for ideal_loads in idf.idfobjects['HVACTEMPLATE:ZONE:IDEALLOADSAIRSYSTEM']:
        if ideal_loads.Zone_Name == zone_uid:
            ideal_loads.Dehumidification_Setpoint = Dictionary.ValueAtKey(d, 'pr_HumidityMax')
            ideal_loads.Humidification_Setpoint = Dictionary.ValueAtKey(d, 'pr_HumidityMin')
            ideal_loads.Design_Specification_Outdoor_Air_Object_Name = clean_outdoor_air_name(ideal_loads.Design_Specification_Outdoor_Air_Object_Name)
            ideal_loads.System_Availability_Schedule_Name = zone_value(d, 'rl_IsScheduledBy_Ventilation', 'AlwaysOff')
            ideal_loads.Heating_Availability_Schedule_Name = zone_value(d, 'rl_IsScheduledBy_Heating', 'AlwaysOff')
            ideal_loads.Cooling_Availability_Schedule_Name = zone_value(d, 'rl_IsScheduledBy_Cooling', 'AlwaysOff')
    for outdoor_air in idf.idfobjects['DESIGNSPECIFICATION:OUTDOORAIR']:
        if zone_uid in outdoor_air.Name:
            # TBIM rates in L/s per person and L/s·m² → m³/s
            outdoor_air.Outdoor_Air_Method = 'Maximum'
            outdoor_air.Outdoor_Air_Flow_per_Person = zone_value(d, 'pr_MechanicalVentilationRatePerPerson', 0) / 1000
            outdoor_air.Outdoor_Air_Flow_per_Zone_Floor_Area = zone_value(d, 'pr_MechanicalVentilationRate', 0) / 1000
            outdoor_air.Name = clean_outdoor_air_name(outdoor_air.Name)

# %% [markdown]
# ### 5.7 Infiltration and constructions

# %%
for infiltration in idf.idfobjects['ZONEINFILTRATION:DESIGNFLOWRATE']:
    infiltration.Name = infiltration.Name.replace('Generic Office ', 'Zone').replace('..', '_')
    infiltration.Flow_Rate_per_Exterior_Surface_Area = infiltration_flow_rate

idf = Eppy.IdfSetFaceConstructions(idfFile=idf, tpBuilding=tp_building, hbOpaqueConstructionNames=hb_opaque_construction_names)
# Surfaces without a construction in the TBIM keep the default construction of the building
for surface in idf.idfobjects['BUILDINGSURFACE:DETAILED']:
    if surface.Construction_Name == 'Generic Exterior Wall':
        surface.Construction_Name = settings['energyplus']['default_wall_construction']
    elif surface.Construction_Name == 'Generic Roof':
        surface.Construction_Name = settings['energyplus']['default_roof_construction']

idf = Eppy.IdfSetWindowConstructions(idfFile=idf, tpBuilding=tp_building, hbWindowConstructionNames=hb_window_construction_names)
idf = Eppy.IdfSetCurtainWallConstructions(idfFile=idf, tpBuilding=tp_building, hbWindowConstructionNames=hb_window_construction_names)
idf = Eppy.IdfSetConstructionsAndMaterials(idfFile=idf, hbOpaqueConstructions=hb_opaque_constructions, hbWindowConstructions=hb_window_constructions)
idf = Eppy.IdfPurgeUnusedConstruction(idf)

# %% [markdown]
# ### 5.8 External blinds
#
# Fixed horizontal aluminium blinds (always on) on the glazed surfaces listed in the settings;
# the solar distribution is set to FullExterior for compatibility with the blind model.

# %%
idf.idfobjects['BUILDING'][0].Solar_Distribution = 'FullExterior'

BLIND_PROPERTIES = {
    'Slat_Width': 0.30, 'Blind_to_Glass_Distance': 0.30, 'Slat_Separation': 0.50, 'Slat_Thickness': 0.001,  # m
    'Slat_Angle': 90.0, 'Slat_Conductivity': 160,                                                           # deg, W/m·K
    'Slat_Beam_Solar_Transmittance': 0, 'Front_Side_Slat_Beam_Solar_Reflectance': 0.6, 'Back_Side_Slat_Beam_Solar_Reflectance': 0.6,
    'Slat_Diffuse_Solar_Transmittance': 0, 'Front_Side_Slat_Diffuse_Solar_Reflectance': 0.6, 'Back_Side_Slat_Diffuse_Solar_Reflectance': 0.6,
    'Slat_Beam_Visible_Transmittance': 0, 'Front_Side_Slat_Beam_Visible_Reflectance': 0.5, 'Back_Side_Slat_Beam_Visible_Reflectance': 0.5,
    'Slat_Diffuse_Visible_Transmittance': 0, 'Front_Side_Slat_Diffuse_Visible_Reflectance': 0.5, 'Back_Side_Slat_Diffuse_Visible_Reflectance': 0.5,
    'Slat_Infrared_Hemispherical_Transmittance': 0, 'Front_Side_Slat_Infrared_Hemispherical_Emissivity': 0.9, 'Back_Side_Slat_Infrared_Hemispherical_Emissivity': 0.9,
    'Blind_Top_Opening_Multiplier': 0, 'Blind_Bottom_Opening_Multiplier': 0,
    'Blind_Left_Side_Opening_Multiplier': 0.5, 'Blind_Right_Side_Opening_Multiplier': 0.5,
    'Minimum_Slat_Angle': 85, 'Maximum_Slat_Angle': 95,
}

constructions = {c.Name: c for c in idf.idfobjects['CONSTRUCTION']}
for fenestration in idf.idfobjects['FENESTRATIONSURFACE:DETAILED']:
    if fenestration.Name not in settings['fenestration_with_external_blinds']:
        continue
    blind = idf.newidfobject('WINDOWMATERIAL:BLIND', Name=f'externalAluminiumBlind-{fenestration.Name}', **BLIND_PROPERTIES)
    shading_control = idf.newidfobject('WINDOWSHADINGCONTROL')
    shading_control.Name = f'myShadingControl-{fenestration.Name}'
    shading_control.Zone_Name = fenestration.Building_Surface_Name.split('-')[1]
    shading_control.Shading_Control_Sequence_Number = 1
    shading_control.Shading_Type = 'ExteriorBlind'
    shading_control.Shading_Control_Type = 'AlwaysOn'
    shading_control.Shading_Control_Is_Scheduled = 'NO'
    shading_control.Glare_Control_Is_Active = 'NO'
    shading_control.Type_of_Slat_Angle_Control_for_Blinds = 'FixedSlatAngle'
    shading_control.Fenestration_Surface_1_Name = fenestration.Name
    # Construction with the blind outside the glazing
    shaded_construction = idf.newidfobject('CONSTRUCTION')
    shaded_construction.Name = f'{fenestration.Construction_Name}-withBlinds-{fenestration.Name}'
    shaded_construction.Outside_Layer = blind.Name
    shaded_construction.Layer_2 = constructions[fenestration.Construction_Name].Outside_Layer
    shading_control.Construction_with_Shading_Name = shaded_construction.Name

# %% [markdown]
# ### 5.9 Boundary conditions
#
# Outdoor and interzone conditions are computed by Honeybee from the room adjacencies; faces
# adjacent to other buildings are set to adiabatic and underground faces to ground.

# %%
for surface in idf.idfobjects['BUILDINGSURFACE:DETAILED']:
    face_uid = surface.Name.split('-')[0]
    if face_uid in adiabatic_face_uids:
        surface.Outside_Boundary_Condition = 'Adiabatic'
    elif face_uid in ground_face_uids:
        surface.Outside_Boundary_Condition = 'Ground'

# %% [markdown]
# ### 5.10 Output variables

# %%
OUTPUT_VARIABLES = Eppy.DigitManOutputVariables() + [
    'Zone Mean Air Temperature', 'Zone Air Temperature', 'Zone Mean Radiant Temperature', 'Zone Operative Temperature']
idf = Eppy.IdfSetOutputVariables(idf, OUTPUT_VARIABLES, 'Hourly')

# %% [markdown]
# ### 5.11 Geometry fixes
#
# Duplicate surface names are made unique and, in Building 10, a curtain wall missing in the TBIM
# is added by copying a curtain wall of the floor above.

# %%
surface_names = [s.Name for s in idf.idfobjects['BUILDINGSURFACE:DETAILED']]
duplicates = {name for name in surface_names if surface_names.count(name) > 1}
counters = dict.fromkeys(duplicates, 0)
for surface in idf.idfobjects['BUILDINGSURFACE:DETAILED']:
    if surface.Name in duplicates:
        name = surface.Name
        surface.Name = f'{name}-{counters[name]}'
        counters[name] += 1

fenestrations = {f.Name: f for f in idf.idfobjects['FENESTRATIONSURFACE:DETAILED']}
for missing in settings['missing_curtain_walls']:
    reference = fenestrations[missing['copy_of']]
    curtain_wall = idf.newidfobject('FENESTRATIONSURFACE:DETAILED')
    curtain_wall.Name = missing['name']
    curtain_wall.Surface_Type = reference.Surface_Type
    curtain_wall.Construction_Name = reference.Construction_Name
    curtain_wall.Building_Surface_Name = missing['host_surface']
    curtain_wall.View_Factor_to_Ground = reference.View_Factor_to_Ground
    curtain_wall.Number_of_Vertices = 4
    for i in range(1, 5):
        curtain_wall[f'Vertex_{i}_Xcoordinate'] = reference[f'Vertex_{i}_Xcoordinate']
        curtain_wall[f'Vertex_{i}_Ycoordinate'] = reference[f'Vertex_{i}_Ycoordinate']
        curtain_wall[f'Vertex_{i}_Zcoordinate'] = round(reference[f'Vertex_{i}_Zcoordinate'] + missing['z_offset_m'], 3)

idf.saveas(str(bem_path))
print(f'Baseline BEM saved to {bem_path}')

# %% [markdown]
# ## 6. Annual simulation of the baseline BEM
#
# The 24.1 model is converted to EnergyPlus 24.2 and simulated with the on-site weather file
# (1 January – 31 December 2024).

# %%
if RUN_SIMULATION:
    simulation_dir = config.BEM_RESULTS_DIR / 'simulation'
    simulation_dir.mkdir(exist_ok=True)
    simulation_idf_path = simulation_dir / f'{BUILDING}_bem_baseline.idf'
    idf.saveas(str(simulation_idf_path))
    Eppy.IdfTransitionVersion(idfFilePath=str(simulation_idf_path), transitionExePath=str(config.TRANSITION_V24_1_TO_V24_2))
    ok =Eppy.EnergyPlus_RunSimulation(idfFilePath=str(simulation_idf_path), epwFilePath=str(config.EPW_PATH),
                                       energyPlusExePath=str(config.ENERGYPLUS_EXE))
    print('Simulation completed' if ok else 'Simulation FAILED: see the .err file')

# %% [markdown]
# ### 6.1 Summary of the results
#
# Annual energy needs normalised by the gross floor area of the TBIM cells.

# %%
if RUN_SIMULATION:
    ep_csv_path = simulation_dir / f'{BUILDING}_bem_baseline.csv'
    results = pd.read_csv(ep_csv_path)

    gross_floor_area = sum(Face.Area(f) / 1e4                       # cm² → m²
                           for c in CellComplex.Cells(tp_building) for f in Cell.Faces(c)
                           if Vertex.Z(Topology.Centroid(f)) < Vertex.Z(Topology.Centroid(c)) and Face.Normal(f)[2] != 0)
    print(f'Gross floor area: {gross_floor_area:.2f} m²')
    for variable in Eppy.DigitManOutputVariables()[:4]:
        annual_kwh = results.filter(like=variable).sum().sum() * 2.77778e-7
        print(f'{variable}: {annual_kwh / gross_floor_area:.2f} kWh/m²')

# %%
if RUN_SIMULATION:
    figure = Show.TBIM_ByEnergyPlusCSV(epCSVPath=str(ep_csv_path), outputVariable='Zone Ideal Loads Zone Total Heating Energy',
                                       tpBuilding=tp_building, colorScale='haline', normalizeArea=False)
    config.show_figure(figure, f'{BUILDING}_baseline_heating_by_zone', figures_dir)
