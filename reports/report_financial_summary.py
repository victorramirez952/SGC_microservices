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


@app.route('/api/reportes/resumen-financiero', methods=['GET'])
@jwt_required()
def report_financial_summary():
    cursor = connection.cursor()

    query = """
    SELECT 
        c.IDCLIENTE,
        COALESCE(SUM(cr.LIMITECREDITO), 0) AS total_credito,
        COALESCE(SUM(p.CANTIDAD), 0) AS total_pago
    FROM 
        CLIENTES c
    LEFT JOIN 
        CREDITOS cr ON c.IDCLIENTE = cr.IDCLIENTE
    LEFT JOIN 
        PAGOS p ON cr.IDCREDITO = p.IDCREDITO
    GROUP BY 
        c.IDCLIENTE
    FETCH FIRST 4000 ROWS ONLY
    """
    try:
         
        cursor.execute(query)
        rows = cursor.fetchall()
        resumen = [
            {
                 "IDCLIENTE": row[0],
                 "TOTALCREDITO": row[1],
                 "TOTALPAGO": row[2]
            }
            for row in rows
        ]

        return jsonify({"message": "Resumen finalizado exitosamente", "resumen": resumen}), 200
    except Exception as e:
        logging.error(f"Ocurrio un error al realizar el resumen: {e}")
        return jsonify({"message": "Error al realizar el resumen"}), 500
    finally:
         cursor.close()
    

if __name__ == '__main__':
	app.run(host = '0.0.0.0', port=5023, debug = True)

