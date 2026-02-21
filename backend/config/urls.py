# backend/config/urls.py
from django.contrib import admin
from django.urls import path, include
# Importamos nuestras vistas personalizadas
from core_bancario.views import MyTokenObtainPairView, health_check
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Ruta para el Health Check de Render
    path('health/', health_check, name='health_check'),
    
    # Autenticación
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # AQUÍ se conectan tus rutas. Fíjate que diga 'api/'
    path('api/', include('core_bancario.urls')),
]