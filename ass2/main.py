import numpy as np
import pandas as pd
import sklearn 

user_reviews = pd.read_csv('user_reviews.csv')
movie_genres = pd.read_csv('movie_genres.csv')

user_reviews_copy = user_reviews.copy()
movie_genres_copy = movie_genres.copy()

# Implement knn for similarly rated movies

# Get movie titles by extratcing headers from user_reviews
movie_titles = user_reviews.columns.values.tolist()

print(movie_titles)