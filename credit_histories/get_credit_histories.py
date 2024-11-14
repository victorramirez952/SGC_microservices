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


@app.route('/api/historial-credito', methods=['GET'])
@jwt_required()
def get_credit_histories():
    cursor = connection.cursor()
    try: 
        # cursor.execute("SELECT * FROM (SELECT * FROM HISTORIALESCREDITICIOS ORDER BY dbms_random.value) WHERE ROWNUM <= 4")
        cursor.execute("SELECT * FROM HISTORIALESCREDITICIOS ORDER BY IDCLIENTE")
        rows = cursor.fetchall()
        historial = [
            {
                "idHistorial": row[0],
                "idCliente": row[1],
                "fechaConsulta": row[2],
                "fechaInicio": row[3],
                "fechaFin": row[4],
                "numeroCreditosPagados": row[5],
                "numeroCreditosAtrasados": row[6]
            }
            for row in rows
        ]
    except Exception as e:
        logging.error(f"Ocurrio un error al obtener el historial: {e}")
        return jsonify({"message": "Error al obtener el historial"}), 500
    finally:
         cursor.close()
    return jsonify({"message": "Historial de creditos", "historial": historial}), 200
    

if __name__ == '__main__':
	app.run(host = '0.0.0.0', port=5008, debug = True)

