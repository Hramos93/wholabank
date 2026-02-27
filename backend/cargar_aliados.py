import csv
import os
import django

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core_bancario.models import Directorio
from core_bancario.serializers import RegistroClienteSerializer
from django.db import transaction

def cargar_datos():
    # Validación: Si ya existen registros en el Directorio, no ejecutamos la carga masiva.
    if Directorio.objects.exists():
        print("ℹ️ La tabla Directorio no está vacía. Se omite la carga masiva inicial.")
        return

    csv_file = 'directorio.csv'
    if not os.path.exists(csv_file):
        print(f"Error: No se encuentra el archivo {csv_file}")
        return

    with open(csv_file, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                with transaction.atomic():
                    # 1. SI ES BANCO: Solo registro en el Directorio
                    if row['tipo'] == 'BANCO':
                        Directorio.objects.update_or_create(
                            codigo=row['codigo'],
                            defaults={
                                'nombre': row['nombre'],
                                'tipo': 'BANCO',
                                'api_url': row['api_url'],
                                'rif': row['rif']
                            }
                        )
                        print(f"✅ Banco registrado: {row['nombre']}")

                    # 2. SI ES COMERCIO: Crear Usuario, Cuenta ($1000) y Afiliación
                    elif row['tipo'] == 'COMERCIO':
                        # Datos inventados para completar el registro (según serializers.py)
                        datos_registro = {
                            'username': row['nombre'].lower().replace(" ", "_"),
                            'email': f"contacto@{row['nombre'].lower().replace(' ', '')}.com",
                            'password': f"{row['codigo']}Test2026.",
                            'nombre_completo': row['nombre'],
                            'tipo_persona': 'JURIDICO',
                            'rif': row['rif'],
                            'telefono': '04140000000', # Inventado
                            'fecha_nacimiento': '2020-01-01', # Fecha Const. inventada
                            'profesion': 'Ventas Retail',
                            'tipo_cuenta': 'CORRIENTE'
                        }

                        # Usamos el serializador para disparar toda la lógica automática
                        serializer = RegistroClienteSerializer(data=datos_registro)
                        if serializer.is_valid():
                            serializer.save()
                            
                            # También lo agregamos al Directorio para enrutamiento
                            Directorio.objects.update_or_create(
                                codigo=row['codigo'],
                                defaults={
                                    'nombre': row['nombre'],
                                    'tipo': 'COMERCIO',
                                    'api_url': row['api_url'],
                                    'rif': row['rif']
                                }
                            )
                            print(f"✅ Comercio y Cuenta ($1000) creados: {row['nombre']}")
                        else:
                            print(f"❌ Error validando {row['nombre']}: {serializer.errors}")

            except Exception as e:
                print(f"⚠️ Error procesando {row['nombre']}: {str(e)}")

if __name__ == "__main__":
    cargar_datos()