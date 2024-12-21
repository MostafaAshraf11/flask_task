from Models.dbModel import db

class Image(db.Model):
    __tablename__ = 'images'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    public_id = db.Column(db.String(255), nullable=False, unique=True)

    def __repr__(self):
        return f"<Image {self.filename}>"

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "url": self.url,
            "public_id": self.public_id
        }
