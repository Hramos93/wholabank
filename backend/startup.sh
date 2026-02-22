#!/bin/bash
# Script de inicio robusto para Azure App Service

# Obtiene el directorio donde se encuentra este script (que es 'backend')
# y cambia el directorio de trabajo a ese lugar.
# Esto hace que el script funcione sin importar desde dónde se le llame.
SCRIPT_DIR=$(dirname "$0")
cd "$SCRIPT_DIR" || exit

echo "Cambiado al directorio: $(pwd)"

# Ejecuta las migraciones de la base de datos
# Intenta aplicar las migraciones. Si falla, intenta "fake" la migración problemática.
python manage.py migrate --noinput
MIGRATE_STATUS=$?

if [ $MIGRATE_STATUS -ne 0 ]; then
    echo "Error al aplicar migraciones (código de salida: $MIGRATE_STATUS). Intentando faking de core_bancario.0002_directorio_rif..."
    # Asumiendo que '0002_directorio_rif' es la migración que falla por columna duplicada.
    # Esto marca la migración como aplicada sin ejecutar el SQL.
    python manage.py migrate core_bancario 0002_directorio_rif --fake || {
        echo "Fallo al faking de core_bancario.0002_directorio_rif. Reintentando todas las migraciones."
        python manage.py migrate --noinput
    }
fi

# Recolecta todos los archivos estáticos (React, etc.) en la carpeta STATIC_ROOT y verifica el éxito
echo "Iniciando collectstatic..."
python manage.py collectstatic --noinput || {
    echo "Error: collectstatic falló. Asegúrate de que el build de React se haya ejecutado correctamente."
    exit 1
}
echo "collectstatic completado. Contenido de STATIC_ROOT:"
ls -la staticfiles/ # Lista el contenido de la carpeta staticfiles dentro del directorio 'backend'

# Crea el superusuario (el script interno comprueba si ya existe)
python manage.py create_superuser

# Inicia el servidor Gunicorn
# El directorio de trabajo ya es 'backend', por lo que Gunicorn encontrará 'config.wsgi'.
gunicorn config.wsgi:application --bind 0.0.0.0:8000