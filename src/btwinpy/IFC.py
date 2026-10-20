class IFC():

    @staticmethod
    def IfcStoreyByIfcSpace(ifcSpace=None):
        """Get the IfcStorey of the IfcSpace"""
        if ifcSpace.Decomposes:
            for relAggregates in ifcSpace.Decomposes:
                if relAggregates.is_a('IfcRelAggregates'):
                    parentObject = relAggregates.RelatingObject
                    if parentObject and parentObject.is_a('IfcBuildingStorey'):
                        return parentObject
                
    @staticmethod
    def IfcSpaceGetPropertyValue(ifcSpace=None,propertyName=None):
        if ifcSpace.IsDefinedBy:
            for rel in ifcSpace.IsDefinedBy:
                if rel.is_a("IfcRelDefinesByProperties"):
                    prop_set=rel.RelatingPropertyDefinition
                    if prop_set.is_a("IfcPropertySet"):
                        for prop in prop_set.HasProperties:
                            if prop.is_a("IfcPropertySingleValue"):
                                if prop.Name == propertyName:
                                    return prop.NominalValue.wrappedValue


                                
    


    
