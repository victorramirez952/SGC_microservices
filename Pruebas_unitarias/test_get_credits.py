import sys
import os
import pytest
from unittest.mock import patch

sys.path.append(os.path.join(os.path.dirname(__file__), '../credits'))
from get_credits import app  

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

## Usamos este decorados para bypassear la verificación de JWT
@patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
def test_get_credits(mock_verify_jwt, client):
    response = client.get('/api/creditos')
    assert response.status_code == 200
    assert response.json['message'] == "Credito encontrado"
