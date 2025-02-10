import os
import argparse
import pandas as pd
import sqlite3
from sklearn.model_selection import train_test_split

# File paths

movie_path = "data/raw/movies.dat"
ratings_path = "data/raw/ratings.dat"
users_path = "data/raw/users.dat"
train_path = "data/processed/train.csv"
test_path = "data/processed/test.csv"
db_path = "data/processed/cineSense.db"

# Allow force processing
parser = argparse.ArgumentParser(description="Preprocess MovieLens 1M dataset.")
parser.add_argument("--force", action="store_true", help="Force preprocessing")
parser.add_argument("--check-db", action="store_true", help="Check data in cineSense.db")
args = parser.parse_args()


# check if proccssed data already exists
if os.path.exists(train_path) and os.path.exists(test_path) and not args.force:
    print(" ✅Processed data already exists. Skipping processing. Use --force to reprocess.")
else:
    print("🔄Preprocessing raw data ...")

    # load datasets
    movies = pd.read_csv(movie_path, sep="::", engine="python", names=["movieId", "title", "genres"], encoding="ISO-8859-1")
    ratings = pd.read_csv(ratings_path, sep="::", engine="python", names=["userId", "movieId", "rating", "timestamp"], encoding="ISO-8859-1")
    users = pd.read_csv(users_path, sep="::", engine="python", names=["userId", "gender", "age", "occupation", "zipCode"], encoding="ISO-8859-1")

    # Convert timestamps to datetime
    ratings["timestamp"] = pd.to_datetime(ratings["timestamp"], unit="s")

    # Extract release year from movie title
    movies["year"] = movies["title"].str.extract(r'\((\d{4})\)')[0]
    movies["year"] = pd.to_numeric(movies["year"], errors="coerce")

    # split genres into lists
    movies["genres"] = movies["genres"].apply(lambda x: "|".join(x.split("|")) if isinstance(x, str) else "")
    
    #Merge datasets
    df = ratings.merge(movies, on = "movieId", how="left").merge(users, on="userId", how="left")
    df.drop(columns=["timestamp"], inplace=True)

    print(f"Loaded movies = {df.shape[0]} \nFeatures : [{df.columns}]")

    # Split dataset into train and test sets (80% train and 20% test)
    train, test = train_test_split(df, test_size=0.2, random_state=42)

    train.to_csv(train_path, index=False, encoding="ISO-8859-1")
    test.to_csv(test_path, index=False, encoding="ISO-8859-1")

    print(df.shape)
    # Save processed data to SQLite database
    conn = sqlite3.connect(db_path)
    df.to_sql("movies_metadata", conn, if_exists="replace", index = False)
    # test.to_sql("test", conn, if_exists="replace", index = False)
    conn.close()

    print(f"✅ Processing complete! Train: {len(train)} rows, Test: {len(test)} rows.")



def check_database():
    """Check the contents of the cineSense.db database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    #Display tables in database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    print(f"Available tables in the database : {tables}")

    # Display sample data 
    for table in ["movies_metadata"]:
        try:
            df_sample = pd.read_sql(f"SELECT * FROM {table} LIMIT 5;", conn)
            print(f"\nSample data from {table}:")
            print(df_sample)
        except Exception as e:
            print(f"Error reading table {table}: {e}")
    
    conn.close()

if args.check_db:
    check_database()
    exit()


