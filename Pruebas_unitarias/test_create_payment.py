import sys
import os
import pytest
from unittest.mock import patch

sys.path.append(os.path.join(os.path.dirname(__file__), '../payments'))
from create_payment import app  

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

## Usamos este decorados para bypassear la verificación de JWT
@patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
def test_create_payment(mock_verify_jwt, client):
    data =  {
        'idCredito': -1,
        'fecha': "2019-09-19",
        'cantidad': 16,
        'idMetodoPago': "Z147"
    }
    response = client.post(f'/api/pagos/{data["idCredito"]}', json=data)
    assert response.status_code == 404
