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


@app.route('/api/historial-credito/<int:client_id>', methods=['GET'])
@jwt_required()
def get_credit_history(client_id):
    cursor = connection.cursor()
    query = """
    SELECT * FROM HISTORIALESCREDITOS WHERE IDCLIENTE = :client_id
    """
    try:
         
        cursor.execute(query, client_id=client_id)
        rows = cursor.fetchall()

        column_names = [col[0] for col in cursor.description]
        historiales = [dict(zip(column_names, row)) for row in rows]
        
        date_column_names = ["FECHACONSULTA", "FECHAINICIO", "FECHAFIN"]
        formatted_historiales = format_date_columns(historiales, date_column_names)
        # historiales = [
        #     {
        #         "IDHISTORIAL": row[0],
        #         "IDCLIENTE": row[1],
        #         "FECHACONSULTA": row[2].strftime('%Y-%m-%d'),
        #         "FECHAINICIO": row[3].strftime('%Y-%m-%d'),
        #         "FECHAFIN": row[4].strftime('%Y-%m-%d'),
        #         "NUMEROCREDITOSPAGADOS": row[5],
        #         "NUMEROCREDTOSATRASADOS": row[6]
        #     }
        #     for row in rows
        # ]
        return jsonify({"message": "Historial de creditos encontrado", "historial": formatted_historiales}), 200
    except Exception as e:
        logging.error(f"Ocurrio un error al obtener el historial de creditos: {e}")
        return jsonify({"message": "Error al obtener el historial de creditos"}), 500
    finally:
         cursor.close()
    

if __name__ == '__main__':
	app.run(host = '0.0.0.0', port=5009, debug = True)

