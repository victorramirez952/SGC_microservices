from flask import Flask, Response, jsonify, request, abort
from flask_jwt_extended import jwt_required
from flask_cors import CORS
from dotenv import load_dotenv
import logging
import os
from datetime import datetime

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

@app.route('/api/clientes/<int:cliente_id>', methods=['DELETE'])
@jwt_required()
def delete_client(cliente_id):
    cursor = connection.cursor()
    query = """
    DELETE FROM CLIENTES WHERE IDCLIENTE = :idCliente
    """

    try:
        cursor.execute(query, {'idCliente': cliente_id})
        connection.commit()
        if cursor.rowcount == 0:
            return jsonify({"message": "Cliente no encontrado"}), 404
    except Exception as e:
        logging.error(f"Error al eliminar el cliente: {e}")
        return jsonify({"message": "Error al eliminar el cliente"}), 500
    finally:
         cursor.close()
    return jsonify({"message": "Cliente eliminado"}), 200
    

if __name__ == '__main__':
	app.run(host = '0.0.0.0', port=5007, debug = True)

