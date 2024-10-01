import pytest
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client



# Test de la route GET /sensors sans token (doit échouer)
def test_get_sensors_no_token(client):
    response = client.get('/sensors')
    assert response.status_code == 401  # Non autorisé




# Test de la route POST /login (doit retourner un token)
def test_login(client):
    response = client.post('/login', json={
        "username": "admin",
        "password": "password123"
    })
    assert response.status_code == 200
    assert 'access_token' in response.get_json()




# Test de la route GET /sensors avec un token valide
def test_get_sensors_with_token(client):
    # Se connecter pour obtenir un token
    response = client.post('/login', json={
        "username": "admin",
        "password": "password123"
    })
    token = response.get_json()['access_token']

    # Accéder à /sensors avec le token
    response = client.get('/sensors', headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    assert isinstance(response.get_json()['sensors'], list)
