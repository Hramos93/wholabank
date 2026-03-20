import csv
import os
import random
import re
import django
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import User

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core_bancario.models import Directorio, Cliente, Cuenta, Tarjeta
from core_bancario.serializers import RegistroClienteSerializer

def validar_y_corregir_rif(rif):
    """
    Valida y corrige el RIF para que cumpla con el formato J-99999999-9.
    Si no cumple, genera un nuevo RIF con el formato correcto.
    """
    # Expresión regular para el formato J-99999999-9
    patron_rif = re.compile(r'^J-\d{8,9}-\d$')

    if patron_rif.match(rif):
        return rif
    else:
        # Generar un nuevo RIF con el formato correcto
        nueve_digitos = ''.join(random.choices('0123456789', k=9))
        un_digito = random.randint(1, 9)
        return f"J-{nueve_digitos}-{un_digito}"


class Command(BaseCommand):
    help = 'Carga datos desde directorio.csv, valida/corrige RIFs y crea registros.'

    def handle(self, *args, **options):
        # Validación: Si ya existen registros en el Directorio, no ejecutamos la carga masiva.
        if Directorio.objects.exists():
            self.stdout.write(self.style.SUCCESS("La tabla Directorio no esta vacia. Se omite la carga masiva inicial."))
            return

        csv_file = 'backend/directorio.csv'
        if not os.path.exists(csv_file):
            self.stderr.write(self.style.ERROR(f"Error: No se encuentra el archivo {csv_file}"))
            return

        with open(csv_file, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                print(row.keys())
                try:
                    with transaction.atomic():
                        rif_corregido = validar_y_corregir_rif(row['rif'])

                        # 1. SI ES BANCO: Solo registro en el Directorio
                        if row['tipo'] == 'BANCO':
                            Directorio.objects.update_or_create(
                                codigo=row['codigo'],
                                defaults={
                                    'nombre': row['nombre'],
                                    'tipo': 'BANCO',
                                    'api_url': row['api_url'],
                                    'rif': rif_corregido
                                }
                            )
                            self.stdout.write(self.style.SUCCESS(f"Banco registrado: {row['nombre']}"))

                        # 2. SI ES COMERCIO: Crear Usuario, Cuenta ($1000) y Afiliación
                        elif row['tipo'] == 'COMERCIO':
                            # Datos inventados para completar el registro (según serializers.py)
                            datos_registro = {
                                'username': row['nombre'].lower().replace(" ", "_"),
                                'email': f"contacto@{row['nombre'].lower().replace(' ', '')}.com",
                                'password': f"{row['codigo']}Test2026.",
                                'nombre_completo': row['nombre'], # Asegúrate que este campo exista en tu CSV
                                'tipo_persona': 'JURIDICO',
                                'rif': rif_corregido,
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
                                        'rif': rif_corregido
                                    }
                                )
                                self.stdout.write(self.style.SUCCESS(f"Comercio y Cuenta ($1000) creados: {row['nombre']}"))
                            else:
                                self.stderr.write(self.style.ERROR(f"Error validando {row['nombre']}: {serializer.errors}"))

                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"Error procesando {row['nombre']}: {str(e)}"))
