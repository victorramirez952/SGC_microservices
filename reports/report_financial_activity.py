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
app.logger.setLevel(logging.INFO) 

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

@app.route('/api/reportes/actividad', methods=['POST'])
@jwt_required()
def create_financial_activity_report():
    data = request.get_json()
    data = uppercase_keys(data)
    
    if not client_exist(data['IDCLIENTE']):
        return jsonify({"message": "El cliente no existe"}), 404
    
    cursor = connection.cursor()

    queryCreditos = """
    SELECT IDCREDITO, IDCLIENTE, LIMITECREDITO, FECHAVENCIMIENTO, STATUS FROM CREDITOS WHERE IDCLIENTE = :client_id
    """
    
    queryPagos = """
    SELECT IDPAGO, IDCREDITO, FECHA, CANTIDAD, IDMETODOPAGO FROM pagos WHERE IDCREDITO IN (SELECT IDCREDITO FROM CREDITOS WHERE IDCLIENTE = :client_id)
    """

    try:
        cursor.execute(queryCreditos, {'client_id': data['IDCLIENTE']})
        rowsCreditos = cursor.fetchall()
        logging.info(f"rowsCreditos: {rowsCreditos}")
        creditos = [
            {
                "IDCREDITO": row[0],
                "IDCLIENTE": row[1],
                "LIMITECREDITO": row[2],
                "FECHAVENCIMIENTO": row[3].strftime('%Y-%m-%d'),
                "STATUS": row[4]
            }
            for row in rowsCreditos
        ]
        # date_column_names = ["FECHA"]
        # creditos = format_date_columns(rowsCreditos, date_column_names)

        cursor.execute(queryPagos, {'client_id': data['IDCLIENTE']})
        rowsPagos = cursor.fetchall()
        pagos = [
            {
                "IDPAGO": row[0],
                "IDCREDITO": row[1],
                "FECHA": row[2].strftime('%Y-%m-%d'),
                "CANTIDAD": row[3],
                "IDMETODOPAGO": row[4]
            }
            for row in rowsPagos
        ]

        reporte = {
            "IDCLIENTE": data['IDCLIENTE'],
            "CREDITOS": creditos,
            "PAGOS": pagos
        }

        return jsonify({"message": "Reporte realizado correctamente", "reporte": reporte}), 201
    except Exception as e:
        logging.error(f"Error al realizar el reporte: {e}")
        return jsonify({"message": "Error al realizar el reporte"}), 500
    finally:
         cursor.close()
    

if __name__ == '__main__':
	app.run(host = '0.0.0.0', port=5022, debug = True)

