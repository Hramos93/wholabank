# backend/core_bancario/admin.py
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from .models import Cliente, Cuenta, Tarjeta, Directorio, Comercio, Transaccion, AdminDashboardProxy

# Registramos el modelo Cliente con personalización
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('get_identidad', 'user', 'tipo_persona', 'is_comercio_afiliado', 'created_at')
    search_fields = ('cedula', 'rif', 'user__username', 'user__first_name')
    list_filter = ('tipo_persona',)

    def get_identidad(self, obj):
        return obj.rif or obj.cedula
    get_identidad.short_description = 'Identidad (RIF/Cédula)'

    @admin.display(description='Comercio Afiliado', boolean=True)
    def is_comercio_afiliado(self, obj):
        """ Chequea si el cliente (si es jurídico) tiene un perfil de comercio asociado a alguna de sus cuentas. """
        if obj.tipo_persona == 'JURIDICO':
            # Un cliente puede tener varias cuentas, buscamos si alguna está asociada a un comercio.
            return Comercio.objects.filter(cuenta__cliente=obj).exists()
        return False

# Registramos el modelo Cuenta
@admin.register(Cuenta)
class CuentaAdmin(admin.ModelAdmin):
    list_display = ('numero_cuenta', 'cliente', 'saldo', 'created_at')
    # search_fields: Buscar por número de cuenta o cédula del dueño
    search_fields = ('numero_cuenta', 'cliente__cedula')
    # list_filter: Filtro lateral (útil si quisieras filtrar por rangos de fecha, etc)
    list_filter = ('created_at',)

# Registramos el modelo Tarjeta
@admin.register(Tarjeta)
class TarjetaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'cuenta', 'fecha_vencimiento', 'estado')
    # list_filter: Filtro lateral para ver rápido tarjetas Bloqueadas vs Activas
    list_filter = ('estado', 'fecha_vencimiento')
    search_fields = ('numero',)

@admin.register(Directorio)
class DirectorioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'tipo', 'api_url')
    list_filter = ('tipo',)

@admin.register(Comercio)
class ComercioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo_identificador', 'cuenta', 'activo')

@admin.register(Transaccion)
class TransaccionAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'monto', 'estado', 'fecha', 'codigo_respuesta')
    list_filter = ('estado', 'tipo')

# --- REGISTRO DEL PROXY PARA EL BOTÓN DEL DASHBOARD ---
@admin.register(AdminDashboardProxy)
class AdminDashboardProxyAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        # Redirigimos al usuario a la URL de nuestra vista de DRF 'admin_panel'
        return HttpResponseRedirect(reverse('admin_panel'))