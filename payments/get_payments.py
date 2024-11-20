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

@app.route('/api/pagos', methods=['GET'])
@jwt_required()
def get_payments():
    cursor = connection.cursor()
    try: 
        # cursor.execute("SELECT * FROM (SELECT * FROM PAGOS ORDER BY dbms_random.value) WHERE ROWNUM <= 4")
        cursor.execute("SELECT * FROM HISTORIALESCREDITICIOS ORDER BY IDCLIENTE")
        rows = cursor.fetchall()
        payments = [
            {
                'idPago': row[0],
                'idCredito': row[1],
                'fecha': row[2].strftime('%Y-%m-%d'),
                'cantidad': row[3],
                'idMetodoPago': row[4]
            }
            for row in rows
        ]
    except Exception as e:
        logging.error(f"Ocurrio un error al obtener los pagos: {e}")
        return jsonify({"message": "Error al obtener los pagos"}), 500
    finally:
         cursor.close()
    return jsonify({"message": "Pagos", "pagos": payments}), 200
    

if __name__ == '__main__':
	app.run(host = '0.0.0.0', port=5019, debug = True)

