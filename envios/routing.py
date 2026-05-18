from django.urls import re_path

from . import consumers

websocket_urlpatterns = [

    # ─────────────────────────────────────────────
    # Consumer general
    # ws://localhost:8000/ws/encomiendas/
    # ─────────────────────────────────────────────
    re_path(
        r'^ws/encomiendas/$',
        consumers.EncomiendaConsumer.as_asgi(),
        name='ws-encomiendas'
    ),

    # ─────────────────────────────────────────────
    # 
    # ─────────────────────────────────────────────
    # re_path(
    #     r'^ws/encomiendas/(?P<pk>\d+)/$',
    #     consumers.EncomiendaDetalleConsumer.as_asgi(),
    #     name='ws-encomienda-detalle'
    # ),

    # ─────────────────────────────────────────────
    # Dashboard
    # ws://localhost:8000/ws/dashboard/
    # ─────────────────────────────────────────────
    re_path(
        r'^ws/dashboard/$',
        consumers.DashboardConsumer.as_asgi(),
        name='ws-dashboard'
    ),
]
