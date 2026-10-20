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
# # 04 · What-if scenario modelling
#
# Builds the EnergyPlus models of the twelve occupancy-management scenarios (**Section 3.3.2**)
# for both buildings, by editing the tuned BEM with Eppy. Four types of modification are combined:
#
# | Category | IDF edit |
# |---|---|
# | Space capacity (S3, S4) | `People per Floor Area` of the classroom People objects |
# | Occupancy schedules (S5–S8) | occupied hours of the classroom booking schedules set to a fixed occupancy rate |
# | Space repurposing (S9–S11) | People density, schedule and equipment density of a closed office |
# | Demand-driven ventilation (S1, S2, S10, S11) | `DesignSpecification:OutdoorAir` method and schedule |
#
# Classrooms are identified in the IDF as the zones whose People object follows a booking
# schedule of the university booking service (`OccSch_<room>`).
#
# **Input**: tuned BEM (`models/<building>_bem_calibrated.idf`, or the model produced by
# `02_bem_calibration` with `--calibrated results`).
#
# **Outputs** (`results/scenarios/scenario<N>/<building>.idf`): scenario models for EnergyPlus 24.2.

# %% [markdown]
# ## 0. Set-up

# %%
import copy
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent if '__file__' in globals() else Path.cwd()
ROOT = next(p for p in (HERE, *HERE.parents) if (p / 'config.py').exists())
sys.path.insert(0, str(ROOT))
import config

from eppy.modeleditor import IDF

from digitmanpy.Operation import Eppy, Scenario

# %%
# Tuned BEM: 'archived' (models/, used in the paper) or 'results' (results/calibration/, from 02_bem_calibration)
CALIBRATED = config.cli_option('calibrated', 'archived')

scenario_definitions = json.loads((config.SCENARIO_DATA_DIR / 'scenario_definitions.json').read_text())['scenarios']
models_dir = config.SCENARIO_RESULTS_DIR / '_baseline'
models_dir.mkdir(parents=True, exist_ok=True)

# %% [markdown]
# ### 0.1 Scenario parameters

# %%
CLASSROOM_EQUIPMENT_DENSITY = 5.4     # W/m², ASHRAE 90.1 classroom
OFFICE_PEOPLE_DENSITY = 0.12          # people/m², closed office
OFFICE_EQUIPMENT_DENSITY = 8.1        # W/m², ASHRAE 90.1 office
OFFICE_SCHEDULE = 'Generic Office Occupancy'
VAV_MINIMUM_FRACTION = 0.214          # 0.15 L/s·m² (unoccupied) / 0.7 L/s·m² (occupied)
BUILDING09_COOLING_SETPOINT = 22      # °C, cooling setpoint of Building 09 in the scenario baseline

# %% [markdown]
# ## 1. Scenario baseline (Scenario 0)
#
# The tuned BEM is converted to EnergyPlus 24.2 and harmonised for the scenario comparison:
# classroom equipment density of 5.4 W/m², outdoor air per floor area (CAV controlled by volume
# flow), equipment schedule `EqpSch_Costant` active from 07:00 to 18:00, cooling setpoint of
# Building 09 at 22 °C, run period 2024.

# %%
def set_constant_equipment_schedule(idf):
    for schedule in idf.idfobjects['SCHEDULE:COMPACT']:
        if schedule.Name == 'EqpSch_Costant':
            schedule.obj = schedule.obj[:3] + ['Through: 12/31', 'For: AllDays', 'Until: 07:00', 0, 'Until: 18:00', 1, 'Until: 24:00', 0]


def set_cooling_setpoint(idf, setpoint):
    for schedule in idf.idfobjects['SCHEDULE:COMPACT']:
        if schedule.Name == 'Generic room Cooling':
            schedule.Field_4 = schedule.Field_6 = schedule.Field_8 = setpoint


def scenario_baseline(building):
    source = (config.MODELS_DIR if CALIBRATED == 'archived' else config.CALIBRATION_RESULTS_DIR) / f'{building}_bem_calibrated.idf'
    baseline_path = models_dir / f'{building}.idf'
    shutil.copy(source, baseline_path)
    Eppy.IdfTransitionVersion(idfFilePath=str(baseline_path), transitionExePath=str(config.TRANSITION_V24_1_TO_V24_2))
    idf = IDF(str(baseline_path))
    classrooms = Scenario.ClassroomZones(idf)
    for equipment in idf.idfobjects['ELECTRICEQUIPMENT']:
        if Scenario.ZoneNameOf(equipment) in classrooms:
            equipment.Watts_per_Floor_Area = CLASSROOM_EQUIPMENT_DENSITY
    for outdoor_air in idf.idfobjects['DESIGNSPECIFICATION:OUTDOORAIR']:
        outdoor_air.Outdoor_Air_Method = 'Flow/Area'
    set_constant_equipment_schedule(idf)
    if building == 'building09':
        set_cooling_setpoint(idf, BUILDING09_COOLING_SETPOINT)
    Eppy.IdfSetRunPeriod(idf, config.RUN_PERIOD)
    idf.saveas(str(baseline_path))
    return idf, classrooms


IDF.setiddname(str(config.IDD_V24_2))
baselines = {building: scenario_baseline(building) for building in config.BUILDINGS}
for building, (_, classrooms) in baselines.items():
    print(f"{config.BUILDINGS[building]['name']}: {len(classrooms)} classroom zones {classrooms}")

# %% [markdown]
# ## 2. Scenario modifications

# %% [markdown]
# ### 2.1 Demand-driven ventilation
#
# * **CAV-person**: outdoor air computed from the flow rate per person (design capacity).
# * **VAV-person**: outdoor air per person modulated by an outdoor-air schedule equal to the
#   occupancy schedule of the zone, with a minimum fraction when the classroom is unoccupied.

# %%
def ventilation_per_person(idf, classrooms):
    for outdoor_air in idf.idfobjects['DESIGNSPECIFICATION:OUTDOORAIR']:
        if Scenario.ZoneNameOf(outdoor_air) in classrooms:
            outdoor_air.Outdoor_Air_Method = 'Flow/Person'


def ventilation_vav_person(idf, classrooms):
    occupancy_schedules = Scenario.PeopleSchedules(idf)
    vav_schedules = {}
    for outdoor_air in idf.idfobjects['DESIGNSPECIFICATION:OUTDOORAIR']:
        zone = Scenario.ZoneNameOf(outdoor_air)
        if zone not in classrooms:
            continue
        outdoor_air.Outdoor_Air_Method = 'Flow/Person'
        occupancy_schedule = occupancy_schedules[zone]
        if occupancy_schedule not in vav_schedules:
            # copy of the occupancy schedule where unoccupied hours keep the minimum fraction
            source = Scenario.ScheduleCompactByName(idf, occupancy_schedule)
            vav = idf.newidfobject('SCHEDULE:COMPACT')
            for field in source.fieldnames:
                value = source[field]
                if field in ('key', 'Name') or value in (None, ''):
                    continue
                try:
                    if float(value) == 0 and field != 'Schedule_Type_Limits_Name':
                        value = VAV_MINIMUM_FRACTION
                except (ValueError, TypeError):
                    pass
                vav[field] = value
            vav.Name = f'VAV_{occupancy_schedule}'
            vav_schedules[occupancy_schedule] = vav.Name
        outdoor_air.Outdoor_Air_Schedule_Name = vav_schedules[occupancy_schedule]


# %% [markdown]
# ### 2.2 Space capacity

# %%
def scale_capacity(idf, classrooms, factor):
    for people in idf.idfobjects['PEOPLE']:
        if Scenario.ZoneNameOf(people) in classrooms:
            people.People_per_Floor_Area = float(people.People_per_Floor_Area) * factor


# %% [markdown]
# ### 2.3 Occupancy schedules
#
# The occupied hours of the classroom booking schedules are set to a fixed occupancy rate;
# the classroom equipment follows the modified occupancy schedule.

# %%
def fixed_occupancy_rate(idf, classrooms, occupancy_rate):
    occupancy_schedules = Scenario.PeopleSchedules(idf)
    for name in {occupancy_schedules[zone] for zone in classrooms}:
        schedule = Scenario.ScheduleCompactByName(idf, name)
        for field in schedule.fieldnames:
            if field in ('key', 'Name', 'Schedule_Type_Limits_Name'):
                continue
            try:
                if float(schedule[field]) > 0:
                    schedule[field] = occupancy_rate
            except (ValueError, TypeError):
                pass
    for equipment in idf.idfobjects['ELECTRICEQUIPMENT']:
        zone = Scenario.ZoneNameOf(equipment)
        if zone in classrooms and equipment.Schedule_Name.startswith('EqpSch_'):
            equipment.Schedule_Name = occupancy_schedules[zone]


# %% [markdown]
# ### 2.4 Space repurposing: classrooms → closed offices

# %%
def closed_offices(idf, classrooms):
    for people in idf.idfobjects['PEOPLE']:
        if Scenario.ZoneNameOf(people) in classrooms:
            people.People_per_Floor_Area = OFFICE_PEOPLE_DENSITY
            people.Number_of_People_Schedule_Name = OFFICE_SCHEDULE
    for equipment in idf.idfobjects['ELECTRICEQUIPMENT']:
        if Scenario.ZoneNameOf(equipment) in classrooms:
            equipment.Schedule_Name = OFFICE_SCHEDULE
            equipment.Watts_per_Floor_Area = OFFICE_EQUIPMENT_DENSITY


def closed_offices_vav_person(idf, classrooms):
    """VAV outdoor-air schedule derived from the generic office occupancy schedule (Schedule:Year/Week/Day)"""
    vav_name = lambda name: 'VAV_' + name
    for schedule_year in idf.idfobjects['SCHEDULE:YEAR']:
        if schedule_year.Name == OFFICE_SCHEDULE:
            vav_year = idf.newidfobject('SCHEDULE:YEAR')
            vav_year.Name = vav_name(schedule_year.Name)
            vav_year.Schedule_Type_Limits_Name = schedule_year.Schedule_Type_Limits_Name
            vav_year.ScheduleWeek_Name_1 = vav_name(schedule_year.ScheduleWeek_Name_1)
            vav_year.Start_Month_1, vav_year.Start_Day_1 = 1, 1
            vav_year.End_Month_1, vav_year.End_Day_1 = 12, 31
            break
    for week in idf.idfobjects['SCHEDULE:WEEK:DAILY']:
        if week.Name == OFFICE_SCHEDULE + '_Week 1':
            vav_week = idf.newidfobject('SCHEDULE:WEEK:DAILY')
            for field in week.fieldnames:
                if field not in ('key', 'Name'):
                    vav_week[field] = week[field]
            vav_week.Name = vav_name(week.Name)
            day_names = [vav_week[f] for f in vav_week.fieldnames if 'ScheduleDay_Name' in f]
            for field in vav_week.fieldnames:
                if 'ScheduleDay_Name' in field:
                    vav_week[field] = vav_week[field].replace('OCC_', 'VAV_')
            for day in idf.idfobjects['SCHEDULE:DAY:INTERVAL']:
                if day.Name in day_names:
                    vav_day = idf.newidfobject('SCHEDULE:DAY:INTERVAL')
                    vav_day.Name = day.Name.replace('OCC_', 'VAV_')
                    vav_day.Schedule_Type_Limits_Name = day.Schedule_Type_Limits_Name
                    for field in day.fieldnames:
                        if 'Time_' in field and len(str(day[field])) > 0:
                            value = day[field]
                            try:
                                value = max(float(value), VAV_MINIMUM_FRACTION)
                            except (ValueError, TypeError):
                                pass
                            vav_day[field] = value
            break
    for outdoor_air in idf.idfobjects['DESIGNSPECIFICATION:OUTDOORAIR']:
        if Scenario.ZoneNameOf(outdoor_air) in classrooms:
            outdoor_air.Outdoor_Air_Method = 'Flow/Person'
            outdoor_air.Outdoor_Air_Schedule_Name = vav_name(OFFICE_SCHEDULE)


# %% [markdown]
# ## 3. Scenario matrix

# %%
SCENARIOS = {
    'scenario0': lambda idf, c: None,
    'scenario1': ventilation_per_person,
    'scenario2': ventilation_vav_person,
    'scenario3': lambda idf, c: scale_capacity(idf, c, 1.2),
    'scenario4': lambda idf, c: scale_capacity(idf, c, 0.8),
    # occupancy rates just below 1, 0.5, 0.75, 0.25 keep the fractions inside the schedule limits
    'scenario5': lambda idf, c: fixed_occupancy_rate(idf, c, 0.9999),
    'scenario6': lambda idf, c: fixed_occupancy_rate(idf, c, 0.4999),
    'scenario7': lambda idf, c: fixed_occupancy_rate(idf, c, 0.7499),
    'scenario8': lambda idf, c: fixed_occupancy_rate(idf, c, 0.2499),
    'scenario9': closed_offices,
    'scenario10': lambda idf, c: (closed_offices(idf, c), ventilation_per_person(idf, c)),
    'scenario11': lambda idf, c: (closed_offices(idf, c), closed_offices_vav_person(idf, c)),
}

for building, (baseline, classrooms) in baselines.items():
    for definition in scenario_definitions:
        idf = copy.deepcopy(baseline)
        SCENARIOS[definition['uid']](idf, classrooms)
        scenario_dir = config.SCENARIO_RESULTS_DIR / definition['uid']
        scenario_dir.mkdir(parents=True, exist_ok=True)
        idf.saveas(str(scenario_dir / f'{building}.idf'))
    print(f"{config.BUILDINGS[building]['name']}: {len(scenario_definitions)} scenario models written")
