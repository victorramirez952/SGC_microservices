from flask import Flask, Response, jsonify, request, abort
from flask_jwt_extended import jwt_required
from flask_cors import CORS
from dotenv import load_dotenv
import logging
import os

load_dotenv()

import sys
main_path = os.getenv('MAIN_DIRECTORY_PATH')
sys.path.append(f'{main_path}')

from db_config import init_oracle
from jwt_settings import init_config
from error_handlers import function_error_handler
from functions import *

app = Flask(__name__)
CORS(app)
jwt = init_config(app)
function_error_handler(app)

connection = init_oracle(app)
    
## Función para saber si un cliente existe
def client_exist(client_id):
    cursor = connection.cursor()
    query = """
    SELECT IDCLIENTE FROM CLIENTES WHERE IDCLIENTE = :client_id
    """
    try:
        cursor.execute(query, {'client_id': client_id})
        clientExist = cursor.fetchone()
        if not clientExist:
            return False
        else:
            return True
    except Exception as e:
        logging.error(f"Error al buscar el cliente: {e}")
        return False

@app.route('/api/creditos/<int:client_id>', methods=['GET'])
@jwt_required()
def get_client_credit(client_id):
    cursor = connection.cursor()
    query = """
    SELECT * FROM CREDITOS WHERE IDCLIENTE = :client_id
    """

    if not client_exist(client_id):
        return jsonify({"message": "El cliente no existe"}), 404
    
    try:
         
        cursor.execute(query, client_id=client_id)
        rows = cursor.fetchall()
        credits = [
            {
                "IDCREDITO": row[0],
                "IDCLIENTE": row[1],
                "LIMITECREDITO": row[2],
                "FECHAVENCIMIENTO": row[3].strftime('%Y-%m-%d'),
                "STATUS": row[4]
            }
            for row in rows
        ]
        return jsonify({"message": "Creditos encontrados", "credits": credits}), 200
    except Exception as e:
        logging.error(f"Ocurrio un error al obtener los creditos: {e}")
        return jsonify({"message": "Error al obtener los creditos"}), 500
    finally:
         cursor.close()
    

if __name__ == '__main__':
	app.run(host = '0.0.0.0', port=5014, debug = True)

