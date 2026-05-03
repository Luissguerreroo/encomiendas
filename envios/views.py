from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse
from django.core.paginator import Paginator

from .models import Encomienda, Empleado, HistorialEstado
from clientes.models import Cliente
from rutas.models import Ruta
from config.choices import EstadoEnvio


# ── Vista mínima ──────────────────────────────────────────────
def mi_vista(request):
    return HttpResponse('Hola desde Django')


# ── Dashboard ────────────────────────────────────────────────
@login_required
def dashboard(request):
    hoy = timezone.now().date()

    context = {
        'total_activas': Encomienda.objects.activas().count(),
        'en_transito': Encomienda.objects.en_transito().count(),
        'con_retraso': Encomienda.objects.con_retraso().count(),
        'entregadas_hoy': Encomienda.objects.filter(
            estado=EstadoEnvio.ENTREGADO,
            fecha_entrega_real=hoy
        ).count(),
        'ultimas': Encomienda.objects.con_relaciones()[:5],
    }

    return render(request, 'envios/dashboard.html', context)


# ── Lista (filtros + paginación) ─────────────────────────────
@login_required
def encomienda_lista(request):
    qs = Encomienda.objects.con_relaciones()

    estado = request.GET.get('estado', '')
    q = request.GET.get('q', '')

    if estado:
        qs = qs.filter(estado=estado)

    if q:
        from django.db.models import Q
        qs = qs.filter(
            Q(codigo__icontains=q) |
            Q(remitente__apellidos__icontains=q) |
            Q(destinatario__apellidos__icontains=q)
        )

    paginator = Paginator(qs, 15)
    page_number = request.GET.get('page', 1)
    encomiendas = paginator.get_page(page_number)

    return render(request, 'envios/lista.html', {
        'encomiendas': encomiendas,
        'estados': EstadoEnvio.choices,
        'estado_activo': estado,
        'q': q,
    })


# ── Redirect ejemplo ─────────────────────────────────────────
def redireccion_ejemplo(request):
    return redirect('encomienda_lista')


# ── Detalle ──────────────────────────────────────────────────
@login_required
def encomienda_detalle(request, pk):
    enc = get_object_or_404(Encomienda.objects.con_relaciones(), pk=pk)

    return render(request, 'envios/detalle.html', {
        'encomienda': enc
    })


# ── Lista por ruta ───────────────────────────────────────────
@login_required
def encomiendas_por_ruta(request, ruta_pk):
    encomiendas = get_list_or_404(Encomienda, ruta__pk=ruta_pk)

    return render(request, 'envios/lista.html', {
        'encomiendas': encomiendas,
    })


# ── Crear encomienda (GET/POST + messages) ───────────────────
@login_required
def encomienda_crear(request):
    from .forms import EncomiendaForm

    if request.method == 'POST':
        form = EncomiendaForm(request.POST)

        if form.is_valid():
            enc = form.save(commit=False)

            enc.empleado_registro = Empleado.objects.get(
                email=request.user.email
            )

            enc.save()

            messages.success(
                request,
                f'Encomienda {enc.codigo} registrada correctamente.'
            )

            return redirect('encomienda_detalle', pk=enc.pk)

        else:
            messages.error(
                request,
                'Corrige los errores del formulario.'
            )

    else:
        form = EncomiendaForm()

    return render(request, 'envios/form.html', {
        'form': form,
        'titulo': 'Nueva Encomienda',
    })


# ── Cambiar estado (POST + messages) ─────────────────────────
@login_required
def encomienda_cambiar_estado(request, pk):
    enc = get_object_or_404(Encomienda, pk=pk)

    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        observacion = request.POST.get('observacion', '')

        try:
            empleado = Empleado.objects.get(email=request.user.email)

            enc.cambiar_estado(nuevo_estado, empleado, observacion)

            messages.success(
                request,
                f'Estado actualizado a: {enc.get_estado_display()}'
            )

        except ValueError as e:
            messages.error(request, str(e))

    return redirect('encomienda_detalle', pk=pk)