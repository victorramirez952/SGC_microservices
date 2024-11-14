import sys
import os
import pytest
from unittest.mock import patch

sys.path.append(os.path.join(os.path.dirname(__file__), '../clients'))
from delete_client import app  

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

## Usamos este decorados para bypassear la verificación de JWT
@patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
def test_delete_client(mock_verify_jwt, client):
    idCliente = -1
    response = client.delete(f'/api/clientes/{idCliente}')
    assert response.status_code == 404
