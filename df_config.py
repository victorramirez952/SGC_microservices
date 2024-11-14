import os
from dotenv import load_dotenv
import cx_Oracle

load_dotenv()

cx_path = r'/opt/oracle/product/21c/dbhomeXE/lib'

if len(cx_path) > 0:
    cx_Oracle.init_oracle_client(lib_dir=rf"{cx_path}")  

def init_oracle(app):
    app.config['USERNAME'] = os.getenv('USERNAME')
    app.config['PASSWORD'] = os.getenv('PASSWORD')
    app.config['HOSTNAME'] = os.getenv('HOSTNAME')
    app.config['PORT'] = os.getenv('PORT')
    app.config['SERVICE_NAME'] = os.getenv('SERVICE_NAME_ORACLE')

    dsn = cx_Oracle.makedsn(app.config['HOSTNAME'], app.config['PORT'], service_name=app.config['SERVICE_NAME'])
    connection = cx_Oracle.connect(app.config['USERNAME'], app.config['PASSWORD'], dsn, encoding="UTF-8")
    
    return connection

