import requests
import json
import spotipy
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
import time

USERNAME = 'dbgoldberg01'

def play_track_by_uri(uri):
    from IPython.core.display import HTML
    return HTML('<iframe src="https://embed.spotify.com/?uri=' + uri + '" width="300" height="80" frameborder="0" allowtransparency="true"></iframe>')

def read_keys():
	global keys	
	with open('keys.json') as keys_file:
	    keys = json.load(keys_file)
	    keys_file.close()
	    return keys

keys = read_keys()

class SpotifyAPIException(Exception):
	pass

class EchoNestAPIException(Exception):
	pass

def login_with_token(username=USERNAME):
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

def get_user_id(session):
	return session.current_user()['id']

def get_playlist_tracks(user_id, name):
	"""
	name refers to playlist name
	"""
	pls = sp.user_playlists(user_id)
	res = [p for p in pls['items']
                 if p['name']==name]
	playlist_id = res[0]['id']
	ps = sp.user_playlist_tracks(
	    user_id, playlist_id=playlist_id)
	return ps['items']

def make_df_from_track_list(track_list):
	tracks_data = [ \
	 (track['track']['name'], 
	  track['track']['id'],
	  track['track']['uri'],
	  track['track']['popularity'],
	  track['added_at'],
	  track['track']['album']['name'],
	  track['track']['album']['id'],
	  track['track']['album']['uri'],
	  track['track']['artists'][0]['name'],
	  track['track']['artists'][0]['id'],
	  track['track']['artists'][0]['uri'],
     ) for track in track_list]
	tracks_df = pd.DataFrame(tracks_data, columns=[\
	  'track_name',
  	  'track_id',
  	  'track_uri',
  	  'track_popularity',
  	  'added_at',
  	  'album_name',
  	  'album_id',
	  'album_uri',
	  'artist_name',
	  'artist_id',
	  'artist_uri'])
	return tracks_df

def get_en_artist_data(artist_uri):
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

def get_data_from_artist_uri(artist_uri):
	"""
	this method uses the method above to get data and 
	return a cleaned tuple with it.
	"""
	artist = get_en_artist_data(artist_uri).get('artist')
	artist_data =  (\
      [g['name'] for g in artist['genres']], 
      artist['familiarity'],
      artist['hotttnesss'],
      artist['discovery'],
      [bio['text'] for bio in artist['biographies']],
      [review['summary'] for review in artist['reviews']]
    )
	return artist_data

def get_track_artist_data(ps_df, debug=True):
	"""ps_df is a dataframe with a bunch of tracks"""
	artist_uris = ps_df['artist_uri']
	artist_series_columns = ['genres','familiarity','hotttnesss',
	        'discovery','biographies', 'reviews']
	artist_data = []

	for i, uri in enumerate(artist_uris):
		try:
			artist_data.append((uri, get_data_from_artist_uri(uri)))
		except TypeError:
			if debug: print "error getting track artist data for ", uri
			pass
		time.sleep(3)
		if debug: 
			if i%10==0:print i

	uris, data = zip(*artist_data)
	a, b, c, d, e, f = zip(*data)
	tmp = pd.DataFrame({artist_series_columns[0]:a,
	                    artist_series_columns[1]:b,
	                    artist_series_columns[2]:c,
	                    artist_series_columns[3]:d,
	                    artist_series_columns[4]:e,
	                    artist_series_columns[5]:f})
	tmp['artist_uri'] = uris
	ps_df2 = ps_df.copy()
	ps_df2 = pd.merge(ps_df2, tmp, on='artist_uri')
	return ps_df2

def get_en_track_data(track_uri):
	base_url = 'http://developer.echonest.com/api/v4/track/profile?'
	suffix = \
        'api_key='+ keys['EN_API_KEY']+'&'\
        'id='+track_uri+'&'+\
        'bucket=audio_summary'
	r = requests.get(base_url+suffix)
	return json.loads(r.content)['response']

def get_data_from_track_uri(track_uri):
	track = get_en_track_data(track_uri).get('track')
	if track is not None:
		series = pd.Series(track.get('audio_summary').values(),
                          index=track.get('audio_summary').keys())
		try:
			if 'analysis_url' in series.index:
				series = series.drop('analysis_url', errors='ignore')
		except ValueError:
			print 'no analysis url for', track_uri
		series.set_value('track_uri',track_uri)
		return series
	else:
		raise EchoNestAPIException('Issue with Echo Nest API probably')

def get_track_data(ps_df2, debug=True):
	"""
	Uses functions above to get track data from Echo Nest
	and merges that data with dataframe given above (ps_df2)
	"""
	track_series_columns = ['key','tempo','energy','liveness','speechiness',
	        'acousticness','instrumentalness','mode','time_signature',
	        'duration','loudness','valence','danceability']
	track_uris = ps_df2['track_uri']
	track_data = pd.DataFrame()
	import time
	for i, uri in enumerate(track_uris):
		try:
			track_data = track_data.append(get_data_from_track_uri(uri), ignore_index=True)
		except EchoNestAPIException:
			if debug: print "error on uri",uri, 'index=',i
		time.sleep(2)
		if i%10==0:print i

	ps_df3 = ps_df2.copy()
	ps_df3 = pd.merge(ps_df2, track_data, on='track_uri', how="outer")
	ps_df3.drop_duplicates('track_uri',inplace=True)
	return ps_df3

def main(user_name, playlist_name):
	#setup
	print "Setting up"
	keys = read_keys()

	sp = login_with_token(user_name)
	user_id = get_user_id(sp)
	
	#get playlist tracks from spotify
	print "getting playlist tracks from spotify"
	ps_tracks = get_playlist_tracks(user_id, playlist_name)
	ps_df = make_df_from_track_list(ps_tracks)

	#merge with track and artist info from echo nest
	print "merge with artist info from echo nest"
	ps_df2 = get_track_artist_data(ps_df)
	print "merge with track info from echo nest"
	ps_df3 =  get_track_data(ps_df2)

	return ps_df3


if '__main__' in __name__:
	user_name = sys.argv[1]
	playlist_name = sys.argv[2]
	main(user_name, playlist_name)
	