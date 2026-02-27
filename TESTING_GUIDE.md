# 🏦 Guía de Pruebas: Ecosistema Bancario WholaBank (0001)

Este documento detalla los escenarios de prueba para la API de pagos, validando la lógica de negocio y la integridad de los datos en los diferentes roles que asume el banco.

---

## 📋 Escenario 1: Pago Interno (On-Us)

### Definición
El Cliente y el Comercio pertenecen ambos a WholaBank (`0001`). La transacción se procesa de forma interna sin salir a redes externas.

### 1. Requisitos Previos
*   **Comercio:** Un comercio como `Cachitos Nola` (Código: `C-J-12345678-0`) debe estar registrado y activo en la tabla `Comercio`.
*   **Cliente:** Una tarjeta como `5000012429890140` debe existir, estar activa y tener saldo suficiente (ej. $1000).
*   **Autenticación:** Se debe poseer un Token JWT vigente generado para un usuario de WholaBank.

### 2. Ejecución en Postman
*   **Endpoint:** `POST /api/procesar_pago_comercio/`
*   **Headers:** `Authorization: Bearer <TU_TOKEN_JWT>`
*   **Body:**
    ```json
    {
      "numero_transaccion": "V-INT-001",
      "codigo_banco_emisor_tarjeta": "0001",
      "numero_tarjeta": "5000012429890140",
      "cvc_tarjeta": "CVV_REAL_DE_TU_DB",
      "fecha_vencimiento_tarjeta": "12/29",
      "codigo_banco_comercio_receptor": "0001",
      "codigo_identificador_comercio_receptor": "C-J-12345678-0",
      "monto_pagado": 50.00
    }
    ```

### 3. Resultados Esperados
*   **Respuesta API:** `201 Created`.
*   **Base de Datos:**
    *   Se resta `$50.00` del saldo de la cuenta del cliente.
    *   Se suma `$50.00` al saldo de la cuenta del comercio (`Cachitos Nola`).
    *   Se crea un nuevo registro en la tabla `Transaccion` con estado `APROBADO`.

---

## 🌎 Escenario 2: WholaBank como Banco Adquiriente (Off-Us)

### Definición
El Comercio es cliente de WholaBank, pero la tarjeta del pagador pertenece a un banco externo (ej. Meridian `0002`).

### 1. Roles
*   **Banco Adquiriente (Tú):** Recibes la solicitud de pago de tu comercio y la enrutas hacia el banco emisor.
*   **Banco Emisor (Ellos):** Validan la tarjeta de su cliente y autorizan (o rechazan) el débito.

### 2. Requisitos Previos
*   El banco aliado (ej. Meridian `0002`) debe estar registrado en tu tabla `Directorio` con su URL de API (`api_url`) activa.
*   Debes tener los datos reales de una tarjeta de prueba proporcionada por el banco aliado.

### 3. Ejecución en Postman
La ejecución es idéntica al Escenario 1, pero cambiando el `codigo_banco_emisor_tarjeta` a `0002`. Tu servidor detectará que no es `0001` y disparará la función `enrutar_pago_externo`.

### 4. Resultados Esperados
*   Tu servidor actúa como una "pasarela", enviando una petición `POST` al `api_url` del banco emisor.
*   Si el banco emisor responde `201 Created`, tu sistema acredita el dinero a tu comercio y responde `201 Created` a Postman.

---

## 🛡️ Escenario 3: WholaBank como Banco Emisor (Off-Us)

### Definición
Un cliente de WholaBank realiza una compra en un punto de venta cuyo banco es una entidad externa.

### 1. Roles
*   **Banco Adquiriente (Ellos):** Reciben la tarjeta de tu cliente en su punto de venta y te consultan a ti para autorizar el pago.
*   **Banco Emisor (Tú):** Validas el saldo y la seguridad de la tarjeta de tu cliente y autorizas el débito.

### 2. Ejecución
*   **Endpoint:** El banco aliado te llama a ti al endpoint `/api/autorizar_pago/`.
*   **Seguridad:** El banco aliado debe enviar un Token JWT válido en los `Headers` de su petición. Tu configuración de `permission_classes = [IsAuthenticated]` los rechazará con un `401 Unauthorized` si no lo hacen.

### 3. Resultados Esperados
*   Tu sistema valida el CVV, saldo y estado de la tarjeta de tu cliente.
*   Se debita el monto de la cuenta de tu cliente y se genera un log de auditoría interna (`Transaccion`).
*   Respondes `201 Created` al banco aliado para que ellos puedan acreditar el dinero a su comercio.