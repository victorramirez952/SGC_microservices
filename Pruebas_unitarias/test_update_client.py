import sys
import os
import pytest
from unittest.mock import patch

sys.path.append(os.path.join(os.path.dirname(__file__), '../clients'))
from update_client import app  

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

## Usamos este decorados para bypassear la verificación de JWT
@patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
def test_update_client(mock_verify_jwt, client):
    data = {
        "fecha": "2001-09-23",
        "identificacionFiscal": "70324411.0",
        "nombre1": "CADAVID SIERRA JESUS MARIA",
        "nombre2": "**CONFITERIA EL PORVENIR**",
        "numeroCliente": 323,
        "telefono": "4-2895557"
    }
    idCliente = 45
    response = client.put(f'/api/clientes/{idCliente}', json=data)
    assert response.status_code == 200
    assert response.json['message'] == "Cliente actualizado"
