# backend/core_bancario/serializers.py

from rest_framework import serializers
from .models import Cliente, Cuenta, Tarjeta
from django.contrib.auth.models import User
from django.db import transaction
from .models import Comercio
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class TarjetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarjeta
        # Solo enviamos campos necesarios al frontend, ocultamos IDs internos si no son necesarios
        fields = ['numero', 'fecha_vencimiento', 'cvv', 'estado']

class CuentaSerializer(serializers.ModelSerializer):
    tarjetas = TarjetaSerializer(many=True, read_only=True)
    
    # Agregamos un campo calculado para que se vea bonito en el JSON
    tipo_texto = serializers.CharField(source='get_tipo_cuenta_display', read_only=True)

    class Meta:
        model = Cuenta
        fields = ['numero_cuenta', 'saldo', 'tipo_cuenta', 'tipo_texto', 'tarjetas']

class DashboardSerializer(serializers.ModelSerializer):
    """
    Serializador personalizado para la vista principal del usuario.
    Agrupa toda la información financiera.
    """
    cuentas = CuentaSerializer(many=True, read_only=True)
    nombre_usuario = serializers.CharField(source='user.first_name', read_only=True)
    is_admin = serializers.BooleanField(source='user.is_staff', read_only=True)
    
    class Meta:
        model = Cliente
        fields = ['nombre_usuario', 'cedula', 'cuentas', 'is_admin']

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

# Serializador para el registro de clientes (Refactorización)
class RegistroClienteSerializer(serializers.Serializer):
    # Campos del modelo User
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True) # No se devuelve en la respuesta
    nombre_completo = serializers.CharField(max_length=150) # Razón Social para Jurídico

    # Campos del modelo Cliente
    tipo_persona = serializers.ChoiceField(choices=Cliente.TIPO_PERSONA_CHOICES, default='NATURAL')
    cedula = serializers.CharField(max_length=20, required=False, allow_null=True, allow_blank=True, help_text="Ej: 20123456 (sin puntos ni letras)")
    rif = serializers.CharField(max_length=20, required=False, allow_null=True, allow_blank=True, help_text="Ej: J-12345678-9 o V-20123456-0")
    telefono = serializers.CharField(max_length=20, help_text="Ej: 04141234567")
    fecha_nacimiento = serializers.DateField(required=False, allow_null=True) # o Fecha Constitución
    lugar_nacimiento = serializers.CharField(max_length=100, default="Venezuela", required=False)
    estado_civil = serializers.CharField(max_length=20, required=False, allow_null=True, allow_blank=True)
    profesion = serializers.CharField(max_length=50, default="Comercio", required=False) # o Rubro
    origen_fondos = serializers.CharField(max_length=50, default="Actividad Comercial", required=False)

    # Campos para Cuenta/Tarjeta
    tipo_cuenta = serializers.ChoiceField(choices=Cuenta.TIPO_CUENTA_CHOICES, default='CORRIENTE', required=False)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("El nombre de usuario ya existe.")
        return value

    def validate(self, data):
        tipo = data.get('tipo_persona')
        if tipo == 'NATURAL':
            cedula = data.get('cedula')
            if not cedula:
                raise serializers.ValidationError({"cedula": "La cédula es obligatoria para personas naturales."})
            if Cliente.objects.filter(cedula=cedula).exists():
                raise serializers.ValidationError({"cedula": "Esta cédula ya está registrada."})
        elif tipo == 'JURIDICO':
            rif = data.get('rif')
            if not rif:
                raise serializers.ValidationError({"rif": "El RIF es obligatorio para personas jurídicas."})
            if Cliente.objects.filter(rif=rif).exists():
                raise serializers.ValidationError({"rif": "Este RIF Jurídico ya está registrado."})
        return data

    def create(self, validated_data):
        with transaction.atomic():
            tipo = validated_data.get('tipo_persona', 'NATURAL')

            # Auto-generar RIF Natural si no viene
            if tipo == 'NATURAL':
                rif_final = validated_data.get('rif') or f"V-{validated_data['cedula']}"
            else: # JURIDICO
                rif_final = validated_data['rif']

            # 1. Crear Usuario (Login)
            user = User.objects.create_user(
                username=validated_data['username'],
                email=validated_data['email'],
                password=validated_data['password'],
                first_name=validated_data['nombre_completo']
            )

            # 2. Crear Cliente
            cliente = Cliente.objects.create(
                user=user,
                tipo_persona=tipo,
                cedula=validated_data.get('cedula') if tipo == 'NATURAL' else None,
                rif=rif_final,
                telefono=validated_data['telefono'],
                fecha_nacimiento=validated_data.get('fecha_nacimiento'),
                lugar_nacimiento=validated_data.get('lugar_nacimiento', 'Venezuela'),
                estado_civil=validated_data.get('estado_civil') if tipo == 'NATURAL' else None,
                profesion=validated_data.get('profesion', 'Comercio'),
                origen_fondos=validated_data.get('origen_fondos', 'Actividad Comercial')
            )

            # 3. Crear Cuenta y Tarjeta
            tipo_cuenta_sel = validated_data.get('tipo_cuenta', 'CORRIENTE')
            cuenta = Cuenta.objects.create(cliente=cliente, tipo_cuenta=tipo_cuenta_sel)
            tarjeta = Tarjeta.objects.create(cuenta=cuenta)

            # 4. Si es Jurídico, afiliarlo como Comercio automáticamente
            if tipo == 'JURIDICO':
                codigo_comercio = f"C-{rif_final}"
                Comercio.objects.create(
                    codigo_identificador=codigo_comercio,
                    nombre=validated_data['nombre_completo'],
                    cuenta=cuenta,
                    activo=True
                )
            
            # Devolvemos los objetos creados para que la vista pueda usarlos
            return {
                "cuenta": cuenta,
                "tarjeta": tarjeta
            }

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

# --- SERIALIZER PERSONALIZADO PARA LOGIN ---
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Ejecuta la validación original (comprueba usuario y contraseña)
        data = super().validate(attrs)
        
        # Añade datos extra a la respuesta del login
        data['is_admin'] = self.user.is_staff
        data['username'] = self.user.username
        
        return data