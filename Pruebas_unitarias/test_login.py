import sys
import os
import pytest
import json
from flask import jsonify
from datetime import timedelta
from unittest.mock import patch, MagicMock

sys.path.append(os.path.join(os.path.dirname(__file__), '../clients'))

from login import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_home(client):
    response = client.get('/api/login')
    assert response.status_code == 401
    assert response.json == {"message": "Sistema gestion de clientes"}

def test_create_token_missing_credentials(client):
    user_data = {}
    response = client.post('/api/login', data=json.dumps(user_data), content_type='application/json')
    assert response.status_code == 401
    assert response.json['message'] == "Faltan credenciales"

