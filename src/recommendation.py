"""
    Applies Filtering & Re-ranking on Retrieved Movies

    Purpose:
        - Enhances results from retrieval.py by applying metadata filtering and user-based re-ranking.
        - Ensures recommendations match user preferences (e.g., preferred genres, minimum rating).
        - Filters out low-rated movies and refines recommendations.

    Key Functions:
        - Loads movie metadata (movie_dataset.csv) to apply filtering.
        - Calls retrieve_similar_movies(query, top_k*2) from retrieval.py and refines results.
        - Applies Filters:
            Genre Filtering
            Rating Threshold: Exclude movies below a given rating.
            Returns filtered top-N recommendations.
"""

import pandas as pd
import os
import yaml
from src.retrieval import retrieve_similar_movies

# ✅ Load configuration
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
        """ Load the movie dataset for filtering based on user preferences """
        if not os.path.exists(MOVIE_DATA_PATH):
            raise FileNotFoundError(f"❌ Movie dataset not found at {MOVIE_DATA_PATH}")
        return pd.read_csv(MOVIE_DATA_PATH)

    def get_movie_recommendations(self, query, top_n=5, genre_filter=None, min_rating=0):
        """
        Fetch top movie recommendations and apply filtering.
        """

        recommendations = retrieve_similar_movies(query, top_k=top_n * 2)

        if not recommendations:
            print("⚠️ No recommendations retrieved from retrieval function.")
            return []

        rec_df = pd.DataFrame(recommendations)

        print("📊 Before Filtering:")
        print("🔍 Unique ratings before filtering:", rec_df["rating"].unique())  # Debug rating values

        # Ensure 'rating' column exists
        if "rating" in rec_df.columns:
            rec_df["rating"] = pd.to_numeric(rec_df["rating"], errors="coerce").fillna(0).astype(int)

        print("✅ After Ensuring Rating is Numeric:")
        print("🔍 Unique ratings after conversion:", rec_df["rating"].unique())

        # Apply Genre Filter
        if genre_filter:
            rec_df = rec_df[rec_df["genres"].str.contains(genre_filter, case=False, na=False)]
            print(f"✅ After Genre Filter ({genre_filter}): {len(rec_df)} movies remaining")

        # Apply Rating Filter
        rec_df = rec_df[rec_df["rating"] >= int(min_rating)]
        print(f"✅ After Rating Filter (min_rating={min_rating}): {len(rec_df)} movies remaining")

        # Remove Duplicates (keep highest-rated version of a movie)
        rec_df = rec_df.sort_values(by=["rating", "score"], ascending=[False, False])
        rec_df = rec_df.drop_duplicates(subset=["title"], keep="first")
        
        final_recommendations = rec_df.head(top_n)[["title", "genres", "rating", "score"]].to_dict(orient="records")
        
        return final_recommendations



if __name__ == "__main__":
    recommender = MovieRecommender()
    recommendations = recommender.get_movie_recommendations(
        query="sci-fi movies",
        top_n=7,
        genre_filter="Sci-Fi",
        min_rating=4.0
    )
    print(recommendations)
