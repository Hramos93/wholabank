# WholaBank - Plataforma Bancaria Digital

Este proyecto es una simulación de una plataforma bancaria completa, incluyendo un backend con Django Rest Framework y un frontend con React, diseñada para ser desplegada en la nube (Azure).

## Características Principales

*   **Core Bancario**: Gestión de clientes, cuentas y tarjetas.
*   **Transacciones**: Procesamiento de pagos en comercios (rol adquiriente) y autorización de pagos interbancarios (rol emisor).
*   **Autenticación**: Sistema de login basado en JWT (JSON Web Tokens).
*   **Panel de Administración**: Vista personalizada para administradores con métricas clave del banco y gestión del ecosistema.
*   **Frontend Moderno**: Interfaz de usuario con React, incluyendo un Punto de Venta (POS) virtual y paneles de control.

## Despliegue en Producción (Azure)

La aplicación está configurada para un despliegue en servicios como Azure App Service.

### Variables de Entorno Requeridas

Asegúrate de configurar las siguientes variables de entorno en tu servicio de Azure:

```
# Configuración de Django
SECRET_KEY=<Tu_llave_secreta_muy_larga_y_segura>
DJANGO_ENV=production
WEBSITE_HOSTNAME=<Tu_dominio_de_azure_app_service>

# Base de Datos (PostgreSQL recomendado)
DATABASE_URL=postgres://USER:PASSWORD@HOST:PORT/NAME

# Credenciales del Superusuario para el primer despliegue
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=<Una_contraseña_fuerte>

# Configuración del Banco
MI_CODIGO_BANCO=0001
MI_CODIGO_AGENCIA=0001
MI_BIN_TARJETA=00001
INTERBANK_API_KEY=<Llave_secreta_para_comunicacion_entre_bancos>
```

### Comandos de Inicio

Azure App Service debe configurarse para ejecutar los siguientes comandos durante el despliegue:

1.  **Recopilar archivos estáticos**: `python manage.py collectstatic --noinput`
2.  **Aplicar migraciones**: `python manage.py migrate`
3.  **Crear superusuario (solo la primera vez)**: `python manage.py create_superuser`
4.  **Iniciar el servidor Gunicorn**: `gunicorn config.wsgi`