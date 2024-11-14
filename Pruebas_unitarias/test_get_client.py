import sys
import os
import pytest
from unittest.mock import patch

sys.path.append(os.path.join(os.path.dirname(__file__), '../clients'))
from get_client import app  

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

## Usamos este decorados para bypassear la verificación de JWT
@patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
def test_get_client(mock_verify_jwt, client):
    client_id = 155
    
    response = client.get('/api/clientes/' + str(client_id))
    assert response.status_code == 200
    assert response.json['message'] == "Cliente encontrado"
