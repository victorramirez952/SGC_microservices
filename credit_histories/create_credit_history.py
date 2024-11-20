from flask import Flask, Response, jsonify, request, abort
from flask_jwt_extended import jwt_required
from flask_cors import CORS
import logging
from datetime import datetime

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

@app.route('/api/historial-credito', methods=['POST'])
@jwt_required()
def create_credit_history():
    data = request.get_json()

    _today = datetime.now().strftime('%Y-%m-%d')
    #Obtener atributos del cliente
    cursor = connection.cursor()
    query = """
    INSERT INTO HISTORIALESCREDITICIOS
    (IDHISTORIAL, IDCLIENTE, FECHACONSULTA, FECHAINICIO, FECHAFIN, NUMEROCREDITOSPAGADOS, NUMEROCREDITOSATRASADOS)
    VALUES
    (:idHistorial, :idCliente, TO_DATE(:fechaConsulta, 'YYYY-MM-DD'), TO_DATE(:fechaInicio, 'YYYY-MM-DD'), TO_DATE(:fechaFin, 'YYYY-MM-DD'), :numeroCreditosPagados, :numeroCreditosAtrasados)
    """

    maxIdHistory = 0
    query2 = """
    SELECT MAX(IDHISTORIAL) FROM HISTORIALESCREDITICIOS
    """
    try:
        cursor.execute(query2)
        maxIdHistory = cursor.fetchone()[0]
    except Exception as e:
        logging.error(f"Error al obtener el ID máximo de los historiales: {e}")
        return jsonify({"message": "Error al obtener el ID máximo de los historiales"}), 500
    
    ## ¿El cliente existe?
    query3 = """
    SELECT IDCLIENTE FROM CLIENTES WHERE IDCLIENTE = :idCliente
    """
    try:
        cursor.execute(query3, {'idCliente': data['idCliente']})
        clientExist = cursor.fetchone()
        if not clientExist:
            return jsonify({"message": "El cliente no existe"}), 404
    except Exception as e:
        logging.error(f"Error al verificar el cliente: {e}")
        return jsonify({"message": "Error al verificar el cliente"}), 500
    
    ## Número de creditos atrasados (Creditos.idCliente == HistorialesCrediticios.idCliente) & (Creditos.fechaVencimiento < HistorialesCrediticios.fechaConsulta) & (Creditos.status = 'Activo')
    query4 = """
    SELECT COUNT(*) FROM CREDITOS WHERE IDCLIENTE = :idCliente AND FECHAVENCIMIENTO < :fechaConsulta AND STATUS = 'Activo'
    """
    try:
        cursor.execute(query4, {'idCliente': data['idCliente'], 'fechaConsulta': _today})
        numeroCreditosAtrasados = cursor.fetchone()[0]
    except Exception as e:
        logging.error(f"Error al obtener el número de creditos atrasados: {e}")
        return jsonify({"message": "Error al obtener el número de creditos atrasados"}), 500

    ## Número de creditos pagados (Creditos.idCLiente = :idCliente) & (Creditos.status = 'Inactivo')
    query5 = """
    SELECT COUNT(*) FROM CREDITOS WHERE IDCLIENTE = :idCliente AND STATUS = 'Inactivo'
    """
    try:
        cursor.execute(query5, {'idCliente': data['idCliente']})
        numeroCreditosPagados = cursor.fetchone()[0]
    except Exception as e:
        logging.error(f"Error al obtener el número de creditos pagados: {e}")
        return jsonify({"message": "Error al obtener el número de creditos pagados"}), 500
    
    try:
        fechaInicio = datetime.strptime(data['fechaInicio'], '%Y-%m-%d').strftime('%Y-%m-%d')
        fechaFin = datetime.strptime(data['fechaFin'], '%Y-%m-%d').strftime('%Y-%m-%d')
    except ValueError as ve:
        logging.error(f"Error al convertir las fechas: {ve}")
        return jsonify({"message": "Formato de fecha inválido"}), 400

    ## Fecha de consulta será la fecha actual
    params = {
        'idHistorial': maxIdHistory + 1,
        'idCliente': data['idCliente'],
        'fechaConsulta': _today,
        'fechaInicio': fechaInicio,
        'fechaFin': fechaFin,
        'numeroCreditosPagados': numeroCreditosPagados,
        'numeroCreditosAtrasados': numeroCreditosAtrasados
    }

    try:
        cursor.execute(query, params)
        connection.commit()
        return jsonify({"message": "Historial crediticio registrado", "idHistorial": maxIdHistory + 1}), 201
    except Exception as e:
        logging.error(f"Error al registrar el historial: {e}")
        return jsonify({"message": "Error al registrar el historial"}), 500
    finally:
         cursor.close()
    

if __name__ == '__main__':
	app.run(host = '0.0.0.0', port=5010, debug = True)

