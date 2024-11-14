from flask import Flask, Response, jsonify, request, abort
from flask_jwt_extended import jwt_required
from flask_cors import CORS
import logging

import sys
sys.path.append('/home/ec2-user/Proyecto/Svelte/Services')

from df_config import init_oracle
from datetime import datetime
from jwt_settings import init_config
from error_handlers import function_error_handler

app = Flask(__name__)
CORS(app)
jwt = init_config(app)
function_error_handler(app)

connection = init_oracle(app)

@app.route('/api/historial-credito/<int:historial_id>', methods=['PUT'])
@jwt_required()
def update_credit_history(historial_id):
    data = request.get_json()

    _today = datetime.now().strftime('%Y-%m-%d')
    
    cursor = connection.cursor()    
    query = """
    UPDATE HISTORIALESCREDITICIOS SET
        FECHACONSULTA = TO_DATE(:fechaConsulta, 'YYYY-MM-DD'),
        FECHAINICIO = TO_DATE(:fechaInicio, 'YYYY-MM-DD'),
        FECHAFIN = TO_DATE(:fechaFin, 'YYYY-MM-DD'),
        NUMEROCREDITOSPAGADOS = :numeroCreditosPagados,
        NUMEROCREDITOSATRASADOS = :numeroCreditosAtrasados
    WHERE IDHISTORIAL = :idHistorial
    """

    ## ¿EL historial existe?
    query2 = """
    SELECT IDHISTORIAL FROM HISTORIALESCREDITICIOS WHERE IDHISTORIAL = :idHistorial
    """
    try:
        cursor.execute(query2, {'idHistorial': historial_id})
        historialExist = cursor.fetchone()
        if not historialExist:
            return jsonify({"message": "El historial no existe"}), 404
    except Exception as e:        
        logging.error(f"Error al verificar el historial: {e}")
        return jsonify({"message": "Error al verificar el historial"}), 500
    
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
    
    ## Damos formato a las fechas
    try:
        fechaInicio = datetime.strptime(data['fechaInicio'], '%Y-%m-%d').strftime('%Y-%m-%d')
        fechaFin = datetime.strptime(data['fechaFin'], '%Y-%m-%d').strftime('%Y-%m-%d')
    except ValueError as ve:
        logging.error(f"Error al convertir las fechas: {ve}")
        return jsonify({"message": "Formato de fecha inválido"}), 400

    ## Fecha de consulta será la fecha actual
    params = {
        'idHistorial': historial_id,
        'fechaConsulta': _today,
        'fechaInicio': fechaInicio,
        'fechaFin': fechaFin,
        'numeroCreditosPagados': numeroCreditosPagados,
        'numeroCreditosAtrasados': numeroCreditosAtrasados
    }

    try:
        cursor.execute(query, params)
        connection.commit()
        return jsonify({"message": "Historial crediticio modificado", "idHistorial": historial_id}), 201
    except Exception as e:
        logging.error(f"Error al modificar el historial: {e}")
        return jsonify({"message": "Error al modificar el historial"}), 500
    finally:
         cursor.close()
    

if __name__ == '__main__':
	app.run(host = '0.0.0.0', port=5011, debug = True)

