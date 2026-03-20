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

    # Ruta para el Health Check de Render
    path('health/', health_check, name='health_check'),
    
    # Autenticación
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # DESPUÉS (Quítale el v1/):
    path('api/', include('core_bancario.urls')),

    # NUEVA VÍA: Forzamos a Django a servir los assets de Vite directamente desde su carpeta original
    re_path(r'^assets/(?P<path>.*)$', serve, {
        'document_root': os.path.join(settings.BASE_DIR, '..', 'frontend', 'dist', 'assets')
    }),

    # RUTA CATCH-ALL ACTUALIZADA: Ignoramos tanto /static/ como /assets/ para que no envíen el index.html por error
    re_path(r'^(?!static/|assets/).*$', FrontendAppView.as_view(), name='frontend_app'),
]

# En modo DEBUG, Django sirve los archivos estáticos. En producción, Whitenoise lo hace.