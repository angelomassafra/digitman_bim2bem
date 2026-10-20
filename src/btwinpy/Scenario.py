class Scenario():

    @staticmethod
    def Constructor(scenarioUID=None, scenarioType='btwin:Scenario', name=None, description=None):
        """
        Creates and returns a dictionary representing a spatial element with optional name and relationships.

        This static method initializes a spatial element with the given unique identifier and class. It can optionally
        include a name for the spatial element. The method also initializes an empty 'relationships' dictionary for
        potential future use.

        Parameters:
            scenarioUID (str): The unique identifier for the spatial element. This parameter is required.
            scenarioType (str): The class/type of the spatial element according to BTwin ontology. This parameter is required.
            name (str, optional): The name of the spatial element. Default is None.

        Returns:
            dict: A dictionary object representing the spatial element with the provided details usable for JSON-LD.

        Raises:
            ValueError: If `scenarioUID` or `scenarioType` is not provided, a ValueError is raised
            with an appropriate error message.

        Examples:
            >>> Constructor("mySpace", "bot:Space")
            {'@id': 'mySpace', '@type': 'bot:Space', 'relationships': {}}
        """

        if scenarioUID is not None and scenarioType is not None:
            # Initialize Spatial Element dictionary
            scenario = {
                '@id': scenarioUID,
                '@type': scenarioType
            }
            # Set name
            if name:
                scenario['name']=name
            # Set description
            if description:
                scenario['description']=description
            # Initialize relationships
            scenario['relationships']={}
            # Result
            return scenario
        # Raise error
        else:
            if scenarioUID is None:
                print('Error: scenarioUID was not provided.')
            if scenarioType is None:
                print('Error: scenarioType was not provided.')
  

