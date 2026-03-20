from django.core.management.base import BaseCommand
from django.db import transaction
from core_bancario.models import Directorio, Cliente, Cuenta, Tarjeta, User

class Command(BaseCommand):
    help = 'Limpia las tablas Directorio, Cliente, Cuenta, Tarjeta y User.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Iniciando limpieza de la base de datos...")

        # Limpiar Directorio
        num_deleted, _ = Directorio.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Directorio: {num_deleted} registros eliminados."))

        # Limpiar Tarjetas
        num_deleted, _ = Tarjeta.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Tarjeta: {num_deleted} registros eliminados."))

        # Limpiar Cuentas
        num_deleted, _ = Cuenta.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Cuenta: {num_deleted} registros eliminados."))

        # Limpiar Clientes
        num_deleted, _ = Cliente.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Cliente: {num_deleted} registros eliminados."))

        # Limpiar Usuarios (Excepto superusuarios)
        num_deleted, _ = User.objects.filter(is_superuser=False).delete()
        self.stdout.write(self.style.SUCCESS(f"User (no-superusuarios): {num_deleted} registros eliminados."))

        self.stdout.write(self.style.SUCCESS("Limpieza completada."))
