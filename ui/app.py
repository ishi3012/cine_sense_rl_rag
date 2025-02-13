import streamlit as st
import requests
import yaml

# Load API URL from config.yaml
def load_config():
    with open("config.yaml", "r") as file:
        return yaml.safe_load(file)

config = load_config()
API_URL = config["api"]["url"]

# Streamlit UI Setup
st.set_page_config(page_title="CineSense: Movie Recommendation", layout="wide")
st.title("🎬 CineSense Movie Recommender")
st.markdown("Enter a movie description or example to get the recommendations!")

# User Inputs
query = st.text_input("Enter a movie description:", placeholder="Mind-bending sci-fi like Interstellar")
top_k = st.slider("Number of recommendations:", min_value=1, max_value=10, value=5)
genre = st.text_input("Filter by Genre (optional):")
min_rating = st.slider("Minimum rating:", 0.0, 5.0, 3.0)

# Submit Button
if st.button("Get Recommendations"):
    if query.strip():
        with st.spinner("Fetching recommendations..."):
            try:
                api_url = f"{API_URL}/recommend"
                params = {"query": query, "top_k": top_k, "genre": genre, "min_rating": min_rating}
                response = requests.get(api_url, params=params)
                
                # ✅ Handle empty or invalid responses safely
                if response.status_code == 200:
                    data = response.json()
                    if "results" in data and data["results"]:
                        st.subheader("Recommended Movies:")
                        for movie in data["results"]:
                            st.write(f"🎥 **{movie['title']}** ({movie['genres']}) - ⭐ {movie['rating']}")
                    else:
                        st.error("❌ No recommendations found!")
                else:
                    st.error(f"❌ API Error: {response.text}")
                    
            except Exception as e:
                st.error(f"⚠️ An error occurred: {str(e)}")