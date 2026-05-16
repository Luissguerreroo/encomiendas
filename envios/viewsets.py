from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from django.core.cache import cache
from django.utils import timezone

from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
)
from drf_spectacular.types import OpenApiTypes

from .models import Encomienda, Empleado

from .serializers import (
    EncomiendaSerializer,
    EncomiendaListSerializer,
    EncomiendaDetailSerializer,
    EncomiendaV2Serializer,
)

from api.pagination import EncomiendaPagination
from api.filters import EncomiendaFilter

from api.throttles import (
    EmpleadoRateThrottle,
    CambioEstadoThrottle,
)

from config.settings import CACHE_TTL


@extend_schema_view(
    list=extend_schema(summary='Listar encomiendas', tags=['Encomiendas']),
    create=extend_schema(summary='Crear encomienda', tags=['Encomiendas']),
    retrieve=extend_schema(summary='Detalle de encomienda', tags=['Encomiendas']),
    update=extend_schema(summary='Actualizar encomienda', tags=['Encomiendas']),
    partial_update=extend_schema(summary='Actualizar parcial', tags=['Encomiendas']),
    destroy=extend_schema(summary='Eliminar encomienda', tags=['Encomiendas']),
)
class EncomiendaViewSet(viewsets.ModelViewSet):

    queryset = Encomienda.objects.con_relaciones()
    permission_classes = [IsAuthenticated]
    pagination_class = EncomiendaPagination
    throttle_classes = [EmpleadoRateThrottle]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    ]

    filterset_class = EncomiendaFilter

    search_fields = [
        'codigo',
        'remitente__apellidos',
        'destinatario__apellidos',
        'descripcion',
    ]

    ordering_fields = [
        'fecha_registro',
        'peso_kg',
        'costo_envio'
    ]

    ordering = ['-fecha_registro']

    # ─────────────────────────────
    # SERIALIZERS POR ACCIÓN / VERSIÓN
    # ─────────────────────────────
    def get_serializer_class(self):

        version = getattr(self.request, 'version', 'v1')

        if version == 'v2':
            return EncomiendaV2Serializer

        if self.action == 'list':
            return EncomiendaListSerializer

        if self.action == 'retrieve':
            return EncomiendaDetailSerializer

        return EncomiendaSerializer

    # ─────────────────────────────
    # QUERYSET OPTIMIZADO + ONLY
    # ─────────────────────────────
    def get_queryset(self):

        qs = Encomienda.objects.con_relaciones()

        estado = self.request.query_params.get('estado')
        if estado:
            qs = qs.filter(estado=estado)

        if self.action == 'list':
            qs = qs.only(
                'id',
                'codigo',
                'estado',
                'peso_kg',
                'costo_envio',
                'fecha_registro',
                'fecha_entrega_est',

                'remitente__nombres',
                'remitente__apellidos',

                'destinatario__nombres',
                'destinatario__apellidos',

                'ruta__destino',
            )

        return qs

    # ─────────────────────────────
    # LIST (CACHE HTTP)
    # ─────────────────────────────
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response['X-API-Version'] = getattr(request, 'version', 'v1')
        return response

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        response['X-API-Version'] = getattr(request, 'version', 'v1')
        return response

    # ─────────────────────────────
    # CREATE
    # ─────────────────────────────
    def perform_create(self, serializer):
        serializer.save(
            empleado_registro=self.request.user.empleado
        )

    # ─────────────────────────────
    # CAMBIAR ESTADO + INVALIDAR CACHE
    # ─────────────────────────────
    @action(detail=True, methods=['post'], url_path='cambiar_estado')
    def cambiar_estado(self, request, pk=None):

        enc = self.get_object()
        nuevo_estado = request.data.get('estado')
        observacion = request.data.get('observacion', '')

        if not nuevo_estado:
            return Response(
                {'error': 'El campo estado es requerido.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        empleado = Empleado.objects.get(email=request.user.email)

        enc.cambiar_estado(
            nuevo_estado,
            empleado,
            observacion
        )

        # INVALIDAR CACHE
        cache.delete(f'estadisticas_empleado_{request.user.id}')

        return Response(self.get_serializer(enc).data)

    # ─────────────────────────────
    # ESTADÍSTICAS (CACHE MANUAL)
    # ─────────────────────────────
    @action(detail=False, methods=['get'], url_path='estadisticas')
    def estadisticas(self, request):

        cache_key = f'estadisticas_empleado_{request.user.id}'
        data = cache.get(cache_key)

        if data is None:
            data = {
                'activas': Encomienda.objects.activas().count(),
                'en_transito': Encomienda.objects.en_transito().count(),
                'con_retraso': Encomienda.objects.con_retraso().count(),
                'entregadas_mes': Encomienda.objects.filter(
                    estado='EN',
                    fecha_entrega_real__month=timezone.now().month
                ).count(),
            }

            cache.set(cache_key, data, CACHE_TTL)

        return Response(data)

    # ─────────────────────────────
    # CON RETRASO
    # ─────────────────────────────
    @action(detail=False, methods=['get'], url_path='con_retraso')
    def con_retraso(self, request):
        qs = Encomienda.objects.con_retraso().con_relaciones()
        return Response(self.get_serializer(qs, many=True).data)

    # ─────────────────────────────
    # PENDIENTES
    # ─────────────────────────────
    @action(detail=False, methods=['get'])
    def pendientes(self, request):
        qs = Encomienda.objects.pendientes().con_relaciones()
        return Response(self.get_serializer(qs, many=True).data)

    # ─────────────────────────────
    # BULK CREATE
    # ─────────────────────────────
    @action(detail=False, methods=['post'], url_path='bulk_create')
    def bulk_create(self, request):

        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        encomiendas = serializer.save(
            empleado_registro=self.request.user.empleado
        )

        return Response(
            self.get_serializer(encomiendas, many=True).data,
            status=status.HTTP_201_CREATED
        )

    # ─────────────────────────────
    # BULK ESTADO
    # ─────────────────────────────
    @action(detail=False, methods=['patch'], url_path='bulk_estado')
    def bulk_estado(self, request):

        ids = request.data.get('ids', [])
        nuevo_estado = request.data.get('estado')
        observacion = request.data.get('observacion', '')

        if not ids:
            return Response({'error': 'ids es requerido'}, status=400)

        if not nuevo_estado:
            return Response({'error': 'estado es requerido'}, status=400)

        try:
            empleado = self.request.user.empleado
        except AttributeError:
            return Response({'error': 'Empleado no encontrado'}, status=403)

        encomiendas = Encomienda.objects.filter(id__in=ids)

        actualizadas = []
        errores = []

        for enc in encomiendas:
            try:
                enc.cambiar_estado(nuevo_estado, empleado, observacion)
                actualizadas.append(enc.id)
            except ValueError as e:
                errores.append({'id': enc.id, 'error': str(e)})

        # INVALIDAR CACHE
        cache.delete(f'estadisticas_empleado_{request.user.id}')

        encontrados = list(encomiendas.values_list('id', flat=True))
        no_encontrados = [i for i in ids if i not in encontrados]

        return Response({
            'actualizadas': actualizadas,
            'errores': errores,
            'no_encontrados': no_encontrados,
            'total': len(actualizadas),
        })