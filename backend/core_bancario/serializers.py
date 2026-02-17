# backend/core_bancario/serializers.py

from rest_framework import serializers
from .models import Cliente, Cuenta, Tarjeta

class TarjetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarjeta
        # Solo enviamos campos necesarios al frontend, ocultamos IDs internos si no son necesarios
        fields = ['numero', 'fecha_vencimiento', 'cvv', 'estado']

class CuentaSerializer(serializers.ModelSerializer):
    # Serializador anidado: Incluye las tarjetas dentro de la información de la cuenta
    tarjetas = TarjetaSerializer(many=True, read_only=True)
    
    class Meta:
        model = Cuenta
        fields = ['numero_cuenta', 'saldo', 'tarjetas']

class DashboardSerializer(serializers.ModelSerializer):
    """
    Serializador personalizado para la vista principal del usuario.
    Agrupa toda la información financiera.
    """
    cuentas = CuentaSerializer(many=True, read_only=True)
    nombre_usuario = serializers.CharField(source='user.first_name') # Obtenemos el nombre real
    
    class Meta:
        model = Cliente
        fields = ['nombre_usuario', 'cedula', 'cuentas']

# Serializador para el CASO 1: Comercio -> Banco Adquiriente (Nosotros)
class PagoComercioSerializer(serializers.Serializer):
    numero_transaccion = serializers.CharField()
    codigo_banco_emisor_tarjeta = serializers.CharField()
    numero_tarjeta = serializers.CharField()
    cvc_tarjeta = serializers.CharField()
    fecha_vencimiento_tarjeta = serializers.CharField()
    codigo_banco_comercio_receptor = serializers.CharField()
    codigo_identificador_comercio_receptor = serializers.CharField()
    monto_pagado = serializers.DecimalField(max_digits=15, decimal_places=2)

# Serializador para el CASO 2: Banco Adquiriente -> Banco Emisor (Nosotros)
class AutorizacionBancoSerializer(serializers.Serializer):
    numero_transaccion = serializers.CharField()
    codigo_banco_emisor_tarjeta = serializers.CharField()
    numero_tarjeta = serializers.CharField()
    cvc_tarjeta = serializers.CharField()
    fecha_vencimiento_tarjeta = serializers.CharField()
    codigo_banco_comercio_receptor = serializers.CharField()
    numero_cuenta_comercio_receptor = serializers.CharField() # Nota que este campo cambia respecto al anterior
    monto_pagado = serializers.DecimalField(max_digits=15, decimal_places=2)

class CuentaSerializer(serializers.ModelSerializer):
    tarjetas = TarjetaSerializer(many=True, read_only=True)
    
    # Agregamos un campo calculado para que se vea bonito en el JSON
    tipo_texto = serializers.CharField(source='get_tipo_cuenta_display', read_only=True)

    class Meta:
        model = Cuenta
        fields = ['numero_cuenta', 'saldo', 'tipo_cuenta', 'tipo_texto', 'tarjetas']