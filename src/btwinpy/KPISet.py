class KPISet():


    @staticmethod
    def Constructor(uid, name='None'):
        """
        Initialize a KPISet as a Python dictionary.

        Parameters:
        - uid (str): Unique identifier for the KPISet.
        - name (str): Name of the KPISet.
        - subclass (str): Subclass information for the KPISet.

        Returns:
        dict: A dictionary representing the KPISet with the provided attributes.
        """
        KPISet = {
            '@id': uid,
            'name': name,
            '@type': 'btwin:KPISet',
            'relationships': {},
            'btwin:hasKPIs':{},
            'timestamp':{'from':None,'to':None}
        }
        return KPISet


    
    @staticmethod
    def SetKPI(kpiSet=None, kpi=None, overwrite=False):
        """
        Adds a kpi to a kpi set if it is not already present.

        This method checks if the specified kpi exists within the 'btwin:hasKPIs' list of the property set.
        If the property is not found, it appends the property to this list. This method ensures that the property set
        does not contain duplicate properties.

        Parameters:
        - pset (dict): The property set to be modified, expected to have a key 'btwin:hasKPIs' that maps to a list.
        - property (dict): The property dictionary to be added to the property set.

        Returns:
        - dict: The updated property set with the possibly appended property.
        """
        if overwrite:
            kpiSet['btwin:hasKPIs'][kpi['@id']]=kpi
        return kpiSet


class KPI():

    @staticmethod
    def Constructor(kpiUID=None,kpiName=None,kpiValue=None,kpiType='eko:KPI',kpiHasBeginning=None,kpiHasEnd=None,kpiUnit=None):

        kpi = {
            '@id':kpiUID,
            '@type':'eko:KPI',
            'name':kpiName,
            'relationships':{
                'eko:hasAssociatedObject':[{'@id':None,'@type':None}],
                'eko:hasEvaluationTimestep':[{'@type':'time:interval','time:hasBeginning':kpiHasBeginning,'time:hasEnd':kpiHasEnd}]},
            'nominalValue':{'@type':kpiType,'value':kpiValue, 'unit':kpiUnit}}
        return kpi
    
