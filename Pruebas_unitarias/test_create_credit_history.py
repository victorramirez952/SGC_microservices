import sys
import os
import pytest
from unittest.mock import patch

sys.path.append(os.path.join(os.path.dirname(__file__), '../credit_histories/'))
from create_credit_history import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

## Usamos este decorados para bypassear la verificación de JWT
@patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
def test_create_credit_history(mock_verify_jwt, client):
    data =  {
            "fechaFin": "2024-01-01",
            "fechaInicio": "2015-01-01",
            "idCliente": 123
    }
    response = client.post('/api/historial-credito', json=data)
    assert response.status_code == 201
    assert response.json['message'] == "Historial crediticio registrado"
