from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token
from werkzeug.exceptions import BadRequest
from flask_cors import CORS
import logging
from dotenv import load_dotenv
import os
import sys
from datetime import timedelta

## Para poder importar el archivo de configuración 
sys.path.append('/home/ec2-user/Proyecto/Svelte/Services')
from df_config import init_oracle

load_dotenv()

app = Flask(__name__)
CORS(app)
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
jwt = JWTManager(app)
connection = init_oracle(app)

@app.errorhandler(BadRequest)
def handle_bad_request(error):
    return jsonify({"message": "Faltan credenciales"}), 401

@app.errorhandler(Exception)
def handle_generic_error(e):
    logging.error(f"Un error ocurrió: {e}")
    return jsonify({"message": "Un error inesperado ocurrió"}), 500

@app.route("/api/login", methods=["GET"])
def index():
    return jsonify({"message": "Sistema gestion de clientes"}), 401


@app.route("/api/login", methods=["POST"])
def create_token():
    data = request.get_json()
    username = data.get('nombreUsuario')
    password = data.get('password_Hash')
    if not username or not password:
        return jsonify({"message": "Faltan credenciales"}), 401

    cursor = connection.cursor()
    query = """
    SELECT IDUSUARIO, IDCLIENTE, NOMBREUSUARIO, CORREO, PASSWORD_HASH FROM USUARIOS 
    WHERE NOMBREUSUARIO = :username AND DBMS_LOB.SUBSTR(PASSWORD_HASH, 4000, 1) = :password
    """
    try:
        cursor.execute(query, username=username, password=password)
        user = cursor.fetchone()
        if not user:
            return jsonify({"message": "Usuario o contrasenia incorrectos"}), 401
    except Exception as e:
        logging.error(f"Ocurrio un error al validar el usuario: {e}")
        return jsonify({"message": "Error al validar el usuario"}), 500
    finally:
        cursor.close()
    
    expires = timedelta(hours=4)
    access_token = create_access_token(identity=user[0], expires_delta=expires)
    return jsonify({"message": "Ingreso correcto de credenciales", "token": access_token, "user_id": user[0], "idCliente": user[1]})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

