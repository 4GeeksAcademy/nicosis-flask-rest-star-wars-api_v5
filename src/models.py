from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    favorites = db.relationship('Favorite', backref='users')

    def __repr__(self):
        return f'<User {self.email}, id:{self.id}>'

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }


class Galaxy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.String(240))
    coordinate_center_x = db.Column(db.Float, nullable=False)
    coordinate_center_y = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Galaxy {self.id}>'

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
        }

class Planet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.String(240))

    # OBLIGATORIO para establecer la relación
    galaxy_id = db.Column(db.Integer, db.ForeignKey(
        'galaxy.id'), nullable=False)
    galaxy = db.relationship('Galaxy')

    def __repr__(self):
        return f'<Planet {self.name}, id:{self.id}>'

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "galaxy_name": self.galaxy.name
        }


class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    gender = db.Column(db.String(240))

    def __repr__(self):
        return f'<Character id:{self.id}, {self.name}>'

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
        }


class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    planet_id = db.Column(
        db.Integer, db.ForeignKey('planet.id'), nullable=True)
    character_id = db.Column(
        db.Integer, db.ForeignKey('character.id'), nullable=True)
    planet = db.relationship('Planet', foreign_keys=[planet_id])
    character = db.relationship('Character', foreign_keys=[character_id])

    def __repr__(self):
        return f'<Favorite {self.id}>'

    def serialize(self):
        return {
            'id_favorite': self.id,
            'user_id': self.user_id,
            'user_email': self.users.email,
            'planet': self.planet.serialize() if self.planet else None,
            'character': self.character.serialize() if self.character else None,
        }
