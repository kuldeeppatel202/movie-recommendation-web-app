import streamlit as st
import pickle
import requests

def fetch_poster(id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=2784c86bbf7f14344a8fb2f0afa10f08&language=en-US".format(id)
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/"+poster_path
    return full_path

new_data = pickle.load(open("movies_list.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

movie_list = new_data['title'].values

st.header("🍿 Popcorn Picks: Your Ultimate Movie Companion 🎬")
selectedValue = st.selectbox("Select Movie" , movie_list)

def recommend(movie):
    index = new_data[new_data['title'] == movie].index[0]
    distance = sorted(list(enumerate(similarity[index])), reverse = True, key = lambda vector:vector[1])
    recommended_movies = []
    recommended_posters = []
    for i in distance[0:5]:
        print(new_data.iloc[i[0]].title)
        movies_id = new_data.iloc[i[0]].id
        recommended_movies.append(new_data.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movies_id))

    return recommended_movies, recommended_posters


if st.button("Show Recommend"):
    movie_names, movie_posters = recommend(selectedValue)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.text(movie_names[0])
        st.image(movie_posters[0])
    with col2:
        st.text(movie_names[1])
        st.image(movie_posters[1])
    with col3:
        st.text(movie_names[2])
        st.image(movie_posters[2])
    with col4:
        st.text(movie_names[3])
        st.image(movie_posters[3])
    with col5:
        st.text(movie_names[4])
        st.image(movie_posters[4])