#!/bin/bash
# ==============================================================================
# Script de Calentamiento (Warm-up) para WholaBank
# ==============================================================================
#
# Este script sondea el endpoint de salud de la aplicación hasta que devuelve
# un código de estado 200 OK. Esto asegura que la aplicación (incluyendo
# los modelos de ML pesados) esté completamente cargada en memoria y lista
# para servir tráfico antes de que el proceso de despliegue se marque como exitoso.
#
# USO:
# ./warmup.sh
#
# Se usa típicamente en un script de inicio (como startup.sh) después de
# lanzar el servidor Gunicorn en segundo plano.

# URL del endpoint de salud de la API.
# Asegúrate de que esta URL sea accesible desde donde se ejecuta el script. Debe ser la URL interna del servidor.
HEALTH_CHECK_URL="http://localhost:8000/api/health/"

# Configuración del sondeo
MAX_ATTEMPTS=60 # Número máximo de intentos (60 intentos * 5 segundos = 300 segundos = 5 minutos)
SLEEP_INTERVAL=5 # Segundos a esperar entre intentos

echo "--- Iniciando script de calentamiento para WholaBank ---"
echo "URL de sondeo: $HEALTH_CHECK_URL"

# Bucle de sondeo
for i in $(seq 1 $MAX_ATTEMPTS); do
  echo "Intento de sondeo #$i de $MAX_ATTEMPTS..."
  
  # Usamos curl para hacer la petición.
  # -s: Modo silencioso (no muestra barra de progreso)
  # -o /dev/null: Descarta el cuerpo de la respuesta, no nos interesa
  # -w "%{http_code}": Escribe solo el código de estado HTTP a la salida estándar
  HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$HEALTH_CHECK_URL")

  echo "Respuesta del servidor: $HTTP_STATUS"

  # Comprobamos si el código de estado es 200 OK
  if [ "$HTTP_STATUS" -eq 200 ]; then
    echo "¡Éxito! El servidor está listo y respondiendo con 200 OK."
    echo "--- Calentamiento completado ---"
    exit 0 # Salir del script con código de éxito
  else
    echo "El servidor aún no está listo. Esperando $SLEEP_INTERVAL segundos..."
    sleep $SLEEP_INTERVAL
  fi
done

# Si el bucle termina sin un 200 OK, significa que se alcanzó el tiempo máximo.
echo "¡Error! El servidor no respondió con 200 OK después de $MAX_ATTEMPTS intentos."
echo "El proceso de calentamiento ha fallado."
echo "--- Calentamiento fallido ---"
exit 1 # Salir del script con código de error
