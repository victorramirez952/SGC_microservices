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


## Función para saber si un cliente existe
def client_exist(client_id):
    found = False
    cursor = connection.cursor()
    query = """
    SELECT IDCLIENTE FROM CLIENTES WHERE IDCLIENTE = :client_id
    """
    try:
        cursor.execute(query, {'client_id': client_id})
        clientExist = cursor.fetchone()
        if not clientExist:
            found = False
        else:
            found = True
    except Exception as e:
        logging.error(f"Error al buscar el cliente: {e}")
        found = False
    finally:
         cursor.close()
    return found

@app.route('/api/reportes/actividad', methods=['POST'])
@jwt_required()
def create_financial_activity_report():
    data = request.get_json()

    
    if not client_exist(data['idCliente']):
        return jsonify({"message": "El cliente no existe"}), 404
    
    cursor = connection.cursor()

    queryCreditos = """
    SELECT IDCREDITO, LIMITECREDITO, FECHAVENCIMIENTO, STATUS FROM creditos WHERE IDCLIENTE = :client_id
    """
    
    queryPagos = """
    SELECT IDPAGO, IDCREDITO, FECHA, CANTIDAD, IDMETODOPAGO FROM pagos WHERE IDCREDITO IN (SELECT IDCREDITO FROM CREDITOS WHERE IDCLIENTE = :client_id)
    """

    try:
        cursor.execute(queryCreditos, {'client_id': data['idCliente']})
        rowsCreditos = cursor.fetchall()
        creditos = [
            {
                "idCredito": row[0],
                "limiteCredito": row[1],
                "fechaVencimiento": row[2].strftime('%Y-%m-%d'),
                "status": row[3]
            }
            for row in rowsCreditos
        ]

        cursor.execute(queryPagos, {'client_id': data['idCliente']})
        rowsPagos = cursor.fetchall()
        pagos = [
            {
                "idPago": row[0],
                "idCredito": row[1],
                "fecha": row[2].strftime('%Y-%m-%d'),
                "cantidad": row[3],
                "idMetodoPago": row[4]
            }
            for row in rowsPagos
        ]

        reporte = {
            "idCliente": data['idCliente'],
            "creditos": creditos,
            "pagos": pagos
        }

        return jsonify({"message": "REporte realizado correctamente", "reporte": reporte}), 201
    except Exception as e:
        logging.error(f"Error al realizar el reporte: {e}")
        return jsonify({"message": "Error al realizar el reporte"}), 500
    finally:
         cursor.close()
    

if __name__ == '__main__':
	app.run(host = '0.0.0.0', port=5022, debug = True)

