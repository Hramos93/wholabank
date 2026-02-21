# backend/core_bancario/models.py

# backend/core_bancario/models.py

from django.db import models
from django.contrib.auth.models import User
import random
from datetime import datetime
from dateutil.relativedelta import relativedelta # Necesitarás: pip install python-dateutil
from django.conf import settings

class Cliente(models.Model):
    TIPO_PERSONA_CHOICES = (
        ('NATURAL', 'Persona Natural'),
        ('JURIDICO', 'Persona Jurídica'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Nuevo campo para saber si es empresa
    tipo_persona = models.CharField(max_length=10, choices=TIPO_PERSONA_CHOICES, default='NATURAL')
    
    # Cédula ahora permite NULL (para empresas) y BLANK
    cedula = models.CharField(max_length=20, unique=True, null=True, blank=True)
    
    # RIF es obligatorio para todos
    rif = models.CharField(max_length=20, unique=True)
    
    telefono = models.CharField(max_length=20)
    
    # Demográficos (Compartidos o adaptados)
    fecha_nacimiento = models.DateField(null=True) # Para empresas será Fecha Constitución
    lugar_nacimiento = models.CharField(max_length=100, default="Venezuela")
    estado_civil = models.CharField(max_length=20, null=True, blank=True) # Empresas no tienen
    profesion = models.CharField(max_length=50, default="Computación") # Para empresas será el Rubro
    origen_fondos = models.CharField(max_length=50, default="Actividad Comercial")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        identificador = self.cedula if self.cedula else self.rif
        return f"{identificador} - {self.user.first_name}"
    
class Cuenta(models.Model):
    TIPO_CUENTA_CHOICES = (
        ('CORRIENTE', 'Corriente'),
        ('AHORRO', 'Ahorro'),
    )

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='cuentas')
    numero_cuenta = models.CharField(max_length=20, unique=True, editable=False)
    saldo = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    tipo_cuenta = models.CharField(max_length=20, choices=TIPO_CUENTA_CHOICES, default='CORRIENTE') # Nuevo campo
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Solo generamos el número si la cuenta es nueva (no tiene ID aún)
        if not self.numero_cuenta:
            unique = False
            while not unique:
                # 1. Definir Estructura Venezolana
                # Banco (0001) + Agencia (0001) + Control (00)
                prefix = f"{settings.MI_CODIGO_BANCO}{settings.MI_CODIGO_AGENCIA}00" 
                
                # 2. Generar 10 dígitos aleatorios
                unique_id = str(random.randint(1, 9999999999)).zfill(10)
                posible_numero = f"{prefix}{unique_id}"
                
                # 3. Verificar colisión (¿Ya existe este número?)
                if not Cuenta.objects.filter(numero_cuenta=posible_numero).exists():
                    self.numero_cuenta = posible_numero
                    unique = True
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_tipo_cuenta_display()}: {self.numero_cuenta} | Bs. {self.saldo}"

class Tarjeta(models.Model):
    cuenta = models.ForeignKey(Cuenta, on_delete=models.CASCADE, related_name='tarjetas')
    numero = models.CharField(max_length=16, unique=True, editable=False)
    cvv = models.CharField(max_length=3, editable=False)
    fecha_vencimiento = models.CharField(max_length=5, editable=False) # MM/YY
    estado = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.numero:
            # --- ESTRUCTURA ISO/IEC 7812 (16 Dígitos) ---
            
            # 1. Identificador de Industria (1): "5" para Mastercard
            industry = "5"
            
            # 2. BIN/IIN (5): Identificador de nuestro banco (00001)
            bin_code = settings.MI_BIN_TARJETA
            
            # 3. Cuenta Individual (9 dígitos aleatorios)
            account_id = str(random.randint(1, 999999999)).zfill(9)
            
            # 4. Dígito Verificador (1): Hardcodeado a "0" según instrucción
            check_digit = "0"
            
            self.numero = f"{industry}{bin_code}{account_id}{check_digit}"

            # --- SEGURIDAD ---
            # CVV: 3 dígitos aleatorios (simulación criptográfica)
            self.cvv = str(random.randint(100, 999))
            
            # FECHA VENCIMIENTO: 5 años a partir de hoy
            fecha_futura = datetime.now() + relativedelta(years=5)
            self.fecha_vencimiento = fecha_futura.strftime("%m/%y") # Formato MM/YY

        super().save(*args, **kwargs)

    def __str__(self):
        return f"TC: {self.numero} (Exp: {self.fecha_vencimiento})"

# --- NUEVO MODELO: DIRECTORIO DE EQUIPOS ---
class Directorio(models.Model):
    """
    Almacena la información de conexión de los otros equipos (Bancos y Comercios).
    Es vital para el enrutamiento de transacciones.
    """
    TIPO_ENTIDAD = (
        ('BANCO', 'Banco'),
        ('COMERCIO', 'Comercio'),
    )

    codigo = models.CharField(max_length=10, unique=True, help_text="Ej: 0002 para Banco 2")
    nombre = models.CharField(max_length=50, help_text="Ej: BANCO_2")
    rif = models.CharField(max_length=20, null=True, blank=True, help_text="J-12345678-9") 
    tipo = models.CharField(max_length=10, choices=TIPO_ENTIDAD)
    api_url = models.URLField(help_text="Endpoint base del equipo. Ej: http://192.168.1.50:8000/api/")
    
    def __str__(self):
        return f"{self.nombre} ({self.codigo})"
    

class Comercio(models.Model):
    """
    Vincula un Código de Comercio (ej: C003) con una Cuenta de nuestro banco.
    Esto nos convierte en su Banco Adquiriente.
    """
    codigo_identificador = models.CharField(max_length=20, unique=True) # El ID que envía el datáfono
    nombre = models.CharField(max_length=100)
    cuenta = models.OneToOneField(Cuenta, on_delete=models.CASCADE, related_name='perfil_comercio')
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} ({self.codigo_identificador})"

class Transaccion(models.Model):
    """
    Bitácora de todas las operaciones (Exitosas o Fallidas).
    """
    TIPO_CHOICES = (
        ('PAGO_COMERCIO', 'Pago en Comercio'),
        ('TRANSFERENCIA', 'Transferencia'),
    )
    ESTADO_CHOICES = (
        ('APROBADO', 'Aprobado'),
        ('RECHAZADO', 'Rechazado'),
    )

    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    monto = models.DecimalField(max_digits=15, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    
    # Datos de origen/destino
    cuenta_origen = models.ForeignKey(Cuenta, on_delete=models.SET_NULL, null=True, blank=True, related_name='debitos')
    cuenta_destino = models.ForeignKey(Cuenta, on_delete=models.SET_NULL, null=True, blank=True, related_name='creditos')
    
    # Referencias externas (para conciliación)
    referencia_externa = models.CharField(max_length=100, null=True, blank=True)
    banco_emisor_id = models.CharField(max_length=10) # Quién emitió la tarjeta
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES)
    codigo_respuesta = models.CharField(max_length=20) # 201, 404, IERROR...
    mensaje_error = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.tipo} - {self.monto} - {self.estado}"
    
# --- MODELO PROXY PARA LINK EN ADMIN ---
class AdminDashboardProxy(Cliente):
    """
    Modelo proxy que no crea una tabla en la DB.
    Se usa para registrar un link en el panel de admin de Django
    que redirige a nuestra vista de dashboard personalizada.
    """
    class Meta:
        proxy = True
        verbose_name = 'Panel de Control del Banco'
        verbose_name_plural = 'Panel de Control del Banco'
    
