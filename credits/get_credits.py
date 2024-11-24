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

@app.route('/api/creditos', methods=['GET'])
@jwt_required()
def get_credits():
    cursor = connection.cursor()
    # query = """SELECT * FROM CREDITOS"""
    query = """SELECT * FROM (SELECT * FROM CREDITOS ORDER BY dbms_random.value) WHERE ROWNUM <= 4"""
    try:
         
        cursor.execute(query)
        rows = cursor.fetchall()
        credits = [
            {
                "IDCREDITO": row[0],
                "IDCLIENTE": row[1],
                "LIMITECREDITO": row[2],
                "FECHAVENCIMIENTO": row[3].strftime('%Y-%m-%d'),
                "STATUS": row[4]
            }
            for row in rows
        ]
        return jsonify({"message": "Credito encontrado", "creditos": credits}), 200
    except Exception as e:
        logging.error(f"Ocurrio un error al obtener el credito: {e}")
        return jsonify({"message": "Error al obtener el credito"}), 500
    finally:
         cursor.close()
    

if __name__ == '__main__':
	app.run(host = '0.0.0.0', port=5013, debug = True)

