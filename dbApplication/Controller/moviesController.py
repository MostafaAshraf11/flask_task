import os
import pandas as pd
from flask import current_app as app
from sqlalchemy import or_
from Models.movies_model import Movies  # Assuming Movies is defined in a models module
from app import db  # Assuming db is imported from your app

UPLOAD_FOLDER = 'uploads'

# Create uploads folder if not exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def upload_csv(file):
    if file.filename == '':
        return {'error': 'No selected file'}, 400

    if not file.filename.endswith('.csv'):
        return {'error': 'Invalid file format, please upload a CSV file'}, 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        # Read the CSV file
        data = pd.read_csv(filepath)

        # Validate required columns
        required_columns = ['id', 'title', 'director', 'release_year', 'runtime', 'genre', 'rating', 'gross']
        for col in required_columns:
            if col not in data.columns:
                return {'error': f'Missing required column: {col}'}, 400

        # Clean the data:
        # Strip spaces from column values (for text columns)
        data = data.applymap(lambda x: x.strip() if isinstance(x, str) else x)

        # Drop rows where any required column is empty
        data.dropna(subset=required_columns, inplace=True)

        # Insert rows into the database
        for _, row in data.iterrows():
            new_movie = Movies(
                id=row['id'],
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
    required_fields = ['title', 'director', 'release_year', 'runtime', 'genre', 'rating', 'gross']
    for field in required_fields:
        if field not in data:
            return {'error': f'Missing required field: {field}'}, 400

    # Create a new Movies object
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
    movie = Movies.query.get_or_404(movie_id)
    return movie.to_dict()


def update_movie(movie_id, data):
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
    movie = Movies.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return {'message': 'Movie deleted'}

def search_movies(search_query):
        # If no search query is provided, return an empty list
        if not search_query:
            return []
        
        print(f"Search query received: {search_query}")  # Debugging line
        # Start the query
        query = Movies.query

        # Apply filtering based on title or director if provided
        query = query.filter(
            or_(
                Movies.title.ilike(f'%{search_query}%'),
                Movies.director.ilike(f'%{search_query}%')
            )
        )

        # Execute the query
        movies = query.all()

        # Prepare the results as a list of dictionaries
        movie_list = [{
            'movie_id': movie.id,
            'title': movie.title,
            'director': movie.director,
            'release_year': movie.release_year,
            'runtime': movie.runtime,
            'genre': movie.genre,
            'rating': movie.rating,
            'gross': movie.gross
        } for movie in movies]

        return movie_list

def filter_movies(genre=None, release_year=None, min_gross=None, min_rating=None, page=1, per_page=20):
    # Start the query
    query = Movies.query

    # Apply filters based on the provided criteria
    if genre:
        query = query.filter(Movies.genre.ilike(f'%{genre}%'))
    if release_year:
        query = query.filter(Movies.release_year == release_year)
    if min_gross:
        query = query.filter(Movies.gross >= min_gross)
    if min_rating:
        query = query.filter(Movies.rating >= min_rating)

    # Paginate the query
    movies = query.paginate(page=page, per_page=per_page)

    # Prepare the results as a list of dictionaries
    movie_list = [{
        'id': movie.id,
        'title': movie.title,
        'director': movie.director,
        'release_year': movie.release_year,
        'runtime': movie.runtime,
        'genre': movie.genre,
        'rating': movie.rating,
        'gross': movie.gross
    } for movie in movies.items]

    return {
        'page': movies.page,
        'per_page': movies.per_page,
        'total_pages': movies.pages,
        'total_items': movies.total,
        'data': movie_list
    }
