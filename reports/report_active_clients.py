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
app.logger.setLevel(logging.INFO) 

connection = init_oracle(app)

@app.route('/api/reportes/clientes-activos', methods=['GET'])
@jwt_required()
def report_active_clients():
    cursor = connection.cursor()

    query = """
    SELECT
        cl.IDCLIENTE,
        cl.NUMEROCLIENTE,
        cl.NOMBRE1,
        cl.NOMBRE2,
        cl.TELEFONO,
        cl.IDENTIFICACIONFISCAL,
        cl.FECHA,
        cr.IDCREDITO,
        cr.STATUS
    FROM
        CLIENTES cl
    JOIN
        CREDITOS cr ON cl.IDCLIENTE = cr.IDCLIENTE
    WHERE
        cr.STATUS = 'activo'
    FETCH FIRST 10 ROWS ONLY
    """
    try:
         
        cursor.execute(query)
        rows = cursor.fetchall()
        logging.info(f"rowsCreditos: {rows}")
        resultados = [
            {
               "IDCLIENTE": row[0],
               "NUMEROCLIENTE": row[1],
               "NOMBRE1": row[2],
               "NOMBRE2": row[3],
               "TELEFONO": row[4],
               "IDENTIFICACIONFISCAL": row[5],
               "CREDITOS": [
                    {
                         "IDCREDITO": row[7],
                         "STATUS": row[8]
                    }
               ]
            }
            for row in rows
        ]
        return jsonify({"message": "Clientes activos encontrados", "clientes": resultados}), 200
    except Exception as e:
        logging.error(f"Ocurrio un error al obtener los clientes activos: {e}")
        return jsonify({"message": "Error al obtener los clientes activos"}), 500
    finally:
         cursor.close()
    

if __name__ == '__main__':
	app.run(host = '0.0.0.0', port=5021, debug = True)

