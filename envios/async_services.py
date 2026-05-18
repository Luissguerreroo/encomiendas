# envios/async_services.py
# Servicios asíncronos del proyecto

import asyncio

import httpx
from django.utils import timezone

from .models import Encomienda


# ─────────────────────────────
# VERIFICAR UNA ENCOMIENDA
# ─────────────────────────────
async def verificar_una(
    session: httpx.AsyncClient,
    codigo: str
) -> dict:
    """
    Verifica UNA encomienda usando una sesión HTTP compartida.
    """

    url = f"https://api.transportista.pe/v1/track/{codigo}"

    try:
        response = await session.get(
            url,
            timeout=5.0
        )

        data = response.json()

        return {
            "codigo": codigo,
            "encontrado": True,
            "estado_ext": data.get("status"),
            "ubicacion": data.get("location"),
            "timestamp": timezone.now().isoformat(),
        }

    except httpx.TimeoutException:
        return {
            "codigo": codigo,
            "encontrado": False,
            "error": "timeout",
        }

    except httpx.ConnectError:
        return {
            "codigo": codigo,
            "encontrado": False,
            "error": "conexion",
        }

    except Exception as e:
        return {
            "codigo": codigo,
            "encontrado": False,
            "error": str(e),
        }


# ─────────────────────────────
# ACTUALIZAR ENCOMIENDAS
# ─────────────────────────────
async def actualizar_estados_en_transito() -> dict:
    """
    Actualiza todas las encomiendas en tránsito
    consultando la API del transportista en paralelo.
    """

    # Obtener encomiendas async
    encomiendas = await Encomienda.objects.en_transito().alist()

    if not encomiendas:
        return {
            "verificadas": 0,
            "actualizadas": [],
        }

    print(
        f"Verificando {len(encomiendas)} encomiendas en paralelo..."
    )

    # UNA sola sesión HTTP compartida
    async with httpx.AsyncClient() as session:

        tareas = [
            verificar_una(session, enc.codigo)
            for enc in encomiendas
        ]

        # Ejecutar TODO en paralelo
        resultados = await asyncio.gather(
            *tareas,
            return_exceptions=True,
        )

    actualizadas = []

    # Procesar resultados
    for enc, resultado in zip(encomiendas, resultados):

        # Ignorar errores
        if isinstance(resultado, Exception):
            continue

        # Si el transportista indica entregado
        if (
            resultado.get("encontrado")
            and resultado.get("estado_ext") == "DELIVERED"
        ):

            enc.estado = "EN"
            enc.fecha_entrega_real = timezone.now().date()

            # Guardado async
            await enc.asave()

            actualizadas.append(enc.codigo)

    return {
        "verificadas": len(encomiendas),
        "actualizadas": actualizadas,
        "total_actualizadas": len(actualizadas),
        "resultados": resultados,
    }