from src.json_to_csv import *
from src.database import *
import random

folder = "data/playlist_data/"
# Dictionary testing

#co_occurences = update_co_occurrences_from_folder(folder, slice_limit=5)
#print(find_top_co_occurrences(co_occurences, "Drake", "One Dance", top_n=10))


# Database testing

artist_name = "Eminem"
song_name = "The Real Slim Shady"
n_slices = 5
db_path = "data/co_occurrences.db"

#setup_database(db_path)
#update_co_occurrences_from_folder(folder, db_path, slice_limit=n_slices)
print('hmm')
top_co_occurring_songs = get_top_co_occurring_songs(db_path, artist_name, song_name)

#for song in top_co_occurring_songs:
#    print(song)

print(artist_name, song_name)
print('--------')

# Start with artist and song, get top related song, get top related artist, get top related song, etc.
for i in range(1000):
    top_co_occurring_songs = get_top_co_occurring_songs(db_path, artist_name, song_name)
    if not top_co_occurring_songs:
        print(f"No co-occurring songs found for {artist_name} - {song_name}")
    artist_name, song_name = artist_song_string_split(top_co_occurring_songs[random.randint(0, len(top_co_occurring_songs)-1)])
    print(artist_name, song_name)
    print('--------')