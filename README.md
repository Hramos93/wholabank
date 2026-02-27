# WholaBank - Plataforma Bancaria & API Interbancaria

Este proyecto implementa el núcleo bancario ("Core Bancario") para la plataforma **WholaBank**. Está diseñado para operar en la nube de **Azure App Service**, utilizando **Django** como backend y sirviendo una aplicación **React** como frontend.

El sistema maneja la gestión de clientes, cuentas, tarjetas de crédito/débito y posee un motor transaccional capaz de procesar pagos internos ("On-Us") y enrutar pagos externos a otros bancos ("Off-Us") mediante una arquitectura de API distribuida.

---

## 1. Arquitectura del Sistema

### Backend (Django REST Framework)
El backend expone una API RESTful segura que maneja toda la lógica de negocio.
*   **Autenticación:** JWT (JSON Web Tokens) vía `rest_framework_simplejwt`.
*   **Base de Datos:** PostgreSQL en producción (Azure) y SQLite en desarrollo.
*   **Servidor Web:** Gunicorn con `whitenoise` para servir archivos estáticos.

### Frontend (React)
La aplicación React se compila (`npm run build`) y los archivos estáticos resultantes son servidos directamente por Django.
*   **Integración:** Django utiliza `TemplateView` para servir el `index.html` de React en cualquier ruta no capturada por la API, permitiendo el manejo de rutas del lado del cliente (React Router).

### Infraestructura (Azure)
*   **Startup Script (`startup.sh`):** Gestiona el ciclo de vida del contenedor.
*   **Warm-up (`warmup.sh`):** Script de calentamiento que asegura que la aplicación esté lista antes de recibir tráfico real.

---

## 2. Lógica de Negocio y Flujos Principales

### A. Registro de Clientes (Cascada de Creación)
El proceso de registro (`RegistroClienteView` y `RegistroClienteSerializer`) es transaccional y atómico. Al registrarse un usuario, ocurren los siguientes eventos automáticamente:

1.  **Usuario (Auth):** Se crea el usuario en el sistema de autenticación de Django.
2.  **Perfil de Cliente:**
    *   **Persona Natural:** Se valida y registra la Cédula.
    *   **Persona Jurídica:** Se valida el RIF.
3.  **Cuenta Bancaria:**
    *   Se genera un **Número de Cuenta** único siguiendo el estándar bancario (Código Banco + Agencia + Dígitos Aleatorios).
    *   **Saldo Inicial:** Se asigna automáticamente un saldo de bienvenida de **$1,000.00** (definido por `default=1000.00` en el modelo y confirmado en el serializador).
4.  **Tarjeta de Débito/Crédito:**
    *   Se genera una tarjeta vinculada a la cuenta.
    *   **PAN (Número):** Generado bajo norma ISO/IEC 7812 (BIN del Banco + Cuenta + Dígito Verificador).
    *   **Seguridad:** Se generan CVV y Fecha de Vencimiento (5 años).
5.  **Transacción de Bono:** Se inserta un registro en el historial de transacciones (`Transaccion`) documentando el abono de los $1,000.00 como "Bono de Bienvenida".
6.  **Afiliación Comercial (Solo Jurídicos):** Si el cliente es una empresa, se crea automáticamente un perfil de `Comercio`, permitiéndole recibir pagos a través de la API de puntos de venta.

### B. Motor Transaccional (Pagos)
El sistema actúa en dos roles fundamentales dentro del ecosistema bancario:

#### 1. Rol Adquirente (Procesar Pago - `ProcesarPagoComercioView`)
Este endpoint simula un Datáfono (POS). Recibe los datos de una tarjeta y decide cómo procesarla:

*   **Validación de Comercio:** Verifica que el comercio receptor exista y esté activo en WholaBank.
*   **Enrutamiento (Routing):**
    *   **Caso "On-Us" (Mismo Banco):** Si el BIN de la tarjeta coincide con `MI_CODIGO_BANCO`, la transacción se procesa internamente:
        1.  Valida existencia de tarjeta, estado (activa/bloqueada), CVV y saldo suficiente.
        2.  Ejecuta una transacción atómica: Debita al Cliente -> Acredita al Comercio.
    *   **Caso "Off-Us" (Otro Banco):** Si el BIN pertenece a otro banco:
        1.  Busca la URL del banco destino en el modelo `Directorio`.
        2.  Reenvía la solicitud al endpoint `autorizar_pago/` del banco emisor.
        3.  Si el banco emisor aprueba (201 Created), WholaBank acredita el dinero a su comercio cliente.

#### 2. Rol Emisor (Autorizar Pago - `AutorizarPagoBancoView`)
Este endpoint es consumido por **otros bancos**.
*   Recibe una solicitud de débito para una tarjeta de WholaBank.
*   Valida las credenciales de la tarjeta (Número, CVV, Expiración) y el saldo disponible.
*   Si todo es correcto, debita la cuenta del cliente local y responde con éxito (`201 Created`) al banco solicitante.

---

## 3. Modelos de Datos (`core_bancario/models.py`)

*   **Cliente:** Extensión del usuario con datos demográficos (Cédula, RIF, Teléfono). Maneja la distinción Natural/Jurídico.
*   **Cuenta:** Almacena el saldo y el número de cuenta. Posee lógica personalizada en `save()` para garantizar la unicidad del número de cuenta.
*   **Tarjeta:** Vinculada a una cuenta. Genera automáticamente su numeración de 16 dígitos y CVV al crearse.
*   **Directorio:** Tabla de enrutamiento. Contiene los `api_url` y códigos de otros bancos aliados. Es vital para la interoperabilidad.
*   **Comercio:** Vincula una cuenta bancaria con un código de afiliación comercial (para recibir pagos).
*   **Transaccion:** Bitácora inmutable de todas las operaciones financieras (Aprobadas o Rechazadas).

---

## 4. Configuración de Despliegue y Scripts

### `backend/startup.sh`
Script de entrada para el contenedor de Azure. Realiza las siguientes tareas críticas en orden:
1.  **Migraciones:** Ejecuta `makemigrations` y `migrate` para asegurar que el esquema de BD (incluyendo el default de saldo) esté sincronizado.
2.  **Archivos Estáticos:** Ejecuta `collectstatic` para preparar los assets de React y Django Admin.
3.  **Superusuario:** Crea un superusuario de administración si no existe.
4.  **Gunicorn:** Inicia el servidor de aplicaciones con la bandera `--preload` para cargar la app en memoria antes de recibir peticiones.
5.  **Warm-up:** Ejecuta el script de calentamiento en segundo plano.

### `warmup.sh`
Script de bash diseñado para mitigar los tiempos de arranque en frío (Cold Starts) y la carga de modelos pesados.
*   Realiza un bucle (`curl`) contra el endpoint `/api/health/`.
*   Espera hasta recibir un código HTTP **200 OK**.
*   Esto garantiza que Azure no dirija tráfico de usuarios hasta que la aplicación esté 100% operativa.

### `backend/config/settings.py`
*   **CORS:** Configurado dinámicamente. En producción, solo permite peticiones desde el dominio de Azure (`wholabank-app...`).
*   **Base de Datos:** Usa `dj_database_url` con `CONN_MAX_AGE=600` (10 minutos) para mantener conexiones persistentes a PostgreSQL y reducir latencia.
*   **Seguridad:** `DEBUG` se desactiva en producción. `ALLOWED_HOSTS` incluye dinámicamente el hostname de Azure.

---

## 5. API Endpoints Clave

| Método | Endpoint | Descripción | Permisos |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/dashboard/` | Obtiene saldo, cuentas y tarjetas del usuario logueado. | `IsAuthenticated` |
| `POST` | `/api/registro/` | Registra nuevo cliente, crea cuenta, tarjeta y abona bono. | `AllowAny` |
| `POST` | `/api/procesar_pago/` | Endpoint para Datáfonos (Simula compra). | Público (Simulado) |
| `POST` | `/api/autorizar_pago/` | Endpoint para comunicación Interbancaria (B2B). | Público (Validado por lógica) |
| `GET` | `/api/admin-panel/` | Estadísticas globales para el administrador del banco. | `IsAdminUser` |
| `GET` | `/api/health/` | Health check para balanceadores de carga y scripts de warm-up. | Público |

---

## 6. Variables de Entorno Requeridas

Para el correcto funcionamiento en Azure, se deben configurar:

*   `DJANGO_ENV`: `production`
*   `SECRET_KEY`: Llave secreta de Django.
*   `DATABASE_URL`: String de conexión a PostgreSQL.
*   `MI_CODIGO_BANCO`: Identificador único del banco (ej: "0001").
*   `MI_BIN_TARJETA`: Primeros 5 dígitos de las tarjetas (ej: "00001").
*   `WEBSITE_HOSTNAME`: (Provisto por Azure) Host de la aplicación.