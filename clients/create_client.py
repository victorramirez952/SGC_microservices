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

@app.route('/api/clientes', methods=['POST'])
@jwt_required()
def create_client():
    data = request.get_json()
    #Obtener atributos del cliente
    cursor = connection.cursor()
    query = """
    INSERT INTO CLIENTES
    (IDCLIENTE,NUMEROCLIENTE, NOMBRE1, NOMBRE2, TELEFONO1, IDENTIFICACIONFISCAL, FECHA)
    VALUES
    (:idCliente, :numeroCliente, :nombre1, :nombre2, :telefono1, :identificacionFiscal, TO_DATE(:fecha, 'YYYY-MM-DD'))
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
        'idCliente': maxIdCliente + 1,
        'numeroCliente': data['numeroCliente'],
        'nombre1': data['nombre1'],
        'nombre2': data['nombre2'],
        'telefono1': data['telefono1'],
        'identificacionFiscal': data['identificacionFiscal'],
        'fecha': data['fecha']
    }

    numeroClienteUnique = 0
    query2 = """
    SELECT COUNT(*) FROM CLIENTES WHERE NUMEROCLIENTE = :numeroCliente
    """
    try:
        cursor.execute(query2, {'numeroCliente': data['numeroCliente']})
        numeroClienteUnique = cursor.fetchone()[0]

        if numeroClienteUnique > 0:
            return jsonify({"message": "El numeroCliente ya existe"}), 400

    except Exception as e:
        logging.error(f"Error al verificar numeroCliente único: {e}")
        return jsonify({"message": "Error al verificar numeroCliente único"}), 500

    try:
        cursor.execute(query, params)
        connection.commit()
        return jsonify({"message": "Cliente registrado", "idCliente": maxIdCliente + 1}), 201
    except Exception as e:
        logging.error(f"Error al registrar el cliente: {e}")
        return jsonify({"message": "Error al registrar el cliente"}), 500
    finally:
         cursor.close()
    

if __name__ == '__main__':
	app.run(host = '0.0.0.0', port=5005, debug = True)

