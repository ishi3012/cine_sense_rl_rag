"""
Applies Filtering & Re-ranking on Retrieved Movies

Purpose:
    - Enhances results from retrieval.py by applying metadata filtering and user-based re-ranking.
    - It ensures that recommendations match user preferences (e.g., preferred genres, minimum rating).

Key Functions:
    - Loads movie metadata (movie_dataset.csv) to apply filtering.
    - Calls retrieve_similar_movies(query, top_k*2) from retrieval.py and refines the results.
    - Applies Filters:
        Genre Filtering: Only recommend movies in a specific genre (e.g., "Sci-Fi").
        Rating Threshold: Exclude movies below a given rating.
        Returns filtered top-N recommendations.

"""

import pandas as pd
import os
from src.retrieval import retrieve_similar_movies
import yaml

def load_config():
    with open("config.yaml", "r") as file:
        return yaml.safe_load(file)

config = load_config()
MOVIE_DATA_PATH = config["data"]["dataset_path"]

class MovieRecommender:
    def __init__(self):

        """Initialize recommender class with movie dataset."""
        self.movies_df = self.load_data()

    def load_data(self):
        """ Load the movie dataset for filtering based on user preferenes"""
        if not os.path.exists(MOVIE_DATA_PATH):
            raise FileNotFoundError(f"Movie dataset not found at {MOVIE_DATA_PATH}")
    
        return pd.read_csv(MOVIE_DATA_PATH)

    def get_movie_recommendations(self, query, top_n = 5, genre_filter=None, min_rating = 0):
        """
        Fetch top movie recommendations and filter results. 
        """

        recommendations = retrieve_similar_movies(query, top_k=top_n*2)

        rec_df = pd.DataFrame(recommendations)

        if "movieId" in self.movies_df.columns and "rating" in self.movies_df.columns:
            # rec_df = rec_df.merge(self.movies_df[["movieId", "rating"]], left_on="id", right_on="movieId", how="left")
            # Ensure 'id' and 'movieId' have the same data type
            rec_df["id"] = rec_df["id"].astype(str)
            self.movies_df["movieId"] = self.movies_df["movieId"].astype(str)

            # Merge retrieved results with additional metadata
            rec_df = rec_df.merge(self.movies_df[["movieId", "rating"]], left_on="id", right_on="movieId", how="left")
            
            rec_df = rec_df.drop_duplicates(subset=["id"])

        if genre_filter:
            rec_df = rec_df[rec_df["genres"].str.contains(genre_filter, case=False, na=False)]

        rec_df = rec_df[rec_df["rating"] >= min_rating]

        final_recommendations  = rec_df.head(top_n)[["title", "genres", "rating", "scores"]].to_dict(orient="records")
        
        return final_recommendations

if __name__ == "__main__":
    recommender = MovieRecommender()
    recommendations = recommender.get_movie_recommendations("Mind-bending sci-fi movies like Interstellar", top_n=5, genre_filter="Sci-Fi", min_rating=4.0)
    print(recommendations)
