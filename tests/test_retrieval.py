import unittest
from src.retrieval import retrieve_similar_movies, store_movie_embeddings
from pinecone import Pinecone
import sys
import os
from dotenv import load_dotenv
import yaml

# Ensure 'src' is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Load environment variables
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# Load configuration
def load_config():
    with open("config.yaml", "r") as file:
        return yaml.safe_load(file)

config = load_config()

# Initialize Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)

# Pinecone Index configuration
INDEX_NAME = config["pinecone"]["index_name"]

class TestRetrieval(unittest.TestCase):

    def test_index_exists(self):
        indexes = pc.list_indexes().names()
        self.assertIn(INDEX_NAME, indexes, "Index does not exist. Did you run retrieval.py?")

    # def test_store_embeddings(self):
    #     try:
    #         store_movie_embeddings()
    #         print("✅ Movie embeddings stored successfully!")
    #     except Exception as e:
    #         self.fail(f"Embedding storage failed: {e}")

    def test_retrieve_movies(self):
        query = "Mind-bending sci-fi movies like Interstellar"
        results = retrieve_similar_movies(query, top_k=5)

        self.assertGreater(len(results), 0, "No recommendations returned!")

        for movie in results:
            self.assertIn("title", movie)
            self.assertIn("scores", movie)  # Corrected from "score"
            self.assertGreater(movie["scores"], 0, "Scores should be positive!")

        print("\n✅ Retrieval test passed! Recommended movies:")
        for movie in results:
            print(f"🎥 {movie['title']} ({movie['scores']}% match)")

    def test_empty_query(self):
        """Test behavior when an empty query is given."""
        results = retrieve_similar_movies("", top_k=5)
        self.assertEqual(len(results), 0, "Empty query should return no results.")

    def test_invalid_query(self):
        """Test retrieval with a completely random query."""
        query = "ajsdhaksjdhakjsd"  # Nonsense query
        results = retrieve_similar_movies(query, top_k=5)
        self.assertLessEqual(len(results), 2, "Random query should return few or no results.")

if __name__ == "__main__":
    unittest.main()
