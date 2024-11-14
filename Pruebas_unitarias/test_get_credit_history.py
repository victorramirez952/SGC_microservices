import sys
import os
import pytest
from unittest.mock import patch

sys.path.append(os.path.join(os.path.dirname(__file__), '../credit_histories/'))
from get_credit_history import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

## Usamos este decorados para bypassear la verificación de JWT
@patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
def test_get_credit_history(mock_verify_jwt, client):
    idCliente = 74
    response = client.get(f'/api/historial-credito/{idCliente}')
    assert response.status_code == 200
    assert response.json['message'] == "Historial de creditos encontrado"
