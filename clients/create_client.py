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

@app.route('/api/clientes', methods=['POST'])
@jwt_required()
def create_client():
    data = request.get_json()
    data = uppercase_keys(data)
    logging.info(f"Datos: {data}")
    cursor = connection.cursor()
    query = """
    INSERT INTO CLIENTES
    (IDCLIENTE,NUMEROCLIENTE, NOMBRE1, NOMBRE2, TELEFONO, IDENTIFICACIONFISCAL, FECHA)
    VALUES
    (:IDCLIENTE, :NUMEROCLIENTE, :NOMBRE1, :NOMBRE2, :TELEFONO, :IDENTIFICACIONFISCAL, TO_DATE(:FECHA, 'YYYY-MM-DD'))
    """

    maxIdCliente = 0
    query2 = """
    SELECT MAX(IDCLIENTE) FROM CLIENTES
    """
    try:
        cursor.execute(query2)
        maxIdCliente = cursor.fetchone()[0]
    except Exception as e:
        logging.error(f"Error al obtener el ID máximo del cliente: {e}")
        return jsonify({"message": "Error al obtener el ID máximo del cliente"}), 500

    params = {
        'IDCLIENTE': maxIdCliente + 1,
        'NUMEROCLIENTE': data['NUMEROCLIENTE'],
        'NOMBRE1': data['NOMBRE1'],
        'NOMBRE2': data['NOMBRE2'],
        'TELEFONO': data['TELEFONO'],
        'IDENTIFICACIONFISCAL': data['IDENTIFICACIONFISCAL'],
        'FECHA': data['FECHA']
    }

    NUMEROCLIENTEUnique = 0
    query2 = """
    SELECT COUNT(*) FROM CLIENTES WHERE NUMEROCLIENTE = :NUMEROCLIENTE
    """
    try:
        cursor.execute(query2, {'NUMEROCLIENTE': data['NUMEROCLIENTE']})
        NUMEROCLIENTEUnique = cursor.fetchone()[0]

        if NUMEROCLIENTEUnique > 0:
            return jsonify({"message": "El NUMEROCLIENTE ya existe"}), 400

    except Exception as e:
        logging.error(f"Error al verificar NUMEROCLIENTE único: {e}")
        return jsonify({"message": "Error al verificar NUMEROCLIENTE único"}), 500

    try:
        cursor.execute(query, params)
        connection.commit()
        return jsonify({"message": "Cliente registrado", "IDCLIENTE": maxIdCliente + 1}), 201
    except Exception as e:
        logging.error(f"Error al registrar el cliente: {e}")
        return jsonify({"message": "Error al registrar el cliente"}), 500
    finally:
         cursor.close()
    

if __name__ == '__main__':
	app.run(host = '0.0.0.0', port=5005, debug = True)

