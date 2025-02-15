"""
Handles Embedding Storage & Vector Search

Purpose:

- This file is responsible for storing and retrieving movie embeddings in/from Pinecone.
- It converts movie metadata into vector representations and performs similarity searches based on user queries.


"""

from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
import pandas as pd
import os
import yaml
from dotenv import load_dotenv
import re
from collections import Counter

# Load environment variables from .env
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env"))
load_dotenv(dotenv_path)

# Fetch API key securely
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")

if not PINECONE_API_KEY:
    raise ValueError("Missing PINECONE_API_KEY. Set it in .env or environment variables.")

# Load configuration
def load_config():
    with open("config.yaml", "r") as file:
        return yaml.safe_load(file)

config = load_config()

# Pinecone Index configuration
INDEX_NAME = config["pinecone"]["index_name"]
DIMENSION = int(config["pinecone"]["dimension"])
METRIC = config["pinecone"]["metric"]

if not PINECONE_API_KEY:
    raise ValueError("Missing PINECONE_API_KEY. Set it in .env or environment variables.")

pc = Pinecone(api_key=PINECONE_API_KEY)

# Check if the index exists, else create it
if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=DIMENSION,
        metric=METRIC,
        spec=ServerlessSpec(
            cloud="aws",  
            region=PINECONE_ENV  
        )
    )
    print(f'Pinecone Index "{INDEX_NAME}" created successfully!')

index = pc.Index(INDEX_NAME)

# Load embedding model 
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# path to movie dataset
MOVIE_DATA_PATH = config["data"]["dataset_path"]

if not os.path.exists(MOVIE_DATA_PATH):
    raise FileNotFoundError(f"❌ Movie dataset not found at {MOVIE_DATA_PATH}")

# def store_movie_embeddings(start_year = 2000, end_year = 2001, genre_list=["Sci-Fi", "Horror"]):
#     """Encodes movies and stores them in Pinecone."""
#     print("🚀 Loading movie dataset...")   
    
#     df = pd.read_csv(MOVIE_DATA_PATH)

#     # Ensure dataset has the required columns
#     required_columns = {"movieId", "title", "genres"}
#     if not required_columns.issubset(df.columns):
#         raise ValueError(f"Dataset must contain columns: {required_columns}")

#     df["text"] = df["title"] + " " + df["genres"]
   
#     # Extract year
#     df["year"] = df["title"].apply(lambda x: int(re.search(r"\((\d{4})\)", str(x)).group(1)) if re.search(r"\((\d{4})\)", str(x)) else None)
#     df["year"].fillna(0, inplace=True)  # Fill missing years
#     df["year"] = df["year"].astype(int)  # Ensure integer type

#     # ✅ Filter dataset only by year range
#     movies_in_range = df[(df["year"] >= start_year) & (df["year"] <= end_year)]

#     print(f"🎥 Movies from {start_year} to {end_year}")
#     print(f"🔄 {len(movies_in_range)} movies will be processed and stored in Pinecone.")

#     remaining_count = len(movies_in_range)
#     to_upsert = []
#     for i, row in movies_in_range.iterrows():
#         unique_id = f"{row['userId']}_{row['movieId']}"
#         embedding = model.encode(row["title"] + " " + row["genres"], convert_to_numpy=True).tolist()

#         to_upsert.append((unique_id, embedding, {
#         "userId": row["userId"],
#         "movieId": row["movieId"],
#         "title": row["title"],
#         "genres": row["genres"],
#         "rating": row["rating"],  
#         "year": row["year"]
#     }))
        
#         if len(to_upsert) >= 1000:
#             index.upsert(vectors=to_upsert)
#             to_upsert = []
#             remaining_count-=1000
#             print(f"📌 {remaining_count} movies remaining to be processed...")
#             print(f"{index.describe_index_stats()["total_vector_count"]} loaded embeddings in Pinecone.")

#     # Final batch upload
#     if to_upsert:
#         index.upsert(vectors=to_upsert)
#         print(f"✅ {len(to_upsert)} new movies indexed with ratings!")

#     print("🎉 Movie embeddings updated successfully!")
#     get_pinecone_record_count()

def store_movie_embeddings():
    """Encodes unique movies and stores them in Pinecone."""

    print("🚀 Loading movie dataset...")
    df = pd.read_csv(MOVIE_DATA_PATH)    
   
    # Extract year
    df["year"] = df["title"].apply(lambda x: int(re.search(r"\((\d{4})\)", str(x)).group(1)) if re.search(r"\((\d{4})\)", str(x)) else None)
    df["year"].fillna(0, inplace=True)  # Fill missing years
    df["year"] = df["year"].astype(int)  # Ensure integer type

    # Ensure dataset has the required columns
    required_columns = {"movieId", "title", "genres", "year"}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"Dataset must contain columns: {required_columns}")

    df["text"] = df["title"] + " " + df["genres"] + " " + df["year"].astype(str)

    # ✅ Store only unique movies (ignore userId)
    unique_movies = df.drop_duplicates(subset=["movieId"])

    print(f"🔹 Storing {len(unique_movies)} unique movies in Pinecone.")

    to_upsert = []
    for _, row in unique_movies.iterrows():
        movie_id = str(row["movieId"])
        embedding = model.encode(row["text"], convert_to_numpy=True).tolist()
        to_upsert.append((movie_id, embedding, {
            "title": row["title"], 
            "genres": row["genres"], 
            "rating": row.get("rating", "N/A"),
            "year": row["year"]
        }))
        
        if len(to_upsert) >= 1000:
            index.upsert(vectors=to_upsert)
            to_upsert = []

    # Final batch upload
    if to_upsert:
        index.upsert(vectors=to_upsert)

    print("✅ Movie embeddings updated successfully!")

    
def get_pinecone_record_count():
    stats = index.describe_index_stats()
    total_records = stats["total_vector_count"]
    print(f"📊 Total records in Pinecone: {total_records}")
    return total_records

def retrieve_similar_movies(query, top_k=5):
    """Returns top-k unique similar movies based on content similarity."""

    print(f"🔍 Processing query: {query}")
    query_embedding = model.encode(query, convert_to_numpy=True).tolist()

    result = index.query(vector=query_embedding, top_k=top_k * 3, include_metadata=True)  # Fetch more results

    if "matches" not in result or not result["matches"]:
        print("⚠️ No matches found in Pinecone!")
        return []

    # print(f"✅ Retrieved {len(result['matches'])} results from Pinecone.")
    # print(result)

    recommendations = []
    for match in result["matches"]:
        metadata = match.get("metadata", {})
        movie_id = match.get("id", None)  # Ensure 'id' is captured

        if movie_id and "title" in metadata:
            recommendations.append({
                "id": movie_id,  # Ensure 'id' is included
                "title": metadata.get("title", "Unknown Title"),
                "genres": metadata.get("genres", "Unknown Genre"),
                "rating": metadata.get("rating", "N/A"),
                "score": round(match["score"] * 100, 2)
            })

    if not recommendations:
        print("❌ Error: No valid recommendations generated.")

    # print(f"✅ Unique Recommendations Found: {len(recommendations)}")
    return recommendations



def retrieve_personalized_movies(query, user_id, top_k=5):
    """Returns personalized movie recommendations for a user using RL-based filtering."""

    # Step 1: Get similar movies from the generic function
    similar_movies = retrieve_similar_movies(query, top_k * 2)  

    # Step 2: Filter only movies relevant to `userId`
    personalized_recommendations = [movie for movie in similar_movies if str(user_id) in movie["id"]][:top_k]  # Limit results to top_k
    print(f"🎯 Personalized Recommendations for User {user_id}:")
    return personalized_recommendations
    
if __name__ == "__main__":  
    # store_movie_embeddings()    
    get_pinecone_record_count()
