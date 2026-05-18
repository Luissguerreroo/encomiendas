from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from envios import views_auth

# JWT
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Swagger / DRF Spectacular
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

# =========================
# ADMIN
# =========================

admin.site.site_header = 'Sistema de Gestión de Encomiendas'
admin.site.site_title = 'Encomiendas Admin'
admin.site.index_title = 'Panel de Administración'


urlpatterns = [
    path('admin/', admin.site.urls),

    # =========================
    # API PRINCIPAL VERSIONADA
    # =========================
    path('api/<version>/', include('api.urls')),

    # =========================
    # AUTH JWT
    # =========================
    path('api/v1/auth/token/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # =========================
    # OPENAPI / SWAGGER
    # =========================
    path('api/<version>/schema/', SpectacularAPIView.as_view(), name='schema'),

    path(
        'api/<version>/docs/',
        SpectacularSwaggerView.as_view(url='/api/v1/schema/'),
        name='swagger-ui'
    ),

    path(
        'api/<version>/redoc/',
        SpectacularRedocView.as_view(url='/api/v1/schema/'),
        name='redoc'
    ),

    # =========================
    # APP PRINCIPAL
    # =========================
    path('', include('envios.urls')),

    path('login/', views_auth.login_view, name='login'),
    path('logout/', views_auth.logout_view, name='logout'),
    path('perfil/', views_auth.perfil_view, name='perfil'),
]

# =========================
# SILK (SOLO DEBUG)
# =========================

if settings.DEBUG:
    urlpatterns += [
        path('silk/', include('silk.urls', namespace='silk')),
    ]

# =========================
# STATIC / MEDIA
# =========================

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
