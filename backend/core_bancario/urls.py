# backend/core_bancario/urls.py
from django.urls import path
from .views import (
    DashboardView, 
    RegistroClienteView, 
    ProcesarPagoComercioView, 
    AutorizarPagoBancoView,
    AdminDashboardView,
    RegistroBancoAliadoView
)

urlpatterns = [
    # 1. Dashboard (Sprint 1)
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    
    # 2. Registro de Clientes (Sprint 3 - LA QUE FALTABA)
    path('registro/', RegistroClienteView.as_view(), name='registro'),

    # 3. Pagos y Transferencias (Sprint 2)
    path('procesar_pago/', ProcesarPagoComercioView.as_view(), name='procesar_pago'),
    path('autorizar_pago/', AutorizarPagoBancoView.as_view(), name='autorizar_pago'),
    path('admin-panel/', AdminDashboardView.as_view(), name='admin_panel'),
    path('admin/registrar-banco/', RegistroBancoAliadoView.as_view(), name='registrar_banco'),
]

