from flask import Flask, Response, jsonify, request, abort
from flask_jwt_extended import jwt_required
from flask_cors import CORS

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

@app.route('/api/clientes/<int:client_id>/detalles', methods=['GET'])
@jwt_required()
def get_cliente(client_id):
    cursor = connection.cursor()
    query = """
    SELECT
        c.IDCLIENTE,
        c.NUMEROCLIENTE,
        c.NOMBRE1,
        c.NOMBRE2,
        c.TELEFONO1,
        c.IDENTIFICACIONFISCAL,
        c.FECHA,
        hc.IDHISTORIAL,
        hc.FECHACONSULTA,
        hc.FECHAINICIO,
        hc.FECHAFIN,
        hc.NUMEROCREDITOSPAGADOS,
        hc.NUMEROCREDITOSATRASADOS
    FROM
        CLIENTES c
    LEFT JOIN
        HISTORIALESCREDITICIOS hc ON c.IDCLIENTE = hc.IDCLIENTE
    WHERE
        c.IDCLIENTE = :client_id
    """
    cursor.execute(query, client_id=client_id)
    rows = cursor.fetchall()
    cursor.close()
    clients = [
         {
              "idCliente": row[0],
              "numeroCliente": row[1],
              "nombre1": row[2],
              "nombre2": row[3],
              "telefono1": row[4],
              "identificacionFiscal": row[5],
              "fecha": row[6].strftime('%Y-%m-%d'),
              "historial": [
                   {
                        "idHistorial": row[7],
                        "fechaConsulta": row[8].strftime('%Y-%m-%d'),
                        "fechaInicio": row[9].strftime('%Y-%m-%d'),
                        "fechaFin": row[10].strftime('%Y-%m-%d'),
                        "numeroCreditosPagados": row[11],
                        "numeroCreditosAtrasados": row[12]
                   }
              ]
         }
         for row in rows
    ]
    return jsonify({"message": "Cliente encontrado", "clients": clients}), 200
    

if __name__ == '__main__':
	app.run(host = '0.0.0.0', port=5004, debug = True)

