// Función para mostrar toast
function showToast(message) {
    // Si usas Bootstrap Toast
    let bootstrap;
    if (typeof bootstrap !== 'undefined') {
        const toastEl = document.createElement('div');
        toastEl.className = 'toast align-items-center';
        toastEl.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        document.body.appendChild(toastEl);
        const toast = new bootstrap.bootstrap(toastEl); // Corregido: bootstrap.Toast en lugar de bootstrap.bootstrap
        toast.show();
    } else {
        // Fallback a alert si no hay Bootstrap
        alert(message);
    }
}

document.addEventListener('DOMContentLoaded', function () {
    // Manejar clicks en botones deshabilitados
    document.querySelectorAll('.btn-disabled').forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            showToast('Producto agotado temporalmente');
        });
    });
});