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

@app.route('/api/pagos', methods=['GET'])
@jwt_required()
def get_payments():
    query = """SELECT * FROM (SELECT * FROM PAGOS ORDER BY IDPAGO) WHERE ROWNUM <= 24 """
    query = """SELECT * FROM (SELECT * FROM PAGOS ORDER BY dbms_random.value) WHERE ROWNUM <= 4"""
    # query = """SELECT * FROM PAGOS ORDER BY IDCLIENTE"""
    try: 
        cursor = connection.cursor()
        cursor.execute(query)
        # cursor.execute(query)
        rows = cursor.fetchall()
        payments = [
            {
                'IDPAGO': row[0],
                'IDCREDITO': row[1],
                'FECHA': row[2].strftime('%Y-%m-%d'),
                'CANTIDAD': row[3],
                'IDMETODOPAGO': row[4]
            }
            for row in rows
        ]
    except Exception as e:
        logging.error(f"Ocurrio un error al obtener los pagos: {e}")
        return jsonify({"message": "Error al obtener los pagos"}), 500
    finally:
         cursor.close()
    return jsonify({"message": "Pagos", "pagos": payments}), 200
    

if __name__ == '__main__':
	app.run(host = '0.0.0.0', port=5019, debug = True)

