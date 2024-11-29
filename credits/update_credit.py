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
from datetime import datetime
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
    data = uppercase_keys(data)

    if not client_exist(data['IDCLIENTE']):
        return jsonify({"message": "El cliente no existe"}), 404
    
    if not credit_exist(credit_id):
        return jsonify({"message": "El crédito no existe"}), 404
    
    
    cursor = connection.cursor()    
    query = """
    UPDATE CREDITOS SET
        LIMITECREDITO = :LIMITECREDITO,
        FECHAVENCIMIENTO = TO_DATE(:FECHAVENCIMIENTO, 'YYYY-MM-DD'),
        STATUS = :STATUS
    WHERE IDCREDITO = :IDCREDITO
    """
    
    ## Damos formato a las fecha
    try:
        FECHAVENCIMIENTO = datetime.strptime(data['FECHAVENCIMIENTO'], '%Y-%m-%d').strftime('%Y-%m-%d')
    except ValueError as ve:
        logging.error(f"Error al convertir las fechas: {ve}")
        return jsonify({"message": "Formato de fecha inválido"}), 400

    params = {
        'IDCREDITO': credit_id,
        'LIMITECREDITO': data['LIMITECREDITO'],
        'FECHAVENCIMIENTO': FECHAVENCIMIENTO,
        'STATUS': data.get('STATUS', 'activo')
    }

    try:
        cursor.execute(query, params)
        connection.commit()
        return jsonify({"message": "Credito modificado", "IDCREDITO": credit_id}), 201
    except Exception as e:
        logging.error(f"Error al modificar el credito: {e}")
        return jsonify({"message": "Error al modificar el credito"}), 500
    finally:
         cursor.close()
    

if __name__ == '__main__':
	app.run(host = '0.0.0.0', port=5016, debug = True)

