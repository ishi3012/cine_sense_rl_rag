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

# Load environment variables from .env
dotenv_path = os.path.join(os.path.dirname(__file__), "../.env")
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
DIMENSION = config["pinecone"]["dimension"]
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
# else:
#     print(f'Pinecone Index {pc.list_indexes().names()} found!')

index = pc.Index(INDEX_NAME)

# Load embedding model 
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# path to movie dataset
MOVIE_DATA_PATH = config["data"]["dataset_path"]

def store_movie_embeddings():
    """Encodes only NEW movies and stores them in Pinecone."""
    print("Loading movie dataset...")
    
    if not os.path.exists(MOVIE_DATA_PATH):
        raise FileNotFoundError(f"Movie dataset not found at {MOVIE_DATA_PATH}")

    df = pd.read_csv(MOVIE_DATA_PATH)
    remaining_count = df.shape[0]
    
    if "movieId" not in df.columns or "title" not in df.columns or "genres" not in df.columns:
        raise ValueError("Dataset must contain 'MovieID', 'Title', and 'Genres' columns.")

    df["text"] = df["title"] + " " + df["genres"]

    print("Fetching existing movie records from Pinecone in batches...")
    existing_ids = set()
    batch_size = 1000  # Limit batch size to avoid URI length issues

    movie_ids = df["movieId"].astype(str).tolist()
    for i in range(0, len(movie_ids), batch_size):
        batch = movie_ids[i:i+batch_size]
        existing_records = index.fetch(ids=batch)  
        existing_ids.update(existing_records.vectors.keys())  

    print("Filtering new movies to encode and store in Pinecone...")
    new_movies_df = df[~df["movieId"].astype(str).isin(existing_ids)]  

    print(f"{len(new_movies_df)} new movies will be processed.")
    to_upsert = []
    
    for i, row in new_movies_df.iterrows():
        movie_id = str(row["movieId"])
        embedding = model.encode(row["text"], convert_to_numpy=True).tolist()
        to_upsert.append((movie_id, embedding, {"title": row["title"], "genres": row["genres"]}))

        # Batch upserting every 1000 items for efficiency
        if len(to_upsert) >= 1000:
            index.upsert(vectors=to_upsert)
            to_upsert = []
            remaining_count -= 1000
            print(f"{remaining_count} movie records left to be encoded...")

    # Final batch upload
    if to_upsert:
        index.upsert(vectors=to_upsert)
        print(f"✅ {len(to_upsert)} new movies indexed!")
    else:
        print("🎉 No new movies to add!")

    print("✅ Movie embeddings updated successfully!")

def get_pinecone_record_count():
    """Fetches and prints the total number of records in Pinecone."""
    stats = index.describe_index_stats()
    total_records = stats["total_vector_count"]
    print(f"📊 Total records in Pinecone: {total_records}")
    return total_records



def retrieve_similar_movies(query, top_k = 5):
    """ Returns top-k similar movies along with similarity scores."""

    print(f"Processing query: {query}")
    query_embedding = model.encode(query, convert_to_numpy = True).tolist()

    result = index.query(vector = query_embedding, top_k=top_k, include_metadata=True)
    # result = result.drop_duplicates(subset=["id"])

    if "matches" not in result:
        print("⚠️ No matches found.")
        return []
    
    recommendations = [
        {
            "id" : match["id"],
            "title" : match["metadata"]["title"],
            "genres": match["metadata"]["genres"],
            "rating": match["metadata"].get("rating", "N/A"),
            "scores": round(match["score"]*100, 2)
        }
        for match in result["matches"]
        ]
    
    return recommendations

if __name__ == "__main__":  
    store_movie_embeddings()
    stats = index.describe_index_stats()
    print(stats)





