import networkx as net
import matplotlib.pyplot as plt
import pandas as pd
from social_util import get_graph
from collections import defaultdict
        
def sorted_map(map_dict):
    """returns a sorted list of dictionary items sorted by the value"""
    return sorted(map_dict.iteritems(), key=lambda x: x[1], reverse=True)

def find_celebrities(g):
    """returns sorted map of nodes with highest degree centrality"""
    d = net.degree(g)
    return sorted_map(d)

def find_gossipmongers(g):
    """
    returns sorted map of nodes with highest degree of 
    closeness centrality.  Closeness centrality is calculated by 
    determining the reciprocal normalized average distance between 
    a given node and every other node in the graph.

    each returned value in map gets number between 0 and 1 supposed
    indicate the closeness between that node and the rest of the graph--
    1 being greater closeness centrality.

    """
    c = net.closeness_centrality(g)
    return sorted_map(c)

def find_bottlenecks_and_bridges(g):
    """
    returns map of nodes sorted by betweenness centrality, which is
    calculated by looking at the shortest path between every node in
    network and seeing how many times any given node appears in those
    sorted paths.  Results are then normalized against the amount of 
    edges in the graph (I think).
    """
    b =  net.betweenness_centrality(g)
    return sorted_map(b)

def find_gray_cardinals(g):
    """
    returns eigenvector closeness, which is a measure of knowing people
    who know people.  Calculated by recursively weighting each link by 
    recursively weighted degree of the node on the other end.
    """
    e = net.eigenvector_centrality(g)
    return sorted_map(e)  

metrics = {
        'degree': net.degree,
        'closeness': net.closeness_centrality,
        'betweenness': net.betweenness_centrality,
        'pagerank': net.pagerank
}

def find_elite(g, metrics=metrics):
    """
    returns dataframe with metrics listed above.  limit_num parameter 
    limits the number of artists in the dataframe by only using the top `limit_num`
    results from each metric.
    """
    results = defaultdict(list)
    metric_index = []
    for metric, func in metrics.iteritems():
        print "carrying out %s"%metric
        metric_index.append(metric)
        for name, value in func(g).iteritems():
            results[name].append(value)
    
    return pd.DataFrame(results, index=metric_index).T

def print_results_sorted_by_metric(df, metrics_dict=metrics, limit_num=-1):
    """
    prints top limit_num results from find_elite sorted by 
    metric name in metric dict
    """
    for m in metrics.keys():
        print m
        print df.sort(m, ascending=False)[:limit_num]


if '__main__' in __name__:
    g = get_graph('music_network.net', 'artist_id_map.p')
    elite_df = find_elite(g)
    print_results_sorted_by_metric(elite_df)

