#!/bin/bash
# Script de inicio para Azure App Service

# Cambia el directorio de trabajo a la carpeta del script ('backend').
# Esto asegura que los comandos se ejecuten en el contexto correcto.
cd "$(dirname "$0")" || exit

echo "Directorio de trabajo actual: $(pwd)"

# Ejecuta las migraciones de la base de datos para asegurar que el esquema esté actualizado.
echo "Ejecutando migraciones de base de datos..."
# En producción, solo aplicamos migraciones existentes, no las creamos.
python manage.py migrate --noinput

# Ejecuta la carga masiva de aliados (solo si la tabla está vacía, validado internamente).
echo "Verificando carga inicial de aliados..."
python manage.py cargar_directorio

# Recolecta todos los archivos estáticos (React, etc.) en la carpeta STATIC_ROOT.
# La opción --noinput evita prompts y --clear asegura una recolección limpia.
echo "Ejecutando collectstatic..."
python manage.py collectstatic --noinput

# Crea el superusuario (el script interno comprueba si ya existe para no duplicarlo).
echo "Asegurando la existencia del superusuario..."
python manage.py create_superuser

# Inicia el servidor Gunicorn en segundo plano para permitir la ejecución del warmup.
echo "Iniciando servidor Gunicorn en segundo plano..."
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 600 --log-level=info &

# Guarda el PID de Gunicorn para poder esperar por él más tarde.
GUNICORN_PID=$!

# Ejecuta el script de calentamiento.
echo "Ejecutando script de calentamiento..."
/bin/bash ../warmup.sh

# Espera a que Gunicorn termine. Esto es crucial para que el contenedor no se cierre.
echo "Esperando a que Gunicorn finalice..."
wait $GUNICORN_PID
echo "Gunicorn ha finalizado."
