import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    """
    Comando para crear un superusuario de forma no interactiva,
    leyendo las credenciales desde las variables de entorno.
    Ideal para despliegues en Render.
    """
    help = 'Crea un superusuario usando las variables de entorno DJANGO_SUPERUSER_*'

    def handle(self, *args, **options):
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not all([username, email, password]):
            self.stdout.write(self.style.ERROR('Faltan variables de entorno requeridas (DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, DJANGO_SUPERUSER_PASSWORD)'))
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f"El superusuario '{username}' ya existe. Omitiendo creación."))
        else:
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f"Superusuario '{username}' creado exitosamente."))