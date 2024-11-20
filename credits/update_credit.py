from flask import Flask, Response, jsonify, request, abort
from flask_jwt_extended import jwt_required
from flask_cors import CORS
import logging

import sys
sys.path.append('/home/ec2-user/Proyecto/Svelte/Services')

from db_config import init_oracle
from datetime import datetime
from jwt_settings import init_config
from error_handlers import function_error_handler

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

## Función para saber si un crédito existe
def credit_exist(credit_id):
    found = False
    cursor = connection.cursor()
    query = """
    SELECT IDCREDITO FROM CREDITOS WHERE IDCREDITO = :credit_id
    """
    try:
        cursor.execute(query, {'credit_id': credit_id})
        creditExist = cursor.fetchone()
        if not creditExist:
            found = False
        else:
            found = True
    except Exception as e:
        logging.error(f"Error al buscar el crédito: {e}")
        found = False
    finally:
         cursor.close()
    return found

@app.route('/api/creditos/<int:credit_id>/actualizar', methods=['PUT'])
@jwt_required()
def update_credit(credit_id):
    data = request.get_json()

    if not client_exist(data['idCliente']):
        return jsonify({"message": "El cliente no existe"}), 404
    
    if not credit_exist(credit_id):
        return jsonify({"message": "El crédito no existe"}), 404
    
    
    cursor = connection.cursor()    
    query = """
    UPDATE CREDITOS SET
        LIMITECREDITO = :limiteCredito,
        FECHAVENCIMIENTO = TO_DATE(:fechaVencimiento, 'YYYY-MM-DD'),
        STATUS = :status
    WHERE IDCREDITO = :idCredito
    """
    
    ## Damos formato a las fecha
    try:
        fechaVencimiento = datetime.strptime(data['fechaVencimiento'], '%Y-%m-%d').strftime('%Y-%m-%d')
    except ValueError as ve:
        logging.error(f"Error al convertir las fechas: {ve}")
        return jsonify({"message": "Formato de fecha inválido"}), 400

    params = {
        'idCredito': credit_id,
        'limiteCredito': data['limiteCredito'],
        'fechaVencimiento': fechaVencimiento,
        'status': data.get('status', 'activo')
    }

    try:
        cursor.execute(query, params)
        connection.commit()
        return jsonify({"message": "Credito modificado", "idCredito": credit_id}), 201
    except Exception as e:
        logging.error(f"Error al modificar el credito: {e}")
        return jsonify({"message": "Error al modificar el credito"}), 500
    finally:
         cursor.close()
    

if __name__ == '__main__':
	app.run(host = '0.0.0.0', port=5016, debug = True)

