from flask import Flask, Response, jsonify, request, abort
from flask_jwt_extended import jwt_required
from flask_cors import CORS
import logging

import sys
sys.path.append('/home/ec2-user/Proyecto/Svelte/Services')

from df_config import init_oracle
from jwt_settings import init_config
from error_handlers import function_error_handler

app = Flask(__name__)
CORS(app)
jwt = init_config(app)
function_error_handler(app)

connection = init_oracle(app)

@app.route('/api/reportes/creditos-atrasados', methods=['GET'])
@jwt_required()
def report_overdue_credits():
    cursor = connection.cursor()

    query = """
    SELECT 
        CLIENTES.IDCLIENTE,
        CLIENTES.NUMEROCLIENTE,
        CLIENTES.NOMBRE1,
        CLIENTES.NOMBRE2,
        CLIENTES.TELEFONO1,
        CLIENTES.IDENTIFICACIONFISCAL,
        CREDITOS.IDCREDITO,
        CREDITOS.FECHAVENCIMIENTO
    FROM 
        CLIENTES
    JOIN 
        CREDITOS ON CLIENTES.IDCLIENTE = CREDITOS.IDCLIENTE
    WHERE 
        CREDITOS.STATUS = 'activo'
        AND CREDITOS.FECHAVENCIMIENTO < SYSDATE
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
               "creditos": [
                    {
                         "idCredito": row[6],
                         "fechaVencimiento": row[7].strftime('%Y-%m-%d')
                    }
               ]
            }
            for row in rows
        ]
        return jsonify({"message": "Clientes con creditos atrasados encontrados", "clientes": resultados}), 200
    except Exception as e:
        logging.error(f"Ocurrio un error al obtener los clientes con creditos atrasados: {e}")
        return jsonify({"message": "Error al obtener los clientes con creditos atrasados"}), 500
    finally:
         cursor.close()
    

if __name__ == '__main__':
	app.run(host = '0.0.0.0', port=5020, debug = True)

