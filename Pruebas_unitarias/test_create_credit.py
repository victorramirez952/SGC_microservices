import sys
import os
import pytest
from unittest.mock import patch

sys.path.append(os.path.join(os.path.dirname(__file__), '../credits'))
from create_credit import app  

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

## Usamos este decorados para bypassear la verificación de JWT
@patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
def test_create_credits(mock_verify_jwt, client):
    data =  {
            "fechaVencimiento": "2023-04-02",
            "idCliente": -1,
            "idCredito": 125,
            "limiteCredito": 261855.0,
            "status": "activo"
    }
    response = client.post('/api/creditos', json=data)
    assert response.status_code == 404
    assert response.json['message'] == "El cliente no existe"
