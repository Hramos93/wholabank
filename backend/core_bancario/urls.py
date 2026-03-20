# backend/core_bancario/urls.py
from django.urls import path
from .views import (
    DashboardView, 
    RegistroClienteView, 
    ProcesarPagoComercioView, 
    AutorizarPagoBancoView,
    AdminDashboardView,
    RegistroBancoAliadoView,
    TransaccionListView
)

urlpatterns = [
    # 1. Dashboard (Sprint 1)
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    
    # 2. Registro de Clientes (Sprint 3 - LA QUE FALTABA)
    path('registro/', RegistroClienteView.as_view(), name='registro'),

    # 3. Pagos y Transferencias (Sprint 2)
    path('procesar_pago_comercio/', ProcesarPagoComercioView.as_view(), name='procesar_pago_comercio'),
    path('autorizar_pago/', AutorizarPagoBancoView.as_view(), name='autorizar_pago'),

    # 4. Historial de Transacciones (NUEVO)
    path('transacciones/', TransaccionListView.as_view(), name='transacciones'),

    path('admin-panel/', AdminDashboardView.as_view(), name='admin_panel'),
    path('admin/registrar-banco/', RegistroBancoAliadoView.as_view(), name='registrar_banco'),
]
