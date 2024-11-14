import os
from flask_jwt_extended import JWTManager
from flask import jsonify
from dotenv import load_dotenv

load_dotenv()

def init_config(app):
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'
    app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
    jwt = JWTManager(app)
    return jwt

