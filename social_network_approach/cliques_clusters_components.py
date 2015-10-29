from social_util import trim_degrees, get_graph
from matplotlib import pyplot as plt
import numpy as np
import networkx as net

def get_component_subgraphs(g, plot=False):
    """
    counts number of subgraphs within a graph and sizes of those subgraphs.

    This is actually really interesting, especially for the smaller components,
    because those seem to represent 'outlier' musicians who are coming from a 
    genre that you don't normally listen to.

    returns subgraphs and sizes
    """
    thelist = list(net.connected_component_subgraphs(net.Graph(g)))
    thesizes = [len(c) for c in thelist]
    if plot:
        plt.hist(thesizes)
    print 'number of component subgraphs:', len(thelist)
    print 'sizes of subgraphs', thesizes
    return thelist, thesizes

def trim_edges(g, weight=1):
    """trim nodes having weight less than weight.  returns a copy of g"""
    g2=net.Graph()
    for f, to, edata in g.edges(data=True):
        if edata['weight'] > weight:
            g2.add_edge(f, to, edata)
    return g2

def trim_nodes(g, min_degree=1):
    """returns a copy of g nodes trimmed if they have degree equal to or less than `min_degree`"""
    g2=g.copy()
    for name, degree in net.degree(g).iteritems():
        if degree <= min_degree:
            g2.remove_node(name)
    return g2

def node_island_method(g, iterations=5):
    """imagine an island where the height of every point is determined by
    the degree of a node in g.  Now raise the water level and see how many 
    islands (ie component subgraphs) our original island has broken into

    zeros into cores of most activity
    """
    degrees = [degree for name, degree in net.degree(g).iteritems()]
    minimum = min(degrees)
    maximum = max(degrees)
    step = int((maximum-minimum)/float(iterations))

    result = [(threshold, trim_nodes(g, threshold)) 
            for threshold in range(minimum, maximum, step)]
    return result

def print_island_info(islands):
    """
    prints info about islands.
    """
    print 'theshold level | size of graph | number of component subgraphs'
    for i in islands:
        print i[0], len(i[1]), len(list(net.connected_component_subgraphs(net.Graph(i[1]))))

def get_ego_graph(g, name, radius=2):
    """
    retuns ego graph to given radius for given node
    
    this is useful for getting similar artists to a given artist that someboy
    really likes
    """
    return net.ego_graph(g, name, radius)

def get_average_clustering_around_ego(g, name, radius=2):
    """
    returns average clustering around an ego.  Not particularly interesting,
    as most graphs are going to have a simlilar amount of clustering due to the 
    fact that the "similar artists" functionality of echo nest probably returns
    the same amount of similar artists for any given artist.
    """
    ego_net = net.Graph(get_ego_graph(g, name, radius))
    print 'size of ego_network:', len(ego_net)
    return net.average_clustering(ego_net)

def get_triadic_census(g):
    """carries out triadic census.  Returns census for graph as a whole and for
    each node."""
    import triadic
    return triadic.triadic_census(g)

def get_cliques(g, min_length=3):
    """returns maximal complete subgraphs greater than given length"""
    return [clique for clique in net.find_cliques(net.Graph(g)) if len(clique) >= min_length]

def get_sorted_cliques(g):
    """returns list of cliques sorted by size"""
    return sorted(list(net.find_cliques(net.Graph(g))), key=len, reverse=True)

def get_shortest_path_distance_matrix(g):
    """computes all pairs shortest paths from graph
    and returns as a numpy array"""
    labels=g.nodes()    
    path_length=net.all_pairs_shortest_path_length(g)
    distances=np.zeros((len(g),len(g))) 
    i=0   
    for u,p in path_length.items():
        j=0
        for v,d in p.items():
            distances[i][j]=d
            distances[j][i]=d
            if i==j: distances[i][j]=0
            j+=1
        i+=1
    return distances

def hierarchical_clustering(g, n_clusters=3):
    """performs hierarchical_clustering to specified number fo clusters"""
    from sklearn.cluster import AgglomerativeClustering
    
    distances = get_shortest_path_distance_matrix(g)
    ac = AgglomerativeClustering(n_clusters, linkage='average')
    labels = ac.fit_predict(distances)
    
    clusters = defaultdict(list)
    for node, label in zip(g.nodes(), labels):
        clusters[label].append(node)
    return clusters

def perform_silhouette_analysis(g, range_n_clusters, plot=True):
    """perfoms silhouette analysis to determine best number of
    clusters for hierarchical clustering"""
    from graph_silhouette_analysis import silhouette_analysis
    g = list(net.connected_component_subgraphs(net.Graph(g)))[0]
    distances = get_shortest_path_distance_matrix(g)
    silhouette_analysis(distances, range_n_clusters, plot=plot)
    plt.show()

def draw_block_model(g):
    """draws block model"""
    import blockmodel
    blockmodel.blockmodel(net.Graph(g))

if '__main__' in __name__:
    g = get_graph('music_network.net', 'artist_id_map.p')
    perform_silhouette_analysis(g, range_n_clusters=range(2,102,5))
