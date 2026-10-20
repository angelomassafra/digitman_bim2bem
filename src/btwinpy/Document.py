class Document():



    @staticmethod
    def Constructor(pointUID=None, pointType=None, name=None):

        if pointUID is not None and pointType is not None:
            # Initialize Spatial Element dictionary
            documentObject = {
                '@id': pointUID,
                '@type': pointType
            }
            # Set name
            if name:
                documentObject['name']=name
            # Initialize relationships
            documentObject['relationships']={}
            # Result
            return documentObject
        # Raise error
        else:
            if pointUID is None:
                print('Error: pointUID was not provided.')
            if pointType is None:
                print('Error: documentObjectType was not provided.')

    @staticmethod
    def SetRelationship(pointObject=None, relationshipName=None, linkedObject=None, linkedObjectUID=None, linkedObjectType=None):
       
        if pointObject is not None:
            # Related element UID and type
            if linkedObjectUID is None:
                linkedObjectUID = linkedObject['@id'] if linkedObject else None
                linkedObjectType = linkedObject['@type'] if linkedObject else linkedObjectType
            # Set relationship
            try:
                if relationshipName not in list(pointObject['relationships'].keys()):
                    pointObject['relationships'][relationshipName] = [{'@id':linkedObjectUID,'@type':linkedObjectType}]
                else:
                    pointObject['relationships'][relationshipName].append({'@id':linkedObjectUID,'@type':linkedObjectType})

                return pointObject
        # Raise error
            except:
                print('Error: linkedObject or linkedObjectUID were not provided.')
        else:
            print('Error: documentObject was not provided.')