from flask import Flask, request, jsonify
import requests
import pickle
import gzip
import numpy as np

app = Flask(__name__)

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=2784c86bbf7f14344a8fb2f0afa10f08&language=en-US"
    data = requests.get(url, timeout=5).json()
    poster_path = data.get('poster_path')
    if poster_path:
        full_path = f"https://image.tmdb.org/t/p/w500/{poster_path}"
        return full_path
    return None

new_data = pickle.load(open("movies_list.pkl", "rb"))

with gzip.open('similarity.pkl.gz', 'rb') as f:
    similarity = pickle.load(f)

movie_list = new_data['title'].values
movie_list = [title.lower() for title in movie_list]

print(movie_list[0:5])

def getSuggestion(movie):
    suggestions = new_data[new_data['title'].str.startswith(movie, case = False)]
    suggestions = suggestions['title'].head(5)
    return suggestions.values.tolist()

def recommend(movie):
    movie = movie.lower()
    movie = movie.strip()
    print(movie)
    if movie not in movie_list:
        return [], [], [], []  # Handle case where the movie is not found

    index = new_data[new_data['title'].str.lower() == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda vector: vector[1])
    
    recommended_movies = []
    recommended_posters = []
    recommended_overview = []
    recommended_genre = []

    for i in distances[1:16]:  # Skip the first one because it is the movie itself
        movie_title = new_data.iloc[i[0]].title
        overview = new_data.iloc[i[0]].overview
        genre = new_data.iloc[i[0]].genre
        movie_id = new_data.iloc[i[0]].id
        recommended_movies.append(movie_title)
        recommended_posters.append(fetch_poster(movie_id))
        recommended_overview.append(overview)
        recommended_genre.append(genre)

    return recommended_movies, recommended_posters, recommended_overview, recommended_genre
  
@app.route('/fetch-movies', methods=["GET"])
def fetch_movies():
    name = request.args.get('name')
    
    if not name:
        return jsonify({"error": "No movie name provided", "status": 400}), 400

    recommended_movies, recommended_posters, recommended_overview, recommended_genre = recommend(name)

    if not recommended_movies:
        return jsonify({"error": "Movie not found" , "status":404}), 404

    return jsonify({
        "status" : 200,
        "recommended_movies": recommended_movies,
        "recommended_posters": recommended_posters,
        "recommended_overview": recommended_overview,
        "recommended_genre": recommended_genre
    })

@app.route('/fetch-suggestions', methods=["GET"])
def fetch_suggestions():
    name = request.args.get('name')
    suggestions = getSuggestion(name)
    return jsonify({
        "status" : 200,
        "recommended_movies": suggestions,
    })

if __name__ == '__main__':
    app.run(debug=True)

   
