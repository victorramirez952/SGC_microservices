from flask import Flask, Response, jsonify, request, abort
from flask_cors import CORS
import logging
import json
import os

import sys
sys.path.append('/home/ec2-user/Proyecto/Svelte/Services')

from df_config import init_oracle
from datetime import datetime

app = Flask(__name__)
CORS(app)

connection = init_oracle(app)

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    cursor = connection.cursor()
    query = """
    SELECT * FROM USUARIOS WHERE IDUSUARIO = :user_id
    """
    try:
         
        cursor.execute(query, user_id=user_id)
        rows = cursor.fetchall()
        users = [
            {
                "idUsuario": row[0],
                "idCliente": row[1],
                "nombreUsuario": row[2],
                "correo": row[3],
                "password_Hash": row[4].read() if hasattr(row[4], "read") else row[4] 
            }
            for row in rows
        ]
        return jsonify({"message": "Usuario encontrado", "users": users}), 200
    except Exception as e:
        logging.error(f"Ocurrio un error al obtener el usuario: {e}")
        return jsonify({"message": "Error al obtener el usuario"}), 500
    finally:
         cursor.close()
    

if __name__ == '__main__':
	app.run(host = '0.0.0.0', port=5002, debug = True)

