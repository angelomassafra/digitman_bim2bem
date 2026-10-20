class KnowledgeGraph():

    @staticmethod        
    def AddEdgeByType(graph=None,objects=[],relationshipName=None):
        """
        Add edges to a graph based on relationships between entities of a particular subclass in the data model.

        Parameters:
        - objects (list): List of entities of a specific subclass.
        - subclass (str): Subclass name (e.g., 'brick:Region', 'tpST').
        - relationshipName (str): Name of the relationship to consider.
        - graph (nx.Graph): The networkx graph to which edges will be added.

        Returns:
        - None

        Example:
        >>> class_entities = [...]  # List of entities of a specific subclass
        >>> graph = nx.Graph()  # Create an empty networkx graph
        >>> AddEdgeByType(class_entities, 'brick:Region', 'HasLocation', graph)
        >>> # The graph is updated with edges based on the given subclass and relationship
        """

        for object in objects:
            try:
                rl_Relationship = object['relationships'][relationshipName]
                for linkedObject in rl_Relationship:
                    objectNodeNumber=KnowledgeGraph.NodeNumberByUID(graph,object['@id'])
                    linkedObjectNumber=KnowledgeGraph.NodeNumberByUID(graph,linkedObject['@id'])
                    graph.add_edge(objectNodeNumber,linkedObjectNumber,label=relationshipName)
            except:
                a=0
                #print(f'Error: impossible to add edge for {relationshipName}: {object}')
     
    @staticmethod
    def AddEdgeByTypes(graph=None,childObjects=[],childObjectsType=None,parentObjects=[],parentObjectsType=None,relationshipName=None,silent=True):
        """
            Adds edges to a graph based on specified relationships between entities of a child subclass and a parent subclass.

            This function iterates over child entities, checks their relationships, and adds an edge to the graph if a corresponding parent entity is found with a matching relationship.

            Parameters:
                graph (nx.Graph): The networkx graph to which edges will be added.
                child_objects (list): List of dictionaries representing child entities.
                child_subclass (str): Name of the child subclass.
                parent_objects (list): List of dictionaries representing parent entities.
                parent_subclass (str): Name of the parent subclass.
                relationship_name (str): Name of the relationship based on which edges will be added.

            Note:
                The function specifically handles 'IfcPropertySet' as a special case for child subclasses.

            Example:
                >>> graph = nx.Graph()
                >>> add_edge_by_subclasses(graph, child_entities, 'tpSP', parent_entities, 'tpBL', 'HasLocation')
                This will update 'graph' with edges between matched child and parent entities based on 'HasLocation' relationship.
            """
        for childClassEntity in childObjects:
            rl = childClassEntity['relationships']
            
            # PropertySets
            if 'IfcPropertySet' in childObjectsType:
                childObjectsType=='ifc:IfcPropertySet'
                try:
                    rl_Relationship = rl['ifc:HasPropertySets']
                    for parentClassEntity in parentObjects:
                        for linkedUID in rl_Relationship:
                            if parentClassEntity['@id']==linkedUID['@id']:
                                childNodeUID = KnowledgeGraph.NodeNumberByUID(KnowledgeGraph.SubGraphBySubclasses(graph,childObjectsType),childClassEntity['@id'])
                                parentNodeUID = KnowledgeGraph.NodeNumberByUID(KnowledgeGraph.SubGraphBySubclasses(graph,parentObjectsType),parentClassEntity['@id'])
                                graph.add_edge(childNodeUID,parentNodeUID,label=relationshipName)
                except:
                    if not silent:
                        print(f'Error: Impossible to link {childClassEntity}')
            
            # Other object types
            else:  
                try:
                    if len(str(rl))>3:
                        rl_Relationship = rl[relationshipName]
                        for parentClassEntity in parentObjects:
                            for linkedUID in rl_Relationship:
                                if parentClassEntity['@id']==linkedUID['@id']:
                                    childNodeUID = KnowledgeGraph.NodeNumberByUID(graph,childClassEntity['@id'])
                                    parentNodeUID = KnowledgeGraph.NodeNumberByUID(graph,parentClassEntity['@id'])
                                    graph.add_edge(childNodeUID,parentNodeUID,label=relationshipName)
                except Exception as e:
                    if not silent:
                        print(f'KnowledgeGraph.AddEdgeByType() - Error {e}')

        return graph
       
    @staticmethod
    def AddNodeByType(graph=None, objects=[], objectsType=None, propertiesAsNodes=False, kpisAsNodes=False):
        """
        Add nodes to a graph based on entities of a particular class in the data model.

        Parameters:
        - objects (list): List of object entities of a specific class.
        - subclass (str): Prefix for the class (e.g., 'pt', 'ps').
        - graph (nx.Graph): The networkx graph to which nodes will be added.
        - propertiesAsNodes (bool): If True, add Property nodes as individual nodes (default is False).
        - kpisAsNodes (bool): If True, add KPI nodes as individual nodes (default is False).

        Returns:
        - None

        Example:
        >>> class_entities = [...]  # List of entities of a specific class
        >>> graph = nx.Graph()  # Create an empty networkx graph
        >>> AddNodeByType(class_entities, 'pt', graph, propertiesAsNodes=True)
        >>> # The graph is updated with nodes based on the given class entities
        """

        i=0
        try:
            i=max(graph.nodes())+1
        except:
            i=0

        if objectsType=='ptSM':
            for classEntity in objects:
                graph.add_node(i,label='ptSM', UID=classEntity['@id'],timestamp=classEntity['timestamp'],value=classEntity['value'])
                i=i+1

        elif objectsType[:2]=='pt':
            for classEntity in objects:
                graph.add_node(i, label=objectsType, UID=classEntity['@id'], 
                            ts_Timestamp=classEntity['timestamp'],vl_Value=classEntity['value'])
                i=i+1
        
        elif objectsType=='ifc:IfcPropertySet':
            for classEntity in objects:
                PSetUID = i
                graph.add_node(i, label=objectsType, UID=classEntity['@id'],hasProperties=classEntity['ifc:HasProperties'])
                i=i+1
                if propertiesAsNodes==True:
                    props = classEntity['ifc:HasProperties']
                    for prop in props:
                        graph.add_node(i,label='pr',UID=prop)
                        graph.add_edge(i,PSetUID,label='IsPropertyOf')
                        i=i+1

        elif objectsType=='btwin:KPISet':
            for classEntity in objects:
                KPISetUID = i
                graph.add_node(i, label=objectsType, UID=classEntity['@id'],hasKPIs=classEntity['btwin:hasKPIs'])
                i=i+1

        elif objectsType=='eko:KPI':
            for classEntity in objects:
                KPISetUID = i
                graph.add_node(i, label=objectsType, UID=classEntity['@id'],
                            timestamp=classEntity['relationships']['eko:hasEvaluationTimestep'],name=classEntity['name'],nominalValue=classEntity['nominalValue'])
                i=i+1
                if kpisAsNodes==True:
                    kpis = classEntity['btwin:hasKPIs']
                    for kpi in kpis:
                        graph.add_node(i,label='kp',UID=kpi)
                        graph.add_edge(i,KPISetUID,label='IsKPIOf')
                        i=i+1
            
        else:
            for classEntity in objects:
                uid = classEntity['@id']
                name = None
                try:
                    name = classEntity['name']
                    graph.add_node(i, label=objectsType, UID=uid, name=name)
                except Exception as e:
                    graph.add_node(i, label=objectsType, UID=uid)
                i=i+1
        
        return graph
    
    @staticmethod
    def ByJSONLDData(JSONLD={},propertiesAsNodes=False,kpisAsNodes=False,silent=True):

        """
            Generate a networkx graph based on BTwin data model.

            Parameters:
            - dataModel (list): List of entities in the data model.
            - propertiesAsNodes (bool): If True, add PropertySet nodes as individual nodes (default is False).
            - KPIsAsNodes (bool): If True, add KPISet nodes as individual nodes (default is False).

            Returns:
            - nx.Graph: A networkx graph representing the data model.

            Example:
            >>> data_model = DataModel.ByObjects()
            >>> graph = ByDataModel(data_model, propertiesAsNodes=True, KPIsAsNodes=True)
        """

        # Import libraries
        import networkx as nx
            
        #Empty graph
        G = nx.Graph()
        tpSKs = []
        tpBCs = []
        tpDSs = []
        tpSTs = []
        tpBLs = []
        tpBSs = []
        tpZNs,tpEZNs,tpFZNs = [],[],[]
        tpSPs = []
        inFCs = []
        inAPs = []

        eqSYs = []
        eqHVACsys,eqDHWsys,eqLghtSys=[],[],[]

        eqSSs = []

        eqDVs = []
        eqAirConds,eqHeatPumps,eqFanCoils,eqRads,eqSpHtrs,eqElBoils=[],[],[],[],[],[]
        eqLmns=[]

        ptSNs = []
        ptSMs = []
        ptBIs = []
        psPSs = []
        ksKSs = []
        eqSNs = []
        eqAHUs = []
        eqEMs=[]


        
        ptSNsTem,ptSNsHum,ptSNsLum,ptSNsPres,ptSNsCO2=[],[],[],[],[]
        ptSNsPM1,ptSNsPM25,ptSNsPM4,ptSNsPM10,ptSNsTVOC=[],[],[],[],[]
        ptSNsAirFlow,ptSNsSpeed,ptSNsCurrent=[],[],[]
        ptEEUs,ptEECs=[],[]

        documents=[]
        scenarios=[]
        kpiSets=[]

            
        j=0
        for entity in JSONLD['@graph']:
            if entity['@type']=='brick:Portfolio':
                tpSKs.append(entity)
            if entity['@type']=='digitman:BuildingCluster':
                tpBCs.append(entity)
            elif entity['@type']=='brick:Region':
                tpDSs.append(entity)
                entity['nodeUID'] = j
            elif entity['@type']=='bot:Site':
                tpSTs.append(entity)
                entity['nodeUID'] = j
            elif entity['@type']=='bot:Building':
                tpBLs.append(entity)
                entity['nodeUID'] = j
            elif entity['@type']=='bot:Storey':
                tpBSs.append(entity)
                entity['nodeUID'] = j
            elif entity['@type']=='brick:Zone':
                tpZNs.append(entity)
                entity['nodeUID'] = j
            elif entity['@type']=='brick:Energy_Zone':
                tpEZNs.append(entity)
                entity['nodeUID'] = j
            elif entity['@type']=='brick:Fire_Zone':
                tpFZNs.append(entity)
                entity['nodeUID'] = j
            elif entity['@type']=='bot:Space':
                tpSPs.append(entity)
                entity['nodeUID'] = j
            elif entity['@type']=='bot:Interface':
                inFCs.append(entity)
                entity['nodeUID'] = j
            elif entity['@type']=='top:Aperture':
                inAPs.append(entity)
                entity['nodeUID'] = j

            elif entity['@type']=='brick:System':
                eqSYs.append(entity)
                entity['nodeUID'] = j
            elif entity['@type']=='brick:HVAC_System':
                eqHVACsys.append(entity)
                entity['nodeUID'] = j
            elif entity['@type']=='brick:Domestic_Hot_Water_System':
                eqDHWsys.append(entity)
                entity['nodeUID'] = j
            elif entity['@type']=='brick:Lighting_System':
                eqLghtSys.append(entity)
                entity['nodeUID'] = j

            elif entity['@type']=='eqSS':
                eqSSs.append(entity)
                entity['nodeUID'] = j
            elif entity['@type']=='eqDV':
                eqDVs.append(entity)
                entity['nodeUID'] = j

            elif entity['@type']=='brick:Wall_Air_Conditioner':
                eqAirConds.append(entity)
                entity['nodeUID'] = j
            elif entity['@type']=='brick:Packaged_Heat_Pump':
                eqHeatPumps.append(entity)
                entity['nodeUID'] = j
            elif entity['@type']=='brick:Fan_Coil_Unit':
                eqFanCoils.append(entity)
                entity['nodeUID'] = j
            elif entity['@type']=='brick:Radiator':
                eqRads.append(entity)
                entity['nodeUID'] = j
            elif entity['@type']=='brick:Space_Heater':
                eqSpHtrs.append(entity)
                entity['nodeUID'] = j
            elif entity['@type']=='brick:Electric_Boiler':
                eqElBoils.append(entity)
                entity['nodeUID'] = j
            elif entity['@type']=='brick:Luminaire':
                eqLmns.append(entity)
                entity['nodeUID'] = j

            elif entity['@type']=='ptSN':
                ptSNs.append(entity)
                entity['nodeUID'] = j
            elif entity['@type']=='ptSM':
                ptSMs.append(entity)
                entity['nodeUID'] = j
            elif entity['@type']=='ptBI':
                ptBIs.append(entity)
                entity['nodeUID'] = j
            elif entity['@type']=='ifc:IfcPropertySet':
                psPSs.append(entity)
                entity['nodeUID'] = j
            elif entity['@type']=='eko:KPI':
                ksKSs.append(entity)
                entity['nodeUID'] = j
            
            elif entity['@type']=='ifc:Sensor':
                eqSNs.append(entity)
                entity['nodeUID'] = j
            elif entity['@type']=='brick:Electrical_Meter':
                eqEMs.append(entity)
                entity['nodeUID'] = j

            elif entity['@type']=='brick:Temperature_Sensor':
                ptSNsTem.append(entity)
                entity['nodeUID'] = j
            elif entity['@type']=='brick:Humidity_Sensor':
                ptSNsHum.append(entity)
                entity['nodeUID'] = j
            elif entity['@type']=='brick:Luminance_Sensor':
                ptSNsLum.append(entity)
                entity['nodeUID'] = j
            elif entity['@type']=='brick:Pressure_Sensor':
                ptSNsPres.append(entity)
                entity['nodeUID'] = j
            elif entity['@type']=='brick:CO2_Sensor':
                ptSNsCO2.append(entity)
                entity['nodeUID'] = j
            
            elif entity['@type']=='brick:Air_Flow_Sensor':
                ptSNsAirFlow.append(entity)
                entity['nodeUID'] = j
            elif entity['@type']=='brick:Speed_Sensor':
                ptSNsSpeed.append(entity)
                entity['nodeUID'] = j
            elif entity['@type']=='brick:Current_Sensor':
                ptSNsCurrent.append(entity)
                entity['nodeUID'] = j
            
            elif entity['@type']=='brick:Air_Handling_Unit':
                eqAHUs.append(entity)
                entity['nodeUID'] = j

            elif entity['@type']=='brick:PM1_Sensor':
                ptSNsPM1.append(entity)
                entity['nodeUID'] = j
            elif entity['@type']=='brick:PM2.5_Sensor':
                ptSNsPM25.append(entity)
                entity['nodeUID'] = j
            elif entity['@type']=='digitman:PM4_Sensor':
                ptSNsPM4.append(entity)
                entity['nodeUID'] = j
            elif entity['@type']=='brick:PM10_Sensor':
                ptSNsPM10.append(entity)
                entity['nodeUID'] = j
            elif entity['@type']=='brick:TVOC_Sensor':
                ptSNsTVOC.append(entity)
                entity['nodeUID'] = j

            elif entity['@type']=='brick:Electricity_Energy_Usage_Sensor':
                ptEEUs.append(entity)
                entity['nodeUID'] = j
            elif entity['@type']=='btwin:Electricity_Energy_Cost_Sensor':
                ptEECs.append(entity)
                entity['nodeUID'] = j

            elif entity['@type']=='btwin:Document':
                documents.append(entity)
                entity['nodeUID']=j
            elif entity['@type']=='btwin:Scenario':
                scenarios.append(entity)
                entity['nodeUID']=j      
            elif entity['@type']=='btwin:KPISet':
                kpiSets.append(entity)
                entity['nodeUID']=j            
            j=j+1

         # Add Portfolio Nodes
        KnowledgeGraph.AddNodeByType(G,tpSKs,'brick:Portfolio')
        

        # Add Cluster Nodes
        KnowledgeGraph.AddNodeByType(G,tpBCs,'digitman:BuildingCluster')
        KnowledgeGraph.AddEdgeByTypes(G,tpBCs,'digitman:BuildingCluster',tpSKs,'brick:Portfolio','brick:hasLocation')

        # Add Region Nodes
        KnowledgeGraph.AddNodeByType(G,tpDSs,'brick:Region')
        KnowledgeGraph.AddEdgeByTypes(G,tpDSs,'brick:Region',tpSKs,'brick:Portfolio','brick:hasLocation')

            # Add Site Nodes
        KnowledgeGraph.AddNodeByType(G,tpSTs,'bot:Site')
            # Add Site Edges
        KnowledgeGraph.AddEdgeByTypes(G,tpSTs,'bot:Site',tpDSs,'brick:Region','brick:hasLocation')
        KnowledgeGraph.AddEdgeByTypes(G,tpSTs,'bot:Site',tpSKs,'brick:Portfolio','brick:hasLocation')

            # Add Building Nodes
        KnowledgeGraph.AddNodeByType(G,tpBLs,'bot:Building')
            # Add Building Edges
        KnowledgeGraph.AddEdgeByTypes(G,tpBLs,'bot:Building',tpSTs,'bot:Site','brick:hasLocation')
        KnowledgeGraph.AddEdgeByTypes(G,tpBLs,'bot:Building',tpBCs,'digitman:BuildingCluster','brick:hasLocation')

            # Add BuildingStorey Nodes    
        KnowledgeGraph.AddNodeByType(G,tpBSs,'bot:Storey')
            # Add BuildingStorey Edges    
        KnowledgeGraph.AddEdgeByTypes(G,tpBSs,'bot:Storey',tpBLs,'bot:Building','brick:hasLocation')

            # Add Zone Nodes 
        KnowledgeGraph.AddNodeByType(G,tpZNs,'brick:Zone')
        KnowledgeGraph.AddNodeByType(G,tpEZNs,'brick:Energy_Zone')
        KnowledgeGraph.AddNodeByType(G,tpFZNs,'brick:Fire_Zone')
            # Add Zone Edges 
        KnowledgeGraph.AddEdgeByTypes(G,tpZNs,'brick:Zone',tpBLs,'bot:Building','brick:hasLocation')
        KnowledgeGraph.AddEdgeByTypes(G,tpEZNs,'brick:Energy_Zone',tpBLs,'bot:Building','brick:hasLocation')
        KnowledgeGraph.AddEdgeByTypes(G,tpFZNs,'brick:Fire_Zone',tpBLs,'bot:Building','brick:hasLocation')
        KnowledgeGraph.AddEdgeByType(G,tpZNs,'IsAdjacentTo')
        KnowledgeGraph.AddEdgeByType(G,tpZNs,'HasPassageTo')   
            
            # Add Space Nodes 
        KnowledgeGraph.AddNodeByType(G,tpSPs,'bot:Space')
            # Add Space Edges 
        if len(tpBSs)>0:
            KnowledgeGraph.AddEdgeByTypes(G,tpSPs,'bot:Space',tpBSs,'bot:Storey','brick:hasLocation')
        if len(tpZNs)>0:
            KnowledgeGraph.AddEdgeByTypes(G,tpSPs,'bot:Space',tpZNs,'brick:Zone','brick:hasLocation')
        if len(tpEZNs)>0:
            KnowledgeGraph.AddEdgeByTypes(G,tpSPs,'bot:Space',tpEZNs,'brick:Energy_Zone','brick:hasLocation')
        if len(tpFZNs)>0:
            KnowledgeGraph.AddEdgeByTypes(G,tpSPs,'bot:Space',tpFZNs,'brick:Fire_Zone','brick:hasLocation')

        KnowledgeGraph.AddEdgeByType(G,tpSPs,'IsAdjacentTo')
        KnowledgeGraph.AddEdgeByType(G,tpSPs,'HasPassageTo')
            
            # Add Face Nodes 
        KnowledgeGraph.AddNodeByType(G,inFCs,'bot:Interface')
            # Add Face Edges
        KnowledgeGraph.AddEdgeByTypes(G,inFCs,'bot:Interface',tpSPs,'bot:Space','bot:isInterface')
        KnowledgeGraph.AddEdgeByType(G,inFCs,'brick:hasLocation')
            
            # Add Aperture Nodes 
        KnowledgeGraph.AddNodeByType(G,inAPs,'top:Aperture')
            # Add Aperture Edges
        KnowledgeGraph.AddEdgeByTypes(G,inAPs,'top:Aperture',tpSPs,'bot:Space','bot:isInterface')

            # Add System Nodes 
        KnowledgeGraph.AddNodeByType(G,eqSYs,'brick:System')
            # Add System Edges
        try:
            KnowledgeGraph.AddEdgeByTypes(G,eqSYs,'brick:System',tpBLs,'bot:Building','brick:feeds')
        except:
            a=0
        # Specific systems
            # HVAC SYSTEM
        KnowledgeGraph.AddNodeByType(G,eqHVACsys,'brick:HVAC_System')
        KnowledgeGraph.AddEdgeByTypes(G,eqHVACsys,'brick:HVAC_System',tpBLs,'bot:Building','brick:feeds')
            # DHW SYSTEM
        KnowledgeGraph.AddNodeByType(G,eqDHWsys,'brick:Domestic_Hot_Water_System')
        KnowledgeGraph.AddEdgeByTypes(G,eqDHWsys,'brick:Domestic_Hot_Water_System',tpBLs,'bot:Building','brick:feeds')
            # LIGHTING SYSTEM
        KnowledgeGraph.AddNodeByType(G,eqLghtSys,'brick:Lighting_System')
        KnowledgeGraph.AddEdgeByTypes(G,eqLghtSys,'brick:Lighting_System',tpBLs,'bot:Building','brick:feeds')

            # Add SubSystem Nodes 
        KnowledgeGraph.AddNodeByType(G,eqSSs,'eqSS')
            # Add SubSystem Edges
        KnowledgeGraph.AddEdgeByTypes(G,eqSSs,'eqSS',tpZNs,'brick:Zone','brick:feeds')
        KnowledgeGraph.AddEdgeByTypes(G,eqSSs,'eqSS',tpSPs,'bot:Space','brick:feeds')
        KnowledgeGraph.AddEdgeByTypes(G,eqSSs,'eqSS',eqSYs,'brick:System','brick:isPartOf')
            
            # Add Device Nodes 
        KnowledgeGraph.AddNodeByType(G,eqDVs,'eqDV')
        KnowledgeGraph.AddNodeByType(G,eqSNs,'ifc:Sensor')
            # Add Device Edges
        try:
            KnowledgeGraph.AddEdgeByTypes(G,eqSNs,'ifc:Sensor',eqSYs,'brick:System','brick:isPartOf')
        except:
            a = 0
        KnowledgeGraph.AddEdgeByTypes(G,eqSNs,'ifc:Sensor',tpSPs,'bot:Space','brick:hasLocation')
        KnowledgeGraph.AddEdgeByTypes(G,eqSNs,'ifc:Sensor',tpBSs,'bot:Building','brick:hasLocation')
        try:
            KnowledgeGraph.AddEdgeByTypes(G,eqDVs,'eqDV',eqSSs,'eqSS','brick:isPartOf')
        except:
            a=0

            # Add specific Equipment decives' nodes
                # AIR CONDITIONERS
        KnowledgeGraph.AddNodeByType(G,eqAirConds,'brick:Wall_Air_Conditioner')
        KnowledgeGraph.AddEdgeByTypes(G,eqAirConds,'brick:Wall_Air_Conditioner',tpSPs,'bot:Space','brick:hasLocation')  
        KnowledgeGraph.AddEdgeByTypes(G,eqAirConds,'brick:Wall_Air_Conditioner',eqHVACsys,'brick:HVAC_System','brick:isPartOf')    
                # FAN COILS
        KnowledgeGraph.AddNodeByType(G,eqFanCoils,'brick:Fan_Coil_Unit')
        KnowledgeGraph.AddEdgeByTypes(G,eqFanCoils,'brick:Fan_Coil_Unit',tpSPs,'bot:Space','brick:hasLocation')  
        KnowledgeGraph.AddEdgeByTypes(G,eqFanCoils,'brick:Fan_Coil_Unit',eqHVACsys,'brick:HVAC_System','brick:isPartOf')   
                # RADIATORS
        KnowledgeGraph.AddNodeByType(G,eqRads,'brick:Radiator')
        KnowledgeGraph.AddEdgeByTypes(G,eqRads,'brick:Radiator',tpSPs,'bot:Space','brick:hasLocation')  
        KnowledgeGraph.AddEdgeByTypes(G,eqRads,'brick:Radiator',eqHVACsys,'brick:HVAC_System','brick:isPartOf')   
                # SPACE HEATERS
        KnowledgeGraph.AddNodeByType(G,eqSpHtrs,'brick:Space_Heater')
        KnowledgeGraph.AddEdgeByTypes(G,eqSpHtrs,'brick:Space_Heater',tpSPs,'bot:Space','brick:hasLocation')  
        KnowledgeGraph.AddEdgeByTypes(G,eqSpHtrs,'brick:Space_Heater',eqHVACsys,'brick:HVAC_System','brick:isPartOf') 
                # HEAT PUMPS
        KnowledgeGraph.AddNodeByType(G,eqHeatPumps,'brick:Packaged_Heat_Pump')
        KnowledgeGraph.AddEdgeByTypes(G,eqHeatPumps,'brick:Packaged_Heat_Pump',tpSPs,'bot:Space','brick:hasLocation')  
        KnowledgeGraph.AddEdgeByTypes(G,eqHeatPumps,'brick:Packaged_Heat_Pump',eqHVACsys,'brick:HVAC_System','brick:isPartOf')

                # ELECTRIC BOILER
        KnowledgeGraph.AddNodeByType(G,eqElBoils,'brick:Electric_Boiler')
        KnowledgeGraph.AddEdgeByTypes(G,eqElBoils,'brick:Electric_Boiler',tpSPs,'bot:Space','brick:hasLocation')  
        KnowledgeGraph.AddEdgeByTypes(G,eqElBoils,'brick:Electric_Boiler',eqDHWsys,'brick:Domestic_Hot_Water_System','brick:isPartOf') 

                # LUMINAIRE
        KnowledgeGraph.AddNodeByType(G,eqLmns,'brick:Luminaire')
        KnowledgeGraph.AddEdgeByTypes(G,eqLmns,'brick:Luminaire',tpSPs,'bot:Space','brick:hasLocation')  
        KnowledgeGraph.AddEdgeByTypes(G,eqLmns,'brick:Luminaire',eqLghtSys,'brick:Lighting_System','brick:isPartOf') 

        

        try:
            # Add Meter Nodes
            KnowledgeGraph.AddNodeByType(G,eqEMs,'brick:Electrical_Meter') 
            # Add Meter Edges
            KnowledgeGraph.AddEdgeByTypes(G,eqEMs,'brick:Electrical_Meter',tpBLs,'bot:Building','brick:feeds')
        except:
            if not silent:
                print('Error: Impossible to link "brick:Electrical_Meter" with "bot:Building" through "brick:feeds"')
        
        KnowledgeGraph.AddEdgeByType(G,eqDVs,'brick:feeds')
        KnowledgeGraph.AddEdgeByTypes(G,eqDVs,'eqDV',tpBLs,'bot:Building','brick:feeds')
        KnowledgeGraph.AddEdgeByType(G,eqDVs,'IsFedBy')
            
            # Add Sensor Nodes 
        KnowledgeGraph.AddNodeByType(G,ptSNs,'ptSN')
        KnowledgeGraph.AddNodeByType(G,ptSNsTem,'brick:Temperature_Sensor')
        KnowledgeGraph.AddNodeByType(G,ptSNsHum,'brick:Humidity_Sensor')
        KnowledgeGraph.AddNodeByType(G,ptSNsLum,'brick:Luminance_Sensor')
        KnowledgeGraph.AddNodeByType(G,ptSNsPres,'brick:Pressure_Sensor')
        KnowledgeGraph.AddNodeByType(G,ptSNsCO2,'brick:CO2_Sensor')

        KnowledgeGraph.AddNodeByType(G,ptSNsPM1,'brick:PM1_Sensor')
        KnowledgeGraph.AddNodeByType(G,ptSNsPM25,'brick:PM2.5_Sensor')
        KnowledgeGraph.AddNodeByType(G,ptSNsPM4,'digitman:PM4_Sensor')
        KnowledgeGraph.AddNodeByType(G,ptSNsPM10,'brick:PM10_Sensor')
        KnowledgeGraph.AddNodeByType(G,ptSNsTVOC,'brick:TVOC_Sensor')

            # Add Equipment Point Nodes
        KnowledgeGraph.AddNodeByType(G,ptSNsAirFlow,'brick:Air_Flow_Sensor')
        KnowledgeGraph.AddNodeByType(G,ptSNsSpeed,'brick:Speed_Sensor')
        KnowledgeGraph.AddNodeByType(G,ptSNsCurrent,'brick:Current_Sensor')

            # Add Meter Point Nodes
        try:
            KnowledgeGraph.AddNodeByType(G,ptEEUs,'brick:Electricity_Energy_Usage_Sensor')
            KnowledgeGraph.AddEdgeByTypes(G,ptEEUs,'brick:Electricity_Energy_Usage_Sensor',eqEMs,'brick:Electrical_Meter','brick:isPointOf')
        except:
            if not silent:
                print('Error: impossible to add "brick:Electricity_Energy_Usage_Sensor" nodes and edges')

        try:
            KnowledgeGraph.AddNodeByType(G,ptEECs,'btwin:Electricity_Energy_Cost_Sensor')
            KnowledgeGraph.AddEdgeByTypes(G,ptEECs,'btwin:Electricity_Energy_Cost_Sensor',eqEMs,'brick:Electrical_Meter','brick:isPointOf')
        except: 
            if not silent:
                print('Error: impossible to add "btwin:Electricity_Energy_Cost_Sensor" nodes and edges')

        # Add HVAC Nodes
        KnowledgeGraph.AddNodeByType(G,eqAHUs,'brick:Air_Handling_Unit')
        try:
            KnowledgeGraph.AddEdgeByTypes(G,eqAHUs,'brick:Air_Handling_Unit',tpSPs,'bot:Space','brick:feeds')
        except:
            if not silent:
                print("Error -KnowledgeGraph.AddEdgeByTypes(G,eqAHUs,'brick:Air_Handling_Unit',tpSPs,'bot:Space','brick:feeds')")
        KnowledgeGraph.AddEdgeByTypes(G,eqAHUs,'brick:Air_Handling_Unit',eqSYs,'brick:System','brick:isPartOf')
        KnowledgeGraph.AddEdgeByTypes(G,eqAHUs,'brick:Air_Handling_Unit',eqHVACsys,'brick:HVAC_System','brick:isPartOf')

            # Add Sensor Edges
        KnowledgeGraph.AddEdgeByTypes(G,ptSNs,'ptSN',eqDVs,'eqDV','brick:isPointOf')
        KnowledgeGraph.AddEdgeByTypes(G,ptSNsTem,'brick:Temperature_Sensor',eqSNs,'ifc:Sensor','brick:isPointOf')
        KnowledgeGraph.AddEdgeByTypes(G,ptSNsHum,'brick:Humidity_Sensor',eqSNs,'ifc:Sensor','brick:isPointOf')
        KnowledgeGraph.AddEdgeByTypes(G,ptSNsLum,'brick:Luminance_Sensor',eqSNs,'ifc:Sensor','brick:isPointOf')
        KnowledgeGraph.AddEdgeByTypes(G,ptSNsPres,'brick:Pressure_Sensor',eqSNs,'ifc:Sensor','brick:isPointOf')
        KnowledgeGraph.AddEdgeByTypes(G,ptSNsCO2,'brick:CO2_Sensor',eqSNs,'ifc:Sensor','brick:isPointOf')

        KnowledgeGraph.AddEdgeByTypes(G,ptSNsPM1,'brick:PM1_Sensor',eqSNs,'ifc:Sensor','brick:isPointOf')
        KnowledgeGraph.AddEdgeByTypes(G,ptSNsPM25,'brick:PM2.5_Sensor',eqSNs,'ifc:Sensor','brick:isPointOf')
        KnowledgeGraph.AddEdgeByTypes(G,ptSNsPM4,'digitman:PM4_Sensor',eqSNs,'ifc:Sensor','brick:isPointOf')
        KnowledgeGraph.AddEdgeByTypes(G,ptSNsPM10,'brick:PM10_Sensor',eqSNs,'ifc:Sensor','brick:isPointOf')
        KnowledgeGraph.AddEdgeByTypes(G,ptSNsTVOC,'brick:TVOC_Sensor',eqSNs,'ifc:Sensor','brick:isPointOf')

            # Add Air Handling Units Sensor Edges
        KnowledgeGraph.AddEdgeByTypes(G,ptSNsTem,'brick:Temperature_Sensor',eqAHUs,'brick:Air_Handling_Unit','brick:isPointOf')
        KnowledgeGraph.AddEdgeByTypes(G,ptSNsAirFlow,'brick:Air_Flow_Sensor',eqAHUs,'brick:Air_Handling_Unit','brick:isPointOf')
        KnowledgeGraph.AddEdgeByTypes(G,ptSNsSpeed,'brick:Speed_Sensor',eqAHUs,'Air_Handling_Unit','brick:isPointOf')
        KnowledgeGraph.AddEdgeByTypes(G,ptSNsCurrent,'brick:Current_Sensor',eqAHUs,'Air_Handling_Unit','brick:isPointOf')
        
            # Add Simulation Nodes 
        KnowledgeGraph.AddNodeByType(G,ptSMs,'ptSM')
            # Add Simulation Edges
        KnowledgeGraph.AddEdgeByTypes(G,ptSMs,'ptSM',tpZNs,'brick:Zone','brick:isPointOf')
        KnowledgeGraph.AddEdgeByTypes(G,ptSMs,'ptSM',tpSPs,'bot:Space','brick:isPointOf')
        KnowledgeGraph.AddEdgeByTypes(G,ptSMs,'ptSM',tpSPs,'bot:Space','brick:isPointOf')
            
            # Add Bill Nodes 
        KnowledgeGraph.AddNodeByType(G,ptBIs,'ptBI')
            # Add Bill Edges
        KnowledgeGraph.AddEdgeByTypes(G,ptBIs,'ptBI',tpZNs,'brick:Zone','brick:isPointOf')
        KnowledgeGraph.AddEdgeByTypes(G,ptBIs,'ptBI',tpSPs,'bot:Space','brick:isPointOf')
        KnowledgeGraph.AddEdgeByTypes(G,ptBIs,'ptBI',tpSPs,'bot:Space','brick:isPointOf')
        KnowledgeGraph.AddEdgeByTypes(G,ptBIs,'ptBI',eqDVs,'eqDV','brick:isPointOf')

        # Add Scenario Nodes
        KnowledgeGraph.AddNodeByType(G,scenarios,'btwin:Scenario')
        #print('Scenarios:',scenarios)

        # Add Document Nodes
        KnowledgeGraph.AddNodeByType(G,documents,'btwin:Document')
        try:
            KnowledgeGraph.AddEdgeByTypes(G,documents,'btwin:Document',tpBLs,'bot:Building','btwin:isDocumentOf')
        except Exception as e:
            if not silent:
                print(f'Error: impossible to add "btwin:Document" nodes and edges {e}')
        try:
            KnowledgeGraph.AddEdgeByTypes(G,documents,'btwin:Document',scenarios,'btwin:Scenario','btwin:hasScenario')
        except Exception as e:
            if not silent:
                print(f'Error: impossible to add "btwin:Document" nodes and edges {e}')

        # Add KPISet Nodes
        KnowledgeGraph.AddNodeByType(G,kpiSets,'btwin:KPISet')

        # eko:hasAssociatedObject
        try:
            KnowledgeGraph.AddEdgeByTypes(G,kpiSets,'btwin:KPISet',tpBLs,'bot:Building','eko:hasAssociatedObject')
        except Exception as e:
            if not silent:
                print(f'Error: impossible to add "btwin:KPISet" nodes and edges {e}')
        
        try:
            KnowledgeGraph.AddEdgeByTypes(G,kpiSets,'btwin:KPISet',tpBSs,'bot:Storey','eko:hasAssociatedObject')
        except Exception as e:
            if not silent:
                print(f'Error: impossible to add "btwin:KPISet" nodes and edges {e}')
        
        try:
            KnowledgeGraph.AddEdgeByTypes(G,kpiSets,'btwin:KPISet',tpSPs,'bot:Space','eko:hasAssociatedObject')
        except Exception as e:
            if not silent:
                print(f'Error: impossible to add "btwin:KPISet" nodes and edges {e}')       
        
        try:
            KnowledgeGraph.AddEdgeByTypes(G,kpiSets,'btwin:KPISet',tpFZNs,'brick:Fire_Zone','eko:hasAssociatedObject')
        except Exception as e:
            if not silent:
                print(f'Error: impossible to add "btwin:KPISet" nodes and edges {e}')

        try:
            KnowledgeGraph.AddEdgeByTypes(G,kpiSets,'btwin:KPISet',inAPs,'top:Aperture','eko:hasAssociatedObject')
        except Exception as e:
            if not silent:
                print(f'Error: impossible to add "btwin:KPISet" nodes and edges {e}')


        # btwin:hasScenario
        try:
            KnowledgeGraph.AddEdgeByTypes(G,kpiSets,'btwin:KPISet',scenarios,'btwin:Scenario','btwin:hasScenario')
        except Exception as e:
            if not silent:
                print(f'Error: impossible to add "btwin:KPISet" nodes and edges {e}')


        # Add PropertySet Nodes
        KnowledgeGraph.AddNodeByType(G,psPSs,'ifc:IfcPropertySet',propertiesAsNodes=propertiesAsNodes)
        if len(psPSs)>0:
            try:
                KnowledgeGraph.AddEdgeByTypes(G,tpDSs,'brick:Region',psPSs,'ifc:IfcPropertySet','ifc:HasPropertySet')
            except:
                if not silent:
                    print('No PSets found for brick:Region')
            try:
                KnowledgeGraph.AddEdgeByTypes(G,tpSTs,'bot:Site',psPSs,'ifc:IfcPropertySet','ifc:HasPropertySet')
            except:
                if not silent:
                    print('No PSets found for bot:Site')
            try:
                KnowledgeGraph.AddEdgeByTypes(G,tpBLs,'bot:Building',psPSs,'ifc:IfcPropertySet','ifc:HasPropertySet')
            except:
                if not silent:
                    print('No PSets found for bot:Building')
            try:
                KnowledgeGraph.AddEdgeByTypes(G,tpSPs,'bot:Storey',psPSs,'ifc:IfcPropertySet','ifc:HasPropertySet')
            except:
                if not silent:
                    print('No PSets found for bot:Storey')
            try:
                KnowledgeGraph.AddEdgeByTypes(G,tpZNs,'brick:Zone',psPSs,'ifc:IfcPropertySet','ifc:HasPropertySet')
            except:
                if not silent:
                    print('No PSets found for brick:Zone')
            try:
                KnowledgeGraph.AddEdgeByTypes(G,tpSPs,'bot:Space',psPSs,'ifc:IfcPropertySet','ifc:HasPropertySet')
            except:
                if not silent:
                    print('No PSets found for bot:Space')
            try:
                KnowledgeGraph.AddEdgeByTypes(G,inAPs,'top:Aperture',psPSs,'ifc:IfcPropertySet','ifc:HasPropertySet')
            except:
                if not silent:
                    print('No PSets found for top:Aperture')
        try:
                # Add PropertySet Edges
            KnowledgeGraph.AddEdgeByTypes(G,psPSs,'ifc:IfcPropertySet',tpDSs,'brick:Region','ifc:HasPropertySets')
            KnowledgeGraph.AddEdgeByTypes(G,psPSs,'ifc:IfcPropertySet',tpSTs,'bot:Site','ifc:HasPropertySets')
            KnowledgeGraph.AddEdgeByTypes(G,psPSs,'ifc:IfcPropertySet',tpBLs,'bot:Building','ifc:HasPropertySets')
            KnowledgeGraph.AddEdgeByTypes(G,psPSs,'ifc:IfcPropertySet',tpBSs,'bot:Storey','ifc:HasPropertySets')
            KnowledgeGraph.AddEdgeByTypes(G,psPSs,'ifc:IfcPropertySet',tpZNs,'brick:Zone','ifc:HasPropertySets')
            KnowledgeGraph.AddEdgeByTypes(G,psPSs,'ifc:IfcPropertySet',tpSPs,'bot:Space','ifc:HasPropertySets')
            KnowledgeGraph.AddEdgeByTypes(G,psPSs,'ifc:IfcPropertySet',inFCs,'inFC','ifc:HasPropertySets')
            KnowledgeGraph.AddEdgeByTypes(G,psPSs,'ifc:IfcPropertySet',inAPs,'inAP','ifc:HasPropertySets')
            KnowledgeGraph.AddEdgeByTypes(G,psPSs,'ifc:IfcPropertySet',eqSYs,'brick:System','ifc:HasPropertySets')
            KnowledgeGraph.AddEdgeByTypes(G,psPSs,'ifc:IfcPropertySet',eqSSs,'eqSS','ifc:HasPropertySets')
            KnowledgeGraph.AddEdgeByTypes(G,psPSs,'ifc:IfcPropertySet',eqDVs,'eqDV','ifc:HasPropertySets')
        except:
            a=0
            #print('Please check if PSets have been added!')

            # Add KPISet Nodes
        KnowledgeGraph.AddNodeByType(G,ksKSs,'eko:KPI',kpisAsNodes=kpisAsNodes)
            # Add KPISet Edges
        KnowledgeGraph.AddEdgeByTypes(G,ksKSs,'eko:KPI',tpBLs,'bot:Building','eko:hasAssociatedObject')
        KnowledgeGraph.AddEdgeByTypes(G,ksKSs,'eko:KPI',tpSPs,'bot:Space','eko:hasAssociatedObject')
        KnowledgeGraph.AddEdgeByTypes(G,ksKSs,'eko:KPI',tpZNs,'brick:Zone','eko:hasAssociatedObject')
        KnowledgeGraph.AddEdgeByTypes(G,ksKSs,'eko:KPI',tpFZNs,'brick:Fire_Zone','eko:hasAssociatedObject')

        return G

    @staticmethod
    def ByJSONLDPath(jsonPath=None,propertiesAsNodes=False,kpisAsNodes=False):
        """
        Constructs a Knowledge Graph from JSON-LD data located at the specified JSON path.

        This method first reads JSON-LD data from a given file path, then utilizes this data to construct a Knowledge Graph. The graph construction can optionally consider specific JSON-LD properties and KPIs (Key Performance Indicators) as nodes within the graph, based on the provided boolean flags.

        Parameters:
        - jsonPath (str, optional): The file path to the JSON-LD data. If not provided, the method may raise an error or return None, depending on the implementation of `DataFormat.ByJSONPath`.
        - propertiesAsNodes (bool, optional): If True, properties within the JSON-LD data are treated as separate nodes in the Knowledge Graph. Defaults to False.
        - kpisAsNodes (bool, optional): If True, KPIs within the JSON-LD data are treated as separate nodes in the Knowledge Graph. Defaults to False.

        Returns:
        - nx.Graph: A NetworkX graph object constructed from the JSON-LD data, with nodes and edges representing the entities and their relationships as defined within the JSON-LD structure.

        Raises:
        - FileNotFoundError: If the `jsonPath` does not point to a valid file.
        - ValueError: If the provided JSON data is not in a valid JSON-LD format.

        Example:
            >>> graph = SomeClass.ByJSONLDPath(jsonPath='data/my_data.json', propertiesAsNodes=True, kpisAsNodes=True)
            >>> type(graph)
            <class 'networkx.classes.graph.Graph'>

        Note:
            This method requires the 'DataFormat' class for reading JSON-LD data and the 'KnowledgeGraph' class for constructing the graph. Ensure these classes are defined and properly handle the input data and graph construction, respectively.
        """
        from .DataFormat import DataFormat
        jsdonData = DataFormat.ByJSONPath(jsonPath=jsonPath)
        graph = KnowledgeGraph.ByJSONLDData(JSONLD=jsdonData,propertiesAsNodes=propertiesAsNodes,kpisAsNodes=kpisAsNodes)
        return graph


    


    @staticmethod
    def NodeByUID(graph=None, uid=None):
        """
        Returns the node with the given unique identifier (UID).

        Parameters:
        - G: A NetworkX graph.
        - uid: The unique identifier of the node to find.

        Returns:
        - The node with the specified UID, or None if no such node exists.
        """
        for node, data in graph.nodes(data=True):
            if data.get('UID') == uid:
                return graph.nodes(data=True)[node]
                break

    @staticmethod
    def NodeLinkedNodes(graph=None, nodeObjectUID=None, nodeNumber=None, linkedNodesType=None, relationshipName=None):
        """
        Retrieves the linked nodes of a specified type and relationship from a given node within a graph.

        This function searches for neighboring nodes linked to a specified node (identified either by its UID or number) 
        in the graph. It filters these nodes based on their type and the name of the relationship connecting them to the 
        specified node.

        Parameters:
            graph : networkx.Graph
                The graph object containing the nodes and edges. Must be an instance of a NetworkX Graph.
            
            nodeObjectUID : str, optional
                The unique identifier of the node whose linked nodes are to be found. If provided, `nodeNumber` is ignored.
            
            nodeNumber : int, optional
                The number of the node whose linked nodes are to be found. Used only if `nodeObjectUID` is not provided.
            
            linkedNodesType : str, optional
                The type of the linked nodes to retrieve. Only nodes of this type are included in the output.
            
            relationshipName : str, optional
                The name of the relationship between the nodes. Only nodes connected by an edge with this label are included.
        
        Returns:
            list of tuples
                A list where each tuple contains two elements: the number of the linked node and its data dictionary. Only nodes 
                that meet the specified type and relationship criteria are included.

        Examples:
            # Example usage to get linked 'bot:Space' nodes with 'brick:hasLocation' relationship from a node with UID 'myStorey'.
            linked_nodes = NodeLinkedNodes(graph=graph, nodeObjectUID='myStorey', linkedNodesType='bot:Space', relationshipName='brick:hasLocation')

        Notes:
            - Ensure that the `graph` parameter is correctly initialized as a NetworkX Graph object containing nodes and edges with
            appropriate 'label' attributes for both nodes and edges.
            - This function does not create a new graph or modify the existing one. It only reads data from the provided graph.
        """
        # Get the number of the searched node
        if nodeObjectUID is not None:
            nodeNumber = KnowledgeGraph.NodeNumberByUID(graph,nodeObjectUID)
        elif nodeNumber is not None:
            nodeNumber = nodeNumber
        
        # Initiate linked Nodes
        linkedNodes = []
        nodeNeighbors = graph.neighbors(nodeNumber)
        for nodeNeighbor in nodeNeighbors:
            nodeNeighborData = graph.nodes(data=True)[nodeNeighbor]
            # Filter by neighbor label
            if nodeNeighborData['label']==linkedNodesType:
                edgeData = graph[nodeNumber][nodeNeighbor]
                # Filter by edge label
                if relationshipName is not None:
                    if edgeData['label']==relationshipName:
                        linkedNodes.append((nodeNeighbor,nodeNeighborData))
                else:
                    linkedNodes.append((nodeNeighbor,nodeNeighborData))
        # Output
        return linkedNodes

    @staticmethod
    def ToNEO4J(
        btwinGraph=None,
        NEO4J_URI=None,
        NEO4J_USERNAME=None,
        NEO4J_PASSWORD=None
    ):
        """
        Writes the graph to a Neo4j database, replacing its content. The connection parameters
        default to the NEO4J_URI, NEO4J_USERNAME and NEO4J_PASSWORD environment variables.
        """
        # Import libraries
        import os
        from neo4j import GraphDatabase

        NEO4J_URI = NEO4J_URI or os.environ['NEO4J_URI']
        NEO4J_USERNAME = NEO4J_USERNAME or os.environ.get('NEO4J_USERNAME', 'neo4j')
        NEO4J_PASSWORD = NEO4J_PASSWORD or os.environ['NEO4J_PASSWORD']

        # Open connection
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

        # Function to delete all nodes and relationships in the database
        def delete_all(tx):
            tx.run("MATCH (n) DETACH DELETE n")

        # Function to create nodes in Neo4j with label and UID and all properties
        def create_node(tx, label, uid, properties):
            # Build the SET clause dynamically
            set_clauses = ", ".join([f"n.{key} = ${key}" for key in properties])
            query = f"MERGE (n:{label} {{UID: $uid}}) SET {set_clauses}"
            
            # Add UID to the properties dictionary
            properties['uid'] = uid

            # Execute the query with all properties
            tx.run(query, **properties)

        # Function to create relationships in Neo4j with label
        def create_relationship(tx, uid1, uid2, relationship_label):
            tx.run(
                f"""
                MATCH (a {{UID: $uid1}}), (b {{UID: $uid2}})
                MERGE (a)-[r:{relationship_label}]->(b)
                """,
                uid1=uid1, uid2=uid2
            )

        # Insert the graph into Neo4j
        with driver.session() as session:
            # Delete all existing nodes and relationships
            session.execute_write(delete_all)

            # Create nodes
            for node, data in btwinGraph.nodes(data=True):
                label = data.get("label", "DefaultLabel").replace(":", "_")
                uid = data["UID"]
                
                # Collect all properties from the btwinGraph
                properties = {'author':'AM'}
                btwinPsets=KnowledgeGraph.NodeLinkedPSets(graph=btwinGraph,nodeUID=uid)
                if len(btwinPsets)>0:
                    for btwinPset in btwinPsets:
                        for prop in btwinPset[1]['hasProperties']:
                            key,value=prop['name'],prop['nominalValue']['value']
                            properties[key]=value
                properties={key: properties[key] for key in sorted(properties)}

                # Create the node
                if label != "ifc_IfcPropertySet":
                    session.execute_write(create_node, label, uid, properties)

            # Create relationships with labels
            for edge in btwinGraph.edges(data=True):
                uid1 = btwinGraph.nodes[edge[0]]["UID"]
                uid2 = btwinGraph.nodes[edge[1]]["UID"]
                relationship_label = edge[2].get("label", "RELATED").replace(":", "_")
                if relationship_label != "ifc_HasPropertySet":
                    session.execute_write(create_relationship, uid1, uid2, relationship_label)

        print("Graph imported into Neo4j successfully!")

        # Close the connection
        driver.close()


    @staticmethod
    def NodeNumberByUID(graph=None, uid=None):
        """
        Returns the number of the node with the given unique identifier (UID).

        Parameters:
        - G: A NetworkX graph.
        - uid: The unique identifier of the node to find.

        Returns:
        - The node with the specified UID, or None if no such node exists.
        """
        for node, data in graph.nodes(data=True):
            if data.get('UID') == uid:
                return node
                break

    
    @staticmethod
    def NodeUID(node=None):
        """
        Extracts the unique identifier (UID) of a node from a node tuple.

        This static method attempts to retrieve the unique identifier of a node, which can be stored under different keys in the node's attribute dictionary. It first looks for the 'UID' key and, if not found, it tries to retrieve the value using the '@id' key.

        Parameters:
            node : tuple, optional
                A tuple representing a node, where the first element is the node's number or identifier and the second element is a dictionary containing the node's attributes.

        Returns:
            str: The unique identifier of the node, if available. If the node's attributes do not contain 'UID' or '@id' keys, `None` is returned.

        Raises:
            KeyError: If neither 'UID' nor '@id' are keys in the node's attribute dictionary.

        Examples:
            # Assuming a node tuple format like (node_number, {node_attributes})
            node_uid = NodeUID(node=(1, {'UID': '123-456'}))

        Notes:
            - The method is designed to handle cases where the unique identifier might be stored under different keys in the node's attribute dictionary.
            - An exception is raised if neither expected key ('UID' or '@id') is found, indicating the need for error handling by the caller.
        """
        try:
            return node[1]['UID']
        except:
            return node[1]['@id']

    
    
    
    
    @staticmethod
    def SubGraphByObjectTypes(graph=None,objectTypes=['bot:Space','bot:Storey']):
        """
        Creates a subgraph from the given graph, retaining only the nodes with labels found in `objectTypes`.

        Parameters:
        - graph (nx.Graph): The original graph from which the subgraph is to be created.
        - objectTypes (list or set): A collection of node labels to retain in the subgraph.

        Returns:
        - nx.Graph: A subgraph containing only the nodes whose labels are in `objectTypes`.
        """

        # Create a copy of the original graph to avoid modifying it
        subGraph = graph.copy()

        # Iterate over a static list of nodes to safely remove nodes during iteration
        for node, data in list(subGraph.nodes(data=True)):
            nodeLabel = data.get('label', '')  # Use a default empty string if the 'label' key is missing
            if nodeLabel not in objectTypes:
                subGraph.remove_node(node)
        #print(f'Subgraph for {objectTypes}',subGraph)
        return subGraph


    


    @staticmethod
    def NodeLinkedPSets(graph=None,nodeUID=None,node=None):
        
        # Get the node
        if node is None and nodeUID is not None:
            try:
                node = KnowledgeGraph.NodeByUID(graph=graph,uid=nodeUID)
            except:
                print('Error - Node not found in the graph')
                
        if nodeUID is None:
            nodeUID = KnowledgeGraph.NodeUID(graph,node)
            
        # Get the psets
        psets = KnowledgeGraph.NodeLinkedNodes(graph=graph,nodeObjectUID=nodeUID,
                                               linkedNodesType='ifc:IfcPropertySet',relationshipName='ifc:HasPropertySet')
        
        return psets


