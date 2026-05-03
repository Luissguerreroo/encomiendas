// ── Esperar a que cargue el DOM ───────────────────────────────
document.addEventListener('DOMContentLoaded', function () {

    // ── Inicializar tooltips de Bootstrap ─────────────────────
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(function (el) {
        new bootstrap.Tooltip(el);
    });

    // ── Auto-cerrar alertas flash después de 5 segundos ───────
    // (complementa la animación CSS del styles.css)
    setTimeout(function () {
        document.querySelectorAll('.alert').forEach(function (alert) {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        });
    }, 5000);

    // ── Confirmación antes de eliminar ────────────────────────
    // Uso en template:
    // <button onclick="return confirmar('Eliminar este registro?')">Eliminar</button>
    window.confirmar = function (mensaje) {
        return confirm(mensaje || '¿Estás seguro?');
    };

    // ── Resaltar fila clickeable (navegación intuitiva) ───────
    // Uso:
    // <tr class="fila-link" data-href="{% url 'encomienda_detalle' enc.pk %}">
    document.querySelectorAll('.fila-link').forEach(function (fila) {
        fila.addEventListener('click', function () {
            window.location = this.dataset.href;
        });
    });

});