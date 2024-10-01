from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)


# Clé secrète pour signer les tokens JWT jsonwebtoken

app.config['JWT_SECRET_KEY'] = 'secret-key'  # Change cette clé dans un vrai projet
jwt = JWTManager(app)


# Configuration Swagger

SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'  # Lien vers ton fichier swagger.json (à créer) Chemin RELATIF non ABSOLU

swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={
    'app_name': "API de Capteurs"
})

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


#----------------------------------------- Exemple de routes et CRUD ici -------------------------------------------------


# Liste de capteurs fictifs
sensors = [
    {"id": 1, "name": "Temperature Salon", "value": 23},
    {"id": 2, "name": "Humidity Chambre", "value": 45},
    {"id": 3, "name": "Pression Exterieur", "value": 1012},
    {"id": 4, "name": "Lumiere Salon", "value": 250},
    # Ajoute d'autres capteurs si nécessaire
]


# Utilisateur fictif pour la démonstration
users = {
    "admin": "password123"
}



# Route pour obtenir un token JWT
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    # Vérification des identifiants de l'utilisateur
    if username not in users or users[username] != password:
        return jsonify({"error": "Nom d'utilisateur ou mot de passe incorrect"}), 401

    # Création du token JWT
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)




# Route pour récupérer tous les capteurs avec pagination et filtre par nom (nécessite un token)
@app.route('/sensors', methods=['GET'])
@jwt_required()
def get_sensors():
    # Paramètres de pagination
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 2))
    start = (page - 1) * limit
    end = start + limit

    # Filtrer par nom (optionnel)
    filter_name = request.args.get('name', None)
    filtered_sensors = [sensor for sensor in sensors if filter_name.lower() in sensor['name'].lower()] if filter_name else sensors

    # Pagination
    paginated_sensors = filtered_sensors[start:end]

    return jsonify({
        "page": page,
        "limit": limit,
        "total_sensors": len(filtered_sensors),
        "sensors": paginated_sensors
    })




# Route protégée - ajoute un capteur (nécessite un token)
@app.route('/sensors', methods=['POST'])
@jwt_required()
def add_sensor():
    new_sensor = request.get_json()
    
    # Validation des données
    if not new_sensor.get("name") or not isinstance(new_sensor.get("value"), (int, float)):
        return jsonify({"error": "Données invalides, le champ 'name' et 'value' sont requis"}), 400

    new_sensor["id"] = len(sensors) + 1
    sensors.append(new_sensor)
    return jsonify(new_sensor), 201




# Route protégée - mise à jour d'un capteur (nécessite un token)
@app.route('/sensors/<int:sensor_id>', methods=['PUT'])
@jwt_required()
def update_sensor(sensor_id):
    updated_data = request.get_json()
    for sensor in sensors:
        if sensor['id'] == sensor_id:
            sensor['name'] = updated_data.get('name', sensor['name'])
            sensor['value'] = updated_data.get('value', sensor['value'])
            return jsonify(sensor)
    return jsonify({"error": "Capteur non trouvé"}), 404





# Route protégée - suppression d'un capteur (nécessite un token)
@app.route('/sensors/<int:sensor_id>', methods=['DELETE'])
@jwt_required()
def delete_sensor(sensor_id):
    for sensor in sensors:
        if sensor['id'] == sensor_id:
            sensors.remove(sensor)
            for i, sensor in enumerate(sensors):
                sensor['id'] = i + 1
            return jsonify({"message": "Capteur supprimé"}), 200
    return jsonify({"error": "Capteur non trouvé"}), 404





if __name__ == '__main__':
    app.run(debug=True)
