# **CineSense: Reinforcement Learning-Driven RAG Movie Recommendation System 🎬🤖**

## 📌 Overview
**CineSense** is an AI-powered **movie recommendation system** that leverages **Retrieval-Augmented Generation (RAG)** and **Reinforcement Learning (RL)** to provide **personalized, engaging, and explainable recommendations**. 

By optimizing recommendations based on **user preferences, watch history, and engagement metrics**, CineSense enhances content discovery and keeps users engaged.

---

## 🚀 Key Features
✅ **RAG-Based Retrieval** – Uses **Sentence-BERT embeddings** and **vector similarity search** to retrieve relevant movies.  
✅ **Reinforcement Learning Optimization** – Trains an **RL agent (DQN/PPO)** to improve recommendations based on **user engagement**.  
✅ **Multi-Modal Data** – Integrates **metadata, genres, reviews, and external ratings (IMDb, Rotten Tomatoes)**.  
✅ **Explainability** – Provides **human-like justifications** for recommendations.  
✅ **API & UI** – Features a **REST API (FastAPI/Flask)** and an interactive **UI (Streamlit/Gradio)**.  

---

## 📁 Project Structure
```
CineSense
│── data/                      # Datasets (raw & processed)
│── models/                    # Trained models & checkpoints
│── src/                       # Core code (retrieval, RL, recommendation logic)
│── notebooks/                 # Jupyter notebooks (EDA, training)
│── ui/                        # UI (Streamlit/Gradio)
│── tests/                     # Unit tests
│── requirements.txt           # Dependencies
│── config.yaml                # Configurations
│── README.md                  # Project documentation
```


---

## 🛠️ Setup Instructions

### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/ishi3012/cine_sense_rl_rag.git
cd CineSense
```

2️⃣ Install Dependencies
``` bash
pip install -r requirements.txt
```

🔄 Preprocess MovieLens 1M Dataset
Before training models, preprocess the MovieLens dataset.

Run Preprocessing (First Time)

``` bash
python src/data_preprocessing.py
```
👉 If the processed data (train.csv and test.csv) already exists, this step will be skipped.

Force Reprocess Raw Data, if you need to reprocess the data, use: 
``` bash
python src/data_preprocessing.py --force
```
👉 This will overwrite train.csv and test.csv.




3️⃣ Run the API

```bash
uvicorn src.api:app --reload
```

4️⃣ Launch the UI
```bash
streamlit run ui/app.py
```
🔍 How It Works
- **Retrieval Module** – Retrieves movies using Sentence-BERT embeddings and vector search.
- **RL Agent – Optimizes** - recommendations based on click-through rate (CTR) & watch time.
- **User Interaction Simulation** – Generates synthetic feedback for RL training.
- **Recommendations API** – Provides real-time movie suggestions.

🌟 Future Enhancements
- Real-time trend updates (e.g., trending movies, new releases).
- Multi-modal recommendations (text + trailers + user behavior).
- Advanced RL techniques (Contextual Bandits, Model-based RL).
- A/B Testing for model evaluation.

🤝 Contributions
Contributions are welcome! Open an issue or submit a PR 🚀.

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for more details.