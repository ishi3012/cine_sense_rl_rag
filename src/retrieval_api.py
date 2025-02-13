"""
FastAPI Service for External Requests.

Purpose:

- Provides a REST API for the movie retrieval system.
- It exposes retrieval.py as a service, allowing external apps or users to request recommendations via HTTP.

Key Functions:
    /recommend endpoint:
        Accepts a query (e.g., "Mind-bending sci-fi movies like Interstellar").
        Calls retrieve_similar_movies() from retrieval.py.
        Returns top similar movies in a JSON response.


"""

import uvicorn
from fastapi import FastAPI, HTTPException
from src.retrieval import retrieve_similar_movies

# Initialize FastAPI app 
app = FastAPI(title="Movie Recommendation API", version="1.0")

@app.get("/")

def home():
    return {"message": "Welcome to the Movie Recommendation API! Use /recommend to get movie suggestions."}

@app.get("/recommend")
def recommend_movies(query:str, top_k:int = 5):
    """
    Recommend movies based on the user query. 
    Example: /recommend?query=Sci-Fi like Interstellar&top_k=5&genre=Sci-Fi&min_rating=4.0
    """

    if not query.strip():
        raise HTTPException(status_code=400, detail = "Query cannot be empty!")
    
    results = retrieve_similar_movies(query, top_k)

    if not results:
        raise HTTPException(status_code = 404, detail="No Recommendation found.")
    
    return {"query": query, "results":results}

if __name__ =="__main__":
    uvicorn.run(app,host="0.0.0.0", port=8080)