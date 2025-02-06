# import pandas as pd
# from sklearn.model_selection import train_test_split

# # Define file paths
# movies_path = "data/raw/movies.dat"
# ratings_path = "data/raw/ratings.dat"
# users_path = "data/raw/users.dat"
# output_train_path = "data/processed/train.csv"
# output_test_path = "data/processed/test.csv"

# # Load datasets with proper separator
# movies = pd.read_csv(movies_path, sep="::", engine="python", names=["movieId", "title", "genres"], encoding="ISO-8859-1")
# ratings = pd.read_csv(ratings_path, sep="::", engine="python", names=["userId", "movieId", "rating", "timestamp"], encoding="ISO-8859-1")
# users = pd.read_csv(users_path, sep="::", engine="python", names=["userId", "gender", "age", "occupation", "zipCode"], encoding="ISO-8859-1")

# # Merge ratings with Movie data
# movie_df = ratings.merge(movies, on="movieId", how="left")

# # Merge users data with movie and ratings dataset
# movie_df = movie_df.merge(users, on="userId", how="left")

# # Drop duplicate column
# movie_df.drop(columns=["timestamp"], inplace=True)

# # Save movie_df to csv file. 
# movie_df.to_csv("data/processed/movie_dataset.csv", index=False)

# print("\n✅ Movie dataset successfully saved at: data/processed/movie_dataset.csv\n")

# # Split the dataset into train and test datasets (80% train, 20%)
# train, test = train_test_split(movie_df, test_size=0.2, random_state=42)
# train.to_csv(output_train_path, index=False,encoding="ISO-8859-1")
# test.to_csv(output_test_path, index=False, encoding="ISO-8859-1")

# print(f"✅ Preprocessing complete! Train: {len(train)} rows, Test: {len(test)} rows.")


import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split

# File paths
movies_path = "data/raw/movies.dat"
ratings_path = "data/raw/ratings.dat"
users_path = "data/raw/users.dat"
train_path = "data/processed/train.csv"
test_path = "data/processed/test.csv"

# Argument parser to allow force processing
parser = argparse.ArgumentParser(description="Preprocess MovieLens 1M dataset.")
parser.add_argument("--force", action="store_true", help="Force reprocessing even if processed files exist.")
args = parser.parse_args()

# Check if processed data already exists
if os.path.exists(train_path) and os.path.exists(test_path) and not args.force:
    print("✅ Processed data already exists. Skipping processing. Use python src/data_preprocessing.py --force to reprocess.")
else:
    print("🔄 Processing raw data...")

    # Load datasets with correct encoding
    movies = pd.read_csv(movies_path, sep="::", engine="python", names=["movieId", "title", "genres"], encoding="ISO-8859-1")
    ratings = pd.read_csv(ratings_path, sep="::", engine="python", names=["userId", "movieId", "rating", "timestamp"], encoding="ISO-8859-1")
    users = pd.read_csv(users_path, sep="::", engine="python", names=["userId", "gender", "age", "occupation", "zipCode"], encoding="ISO-8859-1")

    # Merge datasets
    df = ratings.merge(movies, on="movieId", how="left").merge(users, on="userId", how="left")
    df.drop(columns=["timestamp"], inplace=True)

    # Split into train & test sets (80% train, 20% test)
    train, test = train_test_split(df, test_size=0.2, random_state=42)

    # Save processed data
    train.to_csv(train_path, index=False, encoding="ISO-8859-1")
    test.to_csv(test_path, index=False, encoding="ISO-8859-1")
    print(f"✅ Processing complete! Train: {len(train)} rows, Test: {len(test)} rows.")

