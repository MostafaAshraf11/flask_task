from flask import Blueprint, request, jsonify

from Controller.moviesController import (filter_movies, search_movies, upload_csv,create_movie, delete_movie, get_all_movies, get_movie_by_id, update_movie)

movies_bp = Blueprint('movies', __name__)

@movies_bp.route('/upload_csv', methods=['POST'])
def upload_csv_route():
    file = request.files.get('file')
    return upload_csv(file)

@movies_bp.route('/add', methods=['POST'])
def create_movie_route():
    data = request.json
    return create_movie(data)

@movies_bp.route('/', methods=['GET'])
def get_all_movies_route():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    return jsonify(get_all_movies(page, per_page))

@movies_bp.route('/<int:movie_id>', methods=['GET'])
def get_movie_route(movie_id):
    return jsonify(get_movie_by_id(movie_id))

@movies_bp.route('/update/<int:movie_id>', methods=['PUT'])
def update_movie_route(movie_id):
    data = request.json
    return update_movie(movie_id, data)

@movies_bp.route('/delete/<int:movie_id>', methods=['DELETE'])
def delete_movie_route(movie_id):
    return delete_movie(movie_id)

@movies_bp.route('/search', methods=['GET'])
def search_moviesroute():
    # Get search query from the URL parameter
    search_query = request.args.get('query', default=None, type=str)


    # Call the MovieController to perform the search
    movie_list = search_movies(search_query)

    # Return the results as JSON
    return jsonify(movie_list)

@movies_bp.route('/filter', methods=['GET'])
def filter_moviesroute():
    # Get filter parameters from the URL query string
    genre = request.args.get('genre', default=None, type=str)
    release_year = request.args.get('release_year', default=None, type=int)
    min_gross = request.args.get('min_gross', default=None, type=float)
    min_rating = request.args.get('min_rating', default=None, type=float)
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=20, type=int)

    # Call the controller function to perform the filtering
    filtered_movies = filter_movies(genre, release_year, min_gross, min_rating, page, per_page)

    # Return the results as JSON
    return jsonify(filtered_movies)