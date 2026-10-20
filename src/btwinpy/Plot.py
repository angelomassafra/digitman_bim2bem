# Colors
class Color():

    
    
    
    
    
    @staticmethod
    def Sunsetdark():

        """Return a matplotlib colormap based on Plotly's 'Sunsetdark' color sequence."""

        # Dependencies
        from matplotlib.colors import LinearSegmentedColormap
        import plotly.express as px

        # Create the colormap
        sunsetdarkColors=[tuple(int(num) / 255 for num in color.strip("rgb()").split(",")) for color in px.colors.sequential.Sunsetdark]
        colormap=LinearSegmentedColormap.from_list("Sunsetdark", sunsetdarkColors
                                                   )
        return colormap

# Plots
class Plot():


    @staticmethod
    def KPICardByKPIValue(
        kpiName: str = None,
        kpiValue: float = None,
        kpiUnit: str = None,
        width: int = 200,
        height: int = 100,
        fontSize: int = 16,
        numberSize: int = 20,
        numberColor: str = 'black',
        icon: str = None,             # URL or local path
        icon_size: tuple = (40, 40),  # (px, px)
        icon_pad_y: float = 0.3       # fraction of the height reserved for the icon
    ):
        import plotly.graph_objects as go
        import base64, io
        from PIL import Image

        # --- Image source (URL or base64 data URI) ---
        src = None
        if icon:
            if icon.startswith("http"):
                src = icon
            else:
                img = Image.open(icon)
                buf = io.BytesIO()
                img.save(buf, format='PNG')
                b64 = base64.b64encode(buf.getvalue()).decode()
                src = "data:image/png;base64," + b64

        # --- Indicator in the lower part of the card ---
        fig = go.Figure(go.Indicator(
            mode="number",
            value=kpiValue,
            title={
                "text": kpiName,
                "font": {"size": fontSize, "family": "Raleway"}
            },
            number={
                "suffix": f" {kpiUnit}",
                "font": {"size": numberSize, "color": numberColor}
            },
            domain={
                "x": [0, 1],
                "y": [0, 1 - icon_pad_y]
            }
        ))

        # --- Icon in the upper part of the card ---
        if src:
            sizex = icon_size[0] / width
            sizey = icon_size[1] / height
            fig.update_layout(images=[{
                "source": src,
                "xref": "paper", "yref": "paper",
                "x": 0.5,                         # horizontal centre
                "y": 1 - icon_pad_y/2,           # middle of the upper padding
                "sizex": sizex,
                "sizey": sizey,
                "xanchor": "center",
                "yanchor": "middle",
                "layer": "above"
            }])

        # --- Margins and size ---
        fig.update_layout(
            width=width,
            height=height,
            margin={"l":0, "r":0, "t":0, "b":0}
        )

        return fig


    @staticmethod
    def KnowledgeGraphByMatplotlib(graph=None, showNodeLabels=True, showEdgeLabels=False, nodeColorMap='sunsetdark', nodeSize=50, nodeOpacity=1, edgeColorMap='turbo', edgeWidth=1, savePath=None, figsize=(10,10), showLegend=True):
        
            """
            Visualize a network graph using matplotlib and networkx.

            Parameters:
            - graph (networkx.Graph): The networkX graph to be visualized.
            - showNodeLabels (bool): Whether to display node labels.
            - showEdgeLabels (bool): Whether to display edge labels.
            - nodeColorMap (str): Colormap for node colors.
            - nodeSize (int): Size of nodes in the graph.
            - nodeOpacity (float): Opacity of nodes.
            - edgeColorMap (str): Colormap for edge color.
            - edgeWidth (float): Width of edges in the graph.
            - igsize (tuple): Size of the figure.
            - savePath (str): File path for saving the plot.
            - figsize (tuple): Size of the plot.
            """
    
            # Import libraries
            import matplotlib.pyplot as plt
            import networkx as nx
            import numpy as np

            # Create the figure
            plt.figure(figsize=figsize)
            
            # Node layout
            pos=nx.spring_layout(graph)  # draw the graph

            # Node labels and UIDs
            node_labels=nx.get_node_attributes(graph, 'label')  # label attribute for each node
            node_UIDs=nx.get_node_attributes(graph, 'UID')

            # Node colors
            unique_labels=sorted(set(node_labels.values())) 
            if nodeColorMap.upper()=='SUNSETDARK':
                node_colormap=Color.Sunsetdark()
                # Generate a range of values between 0 and 1 to map to the colormap
                color_range=np.linspace(0, 1, len(unique_labels))
                # Map each unique label to a color in the "Sunsetdark" colormap
                node_label_colors={label: node_colormap(color) for label, color in zip(unique_labels, color_range)}
                # Assign colors to nodes based on their labels
                node_colors=[node_label_colors[label] for label in node_labels.values()]
            else:
                node_colormap=plt.get_cmap(nodeColorMap).resampled(len(unique_labels))  # Colormap based on the number of unique labels
                node_label_colors={label: node_colormap(i) for i, label in enumerate(unique_labels)}  # Assign a color to each unique label
                node_colors=[node_label_colors[label] for label in node_labels.values()]  # Get the color for each node based on its label
            
            # Edge labels
            edge_labels=nx.get_edge_attributes(graph, 'label')
            
            #Edge colors
            unique_labels=set(edge_labels.values())  
            edge_colormap=plt.get_cmap(edgeColorMap).resampled(len(unique_labels))  # Colormap based on the number of unique labels
            edge_label_colors={label: edge_colormap(i) for i, label in enumerate(unique_labels)}  # Assign a color to each unique label
            edge_colors=[edge_label_colors[label] for label in edge_labels.values()]  # Get the color for each node based on its label

            # Draw the graph
            nx.draw(graph, pos,with_labels=False, node_color=node_colors, node_size=nodeSize, alpha=nodeOpacity,
                    edge_color=edge_colors, width=edgeWidth)
            if showNodeLabels:
                nx.draw_networkx_labels(graph, pos, labels=node_UIDs, font_size=10, font_color='black')  # Add node labels
            if showEdgeLabels:
                nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, font_size=8)

            # Create a legend
            if showLegend:
                handles=[]
                handles.append(plt.Line2D([], [], marker='', label='Node Legend', linestyle='None'))
                for label, color in node_label_colors.items():
                    handles.append(plt.Line2D([], [], marker='o', markersize=8, label=label, color=color, linestyle='None'))
                handles.append(plt.Line2D([], [], marker='', label='\nEdge Legend', linestyle='None'))
                for label, color in edge_label_colors.items():
                    handles.append(plt.Line2D([], [], marker='_', markersize=8, label=label, color=color, linestyle='None'))
                plt.legend(handles=handles)
            
            # Save the figure
            if savePath is not None:
                plt.savefig(savePath, format='png', dpi=300)
            
            # Display the graph in Jupyter (the figure is only saved when running as a script)
            import sys
            if 'ipykernel' in sys.modules:
                plt.show()
            else:
                plt.close()
