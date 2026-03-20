# backend/config/urls.py
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings # Importar settings para DEBUG
# Importamos nuestras vistas personalizadas
from core_bancario.views import MyTokenObtainPairView, health_check, FrontendAppView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Ruta para el Health Check de Render
    path('health/', health_check, name='health_check'),
    
    # Autenticación
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # DESPUÉS (Quítale el v1/):
    path('api/', include('core_bancario.urls')),

    # RUTA CATCH-ALL: Cualquier otra ruta que no sea de la API o de archivos estáticos será manejada por React.
    # La expresión regular `(?!static/)` asegura que las rutas que comienzan con /static/ no sean capturadas.
    # Esto es crucial para que Whitenoise pueda servir los archivos estáticos de React y Django Admin.
    re_path(r'^(?!static/).*$', FrontendAppView.as_view(), name='frontend_app'),
]

# En modo DEBUG, Django sirve los archivos estáticos. En producción, Whitenoise lo hace.