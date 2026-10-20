class Annotations():

    @staticmethod
    def TBIM_CellAnnotations(tpBuilding=None,propNames=[],markerColor='black',markerSize=5):

        # Dependencies
        from topologicpy.CellComplex import CellComplex
        from topologicpy.Dictionary import Dictionary
        from topologicpy.Topology import Topology
        from topologicpy.Vertex import Vertex
        import plotly.graph_objects as go

        # Data for the 3D scatter plot
        x_data,y_data,z_data = [],[],[]

        # Text for each vertex
        custom_hover_text,text = [],[]

        # Data
        for tpCell in CellComplex.Cells(tpBuilding):

            tpCentroid=Topology.CenterOfMass(tpCell)
            x=Vertex.X(tpCentroid)
            y=Vertex.Y(tpCentroid)
            z=Vertex.Z(tpCentroid)

            d=Topology.Dictionary(tpCell)
            cellUID=Dictionary.ValueAtKey(d,'UID')
            
            hovertext=f'Cell: {cellUID}'
            for propName in propNames:
                propValue=str(Dictionary.ValueAtKey(d,propName))
                hovertext+=f'<br>{propName}: {propValue}'

            x_data.append(x)
            y_data.append(y)
            z_data.append(z)

            custom_hover_text.append(hovertext)
            text.append(cellUID)

        plotlyData=[go.Scatter3d(
            x=x_data,
            y=y_data,
            z=z_data,
            mode='markers+text',
            text=text,  # Displayed text at each vertex
            textposition='top center',
            marker=dict(size=markerSize,color=markerColor),
            hoverinfo='text',  # Only display custom hover text
            hovertext=custom_hover_text,  # Custom hover text
            hovertemplate='%{hovertext}<extra></extra>'  # Format hover information
        )]

        return plotlyData


class Show():

    @staticmethod
    def TBIM_EnergyZones(tpBuilding=None,colorScale='turbo',showAnnotations=True):

        # Dependencies
        from topologicpy.Cell import Cell
        from topologicpy.CellComplex import CellComplex
        from topologicpy.Color import Color
        from topologicpy.Dictionary import Dictionary
        from topologicpy.Plotly import Plotly
        from topologicpy.Topology import Topology

        # Get all the zone UIDs
        zoneUIDs=[]
        for tpCell in CellComplex.Cells(tpBuilding):
            rl_HasLocation_tpZN=Dictionary.ValueAtKey(Topology.Dictionary(tpCell),'rl_HasLocation_tpZN')
            if rl_HasLocation_tpZN is not None:
                zoneUIDs.append(rl_HasLocation_tpZN)
        zoneUIDs=sorted(list(set(zoneUIDs)))

        # Plotly data
        plotlyData=[]
        for tpCell in CellComplex.Cells(tpBuilding):

            d=Topology.Dictionary(tpCell)
            zoneUID=Dictionary.ValueAtKey(d,'rl_HasLocation_tpZN')

            cellBottomFace=Cell.Decompose(Topology.RemoveCoplanarFaces(tpCell))['bottomHorizontalFaces'][0]
            if zoneUID is not None:
                zoneNumber=zoneUIDs.index(zoneUID)
                color=Color.ByValueInRange(minValue=0,maxValue=len(zoneUIDs),value=zoneNumber,colorScale=colorScale)
                color=Color.PlotlyColor(color)
                plotlyData+=Plotly.DataByTopology(cellBottomFace,faceColor=color,faceOpacity=1,showVertices=False)
            else:
                plotlyData+=Plotly.DataByTopology(cellBottomFace,showFaces=False,showVertices=False)
                

            plotlyData+=Plotly.DataByTopology(tpCell,showFaces=False,showVertices=False,edgeColor='gray')

            # Annotations
            if showAnnotations:
                plotlyData+=Annotations.TBIM_CellAnnotations(tpBuilding=tpBuilding,propNames=['rl_HasLocation_tpZN','pr_OccupancyType'])
                
        # Plotly fig
        fig=Plotly.FigureByData(plotlyData)
        fig.update_layout(title="TBIM: Spaces colored by Energy Zone",showlegend=False)
        return fig


    @staticmethod
    def TBIM_ByEnergyPlusCSV(
        tpBuilding=None,
        epCSVPath=None,
        outputVariable='Zone Ideal Loads Zone Total Heating Energy',
        energyUnit='kWh',
        colorScale='haline',
        buildingStoreyUIDs=[],
        normalizeArea=True,
        width=800,height=600,
        columnTotals=None,
        subTitle=None,
        geometryCache=None
    ):
        
        """
        Floor plans of the thermal zones coloured by the annual total of an EnergyPlus output
        variable. The totals are computed from the hourly CSV at epCSVPath or, alternatively,
        passed as columnTotals ({EnergyPlus CSV column name: annual total in energyUnit}).
        geometryCache: optional dictionary where the zone floor plans and the cell edges of the
        building are stored on the first call and reused afterwards (e.g. in the dashboard).
        """
        
        import pandas as pd
        from topologicpy.Plotly import Plotly
        from topologicpy.Color import Color
        from topologicpy.CellComplex import CellComplex
        from topologicpy.Dictionary import Dictionary
        from topologicpy.Topology import Topology
        from topologicpy.Cell import Cell
        from topologicpy.Face import Face
        
        # Annual totals of each CSV column
        if columnTotals is None:
            df = pd.read_csv(epCSVPath)
            # Convert Joule in kWh
            if energyUnit=='kWh':
                for col in df.columns:
                    if '[J]' in col:
                        df[col] = df[col]/3.6e6
            columnTotals = {col: df[col].sum() for col in df.columns if col != 'Date/Time'}
            if subTitle is None:
                subTitle = f"From: {df['Date/Time'].iloc[0]}  -  To: {df['Date/Time'].iloc[-1]}"
                    
        # Zone floor plans and cell edges (geometry only, independent of the output variable)
        if geometryCache is not None and 'zones' in geometryCache:
            zoneGeometry, cellPlotlyData = geometryCache['zones'], geometryCache['cellPlotlyData']
        else:
            # Group the cells
            groupedCells={}
            for tpCell in CellComplex.Cells(tpBuilding):
                rl_HasLocation_tpZN=Dictionary.ValueAtKey(Topology.Dictionary(tpCell),'rl_HasLocation_tpZN')
                if rl_HasLocation_tpZN is not None:
                    groupedCells.setdefault(rl_HasLocation_tpZN,[]).append(tpCell)
            # Zone floor plans
            zoneGeometry={}
            for rl_HasLocation_tpZN,tpZoneCells in groupedCells.items():
                tpZoneBottomFaces=[]
                pr_ZoneGrossArea=0
                for tpZoneCell in tpZoneCells:
                    rl_HasLocation_tpBS=Dictionary.ValueAtKey(Topology.Dictionary(tpZoneCell),'rl_HasLocation_tpBS')
                    if len(buildingStoreyUIDs)==0 or rl_HasLocation_tpBS in buildingStoreyUIDs:
                        for tpFace in Cell.Decompose(tpZoneCell)['bottomHorizontalFaces']:
                            tpZoneBottomFaces.append(tpFace)
                            pr_ZoneGrossArea+=Face.Area(tpFace)
                if tpZoneBottomFaces:
                    tpZoneBottomFace=Topology.RemoveCollinearEdges(Topology.MergeAll(tpZoneBottomFaces))
                    zoneGeometry[rl_HasLocation_tpZN]=(tpZoneBottomFace,pr_ZoneGrossArea)
            # Cell edges
            cellPlotlyData=[]
            for tpCell in CellComplex.Cells(tpBuilding):
                rl_HasLocation_tpBS=Dictionary.ValueAtKey(Topology.Dictionary(tpCell),'rl_HasLocation_tpBS')
                if len(buildingStoreyUIDs)==0 or rl_HasLocation_tpBS in buildingStoreyUIDs:
                    cellPlotlyData+=Plotly.DataByTopology(Topology.RemoveCoplanarFaces(tpCell),showFaces=False,showVertices=False,edgeColor='gray')
            if geometryCache is not None:
                geometryCache.update(zones=zoneGeometry,cellPlotlyData=cellPlotlyData)

        # Zone values
        plotDicts=[]
        for rl_HasLocation_tpZN,(tpZoneBottomFace,pr_ZoneGrossArea) in zoneGeometry.items():
            for col, value in columnTotals.items():
                if rl_HasLocation_tpZN.upper() in col and outputVariable in col:
                    if normalizeArea:
                        value=value/pr_ZoneGrossArea
                    plotDicts.append({'tpZoneBottomFace':tpZoneBottomFace,outputVariable:value})
        values=[d[outputVariable] for d in plotDicts]
        maxValue,minValue=(max(values),min(values)) if values else (0,0)

        # Zone Plotly data
        plotlyData=[]
        for d in plotDicts:
            color=Color.ByValueInRange(d[outputVariable],minValue,maxValue,colorScale=colorScale)
            plotlyData+=Plotly.DataByTopology(d['tpZoneBottomFace'],showVertices=False,faceColor=color,faceOpacity=1)
        plotlyData+=cellPlotlyData

        # Figure       
        fig=Plotly.FigureByData(plotlyData,width=width,height=height)

        # Color bar
        maxValue,minValue=round(maxValue,3),round(minValue,3)
        fig=Plotly.AddColorBar(figure=fig,values=[minValue,maxValue],
                            title=outputVariable,
                            subTitle=subTitle or '',
                            units=energyUnit,colorScale=colorScale,
                            mantissa=2)
        return fig


class Color():

    @staticmethod
    def Blue():
        return 'rgb(40,35,160)'
    
    @staticmethod
    def Green():
        return 'rgb(65,160,130)'
    
    @staticmethod
    def Yellow():
        return 'rgb(215,225,115)'
    
    
