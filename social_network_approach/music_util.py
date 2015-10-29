import requests
import json
import spotipy
import time

USERNAME = 'dbgoldberg01'

def read_keys(thefile='keys.json'):
    """
    returns a dictionary of access keys from "thefile"
    """
    global keys 
    with open(thefile) as keys_file:
        keys = json.load(keys_file)
        keys_file.close()
        return keys

keys = read_keys()

class SpotifyAPIException(Exception):
    pass

class EchoNestAPIException(Exception):
    pass

def login_with_token(username=USERNAME):
    """gets access token from spotify, logs in, and retuns spotify session"""
    import spotipy.util
    scope = 'user-library-read playlist-read-private user-read-private'
    token = spotipy.util.prompt_for_user_token(
        'dbgoldberg01', scope,
        client_id=keys['CLIENT_ID'],
        client_secret=keys['CLIENT_SECRET'],
        redirect_uri='http://localhost:8888/callback')
    if token:
        global sp
        sp = spotipy.Spotify(auth=token)
        return sp
    else:
        raise SpotifyAPIException("Can't get token")

def get_session_user_id(session):
    """returns spotify id of current user"""
    return session.current_user()['id']

def get_en_artist_data(artist_uri):
    """takes spotify artist uri and finds echo nest artist data"""
    base_url = 'http://developer.echonest.com/api/v4/artist/profile?'
    suffix = \
        'api_key='+ keys['EN_API_KEY']+'&'\
        'id='+artist_uri+'&'+\
        'bucket=genre'+'&'+\
        'bucket=biographies'+'&'+\
        'bucket=discovery'+'&'+\
        'bucket=familiarity'+'&'+\
        'bucket=hotttnesss'+'&'+\
        'bucket=reviews'
    r = requests.get(base_url+suffix)
    return json.loads(r.content)['response']

def get_similar_artists(artist_uri):
    """
    takes spotify artist_uri and retuns a list of similar artists as a 
    list of dicts with id and name fields
    """
    base_url = 'http://developer.echonest.com/api/v4/artist/similar?'
    suffix = \
        'api_key='+ keys['EN_API_KEY']+'&'\
        'id='+artist_uri
    r = requests.get(base_url + suffix)
    
    if int(r.headers['x-ratelimit-remaining']) < 3: 
        print 'approaching ratelimit.  remaining: %d'%int(r.headers['x-ratelimit-remaining'])
        time.sleep(30)
    try:
        return json.loads(r.content)['response']['artists']
    except KeyError:
        raise EchoNestAPIException(json.dumps(json.loads(r.content),indent=4))

def pprint_json(json_dict):
    print json.dumps(json_dict, indent=4)

def get_en_track_data(track_uri):
    """takes spotify track uri and returns a echo nest track data"""
    base_url = 'http://developer.echonest.com/api/v4/track/profile?'
    suffix = \
        'api_key='+ keys['EN_API_KEY']+'&'\
        'id='+track_uri+'&'+\
        'bucket=audio_summary'
    r = requests.get(base_url+suffix)
    return json.loads(r.content)['response']

def get_playlist_tracks(user_id, name):
    """
    name refers to playlist name
    """
    #gets playlist id:
    pls = sp.user_playlists(user_id)
    res = [p for p in pls['items']
                 if p['name']==name]
    playlist_id = res[0]['id']

    #gets tracks
    ps = sp.user_playlist_tracks(
        user_id, playlist_id=playlist_id)
    return ps['items']

if '__main__' in __name__:
    pass