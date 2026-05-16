from rest_framework import serializers
from django.utils import timezone

from .models import Encomienda, HistorialEstado
from clientes.models import Cliente
from rutas.models import Ruta


# ─────────────────────────────
# CLIENTE
# ─────────────────────────────
class ClienteSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.ReadOnlyField()
    esta_activo = serializers.ReadOnlyField()

    class Meta:
        model = Cliente
        fields = [
            'id',
            'tipo_doc',
            'nro_doc',
            'nombres',
            'apellidos',
            'nombre_completo',
            'telefono',
            'email',
            'esta_activo',
        ]


# ─────────────────────────────
# RUTA
# ─────────────────────────────
class RutaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ruta
        fields = [
            'id',
            'codigo',
            'origen',
            'destino',
            'precio_base',
            'dias_entrega',
            'estado',
        ]


# ─────────────────────────────
# HISTORIAL
# ─────────────────────────────
class HistorialEstadoSerializer(serializers.ModelSerializer):

    empleado_nombre = serializers.ReadOnlyField(source='empleado.__str__')

    estado_anterior_display = serializers.CharField(
        source='get_estado_anterior_display',
        read_only=True
    )

    estado_nuevo_display = serializers.CharField(
        source='get_estado_nuevo_display',
        read_only=True
    )

    class Meta:
        model = HistorialEstado
        fields = [
            'id',
            'estado_anterior',
            'estado_anterior_display',
            'estado_nuevo',
            'estado_nuevo_display',
            'empleado_nombre',
            'observacion',
            'fecha_cambio',
        ]


# ─────────────────────────────
# BULK SERIALIZER
# ─────────────────────────────
class EncomiendaBulkSerializer(serializers.ListSerializer):

    def create(self, validated_data):
        encomiendas = [
            Encomienda(**item)
            for item in validated_data
        ]
        return Encomienda.objects.bulk_create(encomiendas)

    def update(self, instances, validated_data):
        instance_map = {obj.id: obj for obj in instances}
        updated = []

        for item in validated_data:
            enc_id = item.get('id')
            enc = instance_map.get(enc_id)

            if not enc:
                continue

            for attr, value in item.items():
                setattr(enc, attr, value)

            updated.append(enc)

        if updated:
            Encomienda.objects.bulk_update(
                updated,
                [
                    'estado',
                    'costo_envio',
                    'observaciones',
                ]
            )

        return updated


# ─────────────────────────────
# ENCOMIENDA (LISTA / SIMPLE)
# ─────────────────────────────
class EncomiendaSerializer(serializers.ModelSerializer):

    esta_entregada = serializers.ReadOnlyField()
    tiene_retraso = serializers.ReadOnlyField()
    dias_en_transito = serializers.ReadOnlyField()
    descripcion_corta = serializers.ReadOnlyField()

    estado_display = serializers.SerializerMethodField()

    class Meta:
        model = Encomienda
        fields = [
            'id',
            'codigo',
            'descripcion',
            'descripcion_corta',
            'peso_kg',
            'costo_envio',
            'remitente',
            'destinatario',
            'ruta',
            'empleado_registro',
            'estado',
            'estado_display',
            'fecha_registro',
            'fecha_entrega_est',
            'fecha_entrega_real',
            'esta_entregada',
            'tiene_retraso',
            'dias_en_transito',
        ]

        read_only_fields = [
            'codigo',
            'fecha_registro',
            'fecha_entrega_real',
        ]

        # 🔥 ACTIVA BULK SERIALIZER
        list_serializer_class = EncomiendaBulkSerializer

    # ─────────────────────────────
    # DISPLAY DE ESTADO
    # ─────────────────────────────
    def get_estado_display(self, obj):
        return obj.get_estado_display()

    # ─────────────────────────────
    # NORMALIZACIÓN (INPUT)
    # ─────────────────────────────
    def to_internal_value(self, data):

        data = data.copy()

        if data.get('codigo'):
            data['codigo'] = str(data['codigo']).upper().strip()

        if data.get('descripcion'):
            data['descripcion'] = str(data['descripcion']).strip()

        if data.get('costo_envio'):
            try:
                from decimal import Decimal, ROUND_HALF_UP

                costo = Decimal(str(data['costo_envio']))
                data['costo_envio'] = str(
                    costo.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                )
            except Exception:
                pass

        return super().to_internal_value(data)

    # ─────────────────────────────
    # RESPONSE (OUTPUT)
    # ─────────────────────────────
    def to_representation(self, instance):

        data = super().to_representation(instance)

        if instance.ruta_id:
            data['ruta_codigo'] = instance.ruta.codigo
            data['ruta_destino'] = instance.ruta.destino
            data['ruta_origen'] = instance.ruta.origen

        data['costo_display'] = f"S/ {instance.costo_envio:.2f}"

        request = self.context.get('request')
        if request and not request.user.is_staff:
            data.pop('empleado_registro', None)

        colores = {
            'PE': 'gray',
            'TR': 'blue',
            'DE': 'orange',
            'EN': 'green',
            'DV': 'red',
        }

        data['estado_color'] = colores.get(instance.estado, 'gray')

        return data

    # ─────────────────────────────
    # VALIDACIONES
    # ─────────────────────────────
    def validate_peso_kg(self, value):
        if value <= 0:
            raise serializers.ValidationError("El peso debe ser mayor a 0 kg.")
        if value > 500:
            raise serializers.ValidationError("El peso máximo permitido es 500 kg.")
        return value

    def validate_codigo(self, value):
        if not value.startswith('ENC-'):
            raise serializers.ValidationError("El código debe comenzar con ENC-")
        return value.upper()

    def validate_costo_envio(self, value):
        if value < 0:
            raise serializers.ValidationError("El costo no puede ser negativo.")
        return value

    def validate(self, data):

        errors = {}

        if data.get('remitente') == data.get('destinatario'):
            errors['destinatario'] = "El destinatario no puede ser el mismo que el remitente."

        fecha = data.get('fecha_entrega_est')
        if fecha and fecha < timezone.now().date():
            errors['fecha_entrega_est'] = "La fecha no puede ser en el pasado."

        ruta = data.get('ruta')
        costo = data.get('costo_envio')

        if ruta and costo and costo < float(ruta.precio_base):
            errors['costo_envio'] = f"El costo mínimo es S/ {ruta.precio_base}"

        if errors:
            raise serializers.ValidationError(errors)

        return data


# ─────────────────────────────
# DETAIL
# ─────────────────────────────
class EncomiendaDetailSerializer(EncomiendaSerializer):

    remitente = ClienteSerializer(read_only=True)
    destinatario = ClienteSerializer(read_only=True)
    ruta = RutaSerializer(read_only=True)

    historial = serializers.SerializerMethodField()

    remitente_id = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.activos(),
        write_only=True,
        source='remitente'
    )

    destinatario_id = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.activos(),
        write_only=True,
        source='destinatario'
    )

    ruta_id = serializers.PrimaryKeyRelatedField(
        queryset=Ruta.objects.activas(),
        write_only=True,
        source='ruta'
    )

    class Meta:
        model = Encomienda
        fields = EncomiendaSerializer.Meta.fields + [
            'remitente_id',
            'destinatario_id',
            'ruta_id',
            'historial',
        ]

    def get_historial(self, obj):
        return HistorialEstadoSerializer(
            obj.historial.all()[:5],
            many=True
        ).data


# ─────────────────────────────
# V2
# ─────────────────────────────
class EncomiendaV2Serializer(serializers.ModelSerializer):

    remitente = ClienteSerializer(read_only=True)
    destinatario = ClienteSerializer(read_only=True)
    ruta = RutaSerializer(read_only=True)

    remitente_id = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.activos(),
        write_only=True,
        source='remitente'
    )

    destinatario_id = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.activos(),
        write_only=True,
        source='destinatario'
    )

    ruta_id = serializers.PrimaryKeyRelatedField(
        queryset=Ruta.objects.activas(),
        write_only=True,
        source='ruta'
    )

    dias_en_transito = serializers.ReadOnlyField()
    tiene_retraso = serializers.ReadOnlyField()
    esta_entregada = serializers.ReadOnlyField()
    descripcion_corta = serializers.ReadOnlyField()

    estado_display = serializers.SerializerMethodField()
    meta = serializers.SerializerMethodField()

    class Meta:
        model = Encomienda
        fields = [
            'id',
            'codigo',
            'descripcion',
            'descripcion_corta',
            'peso_kg',
            'costo_envio',
            'remitente',
            'remitente_id',
            'destinatario',
            'destinatario_id',
            'ruta',
            'ruta_id',
            'empleado_registro',
            'estado',
            'estado_display',
            'fecha_registro',
            'fecha_entrega_est',
            'fecha_entrega_real',
            'dias_en_transito',
            'tiene_retraso',
            'esta_entregada',
            'meta',
        ]

        read_only_fields = [
            'codigo',
            'fecha_registro',
            'fecha_entrega_real',
        ]

    def get_estado_display(self, obj):
        return obj.get_estado_display()

    def get_meta(self, obj):
        return {
            'version': 'v2',
            'generado': timezone.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
            'puede_editar': not obj.esta_entregada,
        }
    
class EncomiendaListSerializer(serializers.ModelSerializer):
    """
    Serializer optimizado para el listado.
    Solo los campos necesarios para la tabla.
    """

    remitente_nombre = serializers.ReadOnlyField(source='remitente.nombre_completo')
    destinatario_nombre = serializers.ReadOnlyField(source='destinatario.nombre_completo')
    ruta_destino = serializers.ReadOnlyField(source='ruta.destino')
    estado_display = serializers.SerializerMethodField()

    esta_entregada = serializers.ReadOnlyField()
    tiene_retraso = serializers.ReadOnlyField()

    class Meta:
        model = Encomienda
        fields = [
            'id',
            'codigo',
            'estado',
            'estado_display',
            'remitente_nombre',
            'destinatario_nombre',
            'ruta_destino',
            'peso_kg',
            'costo_envio',
            'fecha_registro',
            'fecha_entrega_est',
            'esta_entregada',
            'tiene_retraso',
        ]

    def get_estado_display(self, obj):
        return obj.get_estado_display()