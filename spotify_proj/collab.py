from src.json_to_csv import *

folder = "data/playlist_data/"
co_occurences = update_co_occurrences_from_folder(folder, slice_limit=20)
print(find_top_co_occurrences(co_occurences, "Darude", "Sandstorm", top_n=10))