# backend/core_bancario/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User  # <--- CRUCIAL: Faltaba esto seguramente
from django.conf import settings  # Para importar configuraciones
import requests
from rest_framework.permissions import IsAdminUser  # <--- IMPORTANTE
import logging
from rest_framework import serializers

# Configurar un logger para esta vista
logger = logging.getLogger(__name__)

# Importamos tus modelos y serializadores
from .models import Cliente, Cuenta, Tarjeta, Comercio, Directorio, Transaccion
from .serializers import (DashboardSerializer, PagoComercioSerializer, AutorizacionBancoSerializer, 
                          RegistroClienteSerializer, MyTokenObtainPairSerializer)

# --- UTILERÍA PARA RESPUESTAS DE ERROR (ESTÁNDAR) ---
def error_response(code, message, http_status=status.HTTP_404_NOT_FOUND):
    return Response({
        "error": {
            "code": code,
            "message": message
        }
    }, status=http_status)

# ============================================================================
# VISTA 1: DASHBOARD CLIENTE (SPRINT 1)
# ============================================================================
class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            cliente = Cliente.objects.get(user=request.user)
            serializer = DashboardSerializer(cliente)
            return Response(serializer.data)
        except Cliente.DoesNotExist:
            return Response({"error": "Cliente no encontrado"}, status=404)

# --- VISTA DE LOGIN PERSONALIZADA ---
from rest_framework_simplejwt.views import TokenObtainPairView

class MyTokenObtainPairView(TokenObtainPairView):
    """
    Vista de login personalizada que devuelve si el usuario es admin.
    """
    serializer_class = MyTokenObtainPairSerializer



# --- VISTA 2: REGISTRO DE CLIENTES (REFACTORIZADA) ---
class RegistroClienteView(APIView):
    permission_classes = [] 

    def post(self, request):
        serializer = RegistroClienteSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            # El método create del serializador se encarga de toda la lógica de negocio
            # y de las transacciones de base de datos.
            created_data = serializer.save() # .save() llama a .create() o .update()

            return Response({
                "message": "Registro exitoso",
                "cuenta": created_data['cuenta'].numero_cuenta,
                "tarjeta": created_data['tarjeta'].numero
            }, status=status.HTTP_201_CREATED)

        except serializers.ValidationError as e:
            # DRF maneja automáticamente el formato de los errores de validación
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            # Usamos logger para registrar el error detallado en los logs del servidor
            logger.error(f"Error 500 en RegistroClienteView: {str(e)}", exc_info=True)
            # Devolvemos un mensaje genérico al usuario por seguridad
            return error_response("IERROR_REG_99", "Ocurrió un error interno durante el registro. Por favor, intente más tarde.", status.HTTP_500_INTERNAL_SERVER_ERROR)
# ============================================================================
# VISTA 2: PROCESAR PAGO COMERCIO (ROL ADQUIRIENTE - SPRINT 2)
# El comercio nos manda la tarjeta para cobrar.
# ============================================================================
class ProcesarPagoComercioView(APIView):
    # No requiere Auth por Token porque simula un Datáfono público
    permission_classes = [] 

    def post(self, request):
        serializer = PagoComercioSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response("IERROR_000", "Formato JSON inválido: " + str(serializer.errors), status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        
        # 1. Validar que el comercio existe y es nuestro cliente (Adquiriencia)
        try:
            comercio = Comercio.objects.get(codigo_identificador=data['codigo_identificador_comercio_receptor'])
            if not comercio.activo:
                 return error_response("IERROR_1006", "Error: Su comercio no se encuentra afiliado en condición de adquiriencia.")
        except Comercio.DoesNotExist:
            return error_response("IERROR_1001", "Error: No se encontró ningún cliente afiliado con el código identificador provisto.")

        # 2. Determinar si la tarjeta es MÍA (On-Us) o AJENA (Off-Us)
        banco_emisor_code = data['codigo_banco_emisor_tarjeta']

        if banco_emisor_code == settings.MI_CODIGO_BANCO:
            # --- PROCESAMIENTO INTERNO (Nosotros somos el emisor también) ---
            return self.procesar_pago_interno(data, comercio)
        else:
            # --- ENRUTAMIENTO A OTRO BANCO ---
            return self.enrutar_pago_externo(data, comercio, banco_emisor_code)

    def procesar_pago_interno(self, data, comercio):
        """ Lógica cuando el comprador y el comercio son de MI banco """
        try:
            # Buscamos la tarjeta en nuestra base de datos
            tarjeta = Tarjeta.objects.get(numero=data['numero_tarjeta'])
            
            if not tarjeta.estado:
                return error_response("IERROR_1003", "Error: Su tarjeta se encuentra inoperativa.")

            cuenta_cliente = tarjeta.cuenta
            
            # Validaciones de seguridad básicas
            if tarjeta.cvv != data['cvc_tarjeta']:
                 return error_response("IERROR_1005", "Error: Datos de seguridad inválidos (CVV).")
            
            # Validar Saldo
            if cuenta_cliente.saldo < data['monto_pagado']:
                return error_response("IERROR_1004", "Error: Usted ha sobrepasado su límite de crédito.")

            # TRANSACCIÓN ATÓMICA (Descontar y Acreditar)
            with transaction.atomic():
                cuenta_cliente.saldo -= data['monto_pagado']
                cuenta_cliente.save()
                
                comercio.cuenta.saldo += data['monto_pagado']
                comercio.cuenta.save()
                
                # Registrar Historial
                Transaccion.objects.create(
                    tipo='PAGO_COMERCIO',
                    monto=data['monto_pagado'],
                    cuenta_origen=cuenta_cliente,
                    cuenta_destino=comercio.cuenta,
                    estado='APROBADO',
                    codigo_respuesta='201',
                    banco_emisor_id=settings.MI_CODIGO_BANCO
                )

            return Response(status=status.HTTP_201_CREATED)

        except Tarjeta.DoesNotExist:
             return error_response("IERROR_1005", "Error: No se encontró ninguna tarjeta con los datos provistos.")

    def enrutar_pago_externo(self, data, comercio, codigo_banco_destino):
        """ Lógica para reenviar la petición al Banco B """
        try:
            # Buscar la URL del banco en el Directorio
            banco_destino = Directorio.objects.get(codigo=codigo_banco_destino, tipo='BANCO')
            url_destino = f"{banco_destino.api_url}autorizar_pago/" 
            
            # Transformar payload: El banco destino necesita el NÚMERO DE CUENTA del comercio
            payload_banco = {
                "numero_transaccion": data['numero_transaccion'],
                "codigo_banco_emisor_tarjeta": data['codigo_banco_emisor_tarjeta'],
                "numero_tarjeta": data['numero_tarjeta'],
                "cvc_tarjeta": data['cvc_tarjeta'],
                "fecha_vencimiento_tarjeta": data['fecha_vencimiento_tarjeta'],
                "codigo_banco_comercio_receptor": data['codigo_banco_comercio_receptor'],
                "numero_cuenta_comercio_receptor": comercio.cuenta.numero_cuenta, # DATO CLAVE
                "monto_pagado": float(data['monto_pagado'])
            }

            # Enviar Request con Timeout
            try:
                response = requests.post(url_destino, json=payload_banco, timeout=15)
                
                if response.status_code == 201:
                    # El otro banco aprobó. Acredito al comercio.
                    comercio.cuenta.saldo += data['monto_pagado']
                    comercio.cuenta.save()
                    return Response(status=status.HTTP_201_CREATED)
                else:
                    # El otro banco rechazó.
                    try:
                        error_data = response.json()
                        msg = error_data.get('error', {}).get('message', 'Rechazado por banco emisor')
                        return error_response("IERROR_1002", f"Error: {msg}")
                    except:
                         return error_response("IERROR_1002", "Error desconocido del banco emisor")

            except requests.exceptions.RequestException:
                return error_response("IERROR_1002", "Error: Tiempo de espera agotado con el banco emisor.")

        except Directorio.DoesNotExist:
            return error_response("IERROR_1002", f"Error: No hay conexión con el Banco {codigo_banco_destino}")


# ============================================================================
# VISTA 3: AUTORIZAR PAGO BANCO (ROL EMISOR - SPRINT 2)
# Otro banco nos pide autorizar un pago de NUESTRA tarjeta
# ============================================================================
class AutorizarPagoBancoView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = AutorizacionBancoSerializer(data=request.data)
        if not serializer.is_valid():
             return error_response("IERROR_000", "Formato JSON inválido", status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        # 1. Buscar la Tarjeta
        try:
            tarjeta = Tarjeta.objects.get(numero=data['numero_tarjeta'])
        except Tarjeta.DoesNotExist:
            return error_response("IERROR_1005", "Error: No se encontró ninguna tarjeta con los datos provistos.")

        # 2. Validar Estado
        if not tarjeta.estado:
             return error_response("IERROR_1003", "Error: Su tarjeta se encuentra inoperativa.")
        
        # 3. Validar Saldo
        cuenta = tarjeta.cuenta
        if cuenta.saldo < data['monto_pagado']:
             return error_response("IERROR_1004", "Error: Usted ha sobrepasado su límite de crédito.")

        # 4. Validar Seguridad (CVV)
        if tarjeta.cvv != data['cvc_tarjeta']:
            return error_response("IERROR_1005", "Error: Datos de seguridad inválidos.")

        # 5. Ejecutar Débito
        cuenta.saldo -= data['monto_pagado']
        cuenta.save()

        # Registrar Log
        Transaccion.objects.create(
            tipo='TRANSFERENCIA', # O PAGO_INTERBANCARIO
            monto=data['monto_pagado'],
            cuenta_origen=cuenta,
            estado='APROBADO',
            codigo_respuesta='201',
            banco_emisor_id=settings.MI_CODIGO_BANCO,
            mensaje_error=f"Autorizado para comercio ext: {data['codigo_banco_comercio_receptor']}"
        )

        return Response(status=status.HTTP_201_CREATED)
# ============================================================================
# VISTA 4: VIsta de aministración
class AdminDashboardView(APIView):
    """
    Vista exclusiva para administradores del banco.
    Devuelve métricas globales, lista de clientes y directorio de bancos externos.
    """
    permission_classes = [IsAdminUser] # Solo usuarios con is_staff=True

    def get(self, request):
        # 1. Resumen de Clientes (Optimizado con agregaciones y prefetch)
        clientes_qs = Cliente.objects.select_related('user').prefetch_related(
            models.Prefetch('cuentas', queryset=Cuenta.objects.all())
        ).annotate(
            saldo_total=Sum('cuentas__saldo')
        )

        lista_clientes = []
        for c in clientes_qs:
            lista_clientes.append({
                "id": c.id,
                "nombre": f"{c.user.first_name} {c.user.last_name}",
                "identidad": c.rif or c.cedula,
                "tipo": c.tipo_persona,
                "saldo_total": c.saldo_total or 0,
                "cuentas": [cta.numero_cuenta for cta in c.cuentas.all()] # Usa datos prefetched
            })

        # 2. Directorio (OTROS BANCOS Y COMERCIOS)
        directorio = Directorio.objects.all().values('codigo', 'nombre', 'tipo', 'api_url')

        # 3. Métricas (Optimizadas con agregaciones de la DB)
        liquidez_total = Cuenta.objects.aggregate(total=Sum('saldo'))['total'] or 0

        stats = {
            "total_clientes": clientes_qs.count(),
            "total_bancos_conectados": Directorio.objects.filter(tipo='BANCO').count(),
            "total_comercios_externos": Directorio.objects.filter(tipo='COMERCIO').count(),
            "liquidez_total": liquidez_total
        }

        return Response({
            "stats": stats,
            "clientes": lista_clientes,
            "directorio": list(directorio) # Convertir a lista para serialización
        })
    
# ============================================================================
# VISTA 5: registro bancario
    
class RegistroBancoAliadoView(APIView):
    """
    Permite al Administrador registrar nuevos bancos en el ecosistema
    para futuros enrutamientos.
    """
    permission_classes = [IsAdminUser] # Solo Superusuarios

    def post(self, request):
        data = request.data
        
        # Validaciones
        if Directorio.objects.filter(codigo=data.get('codigo')).exists():
            return error_response("IERROR_DIR_01", "Este código bancario ya está registrado.", status.HTTP_400_BAD_REQUEST)
        
        # Validar formato de URL básico
        url = data.get('api_url', '')
        if not url.startswith('http'):
            return error_response("IERROR_DIR_02", "La URL debe comenzar con http:// o https://", status.HTTP_400_BAD_REQUEST)

        try:
            nuevo_banco = Directorio.objects.create(
                codigo=data['codigo'],
                nombre=data['nombre'],
                rif=data['rif'],
                tipo='BANCO', # Forzamos que sea BANCO
                api_url=url
            )
            
            return Response({
                "message": f"Banco {nuevo_banco.nombre} registrado correctamente.",
                "codigo": nuevo_banco.codigo
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return error_response("IERROR_DIR_99", f"Error interno: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)