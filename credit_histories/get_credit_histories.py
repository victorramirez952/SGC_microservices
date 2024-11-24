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


@app.route('/api/historial-credito', methods=['GET'])
@jwt_required()
def get_credit_histories():
    cursor = connection.cursor()
    try: 
        # cursor.execute("SELECT * FROM (SELECT * FROM HISTORIALESCREDITOS ORDER BY dbms_random.value) WHERE ROWNUM <= 4")
        cursor.execute("SELECT * FROM HISTORIALESCREDITOS ORDER BY IDCLIENTE")
        historial = cursor.fetchall()

        column_names = [col[0] for col in cursor.description]
        historial = [dict(zip(column_names, row)) for row in historial]

        date_column_names = ["FECHACONSULTA", "FECHAINICIO", "FECHAFIN"]
        historial = format_date_columns(historial, date_column_names)
    except Exception as e:
        logging.error(f"Ocurrio un error al obtener el historial: {e}")
        return jsonify({"message": "Error al obtener el historial"}), 500
    finally:
         cursor.close()
    return jsonify({"message": "Historial de creditos", "historial": historial}), 200
    

if __name__ == '__main__':
	app.run(host = '0.0.0.0', port=5008, debug = True)

