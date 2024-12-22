from Models.dbModel import db

class Movies(db.Model):
    __tablename__ = 'movies'

    id = db.Column(db.Integer, primary_key=True)  # Primary key
    title = db.Column(db.String(255), nullable=False)
    director = db.Column(db.String(255), nullable=False)
    release_year = db.Column(db.Integer, nullable=False)
    runtime = db.Column(db.Integer, nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    gross = db.Column(db.Float, nullable=False)  # Changed column name

    def __repr__(self):
        return f"<Movies id={self.id} title={self.title}>"

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "director": self.director,
            "release_year": self.release_year,
            "runtime": self.runtime,
            "genre": self.genre,
            "rating": self.rating,
            "gross": self.gross
        }
