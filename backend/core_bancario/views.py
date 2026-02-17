# backend/core_bancario/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.contrib.auth.models import User  # <--- CRUCIAL: Faltaba esto seguramente
from django.conf import settings # Para importar configuraciones
import requests
from rest_framework.permissions import IsAdminUser # <--- IMPORTANTE


# Importamos tus modelos y serializadores
from .models import Cliente, Cuenta, Tarjeta, Comercio, Directorio, Transaccion
from .serializers import DashboardSerializer, PagoComercioSerializer, AutorizacionBancoSerializer

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



# --- VISTA 2: REGISTRO DE CLIENTES (LA QUE ESTÁ FALLANDO) ---
class RegistroClienteView(APIView):
    permission_classes = [] 

    def post(self, request):
        data = request.data
        tipo = data.get('tipo_persona', 'NATURAL') # Recibimos el tipo
        
        # Validaciones de Usuario
        if User.objects.filter(username=data.get('username')).exists():
            return error_response("IERROR_REG_01", "El nombre de usuario ya existe.", status.HTTP_400_BAD_REQUEST)

        # Validaciones según tipo
        if tipo == 'NATURAL':
            if not data.get('cedula'):
                return error_response("IERROR_REG_02", "La cédula es obligatoria para personas.", status.HTTP_400_BAD_REQUEST)
            if Cliente.objects.filter(cedula=data.get('cedula')).exists():
                return error_response("IERROR_REG_03", "Esta cédula ya está registrada.", status.HTTP_400_BAD_REQUEST)
            
            # Auto-generar RIF Natural si no viene
            rif_final = data.get('rif') or f"V-{data['cedula']}"

        else: # JURIDICO
            if not data.get('rif'):
                return error_response("IERROR_REG_04", "El RIF es obligatorio para empresas.", status.HTTP_400_BAD_REQUEST)
            if Cliente.objects.filter(rif=data.get('rif')).exists():
                return error_response("IERROR_REG_05", "Este RIF Jurídico ya está registrado.", status.HTTP_400_BAD_REQUEST)
            
            rif_final = data['rif'] # El RIF viene tal cual (J-123456)

        try:
            with transaction.atomic():
                # 1. Crear Usuario (Login)
                user = User.objects.create_user(
                    username=data['username'],
                    email=data['email'],
                    password=data['password'],
                    first_name=data['nombre_completo'] # En empresas será la Razón Social
                )

                # 2. Crear Cliente
                cliente = Cliente.objects.create(
                    user=user,
                    tipo_persona=tipo,
                    cedula=data.get('cedula') if tipo == 'NATURAL' else None, # Null si es empresa
                    rif=rif_final,
                    telefono=data['telefono'],
                    fecha_nacimiento=data.get('fecha_nacimiento'), # Fecha Constitución
                    lugar_nacimiento=data.get('lugar_nacimiento', 'Venezuela'),
                    estado_civil=data.get('estado_civil') if tipo == 'NATURAL' else None,
                    profesion=data.get('profesion', 'Comercio'), # Rubro
                    origen_fondos=data.get('origen_fondos', 'Actividad Comercial')
                )

                # 3. Crear Cuenta y Tarjeta
                tipo_cuenta_sel = data.get('tipo_cuenta', 'CORRIENTE')
                cuenta = Cuenta.objects.create(cliente=cliente, tipo_cuenta=tipo_cuenta_sel)
                tarjeta = Tarjeta.objects.create(cuenta=cuenta)

                return Response({
                    "message": "Registro exitoso",
                    "cuenta": cuenta.numero_cuenta,
                    "tarjeta": tarjeta.numero
                }, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(f"Error 500: {str(e)}")
            return error_response("IERROR_REG_99", f"Error interno: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)
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
        # 1. Resumen de Clientes
        clientes = Cliente.objects.all().select_related('user')
        lista_clientes = []
        
        total_dinero = 0
        
        for c in clientes:
            # Obtenemos sus cuentas
            cuentas = c.cuentas.all()
            saldo_total_cliente = sum(cta.saldo for cta in cuentas)
            total_dinero += saldo_total_cliente
            
            lista_clientes.append({
                "id": c.id,
                "nombre": f"{c.user.first_name} {c.user.last_name}",
                "identidad": c.rif or c.cedula,
                "tipo": c.tipo_persona,
                "saldo_total": saldo_total_cliente,
                "cuentas": [cta.numero_cuenta for cta in cuentas]
            })

        # 2. Directorio (OTROS BANCOS Y COMERCIOS)
        directorio = Directorio.objects.all().values('codigo', 'nombre', 'tipo', 'api_url')

        # 3. Métricas
        stats = {
            "total_clientes": clientes.count(),
            "total_bancos_conectados": Directorio.objects.filter(tipo='BANCO').count(),
            "total_comercios_externos": Directorio.objects.filter(tipo='COMERCIO').count(),
            "liquidez_total": total_dinero
        }

        return Response({
            "stats": stats,
            "clientes": lista_clientes,
            "directorio": directorio
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