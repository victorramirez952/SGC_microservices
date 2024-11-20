from flask import Flask, Response, jsonify, request, abort
from flask_jwt_extended import jwt_required
from flask_cors import CORS
import logging

import sys
sys.path.append('/home/ec2-user/Proyecto/Svelte/Services')

from db_config import init_oracle
from jwt_settings import init_config
from error_handlers import function_error_handler

app = Flask(__name__)
CORS(app)
jwt = init_config(app)
function_error_handler(app)

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
        cl.TELEFONO1,
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
        resultados = [
            {
               "idCliente": row[0],
               "numeroCliente": row[1],
               "nombre1": row[2],
               "nombre2": row[3],
               "telefono1": row[4],
               "identificacionFiscal": row[5],
               "fecha": row[6].strftime('%Y-%m-%d'),
               "creditos": [
                    {
                         "idCredito": row[7],
                         "status": row[8]
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

