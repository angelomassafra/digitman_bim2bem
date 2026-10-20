class DataFormat():

    @staticmethod
    def ByObjects(objects=[],savePath=None):

        """
        Generates a JSON-LD document based on the input objects and optionally saves it to a file.

        This method processes a list of objects, flattens any nested structures, and incorporates them into the '@graph' section of a JSON-LD document. 
        It then examines the content to dynamically construct the '@context' part, which includes definitions and references for various spatial elements like zones, locations, sites, buildings, storeys, and spaces, based on recognized keywords. These definitions are derived from the Brick Schema and the Building Topology Ontology (BOT).

        Parameters:
        - objects (list, optional): A list of objects (dictionaries, lists, etc.) to be included in the JSON-LD '@graph' section. Defaults to an empty list.
        - savePath (str, optional): The file path where the JSON-LD document should be saved. If provided, the method appends '.json' to the path if it's not already present and writes the JSON-LD document to this file. Defaults to None, in which case the document is not saved to a file.

        Returns:
        - dict: A dictionary representing the JSON-LD document, including '@context' and '@graph' sections.

        Raises:
        - FileNotFoundError: If the specified savePath is not writable or cannot be found.
        - Exception: For other issues that may arise during file writing or JSON serialization.

        Note:
        - This method does not validate the input objects against any JSON-LD schema.
        - Ensure that the input objects are structured appropriately for JSON-LD serialization.

        Example usage:
        ```
        jsonld_document = ClassName.ByObjects(objects=[...], savePath='path/to/save/document.json')
        ```
        """

        # Import libraries
        import json

        # Initialize jsonLD document
        JSONLD = {'@context':{},'@graph':[]}

        def flatten(lst):
            result = []
            for item in lst:
                if isinstance(item, list):
                    result.extend(flatten(item))
                elif item is not None:
                    result.append(item)
            return result
        
        # Initialize graph objects
        JSONLD['@graph']=flatten(objects)
    
        # Determine the Context
        jsonString = str(JSONLD['@graph'])

        # Spatial elements
        # Brick
        if "brick" in jsonString:
            JSONLD['@context']['brick']='https://brickschema.org/schema/1.3/Brick'
        if "Portfolio" in jsonString:
            JSONLD['@context']['brick:Portfolio']='https://w3c-lbd-cg.github.io/bot/#Portfolio'
        if "Region" in jsonString:
            JSONLD['@context']['brick:Region']='https://w3c-lbd-cg.github.io/bot/#Region'
        if "Zone" in jsonString:
            JSONLD['@context']['brick:Zone']='https://w3c-lbd-cg.github.io/bot/#Zone'
        if "hasLocation" in jsonString:
            JSONLD['@context']['brick:hasLocation']='https://brickschema.org/schema/Brick#hasLocation'
        if "isPartOf" in jsonString:
            JSONLD['@context']['brick:isPartOf']='https://brickschema.org/schema/Brick#isPartOf'
    
        if "brick:Temperature_Sensor" in jsonString:
            JSONLD['@context']['brick:Temperature_Sensor']='https://brickschema.org/schema/Brick#Temperature_Sensor'
        if "brick:Humidity_Sensor" in jsonString:
            JSONLD['@context']['brick:Humidity_Sensor']='https://brickschema.org/schema/Brick#Humidity_Sensor'
        if "brick:Luminance_Sensor" in jsonString:
            JSONLD['@context']['brick:Luminance_Sensor']='https://brickschema.org/schema/Brick#Luminance_Sensor'
        if "brick:Pressure_Sensor" in jsonString:
            JSONLD['@context']['brick:Pressure_Sensor']='https://brickschema.org/schema/Brick#Pressure_Sensor'
        if "brick:CO2_Sensor" in jsonString:
            JSONLD['@context']['brick:CO2_Sensor']='https://brickschema.org/schema/Brick#CO2_Sensor'
        if "brick:PM1_Sensor" in jsonString:
            JSONLD['@context']['brick:PM1_Sensor']='https://brickschema.org/schema/Brick#PM1_Sensor'
        if "brick:PM2.5_Sensor" in jsonString:
            JSONLD['@context']['brick:PM2.5_Sensor']='https://brickschema.org/schema/Brick#PM2.5_Sensor'
        if "brick:PM10_Sensor" in jsonString:
            JSONLD['@context']['brick:PM10_Sensor']='https://brickschema.org/schema/Brick#PM10_Sensor'
        if "brick:TVOC_Sensor" in jsonString:
            JSONLD['@context']['brick:TVOC_Sensor']='https://brickschema.org/schema/Brick#TVOC_Sensor'
        if "brick:Current_Sensor" in jsonString:
            JSONLD['@context']['brick:TVOC_Sensor']='https://brickschema.org/schema/Brick#Current_Sensor'
        if "brick:Air_Flow_Sensor" in jsonString:
            JSONLD['@context']['brick:TVOC_Sensor']='https://brickschema.org/schema/Brick#Air_Flow_Sensor'
        if "brick:Speed_Sensor" in jsonString:
            JSONLD['@context']['brick:TVOC_Sensor']='https://brickschema.org/schema/Brick#Speed_Sensor'
        if "brick:Air_Handling_Unit" in jsonString:
            JSONLD['@context']['brick:TVOC_Sensor']='https://brickschema.org/schema/Brick#Air_Handling_Unit'


        # BOT
        if "bot" in jsonString:
            JSONLD['@context']['bot']='http://w3id.org/bot'
        if "Site" in jsonString:
            JSONLD['@context']['bot:Site']='https://w3c-lbd-cg.github.io/bot/#Site'
        if "Building" in jsonString:
            JSONLD['@context']['bot:Building']='https://w3c-lbd-cg.github.io/bot/#Building'
        if "Storey" in jsonString:
            JSONLD['@context']['bot:Storey']='https://w3c-lbd-cg.github.io/bot/#Storey'
        if "Space" in jsonString:
            JSONLD['@context']['bot:Space']='https://w3c-lbd-cg.github.io/bot/#Space'
        # IFC
        if "ifc" in jsonString:
            JSONLD['@context']['ifc']='https://standards.buildingsmart.org/IFC/DEV/IFC4/ADD2_TC1/OWL'
        if "IfcPropertySet" in jsonString:
            JSONLD['@context']['ifc:IfcPropertySet']='https://standards.buildingsmart.org/IFC/DEV/IFC4/ADD2_TC1/OWL#IfcPropertySet'
        if "ifc:HasPropertySet" in jsonString:
            JSONLD['@context']['ifc:HasPropertySet']='https://standards.buildingsmart.org/IFC/DEV/IFC4/ADD2_TC1/OWL/index.html#hasPropertySets_IfcTypeObject'
        if "ifc:HasProperties" in jsonString:
            JSONLD['@context']['ifc:HasProperties']='https://standards.buildingsmart.org/IFC/DEV/IFC4/ADD2_TC1/OWL#hasProperties_IfcPropertySet'
        if "IfcSensor" in jsonString:
            JSONLD['@context']['ifc:IfcSensor']='https://standards.buildingsmart.org/IFC/DEV/IFC4/ADD2_TC1/OWL#IfcSensor'

        # Save
        if savePath:
            if '.json' not in savePath:
                savePath = savePath+'.json'
                with open(savePath, 'w') as file:
                    json.dump(JSONLD, file, indent=4)
            else:
                with open(savePath, 'w') as file:
                    json.dump(JSONLD, file, indent=4)


        # Output
        return JSONLD

    @staticmethod
    def ByJSONPath(jsonPath=None):
        """
        Reads and returns the contents of a JSON-LD file created through BTwin specified by the jsonPath parameter.

        This method attempts to open and read a JSON file located at the path provided by the jsonPath argument. 
        It then parses the JSON file into a Python dictionary using the built-in `json` module. If the file cannot be opened, read, or parsed, it prints an error message.

        Parameters:
        - jsonPath (str, optional): The path to the JSON file to be read. If not provided or None, the method will print an error message.

        Returns:
        - dict: A Python dictionary containing the data parsed from the JSON file. If an error occurs or the jsonPath is None, the method returns None.

        Raises:
        - FileNotFoundError: If the file specified by jsonPath does not exist or cannot be accessed.
        - json.JSONDecodeError: If the file specified is not a valid JSON file or cannot be decoded.

        Example usage:
        ```
        data = ClassName.ByJSONPath(jsonPath='path/to/file.json')
        if data is not None:
            print(data)
        ```

        Note:
        - The method uses a generic exception handler, which is not a best practice. It is recommended to catch specific exceptions to provide more accurate error handling and messages.
        """

        # Import libraries
        import json
        # Impor jsonData
        try:
            # Open the JSON file and read data
            if '.json' not in jsonPath:
                jsonPath=jsonPath+'.json'
            with open(jsonPath, 'r') as file:
                data = json.load(file)
            return data
        except:
            print('Error: no data found in the provided jsonPath.')


    @staticmethod   
    def SpatialHierarchyByIFC(
        ifcPath=None,
        savePath=None,
        siteObject=None,
        humanReadableUIDs=False,
        buildingUID=None,buildingName=None,spaceUIDPropertyName='UID',
        spacePSetNames=['Other'],
        buildingPSets=[], # Additional building PSets not present in the IFC
        includePSets=True
    ):
        
        # Import libraries
        import ifcopenshell
        
        # Import BTwinpy
        from .SpatialElement import SpatialElement
        from .PropertySet import Property,PropertySet
        from .DataFormat import DataFormat

        # Open IFC file
        ifc_file = ifcopenshell.open(ifcPath)

        # Buildings
        buildings = []
        ifcBuildings = ifc_file.by_type('IfcBuilding')
        for ifcBuilding in ifcBuildings:
            buildUID, buildName = ifcBuilding.GlobalId, ifcBuilding.Name
            if humanReadableUIDs:
                buildUID = buildingName
            if buildingUID is not None:
                buildUID = buildingUID
            if buildingName is not None:
                buildName = buildingName
            building = SpatialElement.Constructor(spatialElementUID=buildUID, name=buildName, spatialElementType='bot:Building')
            if siteObject is not None:
                building = SpatialElement.SetRelationship(
                    spatialElementObject=building,linkedObject=siteObject,relationshipName='brick:hasLocation')
            
            # Set Building PSets
            if includePSets:
                for buildingPset in buildingPSets:
                    building = SpatialElement.SetPropertySet(spatialElementObject=building,psetObject=buildingPset)
            
            buildings.append(building)
            
        # Zones
        zones = []
        ifcZones = ifc_file.by_type('ifcZone')
        for ifcZone in ifcZones:
            zoneUID,zoneName = ifcZone.GlobalId,ifcZone.Name.split(":")[0]
            if humanReadableUIDs:
                zoneUID = zoneName
            zone = SpatialElement.Constructor(spatialElementUID=zoneUID, name=zoneName ,spatialElementType='brick:Zone')
            zone = SpatialElement.SetRelationship(
                spatialElementObject=zone,linkedObject=buildings[0],relationshipName='brick:hasLocation')
            zones.append(zone)

        # Storeys
        storeys = []
        ifcStoreys = ifc_file.by_type('ifcBuildingStorey')
        for ifcStorey in ifcStoreys:
            storeyUID,storeyName = ifcStorey.GlobalId,ifcStorey.Name
            if humanReadableUIDs:
                storeyUID = storeyName
            storey = SpatialElement.Constructor(spatialElementUID=storeyUID, name=storeyName ,spatialElementType='bot:Storey')
            storey = SpatialElement.SetRelationship(
                spatialElementObject=storey,linkedObject=buildings[0],relationshipName='brick:hasLocation')
            storeys.append(storey)

        # Spaces
        spaces = []
        spacesPSets=[]
        
        ifcSpaces = ifc_file.by_type('IfcSpace')
        for ifcSpace in ifcSpaces:
            spaceName,spaceUID = ifcSpace.Name, ifcSpace.GlobalId
            for definition in ifcSpace.IsDefinedBy:
                if definition.is_a('IfcRelDefinesByProperties'):
                    property_set = definition.RelatingPropertyDefinition
                    if property_set.is_a('IfcPropertySet'):
                        for property in property_set.HasProperties:
                            if property.Name == spaceUIDPropertyName:
                                if property.is_a('IfcPropertySingleValue'):
                                    spaceName = property.NominalValue.wrappedValue
            if humanReadableUIDs:
                spaceUID = spaceName
            space = SpatialElement.Constructor(spatialElementUID=spaceUID, name=spaceName ,spatialElementType='bot:Space')
            # Set relationship with the storey
            if ifcSpace.Decomposes:
                for relAggregates in ifcSpace.Decomposes:
                    if relAggregates.is_a('IfcRelAggregates'):
                        parentObject = relAggregates.RelatingObject
                        if parentObject and parentObject.is_a('IfcBuildingStorey'):
                            storeyUID = parentObject.GlobalId
                            if humanReadableUIDs:
                                storeyUID = parentObject.Name
                            space = SpatialElement.SetRelationship(
                                spatialElementObject=space,linkedObjectUID=storeyUID,linkedObjectType='bot:Storey',relationshipName='brick:hasLocation')
            # Set relationship with the zones
            spaceZones = []
            for rel_assigns in ifc_file.by_type("IfcRelAssignsToGroup"):
                if ifcSpace in rel_assigns.RelatedObjects:
                    group = rel_assigns.RelatingGroup
                    if group.is_a("IfcZone"):  # Step 3: Check if the group is an IfcZone
                            spaceZones.append(group)
                for spaceZone in spaceZones:
                    spaceZoneUID = spaceZone.GlobalId
                    if humanReadableUIDs:
                        spaceZoneUID = spaceZone.Name.split(":")[0]
                    space = SpatialElement.SetRelationship(
                        spatialElementObject=space,linkedObjectUID=spaceZoneUID,linkedObjectType='brick:Zone',relationshipName='brick:hasLocation')
            
            # Space PSets 
            if includePSets:
                ifcPropertySets=ifcopenshell.util.element.get_psets(ifcSpace)
                for ifcPropertySet in ifcPropertySets:
                    psetUID=ifcPropertySet
                    if psetUID in spacePSetNames:

                        pset=PropertySet.Constructor(psetUID=f'{spaceUID}_{psetUID}',psetName=psetUID)
                        
                        for propName in ifcPropertySets[ifcPropertySet]:
                            if 'pr_' in propName:
                                propValue=ifcPropertySets[ifcPropertySet][propName]
                                propQuantity='IfcLabel'
                                if 'VentilationPerArea' in propName:
                                    propQuantity='IfcCountMeasure'
                                    try:
                                        propValue=float(propValue)
                                    except:
                                        continue
                                elif 'VentilationRate' in propName:
                                    propQuantity='IfcCountMeasure' 
                                    try:
                                        propValue=float(propValue)
                                    except:
                                        continue
                                elif 'Illuminance' in propName:  
                                    propQuantity='IfcIlluminanceMeasure'
                                    try:
                                        propValue=int(propValue)
                                    except:
                                        continue
                                elif 'AreaPerOccupant' in propName: 
                                    propQuantity='IfcAreaMeasure'
                                    try:
                                        propValue=float(propValue)
                                    except:
                                        continue
                                elif 'NumberOf' in propName or 'OccupancyNumber' in propName:
                                    propQuantity='IfcCountMeasure'  
                                    try:
                                        propValue=int(propValue)
                                    except:
                                        continue
                                elif 'SpaceTemperature' in propName:
                                    propQuantity='IfcThermodynamicTemperatureMeasure'
                                    try:
                                        propValue=float(propValue)
                                    except:
                                        continue
                                elif 'Humidity' in propName:
                                    propQuantity='IfcRatioMeasure'
                                    try:
                                        propValue=float(propValue)
                                    except:
                                        continue
                                elif 'PowerDensity' in propName:  
                                    propQuantity='IfcPowerMeasure'
                                    try:
                                        propValue=float(propValue)
                                    except:
                                        continue
                                elif 'pr_Is' in propName:
                                    propQuantity='IfcBoolean'
                                    try:
                                        propValue=bool(propValue)
                                    except:
                                        continue
                                prop=Property.Constructor(propertyName=propName,propertyValue=propValue,propertyQuantity=propQuantity)
                                pset=PropertySet.SetProperty(pset=pset,property=prop)
                        space=SpatialElement.SetPropertySet(spatialElementObject=space,psetObject=pset)
                        spacesPSets.append(pset)    
                    
                    # Dimensions
                    if psetUID=='Dimensions':
                        pset=PropertySet.Constructor(psetUID=f'{spaceUID}_{psetUID}',psetName=psetUID)
                        # Net Area
                        pr_NetArea=round(ifcPropertySets[ifcPropertySet]['Area'],2)
                        prop=Property.Constructor(propertyName='pr_NetArea',propertyValue=pr_NetArea,propertyQuantity='IfcAreaMeasure')
                        pset=PropertySet.SetProperty(pset=pset,property=prop)
                        # Net Volume
                        pr_NetVolume=round(ifcPropertySets[ifcPropertySet]['Volume'],2)
                        prop=Property.Constructor(propertyName='pr_NetVolume',propertyValue=pr_NetVolume,propertyQuantity='IfcVolumeMeasure')
                        pset=PropertySet.SetProperty(pset=pset,property=prop)
                        # Net Height
                        pr_NetHeight=round(ifcPropertySets[ifcPropertySet]['Unbounded Height'],2)
                        prop=Property.Constructor(propertyName='pr_NetHeight',propertyValue=pr_NetHeight,propertyQuantity='IfcLengthMeasure')
                        pset=PropertySet.SetProperty(pset=pset,property=prop)
                        space=SpatialElement.SetPropertySet(spatialElementObject=space,psetObject=pset)
                        spacesPSets.append(pset)

                    # Schedule relationships
                    if psetUID=='Other':
                        pset=PropertySet.Constructor(psetUID=f'{spaceUID}_PSet_SpaceSchedules',psetName='PSet_SpaceSchedules')
                        # Occupancy Schedule
                        rl_IsScheduledBy_Occupancy=ifcPropertySets[ifcPropertySet]['rl_IsScheduledBy_Occupancy']
                        prop=Property.Constructor(propertyName='rl_IsScheduledBy_Occupancy',propertyValue=rl_IsScheduledBy_Occupancy,propertyQuantity='IfcLabel')
                        pset=PropertySet.SetProperty(pset=pset,property=prop)
                        # Heating Schedule
                        rl_IsScheduledBy_Heating=ifcPropertySets[ifcPropertySet]['rl_IsScheduledBy_Heating']
                        prop=Property.Constructor(propertyName='rl_IsScheduledBy_Heating',propertyValue=rl_IsScheduledBy_Heating,propertyQuantity='IfcLabel')
                        pset=PropertySet.SetProperty(pset=pset,property=prop)
                        # Cooling Schedule
                        rl_IsScheduledBy_Cooling=ifcPropertySets[ifcPropertySet]['rl_IsScheduledBy_Cooling']
                        prop=Property.Constructor(propertyName='rl_IsScheduledBy_Cooling',propertyValue=rl_IsScheduledBy_Cooling,propertyQuantity='IfcLabel')
                        pset=PropertySet.SetProperty(pset=pset,property=prop)
                        # Equipment Schedule
                        rl_IsScheduledBy_Equipment=ifcPropertySets[ifcPropertySet]['rl_IsScheduledBy_Equipment']
                        prop=Property.Constructor(propertyName='rl_IsScheduledBy_Equipment',propertyValue=rl_IsScheduledBy_Equipment,propertyQuantity='IfcLabel')
                        pset=PropertySet.SetProperty(pset=pset,property=prop)
                        # Lighting Schedule
                        rl_IsScheduledBy_Lighting=ifcPropertySets[ifcPropertySet]['rl_IsScheduledBy_Lighting']
                        prop=Property.Constructor(propertyName='rl_IsScheduledBy_Lighting',propertyValue=rl_IsScheduledBy_Lighting,propertyQuantity='IfcLabel')
                        pset=PropertySet.SetProperty(pset=pset,property=prop)
                        # PSet
                        space=SpatialElement.SetPropertySet(spatialElementObject=space,psetObject=pset)
                        spacesPSets.append(pset)

            # Append space
            spaces.append(space)

                        
                    
        # Get IFC Spatial Hierarchy as JSONLD
        objects = [building,storeys,zones,spaces]
        if len(buildingPSets)>0:
            objects.append(buildingPSets)
        if len(spacesPSets)>0:
            objects.append(spacesPSets)
        if siteObject is not None:
            objects.append(siteObject)
        jsonLD = DataFormat.ByObjects(objects=objects,savePath=savePath)
        return jsonLD


