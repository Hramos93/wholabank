# backend/config/urls.py
import os
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings # Importar settings para DEBUG
from django.views.static import serve
# Importamos nuestras vistas personalizadas
from core_bancario.views import MyTokenObtainPairView, health_check, FrontendAppView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Movemos el Health Check a la jerarquía de la API (Alineado con warmup.sh)
    path('api/health/', health_check, name='health_check'),
    
    # Autenticación
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # DESPUÉS (Quítale el v1/):
    path('api/', include('core_bancario.urls')),

    # NUEVA VÍA: Forzamos a Django a servir los assets de Vite directamente desde su carpeta original
    re_path(r'^assets/(?P<path>.*)$', serve, {
        'document_root': os.path.join(settings.BASE_DIR, '..', 'frontend', 'dist', 'assets')
    }),

    # RUTA CATCH-ALL SEGURA: Excluimos explícitamente las rutas del backend (con o sin slash).
    # Esto permite que Django devuelva 404s reales o haga redirecciones 301 (Trailing Slash) en vez de servir HTML.
    re_path(r'^(?!api(/|$)|admin(/|$)|static(/|$)|assets(/|$)).*$', FrontendAppView.as_view(), name='frontend_app'),
]

# En modo DEBUG, Django sirve los archivos estáticos. En producción, Whitenoise lo hace.