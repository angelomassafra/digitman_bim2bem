class SpatialElement():

    @staticmethod
    def Constructor(spatialElementUID=None, spatialElementType=None, name=None):
        """
        Creates and returns a JSONLD dictionary representing a spatial element with optional name and relationships.

        Parameters:
            spatialElementUID (str): The unique identifier for the spatial element.
            spatialElementType (str): The type of the spatial element according to BTwin ontology.
            name (str, optional): The name of the spatial element.

        Returns:
            dict: A dictionary object representing the spatial element with the provided identifiers, usable for JSON-LD.

        Examples:
            >>> SpatialElement.Constructor(spatialElementUID="SP001", spatialElementType="bot:Space",name="mySpace")
            {'@id': 'SP001', '@type': 'bot:Space', 'name': 'mySpace', 'relationships': {}}
        """

        if spatialElementUID is not None and spatialElementType is not None:
            # Initialize Spatial Element dictionary
            spatialElement = {'@id': spatialElementUID,'@type': spatialElementType, 'relationships':{}}
            # Set name
            if name:
                spatialElement['name']=name
            # Output
            return spatialElement
        
        # Raise error
        else:
            if spatialElementUID is None:
                print('Error: spatialElementUID was not provided.')
            if spatialElementType is None:
                print('Error: spatialElementType was not provided.')

    @staticmethod
    def SetPropertySet(spatialElementObject=None,psetObject=None,psetUID=None):
        
        # Relationship Name
        relationshipName='ifc:HasPropertySet'

        if psetObject is not None or psetUID is not None:
            # Related element UID and type
            if psetObject is not None:
                psetObjectUID,psetObjectType = psetObject['@id'],psetObject['@type']
            elif psetUID is not None:
                psetObjectUID,psetObjectType = psetUID,'ifc:IfcPropertySet'
            # Set relationship
            try:
                if relationshipName not in list(spatialElementObject['relationships'].keys()):
                    spatialElementObject['relationships'][relationshipName] = [{'@id':psetObjectUID,'@type':psetObjectType}]
                else:
                    spatialElementObject['relationships'][relationshipName].append({'@id':psetObjectUID,'@type':psetObjectType})
                return spatialElementObject
        # Raise error
            except:
                print('Error: linkedObject was not provided.')
        else:
            print('Error: spatialElement was not provided.')

    @staticmethod
    def SetRelationship(spatialElementObject=None, relationshipName=None, linkedObject=None, linkedObjectUID=None, linkedObjectType=None):
        """
        Establishes a relationship between a spatial element and a linked object.

        This method adds a relationship to the 'spatialElement' dictionary. The relationship is defined by the
        'relationshipName' and is associated with a 'linkedObject' or 'linkedObjectUID' and 'linkedObjectType'.

        Parameters:
            spatialElement (dict, optional): The spatial element to which the relationship is to be added. Must contain
                                             a 'relationships' key. If not provided, an error message is printed.
            relationshipName (str, optional): The name of the relationship to be added. If not provided, the relationship
                                              cannot be set, and an error will be printed.
            linkedObject (dict, optional): A dictionary representing the related element. If provided, it should contain
                                             '@id' and '@type' keys. If not provided, 'linkedObjectUID' and
                                             'linkedObjectType' must be provided instead.
            linkedObjectUID (str, optional): The unique identifier of the related element. Required if 'linkedObject'
                                                is not provided.
            linkedObjectType (str, optional): The type of the related element. Required if 'linkedObject' is not
                                                provided and 'linkedObjectUID' is given.

        Returns:
            dict: The updated 'spatialElement' dictionary with the new relationship added. If any required parameters
                  are missing, the original 'spatialElement' is returned unchanged, and an error message is printed.

        Raises:
            ValueError: If 'spatialElement' is not provided or if neither 'linkedObject' nor 'linkedObjectUID' and
                        'linkedObjectType' are provided.

        Examples:
            >>> spatial_element = {'@id': 'mySpace', '@type': 'bot:Space', 'relationships': {}}
            >>> related_element = {'@id': 'myStorey', '@type': 'bot:Storey'}
            >>> SetRelationship(spatialElement=spatial_element, relationshipName='brick:hasLocation', linkedObject=related_element)
            {'@id': 'mySpace', '@type': 'bot:Space', 'relationships': {'brick:hasLocation': [{'@id': 'myStorey', '@type': 'bot:Storey'}]}}
        """
        if spatialElementObject is not None:
            # Related element UID and type
            if linkedObjectUID is None:
                linkedObjectUID = linkedObject['@id'] if linkedObject else None
                linkedObjectType = linkedObject['@type'] if linkedObject else linkedObjectType
            # Set relationship
            try:
                if relationshipName not in list(spatialElementObject['relationships'].keys()):
                    spatialElementObject['relationships'][relationshipName] = [{'@id':linkedObjectUID,'@type':linkedObjectType}]
                else:
                    spatialElementObject['relationships'][relationshipName].append({'@id':linkedObjectUID,'@type':linkedObjectType})

                return spatialElementObject
        # Raise error
            except:
                print('Error: linkedObject or linkedObjectUID were not provided.')
        else:
            print('Error: spatialElement was not provided.')


    