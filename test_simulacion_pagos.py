import requests
import random
import string
import time

# URL de Producción (Azure)
BASE_URL = "https://wholabank-app-fghqdsdrb5f6a4bw.canadacentral-01.azurewebsites.net/api"
# BASE_URL = "http://127.0.0.1:8000/api" # Descomentar para pruebas locales

def random_str(length=6):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def run_audit():
    print("=== INICIANDO AUDITORÍA DE PAGOS WHOLABANK ===")
    
    # 1. REGISTRAR COMERCIO (Para recibir los pagos)
    rif_comercio = f"J-{random.randint(10000000, 99999999)}-0"
    codigo_comercio = f"C-{rif_comercio}"
    print(f"\n[1] Registrando Comercio (Destino): {rif_comercio}")
    
    requests.post(f"{BASE_URL}/registro/", json={
        "username": f"comercio_{random_str()}",
        "email": f"comercio_{random_str()}@test.com",
        "password": "TestPassword123!",
        "nombre_completo": "Tienda de Prueba SA",
        "tipo_persona": "JURIDICO",
        "rif": rif_comercio,
        "telefono": "02125555555"
    })

    # 2. REGISTRAR CLIENTE (Quien paga)
    username_cliente = f"cliente_{random_str()}"
    password_cliente = "TestPassword123!"
    print(f"[2] Registrando Cliente (Origen): {username_cliente}")
    
    resp_registro = requests.post(f"{BASE_URL}/registro/", json={
        "username": username_cliente,
        "email": f"{username_cliente}@test.com",
        "password": password_cliente,
        "nombre_completo": "Juan Perez",
        "tipo_persona": "NATURAL",
        "cedula": str(random.randint(10000000, 29999999)),
        "telefono": "04145555555"
    })
    
    if resp_registro.status_code != 201:
        print("Error registrando cliente:", resp_registro.text)
        return

    # 3. LOGIN PARA OBTENER DATOS DE TARJETA (CVV)
    print("[3] Iniciando sesión para obtener credenciales de tarjeta...")
    resp_login = requests.post(f"{BASE_URL}/token/", json={
        "username": username_cliente,
        "password": password_cliente
    })
    token = resp_login.json()['access']
    
    # Obtener Dashboard
    headers = {"Authorization": f"Bearer {token}"}
    resp_dash = requests.get(f"{BASE_URL}/dashboard/", headers=headers)
    data_dash = resp_dash.json()
    
    cuenta = data_dash['cuentas'][0]
    tarjeta = cuenta['tarjetas'][0]
    
    print(f"    > Tarjeta: {tarjeta['numero']}")
    print(f"    > CVV: {tarjeta['cvv']}")
    print(f"    > Saldo Inicial: {cuenta['saldo']}")

    # 4. EJECUTAR 5 COMPRAS ALEATORIAS
    print("\n[4] Ejecutando 5 compras aleatorias...")
    total_gastado = 0.0
    
    for i in range(1, 6):
        monto = round(random.uniform(10.00, 50.00), 2)
        payload_pago = {
            "numero_transaccion": f"TXN-{random_str()}",
            "codigo_banco_emisor_tarjeta": "0001", # Asumiendo que es nuestro banco
            "numero_tarjeta": tarjeta['numero'],
            "cvc_tarjeta": tarjeta['cvv'],
            "fecha_vencimiento_tarjeta": tarjeta['fecha_vencimiento'],
            "codigo_banco_comercio_receptor": "0001",
            "codigo_identificador_comercio_receptor": codigo_comercio,
            "monto_pagado": monto
        }
        
        resp_pago = requests.post(f"{BASE_URL}/procesar_pago/", json=payload_pago)
        
        if resp_pago.status_code == 201:
            print(f"    Compra #{i}: -${monto} [EXITOSA]")
            total_gastado += monto
        else:
            print(f"    Compra #{i}: FALLIDA ({resp_pago.status_code}) - {resp_pago.text}")

    # 5. VERIFICACIÓN FINAL
    print("\n[5] Verificando saldo final...")
    # Refrescamos dashboard
    resp_dash_final = requests.get(f"{BASE_URL}/dashboard/", headers=headers)
    saldo_final_real = float(resp_dash_final.json()['cuentas'][0]['saldo'])
    
    saldo_inicial = 1000.00
    saldo_esperado = round(saldo_inicial - total_gastado, 2)
    
    print(f"    --------------------------------")
    print(f"    Saldo Inicial:   ${saldo_inicial}")
    print(f"    Total Gastado:   ${round(total_gastado, 2)}")
    print(f"    Saldo Esperado:  ${saldo_esperado}")
    print(f"    Saldo Real:      ${saldo_final_real}")
    print(f"    --------------------------------")
    
    if abs(saldo_final_real - saldo_esperado) < 0.01:
        print("✅ AUDITORÍA APROBADA: El saldo coincide perfectamente.")
    else:
        print("❌ AUDITORÍA FALLIDA: Discrepancia en el saldo.")

if __name__ == "__main__":
    run_audit()