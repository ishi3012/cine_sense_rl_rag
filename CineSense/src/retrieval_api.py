from fastapi import FastAPI, HTTPEXception
from src.retrieval import retrieve_similar_movies

# Initialize FastAPI app 
app = FastAPI(title="Movie Recommendation API", version="1.0")

@app.ge("/")

def home():
    return {"message": "Welcome to the Movie Recommendation API! Use /recommend to get movie suggestions."}

@app.get("/recommend")
def recommend_movies(query:str, top_k:int = 5):
    """
    Recommend movies based on the user query. 
    Example: /recommend?query=Mind-bending sci-fi like Interstellar&top_k=5
    """

    if not query.strip():
        raise HTTPEXception(status_code=400, detail = "Query cannot be empty!")
    
    results = retrieve_similar_movies(query, top_k)

    if not results:
        raise HTTPEXception(status_code = 404, detail="No Recommendation found.")
    
    return {"query": query, "results":results}