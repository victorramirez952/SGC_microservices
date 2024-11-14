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
        numeroCliente = :numeroCliente,
        NOMBRE1 = :nombre1,
        NOMBRE2 = :nombre2,
        TELEFONO1 = :telefono1,
        IDENTIFICACIONFISCAL = :identificacionFiscal,
        FECHA = TO_DATE(:fecha, 'YYYY-MM-DD')
    WHERE
        IDCLIENTE = :client_id
    """

    params = {
        'numeroCliente': data['numeroCliente'],
        'nombre1': data['nombre1'],
        'nombre2': data['nombre2'],
        'telefono1': data['telefono1'],
        'identificacionFiscal': data['identificacionFiscal'],
        'fecha': data['fecha'],
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

