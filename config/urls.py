from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from envios import views_auth
# =========================
# PERSONALIZACIÓN DEL ADMIN
# =========================
admin.site.site_header = 'Sistema de Gestión de Encomiendas'
admin.site.site_title = 'Encomiendas Admin'
admin.site.index_title = 'Panel de Administración'


urlpatterns = [
    path('admin/', admin.site.urls),

    # App principal
    path('', include('envios.urls')),

    
    path('login/', views_auth.login_view, name='login'),
    path('logout/', views_auth.logout_view, name='logout'),
    path('perfil/', views_auth.perfil_view, name='perfil'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)