import sys
import os
import pytest
from unittest.mock import patch

sys.path.append(os.path.join(os.path.dirname(__file__), '../reports'))
from report_financial_activity import app  

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

## Usamos este decorados para bypassear la verificación de JWT
@patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
def test_report_financial_activity(mock_verify_jwt, client):
    data = {
        "idCliente": 288,
    }
    response = client.post('/api/reportes/actividad', json=data)
    assert response.status_code == 201
    assert response.json['message'] == "REporte realizado correctamente"
