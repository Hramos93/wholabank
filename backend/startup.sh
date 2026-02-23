#!/bin/bash
# Script de inicio robusto para Azure App Service

# Obtiene el directorio donde se encuentra este script (que es 'backend')
# y cambia el directorio de trabajo a ese lugar.
# Esto hace que el script funcione sin importar desde dónde se le llame.
SCRIPT_DIR=$(dirname "$0")
cd "$SCRIPT_DIR" || exit

echo "Cambiado al directorio: $(pwd)"

# Ejecuta las migraciones de la base de datos
# Se asegura de que la base de datos esté actualizada con el esquema más reciente.
python manage.py migrate --noinput

# --- MANEJO DE ARCHIVOS ESTÁTICOS (FRONTEND) ---

# 1. Verificar que los archivos del frontend existen antes de continuar.
FRONTEND_ASSETS_DIR="../frontend/dist/assets"
echo "Verificando el directorio de assets del frontend: $FRONTEND_ASSETS_DIR"
if [ ! -d "$FRONTEND_ASSETS_DIR" ] || [ -z "$(ls -A $FRONTEND_ASSETS_DIR)" ]; then
    echo "Error: El directorio de assets del frontend ($FRONTEND_ASSETS_DIR) no existe o está vacío."
    echo "Asegúrate de que el build del frontend (ej. 'npm run build') se haya completado antes de desplegar."
    exit 1
fi
echo "Directorio de assets del frontend encontrado."

# 2. Recolecta todos los archivos estáticos (React, etc.) en la carpeta STATIC_ROOT
echo "Iniciando collectstatic..."
python manage.py collectstatic --noinput --clear || {
    echo "Error: collectstatic falló."
    exit 1
}
echo "collectstatic completado. Contenido de STATIC_ROOT:"
ls -lR staticfiles/ # Lista el contenido de la carpeta staticfiles de forma recursiva

# Crea el superusuario (el script interno comprueba si ya existe)
python manage.py create_superuser

# Inicia el servidor Gunicorn
# El directorio de trabajo ya es 'backend', por lo que Gunicorn encontrará 'config.wsgi'.
# Se recomienda usar workers de tipo 'gthread' para operaciones I/O y configurar el número de workers.
# WEB_CONCURRENCY es una variable que Azure puede establecer. Si no, usamos un valor por defecto.
# Para un plan B1/S1 de Azure (1 core), 3 workers es un buen comienzo.
gunicorn config.wsgi:application --bind 0.0.0.0:8000 \
    --workers ${WEB_CONCURRENCY:-3} \
    --threads 4 \
    --worker-class=gthread \
    --log-level=info