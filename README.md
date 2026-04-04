# Movie Search Engine with Inverted Index

A lightweight Python-based search engine that allows users to search through a database of ~5,000 movies using an **Inverted Index**. By utilizing natural language processing, the engine strips out noise and retrieves movies based on matching keywords in their titles.

---

## 🚀 Features

* **Kaggle Dataset Integration:** Automatically downloads and extracts the TMDB 5,000 Movie Dataset using `kagglehub`.
* **NLP Preprocessing:** Leverages `spaCy` to remove stop words and punctuation for accurate term indexing.
* **Inverted Indexing:** Builds a highly efficient mapping of unique title words to their corresponding dataset row indices.
* **Interactive Querying:** Allows real-time user inputs to fetch top matching movie results complete with summaries, ratings, and runtimes.

---

## 🛠️ Tech Stack

* **Python 3**
* **spaCy** (Natural Language Processing)
* **Pandas** (Data Manipulation)
* **Kagglehub** (Dataset downloading)

---

## 📂 Dataset

The project uses the [TMDB 5000 Movie Dataset](https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata), which contains detailed metadata about roughly 5,000 movies, including budgets, overviews, titles, and audience ratings.

---

## ⚙️ How it Works

To make searches efficient, the search engine does not scan the whole dataset every time you look for a movie. Instead, it relies on two main components:

### 1. Building the Inverted Index
The notebook iterates through the dataset titles, processes them with `spaCy` to remove "unimportant" words (like *the*, *and*, *of*), and catalogs where each word appears.

*Example mapping:*
* `"pirates"` $\rightarrow$ `[1, 12, 17, 199]`
* `"caribbean"` $\rightarrow$ `[1, 12, 199]`

### 2. Executing a Query
When a user searches for a term like `"Pirates of the Caribbean"`, the engine:
1. Normalizes the text to lowercase and removes filler words.
2. Looks up the words `"pirates"` and `"caribbean"` in the inverted index.
3. Gathers the unique row indices and pulls the movie data directly from Pandas.

---

## 💻 Getting Started

### Prerequisites
Make sure you have the required libraries installed before running the notebook. You can install them via pip:

```bash
pip install pandas spacy kagglehub
python -m spacy download en_core_web_sm
```
