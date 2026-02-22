#!/bin/bash
# Script de inicio robusto para Azure App Service

# Obtiene el directorio donde se encuentra este script (que es 'backend')
# y cambia el directorio de trabajo a ese lugar.
# Esto hace que el script funcione sin importar desde dónde se le llame.
SCRIPT_DIR=$(dirname "$0")
cd "$SCRIPT_DIR" || exit

echo "Cambiado al directorio: $(pwd)"

# Ejecuta las migraciones de la base de datos
python manage.py migrate --noinput

# Crea el superusuario (el script interno comprueba si ya existe)
python manage.py create_superuser

# Inicia el servidor Gunicorn
# El directorio de trabajo ya es 'backend', por lo que Gunicorn encontrará 'config.wsgi'.
gunicorn config.wsgi:application --bind 0.0.0.0:8000