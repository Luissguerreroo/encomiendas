import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone

from .models import Encomienda


# =========================================================
# DASHBOARD CONSUMER
# =========================================================

class DashboardConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        user = self.scope['user']

        if not user.is_authenticated:
            await self.close(code=4001)
            return

        self.group_name = 'dashboard'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

        # Enviar estadísticas iniciales
        stats = await self.get_stats()

        await self.send(
            text_data=json.dumps({
                'tipo': 'stats_iniciales',
                'stats': stats,
            })
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def dashboard_actualizar(self, event):
        """
        Recibe eventos del channel layer
        y los reenvía al navegador.
        """

        await self.send(
            text_data=json.dumps({
                'tipo': 'stats_actualizado',
                'stats': event['stats'],
            })
        )

    @database_sync_to_async
    def get_stats(self):
        hoy = timezone.now().date()

        return {
            'activas': Encomienda.objects.activas().count(),
            'en_transito': Encomienda.objects.en_transito().count(),
            'con_retraso': Encomienda.objects.con_retraso().count(),
            'entregadas_hoy': Encomienda.objects.filter(
                estado='EN',
                fecha_entrega_real=hoy
            ).count(),
        }


# =========================================================
# ENCOMIENDA CONSUMER
# =========================================================

class EncomiendaConsumer(AsyncWebsocketConsumer):
    """
    Consumer global de encomiendas.
    """

    async def connect(self):

        user = self.scope['user']

        # Verificar autenticación
        if not user.is_authenticated:
            await self.close(code=4001)
            return

        # Grupo global
        self.group_name = 'encomiendas_global'

        # Unirse al grupo
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        # Aceptar conexión
        await self.accept()

        # Enviar mensaje inicial
        stats = await self.get_estadisticas()

        await self.send(
            text_data=json.dumps({
                'tipo': 'conectado',
                'usuario': user.username,
                'stats': stats,
            })
        )

    async def receive(self, text_data=None, bytes_data=None):
        """
        Manejo seguro de mensajes WebSocket.
        """

        if not text_data:
            return

        try:

            data = json.loads(text_data)

            await self.procesar_mensaje(data)

        except json.JSONDecodeError:

            await self.send(
                text_data=json.dumps({
                    'tipo': 'error',
                    'codigo': 'JSON_INVALIDO',
                    'mensaje': 'El mensaje no es JSON válido',
                })
            )

        except Exception as e:

            import logging

            logger = logging.getLogger(__name__)

            logger.error(
                f'Error en consumer: {e}',
                exc_info=True
            )

            await self.send(
                text_data=json.dumps({
                    'tipo': 'error',
                    'codigo': 'ERROR_INTERNO',
                    'mensaje': 'Error interno del servidor',
                })
            )

    async def procesar_mensaje(self, data):

        tipo = data.get('tipo')

        # ─────────────────────────────
        # Ping/Pong
        # ─────────────────────────────
        if tipo == 'ping':

            await self.send(
                text_data=json.dumps({
                    'tipo': 'pong'
                })
            )

        # ─────────────────────────────
        # Solicitar estadísticas
        # ─────────────────────────────
        elif tipo == 'solicitar_stats':

            stats = await self.get_estadisticas()

            await self.send(
                text_data=json.dumps({
                    'tipo': 'stats',
                    'stats': stats
                })
            )

        # ─────────────────────────────
        # Suscribirse a encomienda
        # ─────────────────────────────
        elif tipo == 'suscribir_encomienda':

            enc_id = data.get('encomienda_id')

            if enc_id:

                await self.channel_layer.group_add(
                    f'encomienda_{enc_id}',
                    self.channel_name
                )

                await self.send(
                    text_data=json.dumps({
                        'tipo': 'suscrito',
                        'encomienda_id': enc_id
                    })
                )

        # ─────────────────────────────
        # Tipo desconocido
        # ─────────────────────────────
        else:

            await self.send(
                text_data=json.dumps({
                    'tipo': 'error',
                    'codigo': 'TIPO_DESCONOCIDO',
                    'mensaje': f'Tipo desconocido: {tipo}'
                })
            )

    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def encomienda_estado_cambio(self, event):
        """
        Handler del grupo.
        """

        await self.send(
            text_data=json.dumps({
                'tipo': 'estado_cambio',
                'encomienda_id': event['encomienda_id'],
                'codigo': event['codigo'],
                'estado_anterior': event['estado_anterior'],
                'estado_nuevo': event['estado_nuevo'],
                'empleado': event['empleado'],
                'timestamp': event['timestamp'],
            })
        )

    @database_sync_to_async
    def get_estadisticas(self):

        hoy = timezone.now().date()

        return {
            'activas': Encomienda.objects.activas().count(),
            'en_transito': Encomienda.objects.en_transito().count(),
            'con_retraso': Encomienda.objects.con_retraso().count(),
            'entregadas_hoy': Encomienda.objects.filter(
                estado='EN',
                fecha_entrega_real=hoy
            ).count(),
        }

