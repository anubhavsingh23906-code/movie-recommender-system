import pickle
import pandas as pd

with open("movie_dict.pkl", "rb") as f:
    movie_dict = pickle.load(f)

with open("similarity.pkl", "rb") as f:
    similarity = pickle.load(f)

movies = pd.DataFrame(movie_dict)

print("Movies shape:", movies.shape)
print("Similarity shape:", similarity.shape)
print("Number of movies:", len(movies))