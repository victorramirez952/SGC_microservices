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

@app.route('/')
def inicio():
    return 'raiz de la app'

@app.route('/api/clientes', methods=['GET'])
@jwt_required()
def get_clientes():
    try: 
        cursor = connection.cursor()
        # cursor.execute("SELECT * FROM (SELECT * FROM CLIENTES ORDER BY dbms_random.value) WHERE ROWNUM <= 4")
        cursor.execute("SELECT * FROM CLIENTES ORDER BY IDCLIENTE")
        clientes = cursor.fetchall()

        return jsonify({"message": "Cliente encontrado", "clientes": clientes}), 200
    except Exception as e:
        logging.error(f"Ocurrio un error al obtener los clientes: {e}")
        return jsonify({"message": "Error al obtener los clientes"}), 500
    finally:
        cursor.close()
    

if __name__ == '__main__':
	app.run(host = '0.0.0.0', port=5002, debug = True)

