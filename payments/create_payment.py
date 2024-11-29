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

## Obtener el ID máximo de creditos
def get_max_id_payment():
    cursor = connection.cursor()
    query = """
    SELECT MAX(IDPAGO) FROM PAGOS
    """
    try:
        cursor.execute(query)
        maxIdCredit = cursor.fetchone()[0]
    except Exception as e:
        logging.error(f"Error al obtener el ID máximo de pagos: {e}")
        return jsonify({"message": "Error al obtener el ID máximo de pagos"}), 500
    finally:
         cursor.close()
    return maxIdCredit

## Obtener el ID del método de pago
def get_id_method_payment(method):
    cursor = connection.cursor()
    query = """
    SELECT IDMETODOPAGO FROM METODOSPAGOS WHERE CPAG = :method
    """
    try:
        cursor.execute(query, {'method': method})
        result = cursor.fetchone()
        if result:
            idMethodPayment = result[0]
        else:
            idMethodPayment = None
    except Exception as e:
        logging.error(f"Error al obtener el ID del método de pago: {e}")
        return jsonify({"message": "Error al obtener el ID del método de pago"}), 500
    finally:
         cursor.close()
    return idMethodPayment

## ¿Cantidad valido?
def valid_amount(amount):
    return (amount > 0)

## Actualizamos el status del crédito
def update_credit_status(credit_id):
    cursor = connection.cursor()
    query = """
    UPDATE CREDITOS SET STATUS = :status WHERE IDCREDITO = :credit_id
    """
    try:
        cursor.execute(query, {'credit_id': credit_id, 'status': 'inactivo'})
        connection.commit()
    except Exception as e:
        logging.error(f"Error al actualizar el status del crédito: {e}")
        return jsonify({"message": "Error al actualizar el status del crédito"}), 500
    finally:
         cursor.close()
    return True

@app.route('/api/pagos', methods=['POST'])
@jwt_required()
def create_payment():
    data = request.get_json()
    data = uppercase_keys(data)
    
    if not credit_exist(data['IDCREDITO']):
        return jsonify({"message": "El crédito no existe"}), 404
    
    idMethodPayment = get_id_method_payment(data['METODOPAGO'])
    if not idMethodPayment:
        return jsonify({"message": "El método de pago no existe"}), 404

    if not valid_amount(data['CANTIDAD']):
        return jsonify({"message": "Cantidad inválida"}), 400
    
    maxIdPayment = get_max_id_payment()


    cursor = connection.cursor()
    query = """
    INSERT INTO PAGOS
    (IDPAGO, IDCREDITO, FECHA, CANTIDAD, IDMETODOPAGO)
    VALUES
    ( :IDPAGO, :IDCREDITO, TO_DATE(:FECHA, 'YYYY-MM-DD'), :CANTIDAD, :IDMETODOPAGO)
    """

    ## Damos formato a las FECHA
    try:
        if data['FECHA']:
            FECHA = datetime.strptime(data['FECHA'], '%Y-%m-%d').strftime('%Y-%m-%d')
        else:
            FECHA = datetime.now().strftime('%Y-%m-%d')
    except Exception as e:
        logging.error(f"Error al convertir las FECHAs: {e}")
        return jsonify({"message": "Hubo un error al convertir las FECHAs"}), 400

    params = {
        'IDPAGO': maxIdPayment + 1,
        'IDCREDITO': data['IDCREDITO'],
        'FECHA': FECHA,
        'CANTIDAD': data['CANTIDAD'],
        'IDMETODOPAGO': idMethodPayment
    }

    try:
        cursor.execute(query, params)

        ## Actualizamos el status del crédito
        update_credit_status(data['IDCREDITO'])

        connection.commit()
        
        return jsonify({"message": "Pago registrado", "IDPAGO": maxIdPayment + 1}), 201
    except Exception as e:
        logging.error(f"Error al registrar el pago: {e}")
        return jsonify({"message": "Error al registrar el pago"}), 500
    finally:
         cursor.close()
    

if __name__ == '__main__':
	app.run(host = '0.0.0.0', port=5018, debug = True)

