class Utils():

    @staticmethod
    def TopologicZoneInheritSpaceData(tpZones=[]):

        from topologicpy.Topology import Topology
        from topologicpy.CellComplex import CellComplex
        from topologicpy.Dictionary import Dictionary
        from topologicpy.Cell import Cell

        newTpZones=[]
        
        for tpZone in tpZones:
            
            # Zone spaces
            tpCells=CellComplex.Cells(tpZone)

            # Zone data
            d=Topology.Dictionary(tpZone)
            zoneUID=Dictionary.ValueAtKey(d,'UID')

            # Geometry data
            pr_ZoneArea=0
            for tpCell in tpCells:
                pr_Area=Cell.Area(tpCell)
                pr_ZoneArea+=pr_Area
            pr_ZoneVolume=0
            for tpCell in tpCells:
                pr_Volume=Cell.Volume(tpCell)
                pr_ZoneVolume+=pr_Volume

            # Occupancy data
            pr_ZoneOccupantCount=0
            for tpCell in tpCells:
                pr_Area=Cell.Area(tpCell)
                cellDict=Topology.Dictionary(tpCell)
                pr_OccupantCount=float(Dictionary.ValueAtKey(cellDict,'pr_OccupancyDensityOperation'))*pr_Area
                pr_ZoneOccupantCount+=pr_OccupantCount

            # New zone data
            pr_ZoneIsHeated,pr_ZoneIsCooled=False,False
            pr_ZoneIsMechanicallyVentilated=False
            pr_ZoneIsOccupied=False
            pr_ZoneOccupancyDensityOperation,pr_ZoneOccupancyDensitySafety=0,0
            pr_ZoneSpaceTemperatureSummerMax,pr_ZoneSpaceTemperatureSummerMin=30,30
            pr_ZoneSpaceTemperatureWinterMax,pr_ZoneSpaceTemperatureWinterMin=10,0
            pr_ZoneHumidityMax,pr_ZoneHumidityMin=100,0
            pr_ZoneMechanicalVentilationRate,pr_ZoneMechanicalVentilationRatePerPerson=0,0
            pr_ZoneOccupancyType,pr_ZoneOccupancyTypeCounter=None,0
            pr_ZoneEquipmentPowerDensity,pr_ZoneLightingPowerDensity=0,0

            # New zone schedules
            rl_ZoneIsScheduledBy_Cooling=None
            rl_ZoneIsScheduledBy_Heating=None
            rl_ZoneIsScheduledBy_Ventilation=None
            rl_ZoneIsScheduledBy_Lighting=None
            rl_ZoneIsScheduledBy_Occupancy=None
            rl_ZoneIsScheduledBy_Equipment=None

            # Zone data by cells
            for tpCell in tpCells:
                d=Topology.Dictionary(tpCell)
                
                # GEOMETRICAL
                pr_Area=Cell.Area(tpCell)
                pr_Volume=Cell.Volume(tpCell)

                # BOOLEANS
                # pr_IsHeated
                pr_IsHeated=bool(Dictionary.ValueAtKey(d,'pr_IsHeated'))
                if pr_IsHeated:
                    pr_ZoneIsHeated=pr_IsHeated
                # pr_IsCooled
                pr_IsCooled=bool(Dictionary.ValueAtKey(d,'pr_IsCooled'))
                if pr_IsCooled:
                    pr_ZoneIsCooled=pr_IsCooled
                # pr_IsMechanicallyVentilated
                pr_IsMechanicallyVentilated=bool(Dictionary.ValueAtKey(d,'pr_IsMechanicallyVentilated'))
                if pr_IsMechanicallyVentilated:
                    pr_ZoneIsMechanicallyVentilated=pr_IsMechanicallyVentilated
                # pr_IsOccupied
                pr_IsOccupied=bool(Dictionary.ValueAtKey(d,'pr_IsOccupied'))
                if pr_IsOccupied:
                    pr_ZoneIsOccupied=pr_IsOccupied

                # AVERAGE
                #pr_OccupancyDensityOperation
                pr_OccupancyDensityOperation=float(Dictionary.ValueAtKey(d,'pr_OccupancyDensityOperation'))
                pr_ZoneOccupancyDensityOperation+=pr_OccupancyDensityOperation*pr_Area/pr_ZoneArea
                #pr_OccupancyDensitySafety
                pr_OccupancyDensitySafety=float(Dictionary.ValueAtKey(d,'pr_OccupancyDensitySafety'))
                pr_ZoneOccupancyDensitySafety+=pr_OccupancyDensitySafety*pr_Area/pr_ZoneArea
                #pr_MechanicalVentilationRate
                pr_MechanicalVentilationRate=float(Dictionary.ValueAtKey(d,'pr_MechanicalVentilationRate'))
                pr_ZoneMechanicalVentilationRate+=pr_MechanicalVentilationRate*pr_Volume/pr_ZoneVolume
                #pr_MechanicalVentilationRatePerPerson
                pr_MechanicalVentilationRatePerPerson=float(Dictionary.ValueAtKey(d,'pr_MechanicalVentilationRatePerPerson'))
                pr_OccupantCount=float(Dictionary.ValueAtKey(d,'pr_OccupancyDensityOperation'))*pr_Area
                try:
                    pr_ZoneMechanicalVentilationRatePerPerson+=pr_MechanicalVentilationRatePerPerson*pr_OccupantCount/pr_ZoneOccupantCount  
                except:
                    pr_ZoneMechanicalVentilationRatePerPerson+=0
                #pr_EquipmentPowerDensity
                pr_EquipmentPowerDensity=float(Dictionary.ValueAtKey(d,'pr_EquipmentPowerDensity'))
                pr_ZoneEquipmentPowerDensity+=pr_EquipmentPowerDensity*pr_Area/pr_ZoneArea
                #pr_LightingPowerDensity
                pr_LightingPowerDensity=float(Dictionary.ValueAtKey(d,'pr_LightingPowerDensity'))
                pr_ZoneLightingPowerDensity+=pr_LightingPowerDensity*pr_Area/pr_ZoneArea
               
                # MIN/MAX
                # pr_SpaceTemperatureSummerMax
                pr_SpaceTemperatureSummerMax=float(Dictionary.ValueAtKey(d,'pr_SpaceTemperatureSummerMax'))
                if pr_SpaceTemperatureSummerMax<pr_ZoneSpaceTemperatureSummerMax:
                    pr_ZoneSpaceTemperatureSummerMax=pr_SpaceTemperatureSummerMax
                # pr_SpaceTemperatureSummerMax
                pr_SpaceTemperatureSummerMin=float(Dictionary.ValueAtKey(d,'pr_SpaceTemperatureSummerMin'))
                if pr_SpaceTemperatureSummerMin<pr_ZoneSpaceTemperatureSummerMin:
                    pr_ZoneSpaceTemperatureSummerMin=pr_SpaceTemperatureSummerMin
                # pr_SpaceTemperatureWinterMax
                pr_SpaceTemperatureWinterMax=float(Dictionary.ValueAtKey(d,'pr_SpaceTemperatureWinterMax'))
                if pr_SpaceTemperatureWinterMax>pr_ZoneSpaceTemperatureWinterMax:
                    pr_ZoneSpaceTemperatureWinterMax=pr_SpaceTemperatureWinterMax
                # pr_SpaceTemperatureWinterMin
                pr_SpaceTemperatureWinterMin=float(Dictionary.ValueAtKey(d,'pr_SpaceTemperatureWinterMin'))
                if pr_SpaceTemperatureWinterMin>pr_ZoneSpaceTemperatureWinterMin:
                    pr_ZoneSpaceTemperatureWinterMin=pr_SpaceTemperatureWinterMin
                # pr_HumidityMax
                pr_HumidityMax=float(Dictionary.ValueAtKey(d,'pr_HumidityMax'))
                if pr_HumidityMax<pr_ZoneHumidityMax:
                    pr_ZoneHumidityMax=pr_HumidityMax
                # pr_HumidityMin
                pr_HumidityMin=float(Dictionary.ValueAtKey(d,'pr_HumidityMin'))
                if pr_HumidityMin>pr_ZoneHumidityMin:
                    pr_ZoneHumidityMin=pr_HumidityMin

                # PREVALENT
                # pr_OccupancyType
                pr_OccupancyType=Dictionary.ValueAtKey(d,'pr_OccupancyType')
                # Schedules
                rl_IsScheduledBy_Cooling=Dictionary.ValueAtKey(d,'rl_IsScheduledBy_Cooling')
                rl_IsScheduledBy_Heating=Dictionary.ValueAtKey(d,'rl_IsScheduledBy_Heating')
                rl_IsScheduledBy_Lighting=Dictionary.ValueAtKey(d,'rl_IsScheduledBy_Lighting')
                rl_IsScheduledBy_Occupancy=Dictionary.ValueAtKey(d,'rl_IsScheduledBy_Occupancy')
                rl_IsScheduledBy_Ventilation=Dictionary.ValueAtKey(d,'rl_IsScheduledBy_Ventilation')
                rl_IsScheduledBy_Equipment=Dictionary.ValueAtKey(d,'rl_IsScheduledBy_Equipment')

                if pr_OccupantCount>pr_ZoneOccupancyTypeCounter:
                    pr_ZoneOccupancyTypeCounter=pr_OccupantCount
                    pr_ZoneOccupancyType=pr_OccupancyType 
                    rl_ZoneIsScheduledBy_Cooling=rl_IsScheduledBy_Cooling 
                    rl_ZoneIsScheduledBy_Heating=rl_IsScheduledBy_Heating 
                    rl_ZoneIsScheduledBy_Lighting=rl_IsScheduledBy_Lighting 
                    rl_ZoneIsScheduledBy_Occupancy=rl_IsScheduledBy_Occupancy 
                    rl_ZoneIsScheduledBy_Ventilation=rl_IsScheduledBy_Ventilation 
                    rl_ZoneIsScheduledBy_Equipment=rl_IsScheduledBy_Equipment 


                    
            
            # Add data to the zones
            zoneDictKeys=['UID','pr_IsHeated','pr_IsCooled','pr_IsMechanicallyVentilated','pr_IsOccupied',
                        'pr_OccupancyDensityOperation','pr_OccupancyDensitySafety','pr_MechanicalVentilationRate',
                        'pr_MechanicalVentilationRatePerPerson','pr_SpaceTemperatureSummerMax','pr_SpaceTemperatureSummerMin',
                        'pr_SpaceTemperatureWinterMax','pr_SpaceTemperatureWinterMin','pr_HumidityMax','pr_HumidityMin','pr_OccupancyType',
                        'pr_EquipmentPowerDensity','pr_LightingPowerDensity',
                        'rl_IsScheduledBy_Cooling','rl_IsScheduledBy_Heating','rl_IsScheduledBy_Lighting',
                        'rl_IsScheduledBy_Occupancy','rl_IsScheduledBy_Ventilation','rl_IsScheduledBy_Equipment'
                        ]
            zoneDictValues=[zoneUID,pr_ZoneIsHeated,pr_ZoneIsCooled,pr_ZoneIsMechanicallyVentilated,pr_ZoneIsOccupied,
                        pr_ZoneOccupancyDensityOperation,pr_ZoneOccupancyDensitySafety,pr_MechanicalVentilationRate,
                        pr_ZoneMechanicalVentilationRatePerPerson,pr_ZoneSpaceTemperatureSummerMax,pr_ZoneSpaceTemperatureSummerMin,
                        pr_ZoneSpaceTemperatureWinterMax,pr_ZoneSpaceTemperatureWinterMin,pr_ZoneHumidityMax,pr_ZoneHumidityMin,pr_ZoneOccupancyType,
                        pr_ZoneEquipmentPowerDensity,pr_ZoneLightingPowerDensity,
                        rl_IsScheduledBy_Cooling,rl_IsScheduledBy_Heating,rl_IsScheduledBy_Lighting,
                        rl_IsScheduledBy_Occupancy,rl_IsScheduledBy_Ventilation,rl_IsScheduledBy_Equipment
                        ]

            zoneDict=Dictionary.ByKeysValues(zoneDictKeys,zoneDictValues)
            tpZone=Topology.SetDictionary(tpZone,zoneDict)
            newTpZones.append(tpZone)
            
        return newTpZones

class HB():


    @staticmethod
    def HBOpaqueConstructionsByIFCPaths(
        ifcFilePath=None,
        ifcMaterialPath=None,
        ifcUnit='cm'
        ):
    
        # Dependencies
        import ifcopenshell
        from honeybee_energy.construction.opaque import OpaqueConstruction
        from honeybee_energy.material.opaque import EnergyMaterial

        # Main IFC file
        ifcFile=ifcopenshell.open(ifcFilePath)

        # File with IFC materials
        ifcMaterialFile=ifcopenshell.open(ifcMaterialPath)

        # Get all the materials from the material IFC file
        ifcMaterials=ifcMaterialFile.by_type('IfcMaterial')
        ifcMaterialNames=[ifcMaterial.Name for ifcMaterial in ifcMaterials]

        # Initiate outputs
        hbMaterials=[]
        hbOpaqueConstructions=[]

        # Get all the stratigraphies from the main IFC file used in walls, roofs and floors
        ifcWallSlabs=ifcFile.by_type("IfcWall")+ifcFile.by_type("IfcSlab")
        ifcWallSlabTypeNames=[]
        ifcWallSlabTypes=[]
        for ifcWallSlab in ifcWallSlabs:
            ifcType=ifcopenshell.util.element.get_type(ifcWallSlab)
            if ifcType.Name not in ifcWallSlabTypeNames:
                ifcWallSlabTypeNames.append(ifcType.Name)
                ifcWallSlabTypes.append(ifcType)
                
        # Iterate over the IFC stratigraphies
        for ifcWallSlabType in ifcWallSlabTypes:
            
            # Get materials and their props
            hbMaterialDicts=[]
            for rel in ifcWallSlabType.HasAssociations: 
                if rel.is_a('IfcRelAssociatesMaterial'):
                    ifcMaterialLayerSet=rel.RelatingMaterial
                    for layer in ifcMaterialLayerSet.MaterialLayers:
                        layerMaterialName=layer.Material.Name
                        layerMaterial=ifcMaterials[ifcMaterialNames.index(layerMaterialName)]
                        # Material thickness
                        layerThickness=layer.LayerThickness
                        if ifcUnit=='cm':
                            layerThickness=layerThickness/100
                        if layerThickness==0:
                            layerThickness=0.005
                        # Material identifiers
                        materialIdentifier=f'{layerMaterial.Name}-{layerThickness}'.replace(',','-')
                        materialName=layerMaterial.Name.replace(',','-')
                        # Material properties
                        conductivity,density,specific_heat=None,None,None
                        thermal_absorptance,solar_absorptance,visible_absorptance=0.9,0.7,0.7 #default
                        if layerMaterial.HasProperties:
                            for propSet in layerMaterial.HasProperties:
                                for prop in propSet.Properties:
                                    if prop.Name=='ThermalConductivity':
                                        conductivity=prop.NominalValue.wrappedValue
                                    elif prop.Name=='Density':
                                        density=prop.NominalValue.wrappedValue
                                    elif 'SPECIFIC' and 'HEAT' in prop.Name.upper():
                                        specific_heat=int(prop.NominalValue.wrappedValue)
                                    elif 'EMISSIVITY' in prop.Name.upper():
                                        if prop.NominalValue.wrappedValue>0.05:
                                            thermal_absorptance=round(prop.NominalValue.wrappedValue,2)
                                        else:
                                            thermal_absorptance=0.7

                        

                        # Honeybee material dictionary
                        if conductivity is not None and density is not None and specific_heat is not None:
                            hbMaterialDict = {
                                "type": 'EnergyMaterial',
                                "identifier": materialIdentifier,
                                "display_name": materialName,
                                "roughness": 'MediumRough',
                                "thickness": layerThickness,
                                "conductivity": round(conductivity,3),
                                "density": density,
                                "specific_heat": specific_heat,
                                "thermal_absorptance":thermal_absorptance,
                                "solar_absorptance": solar_absorptance,
                                "visible_absorptance": visible_absorptance
                            }
                            hbMaterialDicts.append(hbMaterialDict)
                            # HB material
                            hbMaterial=EnergyMaterial.from_dict(hbMaterialDict)
                            hbMaterials.append(hbMaterial)
                        else:
                            print(f'No data found for material {materialName}')
                                    
            # Get the Honeybee opaque construction
            if len(hbMaterialDicts)>0:
                hbConstructionDict={
                    "type": 'OpaqueConstruction',
                    "identifier": ifcWallSlabType.Name.split(":")[1],
                    "display_name": ifcWallSlabType.Name.split(":")[1],
                    "materials": hbMaterialDicts  # list of unique material objects (from outside to inside)
                    }
                hbConstruction=OpaqueConstruction.from_dict(hbConstructionDict)
                hbOpaqueConstructions.append(hbConstruction)
            else:
                print(f'No construction created for {ifcWallSlabType.Name}')

        return hbOpaqueConstructions,hbMaterials


    @staticmethod
    def HBShadesByTopologicBRepPaths(shadingFacesPaths=[], tbimUnits='cm'):
        
        # Dependencies
        from honeybee.shade import Shade
        from ladybug_geometry.geometry3d import Point3D
        from topologicpy.Topology import Topology
        from topologicpy.Cluster import Cluster
        from topologicpy.Wire import Wire
        from topologicpy.Face import Face

        hbShades = []

        j = 0
        for shadingFacesPath in shadingFacesPaths:

            # Get the shading faces as Topologic faces
            tpShadingFaces = Topology.ByBREPPath(shadingFacesPath)
            
            # Iterate
            i = 0
            for tpShadingFace in Cluster.Faces(tpShadingFaces):
                # Topologic vertices
                tpShadingFaceVertices = Wire.Vertices(Face.ExternalBoundary(tpShadingFace))
                # Honeybee vertices
                if tbimUnits == 'm':
                    hbShadingFacePoints = [Point3D(float(tpVertex.X()), float(tpVertex.Y()), float(tpVertex.Z())) for tpVertex in tpShadingFaceVertices]
                elif tbimUnits == 'cm':
                    hbShadingFacePoints = [Point3D(float(tpVertex.X()/100), float(tpVertex.Y()/100), float(tpVertex.Z()/100)) for tpVertex in tpShadingFaceVertices]
                # Honeybee shade
                hbShade = Shade.from_vertices(identifier=f'shade{j}-{i}', vertices=hbShadingFacePoints, is_detached=True)
                hbShades.append(hbShade)
                i += 1
            
            j+=1
            
        return hbShades


    @staticmethod
    def HBDefaultSimulationParameter():
    
        from honeybee_energy.simulation.parameter import SimulationParameter
    
        simulationOutputDict={
            "type": "SimulationOutput",
            "outputs": ['Zone Ideal Loads Supply Air Total Cooling Energy'],
            "reporting_frequency": 'Annual',
            "include_sqlite": True,
            "include_html": True,
            "summary_reports": ['AllSummary', 'AnnualBuildingUtilityPerformanceSummary'],
            "unmet_setpoint_tolerance": 0.2
        }

        daylightsavingDict={
            "type": "DaylightSavingTime",
            "start_date": [3, 12],
            "end_date": [11, 5]
        }

        runPeriodDict={
            "type": "RunPeriod",
            "start_date": (1, 1),
            "end_date": (12, 31),
            "start_day_of_week": 'Monday',
            "holidays": [(1, 1), (7, 4)],
            "daylight_saving_time": daylightsavingDict, # DaylightSavingTime dictionary representation
            "leap_year": False
        }

        simulationControlDict={
            "type": "SimulationControl",
            "do_zone_sizing": True,
            "do_system_sizing": False,
            "do_plant_sizing": False,
            "run_for_sizing_periods": False,
            "run_for_run_periods": True
        }

        shadowCalculationDict={
            "type": "ShadowCalculation",
            "solar_distribution": 'FullInteriorAndExteriorWithReflections',
            "calculation_method": 'PolygonClipping',
            "calculation_update_method": 'Periodic',
            "calculation_frequency": 30,
            "maximum_figures": 15000
        }

        sizingParameterDict={
            "type": "SizingParameter",
            "design_days": [],  # Array of Ladybug DesignDay dictionaries
            "heating_factor": 1.25,
            "cooling_factor": 1.15,
            "efficiency_standard": "ASHRAE_2004",  # standard for HVAC efficiency
            "climate_zone": "5A",  # climate zone for HVAC efficiency
            "building_type": "LargeOffice",  # building type for HVAC efficiency
            "bypass_efficiency_sizing": False  # bypass the efficiency sizing run
        }

        data={
            "type": "SimulationParameter",
            "output": simulationOutputDict, # Honeybee SimulationOutput dictionary
            "run_period": runPeriodDict, # Honeybee RunPeriod dictionary
            "timestep": 6, # Integer for the simulation timestep
            "simulation_control": simulationControlDict, # Honeybee SimulationControl dictionary
            "shadow_calculation": shadowCalculationDict, # Honeybee ShadowCalculation dictionary
            "sizing_parameter": sizingParameterDict # Honeybee SizingParameter dictionary
        }

        simulationParameter=SimulationParameter.from_dict(data)
        return simulationParameter
    
    @staticmethod
    def HBRoomSetSetpointSchedules(HBRoom=None):
    
        """Set default heating, cooling, humidify, dehumidify, serviceHotWater, schedules"""

        from honeybee_energy.schedule.ruleset import ScheduleRuleset
        from honeybee_energy.schedule.typelimit import ScheduleTypeLimit
        from honeybee_energy.schedule.day import ScheduleDay
        from honeybee_energy.load.setpoint import Setpoint
        from honeybee_energy.load.hotwater import ServiceHotWater
        import honeybee_energy
        from ladybug.dt import Time
        
        # Set schedule type limits
        temperatureScheduleTypeLimit=ScheduleTypeLimit.from_dict({
            "type": 'ScheduleTypeLimit',
            "identifier": 'temperatureScheduleTypeLimit',
            "display_name": 'Fractional',
            "lower_limit": 0,
            "upper_limit": 50,
            "numeric_type": 'Continuous',
            "unit_type": "Temperature"
            })

        humidityScheduleTypeLimit=ScheduleTypeLimit.from_dict({
            "type": 'ScheduleTypeLimit',
            "identifier": 'humidityScheduleTypeLimit',
            "display_name": 'Fractional',
            "lower_limit": 0,
            "upper_limit": 100,
            "numeric_type": 'Continuous',
            "unit_type": "Percent"
            })

        occupancyScheduleTypeLimit=ScheduleTypeLimit.from_dict({
            "type": 'ScheduleTypeLimit',
            "identifier": 'occupancyScheduleTypeLimit',
            "display_name": 'Fractional',
            "lower_limit": 0,
            "upper_limit": 1,
            "numeric_type": 'Continuous',
            "unit_type": "Dimensionless"
            })

        # Setpoint
        heatingSchedule = ScheduleRuleset.from_constant_value('Generic room Heating', 20, temperatureScheduleTypeLimit)
        coolingSchedule = ScheduleRuleset.from_constant_value('Generic room Cooling', 26, temperatureScheduleTypeLimit)
        humidifySchedule = ScheduleRuleset.from_constant_value('Generic room Humidifying', 10, humidityScheduleTypeLimit)
        dehumidifySchedule = ScheduleRuleset.from_constant_value('Generic room Dehumidifying', 60, humidityScheduleTypeLimit)
        setpoint = Setpoint(
            identifier='Room Setpoint', 
            heating_schedule=heatingSchedule, cooling_schedule=coolingSchedule, 
            humidifying_schedule=humidifySchedule, dehumidifying_schedule=dehumidifySchedule)
        
        # Occupancy
        simpleOfficeDaySchedule = ScheduleDay(identifier='Simple Weekday',values=[0, 1, 0],times=[Time(0, 0),Time(9, 0),Time(17, 0)]) 
        occupancySchedule = ScheduleRuleset(identifier='Office room dayschedule', default_day_schedule=simpleOfficeDaySchedule, schedule_rules=None, schedule_type_limit=occupancyScheduleTypeLimit) 
        
        # Hot water
        serviceHotWater = ServiceHotWater('Office Hot Water', 0.1, occupancySchedule) 
        program=honeybee_energy.lib.programtypes.office_program
        
        # Set data
        HBRoom.properties.energy.program_type = program
        HBRoom.properties.energy.add_default_ideal_air() 
        HBRoom.properties.energy.setpoint = setpoint 
        HBRoom.properties.energy.service_hot_water = serviceHotWater 
        
        return HBRoom

    @staticmethod
    def DefaultScheduleTypeLimits():

        """"
        Return the default schedule type limits useful for energy loads simulations
        """

        # Import dependencies
        from honeybee_energy.schedule.typelimit import ScheduleTypeLimit

        # Set schedule type limits
        temperatureScheduleTypeLimit={
                    "type": 'ScheduleTypeLimit',
                    "identifier": 'temperatureScheduleTypeLimit',
                    "display_name": 'Fractional',
                    "lower_limit": 0,
                    "upper_limit": 50,
                    "numeric_type": 'Continuous',
                    "unit_type": "Temperature"
                    }

        humidityScheduleTypeLimit={
                    "type": 'ScheduleTypeLimit',
                    "identifier": 'humidityScheduleTypeLimit',
                    "display_name": 'Fractional',
                    "lower_limit": 0,
                    "upper_limit": 100,
                    "numeric_type": 'Continuous',
                    "unit_type": "Percent"
                    }

        occupancyScheduleTypeLimit={
                    "type": 'ScheduleTypeLimit',
                    "identifier": 'occupancyScheduleTypeLimit',
                    "display_name": 'Fractional',
                    "lower_limit": 0,
                    "upper_limit": 1,
                    "numeric_type": 'Continuous',
                    "unit_type": "Dimensionless"
                    }

        lightingScheduleTypeLimit={
                    "type": 'ScheduleTypeLimit',
                    "identifier": 'lightingScheduleTypeLimit',
                    "display_name": 'Fractional',
                    "lower_limit": 0,
                    "upper_limit": 1,
                    "numeric_type": 'Continuous',
                    "unit_type": "Dimensionless"
                    }

        equipmentScheduleTypeLimit={
                    "type": 'ScheduleTypeLimit',
                    "identifier": 'equipmentScheduleTypeLimit',
                    "display_name": 'Fractional',
                    "lower_limit": 0,
                    "upper_limit": 1,
                    "numeric_type": 'Continuous',
                    "unit_type": "Dimensionless"
                    }

        availabilityScheduleTypeLimit={
                    "type": 'ScheduleTypeLimit',
                    "identifier": 'availabilityScheduleTypeLimit',
                    "display_name": 'Fractional',
                    "lower_limit": 0,
                    "upper_limit": 1,
                    "numeric_type": 'Continuous',
                    "unit_type": "Dimensionless"
                    }
        
        return [occupancyScheduleTypeLimit,temperatureScheduleTypeLimit, humidityScheduleTypeLimit, lightingScheduleTypeLimit, equipmentScheduleTypeLimit, availabilityScheduleTypeLimit]

    @staticmethod
    def HBLightingScheduleRulesetDictsByJSONPath(lightingSchedulePath=None,prefix='LghSch_'):

        """Get the lighting schedules ruleset dicts for HB by a JSON file compliant with HB APIs for Schedule Rulesets"""

        # Dependencies
        import json
        from honeybee_energy.schedule.ruleset import ScheduleRuleset

        # Read JSON data
        with open(lightingSchedulePath, 'r') as file:
            lightingSchedulesJSON = json.load(file)
            if not isinstance(lightingSchedulesJSON,list):
                lightingSchedulesJSON=[lightingSchedulesJSON]

        # Schedule type limit
        lightingScheduleTypeLimitDict={"type": 'ScheduleTypeLimit',"identifier": 'lightingScheduleTypeLimit',"display_name": 'Fractional',"lower_limit": 0,"upper_limit": 1,"numeric_type": 'Continuous',"unit_type": "Dimensionless"}

        # Clean data
        lightingSchedulesDicts=[]
        for lightingScheduleJSON in lightingSchedulesJSON:
            # Identifier
            if prefix not in lightingScheduleJSON['identifier']:
                lightingScheduleJSON['identifier']=prefix+lightingScheduleJSON['identifier']
            # Name
            lightingScheduleJSON['display_name']='LightingSchedule_'+lightingScheduleJSON['display_name']
            # Schedule type limits
            lightingScheduleJSON['schedule_type_limit']=lightingScheduleTypeLimitDict
            # Day schedules
            daySchedules=[]
            for daySchedule in lightingScheduleJSON['day_schedules']:
                # Times
                times=[]
                for time in daySchedule['times']:
                    hour,minute=time[0],time[1]
                    time=(hour,minute)
                    times.append(time)
                daySchedule['times']=times
                daySchedules.append(daySchedule)
            lightingScheduleJSON['day_schedules']=daySchedules
            # Schedule Rules
            scheduleRules=[]
            for rule in lightingScheduleJSON['schedule_rules']:
                # Type
                rule['type']='ScheduleRuleAbridged'
                # Date
                rule['start_date']=(rule['start_date'][0],rule['start_date'][1])
                rule['end_date']=(rule['end_date'][0],rule['end_date'][1])
                scheduleRules.append(rule)
            lightingScheduleJSON['schedule_rules']=scheduleRules
        
            lightingSchedulesDicts.append(lightingScheduleJSON)

        # Output
        return lightingSchedulesDicts

    @staticmethod
    def HBOccupancyScheduleRulesetDictsByJSONPath(occupancySchedulePath=None,prefix='OccSch_'):

        """Get the occupancy schedules ruleset dicts for HB by a JSON file compliant with HB APIs for Schedule Rulesets"""

        # Dependencies
        import json
        from honeybee_energy.schedule.ruleset import ScheduleRuleset

        # Read JSON data
        with open(occupancySchedulePath, 'r') as file:
            occupancySchedulesJSON = json.load(file)
            if not isinstance(occupancySchedulesJSON,list):
                occupancySchedulesJSON=[occupancySchedulesJSON]

        # Schedule type limit
        occupancyScheduleTypeLimitDict={"type": 'ScheduleTypeLimit',"identifier": 'occupancyScheduleTypeLimit',"display_name": 'Fractional',"lower_limit": 0,"upper_limit": 1,"numeric_type": 'Continuous',"unit_type": "Dimensionless"}

        # Clean data
        occupancySchedulesDicts=[]
        for occupancyScheduleJSON in occupancySchedulesJSON:
            # Identifier
            if prefix not in occupancyScheduleJSON['identifier']:
                occupancyScheduleJSON['identifier']=prefix+occupancyScheduleJSON['identifier']
            # Name
            occupancyScheduleJSON['display_name']='OccupancySchedule_'+occupancyScheduleJSON['display_name']
            # Schedule type limits
            occupancyScheduleJSON['schedule_type_limit']=occupancyScheduleTypeLimitDict
            # Day schedules
            daySchedules=[]
            for daySchedule in occupancyScheduleJSON['day_schedules']:
                # Times
                times=[]
                for time in daySchedule['times']:
                    hour,minute=time[0],time[1]
                    time=(hour,minute)
                    times.append(time)
                daySchedule['times']=times
                daySchedules.append(daySchedule)
            occupancyScheduleJSON['day_schedules']=daySchedules
            # Schedule Rules
            scheduleRules=[]
            for rule in occupancyScheduleJSON['schedule_rules']:
                # Type
                rule['type']='ScheduleRuleAbridged'
                # Date
                rule['start_date']=(rule['start_date'][0],rule['start_date'][1])
                rule['end_date']=(rule['end_date'][0],rule['end_date'][1])
                scheduleRules.append(rule)
            occupancyScheduleJSON['schedule_rules']=scheduleRules
        
            occupancySchedulesDicts.append(occupancyScheduleJSON)

        # Output
        return occupancySchedulesDicts

    @staticmethod
    def HBEquipmentScheduleRulesetDictsByJSONPath(equipmentSchedulePath=None,prefix='EqpSch_'):

        """Get the equipment schedules ruleset dicts for HB by a JSON file compliant with HB APIs for Schedule Rulesets"""

        # Dependencies
        import json
        from honeybee_energy.schedule.ruleset import ScheduleRuleset

        # Read JSON data
        with open(equipmentSchedulePath, 'r') as file:
            equipmentSchedulesJSON = json.load(file)
            if not isinstance(equipmentSchedulesJSON,list):
                equipmentSchedulesJSON=[equipmentSchedulesJSON]

        # Schedule type limit
        equipmentScheduleTypeLimitDict={"type": 'ScheduleTypeLimit',"identifier": 'equipmentScheduleTypeLimit',"display_name": 'Fractional',"lower_limit": 0,"upper_limit": 1,"numeric_type": 'Continuous',"unit_type": "Dimensionless"}

        # Clean data
        equipmentSchedulesDicts=[]
        for equipmentScheduleJSON in equipmentSchedulesJSON:
            # Identifier
            if prefix not in equipmentScheduleJSON['identifier']:
                equipmentScheduleJSON['identifier']=prefix+equipmentScheduleJSON['identifier']
            # Name
            equipmentScheduleJSON['display_name']='EquipmentSchedule_'+equipmentScheduleJSON['display_name']
            # Schedule type limits
            equipmentScheduleJSON['schedule_type_limit']=equipmentScheduleTypeLimitDict
            # Day schedules
            daySchedules=[]
            for daySchedule in equipmentScheduleJSON['day_schedules']:
                # Times
                times=[]
                for time in daySchedule['times']:
                    hour,minute=time[0],time[1]
                    time=(hour,minute)
                    times.append(time)
                daySchedule['times']=times
                daySchedules.append(daySchedule)
            equipmentScheduleJSON['day_schedules']=daySchedules
            # Schedule Rules
            scheduleRules=[]
            for rule in equipmentScheduleJSON['schedule_rules']:
                # Type
                rule['type']='ScheduleRuleAbridged'
                # Date
                rule['start_date']=(rule['start_date'][0],rule['start_date'][1])
                rule['end_date']=(rule['end_date'][0],rule['end_date'][1])
                scheduleRules.append(rule)
            equipmentScheduleJSON['schedule_rules']=scheduleRules
        
            equipmentSchedulesDicts.append(equipmentScheduleJSON)

        # Output
        return equipmentSchedulesDicts

    @staticmethod
    def HBSystemAvailabilityScheduleRulesetDictsByJSONPath(systemAvailabilitySchedulePath=None,prefix='HtnSch_'):

        """Get the systemAvailability schedules ruleset dicts for HB by a JSON file compliant with HB APIs for Schedule Rulesets"""

        # Dependencies
        import json
        from honeybee_energy.schedule.ruleset import ScheduleRuleset

        # Read JSON data
        with open(systemAvailabilitySchedulePath, 'r') as file:
            systemAvailabilitySchedulesJSON = json.load(file)
            if not isinstance(systemAvailabilitySchedulesJSON,list):
                systemAvailabilitySchedulesJSON=[systemAvailabilitySchedulesJSON]

        # Schedule type limit
        systemAvailabilityScheduleTypeLimitDict={"type": 'ScheduleTypeLimit',"identifier": 'availabilityScheduleTypeLimit',"display_name": 'Fractional',"lower_limit": 0,"upper_limit": 1,"numeric_type": 'Continuous',"unit_type": "Dimensionless"}

        # Clean data
        systemAvailabilitySchedulesDicts=[]
        for systemAvailabilityScheduleJSON in systemAvailabilitySchedulesJSON:
            # Identifier
            if prefix not in systemAvailabilityScheduleJSON['identifier']:
                systemAvailabilityScheduleJSON['identifier']=prefix+systemAvailabilityScheduleJSON['identifier']
            # Name
            systemAvailabilityScheduleJSON['display_name']='SystemAvailabilitySchedule_'+systemAvailabilityScheduleJSON['display_name']
            # Schedule type limits
            systemAvailabilityScheduleJSON['schedule_type_limit']=systemAvailabilityScheduleTypeLimitDict
            # Day schedules
            daySchedules=[]
            for daySchedule in systemAvailabilityScheduleJSON['day_schedules']:
                # Times
                times=[]
                for time in daySchedule['times']:
                    hour,minute=time[0],time[1]
                    time=(hour,minute)
                    times.append(time)
                daySchedule['times']=times
                daySchedules.append(daySchedule)
            systemAvailabilityScheduleJSON['day_schedules']=daySchedules
            # Schedule Rules
            scheduleRules=[]
            for rule in systemAvailabilityScheduleJSON['schedule_rules']:
                # Type
                rule['type']='ScheduleRuleAbridged'
                # Date
                rule['start_date']=(rule['start_date'][0],rule['start_date'][1])
                rule['end_date']=(rule['end_date'][0],rule['end_date'][1])
                scheduleRules.append(rule)
            systemAvailabilityScheduleJSON['schedule_rules']=scheduleRules
        
            systemAvailabilitySchedulesDicts.append(systemAvailabilityScheduleJSON)

        # Output
        return systemAvailabilitySchedulesDicts

    @staticmethod
    def HBWindowConstructionsByIFC(ifcFilePath=None,thermalPSets='btwin'):

        """
        Honeybee window constructions (simple glazing) from the thermal properties of the
        IfcWindow, IfcDoor and curtain-wall IfcWall entities. With thermalPSets='btwin' the
        properties are read from the TBIM property set exported by Revit, named 'Other'
        or 'Altro' depending on the language of the Revit installation.
        """

        import ifcopenshell
        import ifcopenshell.util.element
        from honeybee_energy.construction.window import WindowConstruction

        def tbimPSetName(psets):
            return 'Altro' if 'Altro' in psets else 'Other'

        # Initiate empy list
        hbWindowConstructions=[]

        # Load the IFC file
        ifcFile=ifcopenshell.open(ifcFilePath)

        # Get the window construction
        ifcWindows=ifcFile.by_type("ifcWindow")+ifcFile.by_type("ifcDoor")
        hbWindowConstructionNames=[]
        for ifcWindow in ifcWindows:
            ifcWindowPSets=ifcopenshell.util.element.get_psets(ifcWindow)
            try:
                if thermalPSets=='btwin':
                    other=tbimPSetName(ifcWindowPSets)
                    windowUFactor=float(ifcWindowPSets[other]['pr_ThermalTrasmittance'])
                    windowSHGC=float(ifcWindowPSets[other]['pr_SolarTrasmittance'])
                    windowVT=float(ifcWindowPSets[other]['pr_VisibleTrasmittance'])
                elif thermalPSets=='ifc':
                    windowUFactor=float(ifcWindowPSets['Analytical Properties']['Thermal Resistance (R)'])
                    windowSHGC=float(ifcWindowPSets['Analytical Properties']['Solar Heat Gain Coefficient'])
                    windowVT=float(ifcWindowPSets['Analytical Properties']['Visual Light Transmittance'])
                windowConstructionIdentifier='windowConstruction_U'+str(windowUFactor)+'_SHGC'+str(windowSHGC)+'_VT'+str(windowVT) 
                if windowConstructionIdentifier not in hbWindowConstructionNames:
                    hbWindowConstructionNames.append(windowConstructionIdentifier)
                    hbWindowConstruction=WindowConstruction.from_simple_parameters(windowConstructionIdentifier,windowUFactor,windowSHGC,windowVT)
                    hbWindowConstructions.append(hbWindowConstruction)
            except:
                print(f'Impossible to get the constrution of {ifcWindow}')
        
        # Get curtain wall constructions
        ifcWalls=ifcFile.by_type("ifcWall")
        for ifcWall in ifcWalls:
            ifcWallType=ifcopenshell.util.element.get_type(ifcWall)
            ifcWallTypeName=ifcWallType.Name
            try:
                if thermalPSets=='btwin' and 'CurtainWall' in ifcWallTypeName:
                    ifcWindowPSets=ifcopenshell.util.element.get_psets(ifcWall)
                    other=tbimPSetName(ifcWindowPSets)
                    windowUFactor=float(ifcWindowPSets[other]['pr_WindowThermalTrasmittance'])
                    windowSHGC=float(ifcWindowPSets[other]['pr_WindowSolarTrasmittance'])
                    windowVT=float(ifcWindowPSets[other]['pr_WindowVisibleTrasmittance'])
                    windowConstructionIdentifier='curtainWallWindowConstruction_U'+str(windowUFactor)+'_SHGC'+str(windowSHGC)+'_VT'+str(windowVT) 
                    if windowConstructionIdentifier not in hbWindowConstructionNames:
                        hbWindowConstructionNames.append(windowConstructionIdentifier)
                        hbWindowConstruction=WindowConstruction.from_simple_parameters(windowConstructionIdentifier,windowUFactor,windowSHGC,windowVT)
                        hbWindowConstructions.append(hbWindowConstruction)
            except Exception as e:
                print(f'Impossible to get the constrution of {ifcWallTypeName}: {e}')
        
        return hbWindowConstructions


    @staticmethod
    def HBConstructionNamesByhbConstructions(hbOpaqueConstructions=[]):
        """
        Retrieve the names of Honeybee  constructions from a list of  constructions.

        This static method takes in a list of Honeybee constructions and returns a list 
        of their corresponding names. Each construction is expected to have a `display_name` 
        attribute, which is extracted and compiled into the result list.

        Parameters:
        -----------
        hbOpaqueConstructions : list, optional
            A list of Honeybee construction objects. Each object in the list should have 
            a `display_name` attribute. Default is an empty list.

        Returns:
        --------
        list
            A list containing the `display_name` of each construction provided in the 
            `hbOpaqueConstructions` list.

        Example:
        --------
        >>> constructions = [OpaqueConstruction1, OpaqueConstruction2]
        >>> names = ClassName.HBConstructionNamesByhbConstructions(constructions)
        >>> print(names)
        ['Construction 1', 'Construction 2']

        """
        hbOpaqueConstructionNames = []
        for hbOpaqueConstruction in hbOpaqueConstructions:
            hbOpaqueConstructionNames.append(hbOpaqueConstruction.display_name)
        return hbOpaqueConstructionNames


    @staticmethod
    def HBFacesByTopologicZone(tpZone=None,tbimUnits='cm',tpBuilding=None,adiabaticFaceUIDs=[]):

        from topologicpy.Topology import Topology
        from topologicpy.Dictionary import Dictionary
        from topologicpy.Face import Face
        import honeybee
        from topologicpy.CellComplex import CellComplex
        from topologicpy.Wire import Wire
        from ladybug_geometry.geometry3d import  Point3D, Face3D
        from honeybee.face import Face as HBFace
        from honeybee.aperture import Aperture as HBAperture
        from honeybee.door import Door as HBDoor

        # Initaite the HB faces bunding the zone
        hbRoomFaces=[]
        
        # Zone identifier
        zoneDict=Topology.Dictionary(tpZone)
        zoneUID=Dictionary.ValueAtKey(zoneDict,'UID')
        
        # Iterate over the zones
        for tpFace in CellComplex.Faces(tpZone):
            # Set unique face UID (including the zoneUID)
            faceDict=Topology.Dictionary(tpFace)
            faceUID=Dictionary.ValueAtKey(faceDict,'UID')
            
            # Set facetype
            topologicalType=Dictionary.ValueAtKey(faceDict,'pr_TopologicalType')
            HBFaceType=None
            if 'VER' in topologicalType.upper():
                HBFaceType=honeybee.facetype.Wall()
            if 'HOR' in topologicalType.upper():
                 HBFaceType=honeybee.facetype.Floor()
            if 'TOP' in topologicalType.upper():
                 HBFaceType=honeybee.facetype.RoofCeiling()
            # Face geometry
            tpFaceVertices=Wire.Vertices(Face.ExternalBoundary(tpFace))
            if tbimUnits=='m':
                hbRoomFacePoints=[Point3D(float(tpVertex.X()), float(tpVertex.Y()), float(tpVertex.Z())) for tpVertex in tpFaceVertices]
            elif tbimUnits=='cm':
                hbRoomFacePoints=[Point3D(float(tpVertex.X()/100), float(tpVertex.Y()/100), float(tpVertex.Z())/100) for tpVertex in tpFaceVertices]
            else:
                print('Error: please revise this function for other conversions!')
            # HB face
            hbRoomFace = HBFace(f'{faceUID}-{zoneUID}', Face3D(hbRoomFacePoints),type=HBFaceType)
            
            # Apertures
            if 'EXTVER' in topologicalType.upper():
                
                # Initiate emplty lists
                hbRoomApertures=[]
                hbRoomDoors=[]
                hbCurtainWalls=[]
                
                # Aperture UIDs to avoid duplicate apertures
                apertuireUIDs=[]
                
                # Curtain walls
                pr_WallTypeName=Dictionary.ValueAtKey(faceDict,'pr_WallTypeName')
                if 'CURTAIN' in pr_WallTypeName.upper():
                    tpAperture=Topology.Scale(tpFace,origin=Topology.CenterOfMass(tpFace),x=0.9,y=0.9,z=0.9)
                    tpApertureVertices=Wire.Vertices(Face.ExternalBoundary(tpAperture))
                    if tbimUnits=='m':
                        hbRoomAperturePoints=[Point3D(float(tpVertex.X()), float(tpVertex.Y()), float(tpVertex.Z())) for tpVertex in tpApertureVertices]
                    elif tbimUnits=='cm':
                        hbRoomAperturePoints=[Point3D(float(tpVertex.X()/100), float(tpVertex.Y()/100), float(tpVertex.Z())/100) for tpVertex in tpApertureVertices]
                    hbAperture=HBAperture.from_vertices(f'curtainWall-{faceUID}',hbRoomAperturePoints)
                    if f'curtainWall-{faceUID}' not in apertuireUIDs:
                        if faceUID not in adiabaticFaceUIDs: # DEBUG FOR ADIABATIC FACES
                            apertuireUIDs.append(f'curtainWall-{faceUID}')
                            hbCurtainWalls.append(hbAperture)
                    
                # Windows and doors
                tpApertures=Topology.Apertures(tpBuilding,'face')
                for tpAperture in tpApertures:
                    apertureDict=Topology.Dictionary(tpAperture)
                    apertureUID=Dictionary.ValueAtKey(apertureDict,'UID')
                    apertureUUID=Dictionary.ValueAtKey(apertureDict,'uuid')
                    topologicalType=Dictionary.ValueAtKey(apertureDict,'pr_TopologicalType')
                    rl_HasLocation_inFC=Dictionary.ValueAtKey(apertureDict,'rl_HasLocation_inFC')
                    
                    # Windows and doors
                    if topologicalType=='window' or topologicalType=='door':
                        if faceUID==rl_HasLocation_inFC:
                            tpApertureVertices=Wire.Vertices(Face.ExternalBoundary(tpAperture))
                            if tbimUnits=='m':
                                hbRoomAperturePoints=[Point3D(float(tpVertex.X()), float(tpVertex.Y()), float(tpVertex.Z())) for tpVertex in tpApertureVertices]
                            elif tbimUnits=='cm':
                                hbRoomAperturePoints=[Point3D(float(tpVertex.X()/100), float(tpVertex.Y()/100), float(tpVertex.Z())/100) for tpVertex in tpApertureVertices]
                            hbAperture=HBAperture.from_vertices(apertureUID+'-'+apertureUUID,hbRoomAperturePoints)
                            if apertureUID+'-'+apertureUUID not in apertuireUIDs:
                                if faceUID not in adiabaticFaceUIDs: # DEBUG FOR ADIABATIC FACES
                                    apertuireUIDs.append(apertureUID+'-'+apertureUUID)
                                    hbRoomApertures.append(hbAperture)
                             
                # Add apertures     
                if len(hbCurtainWalls)>0:
                    hbRoomFace.add_apertures(hbCurtainWalls)
                if len(hbRoomApertures)>0 and len(hbCurtainWalls)==0:
                    hbRoomFace.add_apertures(hbRoomApertures)
                if len(hbRoomDoors)>0 and len(hbCurtainWalls)==0:
                    hbRoomFace.add_doors(hbRoomDoors)
                    
            # Append
            hbRoomFaces.append(hbRoomFace)
                    
        # Output
        return hbRoomFaces

class Eppy():

    @staticmethod
    def IdfSetRunPeriod(idfFile=None,runPeriodDict={'beginMonth':1,'beginDayOfMonth':1,'endMonth':12,'endDayOfMonth':31,'beginYear':2024,'endYear':2024}):

        """Annual run period starting on Monday, without weather-file holidays and daylight saving"""

        for runPeriod in idfFile.idfobjects['RUNPERIOD']:
            runPeriod.Name='Annual Simulation'
            runPeriod.Begin_Month=runPeriodDict['beginMonth']
            runPeriod.Begin_Day_of_Month=runPeriodDict['beginDayOfMonth']
            runPeriod.Begin_Year=runPeriodDict['beginYear']
            runPeriod.End_Month=runPeriodDict['endMonth']
            runPeriod.End_Day_of_Month=runPeriodDict['endDayOfMonth']
            runPeriod.End_Year=runPeriodDict['endYear']
            runPeriod.Day_of_Week_for_Start_Day='Monday'
            runPeriod.Use_Weather_File_Holidays_and_Special_Days='No'
            runPeriod.Use_Weather_File_Daylight_Saving_Period='No'
            runPeriod.Apply_Weekend_Holiday_Rule='No'
            runPeriod.Use_Weather_File_Rain_Indicators='Yes'
            runPeriod.Use_Weather_File_Snow_Indicators='Yes'
        return idfFile

    @staticmethod
    def IdfTransitionVersion(idfFilePath=None,transitionExePath=None):

        """Converts an IDF in place to the next EnergyPlus version (e.g. 24.1 -> 24.2) with the official transition program"""

        import os
        import subprocess

        updaterFolder=os.path.dirname(transitionExePath)
        subprocess.run([transitionExePath,os.path.abspath(idfFilePath)],cwd=updaterFolder,check=True,capture_output=True)
        for extension in ('.idfold','.idfnew','.VCpErr'):
            leftover=os.path.splitext(idfFilePath)[0]+extension
            if os.path.exists(leftover):
                os.remove(leftover)

    @staticmethod
    def EnergyPlus_RunSimulation(idfFilePath=None,epwFilePath=None,outputPrefix=None,energyPlusExePath=None):

        """
        Runs EnergyPlus (with ExpandObjects and ReadVarsESO) and writes the outputs next to the
        IDF as <outputPrefix>.csv, <outputPrefix>.eio, ... Returns True if the CSV was produced.
        The run happens in a temporary folder because ReadVarsESO fails on paths with non-ASCII
        characters and ExpandObjects writes a shared expanded.idf, which allows parallel runs.
        """

        import os
        import shutil
        import subprocess
        import tempfile

        idfFolder=os.path.dirname(os.path.abspath(idfFilePath))
        if outputPrefix is None:
            outputPrefix=os.path.splitext(os.path.basename(idfFilePath))[0]
        workFolder=tempfile.mkdtemp(prefix=f'ep_{outputPrefix}_')
        # ReadVarsESO looks for the .rvi next to the input IDF, so the IDF is copied there
        workIdf=os.path.join(workFolder,f'in_{outputPrefix}.idf')
        shutil.copy(idfFilePath,workIdf)
        result=subprocess.run(
            [str(energyPlusExePath),'-w',str(epwFilePath),'-d',workFolder,'-p',outputPrefix,'-s','C','-x','-r',workIdf],
            capture_output=True,text=True,cwd=workFolder)
        for fileName in os.listdir(workFolder):
            if fileName.startswith(outputPrefix):
                shutil.move(os.path.join(workFolder,fileName),os.path.join(idfFolder,fileName))
        shutil.rmtree(workFolder,ignore_errors=True)
        return result.returncode==0 and os.path.exists(os.path.join(idfFolder,f'{outputPrefix}.csv'))

    @staticmethod
    def IdfPurgeUnusedConstruction(idfFile=None):
        usedConstructionNames=[]
        for idfSurface in idfFile.idfobjects["BUILDINGSURFACE:DETAILED"]: 
            constructionName=idfSurface.Construction_Name
            if constructionName not in usedConstructionNames:
                usedConstructionNames.append(constructionName)
        for idfSurface in idfFile.idfobjects["FENESTRATIONSURFACE:DETAILED"]: 
            constructionName=idfSurface.Construction_Name
            if constructionName not in usedConstructionNames:
                usedConstructionNames.append(constructionName)
        unusedConstructions=[]
        allConstructions=idfFile.idfobjects["CONSTRUCTION"]
        for construction in allConstructions:
            constructionName=construction.Name
            if constructionName not in usedConstructionNames:
                unusedConstructions.append(construction)
        for unusedConstruction in unusedConstructions:
            idfFile.removeidfobject(unusedConstruction)
        return idfFile
    
    @staticmethod
    def IdfScheduleCompactByHBScheduleRulesetDict(hbScheduleRulesetDict=None,idfFile=None):

        """
        hbScheduleRulesetDict: honeybee schedule ruleset as dictionaries
        idfFile: Energy Plus IDF file in Python
        """

        # CREATE SCHEDULE
        # Initiate IDF schedule compact
        idfScheduleCompact=idfFile.newidfobject("SCHEDULE:COMPACT")
        idfScheduleCompact.Name=hbScheduleRulesetDict['identifier']
        idfScheduleCompact.Schedule_Type_Limits_Name=hbScheduleRulesetDict['schedule_type_limit']['identifier']
        # Field values
        idfScheduleCompactFields=[]
        t=None
        for rule in hbScheduleRulesetDict['schedule_rules']:

            # Schedule day
            scheduleDayIdentifier=rule['schedule_day']

            # Through:
            month,day=rule['end_date'][0],rule['end_date'][1]
            through=f"Through: {month}/{day}"
            if through!=t:
                idfScheduleCompactFields.append(through)

            # For:
            forDayType = 'For: '
            if 'monday' in scheduleDayIdentifier:
                forDayType+='Monday'
            elif 'tuesday' in scheduleDayIdentifier:
                forDayType+='Tuesday'    
            elif 'wednesday' in scheduleDayIdentifier:
                forDayType+='Wednesday'
            elif 'thursday' in scheduleDayIdentifier:
                forDayType+='Thursday'
            elif 'friday' in scheduleDayIdentifier:
                forDayType+='Friday'    
            elif 'saturday' in scheduleDayIdentifier:
                forDayType+='Saturday'  
            elif 'closure' in scheduleDayIdentifier:
                forDayType+='AllDays'  
            elif 'session' in scheduleDayIdentifier:
                forDayType+='Weekdays' 
            if forDayType == 'For: ':
                forDayType+='AllDays'
                          
            idfScheduleCompactFields.append(forDayType)
            
            # Until: , Value
            if True:
                for hbScheduleDay in hbScheduleRulesetDict['day_schedules']:
                    if hbScheduleDay['identifier']==scheduleDayIdentifier:
                        j=0
                        times,values=hbScheduleDay['times'],hbScheduleDay['values']
                        if sum(values)==0:
                            idfScheduleCompactFields.append('Until: 24:00')
                            idfScheduleCompactFields.append(0.00)
                        else:
                            for time in times:
                                if time[0]!=0:
                                    idfScheduleCompactFields.append(f'Until: {time[0]}:00')
                                    value=values[j]
                                    if value>hbScheduleRulesetDict['schedule_type_limit']['upper_limit']:
                                        value=hbScheduleRulesetDict['schedule_type_limit']['upper_limit']
                                    elif value<hbScheduleRulesetDict['schedule_type_limit']['lower_limit']:
                                        value=hbScheduleRulesetDict['schedule_type_limit']['lower_limit']
                                    idfScheduleCompactFields.append(value)
                                    j+=1
                            if times[-1][0]!=23 or times[-1][0]!=24:
                                idfScheduleCompactFields.append('Until: 24:00')
                                idfScheduleCompactFields.append(0.00)
            
            # For: AllOtherDays (exam session)
            if 'session' in scheduleDayIdentifier:
                idfScheduleCompactFields.append('For: AllOtherDays')
                idfScheduleCompactFields.append('Until: 24:00')
                idfScheduleCompactFields.append(0.00)

            # Update the loop
            t=through

        # Set fields
        i=1
        for idfScheduleCompactField in idfScheduleCompactFields:
            field=f'Field_{i}'
            idfScheduleCompact[field]=idfScheduleCompactField
            i+=1

        # Output
        return idfFile

    @staticmethod
    def IdfSetScheduleTypeLimits(idfFile=None,scheduleTypeLimits=[]):
        idfScheduleTypeLimitsNames=[]
        for idfScheduleTypeLimit in idfFile.idfobjects['ScheduleTypeLimits']:
            idfScheduleTypeLimitsNames.append(idfScheduleTypeLimit['Name'])
        for scheduleTypeLimit in scheduleTypeLimits:
            if scheduleTypeLimit['identifier'] not in idfScheduleTypeLimitsNames:
                idfScheduleTypeLimit = idfFile.newidfobject("ScheduleTypeLimits")
                idfScheduleTypeLimit['Name']=scheduleTypeLimit['identifier']
                idfScheduleTypeLimit['Lower_Limit_Value']=scheduleTypeLimit['lower_limit']
                idfScheduleTypeLimit['Upper_Limit_Value']=scheduleTypeLimit['upper_limit']
                idfScheduleTypeLimit['Numeric_Type']=scheduleTypeLimit['numeric_type']
                idfScheduleTypeLimit['Unit_Type']=scheduleTypeLimit['unit_type']
        return idfFile

    @staticmethod
    def IdfSetOutputVariables(idfFile=None,outputVariables=[],reportingFrequency=None):
        for outputVariable in outputVariables:
            idfOutputVariable = idfFile.newidfobject("OUTPUT:VARIABLE")
            idfOutputVariable.Variable_Name = outputVariable 
            idfOutputVariable.Reporting_Frequency = reportingFrequency  
            idfOutputVariable.Key_Value = "*"
        return idfFile
    
    @staticmethod
    def IdfSetConstructionsAndMaterials(idfFile=None,hbOpaqueConstructions=[],hbWindowConstructions=[]):

        "Put the CONSTRUCTION and MATERIAL objects in the IDF file"
        
        # Add opaque constructions and materials to IDF
        HBMaterials,HBConstructions=[],[]
        for hbOpaqueConstruction in hbOpaqueConstructions:
            if hbOpaqueConstruction not in HBConstructions:
                HBConstructions.append(hbOpaqueConstruction)
                hbOpaqueConstructionMaterials=hbOpaqueConstruction.materials
                for hbOpaqueConstructionMaterial in hbOpaqueConstructionMaterials:
                    if hbOpaqueConstructionMaterial not in HBMaterials:
                        HBMaterials.append(hbOpaqueConstructionMaterial)         
        # Materials
        HBMaterials=list(set(HBMaterials))
        for HBMaterial in HBMaterials:
            idfMaterial=idfFile.newidfobject("MATERIAL") 
            idfMaterial.Name=HBMaterial.identifier
            idfMaterial.Roughness=HBMaterial.roughness
            idfMaterial.Thickness=HBMaterial.thickness
            idfMaterial.Conductivity=HBMaterial.conductivity
            idfMaterial.Density=HBMaterial.density
            idfMaterial.Specific_Heat=HBMaterial.specific_heat
            idfMaterial.Thermal_Absorptance=HBMaterial.thermal_absorptance
            idfMaterial.Solar_Absorptance=HBMaterial.solar_absorptance
            idfMaterial.Visible_Absorptance=HBMaterial.visible_absorptance
        # Constructions
        for HBConstruction in HBConstructions:
            idfConstruction=idfFile.newidfobject("CONSTRUCTION")
            idfConstruction.Name=HBConstruction.display_name
            j=0
            for key in ['Outside_Layer','Layer_2','Layer_3','Layer_4','Layer_5','Layer_6','Layer_7','Layer_8','Layer_9','Layer_10']:
                try:
                    idfConstruction[key]=f'{HBConstruction.materials[j].display_name}-{HBConstruction.materials[j].thickness}'
                except:
                    continue
                j+=1
            
        # Add window constructions and simple glazing materials to IDF
        HBMaterials,HBConstructions=[],[]
        for hbWindowConstruction in hbWindowConstructions:
            if hbWindowConstruction not in HBConstructions:
                HBConstructions.append(hbWindowConstruction)
                hbWindowMaterials=hbWindowConstruction.materials
                for hbWindowMaterial in hbWindowMaterials:
                    if hbWindowMaterial not in HBMaterials:
                        HBMaterials.append(hbWindowMaterial)
        # Materials
        for HBMaterial in HBMaterials:
            idfMaterial=idfFile.newidfobject("WINDOWMATERIAL:SIMPLEGLAZINGSYSTEM") 
            idfMaterial.Name=HBMaterial.display_name
            idfMaterial.UFactor=HBMaterial.u_factor
            idfMaterial.Solar_Heat_Gain_Coefficient=HBMaterial.shgc
            idfMaterial.Visible_Transmittance=HBMaterial.vt
        # Constructions
        for HBConstruction in HBConstructions:
            idfConstruction=idfFile.newidfobject("CONSTRUCTION")
            idfConstruction.Name=HBConstruction.display_name
            idfConstruction.Outside_Layer=HBConstruction.materials[0].display_name

        return idfFile

    @staticmethod
    def IdfSetFaceConstructions(idfFile=None,tpBuilding=None,hbOpaqueConstructionNames=[]):
        # Dependencies
        from topologicpy.CellComplex import CellComplex
        from topologicpy.Topology import Topology
        from topologicpy.Dictionary import Dictionary
        # Set face constructions 
        tpFaceUIDs,tpFaces=[],[]
        for tpFace in CellComplex.Faces(tpBuilding):
            d=Topology.Dictionary(tpFace)
            rl_HasLocation_tpZN=Dictionary.ValueAtKey(d,'rl_HasLocation_tpZN')
            faceUID=Dictionary.ValueAtKey(d,'UID')
            for rl in rl_HasLocation_tpZN:
                tpFaceUIDs.append(f'{faceUID}-{rl}')
                tpFaces.append(tpFace)
        idfSurfaces=idfFile.idfobjects["BuildingSurface:Detailed"]
        for idfSurface in idfSurfaces:
            idfSurfaceName=idfSurface.Name
            try:
                index=tpFaceUIDs.index(idfSurfaceName)
                hbConstructionName=Dictionary.ValueAtKey(Topology.Dictionary(tpFaces[index]),'HBConstructionName')
                if hbConstructionName is not None and hbConstructionName in hbOpaqueConstructionNames:
                    idfSurface.Construction_Name=hbConstructionName                
            except:
                continue
        return idfFile


    @staticmethod
    def IdfSetWindowConstructions(idfFile=None,tpBuilding=None,hbWindowConstructionNames=[]):
        # Dependencies
        from topologicpy.Dictionary import Dictionary
        from topologicpy.Topology import Topology

        tpApertureUIDs,tpApertures=[],[]
        for tpAperture in Topology.Apertures(tpBuilding,'face'):
            d=Topology.Dictionary(tpAperture)
            topologicalType=Dictionary.ValueAtKey(d,'pr_TopologicalType')
            if topologicalType=='window' or topologicalType=='door':
                apertureUID=Dictionary.ValueAtKey(d,'UID')
                apertureUUID=Dictionary.ValueAtKey(d,'uuid')
                tpApertureUIDs.append(f'{apertureUID}-{apertureUUID}')
                tpApertures.append(tpAperture)
        idfSurfaces=idfFile.idfobjects["FenestrationSurface:Detailed"]
        for idfSurface in idfSurfaces:
            idfSurfaceName=idfSurface.Name
            if idfSurfaceName in tpApertureUIDs:
                index=tpApertureUIDs.index(idfSurfaceName)
                tpAperture=tpApertures[index]
                d=Topology.Dictionary(tpAperture)
                pr_ThermalTrasmittance=Dictionary.ValueAtKey(d,'pr_ThermalTrasmittance')
                pr_SolarTrasmittance=Dictionary.ValueAtKey(d,'pr_SolarTrasmittance')
                pr_VisibleTrasmittance=Dictionary.ValueAtKey(d,'pr_VisibleTrasmittance')
                hbConstructionName=f'windowConstruction_U{pr_ThermalTrasmittance}_SHGC{pr_SolarTrasmittance}_VT{pr_VisibleTrasmittance}'
                # Debug
                if hbConstructionName not in hbWindowConstructionNames:
                    hbConstructionName=hbWindowConstructionNames[0]
                # Set
                idfSurface.Construction_Name=hbConstructionName 
        return idfFile

    @staticmethod
    def IdfSetCurtainWallConstructions(idfFile=None,tpBuilding=None,hbWindowConstructionNames=[]):
            
        # Dependencies
        from topologicpy.Dictionary import Dictionary
        from topologicpy.Topology import Topology
        from topologicpy.CellComplex import CellComplex

        tpFaceUIDs,tpFaces=[],[]
        for tpFace in CellComplex.Faces(tpBuilding):
            d=Topology.Dictionary(tpFace)
            if 'EXTVER' in Dictionary.ValueAtKey(d,'pr_TopologicalType').upper():
                if 'CURTAIN' in Dictionary.ValueAtKey(d,'pr_WallTypeName').upper():
                    tpFaceUIDs.append(Dictionary.ValueAtKey(d,'UID'))
                    tpFaces.append(tpFace)
        idfSurfaces=idfFile.idfobjects["FenestrationSurface:Detailed"]
        for idfSurface in idfSurfaces:
            idfSurfaceName=idfSurface.Name
            if 'CURTAIN' in idfSurfaceName.upper():
                idfSurfaceName=idfSurfaceName.split("-")[1]
                if idfSurfaceName in tpFaceUIDs:
                    index=tpFaceUIDs.index(idfSurfaceName)
                    tpFace=tpFaces[index]
                    d=Topology.Dictionary(tpFace)
                    U=Dictionary.ValueAtKey(d,'pr_WindowThermalTrasmittance')
                    SHGC=Dictionary.ValueAtKey(d,'pr_WindowSolarTrasmittance')
                    VT=Dictionary.ValueAtKey(d,'pr_WindowVisibleTrasmittance')
                    hbConstructionName=f'curtainWallWindowConstruction_U{U}_SHGC{SHGC}_VT{VT}'
                    if hbConstructionName in hbWindowConstructionNames:
                        idfSurface.Construction_Name=hbConstructionName  

        return idfFile

    @staticmethod
    def DigitManOutputVariables():
        outputVariables=[
            'Zone Ideal Loads Zone Total Heating Energy',
            'Zone Ideal Loads Zone Total Cooling Energy',
            'Zone Electric Equipment Electricity Energy',
            'Zone Lights Electricity Energy',
            'Zone People Occupant Count'
            ]
        return outputVariables
    
class TBIM():

    @staticmethod
    def Cells_CleanUndefinedData(
        tpBuilding=None,
        undefinedPropertyNames=[
            'pr_OccupancyDensityOperation',
            'pr_EquipmentPowerDensity',
            'pr_MechanicalVentilationRate',
            'pr_MechanicalVentilationRatePerPerson',
            'pr_MechanicalVentilationRatePerVolume',
            'pr_SpaceTemperatureSummerMax',
            'pr_SpaceTemperatureSummerMin',
            'pr_SpaceTemperatureWinterMax',
            'pr_SpaceTemperatureWinterMin',
            'pr_HumidityMax',
            'pr_HumidityMin'
        ]
    ):

        # Dependencies
        from topologicpy.CellComplex import CellComplex
        from topologicpy.Dictionary import Dictionary
        from topologicpy.Topology import Topology
    
        # Clean undefined data
        for tpCell in CellComplex.Cells(tpBuilding):
            d=Topology.Dictionary(tpCell)
            for undefinedPropertyName in undefinedPropertyNames:
                undefinedPropertyValue=Dictionary.ValueAtKey(d,undefinedPropertyName)
                if undefinedPropertyValue=='Undefined' or undefinedPropertyValue is None:
                    newValue=0
                    if undefinedPropertyName=='pr_SpaceTemperatureSummerMax':
                        newValue=30
                    elif undefinedPropertyName=='pr_SpaceTemperatureSummerMin':
                        newValue=28
                    elif undefinedPropertyName=='pr_SpaceTemperatureWinterMax':
                        newValue=16
                    elif undefinedPropertyName=='pr_SpaceTemperatureWinterMin':
                        newValue=10
                    elif undefinedPropertyName=='pr_HumidityMax':
                        newValue=100
                    d=Dictionary.SetValueAtKey(d,undefinedPropertyName,newValue)
                    tpCell=Topology.SetDictionary(tpCell,d)

        # Output
        return tpBuilding
        

    @staticmethod
    def Cells_ClusterizeIntoEnergyZones(
        n_clusters=6,
        tpBuilding=None,
        kmeansPropertyNames=['UID','pr_IsOccupied','pr_IsHeated','pr_IsCooled','pr_OccupancyDensityOperation'],
        singleZoneOccupancyTypes=['EducationandTrainingSpaces:LectureHall(FixedSeats)','EducationandTrainingSpaces:Research/Non-ClassClassLaboratory'],
        notUsefullCellUIDs=[]):
    
        """
        Groups the cells of a TBIM into thermal zones: cells are clustered with K-Means on the
        kmeansPropertyNames attributes, then the clusters are split per storey and into groups
        of adjacent cells. Cells of the singleZoneOccupancyTypes form a zone on their own;
        stairways, elevators and horizontal infrastructures join the adjacent corridor (or
        restroom) zone; notUsefullCellUIDs are excluded from the energy model. Zones are
        finally renamed zone00, zone01, ... The zone of each cell is stored in its
        'rl_HasLocation_tpZN' dictionary key.
        """

        # Import external libraries
        from topologicpy.CellComplex import CellComplex
        from topologicpy.Dictionary import Dictionary
        from topologicpy.Topology import Topology

        import pandas as pd
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler

        # Helper function

        def AdjacencyGroupsByAdjacencyPairs(adjacency_pairs):
    
            # Initialize a list to store groups
            adjacency_groups = []

            # Function to find the group a cell belongs to
            def find_group(cell, groups):
                for group in groups:
                    if cell in group:
                        return group
                return None

            # Loop through each adjacency pair to form groups
            for pair in adjacency_pairs:
                cell1, cell2 = pair
                group1 = find_group(cell1, adjacency_groups)
                group2 = find_group(cell2, adjacency_groups)

                if group1 and group2:
                    if group1 != group2:
                        # Merge two groups if they are different
                        group1.update(group2)
                        adjacency_groups.remove(group2)
                elif group1:
                    group1.add(cell2)
                elif group2:
                    group2.add(cell1)
                else:
                    adjacency_groups.append(set(pair))

            # Number of adjacency groups
            adjacency_groups
        
            return adjacency_groups

        # Get all the cells to be clustered
        tpCells=CellComplex.Cells(tpBuilding)

        # Data to be clustered
        kmeansData=[]
        for tpCell in tpCells:
            d=Topology.Dictionary(tpCell)
            kmeansValues={}
            for key in kmeansPropertyNames:
                kmeansValues[key]=Dictionary.ValueAtKey(d,key)
            kmeansData.append(kmeansValues)
        
        # Clean data to be clustered
        kmeansDF = pd.DataFrame(kmeansData)
        kmeansDF = kmeansDF.drop_duplicates()
        try:
            kmeansDF['pr_OccupancyDensityOperation'] = pd.to_numeric(kmeansDF['pr_OccupancyDensityOperation'], errors='coerce')
            kmeansDF['pr_OccupancyDensityOperation'] = kmeansDF['pr_OccupancyDensityOperation'].fillna(kmeansDF['pr_OccupancyDensityOperation'].mean())
        except:
            print('pr_OccupancyDensityOperation not found!')
        kmeansDF_features = kmeansDF.drop(columns=['UID'])

        # Standardize the features before applying KMeans
        scaler = StandardScaler()
        kmeansDF_features_scaled = scaler.fit_transform(kmeansDF_features)

        # Apply KMeans clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=14, n_init=10)  # n_init=10: default of scikit-learn < 1.4 used in the paper  
        kmeansDF['Cluster'] = kmeans.fit_predict(kmeansDF_features_scaled)

        # Set KMeans clusters
        for tpCell in tpCells:
            # Cell's basic data
            d=Topology.Dictionary(tpCell)
            cellUID=Dictionary.ValueAtKey(Topology.Dictionary(tpCell),'UID')
            # Set dictionary
            for index, row in kmeansDF.iterrows():
                if cellUID==row['UID']:
                    cellCluster=row['Cluster']
            newD=Dictionary.ByKeyValue('cellCluster',cellCluster)
            newD=Dictionary.ByMergedDictionaries([d,newD])
            tpCell=Topology.SetDictionary(tpCell,newD)

        # Assign zones by KMeans clusters
        for tpCell in CellComplex.Cells(tpBuilding):
            # Cell's data
            d=Topology.Dictionary(tpCell)
            cellUID=Dictionary.ValueAtKey(d,'UID')
            pr_OccupancyType=Dictionary.ValueAtKey(d,'pr_OccupancyType')
            clusterUID=Dictionary.ValueAtKey(d,'cellCluster')
            # Zones with single cell
            if pr_OccupancyType in singleZoneOccupancyTypes:
                zoneUID=cellUID
            # Zone with multiple cells
            else:
                storeyUID=Dictionary.ValueAtKey(d,'rl_HasLocation_tpBS')
                if storeyUID is None:
                    storeyUID='noneStorey'
                zoneUID=storeyUID+'-cluster'+str(clusterUID)
            # Set dictionary
            newD=Dictionary.ByKeyValue('rl_HasLocation_tpZN',zoneUID)
            newD=Dictionary.ByMergedDictionaries([d,newD])
            tpCell=Topology.SetDictionary(tpCell,newD)
        
        # Merge stairways and elevators to corridors
        for tpCell in CellComplex.Cells(tpBuilding):
            # Cell's data
            d=Topology.Dictionary(tpCell)
            cellUID=Dictionary.ValueAtKey(d,'UID')
            pr_OccupancyType=Dictionary.ValueAtKey(d,'pr_OccupancyType')
            if pr_OccupancyType is None:
                print(f'{cellUID} occupancy type is None here, assuming it is a storage')
                pr_OccupancyType='StorageSpaces:GeneralStorageSpace'
            # Cell's relationships
            rl_HasLocation_tpBS=Dictionary.ValueAtKey(d,'rl_HasLocation_tpBS')
            if rl_HasLocation_tpBS is None:
                rl_HasLocation_tpBS='noneStorey'
            # Assign new zone by adjacent cells
            if 'STAIR' in pr_OccupancyType.upper() or 'ELEVATOR' in pr_OccupancyType.upper():
                # Adjacent cells
                adjCells=Topology.AdjacentTopologies(topology=tpCell,topologyType='cell',hostTopology=tpBuilding)
                for adjCell in adjCells:
                    # Adjacent cell's data
                    adjCellDict=Topology.Dictionary(adjCell)
                    adjCell_pr_OccupancyType=Dictionary.ValueAtKey(adjCellDict,'pr_OccupancyType')
                    adjCell_rl_HasLocation_tpBS=Dictionary.ValueAtKey(adjCellDict,'rl_HasLocation_tpBS')
                    adjCell_rl_HasLocation_tpZN=Dictionary.ValueAtKey(adjCellDict,'rl_HasLocation_tpZN')
                    # Set the same zone of adjacent corridor
                    if rl_HasLocation_tpBS==adjCell_rl_HasLocation_tpBS and 'CORRIDOR' in adjCell_pr_OccupancyType.upper():
                        rl_HasLocation_tpZN=adjCell_rl_HasLocation_tpZN
                        d=Dictionary.SetValueAtKey(d,key='rl_HasLocation_tpZN',value=rl_HasLocation_tpZN)
                        tpCell=Topology.SetDictionary(tpCell,d)
                    
        # Merge horizontal infrastructures to corridors and stairways
        for tpCell in CellComplex.Cells(tpBuilding):
            # Cell's data
            d=Topology.Dictionary(tpCell)
            cellUID=Dictionary.ValueAtKey(d,'UID')
            pr_OccupancyType=Dictionary.ValueAtKey(d,'pr_OccupancyType')
            # Cell's relationships
            rl_HasLocation_tpBS=Dictionary.ValueAtKey(d,'rl_HasLocation_tpBS')
            if rl_HasLocation_tpBS is None:
                rl_HasLocation_tpBS='noneStorey'
            # Assign new zone by adjacent cells
            if 'HorizontalInfrastructure' in pr_OccupancyType:
                adjCells=Topology.AdjacentTopologies(topology=tpCell,topologyType='cell',hostTopology=tpBuilding)
                for adjCell in adjCells:
                    # Adjacent cell's data
                    adjCellDict=Topology.Dictionary(adjCell)
                    adjCell_pr_OccupancyType=Dictionary.ValueAtKey(adjCellDict,'pr_OccupancyType')
                    adjCell_rl_HasLocation_tpBS=Dictionary.ValueAtKey(adjCellDict,'rl_HasLocation_tpBS')
                    adjCell_rl_HasLocation_tpZN=Dictionary.ValueAtKey(adjCellDict,'rl_HasLocation_tpZN')
                    if rl_HasLocation_tpBS==adjCell_rl_HasLocation_tpBS:
                        # Set the same zone of adjacent corridor or stairway
                        if 'CORRIDOR' in adjCell_pr_OccupancyType.upper() or 'STAIRWAY' in adjCell_pr_OccupancyType.upper():
                            rl_HasLocation_tpZN=adjCell_rl_HasLocation_tpZN
                            d=Dictionary.SetValueAtKey(d,key='rl_HasLocation_tpZN',value=rl_HasLocation_tpZN)
                            tpCell=Topology.SetDictionary(tpCell,d)
                        
        # Merge horizontal infrastructures to restrooms
        for tpCell in CellComplex.Cells(tpBuilding):
            # Cell's data
            d=Topology.Dictionary(tpCell)
            cellUID=Dictionary.ValueAtKey(d,'UID')
            pr_OccupancyType=Dictionary.ValueAtKey(d,'pr_OccupancyType')
            # Cell's relationships
            rl_HasLocation_tpBS=Dictionary.ValueAtKey(d,'rl_HasLocation_tpBS')
            if rl_HasLocation_tpBS is None:
                rl_HasLocation_tpBS='noneStorey'
            # Assign new zone by adjacent cells
            if 'HorizontalInfrastructure' in pr_OccupancyType:
                adjCells=Topology.AdjacentTopologies(topology=tpCell,topologyType='cell',hostTopology=tpBuilding)
                for adjCell in adjCells:
                    # Adjacent cell's data
                    adjCellDict=Topology.Dictionary(adjCell)
                    adjCell_pr_OccupancyType=Dictionary.ValueAtKey(adjCellDict,'pr_OccupancyType')
                    adjCell_rl_HasLocation_tpBS=Dictionary.ValueAtKey(adjCellDict,'rl_HasLocation_tpBS')
                    adjCell_rl_HasLocation_tpZN=Dictionary.ValueAtKey(adjCellDict,'rl_HasLocation_tpZN')
                    if rl_HasLocation_tpBS==adjCell_rl_HasLocation_tpBS:
                        # Set the same zone of adjacent corridor or stairway
                        if 'RESTROOM' in adjCell_pr_OccupancyType.upper():
                            rl_HasLocation_tpZN=adjCell_rl_HasLocation_tpZN
                            d=Dictionary.SetValueAtKey(d,key='rl_HasLocation_tpZN',value=rl_HasLocation_tpZN)
                            tpCell=Topology.SetDictionary(tpCell,d)
        
        # Unassign zones to cells not useful in the energy model
    
        for tpCell in CellComplex.Cells(tpBuilding):
            # Cell's data
            d=Topology.Dictionary(tpCell)
            cellUID=Dictionary.ValueAtKey(d,'UID')
            # Cell's relationships
            if cellUID in notUsefullCellUIDs:
                d=Dictionary.SetValueAtKey(d,'rl_HasLocation_tpZN',None)
                tpCell=Topology.SetDictionary(tpCell,d)
            
        # Get all the zone UIDs
        zoneUIDs=[]
        for tpCell in CellComplex.Cells(tpBuilding):
            rl_HasLocation_tpZN=Dictionary.ValueAtKey(Topology.Dictionary(tpCell),'rl_HasLocation_tpZN')
            if rl_HasLocation_tpZN is not None:
                zoneUIDs.append(rl_HasLocation_tpZN)
        zoneUIDs=sorted(list(set(zoneUIDs)))

        # Group the cells belonging to the same zone
        zoneUIDsDict={}
        for zoneUID in zoneUIDs:
            zoneUIDsDict[zoneUID]=[]
        for tpCell in CellComplex.Cells(tpBuilding):
            # Cell's data
            d=Topology.Dictionary(tpCell)
            cellUID=Dictionary.ValueAtKey(d,'UID')
            # Cell's relationships
            rl_HasLocation_tpZN=Dictionary.ValueAtKey(d,'rl_HasLocation_tpZN')
            # Append cells
            if rl_HasLocation_tpZN is not None:
                zoneUIDsDict[rl_HasLocation_tpZN].append(tpCell)

        # Find adjacency groups in zone clusters
        for zoneUID in zoneUIDs:
        
            # Find adjacency pairs
            adjacency_pairs=[]
            zoneCells=zoneUIDsDict[zoneUID]
            if len(zoneCells)>2:
                zoneCellsUIDs=[Dictionary.ValueAtKey(Topology.Dictionary(tpCell),'UID') for tpCell in zoneCells]
                for tpCell in zoneCells:
                    cellUID=Dictionary.ValueAtKey(Topology.Dictionary(tpCell),'UID')
                    adjCells=Topology.AdjacentTopologies(hostTopology=tpBuilding,topology=tpCell,topologyType='cell')
                    for adjCell in adjCells:
                        adjCellUID=Dictionary.ValueAtKey(Topology.Dictionary(adjCell),'UID')
                        if adjCellUID in zoneCellsUIDs:
                            adjacency_pairs.append((cellUID,adjCellUID))
        
                # Get adjacncy groups
                adjacencyGorups=AdjacencyGroupsByAdjacencyPairs(adjacency_pairs)   

                # Assign adjacency group to cells in zone
                for tpCell in zoneCells:
                    d=Topology.Dictionary(tpCell)
                    cellUID=Dictionary.ValueAtKey(d,'UID')
                    i=0
                    for adjacencyGorup in adjacencyGorups:
                        if cellUID in adjacencyGorup:
                            rl_HasLocation_tpZN=Dictionary.ValueAtKey(d,'rl_HasLocation_tpZN')+'-'+str(i)
                            d=Dictionary.SetValueAtKey(d,'rl_HasLocation_tpZN',rl_HasLocation_tpZN)
                            tpCell=Topology.SetDictionary(tpCell,d)
                        i+=1

        # Rename the zones
        zoneUIDs=[]
        for tpCell in CellComplex.Cells(tpBuilding):
            rl_HasLocation_tpZN=Dictionary.ValueAtKey(Topology.Dictionary(tpCell),'rl_HasLocation_tpZN')
            if rl_HasLocation_tpZN is not None:
                zoneUIDs.append(rl_HasLocation_tpZN)
        zoneUIDs=sorted(list(set(zoneUIDs)))
        newZoneUIDs=[]
        for i in range(0,len(zoneUIDs)):
            if i<10:
                j='0'+str(i)
            else:
                j=str(i)
            newZoneUIDs.append('zone'+j)
        for tpCell in CellComplex.Cells(tpBuilding):
            d=Topology.Dictionary(tpCell)
            rl_HasLocation_tpZN=Dictionary.ValueAtKey(d,'rl_HasLocation_tpZN')
            if rl_HasLocation_tpZN is not None:
                index=zoneUIDs.index(rl_HasLocation_tpZN)
                new_rl_HasLocation_tpZN=newZoneUIDs[index]
                d=Dictionary.SetValueAtKey(d,'rl_HasLocation_tpZN',new_rl_HasLocation_tpZN)
                tpCell=Topology.SetDictionary(tpCell,d)

        return tpBuilding


    @staticmethod
    def Faces_SetHBConstructionName(tpBuilding=None):

        # Import libraries
        from topologicpy.CellComplex import CellComplex
        from topologicpy.Dictionary import Dictionary
        from topologicpy.Topology import Topology

        # Assign HB construction type names to the faces
        for tpFace in CellComplex.Faces(tpBuilding):
            d=Topology.Dictionary(tpFace)
            pr_TopologicalType=Dictionary.ValueAtKey(d,'pr_TopologicalType')
            constructionName=None
            if pr_TopologicalType=='extVer':
                constructionName=Dictionary.ValueAtKey(d,'pr_WallTypeName')
            elif pr_TopologicalType=='intVer':
                constructionName=Dictionary.ValueAtKey(d,'pr_WallTypeName')
            elif pr_TopologicalType=='topHor':
                constructionName=Dictionary.ValueAtKey(d,'pr_RoofTypeName')
            elif pr_TopologicalType=='botHor':
                constructionName=Dictionary.ValueAtKey(d,'pr_FloorTypeName')
            elif pr_TopologicalType=='intHor':
                constructionName=Dictionary.ValueAtKey(d,'pr_FloorTypeName')
            if constructionName is not None:
                newD=Dictionary.ByKeysValues(['HBConstructionName'],[constructionName])
                newD=Dictionary.ByMergedDictionaries([d,newD])
                tpFace=Topology.SetDictionary(tpFace,newD)

        # Output
        return tpBuilding
    


    @staticmethod
    def EnergyZones(tpBuilding=None):

        "Return the enrgy zones as Topologic cell complexes"

        # Dependencies
        from topologicpy.CellComplex import CellComplex
        from topologicpy.Topology import Topology
        from topologicpy.Dictionary import Dictionary
        
        # Gruop and merge cells into the same zones
        tpZones=[]
        groupedCells = {}
        for tpCell in CellComplex.Cells(tpBuilding):
            d=Topology.Dictionary(tpCell)
            hasLocationZone=Dictionary.ValueAtKey(d,'rl_HasLocation_tpZN')
            if hasLocationZone is not None:
                if hasLocationZone in groupedCells:
                    groupedCells[hasLocationZone].append(tpCell)
                else:
                    groupedCells[hasLocationZone] = [tpCell]
        for zoneUID in groupedCells:
            zoneCells=groupedCells[zoneUID]
            tpZone=CellComplex.ByCells(zoneCells)
            
            if tpZone is not None:
                d=Dictionary.ByKeysValues(['UID'],[zoneUID])
                tpZone=Topology.SetDictionary(tpZone,d)
                tpZones.append(tpZone)
                
            # Debug
            else:
                j=0
                for zoneCell in zoneCells:
                    tpZone=CellComplex.ByCells([zoneCell])
                    d=Dictionary.ByKeysValues(['UID'],[zoneUID+'-'+str(j)])
                    tpZone=Topology.SetDictionary(tpZone,d)
                    tpZones.append(tpZone)
                    j+=1
            
        return tpZones

    @staticmethod
    def Faces_SetZoneRelationships(tpBuilding=None,tpZones=[]):
        # Dependencies
        from topologicpy.CellComplex import CellComplex
        from topologicpy.Topology import Topology
        from topologicpy.Dictionary import Dictionary
        # Set zone-face relationship

        if True:
            for tpFace in CellComplex.Faces(tpBuilding):
                rl_HasLocation_tpZN=[]
                for adjCell in Topology.AdjacentTopologies(hostTopology=tpBuilding,topology=tpFace,topologyType='cell'):
                    adjCellUID=Dictionary.ValueAtKey(Topology.Dictionary(adjCell),'UID')
                    for tpZone in tpZones:
                        zoneUID=Dictionary.ValueAtKey(Topology.Dictionary(tpZone),'UID')
                        for tpCell in CellComplex.Cells(tpZone):
                            cellUID=Dictionary.ValueAtKey(Topology.Dictionary(tpCell),'UID')
                            if adjCellUID==cellUID:
                                rl_HasLocation_tpZN.append(zoneUID)
                newD=Dictionary.ByKeyValue('rl_HasLocation_tpZN',rl_HasLocation_tpZN)
                newD=Dictionary.ByMergedDictionaries([Topology.Dictionary(tpFace),newD])
                tpFace=Topology.SetDictionary(tpFace,newD)
        return tpBuilding

class Scenario():

    """Helpers to locate the zones modified by the what-if scenarios in an IDF model"""

    @staticmethod
    def ZoneNameOf(idfObject=None):
        """Zone of an IDF load object named '<object name>..<zone>' by Honeybee (e.g. 'Generic Office People..zone18')"""
        return idfObject.Name.split('..')[1]

    @staticmethod
    def ClassroomZones(idfFile=None):
        """
        Classrooms of the case study: zones whose People object follows a booking schedule
        from the university booking service (OccSch_<room>) and has a non-zero density
        """
        import re
        zones=[]
        for people in idfFile.idfobjects['PEOPLE']:
            schedule=people.Number_of_People_Schedule_Name
            if re.match(r'^OccSch_(?!Unoccupied)',schedule) and float(people.People_per_Floor_Area or 0)>0:
                zones.append(Scenario.ZoneNameOf(people))
        return sorted(zones)

    @staticmethod
    def PeopleSchedules(idfFile=None):
        """Occupancy schedule name of each zone"""
        return {Scenario.ZoneNameOf(people):people.Number_of_People_Schedule_Name for people in idfFile.idfobjects['PEOPLE']}

    @staticmethod
    def ScheduleCompactByName(idfFile=None,name=None):
        for schedule in idfFile.idfobjects['SCHEDULE:COMPACT']:
            if schedule.Name==name:
                return schedule
        return None


class KPI():

    """
    Building-level KPIs of an annual EnergyPlus simulation (Section 3.3.3):
      - heating and cooling: ideal-load supply-air total (sensible + latent) energy;
      - ventilation: rated electrical power of the AHU serving each zone multiplied by the
        hours between 08:00 and 18:00 with non-zero supply-air flow;
      - lighting and equipment: zone electricity;
      - energy need (TOE), cost (EUR) and CO2 emissions (kgCO2eq): heating as natural gas,
        all the other end uses as electricity;
      - utilisation rate: share of the hours of the year in which a zone hosts more than one occupant;
      - occupancy rate: mean number of occupants relative to the zone design capacity;
        both rates are averaged over the zones weighting by their design capacity.
    """

    J_TO_KWH=2.77778e-7
    KWH_PER_SMC=10.944                      # lower heating value of natural gas (kWh/Sm3)
    SMC_TO_TOE,KWH_TO_TOE=8.2e-4,0.86e-4    # tonnes of oil equivalent per Sm3 and per kWh of electricity
    SMC_TO_EUR,KWH_TO_EUR=0.4987,0.164      # tariffs (EUR/Sm3, EUR/kWh)
    SMC_TO_CO2,KWH_TO_CO2=2.02,0.467        # emission factors (kgCO2eq/Sm3, kgCO2eq/kWh)
    VENTILATION_HOURS=(8,18)                # AHU operating hours used for the fan electricity

    @staticmethod
    def NetFloorAreaByIFC(ifcFilePath=None):
        """Sum of the NetFloorArea quantities of the IfcSpace entities (m2)"""
        import ifcopenshell
        import ifcopenshell.util.element
        ifcFile=ifcopenshell.open(ifcFilePath)
        return sum(ifcopenshell.util.element.get_psets(space).get('Qto_SpaceBaseQuantities',{}).get('NetFloorArea',0.0)
                   for space in ifcFile.by_type('IfcSpace'))

    @staticmethod
    def ZoneDesignCapacityByEIO(eioFilePath=None):
        """Design number of people of each zone, from the 'People Internal Gains Nominal' report of the EIO file"""
        capacity,header={},None
        with open(eioFilePath) as eioFile:
            for line in eioFile:
                if line.startswith('! <People Internal Gains Nominal>'):
                    header=[h.strip() for h in line.split(',')]
                elif line.startswith(' People Internal Gains Nominal,'):
                    fields=[f.strip() for f in line.split(',')]
                    zone=fields[header.index('Zone Name')]
                    capacity[zone]=capacity.get(zone,0)+float(fields[header.index('Number of People {}')])
        return capacity

    @staticmethod
    def BuildingKPIsByEnergyPlusResults(csvFilePath=None,eioFilePath=None,ahuElectricalPower=None):
        """
        csvFilePath: hourly EnergyPlus results (ReadVarsESO CSV)
        eioFilePath: EnergyPlus EIO file of the same run
        ahuElectricalPower: DataFrame with the columns 'zone' and 'revised_power_kW' (rated AHU fan power in kW)
        Returns a dictionary with the annual end uses (kWh) and the KPIs.
        """
        import pandas as pd
        df=pd.read_csv(csvFilePath)
        hour=pd.to_datetime(df['Date/Time'],format=' %m/%d  %H:%M:%S',errors='coerce').dt.hour
        total=lambda key: df.filter(like=key).sum().sum()*KPI.J_TO_KWH
        kpis={'heat':total('Zone Ideal Loads Supply Air Total Heating Energy'),
              'cool':total('Zone Ideal Loads Supply Air Total Cooling Energy'),
              'light':total('Zone Lights Electricity Energy'),
              'equip':total('Zone Electric Equipment Electricity Energy')}
        # Ventilation fan electricity
        start,end=KPI.VENTILATION_HOURS
        operating=(hour>=start)&(hour<end)
        kpis['vent']=0
        for column in df.filter(like='Supply Air Standard Density Volume Flow Rate').columns:
            match=ahuElectricalPower['zone'].str.lower()==column.split(' ')[0].lower()
            if match.any():
                kpis['vent']+=((df[column]>0)&operating).sum()*ahuElectricalPower.loc[match,'revised_power_kW'].values[-1]
        # Occupancy indicators, weighted by the design capacity of the zones
        capacity=KPI.ZoneDesignCapacityByEIO(eioFilePath)
        utilisation=occupancy=weight=0
        for column in df.filter(like='Zone People Occupant Count').columns:
            zoneCapacity=capacity.get(column.split(':')[0],0)
            if zoneCapacity<=0:
                continue
            utilisation+=(df[column]>1).sum()/len(df)*zoneCapacity
            occupancy+=(df[column]/zoneCapacity).mean()*zoneCapacity
            weight+=zoneCapacity
        kpis.update(UR=utilisation/weight*100,OR=occupancy/weight*100,capacity=weight)
        # Energy need, cost and emissions
        naturalGas=kpis['heat']/KPI.KWH_PER_SMC
        electricity=kpis['cool']+kpis['light']+kpis['equip']+kpis['vent']
        kpis.update(TOE=naturalGas*KPI.SMC_TO_TOE+electricity*KPI.KWH_TO_TOE,
                    EUR=naturalGas*KPI.SMC_TO_EUR+electricity*KPI.KWH_TO_EUR,
                    CO2=naturalGas*KPI.SMC_TO_CO2+electricity*KPI.KWH_TO_CO2)
        return kpis
