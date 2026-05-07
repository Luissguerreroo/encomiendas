from django.contrib import admin
from django.utils.html import format_html
from .models import Encomienda, Empleado, HistorialEstado


# ========================
# ENCOMIENDA
# ========================

@admin.register(Encomienda)
class EncomiendaAdmin(admin.ModelAdmin):

    # Columnas visibles
    list_display = (
        'codigo',
        'remitente_nombre',
        'destinatario_nombre',
        'ruta',
        'estado_badge',
        'peso_kg',
        'fecha_registro'
    )

    # Filtros laterales
    list_filter = ('estado', 'ruta', 'fecha_registro')

    # Búsqueda
    search_fields = (
        'codigo',
        'remitente__apellidos',
        'destinatario__apellidos',
    )

    # Solo lectura
    readonly_fields = (
        'codigo',
        'fecha_registro',
        'fecha_entrega_real'
    )

    # Orden
    ordering = ('-fecha_registro',)

    list_per_page = 20

    # Organización del formulario
    fieldsets = (
        ('Identificación', {
            'fields': ('codigo', 'descripcion', 'peso_kg')
        }),
        ('Partes', {
            'fields': ('remitente', 'destinatario', 'ruta', 'empleado_registro')
        }),
        ('Estado y fechas', {
            'fields': (
                'estado',
                'costo_envio',
                'fecha_registro',
                'fecha_entrega_est',
                'fecha_entrega_real'
            )
        }),
    )

    # ========================
    # MÉTODOS PERSONALIZADOS
    # ========================

    def remitente_nombre(self, obj):
        return f"{obj.remitente.apellidos}, {obj.remitente.nombres}"
    remitente_nombre.short_description = 'Remitente'

    def destinatario_nombre(self, obj):
        return f"{obj.destinatario.apellidos}, {obj.destinatario.nombres}"
    destinatario_nombre.short_description = 'Destinatario'

    def estado_badge(self, obj):
        colores = {
            'PE': '#6c757d',  # pendiente
            'TR': '#0d6efd',  # tránsito
            'DE': '#198754',  # entregado
        }

        color = colores.get(obj.estado, '#6c757d')

        return format_html(
            '<span style="background:{};color:white;padding:3px 8px;border-radius:5px;">{}</span>',
            color,
            obj.get_estado_display()
        )

    estado_badge.short_description = 'Estado'


# ========================
# EMPLEADO
# ========================

@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'apellidos', 'nombres', 'cargo', 'email')
    search_fields = ('codigo', 'apellidos', 'nombres', 'email')
    list_filter = ('cargo',)


# ========================
# HISTORIAL
# ========================

@admin.register(HistorialEstado)
class HistorialEstadoAdmin(admin.ModelAdmin):
    list_display = (
        'encomienda',
        'estado_anterior',
        'estado_nuevo',
        'empleado',
        'fecha_cambio'
    )

    readonly_fields = (
        'encomienda',
        'estado_anterior',
        'estado_nuevo',
        'empleado',
        'fecha_cambio'
    )

    list_filter = ('estado_nuevo',)
    ordering = ('-fecha_cambio',)