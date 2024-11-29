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

@app.route('/api/clientes/<int:client_id>', methods=['PUT'])
@jwt_required()
def update_client(client_id):
    data = request.get_json()
    logging.info(f"Datos recibidos: {data}")
    cursor = connection.cursor()
    query = """
    UPDATE
        CLIENTES
    SET
        NUMEROCLIENTE = :NUMEROCLIENTE,
        NOMBRE1 = :NOMBRE1,
        NOMBRE2 = :NOMBRE2,
        TELEFONO = :TELEFONO,
        IDENTIFICACIONFISCAL = :IDENTIFICACIONFISCAL,
        FECHA = TO_DATE(:FECHA, 'YYYY-MM-DD')
    WHERE
        IDCLIENTE = :client_id
    """

    params = {
        'NUMEROCLIENTE': data['NUMEROCLIENTE'],
        'NOMBRE1': data['NOMBRE1'],
        'NOMBRE2': data['NOMBRE2'],
        'TELEFONO': data['TELEFONO'],
        'IDENTIFICACIONFISCAL': data['IDENTIFICACIONFISCAL'],
        'FECHA': data['FECHA'],
        'client_id': client_id
    }

    try:
        cursor.execute(query, params)
        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": "Cliente no encontrado"}), 404

        return jsonify({"message": "Cliente actualizado"}), 200
    except Exception as e:
        logging.error(f"Ocurrio un error al actualizar: {e}")
        return jsonify({"message": "Error al actualizar el cliente"}), 500
    finally:
         cursor.close()
    

if __name__ == '__main__':
	app.run(host = '0.0.0.0', port=5006, debug = True)

