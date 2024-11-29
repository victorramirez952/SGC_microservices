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

from db_config import init_oracle
from jwt_settings import init_config
from error_handlers import function_error_handler
from functions import *

app = Flask(__name__)
CORS(app)
jwt = init_config(app)
function_error_handler(app)

connection = init_oracle(app)


@app.route('/')
def inicio():
    return 'raiz de la app'

@app.route('/api/clientes', methods=['GET'])
@jwt_required()
def get_clientes():
    try: 
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM (SELECT * FROM CLIENTES ORDER BY IDCLIENTE) WHERE ROWNUM <= 24")
        # cursor.execute("SELECT * FROM CLIENTES ORDER BY IDCLIENTE")
        clientes = cursor.fetchall()

        column_names = [col[0] for col in cursor.description]
        clientes = [dict(zip(column_names, row)) for row in clientes]
        
        date_column_names = ["FECHA"]
        formatted_clientes = format_date_columns(clientes, date_column_names)

        return jsonify({"message": "Cliente encontrado", "clientes": formatted_clientes}), 200
    except Exception as e:
        logging.error(f"Ocurrio un error al obtener los clientes: {e}")
        return jsonify({"message": "Error al obtener los clientes"}), 500
    finally:
        cursor.close()
    

if __name__ == '__main__':
	app.run(host = '0.0.0.0', port=5002, debug = True)

