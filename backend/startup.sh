#!/bin/bash

# El script se ejecuta desde la raíz del proyecto.
# Navegamos al directorio 'backend' donde está manage.py.
cd backend

# Ejecuta las migraciones de la base de datos
python manage.py migrate --noinput

# Crea el superusuario (el script interno comprueba si ya existe)
python manage.py create_superuser

# Inicia el servidor Gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000