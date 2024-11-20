import threading
import os

def run_services(file, port):
    """
    Este programa ejecutará cada servicio en un thread por separado
    """
    os.system(f"python {file}.py {port}")

services = [
    {"file": "clients/login", "port": 5001},
    {"file": "clients/get_clients", "port": 5002},
    {"file": "clients/get_client", "port": 5003},
    {"file": "clients/get_client_details", "port": 5004},
    {"file": "clients/create_client", "port": 5005},
    {"file": "clients/update_client", "port": 5006},
    {"file": "clients/delete_client", "port": 5007}
    # {"file": "credit_histories/get_credit_histories", "port": 5008},
    # {"file": "credit_histories/get_credit_history", "port": 5009},
    # {"file": "credit_histories/create_credit_history", "port": 5010},
    # {"file": "credit_histories/update_credit_history", "port": 5011},
    # {"file": "credit_histories/delete_credit_history", "port": 5012},
    # {"file": "credits/get_credits", "port": 5013},
    # {"file": "credits/get_client_credits", "port": 5014},
    # {"file": "credits/create_credit", "port": 5015},
    # {"file": "credits/update_credit", "port": 5016},
    # {"file": "payments/get_payments_history", "port": 5017},
    # {"file": "payments/create_payment", "port": 5018},
    # {"file": "payments/get_payments", "port": 5019},
    # {"file": "reports/report_overdue_credits", "port": 5020},
    # {"file": "reports/report_active_clients", "port": 5021},
    # {"file": "reports/report_financial_activity", "port": 5022},
    # {"file": "reports/report_financial_summary", "port": 5023}
]

threads = []
for service in services:
    # vamos a crear un thread para cada servicio
    thread = threading.Thread(target=run_services, args=(service["file"], service["port"]))
    threads.append(thread)
    thread.start()

## Vamos a esperar a que todos los threads terminen antes de continuar
for thread in threads:
    thread.join()
