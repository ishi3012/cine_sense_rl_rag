import streamlit as st
import requests

# FastAPI backend URL
API_URL = "http://127.0.0.1:8000/recommend"

#Stremlit UI
st.set_page_config(page_title="CineSense: Movie Recommendation", layout="wide")

st.title("AI-Powered Movie recommendation system")
st.markdown("Enter a movie description or example to get the recommendations!")

# User Input

query = st.text_input = ("Enter a movie description: ", placeholder="Mind-bending sci-fi like Interstellar")
top_k = st.slider("Number of recommendations: ", min_value = 1, max_vlue = 10, value = 5)

#Submit button
if st.button("Get Recommendations"):
    if query.strip():
        with st.spinner("Fetching recommendations..."):
            try:
                response = requests.get(API_URL, parrams={"query":query, "top_k":top_k})
                data = response.json()
                
                if response.status_code == 200:
                    st.subheader("Recommended Movies: ")
                    for movie in data["results"]:
                        st.write(f"**{movie['title']}** ({movie['genres']}) - 🔥 *{movie['score']}% match*")
                else:
                    st.error(f"❌ Error: {data['detail']}")
            except Exception as e:
                st.error(f"⚠️ An error occurred: {str(e)}")
    else:
        st.warning("⚠️ Please enter a query before searching.")


