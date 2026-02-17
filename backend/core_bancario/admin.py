# backend/core_bancario/admin.py
from django.contrib import admin
from .models import Cliente, Cuenta, Tarjeta, Directorio, Comercio, Transaccion

# Registramos el modelo Cliente con personalización
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    # list_display: Qué columnas verás en la tabla
    list_display = ('cedula', 'user', 'telefono', 'created_at')
    # search_fields: Barra de búsqueda (puedes buscar por cédula o nombre de usuario)
    search_fields = ('cedula', 'user__username', 'user__first_name')

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