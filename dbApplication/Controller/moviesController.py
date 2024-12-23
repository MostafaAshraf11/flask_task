import os
import uuid
import pandas as pd
from flask import current_app as app
from sqlalchemy import or_
from Models.movies_model import Movies 
from app import db

UPLOAD_FOLDER = 'uploads'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def upload_csv(file):
    """
    Uploads a CSV file, validates its format and columns, and inserts the data into the database.

    Input: file (uploaded CSV file)
    Expected Output: JSON response with a success or error message.
    """
    if file.filename == '':
        return {'error': 'No selected file'}, 400

    if not file.filename.endswith('.csv'):
        return {'error': 'Invalid file format, please upload a CSV file'}, 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        data = pd.read_csv(filepath)

        required_columns = ['title', 'director', 'release_year', 'runtime', 'genre', 'rating', 'gross']
        for col in required_columns:
            if col not in data.columns:
                return {'error': f'Missing required column: {col}'}, 400

        data = data.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        data.dropna(subset=required_columns, inplace=True)

        for _, row in data.iterrows():
            # Assuming 'movies_id' is a field in the database and auto-incremented, you don't need to set it manually
            new_movie = Movies(
                title=row['title'],
                director=row['director'],
                release_year=row['release_year'],
                runtime=row['runtime'],
                genre=row['genre'],
                rating=row['rating'],
                gross=row['gross']
            )
            db.session.add(new_movie)

        db.session.commit()
        return {'message': f'{len(data)} movies successfully added to the database'}, 201

    except Exception as e:
        return {'error': str(e)}, 500


def create_movie(data):
    """
    Creates a new movie record in the database.

    Input: data (dictionary with movie details)
    Expected Output: JSON response with success message and movie ID.
    """
    required_fields = ['title', 'director', 'release_year', 'runtime', 'genre', 'rating', 'gross']
    for field in required_fields:
        if field not in data:
            return {'error': f'Missing required field: {field}'}, 400

    new_movie = Movies(
        title=data['title'],
        director=data['director'],
        release_year=data['release_year'],
        runtime=data['runtime'],
        genre=data['genre'],
        rating=data['rating'],
        gross=data['gross']
    )

    db.session.add(new_movie)
    db.session.commit()

    return {'message': 'Movie created', 'id': new_movie.id}, 201

def get_all_movies(page, per_page=20):
    """
    Retrieves paginated movie records from the database.

    Input: page (integer), per_page (integer, default 20)
    Expected Output: JSON response with paginated movie data.
    """
    movies = Movies.query.paginate(page=page, per_page=per_page)
    movies_list = [movie.to_dict() for movie in movies.items]

    return {
        'page': movies.page,
        'per_page': movies.per_page,
        'total_pages': movies.pages,
        'total_items': movies.total,
        'data': movies_list
    }

def get_movie_by_id(movie_id):
    """
    Retrieves a specific movie record by its ID.

    Input: movie_id (integer)
    Expected Output: JSON response with movie details.
    """
    movie = Movies.query.get_or_404(movie_id)
    return movie.to_dict()

def update_movie(movie_id, data):
    """
    Updates an existing movie record with the provided data.

    Input: movie_id (integer), data (dictionary with movie details)
    Expected Output: JSON response with success message.
    """
    movie = Movies.query.get_or_404(movie_id)

    if 'title' in data:
        movie.title = data['title']
    if 'director' in data:
        movie.director = data['director']
    if 'release_year' in data:
        movie.release_year = data['release_year']
    if 'runtime' in data:
        movie.runtime = data['runtime']
    if 'genre' in data:
        movie.genre = data['genre']
    if 'rating' in data:
        movie.rating = data['rating']
    if 'gross' in data:
        movie.gross = data['gross']

    db.session.commit()
    return {'message': 'Movie updated'}


def delete_movie(movie_id):
    """
    Deletes a specific movie record from the database using its ID.

    Input: movie_id (integer)
    Expected Output: JSON response with success message.
    """
    movie = Movies.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return {'message': 'Movie deleted'}

def search_movies(search_query):
    """
    Searches for movies based on a query string, matching title or director.

    Input: search_query (string)
    Expected Output: List of dictionaries with matching movie details.
    """
    if not search_query:
        return []

    # Debugging line to check the received query
    print(f"Search query received: {search_query}")

    query = Movies.query.filter(
        or_(
            Movies.title.ilike(f'%{search_query}%'),
            Movies.director.ilike(f'%{search_query}%')
        )
    )

    movies = query.all()

    return [
        {
            'movie_id': movie.id,
            'title': movie.title,
            'director': movie.director,
            'release_year': movie.release_year,
            'runtime': movie.runtime,
            'genre': movie.genre,
            'rating': movie.rating,
            'gross': movie.gross
        }
        for movie in movies
    ]

def filter_movies(genre=None, release_year=None, min_gross=None, min_rating=None, page=1, per_page=20):
    """
    Filters movies based on genre, release year, minimum gross, and minimum rating.

    Input:
        genre (string, optional)
        release_year (integer, optional)
        min_gross (float, optional)
        min_rating (float, optional)
        page (integer, optional, default 1)
        per_page (integer, optional, default 20)
    Expected Output: JSON response with paginated and filtered movie data.
    """
    query = Movies.query

    if genre:
        query = query.filter(Movies.genre.ilike(f'%{genre}%'))
    if release_year:
        query = query.filter(Movies.release_year == release_year)
    if min_gross:
        query = query.filter(Movies.gross >= min_gross)
    if min_rating:
        query = query.filter(Movies.rating >= min_rating)

    movies = query.paginate(page=page, per_page=per_page)

    movie_list = [
        {
            'id': movie.id,
            'title': movie.title,
            'director': movie.director,
            'release_year': movie.release_year,
            'runtime': movie.runtime,
            'genre': movie.genre,
            'rating': movie.rating,
            'gross': movie.gross
        }
        for movie in movies.items
    ]

    return {
        'page': movies.page,
        'per_page': movies.per_page,
        'total_pages': movies.pages,
        'total_items': movies.total,
        'data': movie_list
    }
