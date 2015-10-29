from music_util import *
import networkx as net
import matplotlib.pyplot as plt
import pickle

def get_playlist_artists(playlist_name):
    """
    Downloads list of tracks from spotify playlist with name above.  See Utils
    file to change username and access.  Implemented as a generator yeilding 
    artist_id, artist_name pair tuple
    """
    sp = login_with_token()
    tracks = get_playlist_tracks(get_session_user_id(sp), playlist_name)
    for i in xrange(len(tracks)):
        try:
            artist_name = tracks[i]['track']['artists'][0]['name']
            artist_id = 'spotify:artist:' + tracks[i]['track']['artists'][0]['id']
            yield (artist_id, artist_name)
        except TypeError:
            print 'artist %s has no id'
            pass
        

def artist_search(g, artist_id, id_map):
    """
    wraps get_get_similar_artists function for use in snowball_sampling.
    Specifically:
        * adds links to graph g.
        * maps ids to artist names
    """
    similar_artists = get_similar_artists(artist_id)
    for similar in similar_artists:
        g.add_edge(artist_id, similar['id'])
        id_map.append(similar)


def snowball_sampling(g, func, center, id_map=[], max_depth=1, current_depth=0, taboo_list=[]):
    """
    gets ego network for "center" by recursively calling func to "max_depth".  id_map is an optional 
    parameter to be used in func.
    """
    print(center, current_depth, max_depth, len(taboo_list))
    if current_depth==max_depth:
        # if we have reached the depth limit of the search, return
        print('out of depth')
        return taboo_list
    if center in taboo_list:
        # We've been here before
        return taboo_list
    else:
        taboo_list.append(center)
    func(g, center, id_map=id_map)
    for node in g.neighbors(center):
        # note: each new version of taboo_list gets passed into the next call
        taboo_list = snowball_sampling(g, func, node, current_depth=current_depth+1,
                                    max_depth=max_depth, 
                                    taboo_list = taboo_list, 
                                    id_map=id_map)
    return taboo_list


def write_list_to_csv(filename, thelist):
    """writes list to csv"""
    with open(filename, 'wb') as my_file:
        wr = csv.writer(my_file)
        wr.writerow(thelist)


def main(max_depth = 2, graphfile='music_network.net', id_mapfile='artist_id_map.p'):
    g = net.Graph()
    id_map = []
    for artist_id, artist_name in get_playlist_artists('science'):
        id_map.append({'id': artist_id, 'name':artist_name})
        snowball_sampling(g, artist_search, artist_id, id_map=id_map, max_depth=max_depth)
    net.write_pajek(g, graphfile)
    pickle.dump(id_map, open(id_mapfile,'wb')) 
    
if '__main__' in __name__:
    main()

