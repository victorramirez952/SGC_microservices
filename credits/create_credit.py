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
    found = False
    cursor = connection.cursor()
    query = """
    SELECT IDCLIENTE FROM CLIENTES WHERE IDCLIENTE = :client_id
    """
    try:
        cursor.execute(query, {'client_id': client_id})
        clientExist = cursor.fetchone()
        if not clientExist:
            found = False
        else:
            found = True
    except Exception as e:
        logging.error(f"Error al buscar el cliente: {e}")
        found = False
    finally:
         cursor.close()
    return found

## Obtener el ID máximo de creditos
def get_max_id_credit():
    cursor = connection.cursor()
    query = """
    SELECT MAX(IDCREDITO) FROM CREDITOS
    """
    try:
        cursor.execute(query)
        maxIdCredit = cursor.fetchone()[0]
    except Exception as e:
        logging.error(f"Error al obtener el ID máximo de creditos: {e}")
        return jsonify({"message": "Error al obtener el ID máximo de creditos"}), 500
    finally:
         cursor.close()
    return maxIdCredit

@app.route('/api/creditos', methods=['POST'])
@jwt_required()
def create_credit():
    data = request.get_json()
    data = uppercase_keys(data)

    if not client_exist(data['IDCLIENTE']):
        return jsonify({"message": "El cliente no existe"}), 404


    cursor = connection.cursor()
    query = """
    INSERT INTO CREDITOS
    (IDCREDITO, IDCLIENTE, LIMITECREDITO, FECHAVENCIMIENTO, STATUS)
    VALUES
    (:IDCREDITO, :IDCLIENTE, :LIMITECREDITO, TO_DATE(:FECHAVENCIMIENTO, 'YYYY-MM-DD'), :STATUS)
    """

    maxIdCredit = get_max_id_credit()

    params = {
        'IDCREDITO': maxIdCredit + 1,
        'IDCLIENTE': data['IDCLIENTE'],
        'LIMITECREDITO': data['LIMITECREDITO'],
        'FECHAVENCIMIENTO': data['FECHAVENCIMIENTO'],
        'STATUS': data.get('STATUS', 'activo')
    }

    try:
        cursor.execute(query, params)
        connection.commit()
        return jsonify({"message": "Credito registrado", "IDCREDITO": maxIdCredit + 1}), 201
    except Exception as e:
        logging.error(f"Error al registrar el credito: {e}")
        return jsonify({"message": "Error al registrar el credito"}), 500
    finally:
         cursor.close()
    

if __name__ == '__main__':
	app.run(host = '0.0.0.0', port=5015, debug = True)

