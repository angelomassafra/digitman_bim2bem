class PropertySet():

    @staticmethod
    def Constructor(psetUID=None, psetName=None):
        PSet = {
            '@id': psetUID,
            '@type': 'ifc:IfcPropertySet',
            'name': psetName,
            'ifc:HasProperties':[]
        }
        return PSet
    
    
                
    @staticmethod
    def SetProperty(pset=None, property=None, overwrite=False):
        """
        Adds a property to a property set if it is not already present.

        This method checks if the specified property exists within the 'ifc:HasProperties' list of the property set.
        If the property is not found, it appends the property to this list. This method ensures that the property set
        does not contain duplicate properties.

        Parameters:
        - pset (dict): The property set to be modified, expected to have a key 'ifc:HasProperties' that maps to a list.
        - property (dict): The property dictionary to be added to the property set.

        Returns:
        - dict: The updated property set with the possibly appended property.
        """
        if property['name'] not in str(pset['ifc:HasProperties']):
            pset['ifc:HasProperties'].append(property)

        elif overwrite is True:
            for prop in pset['ifc:HasProperties']:
                if prop['name']==property['name']:
                    prop=property
            
        return pset
    
class Property():

    @staticmethod
    def Constructor(propertyName=None, propertyValue=None, propertyValues=[], propertyQuantity=None, propertyType='IfcPropertySingleValue'):
        """Creates a property dictionary based on IFC property types.

        Args:
            propertyName (str, optional): Name of the property.
            propertyValue (any, optional): Value of the property for single value properties.
            propertyValues (list, optional): List of values for enumerated properties.
            propertyQuantity (str, optional): Data type of the property value.
            propertyType (str, optional): Type of the IFC property.

        Returns:
            dict: A dictionary representing the property in IFC format.
        """
        property = {'@type': propertyType, 'name': propertyName}

        if property['@type'] == 'IfcPropertySingleValue':
            property['nominalValue'] = {'type': propertyQuantity, 'value': propertyValue}
        elif property['@type'] == 'IfcPropertyEnumeratedValue':
            property['enumeratedValues'] = [{'type': propertyQuantity, 'value': value} for value in (propertyValues or [])]

        return property
    

    


    


    

