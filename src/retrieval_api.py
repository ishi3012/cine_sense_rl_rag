"""
FastAPI Service for External Requests.

Purpose:
- Provides a REST API for the movie retrieval system.
- Exposes `retrieve_similar_movies()` for external requests.
- Accepts filters like genre and min_rating.

Key Endpoints:
    /recommend:
        - Accepts a query (e.g., "Mind-bending sci-fi movies like Interstellar").
        - Calls `retrieve_similar_movies()`.
        - Returns top similar movies in JSON format.
"""

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from typing import Optional
from src.retrieval import retrieve_similar_movies

# Initialize FastAPI app
app = FastAPI(title="Movie Recommendation API", version="1.1")


@app.get("/")
def home():
    return {"message": "🎬 Welcome to the Movie Recommendation API! Use /recommend to get movie suggestions."}


@app.get("/recommend")
def recommend_movies(
    query: str = Query(..., description="Enter movie query for recommendations"),
    top_k: int = Query(5, ge=1, le=20, description="Number of recommendations"),
    genre: Optional[str] = Query(None, description="Filter by genre"),
    min_rating: Optional[float] = Query(0.0, ge=0.0, le=5.0, description="Minimum movie rating")
):
    """
    Recommend movies based on the user query.
    Example: /recommend?query=Sci-Fi like Interstellar&top_k=5&genre=Sci-Fi&min_rating=4.0
    """

    if not query.strip():
        raise HTTPException(status_code=400, detail="❌ Query cannot be empty!")

    # Convert min_rating to an integer for proper filtering
    min_rating = int(min_rating)

    print(f"📥 API Request - Query: {query}, Top K: {top_k}, Genre: {genre}, Min Rating: {min_rating}")

    # Retrieve similar movies from the retrieval module
    results = retrieve_similar_movies(query, top_k)

    if not results:
        raise HTTPException(status_code=404, detail="❌ No recommendations found.")

    # Apply additional filters if specified
    filtered_results = [
        movie for movie in results
        if (not genre or genre.lower() in movie["genres"].lower())  # Genre filtering
        and movie["rating"] >= min_rating  # Rating filtering
    ]
    final_results = filtered_results[:top_k]
    
    # return {"query": query, "results": filtered_results}
    return {"query": query, "results": final_results}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
