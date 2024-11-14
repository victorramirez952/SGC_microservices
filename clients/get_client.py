from flask import Flask, Response, jsonify, request, abort
from flask_jwt_extended import jwt_required
from flask_cors import CORS
import logging

import sys
sys.path.append('/home/ec2-user/Proyecto/Svelte/Services')

from df_config import init_oracle
from jwt_settings import init_config
from error_handlers import function_error_handler

app = Flask(__name__)
CORS(app)
jwt = init_config(app)
function_error_handler(app)

connection = init_oracle(app)

@app.route('/api/clientes/<int:client_id>', methods=['GET'])
@jwt_required()
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
                "idCliente": row[0],
                "numeroCliente": row[1],
                "nombre1": row[2],
                "nombre2": row[3],
                "telefono1": row[4],
                "identificacionFiscal": row[5],
                "fecha": row[6].strftime('%Y-%m-%d'),
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

