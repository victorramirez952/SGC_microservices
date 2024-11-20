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


@app.route('/api/historial-credito/<int:client_id>', methods=['GET'])
@jwt_required()
def get_credit_history(client_id):
    cursor = connection.cursor()
    query = """
    SELECT * FROM HISTORIALESCREDITICIOS WHERE IDCLIENTE = :client_id
    """
    try:
         
        cursor.execute(query, client_id=client_id)
        rows = cursor.fetchall()
        historiales = [
            {
                "idHistorial": row[0],
                "idCliente": row[1],
                "fechaConsulta": row[2].strftime('%Y-%m-%d'),
                "fechaInicio": row[3].strftime('%Y-%m-%d'),
                "fechaFin": row[4].strftime('%Y-%m-%d'),
                "numeroCreditosPagados": row[5],
                "numeroCreditosAtrasados": row[6]
            }
            for row in rows
        ]
        return jsonify({"message": "Historial de creditos encontrado", "historial": historiales}), 200
    except Exception as e:
        logging.error(f"Ocurrio un error al obtener el historial de creditos: {e}")
        return jsonify({"message": "Error al obtener el historial de creditos"}), 500
    finally:
         cursor.close()
    

if __name__ == '__main__':
	app.run(host = '0.0.0.0', port=5009, debug = True)

