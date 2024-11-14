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

@app.route('/api/historial-credito/<int:historial_id>', methods=['DELETE'])
@jwt_required()
def delete_credit_history(historial_id):
    cursor = connection.cursor()
    query = """
    DELETE FROM HISTORIALESCREDITICIOS WHERE IDHISTORIAL = :idHistorial
    """

    try:
        cursor.execute(query, {'idHistorial': historial_id})
        connection.commit()
        if cursor.rowcount == 0:
            return jsonify({"message": "Historial crediticio no encontrado"}), 404
    except Exception as e:
        logging.error(f"Error al eliminar el historial crediticio: {e}")
        return jsonify({"message": "Error al eliminar el historial crediticio"}), 500
    finally:
         cursor.close()
    return jsonify({"message": "Historial eliminado"}), 200
    

if __name__ == '__main__':
	app.run(host = '0.0.0.0', port=5012, debug = True)
