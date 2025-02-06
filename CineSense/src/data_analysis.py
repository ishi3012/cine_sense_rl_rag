import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

movie_df = pd.read_csv("data/processed/movie_dataset.csv")


print(f"\n~~~~~~~~~~~~~~ The movie dataset :~~~~~~~~~~~~~~~~~~~~~~~\n")
print(movie_df.head(3))

## Step 2: Check Missing Values**
print(f"\n~~~~~~~~~~~~~~ Missing Values :~~~~~~~~~~~~~~~~~~~~~~~\n")
print(movie_df.isnull().sum())

print(f"\n~~~~~~~~~~~~~~ Rating Statistics :~~~~~~~~~~~~~~~~~~~~~~~\n")
print(movie_df["rating"].describe())

# Plot rating distribution
plt.figure(figsize=(8,5))
sns.histplot(movie_df["rating"], bins=10)#, kde=True)
plt.title("Distribution of Movie Ratings")
plt.xlabel("Rating")
plt.ylabel("Count")
plt.savefig("data/processed/rating_distribution.png")
plt.show()

# Most Rated Movies**
most_rated = movie_df.groupby("title")["rating"].count().sort_values(ascending=False).head(10)
print(f"\n~~~~~~~~~~~~~~ Most Rated Movies :~~~~~~~~~~~~~~~~~~~~~~~\n")
print(most_rated)


# Popular Genres**
genre_counts = movie_df["genres"].str.split("|", expand=True).stack().value_counts()
print(f"\n~~~~~~~~~~~~~~ Genre Distribution :~~~~~~~~~~~~~~~~~~~~~~~\n")
print(genre_counts.head(10))

# Plot genre distribution
plt.figure(figsize=(20,10))
sns.barplot(x=genre_counts.index[:10], y=genre_counts.values[:10])
plt.xticks(rotation=45)
plt.title("Top 10 Most Popular Genres")
plt.xlabel("Genre")
plt.ylabel("Count")
plt.savefig("data/processed/genre_distribution.png")
plt.show()