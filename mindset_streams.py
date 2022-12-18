import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from netgraph import Graph

def edge_valence(df):
    """Determine the valence of an edge for sentiment attached association data.

       Parameters
       ----------
       df : Pandas dataframe : contains sentiment attached assocation data

       Returns
       ----------
       df : Pandas dataframe : contains sentiment attached assocation data with the edge valence column
    """
    
    conditions = [
    (df['word 1 valence'] == 'neutral') & (df['word 2 valence'] == 'neutral'),
    (df['word 1 valence'] == 'neutral') & (df['word 2 valence'] == 'positive'),
    (df['word 1 valence'] == 'neutral') & (df['word 2 valence'] == 'negative'),
    (df['word 1 valence'] == 'positive') & (df['word 2 valence'] == 'neutral'),
    (df['word 1 valence'] == 'positive') & (df['word 2 valence'] == 'positive'),
    (df['word 1 valence'] == 'positive') & (df['word 2 valence'] == 'negative'),
    (df['word 1 valence'] == 'negative') & (df['word 2 valence'] == 'neutral'),
    (df['word 1 valence'] == 'negative') & (df['word 2 valence'] == 'positive'),
    (df['word 1 valence'] == 'negative') & (df['word 2 valence'] == 'negative')
    ]
    
    values = ['neutral', 'neutral', 'neutral',
          'neutral', 'positive', 'conflicting',
          'neutral', 'conflicting', 'negative']
    df['edge valence'] = np.select(conditions, values)
    return df

def create_base_graph(df):
    """Create a NetworkX graph from a Pandas dataframe and assign valence attribute.

       Parameters
       ----------
       dataframe : Pandas dataframe : contains word assocation data

       Returns
       ----------
       G : NetworkX graph : base graph
    """
    G = nx.from_pandas_edgelist(df, 'word 1', 'word 2', edge_attr = 'edge valence')
    
    for index, row in df.iterrows():
        G.nodes[row['word 1']]['valence'] = row['word 1 valence']
        G.nodes[row['word 2']]['valence'] = row['word 2 valence']

    return G

def shortest_paths(G, source, target):
    """Find the shortest paths between source and target nodes in a given NetworkX graph.

       Parameters
       ----------
       graph : NetworkX graph : shortest paths source
       source : string : name of source node
       target : string : name of target node

       Returns
       ----------
       paths : list : shortest paths from source to target
    """
    paths = [p for p in nx.all_shortest_paths(G, source, target)]
    return paths

def bridge_graph(graph, paths):
    """Create a NetworkX subgraph using path list.

       Parameters
       ----------
       graph : NetworkX graph : base graph which the subgraph is generated from
       paths : list : shortest paths

       Returns
       ----------
       subgraph : NetworkX graph: subgraph composed of shortest paths
    """
    subgraph = graph.subgraph(paths[0])
    for path in paths[1:]:
        new_subgraph = graph.subgraph(path)
        subgraph = nx.compose(subgraph, new_subgraph)
    return subgraph

def node_positions(paths):
    """Calculate the positions of nodes in the stream network. The position of nodes is dependent on the topology of the stream
       network and is not the same for every network.

       Parameters
       ----------
       paths : list : shortest paths

       Returns
       ----------
       node_positions_dict : dictionary : {key = node, value = coordinate}
    """
    
    source_nodes = []
    target_nodes = []
    layer_nodes = []
    
    #prepare empty lists for each network layer.
    num_layers = len(paths[0]) - 2
    for i in range(num_layers):
            layer_nodes.append([])
    
    #append nodes based on their position in the network.
    for path in paths:
        counter = 0
        for node in path:
            if counter == 0:
                source_nodes.append(node)
                counter += 1
            elif 0 < counter < num_layers + 1:
                layer_nodes[counter-1].append(node)
                counter += 1
            else:
                target_nodes.append(node)
                break
    
    #remove duplicate nodes from each layer.
    dup_free = []
    for l in layer_nodes:
        l = list(set(l))
        dup_free.append(l)

    layer_nodes = dup_free

    source_node = list(set(source_nodes))[0]

    target_node = list(set(target_nodes))[0]
    
    
    node_positions_dict = {}
    node_positions_dict[source_node] = (0.1, 0.5) #source node positioned on the far left.
    node_positions_dict[target_node] = (0.9, 0.5) #target node positioned on the far right.
    
    layer_number = 0
    layer_y_positions = []
    layer_x_positions = []
    
    #Assign each node a numerical position based on its layer.
    for i in range(num_layers):
        x_position = (1/(num_layers + 1)) * (i + 1)
        layer_x_positions.append(x_position)
    
    for layer in layer_nodes:
        layer_x_position = layer_x_positions[layer_number]
        node_number = 0
        
        for node in layer:
            y_position = 1 - ((1/(len(layer) + 1)) * (node_number + 1))
            node_positions_dict[node] = (layer_x_position, y_position)
            
            node_number += 1
        
        layer_number += 1

    return node_positions_dict

def node_colours(graph):
    """Assign graph nodes a colour based on their valence.

       Parameters
       ----------
       graph : NetworkX graph : graph for node modification

       Returns
       ----------
       node_colour_dict : dictionary : {key = node, value = colour}
    """
    valence_dict = dict(graph.nodes(data=True))
    node_colour_dict = {}

    for node, valence in valence_dict.items():
        if valence == {'valence': 'positive'}:
            node_colour_dict[node] = 'tab:blue'
        elif valence == {'valence': 'neutral'}:
            node_colour_dict[node] = 'tab:grey'
        elif valence == {'valence': 'negative'}:
            node_colour_dict[node] = 'tab:red'

    return node_colour_dict

def edge_colours(graph):
    """Assign graph edges a colour based on their valence.

       Parameters
       ----------
       graph : NetworkX graph : graph for edge modification

       Returns
       ----------
       edge_colour_dict : dictionary : {key = edge, value = colour}
    """
    
    edge_colour_dict = {}
    for source, target, attribute in graph.edges(data=True):
        valence = attribute.get('edge valence')
        if valence == 'positive':
            colour = 'tab:blue'
        elif valence == 'neutral':
            colour = 'tab:grey'
        elif valence == 'negative':
            colour = 'tab:red'
        edge_colour_dict[(source, target)] = colour

    return edge_colour_dict

def node_sizes(node_closeness):
    """Assign graph nodes a size based on their closeness centrality calculated from its base graph.

       Parameters
       ----------
       node_closeness : dictionary : {key = node, value = closeness centrailty}

       Returns
       ----------
       node_sizes_dict : dictionary : {key = node, value = node size}
    """
    
    node_sizes_dict = node_closeness.copy()
    
    for i, v in node_sizes_dict.items():
        node_sizes_dict[i] = v * 8
    
    return node_sizes_dict

def path_betweenness(path, base_graph):
    """Calculate the betweenness centrality of all edges in a given path.

       Parameters
       ----------
       path : list : contains a network path
       base_graph : NetworkX Graph : networkX base graph

       Returns
       ----------
       sum(betweenness_list) : int : the sum of all calculated edge betweennesses in the path
    """
    
    betweenness_dict = nx.edge_betweenness_centrality(base_graph)
    
    tuple_pairs = list(zip(path, path[1:] + path[:1]))[:-1] #list of all node pairs
    betweenness_list = []
    
    #append the betweenness value for each node pair checking both orders.
    for edge in tuple_pairs:
        word_1 = list(edge)[0]
        word_2 = list(edge)[1]
        if ((word_1, word_2) in betweenness_dict):
            betweenness = betweenness_dict[(word_1, word_2)]
            betweenness_list.append(betweenness)
            continue
        elif ((word_2, word_1) in betweenness_dict):
            betweenness = betweenness_dict[(word_2, word_1)]
            betweenness_list.append(betweenness)
            continue
            
    return sum(betweenness_list)

def path_type(path, subgraph):
    """Returns the path type for a given path.

       Parameters
       ----------
       path : list : contains a network path
       subgraph : NetworkX Graph : networkX subgraph

       Returns
       ----------
       path_type : String : the type of the provided path
    """
    
    path_valences = []
    
    for node in path:
        valence = dict(subgraph.nodes(data=True)).get(node).get('valence')
        path_valences.append(valence)
    
    #if all nodes in path are Positive path type is 'Purely Positive Path'
    if all(v == 'positive' for v in path_valences) == True:
        path_type = 'purely positive path'
        return path_type
    #if all nodes in path are Neutral path type is 'Purely Neutral Path'
    elif all(v == 'neutral' for v in path_valences) == True:
        path_type = 'purely neutral path'
        return path_type
    #if all nodes in path are Negative path type is 'Purely Negative Path'
    elif all(v == 'negative' for v in path_valences) == True:
        path_type = 'purely negative path'
        return path_type 
    #if all nodes in path are Positive and Negative path type is 'Conflicting Path'
    elif any(v == 'negative' for v in path_valences) & any(v == 'positive' for v in path) == True:
        path_type = 'conflicting path'
        return path_type
    #any other path type is 'Mixed Path'
    else:
        path_type = 'mixed path'
        return path_type

def stream_graph(df, source_node, target_node):
    """Create a mindset stream network using the provided source and target node and generate the network statistics
       (path frequencies and betweennesses).

       Parameters
       ----------
       base_graph : NetworkX Graph : network graph representing association data
       source_node : string : name of the source node
       target_node : string : name of the target node

       Returns
       ----------
       graph : netgraph graph : mindset stream network

    """
    
    #create base graph
    base_graph = create_base_graph(df)
    
    #generate shortest paths and create a subgraph using paths
    base_paths = shortest_paths(base_graph, source_node, target_node)
    subgraph = nx.Graph(bridge_graph(base_graph, base_paths))
    subgraph.remove_edges_from(nx.selfloop_edges(subgraph))
    
    #create dictionary containing all node closeness centrality values in subgraph
    closeness_dict = nx.closeness_centrality(base_graph)
    node_closeness = {k:closeness_dict[k] for k in tuple(list(subgraph.nodes)) if k in closeness_dict}
    
    #generate graph sub paths
    sub_paths = shortest_paths(subgraph, source_node, target_node)
    
    #generate node positions
    node_dict = node_positions(sub_paths) 
    
    #generate node colours
    node_colour_dict = node_colours(subgraph) 
    
    #generate edge colours
    edge_colour_dict = edge_colours(subgraph) 
    
    #generate node sizes
    node_size_dict = node_sizes(node_closeness) 
    
    fig, ax = plt.subplots(figsize=(30, 30))

    graph = Graph(subgraph, node_layout = node_dict, node_labels=True, 
                    node_color = node_colour_dict, edge_color= edge_colour_dict,
                    node_size=node_size_dict, node_edge_width = 0)
    
    #source and target node labels in italics
    graph.node_label_artists[source_node].set_style('italic')
    graph.node_label_artists[target_node].set_style('italic')
    
    #set node label font size proportional to its closeness
    for node in graph.nodes:
        graph.node_label_artists[node].set_fontsize(node_closeness[node] * 120)
    
    stats_list = []
    
    #create list of node valences for each path in paths list
    for path in sub_paths:
        type_ = path_type(path, subgraph)
        betweenness = round(path_betweenness(path, base_graph), 4)
        stats_list.append([path, type_, betweenness])
  
    #convert path_types list to Pandas dataframe
    path_stats = pd.DataFrame(stats_list, columns=['Path Structure', 'Path Type', 'Sum of Edge Betweenness Centralities'])
    
    return graph, path_stats

