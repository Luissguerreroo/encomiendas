from django.urls import path, include

from rest_framework.routers import DefaultRouter

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

from envios import api_views

router = DefaultRouter()

urlpatterns = [

    # JWT
    path(
        'auth/token/',
        TokenObtainPairView.as_view(),
        name='token_obtain',
    ),

    path(
        'auth/token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh',
    ),

    # Swagger
    path(
        'schema/',
        SpectacularAPIView.as_view(),
        name='schema',
    ),

    path(
        'docs/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger',
    ),

    # Encomiendas
    path(
        'encomiendas/',
        api_views.EncomiendaListCreateView.as_view(),
    ),

    path(
        'encomiendas/<int:pk>/',
        api_views.EncomiendaDetailView.as_view(),
    ),

    # Clientes
    path(
        'clientes/',
        api_views.ClienteListView.as_view(),
    ),

    # Rutas
    path(
        'rutas/',
        api_views.RutaListView.as_view(),
    ),

    # Router
    path('', include(router.urls)),
]