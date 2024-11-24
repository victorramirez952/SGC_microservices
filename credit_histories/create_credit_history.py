from flask import Flask, Response, jsonify, request, abort
from flask_jwt_extended import jwt_required
from flask_cors import CORS
from dotenv import load_dotenv
import logging
import os
from datetime import datetime

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

@app.route('/api/historial-credito', methods=['POST'])
@jwt_required()
def create_credit_history():
    try:
        data = request.get_json()
        data = uppercase_keys(data)
        _today = datetime.now().strftime('%d/%m/%y')
        #Obtener atributos del cliente
        cursor = connection.cursor()
        query = """
        INSERT INTO HISTORIALESCREDITOS
        (IDCLIENTE, FECHACONSULTA, FECHAINICIO, FECHAFIN, NUMEROCREDITOSPAGADOS, NUMEROCREDITOSATRASADOS)
        VALUES
        (:IDCLIENTE, TO_DATE(:FECHACONSULTA, 'YYYY-MM-DD'), TO_DATE(:FECHAINICIO, 'YYYY-MM-DD'), TO_DATE(:FECHAFIN, 'YYYY-MM-DD'), :NUMEROCREDITOSPAGADOS, :NUMEROCREDITOSATRASADOS)
        """

        maxIdHistory = 0
        query2 = """
        SELECT MAX(IDHISTORIAL) FROM HISTORIALESCREDITOS
        """
        try:
            cursor.execute(query2)
            result = cursor.fetchone()
            maxIdHistory = 1 if result is None or result[0] is None else result[0]
            print("maxIdHistory", maxIdHistory)
        except Exception as e:
            logging.error(f"Error al obtener el ID máximo de los historiales: {e}")
            return jsonify({"message": "Error al obtener el ID máximo de los historiales"}), 500
            
        
        ## ¿El cliente existe?
        query3 = """
        SELECT IDCLIENTE FROM CLIENTES WHERE IDCLIENTE = :IDCLIENTE
        """
        try:
            cursor.execute(query3, {'IDCLIENTE': data['IDCLIENTE']})
            clientExist = cursor.fetchone()
            if not clientExist:
                return jsonify({"message": "El cliente no existe"}), 404
        except Exception as e:
            logging.error(f"Error al verificar el cliente: {e}")
            return jsonify({"message": "Error al verificar el cliente"}), 500
        
        ## Número de creditos atrasados (Creditos.IDCLIENTE == HISTORIALESCREDITOS.IDCLIENTE) & (Creditos.fechaVencimiento < HISTORIALESCREDITOS.FECHACONSULTA) & (Creditos.status = 'Activo')
        query4 = """
        SELECT COUNT(*) FROM CREDITOS WHERE IDCLIENTE = :IDCLIENTE AND FECHAVENCIMIENTO < :FECHACONSULTA AND STATUS = 'activo'
        """
        try:
            print(f"SELECT COUNT(*) FROM CREDITOS WHERE IDCLIENTE = {data['IDCLIENTE']} AND FECHAVENCIMIENTO < {_today} AND STATUS = 'activo'")
            cursor.execute(query4, {'IDCLIENTE': data['IDCLIENTE'], 'FECHACONSULTA': _today})
            NUMEROCREDITOSATRASADOS = cursor.fetchone()[0]
        except Exception as e:
            logging.error(f"Error al obtener el número de creditos atrasados: {e}")
            return jsonify({"message": "Error al obtener el número de creditos atrasados"}), 500

        ## Número de creditos pagados (Creditos.idCLiente = :IDCLIENTE) & (Creditos.status = 'Inactivo')
        query5 = """
        SELECT COUNT(*) FROM CREDITOS WHERE IDCLIENTE = :IDCLIENTE AND STATUS = 'inactivo'
        """
        try:
            cursor.execute(query5, {'IDCLIENTE': data['IDCLIENTE']})
            NUMEROCREDITOSPAGADOS = cursor.fetchone()[0]
        except Exception as e:
            logging.error(f"Error al obtener el número de creditos pagados: {e}")
            return jsonify({"message": "Error al obtener el número de creditos pagados"}), 500
        
        try:
            FECHAINICIO = datetime.strptime(data['FECHAINICIO'], '%Y-%m-%d').strftime('%Y-%m-%d')
            FECHAFIN = datetime.strptime(data['FECHAFIN'], '%Y-%m-%d').strftime('%Y-%m-%d')
        except ValueError as ve:
            logging.error(f"Error al convertir las fechas: {ve}")
            return jsonify({"message": "Formato de fecha inválido"}), 400

        ## Fecha de consulta será la fecha actual
        # if maxIdHistory
        params = {
            # 'IDHISTORIAL': maxIdHistory + 1,
            'IDCLIENTE': data['IDCLIENTE'],
            'FECHACONSULTA': _today,
            'FECHAINICIO': FECHAINICIO,
            'FECHAFIN': FECHAFIN,
            'NUMEROCREDITOSPAGADOS': NUMEROCREDITOSPAGADOS,
            'NUMEROCREDITOSATRASADOS': NUMEROCREDITOSATRASADOS
        }
        print(params)

        try:
            cursor.execute(query, params)
            connection.commit()
            return jsonify({"message": "Historial crediticio registrado", "IDHISTORIAL": maxIdHistory + 1}), 201
        except Exception as e:
            logging.error(f"Error al registrar el historial: {e}")
            return jsonify({"message": "Error al registrar el historial"}), 500
        finally:
            cursor.close()
    except Exception as e:
        logging.error(f"Error al registrar el historial: {e}")
        return jsonify({"message": "Error al registrar el historial"}), 500
    

if __name__ == '__main__':
	app.run(host = '0.0.0.0', port=5010, debug = True)

