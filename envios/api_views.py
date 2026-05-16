from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema

from .models import Encomienda
from clientes.models import Cliente
from rutas.models import Ruta

from .serializers import (
    EncomiendaSerializer,
    EncomiendaDetailSerializer,
    ClienteSerializer,
    RutaSerializer,
)

from api.pagination import ClientePagination


# ─────────────────────────────
# ENCOMIENDAS (LISTA + CREAR)
# ─────────────────────────────

class EncomiendaListCreateView(generics.ListCreateAPIView):

    queryset = Encomienda.objects.con_relaciones()
    serializer_class = EncomiendaSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(
            empleado_registro=self.request.user.empleado
        )


# ─────────────────────────────
# ENCOMIENDAS (DETALLE + EDITAR + ELIMINAR)
# ─────────────────────────────

class EncomiendaDetailView(generics.RetrieveUpdateDestroyAPIView):

    queryset = Encomienda.objects.con_relaciones()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return EncomiendaDetailSerializer
        return EncomiendaSerializer


# ─────────────────────────────
# CLIENTES
# ─────────────────────────────

@extend_schema(
    summary='Listar clientes activos',
    description='Devuelve todos los clientes con estado activo, paginados.',
    tags=['Clientes'],
)
class ClienteListView(generics.ListAPIView):

    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ClientePagination

    def get_queryset(self):
        return Cliente.objects.activos()


# ─────────────────────────────
# RUTAS
# ─────────────────────────────

@extend_schema(
    summary='Listar rutas activas',
    description='Devuelve todas las rutas activas sin paginación.',
    tags=['Rutas'],
)
class RutaListView(generics.ListAPIView):

    serializer_class = RutaSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return Ruta.objects.activas()