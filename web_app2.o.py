import streamlit as st
import pickle
import requests
import gzip
import numpy as np
import pandas as pd

# Function to fetch movie poster
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=2784c86bbf7f14344a8fb2f0afa10f08&language=en-US"
    response = requests.get(url)
    if response.status_code != 200:
        return ""
    data = response.json()
    poster_path = data.get('poster_path', '')
    full_path = f"https://image.tmdb.org/t/p/w500/{poster_path}" if poster_path else ""
    return full_path

# Function to fetch movie cast
def fetch_cast(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key=2784c86bbf7f14344a8fb2f0afa10f08&language=en-US"
    response = requests.get(url)
    if response.status_code != 200:
        return []
    data = response.json()
    cast = [member['name'] for member in data.get('cast', [])[:5]]  # Get top 5 cast members
    return cast

# Function to fetch movie trailer
def fetch_trailer(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key=2784c86bbf7f14344a8fb2f0afa10f08&language=en-US"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    data = response.json()
    videos = data.get('results', [])
    for video in videos:
        if video['type'] == 'Trailer' and video['site'] == 'YouTube':
            return f"https://www.youtube.com/watch?v={video['key']}"
    return None

# Load data
@st.cache_data  # Use caching to improve performance
def load_data():
    with open("movies_list.pkl", "rb") as f:
        new_data = pickle.load(f)
    with gzip.open('similarity.pkl.gz', 'rb') as f:
        similarity = pickle.load(f)
    return new_data, similarity

new_data, similarity = load_data()

# Ensure 'title' is a pandas Series
movie_series = new_data['title']

# OTT Style Header
st.markdown("<h1 style='text-align: center; color: black;'>🍿 Popcorn Picks: Your Ultimate Movie Companion 🎬</h1>", unsafe_allow_html=True)

# Search bar to filter movie list
search_query = st.text_input("Search for a movie", "")

if search_query:
    # Filter the movie titles based on the search query (case-insensitive)
    filtered_movie_series = movie_series[movie_series.str.contains(search_query, case=False, na=False)]
else:
    filtered_movie_series = movie_series

# Handle case when no movies match the search
if filtered_movie_series.empty and search_query:
    st.warning("No movies found matching your search.")
    selected_movie = None
else:
    # Create a selectbox with the filtered list
    selected_movie = st.selectbox("Select a Movie", filtered_movie_series) if not filtered_movie_series.empty else None

def recommend(movie):
    index = new_data[new_data['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movies = []
    recommended_posters = []
    recommended_casts = []
    recommended_trailers = []
    
    for i in distances[1:6]:  # Skip the first since it's the selected movie itself
        movie_id = new_data.iloc[i[0]].id
        recommended_movies.append(new_data.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))
        recommended_casts.append(fetch_cast(movie_id))
        recommended_trailers.append(fetch_trailer(movie_id))
        
    return recommended_movies, recommended_posters, recommended_casts, recommended_trailers

if selected_movie and st.button("🎥 Show Recommendations"):
    with st.spinner("Fetching recommendations..."):
        movie_names, movie_posters, movie_casts, movie_trailers = recommend(selected_movie)
    
    # Display recommendations using the full page layout
    st.markdown("## Recommendations")
    for movie_name, movie_poster, movie_cast, movie_trailer in zip(movie_names, movie_posters, movie_casts, movie_trailers):
        st.markdown(f"### **{movie_name}**")
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(movie_poster, use_column_width=True)
        with col2:
            st.write("**Cast:**")
            st.write(", ".join(movie_cast))
            if movie_trailer:
                st.markdown(f"[Watch Trailer]({movie_trailer})")
        st.markdown("---")

# Custom CSS for OTT Styling
st.markdown("""
    <style>
    body {
        background-color: #141414;
        color: white;
        font-family: 'Arial', sans-serif;
    }
    .stButton>button {
        background-color: #ff4b4b;
        color: white;
        border: none;
        padding: 10px;
        border-radius: 5px;
        font-size: 16px;
    }
    .stButton>button:hover {
        background-color: #ff1a1a;
        color: white;
    }
    .stTextInput>div>div>input {
        background-color: #333;
        color: white;
        padding: 10px;
        border-radius: 5px;
        border: none;
    }
    .stSelectbox>div>div>div>div>select {
        background-color: #333;
        color: white;
        padding: 10px;
        border-radius: 5px;
        border: none;
    }
    .stImage {
        border-radius: 10px;
        box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
        transition: 0.3s;
    }
    .stImage:hover {
        box-shadow: 0 8px 16px 0 rgba(0, 0, 0, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)
