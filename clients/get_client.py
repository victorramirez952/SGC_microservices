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

app = Flask(__name__)
CORS(app)
jwt = init_config(app)
function_error_handler(app)

connection = init_oracle(app)

@app.route('/api/clientes/<int:client_id>', methods=['GET'])
# @jwt_required()
def get_cliente(client_id):
    cursor = connection.cursor()
    query = """
    SELECT * FROM CLIENTES WHERE IDCLIENTE = :client_id
    """
    try:
         
        cursor.execute(query, client_id=client_id)
        rows = cursor.fetchall()
        clients = [
            {
                "IDCLIENTE": row[0],
                "NUMEROCLIENTE": row[1],
                "NOMBRE1": row[2],
                "NOMBRE2": row[3],
                "TELEFONO": row[4],
                "IDENTIFICACIONFISCAL": row[5],
                "FECHA": row[6].strftime('%Y-%m-%d'),
            }
            for row in rows
        ]
        return jsonify({"message": "Cliente encontrado", "clients": clients}), 200
    except Exception as e:
        logging.error(f"Ocurrio un error al obtener el cliente: {e}")
        return jsonify({"message": "Error al obtener el cliente"}), 500
    finally:
         cursor.close()
    

if __name__ == '__main__':
	app.run(host = '0.0.0.0', port=5003, debug = True)

