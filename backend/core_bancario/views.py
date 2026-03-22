# backend/core_bancario/views.py

import logging
import requests
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models, transaction
from django.db.models import Sum, Q
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

# Importación de Modelos y Serializadores locales
from .models import Cliente, Cuenta, Tarjeta, Comercio, Directorio, Transaccion
from .serializers import (
    DashboardSerializer, PagoComercioSerializer, AutorizacionBancoSerializer, 
    RegistroClienteSerializer, MyTokenObtainPairSerializer, TransaccionSerializer
)

logger = logging.getLogger(__name__)

# --- CONSTANTES GLOBALES ---
MI_BANCO_DEFAULT = getattr(settings, 'MI_CODIGO_BANCO', '0001')

MAPEO_BANCOS = {
    "BANCO_1": "0001", "0001": "0001",
    "BANCO_2": "0002", "0002": "0002",
    "BANCO_5": "0005", "0005": "0005"
}

# --- MAPEO INVERSO (B2B) ---
# Para cumplir con el formato estricto de los otros bancos en peticiones salientes
FORMATO_EXTERNO_BANCOS = {
    "0001": "BANCO_1", "BANCO_1": "BANCO_1",
    "0002": "BANCO_2", "BANCO_2": "BANCO_2",
    "0005": "BANCO_5", "BANCO_5": "BANCO_5"
}

# --- UTILERÍA ---
def error_response(code, message, http_status=status.HTTP_404_NOT_FOUND):
    return Response({"error": {"code": code, "message": message}}, status=http_status)


# ============================================================================
# VISTAS BASE Y SISTEMA
# ============================================================================
def health_check(request):
    return JsonResponse({"status": "ok", "message": "Servicio activo"})

class FrontendAppView(TemplateView):
    template_name = 'index.html'


# ============================================================================
# AUTENTICACIÓN Y REGISTRO (CON EXCEPCIÓN CSRF)
# ============================================================================
@method_decorator(csrf_exempt, name='dispatch')
class MyTokenObtainPairView(TokenObtainPairView):
    """ Vista de login personalizada que devuelve datos extra del usuario. """
    serializer_class = MyTokenObtainPairSerializer

@method_decorator(csrf_exempt, name='dispatch')
class RegistroClienteView(APIView):
    """ Vista para el registro de nuevos clientes (Naturales y Jurídicos). """
    permission_classes = [AllowAny] 

    def post(self, request):
        serializer = RegistroClienteSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            created_data = serializer.save()

            return Response({
                "message": "Registro exitoso",
                "cuenta": created_data['cuenta'].numero_cuenta,
                "tarjeta": created_data['tarjeta'].numero
            }, status=status.HTTP_201_CREATED)

        except serializers.ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error 500 en RegistroClienteView: {str(e)}", exc_info=True)
            return error_response("IERROR_REG_99", "Ocurrió un error interno. Intente más tarde.", status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# VISTAS DE CLIENTE
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

class TransaccionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_accounts = Cuenta.objects.filter(cliente__user=request.user)
        transactions = Transaccion.objects.filter(
            Q(cuenta_origen__in=user_accounts) | Q(cuenta_destino__in=user_accounts)
        ).distinct().order_by('-fecha')
        
        serializer = TransaccionSerializer(transactions, many=True, context={'request': request})
        return Response(serializer.data)

# ============================================================================
# VISTA 5: RECLAMAR BONO DE BIENVENIDA (CAMPAÑA)
# ============================================================================
class ClaimBonusView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # 1. Importación local a prueba de fallos (Garantiza que Decimal exista)
            from decimal import Decimal

            # 2. Validación: ¿El usuario actual es un cliente o es el superadmin?
            if not hasattr(request.user, 'cliente'):
                return Response(
                    {"error": "Tu usuario (Admin) no tiene un perfil de cliente bancario para recibir bonos."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            cliente = request.user.cliente

            if cliente.bono_reclamado:
                return Response({"error": "Bono ya reclamado."}, status=status.HTTP_400_BAD_REQUEST)
                
            cuenta_a_creditar = cliente.cuentas.first()
            if not cuenta_a_creditar:
                return Response({"error": "No se encontró una cuenta bancaria activa."}, status=status.HTTP_404_NOT_FOUND)

            with transaction.atomic():
                bono_monto = Decimal('1000.00')

                cuenta_a_creditar.saldo += bono_monto
                cuenta_a_creditar.save()
                
                cliente.bono_reclamado = True
                cliente.save()

                Transaccion.objects.create(
                    tipo='TRANSFERENCIA', 
                    monto=bono_monto, 
                    cuenta_destino=cuenta_a_creditar,
                    estado='APROBADO', 
                    codigo_respuesta='00', 
                    banco_emisor_id='0001', # Ajustado a 4 dígitos por seguridad del modelo
                    mensaje_error='¡Activaste tu Bono de Bienvenida!' 
                )

            return Response({"message": "¡Felicidades! Has reclamado tu bono."}, status=status.HTTP_200_OK)

        except Exception as e:
            # 3. CAPTURA DEL ERROR REAL: Esto enviará el fallo exacto a tu SweetAlert en React
            import traceback
            logger.error(f"Error en Bono: {traceback.format_exc()}")
            return Response(
                {"error": f"Error interno de Python: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ============================================================================
# NÚCLEO TRANSACCIONAL: PASARELA DE PAGOS E INTEROPERABILIDAD
# ============================================================================
@method_decorator(csrf_exempt, name='dispatch')
class ProcesarPagoComercioView(APIView):
    """ Recibe cobros desde datáfonos de comercios (Rol Adquiriente). """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PagoComercioSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response("IERROR_000", f"JSON inválido: {serializer.errors}", status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        
        # Validación de Idempotencia (Prevenir cobros duplicados)
        if Transaccion.objects.filter(referencia_externa=data['numero_transaccion']).exists():
            return Response({"message": "Esta transacción ya fue procesada exitosamente."}, status=status.HTTP_200_OK)
        
        numero_tarjeta_limpio = data.get('numero_tarjeta', '').replace(' ', '')
        data['numero_tarjeta'] = numero_tarjeta_limpio

        receptor_raw = data.get('codigo_banco_comercio_receptor')
        codigo_banco_receptor = MAPEO_BANCOS.get(receptor_raw, receptor_raw)
        data['codigo_banco_comercio_receptor'] = codigo_banco_receptor
        
        # Validación: El comercio receptor debe ser de nuestro banco para que actuemos como adquirente.
        if codigo_banco_receptor != MI_BANCO_DEFAULT: 
            return error_response("IERROR_1007", "Error: El comercio receptor no pertenece a este banco.", status.HTTP_400_BAD_REQUEST)

        try:
            comercio = Comercio.objects.get(codigo_identificador=data['codigo_identificador_comercio_receptor'])
            if not comercio.activo:
                 return error_response("IERROR_1006", "Error: Comercio no afiliado.", status.HTTP_400_BAD_REQUEST)
        except Comercio.DoesNotExist:
            return error_response("IERROR_1001", "Error: Comercio no encontrado.", status.HTTP_404_NOT_FOUND)

        # --- INTELIGENCIA DE ENRUTAMIENTO POR BIN (NUEVO ESTÁNDAR) ---
        # Extraemos los primeros 4 dígitos de la tarjeta entrante
        bin_tarjeta = numero_tarjeta_limpio[:4]
        bin_local = getattr(settings, 'MI_BIN_TARJETA', '0001')[:4]
        
        if bin_tarjeta == bin_local:
            banco_emisor_code = MI_BANCO_DEFAULT # Si los 4 dígitos son nuestros, es "On-Us"
        else:
            banco_emisor_code = MAPEO_BANCOS.get(bin_tarjeta, bin_tarjeta) # Si no, mapeamos al banco externo

        # Si el JSON proporciona un código de banco emisor, lo usamos si es válido.
        if data.get('codigo_banco_emisor_tarjeta'):
            emisor_raw_from_json = data.get('codigo_banco_emisor_tarjeta')
            banco_emisor_code = MAPEO_BANCOS.get(emisor_raw_from_json, emisor_raw_from_json)

        if not banco_emisor_code:
            return error_response("IERROR_BIN_01", "No se pudo determinar el banco emisor.", status.HTTP_400_BAD_REQUEST)

        if banco_emisor_code == MI_BANCO_DEFAULT:
            return self.procesar_pago_interno(data, comercio)
        else:
            return self.enrutar_pago_externo(data, comercio, banco_emisor_code)

    def procesar_pago_interno(self, data, comercio):
        try:
            tarjeta = Tarjeta.objects.get(numero=data['numero_tarjeta'])
            if not tarjeta.estado:
                return error_response("IERROR_1003", "Tarjeta inoperativa.")
            
            cuenta_cliente = tarjeta.cuenta
            if tarjeta.cvv != data['cvc_tarjeta']:
                 return error_response("IERROR_1005", "CVV inválido.")
            if cuenta_cliente.saldo < data['monto_pagado']:
                return error_response("IERROR_1004", "Saldo insuficiente.")

            with transaction.atomic():
                cuenta_cliente.saldo -= data['monto_pagado']
                cuenta_cliente.save()
                
                comercio.cuenta.saldo += data['monto_pagado']
                comercio.cuenta.save()
                
                Transaccion.objects.create(
                    tipo='PAGO_COMERCIO', monto=data['monto_pagado'],
                    cuenta_origen=cuenta_cliente, cuenta_destino=comercio.cuenta,
                    estado='APROBADO', codigo_respuesta='201', banco_emisor_id=settings.MI_CODIGO_BANCO,
                    referencia_externa=data['numero_transaccion'] # Guardamos ID para idempotencia
                )

            return Response(status=status.HTTP_201_CREATED)

        except Tarjeta.DoesNotExist:
             return error_response("IERROR_1005", "Tarjeta no encontrada.")

    def enrutar_pago_externo(self, data, comercio, codigo_banco_destino):
        if codigo_banco_destino == MI_BANCO_DEFAULT:
            return self.procesar_pago_interno(data, comercio)

        try:
            banco_destino = Directorio.objects.get(codigo=codigo_banco_destino, tipo='BANCO')
            url_destino = f"{banco_destino.api_url.rstrip('/')}/autorizar_pago/"
            
            # --- CASO ESPECIAL: INTEROPERABILIDAD CON BANCO 0005 ---
            if codigo_banco_destino in ["0005", "BANCO_5"]:
                url_destino = "https://api.banprofi.site/api/pagos/banco"
            
            # Aplicamos la traducción global de bancos
            banco_receptor = str(data.get('codigo_banco_comercio_receptor', ''))
            
            payload_banco = {
                "numero_transaccion": str(data['numero_transaccion']),
                "numero_tarjeta": str(data['numero_tarjeta']),
                "cvc_tarjeta": str(data['cvc_tarjeta']),
                "fecha_vencimiento_tarjeta": str(data['fecha_vencimiento_tarjeta']),
                "codigo_banco_comercio_receptor": FORMATO_EXTERNO_BANCOS.get(banco_receptor, banco_receptor),
                "numero_cuenta_comercio_receptor": str(comercio.codigo_identificador), # Ahora enviamos "COMERCIO_3" en lugar de la cuenta interna de 20 dígitos
                "monto_pagado": float(data['monto_pagado']),
            }
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"  # <--- FUERZA A QUE EL OTRO BANCO RESPONDA EN JSON
            }
            
            # --- CASO ESPECIAL: INTEROPERABILIDAD CON BANCO 0002 ---
            if codigo_banco_destino in ["0002", "BANCO_2"]:
                token_banco_2 = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt2Ymd0amJ4eWNxYXFjeW1iZHlrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ2OTg3NTMsImV4cCI6MjA4MDI3NDc1M30.jJ4yRilhpAPHjkNNWNEjI1IHA7ml6-bSjM6CTdxcl-w"
                headers["Authorization"] = f"Bearer {token_banco_2}"
                # Supabase requiere adicionalmente este header en la mayoría de sus configuraciones
                headers["apikey"] = token_banco_2
            
            try:
                response = requests.post(url_destino, json=payload_banco, headers=headers, timeout=15)
                
                if response.status_code == 201:
                    with transaction.atomic():
                        comercio.cuenta.saldo += data['monto_pagado']
                        comercio.cuenta.save()
                        Transaccion.objects.create(
                            tipo='PAGO_COMERCIO', monto=data['monto_pagado'],
                            cuenta_destino=comercio.cuenta, estado='APROBADO', codigo_respuesta='201', 
                            banco_emisor_id=codigo_banco_destino, referencia_externa=data['numero_transaccion']
                        )
                    return Response({"message": "Pago aprobado por banco externo"}, status=status.HTTP_201_CREATED)
                
                # --- MEJORA PARA DEPURACIÓN B2B ---
                # Si el banco responde algo distinto a 201, capturamos su mensaje exacto
                try:
                    detalle_banco = response.json()
                except Exception:
                    detalle_banco = response.text
                
                mensaje_rechazo = f"Transacción declinada por el banco emisor. Detalle: {detalle_banco}"
                return error_response("IERROR_1002", mensaje_rechazo, http_status=status.HTTP_402_PAYMENT_REQUIRED)
            except requests.exceptions.RequestException:
                return error_response("IERROR_1002", "Timeout conectando con banco emisor.")
        except Directorio.DoesNotExist:
            return error_response("IERROR_1002", f"Banco {codigo_banco_destino} no registrado.")


@method_decorator(csrf_exempt, name='dispatch')
class AutorizarPagoBancoView(APIView):
    """ Recibe peticiones de otros bancos para cobrar a nuestras tarjetas (Rol Emisor). """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AutorizacionBancoSerializer(data=request.data)
        if not serializer.is_valid():
             return error_response("IERROR_000", "Formato JSON inválido", status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        # Idempotencia
        if Transaccion.objects.filter(referencia_externa=data['numero_transaccion']).exists():
            return Response({"message": "Transacción autorizada exitosamente"}, status=status.HTTP_201_CREATED)

        numero_tarjeta_limpio = data.get('numero_tarjeta', '').replace(' ', '')

        try:
            tarjeta = Tarjeta.objects.get(numero=numero_tarjeta_limpio)
            if not tarjeta.estado:
                 return error_response("IERROR_1003", "Tarjeta inoperativa.")
            if tarjeta.cvv != data['cvc_tarjeta']:
                return error_response("IERROR_1005", "CVV inválido.")
            
            cuenta = tarjeta.cuenta
            if cuenta.saldo < data['monto_pagado']:
                 return error_response("IERROR_1004", "Límite de crédito sobrepasado.")
            
            with transaction.atomic():
                cuenta.saldo -= data['monto_pagado']
                cuenta.save()
                Transaccion.objects.create(
                    tipo='PAGO_INTERBANCARIO', monto=data['monto_pagado'], cuenta_origen=cuenta,
                    estado='APROBADO', codigo_respuesta='201', banco_emisor_id=MI_BANCO_DEFAULT,
                    referencia_externa=data['numero_transaccion'],
                    mensaje_error=f"Aprobado para comercio: {data['codigo_banco_comercio_receptor']}"
                )
            
            return Response({"message": "Transacción autorizada exitosamente"}, status=status.HTTP_201_CREATED)
        except Tarjeta.DoesNotExist:
            return error_response("IERROR_1005", "Tarjeta no encontrada.")


# ============================================================================
# VISTAS DE ADMINISTRACIÓN
# ============================================================================
class AdminDashboardView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        clientes_qs = Cliente.objects.select_related('user').prefetch_related(
            models.Prefetch('cuentas', queryset=Cuenta.objects.all())
        ).annotate(saldo_total=Sum('cuentas__saldo'))
        
        lista_clientes = [{
            "id": c.id, "nombre": f"{c.user.first_name} {c.user.last_name}",
            "identidad": c.rif or c.cedula, "tipo": c.tipo_persona,
            "saldo_total": c.saldo_total or 0, "cuentas": [cta.numero_cuenta for cta in c.cuentas.all()]
        } for c in clientes_qs]

        directorio = Directorio.objects.all().values('codigo', 'nombre', 'tipo', 'api_url')
        liquidez = Cuenta.objects.aggregate(total=Sum('saldo'))['total'] or 0

        stats = {
            "total_clientes": clientes_qs.count(),
            "total_bancos_conectados": Directorio.objects.filter(tipo='BANCO').count(),
            "total_comercios_externos": Directorio.objects.filter(tipo='COMERCIO').count(),
            "liquidez_total": liquidez
        }
        return Response({"stats": stats, "clientes": lista_clientes, "directorio": list(directorio)})
    
class RegistroBancoAliadoView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        data = request.data
        if Directorio.objects.filter(codigo=data.get('codigo')).exists():
            return error_response("IERROR_DIR_01", "Código bancario registrado.", status.HTTP_400_BAD_REQUEST)
        try:
            nuevo_banco = Directorio.objects.create(
                codigo=data['codigo'], nombre=data['nombre'], rif=data.get('rif'),
                tipo='BANCO', api_url=data.get('api_url', '')
            )
            return Response({"message": f"Banco {nuevo_banco.nombre} registrado.", "codigo": nuevo_banco.codigo}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return error_response("IERROR_DIR_99", f"Error interno: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)