import sys
import os
import pytest
from unittest.mock import patch

sys.path.append(os.path.join(os.path.dirname(__file__), '../clients'))
from create_client import app  

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

## Usamos este decorados para bypassear la verificación de JWT
@patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
def test_create_client(mock_verify_jwt, client):
    data = {
        "fecha": "2001-09-23",
        "identificacionFiscal": "70324411.0",
        "nombre1": "CADAVID SIERRA JESUS MARIA",
        "nombre2": "**CONFITERIA EL PORVENIR**",
        "numeroCliente": 323,
        "telefono1": "4-2895557"
    }
    
    response = client.post('/api/clientes', json=data)
    assert response.status_code == 400
    assert response.json['message'] == "El numeroCliente ya existe"
