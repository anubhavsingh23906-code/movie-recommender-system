# 🎬 CineMatch — Movie Recommendation System

CineMatch is a content-based movie recommendation system that suggests similar movies based on a user's selected title. It combines a precomputed similarity matrix with TMDB metadata to display movie posters, ratings, genres, and descriptions.

## 🚀 Live Demo

**[Try CineMatch](https://movie-recommender-system-ymvgtesq54z735ctbsqhn8.streamlit.app/)**

## ✨ Features

- 🎯 Content-based movie recommendations
- 🔍 Search and select from a movie collection
- 🖼️ Movie posters using TMDB
- ⭐ Ratings, genres, release dates, and descriptions
- ⚡ Cached model loading and metadata requests
- ☁️ Deployed using Streamlit Community Cloud
- 🤗 Large similarity matrix hosted on Hugging Face

## 🛠️ Tech Stack

- **Language:** Python
- **Data Processing:** Pandas, NumPy
- **Machine Learning:** Content-based filtering and similarity scoring
- **Application:** Streamlit
- **Movie Metadata:** TMDB API
- **Model Hosting:** Hugging Face Hub
- **Deployment:** Streamlit Community Cloud

## ⚙️ How It Works

1. The user selects a movie.
2. CineMatch retrieves the selected movie's similarity scores.
3. Movies are ranked by similarity.
4. The system returns the highest-ranked similar movies.
5. TMDB supplies available posters and movie metadata.

## 🧠 Key Learning Outcomes

- Building a recommendation pipeline with precomputed similarity scores
- Working with serialized Python data and large model artifacts
- Integrating a third-party REST API
- Caching resources and API responses in Streamlit
- Managing secrets and deploying an ML application to the cloud

## 💻 Run Locally

Clone the repository:

```bash
git clone https://github.com/anubhavsingh23906-code/movie-recommendation-system.git
cd movie-recommendation-system
```

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a `.env` file with the required credentials:

```text
HF_TOKEN=your_hugging_face_token
TMDB_API_KEY=your_tmdb_api_key
```

Ensure `movie_dict.pkl` and `movies.pkl` are available in the project directory. If `similarity.pkl` is not present locally, the app downloads it from the configured Hugging Face dataset.

Run the application:

```bash
streamlit run app.py
```

## 🔐 Security

- API credentials are stored in environment variables or Streamlit Secrets.
- Secret files and large model artifacts should not be committed to GitHub.

## ⚠️ Disclaimer

This product uses the TMDB API but is not endorsed or certified by TMDB.
