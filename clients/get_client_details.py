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

@app.route('/api/clientes/<int:client_id>/detalles', methods=['GET'])
@jwt_required()
def get_cliente(client_id):
    cursor = connection.cursor()
    query = """
    SELECT
        c.IDCLIENTE,
        c.NUMEROCLIENTE,
        c.NOMBRE1,
        c.NOMBRE2,
        c.TELEFONO,
        c.IDENTIFICACIONFISCAL,
        c.FECHA,
        hc.IDHISTORIAL,
        hc.FECHACONSULTA,
        hc.FECHAINICIO,
        hc.FECHAFIN,
        hc.NUMEROCREDITOSPAGADOS,
        hc.NUMEROCREDITOSATRASADOS
    FROM
        CLIENTES c
    INNER JOIN
        HISTORIALESCREDITOS hc ON c.IDCLIENTE = hc.IDCLIENTE
    WHERE
        c.IDCLIENTE = :client_id
    """
    try:
        cursor.execute(query, client_id=client_id)
        rows = cursor.fetchall()
        if not rows:
            return jsonify({"message": "Datos no encontrados"}), 404
        clients = [
            {
                "IDCLIENTE": row[0],
                "NUMEROCLIENTE": row[1],
                "NOMBRE1": row[2],
                "NOMBRE2": row[3],
                "TELEFONO": row[4],
                "IDENTIFICACIONFISCAL": row[5],
                "FECHA": row[6].strftime('%Y-%m-%d'),
                "HISTORIAL": [
                    {
                        "IDHISTORIAL": row[7],
                        "FECHACONSULTA": row[8].strftime('%Y-%m-%d'),
                        "FECHAINICIO": row[9].strftime('%Y-%m-%d'),
                        "FECHAFIN": row[10].strftime('%Y-%m-%d'),
                        "NUMEROCREDITOSPAGADOS": row[11],
                        "NUMEROCREDITOSATRASADOS": row[12]
                    }
                ]
            }
            for row in rows
        ]

        return jsonify({"message": "Cliente encontrado", "clients": clients}), 200
    except Exception as e:
        logging.error(f"Ocurrio un error al obtener los clientes: {e}")
        return jsonify({"message": "Hubo un error"}), 500
    finally:
        cursor.close()
    

if __name__ == '__main__':
	app.run(host = '0.0.0.0', port=5004, debug = True)

