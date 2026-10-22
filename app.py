
import os
import pickle
import requests
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from huggingface_hub import hf_hub_download


load_dotenv()

def get_secret(name):
    try:
        value = st.secrets.get(name)
        if value:
            return str(value)
    except Exception:
        pass

    return os.getenv(name)

TMDB_API_KEY = get_secret("TMDB_API_KEY")
HF_TOKEN = get_secret("HF_TOKEN")

TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"


st.set_page_config(
    page_title="CineMatch",
    page_icon="🎬",
    layout="wide",
)

# -----------------------------
# Load recommendation data
# -----------------------------

@st.cache_resource
def load_data():
    with open("movie_dict.pkl", "rb") as file:
        movie_dict = pickle.load(file)

    # Use the local file if available; otherwise download from Hugging Face.
    if os.path.exists("similarity.pkl"):
        similarity_path = "similarity.pkl"
    else:
        if not HF_TOKEN:
            raise ValueError(
                "HF_TOKEN is missing. Add it to Streamlit Cloud Secrets."
            )

        similarity_path = hf_hub_download(
            repo_id="23Anubhav/cinematch-models",
            filename="similarity.pkl",
            repo_type="dataset",
            token=HF_TOKEN,
        )

    with open(similarity_path, "rb") as file:
        similarity = pickle.load(file)

    movies = pd.DataFrame(movie_dict).reset_index(drop=True)
    movies_details = pd.read_pickle("movies.pkl")

    if len(movies) != similarity.shape[0]:
        raise ValueError(
            "Movie data and similarity matrix have different sizes."
        )

    if similarity.shape[0] != similarity.shape[1]:
        raise ValueError("The similarity matrix must be square.")

    return movies, movies_details, similarity



try:
    movies, movies_details, similarity = load_data()
except Exception as error:
    st.error(f"Could not load recommendation data: {error}")
    st.stop()


# -----------------------------
# Safe metadata helpers
# -----------------------------

def clean_text(value):
    if value is None:
        return ""

    if isinstance(value, (list, tuple, set)):
        parts = []
        for item in value:
            if isinstance(item, dict):
                name = item.get("name", "")
                if name:
                    parts.append(str(name))
            else:
                parts.append(str(item))
        return ", ".join(parts)

    if isinstance(value, dict):
        return str(value.get("name", ""))

    if pd.isna(value):
        return ""

    return str(value)


def get_local_details(title):
    matches = movies_details[
        movies_details["title"].astype(str).str.strip().str.casefold()
        == str(title).strip().casefold()
    ]

    if matches.empty:
        return {}

    return matches.iloc[0].to_dict()


# -----------------------------
# TMDB lookup
# -----------------------------

@st.cache_data(ttl=86400, show_spinner=False)
def get_tmdb_movie(title):
    """Find a movie on TMDB and cache the result for one day."""

    if not TMDB_API_KEY:
        return {}

    try:
        response = requests.get(
            f"{TMDB_BASE_URL}/search/movie",
            params={
                "api_key": TMDB_API_KEY,
                "query": title,
                "include_adult": "false",
            },
            timeout=15,
        )
        response.raise_for_status()

        results = response.json().get("results", [])

        if not results:
            return {}

        # TMDB's first search result is usually the closest title match.
        return results[0]

    except (requests.RequestException, ValueError):
        return {}


def get_movie_metadata(title):
    local = get_local_details(title)
    tmdb = get_tmdb_movie(title)

    # Prefer TMDB information when available.
    overview = tmdb.get("overview") or clean_text(
        local.get("overview", "")
    )

    genres = tmdb.get("genre_ids", [])
    genre_names = []

    # Convert TMDB genre IDs into readable names.
    genre_map = {
        28: "Action",
        12: "Adventure",
        16: "Animation",
        35: "Comedy",
        80: "Crime",
        99: "Documentary",
        18: "Drama",
        10751: "Family",
        14: "Fantasy",
        36: "History",
        27: "Horror",
        10402: "Music",
        9648: "Mystery",
        10749: "Romance",
        878: "Science Fiction",
        10770: "TV Movie",
        53: "Thriller",
        10752: "War",
        37: "Western",
    }

    for genre_id in genres:
        if genre_id in genre_map:
            genre_names.append(genre_map[genre_id])

    if not genre_names:
        genre_names = [
            part.strip()
            for part in clean_text(local.get("genres", "")).split(",")
            if part.strip()
        ]

    release_date = tmdb.get("release_date", "")
    rating = tmdb.get("vote_average")
    poster_path = tmdb.get("poster_path")

    return {
        "overview": overview,
        "genres": ", ".join(genre_names) or "Not available",
        "release_date": release_date,
        "rating": rating,
        "poster_url": (
            f"{TMDB_IMAGE_URL}{poster_path}"
            if poster_path
            else None
        ),
    }


# -----------------------------
# Recommendation engine
# -----------------------------

def recommend(title, number=5):
    matches = movies.index[
        movies["title"].astype(str) == str(title)
    ].tolist()

    if not matches:
        return []

    movie_index = matches[0]
    distances = similarity[movie_index]

    ranked = sorted(
        enumerate(distances),
        key=lambda item: item[1],
        reverse=True,
    )

    recommendations = []

    for index, score in ranked:
        if index == movie_index:
            continue

        recommendations.append({
            "title": str(movies.iloc[index]["title"]),
            "score": float(score),
        })

        if len(recommendations) >= number:
            break

    return recommendations


# -----------------------------
# CineMatch interface
# -----------------------------

st.title("🎬 CineMatch")
st.caption("Find your next favorite movie using content-based recommendations.")

st.markdown(
    """
    Choose a movie you enjoy, and CineMatch will recommend films
    with similar content, along with posters and movie information.
    """
)

movie_titles = sorted(
    movies["title"].dropna().astype(str).unique().tolist()
)

if not movie_titles:
    st.error("No movie titles were found in movie_dict.pkl.")
    st.stop()

selected_movie = st.selectbox(
    "🔎 Choose a movie",
    movie_titles,
)

if st.button("🎯 Recommend Movies", type="primary"):
    recommendations = recommend(selected_movie)

    if not recommendations:
        st.warning("No recommendations were found for this movie.")
    else:
        st.subheader(f"Movies similar to {selected_movie}")

        with st.spinner("Fetching movie information..."):
            selected_details = get_movie_metadata(selected_movie)

        if selected_details.get("poster_url"):
            st.image(
                selected_details["poster_url"],
                width=140,
            )

        if selected_details.get("overview"):
            st.write(selected_details["overview"])

        st.divider()
        columns = st.columns(len(recommendations))

        for column, movie in zip(columns, recommendations):
            with column:
                st.markdown(f"**{movie['title']}**")

                details = get_movie_metadata(movie["title"])

                if details.get("poster_url"):
                    st.image(
                        details["poster_url"],
                        use_container_width=True,
                    )
                else:
                    st.info("Poster unavailable")

                st.caption(
                    f"Similarity: {movie['score']:.1%}"
                )

                rating = details.get("rating")
                if rating is not None:
                    st.write(f"⭐ TMDB: {rating:.1f}/10")

                release_date = details.get("release_date", "")
                if release_date:
                    st.write(f"📅 {release_date[:4]}")

                st.write(f"🎭 {details['genres']}")

                overview = details.get("overview", "")
                if overview:
                    st.write(
                        overview[:220] + (
                            "..." if len(overview) > 220 else ""
                        )
                    )
                else:
                    st.caption("Overview unavailable")

st.divider()
st.caption(
    "This product uses the TMDB API but is not endorsed or certified by TMDB."
)
