import requests
import random
import string

BASE_URL = "http://127.0.0.1:8000/api"

def random_str(length=6):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def run_test():
    print("=== INICIANDO TEST DE REGISTRO SIMPLE ===")
    
    username_cliente = f"cliente_{random_str()}"
    
    resp_registro = requests.post(f"{BASE_URL}/registro/", json={
        "username": username_cliente,
        "email": f"{username_cliente}@test.com",
        "password": "TestPassword123!",
        "nombre_completo": "Juan Perez",
        "tipo_persona": "NATURAL",
        "cedula": str(random.randint(10000000, 29999999)),
        "telefono": "04145555555"
    })
    
    if resp_registro.status_code == 201:
        print("✅ REGISTRO EXITOSO")
    else:
        print(f"❌ REGISTRO FALLIDO ({resp_registro.status_code}) - {resp_registro.text}")

if __name__ == "__main__":
    run_test()
