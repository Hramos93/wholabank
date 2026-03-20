
from django.core.management.base import BaseCommand
from core_bancario.models import Comercio

class Command(BaseCommand):
    help = 'Removes the "C-" prefix from the codigo_identificador of all Comercio objects.'

    def handle(self, *args, **options):
        self.stdout.write('Starting the process of fixing codigo_identificador...')
        
        comercios = Comercio.objects.all()
        updated_count = 0
        
        for comercio in comercios:
            if comercio.codigo_identificador.startswith('C-'):
                comercio.codigo_identificador = comercio.codigo_identificador[2:]
                comercio.save()
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f'Updated comercio: {comercio.nombre}'))
        
        self.stdout.write(self.style.SUCCESS(f'Process finished. {updated_count} comercio objects were updated.'))
