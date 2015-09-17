# 
# This script is used to create a dataframe with songs I love  
# (labeled with column, love=1) and songs that I just like (love=0)
# These two playlists are the second and third sys.argv.  The first 
# is a username.
#
# e.g. $ python clean_data.py 'dbgoldberg01' 'science' 'justlike'
#

import playlist_data
import sys
import pandas as pd
import numpy as np

def main(username='dbgoldberg01', favorites_name='science', justlike_name='justlike'):
	
	favorites = playlist_data.main(username, favorites_name)
	favorites['love'] = 1
	
	justlike = playlist_data.main(username, justlike_name)
	justlike['love'] = 0

	df_all = favorites.append(justlike, ignore_index=True)
	df_all = df_all.reindex(np.random.permutation(df_all.index))

	relavent_columns = ['track_popularity','discovery','familiarity',
                    'hotttnesss','acousticness','danceability','duration',
                    'energy','instrumentalness','liveness',
                    'loudness', 'speechiness','tempo', 'valence']
	df_all = df_all[relavent_columns]

	to_normalize = ['duration','tempo','track_popularity','loudness']
	df_all[to_normalize] = df_all[to_normalize] \
            .apply(lambda x: x/x.max())	
	return df_all

if '__main__' in __name__:
	res = main(sys.argv[1], sys.argv[2], sys.argv[3])
	sys.stdout(res)