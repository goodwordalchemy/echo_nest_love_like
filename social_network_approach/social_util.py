import csv
import networkx as net
import pickle

def make_id_map(map_file):
    """id map is saved as a list of dicts.  This file converts that list
    into a single dict with 'id' as key and 'name' as value"""
    list_of_dicts = pickle.load(open(map_file,'rb'))
    the_dict = {}
    for dict_item in list_of_dicts:
        the_dict[dict_item['id']] = dict_item['name']
    return the_dict

def trim_degrees(graph, degree=1):
    """trims nodes having degree less than the parameter"""
    d = net.degree(graph)
    for n in graph.nodes():
        if d[n] <= degree: graph.remove_node(n)
    return graph

def get_graph(graph_file, map_file, trim=False):
    """
    graph_file --> is the file to convert to a networkx graph
    trim --> either takes an integer or 'False'.  If integer, returned graph
        will call return graph with nodes having degree greater than integer
    """
    the_graph = net.DiGraph(net.read_pajek(graph_file))
    id_map = make_id_map(map_file)
    net.relabel_nodes(the_graph, id_map, copy=False)
    if trim:
        the_graph = trim_degrees(the_graph, degree=trim)
    return the_graph


if '__main__' in __name__:
    pass