import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, Character, Favorite


app = Flask(__name__)
app.url_map.strict_slashes = False


db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)


# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


# POST DE FAVORITE DE PLANET_ID
current_logged_user_id = 1


# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


# [GET] /users Listar todos los usuarios del blog
@app.route('/user', methods=['GET'])
def get_users():
    users = User.query.all()
    all_users = list(map(lambda x: x.serialize(), users))
    return jsonify(all_users), 200

# post user
@app.route('/user', methods=['POST'])
def add_users():

    request_body_user = request.get_json()
    new_user = User(
        email=request_body_user['email'], password=request_body_user['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify('user added:', request_body_user), 200

# edith user
@app.route('/user/<int:user_id>', methods=['PUT'])
def update_users(user_id):

    request_body_user = request.get_json()
    user1 = User.query.get(user_id)
    if user1 is None:
        raise APIException('watafak! no encontrado...', status_code=404)
    if 'email' in request_body_user:
        user1.email = request_body_user['email']
    db.session.commit()
    return jsonify('funky user editado:', request_body_user), 200

# delete user
@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_users(user_id):

    user1 = User.query.get(user_id)
    if user1 is None:
        raise APIException('watafak! no encontrado...', status_code=404)
    db.session.delete(user1)
    db.session.commit()
    return jsonify('funky user borrado'), 200


# GET PLANET-GALAXY
@app.route('/planet-galaxy', methods=['GET'])
def get_relation_planet_galaxy():
    planets = Planet.query.all()
    response = []
    for planet in planets:
        response.append({
            'planet': planet.name,
            'planet_description': planet.description,
            'galaxy': planet.galaxy.name,
            'galaxy_coordinate_x': planet.galaxy.coordinate_center_x
        })
    return jsonify(response)


# [GET] /planets Listar los registros de planets en la base de datos
@app.route('/planet', methods=['GET'])
def get_planets():

    planets = Planet.query.all()
    all_planets = list(map(lambda x: x.serialize(), planets))
    return jsonify(all_planets), 200

# [GET] /planets/<int:planet_id> Listar la información de un solo planet
@app.route('/planet/<int:planets_id>', methods=['GET'])
def get_single_planet(planets_id):

    single_planet = Planet.query.get(planets_id)
    if single_planet is None:
        raise APIException('watafank! ese planeta no existe...', status_code=404)
    return jsonify(single_planet.serialize()), 200

# agregar planeta
@app.route('/planet', methods=['POST'])
def add_planet():

    request_body_planet = request.get_json()  
    new_planet = Planet(name=request_body_planet['name'], description=request_body_planet['description'], population=request_body_planet['population'])
    db.session.add(new_planet)
    db.session.commit()
    return jsonify('planeta added:',new_planet.serialize()), 200


# [GET] /people Listar todos los registros de people en la base de datos
@app.route('/character', methods=['GET'])
def get_people():

    character = Character.query.all()
    all_character = list(map(lambda x: x.serialize(), character))
    return jsonify(all_character), 200

# [GET] /people/<int:people_id> Listar la información de una sola people
@app.route('/character/<int:character_id>', methods=['GET'])
def get_single_character(character_id):

    single_character = Character.query.get(character_id)
    if single_character is None:
        raise APIException('watafank! esa persona no existe...', status_code=404)
    return jsonify(single_character.serialize()), 200

# agrregar character
@app.route('/character', methods=['POST'])
def add_people():

    request_body_character = request.get_json()  
    new_character = Character(name=request_body_character['name'], gender=request_body_character['gender'])
    db.session.add(new_character)
    db.session.commit()
    return jsonify('character added:',new_character.serialize()), 200


# [GET] /users/favorites Listar todos los favoritos que pertenecen al usuario actual.
@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user = User.query.get(current_logged_user_id)
    favorites = user.favorites
    serialized_favorites = [f.serialize() for f in favorites]
    response_body = {
        "msg": f"Aqui tienes los favoritos del user: {user.email}",
        "favorites": serialized_favorites
    }
    return jsonify(response_body), 200

# get single fav/planet of current user
@app.route('/users/favorite/<int:favorite_id>', methods=['GET'])
def get_user_favorites_id(favorite_id):
    user_id = current_logged_user_id

    single_planet = Favorite.query.filter_by(user_id=user_id, id=favorite_id).first()
    if single_planet is None:
        raise APIException('watafank! ese favorito no existe...', status_code=404)
    return jsonify(single_planet.serialize()), 200


# [POST] /favorite/planet/<int:planet_id> Añade un nuevo planet favorito al usuario actual con el planet id = planet_id.
@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):

    user_id = current_logged_user_id

    # Verificamos si el planet_id existe en la base de datos
    planet = Planet.query.get(planet_id)
    if not planet:
        response_body = {
            "msg": "funky planet no existe"
        }
        return jsonify(response_body), 404


    # Verificamos si ya existe un favorito con el mismo user_id y planet_id
    existing_favorite = Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if existing_favorite:
        response_body = {
            "msg": "ese funky favorito ya existe loco"
        }
        return jsonify(response_body), 400

    # Si no existe, creamos un nuevo favorito
    new_favorite = Favorite(user_id=user_id, planet_id=planet_id)
    db.session.add(new_favorite)
    db.session.commit()

    response_body = {
        "msg": "funky favorito agregado", 
        "favorite": new_favorite.serialize()
    }

    return jsonify(response_body), 200

# [DELETE] /favorite/planet/<int:planet_id> Elimina un planet favorito con el id = planet_id`.
@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):

    user_id = current_logged_user_id

    favorite = Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()

    if favorite is None:
        return jsonify({'msg' : 'funky favorito no encontrado'}), 404

    db.session.delete(favorite)
    db.session.commit()

    response_body = {'msg' : 'funky favorito con ese planeta eliminado'}
    return jsonify(response_body), 200


# [POST] /favorite/people/<int:people_id> Añade una nueva people favorita al usuario actual con el people.id = people_id.
@app.route('/favorite/character/<int:character_id>', methods=['POST'])
def add_favorite_character(character_id):

    user_id = current_logged_user_id

    # Verificamos si el planet_id existe en la base de datos
    character = Character.query.get(character_id)
    if not character:
        response_body = {
            "msg": "funky character no existe"
        }
        return jsonify(response_body), 404


    # Verificamos si ya existe un favorito con el mismo user_id y character_id
    existing_favorite = Favorite.query.filter_by(user_id=user_id, character_id=character_id).first()
    if existing_favorite:
        response_body = {
            "msg": "ese funky favorito ya existe loco"
        }
        return jsonify(response_body), 400

    # Si no existe, creamos un nuevo favorito
    new_favorite = Favorite(user_id=user_id, character_id=character_id)
    db.session.add(new_favorite)
    db.session.commit()

    response_body = {
        "msg": "funky favorito agregado", 
        "favorite": new_favorite.serialize()
    }

    return jsonify(response_body), 200

# [DELETE] /favorite/people/<int:people_id> Elimina una people favorita con el id = people_id.
@app.route('/favorite/character/<int:character_id>', methods=['DELETE'])
def delete_favorite_character(character_id):

    user_id = current_logged_user_id

    favorite = Favorite.query.filter_by(user_id=user_id, character_id=character_id).first()

    if favorite is None:
        return jsonify({'msg' : 'funky favorito no encontrado'}), 404

    db.session.delete(favorite)
    db.session.commit()

    response_body = {'msg' : 'funky favorito con ese character eliminado'}
    return jsonify(response_body), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
